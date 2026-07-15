from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QSplitter,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from database.connection import init_db
from ui.components.chat_area import ChatArea
from ui.components.input_bar import InputBar
from ui.components.preview_panel import PreviewPanel
from ui.components.sidebar import Sidebar
from ui.controller import ChatController


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        init_db()

        self.setWindowTitle("Vektor")
        self.setObjectName("MainWindow")
        self.setMinimumSize(QSize(900, 600))
        self.showMaximized()

        self._is_fullscreen = False
        self._preview_visible = False

        self.controller = ChatController()

        self._build_ui()
        self._bind_shortcuts()
        self._wire_controller()

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)

        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setHandleWidth(1)
        self.splitter.setChildrenCollapsible(False)

        self.sidebar = Sidebar()
        self.chat_area = ChatArea()
        self.input_bar = InputBar()
        self.preview = PreviewPanel()
        self.preview.setVisible(False)

        chat_container = QWidget()
        chat_layout = QVBoxLayout(chat_container)
        chat_layout.setContentsMargins(0, 0, 0, 0)
        chat_layout.setSpacing(0)
        chat_layout.addWidget(self.chat_area, stretch=1)
        chat_layout.addWidget(self.input_bar)

        self.splitter.addWidget(self.sidebar)
        self.splitter.addWidget(chat_container)
        self.splitter.addWidget(self.preview)
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)
        self.splitter.setStretchFactor(2, 1)
        self.splitter.setSizes([220, 600, 0])

        layout.addWidget(self.splitter)

        from config import OLLAMA_MODEL
        self.status_bar = QStatusBar()
        self.status_bar.setObjectName("StatusBar")
        self.status_bar.showMessage(f"LLM: idle  |  DB: connected  |  Model: {OLLAMA_MODEL}  |  Voice: off")
        self.setStatusBar(self.status_bar)

    def _bind_shortcuts(self) -> None:
        fs = QShortcut(QKeySequence(Qt.Key.Key_F11), self)
        fs.activated.connect(self._toggle_fullscreen)

        esc = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
        esc.activated.connect(self._exit_fullscreen)

    def _wire_controller(self) -> None:
        self.input_bar.message_sent.connect(self._on_user_message)
        self.input_bar.voice_triggered.connect(self._on_voice_trigger)

        self.controller.response_received.connect(self._on_response)
        self.controller.error_occurred.connect(self._on_error)
        self.controller.thinking_changed.connect(self._on_thinking_changed)
        self.controller.voice_text.connect(self._on_voice_text)
        self.controller.command_output.connect(self._on_command_output)
        self.controller.preview_ready.connect(self._on_preview_ready)

    def _on_user_message(self, text: str) -> None:
        self.chat_area.add_message("user", text)
        self.controller.send_message(text)

    def _on_voice_trigger(self) -> None:
        self.chat_area.add_message("system", "🎤 Listening...")
        self.controller.start_voice_recording()

    def _on_voice_text(self, text: str) -> None:
        self.chat_area.add_message("user", f"[voice] {text}")
        self.controller.send_message(text)

    def _on_response(self, user_input: str, reply: str) -> None:
        self.chat_area.add_message("assistant", reply)

    def _on_error(self, error_message: str) -> None:
        self.chat_area.add_message("assistant", f"**Error:** {error_message}")

    def _on_command_output(self, output: str) -> None:
        self.chat_area.add_message(
            "assistant",
            f"```\n{output}\n```",
        )

    def _on_preview_ready(self, path: str) -> None:
        self.preview.load_file(path)
        self._show_preview()

    def _on_thinking_changed(self, thinking: bool) -> None:
        from config import OLLAMA_MODEL
        self.input_bar.set_input_enabled(not thinking)
        self.sidebar.set_llm_status("thinking" if thinking else "active")
        state = "THINKING" if thinking else "IDLE"
        voice = "on" if self.controller._tts_enabled else "off"
        self.status_bar.showMessage(
            f"LLM: {state}  |  DB: connected  |  Model: {OLLAMA_MODEL}  |  Voice: {voice}"
        )

    def _show_preview(self) -> None:
        if not self._preview_visible:
            self._preview_visible = True
            self.preview.setVisible(True)
            self.splitter.setSizes([220, 400, 500])

    def _toggle_fullscreen(self) -> None:
        if self._is_fullscreen:
            self.showNormal()
        else:
            self.showFullScreen()
        self._is_fullscreen = not self._is_fullscreen

    def _exit_fullscreen(self) -> None:
        if self._is_fullscreen:
            self.showNormal()
            self._is_fullscreen = False


if __name__ == "__main__":
    import sys
    from pathlib import Path
    from PySide6.QtGui import QFont
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    app.setApplicationName("Vektor")
    font = QFont("JetBrains Mono", 10)
    font.setStyleHint(QFont.StyleHint.Monospace)
    app.setFont(font)

    stylesheet_path = Path(__file__).parent / "assets" / "style.qss"
    if stylesheet_path.exists():
        with open(stylesheet_path) as f:
            app.setStyleSheet(f.read())

    w = MainWindow()
    w.show()
    sys.exit(app.exec())
