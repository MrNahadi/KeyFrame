# Engineering checklist: what each fault should do to the sensors

Written 28 September 2026, **before any fault run was compared with healthy running and before any model saw the data** (the only data inspected so far: row counts, time steps and shaft-power ranges per file). This is the pre-registered prediction that the SHAP physics check (roadmap item 8) is scored against. The "Expected" sections below are never edited after this commit; what the EDA actually shows is added underneath in a separate "Observed" section.

Drafted by the agent from marine diesel engineering knowledge under the owner's fully automatic working agreement (ADR 0003). **Owner review requested:** Farid, please check and annotate; any change you make is recorded with its date in the "Owner review" section so the pre-registration stays honest.

## How to read it

The bench holds engine speed and brake load at a setpoint, so the governor adds fuel when efficiency drops. "↑" and "↓" are changes relative to healthy running **at the same load**. Strength: strong (should be visible by eye), moderate, weak (may need residuals or rolling statistics). Channel names are the dataset's full variable names; symbols in brackets.

## Air cooler fouling (AC)

Mechanism: the charge air cooler removes less heat, so hotter, less dense air reaches the cylinders.

| Channel or feature | Expected | Strength |
|---|---|---|
| Charge Air IC Air Temp. Out (T15) | ↑ | strong |
| Cooler effectiveness (T14 − T15) / (T14 − T16) | ↓ | strong |
| Loss in Charge Air IC (Qrej_air); Charge Air IC Cooling Water Temp. Out (T17) | Qrej_air ↓; T17 depends on how the fouling was imposed (↑ if cooling water flow was throttled) | moderate |
| Exh.Gas Temp. No.1–3 (T1–T3) and Turbine In (T4) | ↑ (less air mass per cycle) | moderate |
| Charge Air Press. (Pturb) | ≈ or slightly ↑ | weak |
| Fuel Flow per kW | slightly ↑ | weak |

Expected top 5: T15, cooler effectiveness, Qrej_air (or IC cooling water flow/T17), T4, mean of T1–T3.

## Air filter clogging (AF)

Mechanism: pressure loss at the compressor inlet grows gradually, so the turbocharger delivers less air.

| Channel or feature | Expected | Strength |
|---|---|---|
| Charge Air Press. (Pturb) | ↓, growing over the run | strong |
| Exh.Gas Temp. No.1–3, Turbine In and Out (T1–T5) | ↑ (richer mixture) | moderate |
| Max. In-Cylinder Press. No.1–3 (Pmax) | ↓ (lower compression pressure) | moderate |
| TCH Power (Qturb), Exh. Gas Mass Flow (Mexh) | ↓ | moderate |
| Charge Air IC Air Temp. In (T14) | slightly ↑ (higher compressor pressure ratio) | weak |
| Fuel Flow per kW | slightly ↑ | weak |

Expected top 5: Pturb, T4, mean of T1–T3, mean Pmax, turbocharger pressure ratio or Qturb. The signature grows with time, so the first minutes after switch-on may look healthy (brief risk "Gradual faults").

## Injector nozzle clogging (INJ)

Mechanism: one hole of one injector nozzle is plugged. That cylinder gets less fuel, badly atomised; the governor adds fuel and the other cylinders take up the load.

| Channel or feature | Expected | Strength |
|---|---|---|
| Spread of Exh.Gas Temp. No.1–3 (max − min) | ↑ (one cylinder out of line) | strong |
| Spread of Max. In-Cylinder Press. No.1–3 | ↑ | strong |
| Spread of Indicated Work No.1–3 | ↑ | strong |
| Affected cylinder's exhaust temperature and Pmax | ↓ (under-fuelled) or exhaust temperature ↑ if poor atomisation causes late burning; the direction is uncertain, the imbalance is not | moderate |
| Indicated / Effective Efficiency (Effi, Efft), Fuel Flow per kW | efficiency ↓, fuel per kW ↑ | weak |
| Air path (Pturb, T14, T15) | ≈ | — |

