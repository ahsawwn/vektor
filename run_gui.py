import multiprocessing
import sys
import time
from pathlib import Path

from PySide6.QtCore import QUrl, Qt
from PySide6.QtGui import QFont, QKeySequence, QShortcut
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PySide6.QtWebEngineWidgets import QWebEngineView

_FRONTEND_DIST = Path(__file__).parent / "frontend" / "dist"
_FRONTEND_INDEX = _FRONTEND_DIST / "index.html"


def _run_backend():
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, log_level="warning")


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Vektor")
        self.setMinimumSize(900, 600)
        self.showMaximized()
        self._fullscreen = False

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)

        self.web = QWebEngineView()
        self.web.setObjectName("WebEngine")

        if _FRONTEND_INDEX.exists():
            self.web.load(QUrl.fromLocalFile(str(_FRONTEND_INDEX)))
        else:
            self.web.load(QUrl("http://127.0.0.1:8000"))

        layout.addWidget(self.web)

        fs = QShortcut(QKeySequence(Qt.Key.Key_F11), self)
        fs.activated.connect(self._toggle_fullscreen)
        esc = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
        esc.activated.connect(self._exit_fullscreen)

    def _toggle_fullscreen(self) -> None:
        if self._fullscreen:
            self.showNormal()
        else:
            self.showFullScreen()
        self._fullscreen = not self._fullscreen

    def _exit_fullscreen(self) -> None:
        if self._fullscreen:
            self.showNormal()
            self._fullscreen = False


def main() -> None:
    proc = multiprocessing.Process(target=_run_backend, daemon=True)
    proc.start()
    time.sleep(1.5)

    app = QApplication(sys.argv)
    app.setApplicationName("Vektor")
    font = QFont("Inter", 10)
    app.setFont(font)

    window = MainWindow()
    window.show()
    exit_code = app.exec()
    proc.kill()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
