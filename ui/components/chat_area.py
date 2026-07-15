from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)


class MessageBubble(QFrame):
    def __init__(
        self,
        role: str,
        content: str,
        timestamp: datetime | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.NoFrame)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(8)

        role_label = QLabel()
        role_label.setObjectName("MessageRole")

        ts_label = QLabel()
        ts_label.setObjectName("MessageTimestamp")
        if timestamp:
            ts_label.setText(timestamp.strftime("%H:%M"))
        ts_label.setVisible(timestamp is not None)

        header_layout.addWidget(role_label)
        header_layout.addWidget(ts_label)
        header_layout.addStretch()
        layout.addWidget(header)

        self.text_browser = QTextBrowser()
        self.text_browser.setObjectName("MessageContent")
        self.text_browser.setOpenExternalLinks(True)
        self.text_browser.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.text_browser.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.text_browser.setMarkdown(content)
        self.text_browser.document().setDocumentMargin(8)
        self.text_browser.setFrameShape(QTextBrowser.Shape.NoFrame)
        layout.addWidget(self.text_browser)

        if role == "user":
            self.setProperty("msgRole", "user")
            role_label.setText("You")
            role_label.setStyleSheet("color: #60A5FA; font-weight: 700; font-size: 11px; text-transform: uppercase;")
        elif role == "system":
            self.setProperty("msgRole", "system")
            role_label.setText("System")
            role_label.setStyleSheet("color: #94A3B8; font-weight: 700; font-size: 11px; text-transform: uppercase;")
        else:
            self.setProperty("msgRole", "assistant")
            role_label.setText("Vektor")
            role_label.setStyleSheet("color: #A78BFA; font-weight: 700; font-size: 11px; text-transform: uppercase;")

        self.style().unpolish(self)
        self.style().polish(self)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        doc = self.text_browser.document()
        doc.setTextWidth(self.text_browser.viewport().width())
        self.text_browser.setFixedHeight(int(doc.size().height() + 16))


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