Expected top 5: exhaust temperature spread, Pmax spread, indicated work spread, the affected cylinder's Pmax, indicated efficiency. A model that relies instead on cooling water, lube oil or room-driven temperatures is probably recognising the test day (brief risk "Test-day shortcuts").

## Cooling water pump cavitation (CW)

Mechanism: air injected at the pump suction makes the pump deliver less, and unsteadily. Combustion and the air path should be almost untouched.

| Channel or feature | Expected | Strength |
|---|---|---|
| Fresh Cooling Water Press. (Pl_water1, raw V) | mean ↓, fluctuation ↑ | strong (fluctuation) |
| Engine Cooling water flow (Qw_eng) | mean ↓, fluctuation ↑ | strong (fluctuation) |
| Cooling water temperature rise across the engine (T7–T9 minus T6) | ↑ | moderate |
| Loss with cooling water (Qrej_eng) | noisier (computed from flow × temperature rise) | moderate |
| Combustion and air path (T1–T5, Pmax, Pturb) | ≈ | — |

Expected top 5: rolling standard deviation of Pl_water1, rolling standard deviation of Qw_eng, mean Qw_eng, cooling water temperature rise, Qrej_eng. This predicts the "cavitation looks too easy" puzzle: the fault shows up as instability rather than a shift in averages, so rolling standard deviations should carry it. If instead a single channel steps at switch-on with no physical reason, suspect a recording artefact.

## Turbine degradation (TD)

Mechanism: raised back pressure after the turbine cuts the turbine's expansion ratio, so it extracts less energy, the turbocharger slows and delivers less air.

| Channel or feature | Expected | Strength |
|---|---|---|
| Exh.Gas Temp. Turbine Out (T5) | ↑ | strong |
| Temperature drop across the turbine (T4 − T5) | ↓ | strong |
| Charge Air Press. (Pturb) | ↓ | strong |
| Exh.Gas Temp. Turbine In (T4), No.1–3 (T1–T3) | ↑ | moderate |
| TCH Power (Qturb) | ↓ | moderate |
| Max. In-Cylinder Press. (Pmax), efficiencies | slightly ↓ (higher pumping work) | weak |

Expected top 5: T5, T4 − T5, Pturb, T4, Qturb.

## Telling the faults apart

- **AF and TD both lower charge air pressure and raise exhaust temperatures.** TD raises turbine outlet temperature and shrinks the temperature drop across the turbine; AF keeps that drop closer to normal and develops gradually.
- **AC is the only fault that should raise charge air temperature after the cooler** with little change in boost.
- **CW is the only fault confined to the cooling water system**, and it shows as instability rather than a shift.
- **INJ is the only fault that makes the three cylinders disagree.**
- **Normal:** residuals from the healthy-engine model stay near zero on every group.

## Channels that must not drive a diagnosis

Engine room temperature, dPf, dPex and time are excluded as inputs (brief non-negotiables). Beyond those, if a fault's top features are dominated by slow, day-dependent temperatures (lube oil cooling water inlet T12, fuel temperatures T18/T21, sea cooling water pressure Pl_water2) with no mechanism above, treat it as a test-day shortcut and investigate before trusting the score.

## Owner review

- (none yet)

## Observed in the EDA

Added by notebook 01 (roadmap item 3), below this line, without editing anything above. Shift is the median standardised shift (faulty − healthy, divided by healthy std) across the fault's runs; for the gradual faults (AC, AF, CW, TD) it is measured over each run's last 30 minutes, per `keyframe.eda.fault_shift`. Std ratio is faulty std / healthy std over the same window. Source: `reports/results/01_fault_shifts.csv`; the derived physics quantities (cooler effectiveness, spreads, cooling water rise, turbine temperature drop, efficiencies, fuel flow per kW) use the same computation over `keyframe.eda`'s physics functions, source `reports/results/01_checklist_derived_shifts.csv`. The CW rolling-std ratios are 60 s rolling std (`keyframe.eda.rolling_std`) averaged over the run's last 30 minutes, divided by the same average over the matched healthy segment; not saved to a separate file, computed in notebook 01.

### Air cooler fouling (AC)

