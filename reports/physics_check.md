# Physics check on SHAP explanations

Applies `keyframe.explain.physics_check` (R5) to the T-002 SHAP arrays
(`data/processed/experiments/shap_fold{40,60,75,85}.npz`), combined across all four
LOLO folds: for each fault, the top 5 features by mean |SHAP| over that fault's own
held-out rows, each mapped to its source channel(s) and checked against
`keyframe.explain.CHECKLIST` (the pre-registered "Expected top 5" plus any "Agree"
channel from `reports/engineering_checklist.md`'s Observed section). A fault passes
with at least 3 of 5 matches and no day-dependent channel in its top 5.

## Result: 2 of 5 faults pass (target 4 of 5) — **not met**

| Fault | Top 5 features (mean \|SHAP\|, all folds combined) | Channel(s) | Match | Day-dependent | Pass |
|---|---|---|---|---|---|
| AC | `Charge Air IC Air Temp. Out_roll_300s_mean`, `Charge Air IC Air Temp. Out`, `Charge Air IC Air Temp. Out_roll_900s_mean`, `Charge Air IC Air Temp. Out_roll_60s_mean`, `Mechanical Efficiency_roll_300s_mean` | T15 (×4), Mechanical Efficiency | 4/5 | No | **Yes** |
| AF | `Engine Cooling water flow_roll_300s_mean`, `Fuel Oil Temp. Flow meter In_roll_900s_mean`, `Engine Cooling water flow_roll_900s_mean`, `Engine Cooling water flow`, `Fuel Temp._roll_900s_slope` | Qw_eng (×3), T21, T18 | 0/5 | **Yes** (T21, T18) | No |
| INJ | `phys_exhaust_temp_dev_3_roll_60s_mean`, `No.3 Exh.Gas Temp._roll_300s_mean`, `phys_exhaust_temp_spread`, `phys_exhaust_temp_dev_3_roll_900s_mean`, `phys_exhaust_temp_dev_3_roll_300s_mean` | T1–T3 (all five) | 5/5 | No | **Yes** |
| CW | `Sea Cooling Water Press.`, `Sea Cooling Water Press._roll_60s_mean`, `Sea Cooling Water Press._roll_300s_mean`, `LO Cooling Water Temp. In`, `Charge Air IC Cooling Water Temp. In` | Pl_water2 (×3), T12, T17-in | 0/5 | **Yes** (Pl_water2, T12) | No |
| TD | `Indicated Efficiency_roll_900s_std`, `phys_fuel_flow_per_kw_roll_900s_mean`, `LO Cooling water flow_roll_300s_mean`, `TCH LO Cooling water flow_roll_900s_mean`, `LO Circulating Pump Press._roll_900s_std` | Indicated Efficiency, Fuel Flow/Shaft Power, LO Cooling water flow, TCH LO Cooling water flow, LO Circulating Pump Press. | 0/5 | No | No |

## Mismatch investigations

**AC (pass, 4/5).** The one non-match, `Mechanical Efficiency_roll_300s_mean`, is not
in the checklist's expected list or Observed "Agree" set. Mechanical efficiency falls
as more charge air temperature raises exhaust and in-cylinder temperatures, so this is
a **plausible mechanism the checklist missed** (a downstream consequence of the
fouling, not a shortcut) rather than a correlated proxy or day artefact — no channel in
AC's top 5 is day-dependent.

**AF (fail, 0/5, day-dependent).** The checklist itself already found, in its Observed
section, that AF's exhaust temperatures do not rise as predicted at this load range
(T1, T2, T4 all Disagree). The model's top 5 instead lean on `Engine Cooling water
flow` and the two day-dependent fuel-temperature channels (T18, T21). This matches the
checklist's own pre-registered risk ("Gradual faults" / test-day shortcut): AF is a
slow, run-long drift, so a fuel-temperature channel that co-varies with which day a run
was recorded on is a **test-day shortcut**, not a correlated proxy of the expected
boost-loss mechanism. `Engine Cooling water flow` has no expected mechanism link to air
filter clogging either; flagged as a shortcut candidate, not a proxy.

**CW (fail, 0/5, day-dependent).** The checklist's own note (`reports/targets.md`)
already expects CW's true signature to be the *rolling standard deviation* of Pl_water1
and Qw_eng, not a mean-level channel — and the pre-registered checklist explicitly
allows a day-dependent mean-level channel here to be a red flag. `Sea Cooling Water
Press.` (Pl_water2, day-dependent; kept as a model input because notebook 01 judged it load-linked, which this result now calls into question) and `LO Cooling Water Temp. In`
(T12, day-dependent) dominate the top 5 instead of the expected rolling-std features:
this is a **test-day shortcut** exactly as the checklist warned against, not a genuine
cavitation mechanism. `Charge Air IC Cooling Water Temp. In` has no expected mechanism
link to cavitation and is a further shortcut candidate.

**TD (fail, 0/5, no day-dependent hit).** None of the checklist's core mechanism
(Pturb, T4, T5, turbine temperature drop, Qturb) appears in the top 5. Instead, LO
system channels (`LO Cooling water flow`, `TCH LO Cooling water flow`, `LO Circulating
Pump Press.`) and `Indicated Efficiency`/fuel-flow-per-kW dominate. These are not
day-dependent, so this isn't the test-day shortcut the checklist warns about; they are
more likely **correlated proxies**: raised back pressure lowers indicated efficiency
(a genuine downstream consequence, plausible mechanism the checklist missed, like AC's
mechanical efficiency), while the LO-side channels tracking engine load/thermal state
may correlate with TD's slowly growing severity without being caused by it. Worth a
follow-up residualising these channels against load before trusting them as TD
features (T-005's permutation-importance and PDP cross-checks are a natural next
place to test this).

## Summary

Only AC and INJ meet the pre-registered bar; the brief's target of 4 of 5 is **not
met**. Two of the three failures (AF, CW) are day-dependent test-day shortcuts the
checklist explicitly anticipated as a risk; the third (TD) looks like correlated
proxies for a real but weaker mechanism rather than a shortcut. This is reported
honestly rather than tuned to reach the target.
