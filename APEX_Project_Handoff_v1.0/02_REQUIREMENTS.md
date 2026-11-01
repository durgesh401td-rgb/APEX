# 02 — Product Requirements

Priorities: **P0** essential foundation; **P1** next; **P2** later; **P3** exploratory.

## Functional requirements

| ID | Priority | Requirement |
|---|---|---|
| FR-001 | P0 | APEX shall launch as a Windows desktop application. |
| FR-002 | P0 | APEX shall provide a text chat interface. |
| FR-003 | P0 | APEX shall persist conversations locally. |
| FR-004 | P0 | APEX shall provide settings for appearance and AI provider configuration. |
| FR-005 | P0 | APEX shall show clear connection, loading, and error states. |
| FR-006 | P0 | Secrets shall not be stored in source code or plain-text configuration. |
| FR-007 | P1 | APEX shall support a provider-independent AI adapter interface. |
| FR-008 | P1 | APEX shall support English, Hindi, and Marathi interaction where providers/models permit. |
| FR-009 | P1 | APEX shall support voice input and speech output. |
| FR-010 | P1 | APEX shall offer local wake-word detection with a visible microphone state. |
| FR-011 | P1 | APEX shall support user-controlled memory with inspect/edit/clear controls. |
| FR-012 | P1 | APEX shall support approved desktop actions such as opening applications. |
| FR-013 | P1 | APEX shall request confirmation for sensitive or destructive actions. |
| FR-014 | P2 | APEX shall provide an Android companion for approved integrations. |
| FR-015 | P2 | APEX shall support document and screenshot understanding. |
| FR-016 | P2 | APEX shall support web research through an explicit, auditable tool layer. |
| FR-017 | P2 | APEX shall support reminders and task management. |
| FR-018 | P2 | APEX shall support IoT integration using a broker/protocol such as MQTT. |
| FR-019 | P3 | APEX may support multiple specialized agents coordinated by a main planner. |
| FR-020 | P3 | APEX may support proactive suggestions and pre-approved workflows. |

## Non-functional requirements

- NFR-001: Must be usable on 8 GB RAM and a dual-core Intel i3-class laptop.
- NFR-002: Must avoid running heavyweight local models by default.
- NFR-003: Core chat and settings should remain responsive while background work runs.
- NFR-004: UI must be dark, uncluttered, and responsive to window resizing.
- NFR-005: Data and secrets must be handled according to the security specification.
- NFR-006: Modules should have clear boundaries and testable interfaces.
- NFR-007: The application must provide useful offline states; cloud AI is not assumed to be always available.
- NFR-008: Free-tier limits, data usage, and provider terms must be checked before enabling a service.

## Out of scope for initial release

- Unrestricted remote access to the PC.
- Bypassing Windows lock screen or Android security restrictions.
- Autonomous purchases, payments, or account changes.
- Always-on cloud audio streaming.
- Training a foundation model from scratch.
- Guaranteed control of every third-party phone application.
- Paid infrastructure unless separately approved.
