# 05 — Proposed Technology Stack

This is a proposal, not a command to install everything immediately. Confirm compatibility with the actual dependency versions before choosing.

| Area | Candidate | Reason |
|---|---|---|
| Main language | Python | Familiar, broad ecosystem |
| IDE | VS Code | Already installed |
| Version control | Git | Already installed |
| Desktop UI | PySide6 | Native-feeling desktop UI and layouts |
| Local database | SQLite | No separate database server |
| Data validation | Pydantic | Typed settings and tool schemas |
| AI abstraction | Provider adapter interface | Avoid provider lock-in |
| Local API (if needed) | FastAPI | Typed local service endpoints |
| Voice | Pluggable STT/TTS components | Provider/model flexibility |
| Wake word | Local wake-word engine | Avoid continuous cloud audio |
| IoT | MQTT client/broker | Common lightweight messaging pattern |
| Tests | pytest | Unit and integration testing |
| Packaging | PyInstaller or equivalent | Consider only after stable app |

## Python compatibility note

The machine currently reports Python **3.14.6**. Some desktop, audio, AI, or hardware libraries may not yet provide compatible wheels for this version. Do not downgrade or uninstall the existing Python installation blindly.

Before implementation:
1. Check the supported Python versions for the chosen libraries.
2. If needed, install a second supported Python version side-by-side.
3. Use a project virtual environment.
4. Pin tested dependency versions.
5. Record the exact environment in the project documentation.

## Hardware-aware AI strategy

Laptop: Intel Core i3-7020U, 2 cores / 4 threads, 8 GB RAM, Intel integrated graphics, SSD + HDD.

- Use cloud AI for demanding reasoning when internet is available.
- Use small local models only after measuring memory and speed.
- Do not assume GPU acceleration.
- Do not keep multiple large models loaded simultaneously.
- Design a graceful offline mode for basic commands and local data.
- Keep model downloads optional and store large assets on the HDD if appropriate.
