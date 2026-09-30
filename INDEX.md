# CS F407: Artificial Intelligence — Repository Index

Coursework for **CS F407 (Artificial Intelligence)**, one folder per lab.

```
CS F407/
├── INDEX.md                        <- this file
├── ai_handout_2026-2027_s1.pdf     <- course handout
│
├── Search Hands-on/                <- Lab 1: Search and A*
├── Logic Hands-on/                 <- Lab 2: Logical reasoning for planning (+ Prolog)
├── Machine Translation Hands-on/   <- Lab 3: Transformer architectures
└── Bayesian Networks Hands-on/     <- Lab 4: Bayesian networks and autoregressive language models
```

Every lab folder has the same layout:

```
<Lab>/
├── INDEX.md          <- start here: what the lab asks for and where each answer is
├── *_lab_ex.pdf      <- the handout (Lab 3 has none)
├── deliverables/     <- what gets submitted (on GitHub)
└── explainers/       <- plain-English study notes (LOCAL ONLY, git-ignored, not on GitHub)
```

> **Explainers are local only.** Every `explainers/` folder is git-ignored and
> is not on GitHub.

---

## Course information

- **Course:** CS F407 Artificial Intelligence (3 credits)
- **Instructors:** Dr. Tirtharaj Dash (CC-107), Prof. Ashwin Srinivasan (D-167)
- **Handout:** [ai_handout_2026-2027_s1.pdf](ai_handout_2026-2027_s1.pdf)
- **Evaluation:** Lab work (best k of N) 20 · Comprehensive exam 30 ·
  Course project 30 · Paper reading 10 · Tutorial participation 10

---

## Lab 1 — Search and A\* ([`Search Hands-on/`](Search%20Hands-on/INDEX.md))

A warehouse robot finding its way around a 64-cell grid: problem formulation,
A\* vs BFS, and heuristic design, with an LLM writing the code.

| | |
|---|---|
| Handout | [search_lab_ex.pdf](Search%20Hands-on/search_lab_ex.pdf) |
| Main report | [LAB_REPORT.md](Search%20Hands-on/deliverables/LAB_REPORT.md) |
| Code | `astar_warehouse.py` · `test_search.py` (20 checks) · `experiments.py` |
| Explainer (local) | `explainers/explainer.pdf` — 10 pages from first principles |

**Key findings:** The optimal path is 40 moves. On a unit-cost grid, when
f-values tie, FIFO tie-breaking makes A\* expand as much as BFS; preferring the
deeper node cuts expansions from 116 to 26. The inadmissible heuristic
2×Manhattan gives a 30-move path where 28 is optimal.

```bash
cd "Search Hands-on/deliverables" && python test_search.py && python experiments.py
```

---

## Lab 2 — Logical Reasoning for Planning ([`Logic Hands-on/`](Logic%20Hands-on/INDEX.md))

Logic + search = planning: a propositional planner for moving a package A → C,
checked independently by Prolog.

| | |
|---|---|
| Handout | [logic_lab_ex.pdf](Logic%20Hands-on/logic_lab_ex.pdf) |
| Main report | [LAB_REPORT.md](Logic%20Hands-on/deliverables/LAB_REPORT.md) |
| Code | `planner.py` · `test_planner.py` (42 checks) · `experiments.py` · `planner.pl` · `reasoning.pl` · `prolog_engine.py` · `run_prolog.py` |
| Explainer (local) | `explainers/explainer.pdf` — 11 pages from first principles |

**Key findings:** The optimal plan has 4 actions: PickUp → Move(A,B) → Move(B,C) →
Drop. The `visited` set is needed for the planner to terminate, not just to make
it faster. An LLM-generated `Move(A,C)` passed every Python check and was only
caught by the independent Prolog knowledge base.

```bash
cd "Logic Hands-on/deliverables" && python test_planner.py && python run_prolog.py
```

---

## Lab 3 — Transformer Architectures ([`Machine Translation Hands-on/`](Machine%20Translation%20Hands-on/INDEX.md))

One notebook with one small demo per transformer shape: encoder-decoder
(translation, M2M100), decoder-only (generation, GPT-2) and encoder-only
(sentiment, DistilBERT).

| | |
|---|---|
| Notebook | [transformer_architectures_demo.ipynb](Machine%20Translation%20Hands-on/deliverables/transformer_architectures_demo.ipynb) |
| Explainer (local) | `explainers/explainer.md` — the notebook explained for a complete beginner |

---

## Lab 4 — Bayesian Networks and Autoregressive LMs ([`Bayesian Networks Hands-on/`](Bayesian%20Networks%20Hands-on/INDEX.md))

A first-order and a second-order n-gram language model built from six sentences,
seen as Bayesian networks: CPTs from counts, greedy vs sampled generation, and
the cost of more context.

| | |
|---|---|
| Handout | [bn_lab_ex.pdf](Bayesian%20Networks%20Hands-on/bn_lab_ex.pdf) |
| Main report | [LAB_REPORT.md](Bayesian%20Networks%20Hands-on/deliverables/LAB_REPORT.md) — Q1–Q14 plus the reflection |
| Code | `bigram_model.py` · `trigram_model.py` · `run_lab.py` · `test_models.py` (26 checks) |
| Prompts | [prompts.md](Bayesian%20Networks%20Hands-on/deliverables/prompts.md) |
| Explainers (local) | `explainers/explainer.md` (from zero to the whole picture, with notes boxes) · `explainers/code_walkthrough.md` |

**Key findings:** Greedy decoding loops forever (the → cat → sat → on → the …),
and the LLM's first version hung. A second word of context makes predictions
sharper, but 96 of 111 contexts have no data, and the model can only repeat its
six training sentences. Normalisation and chain-rule tests catch bugs that the
generated text hides.

```bash
cd "Bayesian Networks Hands-on/deliverables" && python test_models.py && python run_lab.py
```

---

## Term project

The term project (whospoke) lives in its own repository, not here:
https://github.com/darshanrajagoli/whospoke

---

## Run every test

```bash
python "Search Hands-on/deliverables/test_search.py"
python "Logic Hands-on/deliverables/test_planner.py"
python "Logic Hands-on/deliverables/run_prolog.py"
python "Bayesian Networks Hands-on/deliverables/test_models.py"
```
