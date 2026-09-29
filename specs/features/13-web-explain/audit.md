# Feature 13 screen audit (manifesto Part 15)

Screens: **Explain panel** (replay, paused), **What-if**, **Model card**. Read from source; T-006 fixed the failures marked FIXED. "Open" items are explained, not hidden. Not checked in a real browser (unattended loop): dark mode, 200% zoom and 390 px rely on token use and wrapping rules, not on screenshots.

## Explain panel (`replay/ExplainPanel.tsx`)

- **Purpose.** Question: "Why does the model read this frame as this fault?" Pass. Nothing off-topic; probabilities live in the Probabilities component, not repeated. Top features are the detail for the same question.
- **Wayfinding.** Pass. Sits under the replay body; the hint "Pause to see why" tells people how to reach it.
- **Hierarchy.** Pass. Title, then one summary sentence, then chart, then the text list. No actions of its own, so no competing primary action. Progressive disclosure: hidden while playing, and the hint says so.
- **Visual.** Pass. Tokens only (`--data-1` for towards, `--data-neutral` for away); sign is also written in text. Icons: none. Chart ticks use fixed 11 px, a Recharts prop that cannot read CSS tokens. Open, minor.
- **Behaviour.** Pass. Nothing interactive, nothing looks interactive. No motion (`isAnimationActive={false}`).
- **Words.** Pass. "Towards / away from" in plain language; caveat says credit between groups is approximate. "SHAP" is avoided in headings; feature names come from data.
- **States.** Playing state = hint. Low-confidence state = note. Open: no loading state needed (data already loaded by the replay screen). Plot is `min-width: 0`, labels are 120 px wide; long names wrap in the text list.
- **People.** Pass. The text list carries every value, so the chart is not the only signal and screen readers get the full content. Colour is never the only signal.
- **Responsibility.** Pass. The caveat and low-confidence note stop it overclaiming.

## What-if (`whatif/WhatIfScreen.tsx`)

- **Purpose.** Question: "What does the model say if the readings were like this?" Pass. The notice states the 15-minute steady assumption.
- **Wayfinding.** Pass. H1 "Try your own readings" and the active nav item. Nav links lead to Replay and Model card.
- **Hierarchy.** Pass. Load selector, then sliders (next to what they affect), then result. One primary action: dragging; "Reset to healthy baseline" is secondary and sits with the sliders it resets. Open: the result appears below the sliders, so on phones it is below the fold. Kept because sliders must come first in reading order.
- **Visual.** FIXED. Buttons used a raw 4 px radius and `--text-secondary` border; now `--radius-md`, `--border-strong`, `--surface`, matching the model card button. Title now uses the title-1 scale like the other page titles (it was headline size).
- **Behaviour.** Pass. Debounced update shows "Updating…" and dims the result with `aria-busy`. Stale responses are dropped. Reset undoes edits. Validation errors are inline and shown next to the sliders; API-unreachable shows the start command and Retry. No irreversible actions.
- **Words.** Pass. "Reset to healthy baseline" says what happens; "Retry" is used only for reloading.
- **States.** Loading, updating, validation error, unreachable and empty (no result yet) all designed. Segmented control wraps (FIXED, `flex-wrap`) so it cannot overflow at 390 px.
- **People.** FIXED. Buttons and segmented items now have `min-height: var(--touch-min)` (44 px); slider inputs also get 44 px height. Visible focus comes from the global `:focus-visible` rule in `base.css`. Radio group uses `role="radiogroup"` with `aria-checked`; arrow-key movement between radios is not implemented (open; each option is still reachable with Tab).
- **Responsibility.** Pass. Data stays in the browser and the local API. The result is labelled as what the model reads, not a real diagnosis.

## Model card (`modelcard/ModelCardPage.tsx`)

- **Purpose.** Question: "How good is this model and where does it fail?" Pass. Card text, confusion matrix, link to the full notebook. Nothing repeated from the other screens.
- **Wayfinding.** Pass. Active nav item, and the card's own headings come from the Markdown.
- **Hierarchy.** Pass. Reading page, one figure with caption, one link at the end. No primary action needed.
- **Visual.** Pass. Tokens only; card uses `--radius-lg` and `--bg-secondary`. Dark mode relies on tokens; the confusion matrix PNG is a light image (open, minor).
- **Behaviour.** Pass. Loading skeleton; error state uses EmptyState with "Try again", which reloads.
- **Words.** Pass. Error copy says what failed and what to try. The link says where it goes.
- **States.** Loading, error and ready designed. Long lines wrap (`overflow-wrap: anywhere`) and the image is capped at `max-width: 100%`; the Markdown renderer has no table support, so none is needed. The image has alt text and caption.
- **People.** Pass. Button 44 px, focus ring, real `<article>`, alt text describes the chart.
- **Responsibility.** Pass. The card states limits, so the page does not oversell the model.

## Summary

Three fixes made (what-if buttons, touch targets, title scale and wrap). Open and explained: no arrow-key navigation in the load selector, fixed 11 px chart ticks, light-only confusion matrix image, no browser check of dark mode or zoom.
