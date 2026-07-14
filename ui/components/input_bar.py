from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QLineEdit, QPushButton, QWidget

from ui.components.voice_toggle import VoiceToggle


class InputBar(QWidget):
    message_sent = Signal(str)
    voice_triggered = Signal()

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

        self.voice_toggle = VoiceToggle()
        self.voice_toggle.voice_triggered.connect(self.voice_triggered.emit)

        layout.addWidget(self.input_field, stretch=1)
        layout.addWidget(self.send_button)
        layout.addWidget(self.voice_toggle)

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
