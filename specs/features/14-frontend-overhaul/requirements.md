# 14 Front-end overhaul: requirements

- R1. A design plan grounded in the subject (engine-room alarm and trend pages), with 4 to 6 base colours, type roles, layout wireframes and principles, and a written review of what was generic and changed. Sensor-group colours validated for colour-vision deficiency in both modes.
- R2. Tokens only: no raw colour outside `tokens.css`, and every token a component uses is defined there (both enforced by tests).
- R3. Every reading shows its unit and a sensible precision; every fault and sensor group is named in words; colour never carries meaning alone.
- R4. Runs page: says what the demo does, offers one primary action (play the run with the quickest alarm), and lists runs in a table with a miniature keyframe strip and the alarm delay.
- R5. Replay: the keyframe timeline (healthy and faulty spans, switch-on and alarm keyframes) is also the scrubber; the model's reading states plainly whether the alarm has fired and how long after switch-on; the explanation (on pause) is a grouped waterfall with plain feature names; held-out load and provenance are stated.
- R6. What-if: sliders grouped by sensor group, each with unit, a precision that fits its range, the healthy value and the change from it; the diagnosis beside the sliders on desktop and kept in view on phones; the steady-state assumption always visible.
- R7. Model card: a targets table first (result, target, met or not, with notes where a number needs context), checked by a test against the locked results files; then the card and the confusion matrix.
- R8. Quality floor: keyboard reachable with visible focus, one tab stop per radio group with arrow keys, touch targets of 44 px, contrast of at least 4.5:1 for text, reduced motion respected, no horizontal overflow at 390 px or at 200% zoom.
