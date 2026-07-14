from PySide6.QtCore import Signal, Qt, QTimer
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget


class VoiceToggle(QWidget):
    voice_triggered = Signal()
    recording_started = Signal()
    recording_finished = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("VoiceToggle")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self.button = QPushButton("🎤")
        self.button.setObjectName("SendButton")
        self.button.setFixedWidth(40)
        self.button.setToolTip("Hold Space to record")
        self.button.clicked.connect(self._toggle_recording)
        layout.addWidget(self.button)

        self.indicator = QLabel("")
        self.indicator.setStyleSheet("color: #22C55E; font-size: 16px;")
        self.indicator.setVisible(False)
        layout.addWidget(self.indicator)

        self._is_recording = False
        self._animation_timer = QTimer()
        self._animation_timer.setInterval(300)
        self._animation_timer.timeout.connect(self._animate)
        self._animation_dots = 0

    def _toggle_recording(self) -> None:
        if self._is_recording:
            self._stop_recording_ui()
        else:
            self._start_recording_ui()

    def _start_recording_ui(self) -> None:
        self._is_recording = True
        self.indicator.setVisible(True)
        self.indicator.setText("●")
        self._animation_dots = 0
        self._animation_timer.start()
        self.recording_started.emit()

    def _stop_recording_ui(self) -> None:
        self._is_recording = False
        self._animation_timer.stop()
        self.indicator.setVisible(False)
        self.recording_finished.emit("")

    def _animate(self) -> None:
        self._animation_dots = (self._animation_dots + 1) % 4
        self.indicator.setText("●" + "." * self._animation_dots)

    def set_recording(self, recording: bool) -> None:
        if recording:
            self._start_recording_ui()
        else:
            self._stop_recording_ui()

    @property
    def is_recording(self) -> bool:
        return self._is_recording
