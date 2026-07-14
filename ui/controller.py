from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal, Slot

from core.agent import VektorAgent


class ChatWorker(QRunnable):
    class Signals(QObject):
        finished = Signal(str)
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
            self.signals.finished.emit(reply)
        except Exception as exc:
            self.signals.error.emit(str(exc))


class ChatController(QObject):
    thinking_changed = Signal(bool)
    response_received = Signal(str)
    error_occurred = Signal(str)

    def __init__(self, agent: VektorAgent | None = None, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._agent = agent or VektorAgent()
        self._pool = QThreadPool()
        self._thinking = False

    @property
    def is_thinking(self) -> bool:
        return self._thinking

    def send_message(self, text: str) -> None:
        if self._thinking:
            return

        self._thinking = True
        self.thinking_changed.emit(True)

        worker = ChatWorker(self._agent, text)
        worker.signals.finished.connect(self._on_finished)
        worker.signals.error.connect(self._on_error)
        self._pool.start(worker)

    def _on_finished(self, reply: str) -> None:
        self._thinking = False
        self.thinking_changed.emit(False)
        self.response_received.emit(reply)

    def _on_error(self, error_message: str) -> None:
        self._thinking = False
        self.thinking_changed.emit(False)
        self.error_occurred.emit(error_message)
