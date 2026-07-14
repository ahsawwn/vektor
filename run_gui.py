import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

from ui.app import MainWindow


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("Vektor")
    app.setOrganizationName("ahsawwn")

    font = QFont("JetBrains Mono", 10)
    font.setStyleHint(QFont.StyleHint.Monospace)
    app.setFont(font)

    stylesheet_path = Path(__file__).parent / "ui" / "assets" / "style.qss"
    if stylesheet_path.exists():
        with open(stylesheet_path) as f:
            app.setStyleSheet(f.read())

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
