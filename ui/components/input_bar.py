from PySide6.QtCore import Signal
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QWidget,
)


class InputBar(QWidget):
    message_sent = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("InputBar")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.input_field = QLineEdit()
        self.input_field.setObjectName("InputField")
        self.input_field.setPlaceholderText("Ask Vektor anything...")
        self.input_field.returnPressed.connect(self._send_message)

        self.send_button = QPushButton("Send")
        self.send_button.setObjectName("SendButton")
        self.send_button.clicked.connect(self._send_message)

        layout.addWidget(self.input_field, stretch=1)
        layout.addWidget(self.send_button)

    def _send_message(self) -> None:
        text = self.input_field.text().strip()
        if text:
            self.message_sent.emit(text)
            self.input_field.clear()

    def set_input_enabled(self, enabled: bool) -> None:
        self.input_field.setEnabled(enabled)
        self.send_button.setEnabled(enabled)
        if enabled:
            self.input_field.setFocus()
