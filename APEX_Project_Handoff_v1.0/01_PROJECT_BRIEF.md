# 01 — Project Brief

## Product identity

- Product name: **APEX**
- Tagline: **Think • Assist • Achieve**
- Wake phrase: **“Hey Apex!!!”**
- Owner's friendly name for ChatGPT: “Buddy” (this is not the product name).
- APEX is the name of the assistant being developed.

## Vision

Create a personal AI assistant that feels like a reliable digital companion: conversational, useful, multilingual, privacy-conscious, and capable of taking approved actions across the user's PC, phone, projects, and supported IoT devices.

## Primary outcomes

1. A polished Windows desktop application.
2. Text and voice conversations with an AI backend.
3. Optional long-term memory controlled by the user.
4. Safe, permissioned PC automation.
5. Android companion features using supported Android APIs and explicit permissions.
6. Research, document, productivity, developer, and IoT capabilities.
7. Hybrid operation: local features remain useful offline; cloud services provide heavier reasoning when connected.

## Product principles

- Useful before flashy.
- Dark, spacious, clean UI.
- Permission before consequential actions.
- Local-first for sensitive state where practical.
- Cloud services are optional adapters, not hard dependencies in the core design.
- Modular architecture so providers and tools can be replaced.
- Explain what happened and verify actions.
- Never pretend an action succeeded when it did not.

## Target users and devices

Initial owner/operator: one person. Initial host: Windows laptop. Companion: Android phone. Later architecture may support additional devices, but multi-user support is out of scope for the first release.

## Success criteria for the first usable release

- Desktop app launches reliably.
- User can send and receive text messages.
- Conversation history persists locally.
- Settings are stored safely.
- AI provider can be configured without hardcoding secrets.
- Clear loading, error, offline, and permission states exist.
- No PC automation executes without an explicit permission policy.
