# 10 — Test Strategy

## Test levels

- Unit tests: isolated logic, settings validation, permission decisions.
- Integration tests: database, AI adapter, tool registry.
- UI tests: navigation, resizing, keyboard access, dialogs.
- Security tests: secret leakage, denied permissions, prompt injection boundaries.
- Manual tests: microphone, audio devices, Windows integration, Android pairing.

## Stage 1 acceptance criteria

- App launches from the documented command.
- Main window opens at target laptop resolution.
- Sidebar navigation works.
- Home and Chat are separate pages.
- Chat composer accepts text and displays a local demo response before cloud AI is connected.
- Conversation persists after restart.
- Settings persist after restart.
- UI remains responsive during simulated waiting.
- Errors are visible and understandable.
- No credentials are present in source files or logs.

## Automation acceptance criteria

- Unapproved actions are blocked.
- Sensitive actions require confirmation.
- Every action reports success/failure accurately.
- Emergency stop halts queued actions.
- Tests cover denied, cancelled, failed, and successful actions.

## Performance checks

- Measure startup time and idle memory.
- Test at 1280×720 and smaller window sizes.
- Avoid heavy background animations.
- Keep local AI disabled until resource usage is measured.
