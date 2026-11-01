"""APEX Desktop Application Entry Point."""

import sys
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication
from apex.core.config import config
from apex.core.logging import logger
from apex.ui.main_window import MainWindow
from apex.ui.styles.qss import get_application_stylesheet


def main() -> int:
    """Launch the APEX desktop application."""
    logger.info("Starting %s v%s", config.app_name, config.version)

    # Initialize Qt Application
    app = QApplication(sys.argv)
    app.setApplicationName(config.app_name)
    app.setApplicationVersion(config.version)

    # Apply typography font
    font = QFont("Segoe UI", 10)
    font.setStyleHint(QFont.StyleHint.SansSerif)
    app.setFont(font)

    # Apply Dark Stylesheet
    stylesheet = get_application_stylesheet()
    app.setStyleSheet(stylesheet)

    # Create & display primary window
    window = MainWindow()
    window.show()

    logger.info("Window displayed at %dx%d", config.window_width, config.window_height)
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