| Channel | Expected | Observed shift | Std ratio | Agree / Disagree / Unclear |
|---|---|---|---|---|
| Charge Air IC Air Temp. Out (T15) | ↑ strong | +29.8 | 10.8 | Agree |
| No.1 Exh.Gas Temp. (T1) | ↑ moderate | +1.17 | 0.66 | Agree |
| No.2 Exh.Gas Temp. (T2) | ↑ moderate | +1.43 | 0.65 | Agree |
| No.3 Exh.Gas Temp. (T3) | ↑ moderate | +1.63 | 0.78 | Agree |
| Exh.Gas Temp. Turbine In (T4) | ↑ moderate | +1.57 | 0.72 | Agree |
| Charge Air Press. (Pturb) | ≈ weak | −0.47 | 0.23 | Unclear |
| Cooler effectiveness (T14−T15)/(T14−T16) | ↓ strong | −4.76 | 1.55 | Agree |
| Loss in Charge Air IC (Qrej_air) | ↓ moderate | +8.23 | 2.99 | Disagree |
| Charge Air IC Cooling Water Temp. Out (T17) | depends moderate | +15.66 | 6.17 | Agree (rise) |

AC matches the checklist cleanly: T15 rises far more than anything else in the dataset (standardised shift +29.8), and the whole exhaust chain (T1–T4) rises with it. Only Pturb, predicted flat, drifts down by less than half a standard deviation — small enough to call noise, not a real boost change. Cooler effectiveness falls hard, exactly as fouling should look from the metal side of the intercooler. Qrej_air moves the wrong way (up, not down) and T17 rises sharply — both point at cooling water flow being throttled during the fault, one of the two mechanisms the checklist named for T17, but the opposite of the "less heat rejected" story implied for Qrej_air; worth checking whether this dataset's fouling was imposed by restricting cooling water rather than fouling the air side. `00_switch_on.png` shows all four AC runs drifting upward through their pre-fault segment (steepest at 40% load), so some of the exhaust-chain rise likely continues that warm-up trend rather than starting at switch-on — T15 and cooler effectiveness still step clearly at the red line, so the core signature is real.

### Air filter clogging (AF)

| Channel | Expected | Observed shift | Std ratio | Agree / Disagree / Unclear |
|---|---|---|---|---|
| Charge Air Press. (Pturb) | ↓ strong | −1.62 | 0.25 | Agree |
| No.1 Exh.Gas Temp. (T1) | ↑ moderate | −0.27 | 0.26 | Disagree |
| No.2 Exh.Gas Temp. (T2) | ↑ moderate | −0.36 | 0.21 | Disagree |
| No.3 Exh.Gas Temp. (T3) | ↑ moderate | +0.30 | 0.25 | Unclear |
| Exh.Gas Temp. Turbine In (T4) | ↑ moderate | −0.26 | 0.25 | Disagree |
| Exh.Gas Temp. Turbine Out (T5) | ↑ moderate | −0.04 | 0.98 | Unclear |
| Max. In-Cylinder Press. No.1 (Pmax) | ↓ moderate | −0.21 | 0.93 | Agree |
| TCH Power (Qturb) | ↓ moderate | −0.12 | 1.02 | Agree |
| Exh. Gas Mass Flow (Mexh) | ↓ moderate | −0.93 | 0.14 | Agree |
| Charge Air IC Air Temp. In (T14) | slightly ↑ weak | −1.07 | 0.11 | Disagree |
| Fuel Flow per kW | slightly ↑ weak | −0.08 | 0.36 | Disagree |

AF's boost loss shows exactly as predicted (Pturb −1.62), but the exhaust temperatures do not rise with it — T1, T2 and T4 fall slightly instead, and T14 falls hard rather than rising. The checklist's "richer mixture raises exhaust temperature" story does not hold up over the last 30 minutes of these runs; either the governor's fuelling response outpaces the air loss at this load range, or the clogging in this dataset is milder than assumed. Worth residualising T1/T2/T4 against load before trusting them as AF features. Fuel flow per kW is flat-to-slightly-down rather than up, consistent with the exhaust temperatures: nothing here points at richer fuelling. AF's pre-fault segments (`00_switch_on.png`) are not at steady state either — the 40% run cycles up and down by several degrees (likely load dithering) and the others drift upward slowly, so small shifts on these channels should be read cautiously.

