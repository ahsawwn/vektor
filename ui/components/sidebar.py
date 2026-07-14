from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)


class StatusDot(QLabel):
    def __init__(self, initial_state: str = "inactive", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("StatusDot")
        self.setProperty("state", initial_state)
        self.setFixedSize(8, 8)

    def set_state(self, state: str) -> None:
        self.setProperty("state", state)
        self.style().unpolish(self)
        self.style().polish(self)


class StatusRow(QWidget):
    def __init__(self, label: str, initial_state: str = "inactive", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("StatusIndicator")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.dot = StatusDot(initial_state)
        self.label = QLabel(label)
        self.label.setStyleSheet("color: #94A3B8; font-size: 12px;")

        layout.addWidget(self.dot)
        layout.addWidget(self.label)
        layout.addStretch()

    def set_state(self, state: str) -> None:
        self.dot.set_state(state)


class Sidebar(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("Sidebar")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        title = QLabel("VEKTOR")
        title.setObjectName("SidebarTitle")
        layout.addWidget(title)

        layout.addSpacing(8)

        status_label = QLabel("SYSTEM STATUS")
        status_label.setObjectName("SidebarLabel")
        layout.addWidget(status_label)

        self.db_status = StatusRow("SQLite DB")
        self.db_status.set_state("active")
        layout.addWidget(self.db_status)

        self.llm_status = StatusRow("Local LLM")
        self.llm_status.set_state("thinking")
        layout.addWidget(self.llm_status)

        self.daemon_status = StatusRow("System Daemon")
        self.daemon_status.set_state("inactive")
        layout.addWidget(self.daemon_status)

        layout.addSpacing(16)

        model_label = QLabel("ACTIVE MODEL")
        model_label.setObjectName("SidebarLabel")
        layout.addWidget(model_label)

        self.model_selector = QComboBox()
        self.model_selector.addItems(["llama3", "mistral", "codellama", "deepseek-coder"])
        self.model_selector.setCurrentText("llama3")
        layout.addWidget(self.model_selector)

        layout.addSpacing(16)

        recent_label = QLabel("RECENT CONVERSATIONS")
        recent_label.setObjectName("SidebarLabel")
        layout.addWidget(recent_label)

        self.recent_list = QListWidget()
        self.recent_list.setObjectName("RecentConversations")
        self.recent_list.setAlternatingRowColors(False)

        placeholder = QListWidgetItem("No conversations yet")
        placeholder.setFlags(placeholder.flags() & ~Qt.ItemFlag.ItemIsSelectable)
        self.recent_list.addItem(placeholder)

        layout.addWidget(self.recent_list, stretch=1)

        version_label = QLabel("v0.1.0 — local")
        version_label.setStyleSheet(
            "color: #475569; font-size: 10px; padding: 8px 16px;"
        )
        layout.addWidget(version_label)

    def set_llm_status(self, state: str) -> None:
        self.llm_status.set_state(state)

    def set_db_status(self, state: str) -> None:
        self.db_status.set_state(state)

    def set_daemon_status(self, state: str) -> None:
        self.daemon_status.set_state(state)
