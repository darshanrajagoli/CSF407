# Appendix — Every Prompt Issued to the LLM

**CS F407 Artificial Intelligence** · Laboratory: Logical Reasoning for Planning
**Model used:** Claude (Anthropic). The handout permits ChatGPT, Gemini, Claude
or Microsoft Copilot.

The handout's instruction for Task 2 is specific:

> *Do **not** immediately ask the LLM to "solve the problem". Instead, give it a
> precise specification.*

Prompt 1 below is that specification. It is a transcription of the design table
at the end of `task0_1_specification_and_plan.md`, which was written before any
prompting began. The prompts that follow are the repair cycle: each one exists
because something in the previous output was found to be wrong.

Prompts are reproduced verbatim. The outcome line after each one records what
came back and what was done about it.

---

## Prompt 1 — the specification (Task 2)

> I want to implement a simple planning agent in Python.
>
> Represent a state as a set of logical propositions. Each action should
> contain:
>
> - a name;
> - positive preconditions;
> - negative preconditions;
> - positive effects;
> - negative effects.
>
> An action is applicable if all of its preconditions are satisfied by the
> current state. When an action is applied:
>
> 1. remove its negative effects from the state;
> 2. add its positive effects to the state.
>
> Use breadth-first search to find a sequence of actions that achieves a
> specified goal. The program should also:
>
> - detect when no plan exists;
> - print the resulting sequence of actions;
> - print the states reached after each action.
>
> Explain the implementation and identify any assumptions you make.
>
> Then instantiate the following domain.
>
> Locations A, B, C. The warehouse is a corridor: A is connected to B, B is
> connected to C, and **A is not connected to C**. Connections are
> bidirectional.
>
> Initial state: `At(Robot,A)`, `At(Package,A)`.
> Goal: `At(Package,C)`.
>
> Actions:
>
> - `Move(x,y)`, for connected x and y only.
>   Pre+ `At(Robot,x)`. Add `At(Robot,y)`. Del `At(Robot,x)`.
> - `PickUp(Package,x)`.
>   Pre+ `At(Robot,x)`, `At(Package,x)`. Pre- `Holding(Package)`.
>   Add `Holding(Package)`. Del `At(Package,x)`.
> - `Drop(Package,x)`.
>   Pre+ `At(Robot,x)`, `Holding(Package)`.
>   Add `At(Package,x)`. Del `Holding(Package)`.
>
> The goal is a partial description of the world, so the goal test is
> `goal ⊆ state`, not equality.

**Outcome.** Returned a complete, readable program: an `Action` class with the
five fields, an `applicable` method, an `apply` method, a BFS driver and a
printer. The structure was good and was kept. Three things were wrong:

1. states were plain `set`s, so they could not be put in a `visited` set;
2. there was no `visited` set at all;
3. `Move` was generated for **every ordered pair** of locations, despite the
   two separate places in the prompt that say only connected ones.

The explanation it produced alongside the code was fluent and did not mention
any of the three.

---

## Prompt 2 — the hashability error

> Running it gives `TypeError: unhashable type: 'set'` when a state is added to
> the visited set. Fix the state representation, and say why your fix is
> necessary rather than merely convenient.

**Outcome.** Correctly switched to `frozenset` and explained hashability. The
explanation was accurate. *Accepted.*

This is the class of error an LLM handles well: it is local, it has a
deterministic symptom, and the fix does not depend on anything outside the
code.

---

## Prompt 3 — the non-termination

> On the problem with the `PickUp` action removed, the program never prints
> "No plan found" — it runs indefinitely. Diagnose the cause and fix it.

**Outcome.** Diagnosed it correctly: `Move(A,B)` and `Move(B,A)` form a cycle,
so the frontier never empties, and BFS without duplicate detection re-expands
the same states forever. Added a `visited` set.

Two remarks. First, it needed to be *told* about the symptom — Task B is what
found this, not the model. Second, its first phrasing called the visited set
"an efficiency improvement". It is not: it is a **termination requirement**.
The comment in `planner.py::bfs_plan` was rewritten by hand to say so.

---

## Prompt 4 — asking it to verify its own plan (Task 5)

