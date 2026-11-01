# 11 — Risks & Constraints

| Risk | Impact | Mitigation |
|---|---|---|
| 8 GB RAM / dual-core CPU | Heavy models and multiple services may be slow | Cloud-first for heavy reasoning; lightweight local tasks |
| Python 3.14 library gaps | Some packages may not install | Check compatibility; use side-by-side interpreter if needed |
| Zero budget | Paid APIs or hosting may be unavailable | Free/open-source first; provider adapter; monitor free-tier limits |
| Mobile hotspot dependence | Cloud functions fail when disconnected | Offline states and local fallback |
| Windows 10 | OS lifecycle/security constraints | ESU enrollment reported by owner; keep updates enabled and periodically verify |
| Android restrictions | Some apps/actions cannot be controlled | Use supported APIs and permissions; explain limits |
| Prompt injection | Malicious content may try to trigger actions | Treat external content as untrusted; permission gate tools |
| Autonomous file operations | Data loss | Scoped paths, previews, confirmations, backups |
| Always-on microphone | Privacy and resource concerns | Local wake word, visible indicator, mute control |
| Remote control exposure | Unauthorized access | No public control ports; authenticated encrypted pairing |

## Known environment constraints

- Windows 10 Home Single Language, version 22H2, OS build 19045.7807 (reported from screenshot).
- Owner reports enrollment in Windows 10 ESU; verify update status periodically.
- Intel Core i3-7020U, 2 cores / 4 logical processors.
- 8 GB RAM.
- Disk 0: 238.46 GB SSD, C: partition 237.83 GB, approximately 105.79 GB free at time of check.
- Disk 1: 465.76 GB HDD, D:/E:/F: partitions, approximately 460 GB free combined at time of check.
- Python 3.14.6.
- Git 2.55.0.windows.1.
- VS Code 1.142.0.
- Phone: itel A95 5G, Android 14.
- Internet: mobile hotspot, unlimited 5G plan reported.
- Budget: ₹0.

Storage free-space figures are snapshots and must be rechecked before installing models or large dependencies.
