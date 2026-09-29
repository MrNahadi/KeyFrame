# Keyframe web demo: design plan

Written 29 September 2026 for the front-end overhaul (roadmap item 14), following the frontend-design skill's process (plan, review against the brief, build, critique), the design manifesto (`docs/design/manifesto.md`) and the SaaS UI checklist (`docs/design/saas-ui.md`). Where the manifesto's rules sheet (Part 14) sets a value, it wins; where it leaves an axis free, this plan chooses deliberately.

## Subject, audience, job

- **Subject:** a machine-learning diagnosis of a marine diesel on a test bench, replayed from real runs.
- **Audience:** an engineer or recruiter at an engine maker, who knows engine rooms, alarm panels and trend pages, and has about five minutes.
- **Primary job:** watch the model catch a real fault, see how long after the fault it raised the alarm, and read which readings led it there. Everything else (what-if, model card) supports trusting or questioning that answer.

## The vernacular we borrow from

Engine-control-room alarm and monitoring systems: trend pages drawn like chart recorders, alarm lists where red means alarm, plain DIN-style labels on painted machinery, and pipework colour-coded by what flows through it (ISO 14726: air light blue, fuel brown, lube oil yellow, water green/blue). Not a dark sci-fi HUD; a well-kept engine room in daylight.

## Colour

Five base colours; everything else is a data or status role.

| Name | Light | Dark | Role |
|---|---|---|---|
| Bulkhead | `#eef1f3` | `#0e151b` | page background |
| Panel | `#ffffff` | `#151f27` | surfaces that hold readings |
| Hull ink | `#15212a` | `#e3e9ed` | text, and the primary action (solid ink button) |
| Gauge grey | `#56636e` | `#9aa8b3` | secondary text, axes |
| Rule | `#d3dae0` | `#26333d` | 1px borders and dividers |

- **No brand accent colour.** The primary action is solid hull ink with white text (one per view). Chrome stays grey; colour is reserved for meaning (saas-ui: "only reserve color for things that are trying to show something").
- **Sensor groups carry the data colour**, taken from ship pipework colour coding (ISO 14726 inspired), always shown in this fixed order and always labelled with text:

| Group | Light | Dark | Pipe colour it echoes |
|---|---|---|---|
| Air path | `#3d8fd1` | `#4a8fe0` | air, light blue |
| Fuel system | `#a0561a` | `#c2602a` | fuel, brown |
| Cooling | `#1f8a70` | `#22987a` | sea water, green |
| Lube oil | `#c99a06` | `#ad8c16` | lube oil, yellow |
| Combustion and power | `#7b4fa8` | `#a45bc9` | no pipe colour; violet, distinct from the others |

  Validated with the dataviz validator in fixed (adjacent) order: light worst CVD ΔE 9.9, normal-vision 19.3; dark passes every check. Light yellow sits under 3:1 on white, so every coloured mark has a text label (relief rule).
- **Status:** alarm red (`#c62828` light, `#ef6b6b` dark) with a filled diamond and the word "Alarm"; the fault switch-on is ink (a hollow diamond and the words "Fault switched on"). Nothing else is red.
- Fault classes are named in words, not colours. The model's leading class is drawn in ink, the rest in grey.

## Type

