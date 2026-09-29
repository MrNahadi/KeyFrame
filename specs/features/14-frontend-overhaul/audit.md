# Feature 14 screen audit (manifesto Part 15)

Screens: **Runs**, **Replay**, **What-if**, **Model card**. Checked on 29 September 2026 from screenshots at 1440 and 390 px in light and dark, a keyboard walk and a 720 px viewport (standing in for 200% zoom) on every screen, and a contrast calculation for every new colour pair. FIXED marks what the audit itself caught and changed. Open items are listed, not hidden.

## Across every screen

- **Visual.** Colours come from roles only (two tests: no raw colours, no undefined tokens). No accent colour: the one primary action per view is solid ink. Colour means something or is not used: pipe colours for sensor groups, red only for the alarm, green only for "Met". Type: Barlow and Barlow Semi Condensed from the scale, sentence case throughout, tabular figures. One icon family (Lucide, 2 px). Radius 4 (tags, tracks), 8 (controls), 12 (panels). No shadows or glass (nothing floats). Dark mode checked on every screen.
- **Contrast.** Every text pair passes 4.5:1 in both modes. Lowest: secondary text on the fault span, 4.62 (light). Alarm red on panel is 5.62 (light) and 5.56 (dark).
- **People.** FIXED: buttons and segmented options were 34 to 40 px tall, now 44 px. FIXED: segmented controls were one tab stop per option; they are now one stop with arrow keys (radio group pattern, tested). FIXED: Recharts 3 made each trend chart a tab stop with a meaningless name (8 extra stops on the replay); `accessibilityLayer` is now off, because each chart's caption already gives the current reading. Visible focus on every stop; the runs table draws its ring on the whole row.
- **Motion.** Only the playhead moves, and only because the run is playing. The what-if "Updating" spinner is the one animation; reduced motion stops it.
- **Open.** Not tested with a real screen reader (roles and names are covered by tests). Zoom was checked with a 720 px viewport, not browser zoom. The theme follows the system with no toggle.

## Runs (`replay/RunsPage.tsx`)

- **Purpose.** "Which run should I watch, and what happened in each?" Pass. Intro sentence, one start action, the table.
- **Wayfinding.** Pass. Active nav item and a page title; each row names its fault and load.
- **Hierarchy.** Pass. One primary action ("Play air cooler fouling at 75% load", the run with the quickest alarm). The number that matters, the alarm delay, is pushed right; "No alarm" is written, not blank.
- **Container.** Pass. A table grouped by fault, not cards. The keyframe strip in each row previews the replay's own timeline.
- **States.** Loading, error with retry, and empty index designed. Phone: each row restacks to load and alarm on one line with the strip below.
- **Open.** On phones the table rows are restacked with CSS grid, which can drop table semantics in some screen readers (Safari). The row link's accessible name carries fault and load, so each row still reads on its own.

## Replay (`replay/ReplayScreen.tsx`)

- **Purpose.** "Did the model catch this fault, how soon, and why?" Pass. The status panel answers the first two in its headline and detail; the explanation answers the third on pause.
- **Wayfinding.** Pass. "All runs" back link, title, and a held-out note naming the load the model never saw (or saying that the load changes, for the injector run) with a link to the model card.
- **Hierarchy.** Pass. The keyframe timeline is the one bold element and doubles as the scrubber; Play is the one primary action. The model's reading comes first in reading order and on phones, and sits to the right on desktop.
- **Mapping.** Pass. The scrubber is the timeline itself; the diamonds on it match the rules on the trend charts and the legend under it.
- **Behaviour.** Pass. Keys: Space, arrows, Home, End and S (listed under the controls, hidden on phones where there is no keyboard). The explanation appears only when paused, and the dashed hint says so.
- **Words.** Pass. "Healthy by design", "Fault on, no alarm yet", "Alarm: air cooler fouling", "No alarm raised". If the alarm names a different fault from the one switched on, the detail says so.
- **Real data.** Pass. The low-confidence note appears for the 85% load runs (ADR 0011). Readings are shown with units at 3 significant figures. Axes get enough decimals to keep ticks distinct. FIXED: a narrow-range sensor showed two identical ticks ("12.7, 12.7"). FIXED: a push that rounds to zero read "−0.00 away" and now reads "0.00".
- **Open.** When switch-on and alarm are close (2 min 50 s in a 2 h 47 min run) the two diamonds touch; the legend gives both times in words. The shape of each trend has no text alternative beyond its current value.

## What-if (`whatif/WhatIfScreen.tsx`)

- **Purpose.** "What would the model say if the readings were like this?" Pass. The steady-state assumption is always visible under the title.
- **Hierarchy.** Pass. Load and reset sit with the sliders they affect. The diagnosis sits beside them on desktop (sticky). On phones, a verdict bar stays in view while the sliders scroll, because the full diagnosis is below them. No primary action in the normal state: dragging is the action. Retry is primary only in the error state.
- **Grouping.** Pass. Sliders are grouped by sensor group (fieldset and legend, with the group's colour tag) in the fixed group order.
- **Real data.** Pass. Every value shows its unit and a precision fitted to the slider's range. FIXED: engine cooling water flow read "12.7" at minimum, healthy and maximum; now 12.706, 12.750 and 12.756. Each slider shows the healthy value, or the change from it once moved. Reset is disabled until something has changed.
- **Behaviour.** Pass. Requests are debounced and the latest wins. While updating, the old result dims and says "Updating". Validation errors appear in the result panel. If the API is unreachable, the page gives the start command and a Retry button.
- **Open.** The phone verdict bar is `aria-hidden` because it repeats the diagnosis, which screen-reader users reach in order.

## Model card (`modelcard/ModelCardPage.tsx`)

- **Purpose.** "How good is it, and where does it fail?" Pass. The page opens with the targets table: 2 of 9 met, said in the lead.
- **Honesty.** Pass. Every number in the table is checked by `scorecard.test.ts` against the locked results files. Notes carry the context a number needs: detection delay counts only the 6 of 13 runs that alarmed; unseen severity is weak evidence; response time was measured after the lock.
- **Hierarchy.** Pass. One h1: the card's own title is lifted out of the Markdown. Then the targets table, the card and the figure. FIXED: on phones the four-column table squeezed the measure names into tall, narrow stacks; rows now restack to measure, then result, target and status.
- **Open.** The confusion matrix is a light PNG on a dark page in dark mode, framed on a panel. Regenerating it per theme belongs to the evaluation notebook.
