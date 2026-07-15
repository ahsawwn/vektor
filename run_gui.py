import multiprocessing
import sys
import time
from urllib.request import urlopen

from PySide6.QtCore import QTimer, QUrl, Qt
from PySide6.QtGui import QFont, QKeySequence, QShortcut
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PySide6.QtWebEngineWidgets import QWebEngineView


def _run_backend():
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, log_level="warning")


_BACKEND_URL = "http://127.0.0.1:8000"


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
        layout.addWidget(self.web)

        self._retry_count = 0
        self._try_load()

        fs = QShortcut(QKeySequence(Qt.Key.Key_F11), self)
        fs.activated.connect(self._toggle_fullscreen)
        esc = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
        esc.activated.connect(self._exit_fullscreen)

    def _try_load(self) -> None:
        try:
            urlopen(_BACKEND_URL, timeout=1)
            self.web.load(QUrl(_BACKEND_URL))
        except Exception:
            self._retry_count += 1
            if self._retry_count < 30:
                QTimer.singleShot(1000, self._try_load)
            else:
                self.web.setHtml(
                    "<html><body style='background:#0F172A;color:#EF4444;"
                    "font-family:monospace;padding:40px;'>"
                    "<h2>Backend failed to start</h2>"
                    "<p>Run <code>poetry run python -m backend.main</code> manually.</p>"
                    "</body></html>"
                )

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
