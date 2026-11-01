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

## Stage 3 — Memory

- [x] Separate chat history from long-term memory in SQLite.
- [x] Implement MemoryService for user-approved facts and prompt context injection.
- [x] Build dedicated User Memory Vault screen (inspect, search, add, edit, delete).
- [x] Add explicit save/forget controls (never silently convert chats into memory).
- [x] Add memory pause/resume toggle with visual state indicator.
- [x] Add clear vault confirmation workflow.
- [x] Automated test coverage for memory persistence and UI.

## Stage 4 — Voice

- [x] Implement Push-to-Talk (press-and-hold mic button in composer).
- [x] Implement non-blocking Text-to-Speech (TTS) service using native Windows SAPI5 (`Microsoft David` deep, calm male voice).
- [x] Implement Speech-to-Text (STT) capture and adapter interface.
- [x] Add reactive visualizer states (idle, listening, thinking, speaking, muted).
- [x] Add physical/software mute controls and audio playback toggle.
- [x] Automated test coverage for voice state, TTS markdown sanitization, and STT workflow.

## Later stages

See `06_ROADMAP.md`. Do not start later-stage work before Stage 1 acceptance is met.
