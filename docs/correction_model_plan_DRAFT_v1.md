# Correction Model: Locked Plan (DRAFT v1, not yet locked)

Owner: Person 4 (Neha). Reviewers: Person 3 (Jhalak, analysis), Person 1 (Aryan, paper text). Status: **DRAFT**. Everything in `[brackets]` is still to be filled. After all four sign below, this file is frozen and may not be edited; any change becomes `correction_model_plan_v2.md` with a stated reason.

## 1. Question

The audit found that the RouteLLM BERT router gives Hinglish scores about half the spread of their English twins (SD ratio 1.93 on the 152 confirmatory pairs). Can a small model, fitted on the third set, map a Hinglish score to a corrected score so that Hinglish and English twins are routed alike, **without** damaging the ranking of hard questions?

This plan covers only the correction model, for the **BERT router only**. It does not re-test the audit. The matrix-factorisation (MF) router showed no compression on the 80 pilot and 152 confirmatory pairs (SD ratio 0.99 against BERT's 1.93, exploratory), so the compression looks specific to BERT. The correction is therefore a fix for one router's behaviour, not for routers in general. The old "first correction demo" is withdrawn and is not part of this plan or the paper.

## 2. Data and split

| Role | Data | Rule |
|---|---|---|
| Fit and tune | Third set (200 pairs, `[confirmatory_v2 / third_set file name]`, SHA-256 `[hash]`) | The only data used to fit or tune anything |
| Test, used once | 152 confirmatory pairs (`confirmatory_v1.csv`, hash in `HASHES.md`) and their saved scores | Scores are read once at the end. No tuning, no peeking before this plan is signed |
| Not used | 80 pilot pairs; MF scores; Spanish and Bengali sets | Pilot is retired from the correction model. MF scores sit around 0.2 and BERT's cut-offs do not apply to them. Spanish and Bengali are translations of the 152 test questions, so using them would leak the test set |

Splitting inside the third set is by `pair_id` (one row per pair, so twins never separate). Cross-validation: 10 folds, seed 0.

## 3. Inputs and target

**Allowed inputs (Hinglish text only):** the Hinglish **BERT** router score (the third-set scoring run also saves MF columns; they are not used); Hinglish token count, word count and fertility from the router's own tokenizer (same code as Person 3).

**Never allowed as inputs:** the English score or text, `task_type`, `difficulty`, `source`, `written_by`, `drafting_method`, anything computed from the English version.

**Target:** the English twin's router score. It is a proxy: it is used only to fit and to evaluate, never as an input, and no claim is made that it is the "true" difficulty.

## 4. Methods compared (all Hinglish-only; English scores are never changed)

1. **M0, no correction.** Original Hinglish score.
2. **M1, share-matched cut-off (training-free baseline).** For each of the five Arena cut-offs `t`, find the share `s` of third-set English scores at or above `t`. The Hinglish cut-off is the third-set Hinglish score quantile that sends the same share `s` to the strong model. Only routing decisions change, not scores.
3. **M2, quantile mapping (primary candidate).** Map each Hinglish score `h` to `F_E^-1(F_H(h))`, where `F_H` and `F_E` are the third-set empirical distributions of Hinglish and English scores, with linear interpolation between `K` knots and clipping at the ends of the third-set English range. The map keeps the ranking of questions.
4. **M3, linear regression** of the English score on the allowed inputs, predictions clipped to [0, 1].
5. **M4, small gradient boosting** on the allowed inputs, with the grid fixed in Section 5.

All five Arena cut-offs `0.5949, 0.5094, 0.4651, 0.4066, 0.3372` (from `config_v4.json`, confirmed to four decimals `[ ]`) are applied unchanged to corrected scores. The primary cut-off is 0.4066.

**Known equivalence, stated in advance.** M2 and M1 send exactly the same questions to the strong model at each cut-off when fitted on the same data (checked on synthetic data: 99.3 to 100% agreement, the rest being interpolation). So M2 cannot beat M1 on routing decisions. M2 adds a usable corrected score, M1 does not. Only M3 and M4 can beat M1, and only if the extra inputs carry information. The earlier ridge result (cross-validated R² about 0.05) makes a null result likely. A null result is a valid result and will be reported as such.

## 5. Tuning (third set only)

- M2: `K` in `{11, 21, 51, 101}`.
- M3: no tuning.
- M4: `max_depth` in `{1, 2, 3}`, `n_estimators` in `{25, 50, 100}`, learning rate 0.05, `subsample` 1.0, seed 0.
- Criterion: cross-validated mean absolute error between corrected Hinglish and English twin. Ties go to the simpler setting.

**Selection rule for the final model.** The final model is M2 unless M3 or M4 beats M2 on cross-validated mean absolute error by more than one standard error **and** beats M1 on cross-validated routing agreement averaged over the five cut-offs. If not, M2 is final. This rule is applied before the test set is opened.

## 6. Test protocol

1. Fit the final model on the whole third set. Save the model, its settings and the hash of the third-set scores file in `config_corr_v1.json`.
2. Record the hash of the 152 confirmatory score file. Apply the model **once** to the 152 Hinglish scores. Save to a new versioned file (`corrected_scores_conf_v1.csv`). Never overwrite.
3. Run Section 7 exactly once. Any analysis not in this plan is labelled **exploratory**.
4. Negative results are reported.

Bootstrap: 10,000 resamples of pairs, seed 0, 95% intervals. All tests two-sided. McNemar exact tests with Holm correction across the five cut-offs, as in the audit plan.

## 7. Measures and success criteria (on the 152 test pairs)

| Id | Measure | "Works" if |
|---|---|---|
| C1 | SD ratio, English over corrected Hinglish (original 1.93) | 95% interval contains 1 |
| C2 | McNemar on routing decisions at the five cut-offs (originally 4 of 5 significant after Holm) | No cut-off has Holm-adjusted p < 0.05 |
| C3 | Hard-versus-Easy AUC of corrected Hinglish scores, against the original Hinglish AUC (English is 0.610, 95% CI 0.518 to 0.700) | Corrected AUC is not lower than original by more than 0.02 |
| B1 | Final model against M1 on routing agreement with English, averaged over five cut-offs (paired bootstrap) | Interval for the difference excludes 0. Only applies if M3 or M4 is final |

**Always reported, not pass or fail:** mean absolute error against the English twin (original vs corrected, paired bootstrap interval); orthogonal slope; strong-call shares and discordant pair counts (English-only and Hinglish-only) at each cut-off; Cohen's kappa at each cut-off.

"Works" means C1, C2 and C3 all hold. If only some hold, the paper says which. **Not significant is not the same as no gap.** With 152 pairs, C2 cannot show equivalence, so discordant counts are always shown next to p-values.

Expected, stated in advance: a monotone map such as M2 leaves question ranking and therefore the AUC unchanged, so C3 mainly guards M3 and M4.

## 8. Exploratory checks (labelled as such)

- Refit on the third set without the Coding pairs (they were drafted with AI help), and rerun Section 7.
- Results by task type and by difficulty.

## 9. Limitations to state in the paper

- One router, one language pair, one strong and weak pair; the target is the English twin's score, not answer quality.
- The compression appeared with BERT but not with MF (exploratory), so this correction addresses a router-dependent effect. Nothing is claimed for other routers.
- The 152 pairs are the final **held-out** test: nothing is fitted or tuned on them. They are not strictly untouched, so the paper should say "held-out" rather than "untouched": the earlier demo and the audit were run on it, and quantile mapping was suggested by the compression seen there. The procedure is confirmatory, but a fresh fourth set would be stronger evidence.
- M1 and M2 assume Hinglish and English questions have the same difficulty distribution. Matched pairs guarantee this here. Real Hinglish traffic may differ.
- The correction applies only to Hinglish input, so it needs a language detector in use. No detector is evaluated here.
- Arena cut-offs are not calibrated on Hinglish traffic. Nothing is claimed about the models Hinglish users receive.
- The third set's Coding pairs were AI-drafted, then edited by the writer.

## 10. Files (new, versioned, never overwritten)

`corrected_scores_conf_v1.csv`, `correction_results_v1.csv`, `config_corr_v1.json`, `Person04_CorrectionModel.ipynb`.

## 11. Sign-off

| Name | Role | Date |
|---|---|---|
| Neha Malhotra | Person 4 | |
| Jhalak Mittal | Person 3 | |
| Aryan Singhal | Person 1 | |
| Reshmi Yadav | Person 2 | |
