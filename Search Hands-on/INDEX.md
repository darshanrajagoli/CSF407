# CS F407 — Laboratory: Search and A\*

Warehouse robot navigation. Formulate the problem, implement A\* with an LLM's
help, test it, compare it with BFS, investigate the heuristic, reflect on the
process.

```
.
├── INDEX.md                 <- you are here
├── search_lab_ex.pdf        <- the original lab handout
│
├── deliverables/            <- SUBMIT THIS
└── explainers/              <- for understanding only, do not submit
```

---

## `deliverables/` — what gets submitted

The lab asks for eight things. All eight are covered.

| # | The lab asks for | Where it is |
|---|---|---|
| 1 | Formulation of the search problem | `LAB_REPORT.md` §1, full version in `task0_1_formulation_and_design.md` |
| 2 | Design of the agent | `LAB_REPORT.md` §2, full version in `task0_1_formulation_and_design.md` |
| 3 | The final Python program | `astar_warehouse.py` |
| 4 | The prompts used with the LLM | `prompts.md` |
| 5 | Results of the tests | `LAB_REPORT.md` §4, raw output in `test_results.txt` |
| 6 | The BFS / A\* comparison | `LAB_REPORT.md` §6, raw output in `results.txt` |
| 7 | The heuristic investigation | `LAB_REPORT.md` §7 |
| 8 | Answers to the reflection questions | `LAB_REPORT.md` §8 and §9 |

**If you submit one file, submit `LAB_REPORT.md`** — it is self-contained and
covers all eight items. The rest are the supporting evidence it refers to.

### Every file in `deliverables/`

| File | What it is |
|---|---|
| `LAB_REPORT.md` | **The main document.** Nine sections, one per lab task. |
| `task0_1_formulation_and_design.md` | Tasks 0 and 1 in full — the pre-LLM design |
| `astar_warehouse.py` | The program: A\*, BFS, four heuristics, reporting |
| `test_search.py` | Task 3 test suite — 6 maps, 20 checks |
| `experiments.py` | Tasks 5 and 6 — the comparison measurements |
| `prompts.md` | Appendix of every prompt issued to the LLM |
| `results.txt` | Raw output of `experiments.py` |
| `test_results.txt` | Raw output of `test_search.py` |
| `warehouse.txt` | The supplied map, extracted from the PDF as plain text |

### Reproducing the numbers

```bash
cd deliverables
python astar_warehouse.py     # solve the warehouse -> 40 moves
python test_search.py         # Task 3  -> 20 passed, 0 failed
python experiments.py         # Tasks 5 and 6 -> the comparison tables
```

No libraries needed beyond the Python standard library.

---

## `explainers/` — for understanding, not for submission

| File | What it is |
|---|---|
| `explainer.pdf` | **Read this.** 10 pages, everything from first principles. |
| `explainer.tex` | LaTeX source, if you want to edit it |

Covers: what a search problem is · state vs. node · how BFS/DFS/UCS/Greedy/A\*
differ · `f = g + h` worked on real cells from this map · what the code actually
does (heap, closed set, lazy deletion) · **the tie-break bug and why it matters**
· admissible vs. consistent vs. informative · what happens when you break
admissibility · what to remember · likely exam questions.

Rebuild the PDF with `pdflatex explainer.tex` (run twice, for the contents page).

---

## The three results worth knowing

**1. The answer is 40 moves.** `h(s₀) = 20` is a lower bound, so the shelves
exactly double the ideal distance. The route is forced — the warehouse is
essentially one long corridor.

**2. The first working A\* was secretly BFS.** It passed all 20 tests and
returned optimal paths, while expanding 116 of 130 cells on an open test map —
*identical* to BFS, same peak frontier. Cause: on a unit-cost grid, Manhattan
makes `f = g + h` constant along every sensible route (all 130 cells had `f = 25`),
so the tie-break rule alone decided the order — and FIFO order *is* BFS order.
Breaking ties toward larger `g` fixed it: **116 → 26 expansions**, same 25-move
path. No test caught this; only an implausible *number* did.

**3. Inflating the heuristic trades correctness for speed.** `2 × Manhattan`
still returned optimal paths on both supplied maps — inadmissibility removes the
*guarantee*, it doesn't force a violation. Over 2,754 random maps it returned a
suboptimal path on **25.9%** of them. On the worked example: 77% fewer expansions,
path 2 moves too long.

---

## Confidence in the code

Beyond the 20 fixed tests, the final program was fuzzed against an independently
written BFS oracle over **6,000 random maps** (3,372 solvable, 2,628 unsolvable) —
**36,000 A\* runs** across three admissible heuristics and both tie-break rules.
Every run agreed with the oracle on path length, returned a legal contiguous path,
and correctly reported failure where no path existed. **Zero disagreements.**

Every figure quoted in `LAB_REPORT.md` was cross-checked against the actual
contents of `results.txt` and `test_results.txt`.

---

## One thing to do yourself

Tasks 0 and 1 are meant to be written **before** any LLM prompting — the handout
is explicit that if you cannot specify the problem, generating code is premature.
Task 7 then asks you to separate what you designed from what the LLM contributed.

So read `task0_1_formulation_and_design.md` and put it in your own words. Three
points to be able to defend if asked:

- **State is position only.** Path-so-far and step count are *history*, not
  state — folding them in breaks duplicate detection.
- **The goal is tested on pop, not on generation.** That is what makes A\*
  optimal.
- **`h(s₀) = 20`**, so no route can beat 20 moves. The actual answer is 40.
