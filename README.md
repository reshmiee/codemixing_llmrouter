# Code-mixing and score compression in LLM routing

Does the RouteLLM BERT router score Hinglish questions differently from their English twins?
Main finding (152 confirmatory pairs): the average score is the same, but Hinglish scores have about half the spread of English scores, so routing depends on the cut-off. Answer quality was not measured.

Team: Jhalak Mittal, Aryan Singhal, Reshmi Yadav, Neha Malhotra (GLA University).

## Layout
| Folder | Contents |
| --- | --- |
| `data/processed/` | `confirmatory_v1.csv`, the frozen 152 pairs (IDs 101-252). Never edit. |
| `data/provenance/` | Earlier drafts of the frozen file. Not for scoring. |
| `scores/` | `scores_confirmatory_v1.csv`, `scores_triple_v1.csv`, `scores_ood_scrambled_v1.csv` (confirmatory run). [Other files: pilot / exploratory, see below.] |
| `features/` | `features_confirmatory_v1.csv`, `features_triple_v1.csv`. [Others: pilot.] |
| `configs/` | `config_conf_v1.json` (router, version, file hash), `config_v4.json` (the five cut-offs). |
| `results/person3/` | Confirmatory analysis outputs, `_v2` set (the one the paper cites). |
| `notebooks/` | Dataset building, scoring and analysis notebooks (outputs stripped). |
| `routerbench/` | Why-BERT experiment on 997 RouterBench prompts. Scores only, no prompt text. |
| `HASHES.md` | SHA-256 of every frozen file. Check with `python scripts/verify_hashes.py`. |

## Rules
- Frozen files are never edited. A fix becomes a new version with a new hash and a new run.
- Scoring ran once on the frozen file. The analysis notebook ran more than once (`_v1`, `_v2`); the paper cites `_v2`.
- Cut-off shares (10/20/30/50/70%) are nominal, from Chatbot Arena calibration.

## Status
Pilot (80 pairs) and confirmatory (152 pairs) done. In progress: third set (200 pairs), paper fixes, final correction model (Hinglish only, tuned on the third set, tested once on the 152 pairs). The earlier correction demo was removed (tag `pre-cleanup` keeps it).

## Not included
ARC and LeetCode question text is not to be released; release will use pair IDs, source IDs and our own Hinglish text.
