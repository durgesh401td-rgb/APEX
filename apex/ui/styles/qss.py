"""Qt Style Sheet (QSS) generator for APEX."""

from apex.ui.styles.palette import (
    BG_DARK,
    SURFACE_PRIMARY,
    SURFACE_ELEVATED,
    SURFACE_HOVER,
    BORDER_COLOR,
    BORDER_FOCUS,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    TEXT_MUTED,
    ACCENT_PRIMARY,
    ACCENT_CYAN,
    STATUS_ONLINE,
)


def get_application_stylesheet() -> str:
    """Return the global QSS stylesheet for the APEX application."""
    return f"""
    /* Global Application Reset */
    QMainWindow, QWidget {{
        background-color: {BG_DARK};
        color: {TEXT_PRIMARY};
        font-family: "Segoe UI", Inter, -apple-system, BlinkMacSystemFont, sans-serif;
        font-size: 13px;
        selection-background-color: {ACCENT_PRIMARY};
        selection-color: #FFFFFF;
    }}

    /* Scrollbars */
    QScrollBar:vertical {{
        background-color: transparent;
        width: 8px;
        margin: 0px;
    }}
    QScrollBar::handle:vertical {{
        background-color: {SURFACE_HOVER};
        min-height: 24px;
        border-radius: 4px;
    }}
    QScrollBar::handle:vertical:hover {{
        background-color: {TEXT_MUTED};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
        background: none;
        height: 0px;
    }}

    /* Navigation Rail */
    #navRail {{
        background-color: {SURFACE_PRIMARY};
        border-right: 1px solid {BORDER_COLOR};
    }}

    /* Navigation Buttons */
    QPushButton.nav-btn {{
        background-color: transparent;
        color: {TEXT_SECONDARY};
        text-align: left;
        padding: 10px 16px;
        border: none;
        border-radius: 8px;
        font-weight: 500;
        font-size: 13px;
    }}
    QPushButton.nav-btn:hover {{
        background-color: {SURFACE_HOVER};
        color: {TEXT_PRIMARY};
    }}
    QPushButton.nav-btn:checked {{
        background-color: {SURFACE_ELEVATED};
        color: {ACCENT_CYAN};
        font-weight: 600;
        border-left: 3px solid {ACCENT_PRIMARY};
    }}

    /* Content Cards */
    QFrame.content-card {{
        background-color: {SURFACE_PRIMARY};
        border: 1px solid {BORDER_COLOR};
        border-radius: 12px;
        padding: 20px;
    }}
    QFrame.content-card:hover {{
        border: 1px solid {SURFACE_HOVER};
    }}

    /* Action Buttons */
    QPushButton.action-btn {{
        background-color: {ACCENT_PRIMARY};
        color: #FFFFFF;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
        font-size: 13px;
    }}
    QPushButton.action-btn:hover {{
        background-color: #2B96FF;
    }}
    QPushButton.action-btn:pressed {{
        background-color: #0F75DC;
    }}

    QPushButton.secondary-btn {{
        background-color: {SURFACE_ELEVATED};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER_COLOR};
        border-radius: 8px;
        padding: 10px 18px;
        font-weight: 500;
    }}
    QPushButton.secondary-btn:hover {{
        background-color: {SURFACE_HOVER};
        border-color: {TEXT_MUTED};
    }}

    /* Chat Text Input & Composer */
    QTextEdit, QLineEdit {{
        background-color: {SURFACE_PRIMARY};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER_COLOR};
        border-radius: 10px;
        padding: 12px 14px;
        font-size: 14px;
    }}
    QTextEdit:focus, QLineEdit:focus {{
        border: 1px solid {BORDER_FOCUS};
        background-color: {SURFACE_ELEVATED};
    }}

    /* Labels */
    QLabel {{
        color: {TEXT_PRIMARY};
    }}
    QLabel.heading-1 {{
        font-size: 24px;
        font-weight: 700;
        color: {TEXT_PRIMARY};
    }}
    QLabel.heading-2 {{
        font-size: 18px;
        font-weight: 600;
        color: {TEXT_PRIMARY};
    }}
    QLabel.subheading {{
        font-size: 14px;
        color: {TEXT_SECONDARY};
    }}
    QLabel.caption {{
        font-size: 12px;
        color: {TEXT_MUTED};
    }}

    /* Status Pill */
    QLabel.status-pill {{
        background-color: rgba(16, 185, 129, 0.12);
        color: {STATUS_ONLINE};
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 12px;
        padding: 4px 10px;
        font-size: 11px;
        font-weight: 600;
    }}
    """
