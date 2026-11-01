# 03 — UI/UX Specification

## Design direction

**Dark • Clean • Spacious • Premium • Futuristic, but restrained.**

Use the supplied dashboard image as a visual direction reference. Do not reproduce its information density literally. The interface must feel calm and spacious.

## Visual system

- Main background: near-black navy, approximately `#080B12`.
- Surface/panels: graphite, approximately `#111827`.
- Elevated surface: `#151D2B`.
- Primary accent: electric blue, approximately `#168BFF`.
- Secondary accent: cyan, approximately `#00D9FF`.
- Primary text: soft white, approximately `#EAF1FF`.
- Secondary text: muted blue-grey, approximately `#91A0B8`.
- Success: restrained green; warning/error colors only for meaningful states.
- Typography: Inter or a clean system sans-serif fallback.
- Corner radius: generally 10–14 px.
- Shadows/glows: subtle and sparse; avoid neon outlines around every component.
- Motion: short, calm transitions; respect reduced-motion settings.

## Layout rules

- Use a persistent left navigation rail/sidebar.
- Main content area should have generous spacing and a clear hierarchy.
- Avoid stacking many small cards in the same viewport.
- Use dedicated pages for major capabilities.
- Keep the chat composer easy to find.
- Widgets should be optional and removable where practical.
- Do not make a single “everything dashboard.”

## Information architecture

1. **Home** — greeting, APEX identity/visualizer, a few quick actions, optional compact status.
2. **Chat** — dedicated conversation workspace; history list, message area, composer, attachment action.
3. **Tools** — searchable catalogue of tools grouped by category.
4. **Automation** — workflows, permissions, run history, pause/stop controls.
5. **Files** — approved file tasks and document workspace; no unrestricted file access by default.
6. **Memory** — inspect, edit, pause, and clear saved information.
7. **Devices** — paired phone, connection status, approved capabilities.
8. **Settings** — General, AI & Models, Appearance, Voice & Audio, Privacy & Security, Devices, About.

## Key screens

### Home
- APEX logo/mark and name.
- Minimal holographic A mark or energy-core visualizer.
- Short greeting and one-line prompt.
- 3–4 quick actions maximum (Ask APEX, Run a Task, Check System, Explore Tools).
- Optional compact system/network status panel.
- Recent activity should be a separate collapsible or navigable area.

### Chat
- Conversation history in a narrow left column or drawer.
- Large central message canvas.
- Clear user/assistant distinction.
- Streaming indicator and stop-generation control.
- Composer with text input, attach, send, voice controls.
- No unrelated system widgets inside chat.

### Tools
- Search and category filters.
- Tool cards with title, short description, permission level, and enabled/disabled state.
- Tool detail view explains inputs, effects, and required permissions.

### Automation
- Workflow list and status.
- Each workflow shows trigger, actions, permissions, last run, and result.
- “Run once” and “Pause” controls.
- Destructive or external actions require confirmation.

### Settings
- Left sub-navigation and one focused settings panel.
- Save/apply feedback.
- Provider/API configuration must never reveal stored secrets after saving.
- Appearance includes theme/accent and motion preferences.

## Floating assistant

A small optional floating orb/mini-window can be opened from the system tray. It must not obstruct work. It can show listening/thinking/speaking states and open the full app. The user can disable it.

## Visualizer states

- Idle: slow subtle pulse.
- Listening: clear cyan listening indicator and microphone status.
- Thinking: restrained rotating/radial animation.
- Speaking: waveform or audio-reactive rings.
- Offline/error: muted state and explicit text.
- Disabled: no active microphone indicator.

## Accessibility and usability

- Keyboard navigation for all primary controls.
- Visible focus indicators.
- Adequate contrast and readable text sizes.
- Do not rely on color alone for status.
- Tooltips for unfamiliar controls.
- Confirmation dialogs must state what will happen.
- Avoid unnecessary animation and high CPU/GPU effects.

## Responsive behavior

Initial target is desktop at 1280×720 and above, with sensible behavior at smaller laptop sizes. Sidebar may collapse; secondary widgets should move below main content or be hidden—not compressed into tiny cards.