### Injector nozzle clogging (INJ)

| Channel | Expected | Observed shift | Std ratio | Agree / Disagree / Unclear |
|---|---|---|---|---|
| No.1 Exh.Gas Temp. (T1) | part of spread ↑ strong | +0.32 | 1.43 | — |
| No.2 Exh.Gas Temp. (T2) | part of spread ↑ strong | −0.21 | 1.25 | — |
| No.3 Exh.Gas Temp. (T3) | part of spread ↑ strong | −2.13 | 0.85 | Agree (spread) |
| Charge Air Press. (Pturb) | ≈ | −0.07 | 1.39 | Agree |
| Charge Air IC Air Temp. In/Out (T14/T15) | ≈ | −0.51 / −0.38 | 1.31 / 1.68 | Unclear |
| Spread of Exh.Gas Temp. No.1–3 (max−min) | ↑ strong | +5.39 | 2.32 | Agree |
| Spread of Max. In-Cylinder Press. No.1–3 | ↑ strong | +3.32 | 2.21 | Agree |
| Spread of Indicated Work No.1–3 | ↑ strong | +2.55 | 2.25 | Agree |
| Indicated Efficiency (Effi) | ↓ weak | −5.49 | 4.58 | Agree |
| Effective Efficiency (Efft) | ↓ weak | −7.09 | 5.99 | Agree |
| Fuel Flow per kW | ↑ weak | +16.48 | 17.15 | Agree |

INJ does the one thing the checklist says it should: the three cylinders stop agreeing. No.3's exhaust temperature drops 2.1 standard deviations below healthy while No.1 rises slightly, a 2.5 SD spread that dwarfs anything in the other faults — consistent with one nozzle under-fuelling its cylinder. Computing the spreads directly (max−min across cylinders, not reading the per-cylinder rows individually) confirms it: exhaust temperature, Pmax and indicated-work spreads all move 2–5 standard deviations above healthy, the largest shifts in the whole checklist. Both efficiencies fall and fuel flow per kW rises sharply, all in the predicted direction — but these last four rows have shifts and std ratios far outside the range seen anywhere else (up to +17), which is as much a sign that `matched_healthy`'s cross-run reference has a much tighter spread on these channels as it is a sign of a huge fault effect; treat the magnitude, not just the sign, with caution (INJ has no pre-fault segment of its own — see the caveat above). The air path stays close to flat as expected, though std ratios above 1 everywhere hint this run is simply noisier throughout (INJ has no pre-fault segment to compare against, so "healthy" here is `matched_healthy` from other runs, not a same-run baseline — treat small shifts here cautiously).

### Cooling water pump cavitation (CW)

| Channel | Expected | Observed shift | Std ratio | Agree / Disagree / Unclear |
|---|---|---|---|---|
| Fresh Cooling Water Press. (Pl_water1) | mean ↓, fluctuation ↑ strong | −0.29 | 1.10 | Unclear |
| Engine Cooling water flow (Qw_eng) | mean ↓, fluctuation ↑ strong | −0.84 | 0.09 | Disagree (fluctuation) |
| Loss with cooling water (Qrej_eng) | noisier moderate | +0.01 | 0.40 | Disagree |
| Combustion/air path (T1–T3, T4, T5, Pmax, Pturb) | ≈ | −0.32 to −1.19 (Pturb) | 0.14–1.15 | Disagree |
| Cooling water temperature rise (mean T7–T9 − T6) | ↑ moderate | +0.02 | 1.02 | Disagree |
| Rolling std ratio, Fresh Cooling Water Press. (60 s) | fluctuation ↑ strong | 1.09 (both runs) | — | Agree |
| Rolling std ratio, Engine Cooling water flow (60 s) | fluctuation ↑ strong | 0.48 (60% run), 4.63 (85% run) | — | Unclear |

