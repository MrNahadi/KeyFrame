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

Added by notebook 01 (roadmap item 3), below this line, without editing anything above. Shift is the median standardised shift (faulty − healthy, divided by healthy std) across the fault's runs; for the gradual faults (AC, AF, CW, TD) it is measured over each run's last 30 minutes, per `keyframe.eda.fault_shift`. Std ratio is faulty std / healthy std over the same window. Source: `reports/results/01_fault_shifts.csv`.

### Air cooler fouling (AC)

| Channel | Expected | Observed shift | Std ratio | Agree / Disagree / Unclear |
|---|---|---|---|---|
| Charge Air IC Air Temp. Out (T15) | ↑ strong | +29.8 | 10.8 | Agree |
| No.1 Exh.Gas Temp. (T1) | ↑ moderate | +1.17 | 0.66 | Agree |
| No.2 Exh.Gas Temp. (T2) | ↑ moderate | +1.43 | 0.65 | Agree |
| No.3 Exh.Gas Temp. (T3) | ↑ moderate | +1.63 | 0.78 | Agree |
| Exh.Gas Temp. Turbine In (T4) | ↑ moderate | +1.57 | 0.72 | Agree |
| Charge Air Press. (Pturb) | ≈ weak | −0.47 | 0.23 | Unclear |

AC matches the checklist cleanly: T15 rises far more than anything else in the dataset (standardised shift +29.8), and the whole exhaust chain (T1–T4) rises with it. Only Pturb, predicted flat, drifts down by less than half a standard deviation — small enough to call noise, not a real boost change.

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

AF's boost loss shows exactly as predicted (Pturb −1.62), but the exhaust temperatures do not rise with it — T1, T2 and T4 fall slightly instead, and T14 falls hard rather than rising. The checklist's "richer mixture raises exhaust temperature" story does not hold up over the last 30 minutes of these runs; either the governor's fuelling response outpaces the air loss at this load range, or the clogging in this dataset is milder than assumed. Worth residualising T1/T2/T4 against load before trusting them as AF features.

### Injector nozzle clogging (INJ)

| Channel | Expected | Observed shift | Std ratio | Agree / Disagree / Unclear |
|---|---|---|---|---|
| No.1 Exh.Gas Temp. (T1) | part of spread ↑ strong | +0.32 | 1.43 | — |
| No.2 Exh.Gas Temp. (T2) | part of spread ↑ strong | −0.21 | 1.25 | — |
| No.3 Exh.Gas Temp. (T3) | part of spread ↑ strong | −2.13 | 0.85 | Agree (spread) |
| Charge Air Press. (Pturb) | ≈ | −0.07 | 1.39 | Agree |
| Charge Air IC Air Temp. In/Out (T14/T15) | ≈ | −0.51 / −0.38 | 1.31 / 1.68 | Unclear |

INJ does the one thing the checklist says it should: the three cylinders stop agreeing. No.3's exhaust temperature drops 2.1 standard deviations below healthy while No.1 rises slightly, a 2.5 SD spread that dwarfs anything in the other faults — consistent with one nozzle under-fuelling its cylinder. The air path stays close to flat as expected, though std ratios above 1 everywhere hint this run is simply noisier throughout (INJ has no pre-fault segment to compare against, so "healthy" here is `matched_healthy` from other runs, not a same-run baseline — treat small shifts here cautiously).

### Cooling water pump cavitation (CW)

| Channel | Expected | Observed shift | Std ratio | Agree / Disagree / Unclear |
|---|---|---|---|---|
| Fresh Cooling Water Press. (Pl_water1) | mean ↓, fluctuation ↑ strong | −0.29 | 1.10 | Unclear |
| Engine Cooling water flow (Qw_eng) | mean ↓, fluctuation ↑ strong | −0.84 | 0.09 | Disagree (fluctuation) |
| Loss with cooling water (Qrej_eng) | noisier moderate | +0.01 | 0.40 | Disagree |
| Combustion/air path (T1–T3, T4, T5, Pmax, Pturb) | ≈ | −0.32 to −1.19 (Pturb) | 0.14–1.15 | Disagree |

CW is the puzzle T-004 already flagged: the checklist expects the combustion and air path to stay untouched, but Pturb (−1.19), T1–T4 and Pmax all move by moderate amounts over the last 30 minutes. The std ratios here are also lower, not higher, than healthy — the opposite of "fluctuation ↑". That is because this table uses the whole-window std, which last30 smooths out; the dedicated cavitation analysis (`01_cavitation_rolling_std.png`, `01_cavitation_shifts.csv`) computes rolling standard deviation instead and finds the real, non-artefactual variance signature the checklist predicted. Read this table together with that section, not instead of it.

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

TD is the cleanest match to the checklist of all five faults: every strong and moderate prediction lands in the right direction, with Pturb and the exhaust chain (T1–T5) moving together as the mechanism describes. Only Qturb stays essentially flat where a moderate drop was expected — worth checking whether TCH Power in this dataset already nets out the turbocharger speed loss the checklist assumed it would show directly.
