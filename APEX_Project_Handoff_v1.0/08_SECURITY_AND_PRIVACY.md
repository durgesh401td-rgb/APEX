# 08 — Security & Privacy Requirements

## Trust boundaries

Treat model output, websites, emails, PDFs, documents, screenshots, and tool results as untrusted data. They may contain prompt injection or malicious instructions. They cannot override APEX's system policy or user permissions.

## Permission model

- Read-only actions: may be allowed within clearly scoped locations.
- Reversible low-risk actions: may be allowed after user configuration.
- File modification, deletion, software installation, settings changes, messages, external sharing, and remote control: require explicit confirmation unless a narrowly defined workflow has been pre-approved.
- Payments, purchases, credential changes, and other high-impact actions: require direct user action; do not automate in initial releases.

## Credentials

- Never place keys in source code, screenshots, logs, or Git.
- Use Windows Credential Manager or another vetted OS-backed secret store.
- Use `.env` only for local development when excluded from Git; it is not a secure vault.
- Provide a way to revoke and replace provider credentials.

## Network

- Bind local services to localhost by default.
- Use authenticated encrypted channels for device pairing.
- Do not expose raw control endpoints or ports to the internet.
- Avoid automatic UPnP/router port forwarding.
- Verify peer identity before accepting phone commands.

## Voice and camera

- Wake-word detection should be local where feasible.
- Do not continuously upload microphone audio by default.
- Always show microphone/camera activity.
- Provide mute/disable controls.
- Camera access must be explicit and session-scoped.

## Windows and Android

- Do not bypass lock screens.
- Background tasks while locked must be explicitly permitted and must not simulate interactive user control.
- Use supported Windows APIs and Android permissions.
- Explain permission use before requesting it.

## Recovery

- Maintain backups of application data.
- Offer emergency stop through UI and keyboard shortcut.
- Provide an automation pause switch.
- Record action outcome and errors without storing unnecessary sensitive content.