- **Barlow** (Jeremy Tribby; a grotesk that shares DIN 1451's engineering-signage roots) for all text, 400/500/600.
- **Barlow Semi Condensed** 600 for page titles and the big readouts (elapsed time, alarm delay): a narrower width, like an instrument label, so numbers read as readings.
- Tabular figures (`font-variant-numeric: tabular-nums`) on every number. No monospace anywhere.
- Scale from the manifesto (30/24/20/16/16/14/12/12). Labels are sentence case, not uppercase: the manifesto's values are per-project defaults, and the frontend-design skill flags all-caps labels as a template tell; consistency is kept by using one label style everywhere.
- Every reading shows its unit and a sensible precision (two to four significant figures), never raw floats.

## Layout

Left aligned throughout; content width up to 80 rem; reading text capped at 68 ch.

**Runs (home).** Opens with the job, one primary action, then a table (not cards): the number that matters, the alarm delay, is pushed right, and each row carries a miniature keyframe strip.

```
Keyframe                                   Replay  What-if  Model card
-----------------------------------------------------------------------
Watch a marine diesel go from healthy to faulty,
and see when the model raised the alarm.
Real test-bench runs, replayed with predictions from a
model that never saw that engine load.

[ Play air cooler fouling at 60% load ]   (primary, ink)

Fault runs                                                 (title 2)
Fault                 Load  Length   Timeline            Alarm
Air cooler fouling    40%   2 h 13   ──◇────────────     No alarm
                      60%   2 h 54   ─────◇──◆───────    9 min 5 s
...
Healthy running       40%   30 min   ───────────────     No fault
```

**Replay.** The keyframe timeline is the page's one bold element: a full-width strip that is also the scrubber, with a hollow diamond at the fault switch-on, a filled red diamond at the alarm and the healthy / faulty spans shaded. Below it, readings on the left, the model's reading and its explanation on the right.

```
All runs
Air cooler fouling at 60% load            Model never saw 60% load
[====== healthy ======◇ fault ======◆ alarm ===|=========]  <- scrub
 0:00                 53:21          62:26    now 64:30   2:54:10
[|<] [<] [ Play ] [>] [>|]  [Jump to switch-on]     Speed 1× 10× 60×
+-------------------------------------+----------------------------+
| 8 trend charts, 2 columns           | Alarm: air cooler fouling  |
| grouped by sensor group colour tag  | 9 min 5 s after switch-on  |
|                                     | Model's reading (bars)     |
|                                     | Why (on pause): grouped    |
|                                     | contributions + top 3      |
+-------------------------------------+----------------------------+
```

**What-if.** Controls left, result right (sticky on desktop, stacked on phones). Sliders grouped by sensor group with its colour tag, each showing the value with unit and the healthy baseline.

**Model card.** One reading column: the targets table (target, achieved, met or not) at the top because it answers the page's question ("how good is it, and where does it fail?"), then the card, then the confusion matrix.

## Principles

1. **One bold element: the keyframe diamond.** Switch-on and alarm are drawn as animation keyframes on a timeline, on the replay scrubber and in miniature in the run table. The product's name and its job in one mark. Everything else stays quiet.
2. **Colour means something or is not used.** Grey chrome; pipe colours for sensor groups; red only for the alarm.
3. **Readings look like readings.** Units always, tabular figures, sensible precision, instrument-width numerals for the big values.
4. **Flat, ruled surfaces.** 1px rules and background steps separate things; radius 4 (tags), 8 (buttons, inputs), 12 (panels); no shadows (nothing floats yet); no gradients.
5. **Plain engineer's language.** Sentence case, verbs from the manifesto's dictionary, errors that say what happened and how to fix it.
6. **Motion only answers an action.** The playhead moves because the run is playing; nothing else animates. Reduced motion respected.

## Review against the brief (what was generic, what changed)

- **First draft used a petrol-teal accent (`#0b5d6e`) for buttons and links.** Working through a similar prompt ("ML dashboard for industrial sensors") lands on slate plus teal almost every time, so it was a default. Changed to ink-only actions with colour reserved for data, which also matches the saas-ui checklist's grayscale Attio/Stripe direction.
- **First draft had one card per run in a grid.** That is the SaaS-card kit. Changed to a table with the alarm delay pushed right (saas-ui: "push the number that actually matters to the right"; the Capern table).
- **First draft labelled sections with uppercase eyebrows** (manifesto Part 14 default). Changed to sentence-case labels, recorded above.
- **First draft used the dataviz reference palette for fault classes.** Five fault colours plus five group colours would be ten hues on one screen. Faults are now words; only sensor groups carry colour, and those colours come from the engine room's own convention.
- **Kept:** Barlow (chosen for its DIN signage lineage, not a default family), the keyframe diamond (specific to this product's name and job), left alignment.

## Build notes

- Fonts self-hosted with `@fontsource/barlow` and `@fontsource/barlow-semi-condensed` (latin subsets, weights 400/500/600), so the demo works offline and on any static host.
- Watch selector specificity: component CSS Modules only, no element selectors beyond `base.css`.
- Screens to screenshot after each step: runs, replay (playing and paused), what-if, model card; 390 px and 1440 px; light and dark.
