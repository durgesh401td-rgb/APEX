# APEX — Personal AI Assistant

> **Think • Assist • Achieve**  
> Wake phrase: “Hey Apex!!!”

APEX is a personal AI assistant desktop ecosystem for Windows (with Android companion planned), built with a calm, dark, clean, and spacious user interface.

---

## Stage 1 — Core Desktop Baseline (Complete)

- **UI Framework:** PySide6 (Qt 6)
- **Design Tokens:** Deep near-black navy canvas (`#080B12`), graphite panels (`#111827`), electric blue (`#168BFF`), and cyan accents (`#00D9FF`).
- **Persistence:** Local SQLite database storing conversation sessions, message history, and user settings.
- **Security & Privacy:** Redacted logging (no secrets/tokens leaked), zero external telemetry, local-first architecture.
- **Hardware Optimization:** Lightweight CPU/RAM footprint engineered for Intel Core i3 with 8 GB RAM.

---

## Quickstart

### 1. Activate Environment
Using PowerShell in `d:\Apex`:
```powershell
.\.venv\Scripts\Activate.ps1
```

### 2. Launch APEX Desktop
```powershell
python run.py
```
*(or `python -m apex.app`)*

### 3. Run Automated Tests
```powershell
pytest -v
```

---

## Project Structure

```
d:\Apex\
├── run.py                          # Convenient root launch script
├── pyproject.toml                  # Project dependencies and configuration
├── .gitignore                      # Git ignore rules
├── APEX_Project_Handoff_v1.0/      # Source-of-truth specifications & roadmap
├── apex/
│   ├── app.py                      # Application bootstrap & Qt event loop
│   ├── core/
│   │   ├── config.py               # Typed configuration & design tokens
│   │   ├── logging.py              # Secret-redacting structured logger
│   │   └── database.py             # SQLite persistence (threads, FKs, indices)
│   └── ui/
│       ├── main_window.py          # Primary 1280x720 window shell & router
│       ├── styles/
│       │   ├── palette.py          # Color hexes & design tokens
│       │   └── qss.py              # Application-wide dark stylesheet
│       ├── widgets/
│       │   ├── nav_rail.py         # Left navigation sidebar
│       │   ├── visualizer.py       # Geometric "A" core with ambient pulse
│       │   └── chat_bubble.py      # Styled user & assistant message cards
│       └── pages/
│           ├── home_page.py        # Greeting, visualizer, quick action cards
│           ├── chat_page.py        # Multi-session chat drawer & composer
│           ├── settings_page.py    # General, AI provider & appearance tabs
│           └── placeholder_page.py # Roadmap placeholders for upcoming stages
└── tests/
    ├── test_config.py              # Token & secret redaction tests
    ├── test_database.py            # SQLite conversation & settings tests
    └── test_ui_smoke.py            # Headless UI integration & navigation tests
```

---

## Next Milestone: Stage 2 (AI Provider Connection)

In Stage 2, APEX will connect its chat composer to real AI providers (Google Gemini / OpenAI / local Ollama) via a pluggable adapter interface, with zero credentials hardcoded (integrating Windows Credential Manager).
