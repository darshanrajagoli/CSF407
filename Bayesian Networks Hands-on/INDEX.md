# CS F407 — Laboratory: Bayesian Networks and Autoregressive Language Models

Build a tiny language model from six sentences: count which word follows which,
turn the counts into probabilities, generate text, then add a second word of
context and see what that buys and what it costs. Along the way, get an LLM to
write the code, and check that it actually implements the model.

```
.
├── INDEX.md                 <- you are here
├── bn_lab_ex.pdf            <- the original lab handout
│
├── deliverables/            <- SUBMIT THIS
└── explainers/              <- for understanding only (LOCAL ONLY, git-ignored)
```

---

## `deliverables/` — what gets submitted

The handout (§21) asks for seven things. All seven are covered.

| # | The lab asks for | Where it is |
|---|---|---|
| 1 | Python implementation of the first-order model | `bigram_model.py` |
| 2 | Python implementation of the second-order model | `trigram_model.py` |
| 3 | Conditional probability tables for selected contexts | `LAB_REPORT.md` §4 and §11; raw in `results.txt` |
| 4 | Examples of generated text | `LAB_REPORT.md` §9, §10, §13; `generated_sentences.txt` |
| 5 | Results of the probability-normalisation tests | `LAB_REPORT.md` §7; `test_results.txt`, `results.txt` |
| 6 | Answers to Questions 1–14 | `LAB_REPORT.md` §1–§16, one section per part of the handout |
| 7 | Reflection on LLM use, with a piece of code that was inspected and corrected | `LAB_REPORT.md` §17; prompts in `prompts.md` |

**If you submit one file, submit `LAB_REPORT.md`.** It answers everything and
cites the rest.

### Every file in `deliverables/`

| File | What it is |
|---|---|
| `LAB_REPORT.md` | **The main document.** One section per part, Q1–Q14, and the reflection |
| `bigram_model.py` | First-order model P(X_t \| X_{t−1}): counts, CPT, predict, greedy and sampling generation |
| `trigram_model.py` | Second-order model P(X_t \| X_{t−2}, X_{t−1}), with two `<START>` pads |
| `corpus.txt` | The six training sentences from the handout |
| `run_lab.py` | Runs Parts III–XIII and writes the two output files below |
| `test_models.py` | 26 checks: normalisation, hand counts, sampling matches the CPT, chain rule, edge cases |
| `prompts.md` | The prompts used to build the two models, what came back, and what was fixed |
| `results.txt` | Raw output of `run_lab.py` |
| `generated_sentences.txt` | 20 sampled sentences, plus 5 greedy and 5 sampled |
| `test_results.txt` | Raw output of `test_models.py` (26 passed, 0 failed) |

### Reproducing everything

```bash
cd deliverables
python run_lab.py       # all parts        -> results.txt, generated_sentences.txt
python test_models.py   # 26 checks        -> 26 passed, 0 failed
python bigram_model.py  # quick demo of the first-order model
python trigram_model.py # quick demo of the second-order model
```

Plain Python 3. No installs, no arguments. Seeded, so every number repeats exactly.

---

## `explainers/` — local only, for understanding

This folder is git-ignored. It stays on this computer and is not on GitHub.

| File | What it is |
|---|---|
| `explainer.md` | **Read this first.** Starts from zero (no CS, no probability) and builds to the whole picture. It has a 📝 notes box after every section, a cheat sheet, and likely exam questions |
| `code_walkthrough.md` | Every file and every important line of code, in plain English |

---

## The three things worth knowing

**1. Greedy decoding never finishes on this data.** The top choice after each
word gives the → cat → sat → on → the → …, a cycle that never reaches `<END>`.
The LLM's first version had no length cap, and it hung. Always taking the best
*next* word does not give the best *sentence*: the most probable sentences here
are "the mat", "the rug" and "the park".

**2. More context: sharper predictions, much hungrier model.** Going from one
word of context to two, P(mat | on, the) = 0.5 where P(mat | the) was 0.167. But
the table grows from 11 to 111 contexts on the same 42 transitions, 96 contexts
have no data at all, and the second-order model only ever reproduces its six
training sentences (0 new sentences in 1,000). The first-order model makes 886
new ones out of 1,000, mostly nonsense.

**3. Test what the maths guarantees, not what the output looks like.** Every CPT
row must sum to 1. Sampled frequencies must match the table. Sentence
frequencies must match the chain rule. A broken table can still produce
normal-looking text, because `random.choices` quietly rescales weights. Only
these invariants catch it.
