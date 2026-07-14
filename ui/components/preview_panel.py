from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QVBoxLayout, QWidget
from PySide6.QtWebEngineWidgets import QWebEngineView


class PreviewPanel(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("PreviewPanel")
        self.setWindowTitle("Vektor — Live Preview")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.web_view = QWebEngineView()
        self.web_view.setObjectName("WebPreview")
        layout.addWidget(self.web_view)

    def load_file(self, path: Path | str) -> None:
        self.web_view.load(QUrl.fromLocalFile(str(path)))
        self.setVisible(True)

    def load_url(self, url: str) -> None:
        self.web_view.load(QUrl(url))
        self.setVisible(True)

    def reload(self) -> None:
        self.web_view.reload()
