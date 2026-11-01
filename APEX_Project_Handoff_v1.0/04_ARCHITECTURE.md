# 04 — Proposed System Architecture

## Architecture principles

- Modular monolith first; avoid premature microservices.
- UI, application logic, providers, tools, and persistence are separate layers.
- AI model/provider is replaceable.
- Tool execution is permission-gated and logged.
- Local-first storage for app settings and conversation history.
- Network services bind to localhost by default.

## Logical components

1. **Desktop UI** — navigation, chat, settings, status, visualizer.
2. **Application/Core** — session manager, message orchestration, task planner, permissions.
3. **AI Provider Adapter** — common interface for cloud/local model providers.
4. **Tool Registry** — registered tools with schemas, permission labels, and execution policies.
5. **Memory Service** — user-approved memory retrieval and updates.
6. **Persistence** — SQLite database and managed local files.
7. **Voice Layer** — wake word, speech-to-text, text-to-speech, audio state.
8. **PC Integration** — narrowly scoped Windows actions.
9. **Mobile Integration** — authenticated pairing and Android-supported operations.
10. **IoT Adapter** — MQTT or other explicitly configured protocols.
11. **Audit/Diagnostics** — action history, errors, and health checks.

## Suggested interaction flow

User input → UI → application orchestrator → policy/permission check → AI provider and/or approved tool → result verification → response → audit log.

The model must not directly execute arbitrary shell commands. It can propose a tool action; the application validates and authorizes it.

## Initial deployment

- Single-user Windows desktop process.
- Local SQLite database.
- Optional localhost API only when needed.
- No public inbound ports.
- Cloud provider calls only for user-requested or explicitly enabled operations.

## Future phone connection

- Pairing should use a deliberate user-approved process.
- Use encrypted authenticated communication.
- Prefer local network discovery or a secure relay; do not expose raw control ports to the public internet.
- Android functionality must stay within supported permissions and APIs.
