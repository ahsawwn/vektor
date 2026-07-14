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

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(1)
        splitter.setChildrenCollapsible(False)

        self.sidebar = Sidebar()
        self.chat_area = ChatArea()
        self.input_bar = InputBar()

        chat_container = QWidget()
        chat_layout = QVBoxLayout(chat_container)
        chat_layout.setContentsMargins(0, 0, 0, 0)
        chat_layout.setSpacing(0)
        chat_layout.addWidget(self.chat_area, stretch=1)
        chat_layout.addWidget(self.input_bar)

        splitter.addWidget(self.sidebar)
        splitter.addWidget(chat_container)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([220, 900])

        layout.addWidget(splitter)

        self.status_bar = QStatusBar()
        self.status_bar.setObjectName("StatusBar")
        self.status_bar.showMessage("LLM: idle  |  DB: connected  |  Model: llama3")
        self.setStatusBar(self.status_bar)

    def _bind_shortcuts(self) -> None:
        fs = QShortcut(QKeySequence(Qt.Key.Key_F11), self)
        fs.activated.connect(self._toggle_fullscreen)

        esc = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
        esc.activated.connect(self._exit_fullscreen)

    def _wire_controller(self) -> None:
        self.input_bar.message_sent.connect(self._on_user_message)
        self.controller.response_received.connect(self._on_response)
        self.controller.error_occurred.connect(self._on_error)
        self.controller.thinking_changed.connect(self._on_thinking_changed)

    def _on_user_message(self, text: str) -> None:
        self.chat_area.add_message("user", text)
        self.controller.send_message(text)

    def _on_response(self, reply: str) -> None:
        self.chat_area.add_message("assistant", reply)

    def _on_error(self, error_message: str) -> None:
        self.chat_area.add_message("assistant", f"**Error:** {error_message}")

    def _on_thinking_changed(self, thinking: bool) -> None:
        self.input_bar.set_input_enabled(not thinking)
        self.sidebar.set_llm_status("thinking" if thinking else "active")
        state = "THINKING" if thinking else "IDLE"
        self.status_bar.showMessage(
            f"LLM: {state}  |  DB: connected  |  Model: llama3"
        )

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
