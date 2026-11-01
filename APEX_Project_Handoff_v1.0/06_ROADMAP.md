# 06 — Development Roadmap

Each milestone follows: **Learn → Prepare → Build → Verify**.

## Stage 0 — Environment & feasibility
Status: completed planning checks.
- Windows version/build, ESU, CPU/RAM, disks, Python, Git, VS Code, Android, network, budget.
- Before coding: verify disk-letter mapping and free space again if it has changed.

## Stage 1 — APEX Core Desktop
- Create repository and isolated Python environment.
- Establish app entry point and logging.
- Build navigation shell and dark design system.
- Build dedicated Home and Chat pages.
- Add local settings and SQLite conversation history.
- Verify launch, persistence, resizing, and error handling.

## Stage 2 — AI Provider Connection
- Define provider adapter interface.
- Add one provider selected by the owner.
- Store secrets using a secure OS-backed credential store.
- Add timeout, retry, cancellation, and usage visibility.
- Verify offline/error behavior and never log secrets.

## Stage 3 — Memory
- Separate chat history from long-term memory.
- Add explicit save/forget controls.
- Add memory inspection and deletion workflow.
- Verify that unapproved content is not silently promoted to memory.

## Stage 4 — Voice
- Add push-to-talk first.
- Add speech-to-text and text-to-speech adapters.
- Add local wake-word detection after push-to-talk is stable.
- Show microphone activity and provide a physical/software mute.
- Verify Hindi, Marathi, and English as supported by selected services.

## Stage 5 — Safe PC Automation
- Start with low-risk allowlisted actions (e.g. open approved applications).
- Add typed tool schemas, permission checks, confirmation prompts, audit trail.
- Add emergency stop.
- Never allow model-generated arbitrary shell execution.

## Stage 6 — Android Companion
- Pairing and authentication.
- File transfer and clipboard sync with user consent.
- Media controls and supported app/deep-link actions.
- Respect Android permission and background execution limits.

## Stage 7 — Vision, Research & Productivity
- User-selected screenshots and document import.
- Web research with source tracking.
- Tasks, reminders, calendar/email only after explicit integration setup.
- Safe downloads and file operations.

## Stage 8 — IoT & Advanced Agents
- MQTT test environment.
- ESP8266/ESP32 integrations.
- Specialized agents with constrained tool permissions.
- Proactive suggestions and pre-approved workflows.

## Release gates

Do not move to the next stage until the current stage's acceptance criteria and tests pass. Keep the first release small and reliable.
