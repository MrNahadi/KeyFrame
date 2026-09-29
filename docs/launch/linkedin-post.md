# LinkedIn post (draft for the owner)

Drafted 29 September 2026. Every number is from the locked results (`reports/model_card.md`). Replace the two links in brackets before posting.

---

My final-year project, Marine AIMS, trained a fault model on a synthetic engine dataset. It scored well. Then I checked the data: no correlation between sensors, no link between one reading and the next, faults that lasted one second. The model had learned the generator, not the engine.

So I rebuilt it on real data. Keyframe diagnoses faults on a marine diesel from its sensor readings, using the Marine Engine Fault Dataset (BahooToroody et al., 2026): a Matsui MU323DGSC on a test bench, with five faults switched on partway through 2 to 3 hour runs.

The rule I set myself: every score comes from an engine load the model never saw in training, and the targets, plus a checklist of what each fault should do to the sensors, were written down before any model saw the data.

What came out:
- Macro F1 of 0.717 on unseen loads. My target was 0.80.
- A sustained alarm on 6 of 13 fault runs, the fastest 3 minutes after the fault began.
- For air cooler fouling and injector clogging, the model reads the same sensors an engineer would.
- For two other faults it partly learned which day the test was run. Remove those channels and one fault's recall at 60% load drops from 0.96 to 0.

2 of 9 targets met. I would rather show that than a 0.99 from a random split.

You can replay a run, watch when the alarm fires and pause to see why: [demo link]
Code, paper and model card: [repository link]

#MarineEngineering #MachineLearning #PredictiveMaintenance #ConditionMonitoring