> For every action in the plan your program produced, identify its
> preconditions and show that those preconditions are satisfied in the state in
> which the action is executed.

**Outcome — this is the interesting one.** At this point the program still had
Defect 2 (unrestricted `Move`) and was returning the three-action plan

```
PickUp(Package,A) → Move(A,C) → Drop(Package,C)
```

The LLM produced a step-by-step verification of it. Every line of that
verification was **true**:

- `PickUp(Package,A)` requires `At(Robot,A)` and `At(Package,A)`; both hold in
  *S₀*. ✓
- `Move(A,C)` requires `At(Robot,A)`; it holds in *S₁*. ✓
- `Drop(Package,C)` requires `At(Robot,C)` and `Holding(Package)`; both hold in
  *S₂*. ✓
- *S₃* contains `At(Package,C)`, so the goal is achieved. ✓

The verification was sound with respect to the action model. The action model
was wrong. Nothing in the exercise of checking preconditions against effects
could have revealed that, because the illegal move had been written into the
set of actions being checked *against*.

The independent re-execution in `validate_plan` agreed with the LLM, for the
same reason. So did BFS, which additionally certified the plan as shortest.
**Three separate confirmations, all of them correct, all of them useless.**

---

## Prompt 5 — the model error, once it had been found by hand

> The plan uses `Move(A,C)`. A and C are not connected — the specification said
> so. Where did the `Move` actions come from, and what should the instantiation
> have been?

**Outcome.** Immediately identified the cause (`itertools.permutations` over
all locations rather than over a connectivity list), and produced the corrected
instantiation. It apologised and characterised it as an oversight.

Two things are worth recording:

- the correction was **easy** — one line, and the model had no difficulty with
  it once the error was named;
- the model **did not find it**. It was found by reading the plan and noticing
  three actions where the hand-built plan in Task 1 needed four.

The knowledge that A and C are not connected was in the prompt, twice. It was
still not applied. That is the gap that Task 7's Prolog verifier exists to
close: it holds the connectivity separately and checks the plan against it.

---

## Prompt 6 — the Prolog knowledge base (Task 6)

> Write a Prolog file describing a warehouse with locations a, b, c where a-b
> and b-c are connected in both directions and a-c is not. Define `can_move/2`
> from `connected/2`. Then add `valid_move/2` and a recursive `valid_route/2`
> that checks a list of `move(X,Y)` terms joins up and only uses connected
> pairs.

**Outcome.** Produced `connected/2`, `can_move/2`, `valid_move/2` and a
`valid_route/2` that was correct. Accepted with one hand change: `reachable/2`
was added afterwards, to make the point that `can_move/2` is deliberately
non-transitive and that reachability is a different question.

---

## Prompt 7 — the reflection questions

> For each of the reflection questions in the handout, tell me what a good
> answer would contain.

**Outcome.** Used only as a checklist against the answers already drafted in
§9 of `LAB_REPORT.md`. It suggested nothing that had not already been written,
and its answer to "what did you have to verify independently?" was generic —
it did not, and could not, know about the three defects in this particular run.
The answers in the report are written from the evidence in `results.txt` and
`test_results.txt`.

---

## What the LLM contributed, and what it did not

| | |
|---|---|
| **Generated by the LLM** | the `Action` / `Problem` class structure; `applicable`, `apply`; the BFS driver; the state-trajectory printer; the `frozenset` fix (Prompt 2); the `visited` set (Prompt 3); the first draft of `planner.pl` |
| **Specified by hand, then implemented by the LLM** | the five-field action representation; the delete-then-add order; the subset goal test; the domain itself |
| **Written by hand** | `validate_plan`; `why_inapplicable`; the whole of `test_planner.py`; the whole of `experiments.py`; `bfs_plan_no_visited` (kept to demonstrate Defect 1); `prolog_engine.py`; `run_prolog.py`; `reachable/2` in `planner.pl` |
| **Found by hand** | Defect 2. Both the LLM's explanation and the program's own re-execution certified the faulty plan as valid |

The division is not accidental. The LLM was good at everything whose
correctness could be judged **from inside the code**, and it was the wrong tool
for the one error whose correctness could only be judged **against the world**.
