# 14 — Initial Backlog

## Stage 1 — Core desktop

- [x] Inspect current workspace and Git state.
- [x] Confirm project directory and naming.
- [x] Check available Python interpreters and package compatibility.
- [x] Create isolated project environment after approval.
- [x] Establish logging and configuration.
- [x] Create desktop window shell.
- [x] Implement sidebar navigation.
- [x] Create separate Home and Chat pages.
- [x] Implement chat composer and local demo response.
- [x] Add SQLite conversation persistence.
- [x] Add Settings page and theme tokens.
- [x] Add tests and setup documentation.

## Stage 2 — AI connection

- [x] Select a provider with free-tier/zero-cost option (Google Gemini 2.5 Flash).
- [x] Confirm provider terms and data handling.
- [x] Implement provider adapter (BaseAIProvider, MockAIProvider, GeminiAIProvider, ProviderRegistry).
- [x] Add secure credential storage (Windows Credential Manager / keyring).
- [x] Add timeout/cancel/error handling (AIWorkerThread with stop generation).
- [x] Display usage and connection state (Dynamic provider status pill & real-time connection tester).

## Later stages

See `06_ROADMAP.md`. Do not start later-stage work before Stage 1 acceptance is met.
