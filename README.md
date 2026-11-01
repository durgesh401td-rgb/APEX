# 🚀 APEX — Personal AI Assistant

> **Think • Assist • Achieve**  
> *Wake phrase: "Hey Apex!!!"*

![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg)
![UI Framework](https://img.shields.io/badge/GUI-PySide6%20(Qt6)-41CD52.svg)
![AI Backend](https://img.shields.io/badge/AI-Google%20Gemini%20%7C%20Mock-orange.svg)
![Voice](https://img.shields.io/badge/Voice-Windows%20SAPI5%20(Deep%20Calm%20Male)-cyan.svg)
![Security](https://img.shields.io/badge/Security-Windows%20Credential%20Manager%20(DPAPI)-success.svg)
![Tests](https://img.shields.io/badge/Tests-28%20Passing-brightgreen.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%2010%2F11-0078D6.svg)

**APEX** is a personal AI assistant desktop ecosystem built specifically for Windows. Engineered from the ground up to be **privacy-first**, **local-first**, and **resource-conscious**, APEX pairs an elegant, dark, spacious desktop interface with pluggable AI models, long-term contextual memory, native voice interactions, and a secure credential architecture.

---

## 📸 Overview & Design Philosophy

APEX is designed around four core tenets:

1. **Dark, Clean, Spacious Aesthetics:** A distraction-free canvas built with custom design tokens (`#080B12` deep space navy canvas, `#111827` graphite cards, `#168BFF` electric blue, and `#00D9FF` cyan accents) paired with clean geometric visualizers.
2. **Local-First & Privacy-Obsessed:** All conversation histories, settings, and memory records live in local SQLite databases on your machine. API keys are locked inside Windows Credential Manager via DPAPI; zero telemetry, zero unexpected data leaks.
3. **Hardware Efficiency:** Designed and optimized for everyday consumer laptops and workstations (including dual-core Intel Core i3 machines with 8 GB RAM) through non-blocking asynchronous Qt worker threads and lazy audio loading.
4. **Autonomous Extensibility:** Pluggable AI engines allow instant switching between cloud-scale reasoning (Google Gemini 2.5 Flash free tier) and offline mock/local testing.

---

## ⚡ Implemented Capabilities

### 🖥️ Stage 1: Core Desktop Shell
- **PySide6 (Qt6) Application Architecture:** Responsive desktop window (1280x720 default) with custom sidebar navigation rail (`Home`, `Chat`, `Memory`, `Settings`).
- **Dynamic Geometric Visualizer:** Real-time animated core visualizer featuring dynamic breathing, rotational arcs, and ambient glow that reacts to system and voice states.
- **SQLite Data Layer:** Thread-safe local SQLite storage (`apex/core/database.py`) with foreign key constraints, automatic indexing, and clean connection lifecycle management.
- **Redacted Structured Logging:** Production logger with custom `SensitiveDataFilter` ensuring API keys, passwords, and authorization tokens never leak into console or log files.

### 🧠 Stage 2: Pluggable AI Provider Engine
- **Provider Abstraction:** Unified `BaseAIProvider` protocol and `ProviderRegistry` supporting runtime dynamic provider switching.
- **Google Gemini Integration:** Direct support for `gemini-2.5-flash` and `gemini-1.5-flash` using the official `google-genai` SDK.
- **Offline Mock Provider:** Built-in offline testing engine that simulates realistic AI streaming responses without requiring internet access or API quotas.
- **Windows Credential Manager Security:** Leverages system DPAPI via `keyring` (`apex/core/credentials.py`) so API keys are never stored in plain-text `.env` or config files.
- **Non-Blocking Background Workers:** `AIWorkerThread` handles all network I/O off the main thread, supporting real-time token streaming and immediate user-initiated generation cancellation.

### 💾 Stage 3: Long-Term Memory Vault
- **Memory Management Page:** Full-featured user vault to view, search, categorize, edit, delete, and toggle long-term personal facts and preferences.
- **Category Taxonomies:** Tag memories as `preference`, `fact`, `instruction`, `work`, or `general`.
- **System Prompt Context Injection:** Active memories are automatically synthesized and injected into AI system prompts, giving APEX continuous context across sessions.
- **In-Chat Quick Memory Capture:** Prefix any message with `remember: <fact>` to instantly store information directly into the vault from chat.

### 🎙️ Stage 4: Voice & Audio Layer
- **Deep, Calm Male Voice (SAPI5):** Built-in native Windows SAPI5 text-to-speech engine (`Microsoft David`) configured at 145 WPM for a composed, reliable, fee-free voice experience.
- **Push-to-Talk Speech Capture:** Microphone listener integrating native Windows speech recognition with silence detection and clean input buffering.
- **Reactive Voice State Engine:** Visualizer states transition dynamically between `idle`, `listening`, `thinking`, `speaking`, and `muted`.
- **Chat Bubble Speech Controls:** Replay or read aloud any assistant message with a single click on the audio icon.

---

## 🗺️ Roadmap & Upcoming Milestones

```
[✅] Stage 1: Desktop Shell & Theme (PySide6, SQLite, Redacted Logs)
[✅] Stage 2: AI Provider Engine (Google Gemini Free Tier, Mock, Keyring DPAPI)
[✅] Stage 3: Memory Vault (Persistent User Preferences & Context Injection)
[✅] Stage 4: Native Windows Voice Layer (Push-to-Talk, SAPI5 Deep Voice)
[  ] Stage 5: Safe PC Automation (Typed Tools, Allowlisted App Execution, Killswitch)
[  ] Stage 6: Android Companion (Jetpack Compose, Local Pair-to-Sync)
[  ] Stage 7: Vision & Document Intelligence (Local PDF Search, OCR, Screen Context)
[  ] Stage 8: IoT & Smart Home Hub (Home Assistant Integration & Automations)
```

---

## 📂 Project Architecture

```
d:\Apex\
├── run.py                          # Convenient application launcher
├── launch_apex.bat                 # One-click Windows desktop runner
├── pyproject.toml                  # Dependencies & tool configurations
├── README.md                       # Repository documentation
├── .gitignore                      # Git ignore rules
│
├── apex/
│   ├── app.py                      # Application bootstrap & Qt event loop
│   ├── core/
│   │   ├── config.py               # Settings, color palettes, and constants
│   │   ├── database.py             # SQLite persistence (threads, chats, memories)
│   │   ├── logging.py              # Secret-redacting structured logging
│   │   ├── credentials.py          # Windows Credential Manager DPAPI vault
│   │   ├── memory.py               # MemoryService for storing & querying context
│   │   ├── ai/
│   │   │   ├── base.py             # BaseAIProvider interface & ResponseChunk
│   │   │   ├── registry.py         # ProviderRegistry for dynamic switching
│   │   │   ├── mock_provider.py    # Offline simulated provider
│   │   │   └── gemini_provider.py  # Google Gemini SDK provider
│   │   └── voice/
│   │       ├── state.py            # Reactive VoiceStateManager & state observer
│   │       ├── tts.py              # Windows SAPI5 Speech Synthesizer engine
│   │       └── stt.py              # Push-to-Talk speech recognizer
│   │
│   └── ui/
│       ├── main_window.py          # Primary 1280x720 window shell & router
│       ├── styles/
│       │   ├── palette.py          # Design tokens & color hex constants
│       │   └── qss.py              # Application-wide dark stylesheet
│       ├── widgets/
│       │   ├── nav_rail.py         # Left vertical navigation sidebar
│       │   ├── visualizer.py       # Geometric "A" core with pulse & orbit rings
│       │   └── chat_bubble.py      # Styled message cards with audio replay
│       └── pages/
│           ├── home_page.py        # Greeting, visualizer, quick action cards
│           ├── chat_page.py        # Multi-session chat drawer & composer
│           ├── memory_page.py      # Vault manager (search, filter, edit cards)
│           ├── settings_page.py    # AI provider config, voice, & appearance tabs
│           └── placeholder_page.py # Clean placeholders for upcoming stages
│
└── tests/
    ├── conftest.py                 # Pytest fixtures & isolated in-memory DBs
    ├── test_config.py              # Config validation & secret redaction tests
    ├── test_database.py            # SQLite schema, indices, & session tests
    ├── test_providers.py           # Gemini & Mock AI provider tests
    ├── test_memory.py              # Memory CRUD, categories, & prompt injection tests
    ├── test_voice.py               # Voice states, SAPI5 TTS, & STT tests
    └── test_ui_smoke.py            # Headless UI integration & navigation tests
```

---

## 🚀 Quickstart

### Prerequisites
- **Operating System:** Windows 10 or Windows 11 (64-bit)
- **Python:** Python 3.12+ installed (or installed hermetically via `uv`)

### 1. Clone the Repository
```bash
git clone https://github.com/durgesh401td-rgb/APEX.git
cd APEX
```

### 2. Set Up Virtual Environment & Dependencies
```powershell
# Create virtual environment
python -m venv .venv

# Activate environment
.\.venv\Scripts\Activate.ps1

# Upgrade pip & install dependencies
pip install -e .
```

### 3. Launch APEX Desktop
Double-click `launch_apex.bat` in File Explorer, or run:
```powershell
python run.py
```

### 4. Configure Your AI Provider
1. In APEX, click the **Settings** icon on the left navigation rail.
2. Select **Google Gemini** as the active provider.
3. Paste your Gemini API key (obtainable free from [Google AI Studio](https://aistudio.google.com/)).
4. Click **Save Configuration**. Your key is securely saved into **Windows Credential Manager** (encrypted with Windows DPAPI).
5. Open the **Chat** page and say: *"Hey Apex, who are you?"*

---

## 🧪 Testing & Verification

APEX comes with an automated test suite covering unit logic, database migrations, AI providers, memory vault, voice states, and headless Qt UI navigation.

Run tests using `pytest`:
```powershell
.\.venv\Scripts\pytest -v
```

Expected result:
```text
============================== 28 passed in 3.14s ==============================
```

---

## 🔒 Security & Privacy Commitments

- **No Secret Leakage:** Logs automatically scrub any string matching API key or password formats.
- **Hardware DPAPI Protection:** Keys are never written to plain JSON, YAML, or `.env` files.
- **Strict User Consent:** All future automation capabilities (Stage 5+) adhere to explicit confirmation gates and an immediate emergency stop mechanism.

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
