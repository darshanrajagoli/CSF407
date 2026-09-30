# CS F407 — Laboratory: Logical Reasoning for Planning

Warehouse robot, package from A to C. Specify the planning problem, build a
plan by hand, get an LLM to implement the planner, test it, work out where
logic ends and search begins, and — the optional extension — use Prolog as an
independent verifier of the result.

```
.
├── INDEX.md                 <- you are here
├── logic_lab_ex.pdf         <- the original lab handout
│
├── deliverables/            <- SUBMIT THIS
└── explainers/              <- for understanding only, do not submit (LOCAL ONLY, git-ignored)
```

---

## `deliverables/` — what gets submitted

The handout asks for seven things (§4). All seven are covered.

| # | The lab asks for | Where it is |
|---|---|---|
| 1 | Your specification of the planning problem | `LAB_REPORT.md` §1, full version in `task0_1_specification_and_plan.md` |
| 2 | Your manually constructed plan | `LAB_REPORT.md` §2, full version in `task0_1_specification_and_plan.md` |
| 3 | The prompt used with the LLM | `prompts.md` (Prompt 1 is the Task 2 prompt; all seven are recorded) |
| 4 | The generated Python program | `planner.py` |
| 5 | The results of your tests | `LAB_REPORT.md` §4, raw output in `test_results.txt` |
| 6 | Answers to the "Think About It" questions | `LAB_REPORT.md` §1 (applicability), §3 (where the four spec ideas landed), §5 (logic vs. search), §6 (trusting an explanation), §8 (generate → verify) |
| 7 | Your reflection on the use of the LLM | `LAB_REPORT.md` §7, and the seven reflection questions answered in §9 |

