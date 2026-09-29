# Replay screen audit (manifesto Part 15)

Screen: `#/replay/<run>` (ReplayScreen, Traces, Probabilities). Picker: RunPicker.

## Purpose
- One question: "What did the model see, and when did it raise the alarm, on this real run?" Pass.
- Nothing off-topic: pass. No KPI cards or analytics repeated: pass.
- Every element serves watching or scrubbing the run: pass.

## Wayfinding
- Where am I: page title `Replay: <run>` and active Replay nav item (App). Pass.
- What can I do: labelled playback controls, speeds, scrubber. Pass.
- Where can I go: `Back to all runs` link in App and in error and empty states. Pass.
- Out or back: same link. Pass.

## Hierarchy and layout
- Eye lands on traces and probabilities, controls sit above them. Pass.
- One primary action: Play/Pause (`primary` style). Pass.
- Grouping: controls, scrubber, then the two panels. Pass.
- Controls next to what they affect: scrubber sits directly above the traces. Pass.
- Mapping: start, back, play, forward, end run left to right like the timeline. Pass.
- Spacing from tokens; the body collapses to one column under 900px. Pass.
- Container: grid of charts plus bars is right for the data. Pass.
- Progressive disclosure: keyboard shortcuts were hidden, so a one-line hint was added under the scrubber. Fixed.

## Visual
- Colours only from tokens (a test fails on raw colours); data colours use `--data-*`. Pass.
- Type scale from tokens, sentence case. Pass.
- Lucide through `Icon` at 20px, no emojis. Pass.
- One button radius via `.button`. Pass.
- No shadows or translucency: nothing floats. Pass.
- No text over images. Pass.
- Dark mode: tokens carry both themes. Pass (token-driven, not re-inspected in a browser).

## Behaviour
- Interactive things are buttons with borders and focus rings; static text is plain. Pass.
- Nothing mimics a control it is not. Pass.
- Feedback: play/pause icon and label swap, `aria-pressed` on speeds, position readout updates. Pass.
- Waits: skeleton with `role="status"` while loading. Pass.
- Mistakes: nothing destructive; every jump can be undone by scrubbing. Pass.
- Motion: only the playback the user asked for; charts have animation off; reduced motion handled in T-006. Pass.
- Errors: message plus `Try again` and back link; empty run has its own state. Pass.

## Words
- Plain language: alarm status and probability sentences use plain class names. Real replay files use the codes AC, AF, CW, INJ, TD, which the name map did not know (it showed the raw code lowercased). Fixed in `status.ts`, with a test.
- Verbs consistent (Play, Pause, Step, Go to, Jump to). Pass.
- Buttons say what happens. Pass.
- Context: elapsed time readout, provenance line, sampling note. Pass.

## Real data and states
- Long run names wrap in the picker and title; runs of 1000+ frames were checked against the real JSON sizes. Pass.
- Loading, error, empty and no-fault-run states exist. Pass.
- Phone to desktop: single column under 900px. Pass (not device-tested).

## People
- Keyboard: every control reachable, shortcuts documented on screen, visible `--focus-ring`. Pass.
- Screen reader: labelled controls, `aria-valuetext` on the scrubber, sentence status. Pass.
- Colour never the only signal: bars carry text labels, alarm is stated in words. Pass.
- Touch targets use `--touch-min`. Pass.
- First-time use: run picker with plain titles, then play. Pass.
- Experts: speeds, step keys, jump to switch-on. Pass.
- Personalisation: speed choice only; nothing else needs it. Pass.

## Responsibility
- No data or permissions requested. Pass.
- Misuse: the replay is recorded data with a provenance line saying which model made it; it is not a live safety system. Pass.
- AI: predictions are labelled with their provenance and are read-only. Pass.
- No dark patterns. Pass.

## Quality
- Details checked in code, not with a person or a browser; the dark-mode and phone-width answers rest on tokens and media queries. Noted as the limit of this audit.
