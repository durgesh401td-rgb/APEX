"""Configuration management for APEX."""

from pathlib import Path
from typing import Literal
from pydantic import BaseModel, Field

# Root directory of the APEX project
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"

# Ensure data and logs directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)


class AppConfig(BaseModel):
    """Core application settings and design tokens."""

    # Product Identity
    app_name: str = "APEX"
    tagline: str = "Think • Assist • Achieve"
    wake_phrase: str = "Hey Apex!!!"
    version: str = "0.1.0"

    # UI / Design Tokens
    theme: Literal["dark"] = "dark"
    bg_primary: str = "#080B12"       # Near-black navy
    surface_primary: str = "#111827"  # Graphite
    surface_elevated: str = "#151D2B" # Elevated panels
    border_color: str = "#1F2937"     # Subtle border
    accent_primary: str = "#168BFF"   # Electric blue
    accent_secondary: str = "#00D9FF" # Cyan / energy glow
    text_primary: str = "#EAF1FF"     # Soft white
    text_secondary: str = "#91A0B8"   # Slate blue-grey
    text_muted: str = "#64748B"       # Subtle muted text
    status_success: str = "#10B981"
    status_warning: str = "#F59E0B"
    status_error: str = "#EF4444"

    # Window geometry
    window_width: int = Field(default=1280, ge=800)
    window_height: int = Field(default=720, ge=600)
    min_width: int = 1024
    min_height: int = 640

    # Paths
    data_dir: Path = DATA_DIR
    db_path: Path = DATA_DIR / "apex.db"
    log_file: Path = LOGS_DIR / "apex.log"

    # Providers & Features
    ai_provider: str = "mock"  # Offline mock assistant for Stage 1


# Global configuration singleton
config = AppConfig()