The optional Prolog extension (Tasks 6, 7, 8 and §7.2's four questions) is
`LAB_REPORT.md` §8.

> The handout also asks you to **clearly identify which parts of the program
> were generated or modified with LLM assistance.** Every such part is marked
> `[HAND]` in `planner.py` where it was written or repaired by hand, and the
> full division is tabulated at the end of `prompts.md`.

**If you submit one file, submit `LAB_REPORT.md`** — it is self-contained and
covers all seven items. Everything else is the evidence it cites.

### Every file in `deliverables/`

| File | What it is |
|---|---|
| `LAB_REPORT.md` | **The main document.** Ten sections, following the lab tasks in order. |
| `task0_1_specification_and_plan.md` | Tasks 0 and 1 in full — the pre-LLM specification and the hand-built plan |
| `planner.py` | The planning agent: propositions, actions, BFS, independent plan validation |
| `test_planner.py` | Task 3 — Tests A, B, C plus eight more; 42 checks |
| `experiments.py` | The measurements behind §5, §6 and §7 of the report |
| `prompts.md` | Every prompt issued to the LLM, what came back, and what was done about it |
| `planner.pl` | Tasks 6 and 7 — the warehouse as independent Prolog facts and rules |
| `reasoning.pl` | Task 8 — `wet_road`/`slippery`/`reduce_speed`, and the penguin |
| `prolog_engine.py` | A minimal SLD-resolution engine (SWI-Prolog is not installed here) |
| `run_prolog.py` | The Prolog session: every query, plus the generate → verify loop |
| `planner_output.txt` | Raw output of `planner.py` |
| `test_results.txt` | Raw output of `test_planner.py` |
| `results.txt` | Raw output of `experiments.py` |
| `prolog_session.txt` | Raw output of `run_prolog.py` |

### Reproducing the numbers

```bash
cd deliverables
python planner.py         # the warehouse solved  -> 4-action plan
python test_planner.py    # Task 3                -> 42 passed, 0 failed
python experiments.py     # state space, the three defects, BFS vs DFS
python run_prolog.py      # Tasks 6, 7, 8
```

Python standard library only. No installation, no arguments, a second or two
each.

---

## `explainers/` — for understanding, not for submission

> **Local only.** This folder is git-ignored. It stays on this computer and is
> not on GitHub.

| File | What it is |
|---|---|
| `explainer.md` | **Read this.** The whole lab from zero, for someone with no CS background: an opening story, then one idea per section, each ending with a 📝 Notes box, and a one-page cheat sheet with likely exam questions at the end. |

Covers: what a proposition and a state are, and why absence means false · why `frozenset` and not
`set` · preconditions as an entailment check `S ⊨ Pre(a)` · why the effect order
is specified in advance · why the goal test is `⊆` and never `=` · how the
action definitions describe a graph nobody builds · **why the `visited` set is
a termination requirement, not an optimisation** · why the handout's own
suggested plan is invalid · **the bug no Python test could catch, and why** ·
Prolog facts, rules, Horn clauses, modus ponens, unification, SLD resolution and
negation as failure · what to remember · likely exam questions with answers.

---

## The three things worth knowing

**1. The answer is a four-action plan, and four is provably optimal.**

```
PickUp(Package,A) → Move(A,B) → Move(B,C) → Drop(Package,C)
```

One `PickUp` and one `Drop` are unavoidable; two `Move`s are unavoidable
because A and C are not adjacent. The handout's own suggested ordering —
`Move(A,B)`, `PickUp(Package,B)`, … — is **invalid at step 2**, because `Move`
does not move the package. That trap is the most useful thing in Task 1.

**2. The `visited` set is a termination requirement, not an optimisation.**
`Move(A,B)`/`Move(B,A)` is a 2-cycle. Without duplicate detection the planner
returns the *same correct 4-action plan* on the solvable problem — 25 expansions
instead of 8 — and on the **unsolvable** problem it never reports failure at
all: still expanding at 50,000 states, against 3 for the corrected version.
Test A cannot tell the two versions apart. Test B is what finds it.

**3. One bug was invisible to every check that could be written in Python.**
The LLM instantiated `Move` over *all six* ordered pairs of locations instead of
the four connected ones, so `Move(A,C)` existed. The planner then returned a
**3-action plan** that:

- satisfied every precondition at every step;
- re-executed correctly from *I* and reached the goal;
- was certified by BFS as the **shortest** such plan;
- and was **confirmed, correctly, by the LLM** when asked to justify it.

All four confirmations were true and all four were useless, because they were
evaluated *against the action set*, and the action set was the thing that was
wrong. It was found by noticing **three** actions where the hand-built plan
needed **four** — and caught mechanically only by `planner.pl`, which holds the
warehouse connectivity independently and answers `false`.

> **A generated explanation is not the same as an independent verification —
> and an independent *execution* is only as good as the model it executes.**

---

## A note on the Prolog section

SWI-Prolog is not installed on this machine. `planner.pl` and `reasoning.pl`
are ordinary standard Prolog and load unchanged in `swipl` or SWISH — you can
paste them in and check. Rather than quote output that was never produced, they
are executed here by `prolog_engine.py`, a small SLD-resolution engine
(unification, backtracking, definite clauses, `\+`) written for this laboratory.
Every answer in `prolog_session.txt` is a real answer computed from the real
`.pl` files.

---

## What to do yourself

Tasks 0 and 1 are meant to be done **before** any prompting — the handout is
explicit, and this run is a good argument for why: the specification written in
Task 0 predicted Defect 0 in advance, and the plan built in Task 1 is the only
reason Defect 2 was ever noticed.

Read `task0_1_specification_and_plan.md` and put it in your own words. Four
things to be able to defend if asked:

- **The goal is entailed, not equalled.** `G ⊆ S`. *G* is a *partial*
  description of the world, so the final state legitimately contains more than
  *G* does.
- **`Move` does not move the package** — unless it is held, in which case it has
  no location proposition at all. That is what makes the handout's suggested
  ordering invalid.
- **`Drop(Package,C)` is not applicable in *I*** even though it is the action
  that achieves the goal and it is on the list of available actions. Neither of
  those is the applicability test.
- **The missing box in Task 4's diagram** is the applicability decision,
  *S* ⊨ Pre(*a*). Everything above it is logic; everything below it is search.
