# 09 — Data & Memory Plan

## Data categories

1. App settings — theme, preferences, provider selection.
2. Conversation history — messages and timestamps.
3. Long-term memory — only user-approved facts/preferences.
4. Project knowledge — documents and notes explicitly added by the user.
5. Tool/action history — action type, permission decision, outcome, timestamp.
6. Credentials — stored separately in OS-backed secure storage.

## Principles

- Separate conversation history from long-term memory.
- Do not silently convert every chat into persistent memory.
- Let the user inspect, edit, pause, and clear memory.
- Provide deletion for individual records and all app-managed memory.
- Keep raw audio/video only when explicitly requested and explain retention.
- Minimize collected data.
- Do not send local documents to cloud providers without user consent.

## Initial persistence

SQLite is the proposed local database for settings, conversations, memory metadata, and action records. Large files should remain in user-selected folders with references stored in the database.

## Backup

- User-selected backup location.
- Optional encrypted backup.
- Test restore, not just backup creation.
- Avoid syncing sensitive data to a cloud service by default.
