import re
from pathlib import Path

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal, Slot
from sqlmodel import Session, select

from config import SQLITE_PATH
from core.agent import VektorAgent
from database.connection import engine
from database.models import ConversationLog, UserPreference
from services.audio_service import speak, transcribe_microphone
from services.executor_service import execute as sys_execute
from services.web_scaffolder import generate_page


class ChatWorker(QRunnable):
    class Signals(QObject):
        finished = Signal(str, str)
        error = Signal(str)

    def __init__(self, agent: VektorAgent, user_input: str) -> None:
        super().__init__()
        self.agent = agent
        self.user_input = user_input
        self.signals = ChatWorker.Signals()

    @Slot()
    def run(self) -> None:
        try:
            reply = self.agent.chat(self.user_input)
            self.signals.finished.emit(self.user_input, reply)
        except Exception as exc:
            self.signals.error.emit(str(exc))


class VoiceWorker(QRunnable):
    class Signals(QObject):
        finished = Signal(str)
        error = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self.signals = VoiceWorker.Signals()

    @Slot()
    def run(self) -> None:
        try:
            text = transcribe_microphone()
            self.signals.finished.emit(text)
        except Exception as exc:
            self.signals.error.emit(str(exc))


class SpeakWorker(QRunnable):
    class Signals(QObject):
        finished = Signal()

    def __init__(self, text: str) -> None:
        super().__init__()
        self.text = text
        self.signals = SpeakWorker.Signals()

    @Slot()
    def run(self) -> None:
        try:
            speak(self.text)
        except Exception:
            pass
        finally:
            self.signals.finished.emit()


class ExecuteWorker(QRunnable):
    class Signals(QObject):
        finished = Signal(str)

    def __init__(self, command: str) -> None:
        super().__init__()
        self.command = command
        self.signals = ExecuteWorker.Signals()

    @Slot()
    def run(self) -> None:
        output = sys_execute(self.command)
        self.signals.finished.emit(output)


_LEARN_RE = re.compile(
    r"(?:remember|learn)\s+that\s+(.+?)\s+(?:is|uses?|has|prefers?|runs?on)\s+(.+)",
    re.IGNORECASE,
)

_REMEMBER_RE = re.compile(
    r"(?:remember|learn)\s+['\"](.+?)['\"]\s+(?:as|is|=|->)\s+['\"](.+?)['\"]",
    re.IGNORECASE,
)


def _handle_learning(text: str) -> str | None:
    m = _LEARN_RE.match(text) or _REMEMBER_RE.match(text)
    if not m:
        return None
    key = m.group(1).strip().lower().replace(" ", "_")
    value = m.group(2).strip()

    with Session(engine) as session:
        stmt = select(UserPreference).where(UserPreference.key == key)
        existing = session.exec(stmt).one_or_none()
        if existing:
            existing.value = value
        else:
            session.add(UserPreference(key=key, value=value))
        session.commit()

    return f"Stored: `{key}` → `{value}`"


_WEB_GEN_RE = re.compile(
    r"(?:build|create|generate|scaffold)\s+(?:a\s+)?(.*?)(?:page|site|landing|ui|html)",
    re.IGNORECASE,
)


def _handle_web_scaffold(text: str, reply: str) -> Path | None:
    if not _WEB_GEN_RE.search(text):
        return None
    html_match = re.search(
        r"```(?:html)?\s*\n(<!DOCTYPE html>.*?)\n```", reply, re.DOTALL
    )
    if not html_match:
        html_match = re.search(
            r"```(?:html)?\s*\n(<html>.*?</html>)\n```", reply, re.DOTALL
        )
    if not html_match:
        html_match = re.search(r"(<!DOCTYPE html>.*?</html>)", reply, re.DOTALL)
    if html_match:
        return generate_page(html_match.group(1))
    return None


class ChatController(QObject):
    thinking_changed = Signal(bool)
    response_received = Signal(str, str)
    error_occurred = Signal(str)
    voice_text = Signal(str)
    command_output = Signal(str)
    preview_ready = Signal(str)

    def __init__(self, agent: VektorAgent | None = None, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._agent = agent or VektorAgent()
        self._pool = QThreadPool()
        self._thinking = False
        self._tts_enabled = False

    @property
    def is_thinking(self) -> bool:
        return self._thinking

    def set_tts_enabled(self, enabled: bool) -> None:
        self._tts_enabled = enabled

    def send_message(self, text: str) -> None:
        if self._thinking:
            return

        learned = _handle_learning(text)
        if learned:
            self.response_received.emit(text, learned)
            return

        self._thinking = True
        self.thinking_changed.emit(True)

        worker = ChatWorker(self._agent, text)
        worker.signals.finished.connect(self._on_finished)
        worker.signals.error.connect(self._on_error)
        self._pool.start(worker)

    def start_voice_recording(self) -> None:
        worker = VoiceWorker()
        worker.signals.finished.connect(self._on_voice_result)
        worker.signals.error.connect(lambda e: self.error_occurred.emit(e))
        self._pool.start(worker)

    def speak_text(self, text: str) -> None:
        if not self._tts_enabled:
            return
        worker = SpeakWorker(text)
        self._pool.start(worker)

    def execute_command(self, command: str) -> None:
        worker = ExecuteWorker(command)
        worker.signals.finished.connect(self.command_output.emit)
        self._pool.start(worker)

    def _on_finished(self, user_input: str, reply: str) -> None:
        self._thinking = False
        self.thinking_changed.emit(False)
        self.response_received.emit(user_input, reply)

        scaffolded = _handle_web_scaffold(user_input, reply)
        if scaffolded:
            self.preview_ready.emit(str(scaffolded))

        if self._tts_enabled:
            self.speak_text(reply)

    def _on_error(self, error_message: str) -> None:
        self._thinking = False
        self.thinking_changed.emit(False)
        self.error_occurred.emit(error_message)

    def _on_voice_result(self, text: str) -> None:
        self.voice_text.emit(text)
        self.send_message(text)