CW is the puzzle T-004 already flagged: the checklist expects the combustion and air path to stay untouched, but Pturb (−1.19), T1–T4 and Pmax all move by moderate amounts over the last 30 minutes, and cooling water rise barely moves at all where a moderate rise was expected. A whole-window std ratio below 1 is not evidence against fluctuation — it is evidence that a single std over 30 minutes averages a short-lived jump away, not that the jump did not happen. Rolling std (60 s window, matching the cavitation section) is the right measure: Fresh Cooling Water Press. is noisier throughout the fault at both loads (ratio 1.09), and Engine Cooling water flow is noisier at 85% load (4.63×) but *quieter* at 60% load (0.48×) — the fluctuation signature the checklist predicted is present but load-dependent, not universal, so a fixed-threshold rolling-std feature would miss the 60% case.

Before calling the combustion/air-path moves a fault effect, they need to be checked against warm-up drift, since neither CW run's pre-fault segment is at steady state (`00_switch_on.png`): the 85%-load run steps up sharply around 20 minutes before switch-on, and the 60%-load run drifts upward continuously through its pre-fault window. Comparing the last 15 minutes before switch-on with the first 15 minutes after it isolates the actual step: at 85% load, T1–T5 already drifted 7–9 °C during the pre-fault warm-up but move by only 0.1–0.5 °C at switch-on itself — almost all of the "moderate" shift in the table above is warm-up drift that happened to still be settling, not cavitation. At 60% load the picture is less clean: pre-fault drift (1.5–9.9 °C) and the switch-on step (1.8–5.8 °C) are comparable in size, so the exhaust-chain rise there cannot be cleanly attributed either way. Net: the combustion/air-path "Disagree" call in the table above should be read as "mostly explained by warm-up drift, not cavitation" rather than as a genuine fault effect — the real, checklist-matching CW signature is the rolling-std fluctuation, not a mean shift. Read this table together with the dedicated cavitation analysis (`01_cavitation_rolling_std.png`, `01_cavitation_shifts.csv`), not instead of it.

### Turbine degradation (TD)

| Channel | Expected | Observed shift | Std ratio | Agree / Disagree / Unclear |
|---|---|---|---|---|
| Exh.Gas Temp. Turbine Out (T5) | ↑ strong | +0.44 | 0.85 | Agree |
| Charge Air Press. (Pturb) | ↓ strong | −1.64 | 0.45 | Agree |
| Exh.Gas Temp. Turbine In (T4) | ↑ moderate | +1.12 | 0.76 | Agree |
| No.1 Exh.Gas Temp. (T1) | ↑ moderate | +0.81 | 0.79 | Agree |
| No.2 Exh.Gas Temp. (T2) | ↑ moderate | +1.42 | 0.75 | Agree |
| No.3 Exh.Gas Temp. (T3) | ↑ moderate | +0.95 | 0.80 | Agree |
| TCH Power (Qturb) | ↓ moderate | −0.03 | 0.84 | Unclear |
| Max. In-Cylinder Press. No.1 (Pmax) | slightly ↓ weak | −0.56 | 0.93 | Agree |
| Turbine temperature drop (T4−T5) | ↓ strong | +0.03 | 0.85 | Disagree |

TD is the cleanest match to the checklist of all five faults: every strong and moderate prediction lands in the right direction, with Pturb and the exhaust chain (T1–T5) moving together as the mechanism describes. Only Qturb stays essentially flat where a moderate drop was expected — worth checking whether TCH Power in this dataset already nets out the turbocharger speed loss the checklist assumed it would show directly. The one surprise is the turbine temperature drop itself: T4 and T5 both rise by similar amounts (+1.12 and +0.44 SD respectively), so T4−T5 barely moves rather than shrinking — a degraded turbine extracting less energy should widen the gap between inlet and outlet temperature, not leave it flat. TD's pre-fault segments (`00_switch_on.png`) are close to steady state at all three loads, so this is not a warm-up artefact; it is worth checking whether T5's sensor position downstream of the turbine responds more slowly than T4 during the ramp, compressing the apparent drop.
