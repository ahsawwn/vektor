from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QLabel,
    QScrollArea,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)


class MessageBubble(QWidget):
    def __init__(
        self,
        role: str,
        content: str,
        timestamp: datetime | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("MessageContainer")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        header = QWidget()
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(2)

        role_label = QLabel("You" if role == "user" else "Vektor")
        role_label.setObjectName("MessageRole")

        if timestamp:
            ts = QLabel(timestamp.strftime("%H:%M"))
            ts.setObjectName("MessageTimestamp")
            header_layout.addWidget(ts)

        layout.addWidget(role_label)

        self.text_browser = QTextBrowser()
        self.text_browser.setObjectName("MessageContent")
        self.text_browser.setOpenExternalLinks(True)
        self.text_browser.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.text_browser.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.text_browser.setMarkdown(content)
        self.text_browser.document().setDocumentMargin(0)
        self.text_browser.setFrameShape(QTextBrowser.Shape.NoFrame)

        if role == "user":
            self.setObjectName("UserMessage")
            role_label.setText("You")
            role_label.setStyleSheet("color: #60A5FA;")
        else:
            self.setObjectName("AssistantMessage")
            role_label.setText("Vektor")
            role_label.setStyleSheet("color: #A78BFA;")

        layout.addWidget(self.text_browser)

        self._adjust_height()

    def _adjust_height(self) -> None:
        doc = self.text_browser.document()
        doc.setTextWidth(self.text_browser.viewport().width())
        height = doc.size().height() + 8
        self.text_browser.setFixedHeight(int(height))

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._adjust_height()


class ChatArea(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("ChatArea")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.scroll = QScrollArea()
        self.scroll.setObjectName("ChatScrollArea")
        self.scroll.setWidgetResizable(True)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        self.scroll_content = QWidget()
        self.scroll_content.setObjectName("ChatScrollContent")
        self.message_layout = QVBoxLayout(self.scroll_content)
        self.message_layout.setContentsMargins(0, 0, 0, 0)
        self.message_layout.setSpacing(0)
        self.message_layout.addStretch()

        self.scroll.setWidget(self.scroll_content)
        layout.addWidget(self.scroll)

    def add_message(self, role: str, content: str) -> None:
        bubble = MessageBubble(role=role, content=content, timestamp=datetime.now())
        self.message_layout.insertWidget(self.message_layout.count() - 1, bubble)
        self._scroll_to_bottom()

    def _scroll_to_bottom(self) -> None:
        scrollbar = self.scroll.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
