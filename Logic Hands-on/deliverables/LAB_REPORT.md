# Laboratory Report — Logical Reasoning for Planning

**CS F407 Artificial Intelligence** · Warehouse robot: deliver a package from A to C
Using an LLM to construct and test a simple planning agent

> **Logic + Search = Planning**
> Logic determines what is *possible*; search determines what to *try*.

**Files accompanying this report**

| File | Contents |
|---|---|
| `task0_1_specification_and_plan.md` | Tasks 0 and 1 in full — the specification and the hand-built plan, written *before* any prompting |
| `planner.py` | The planning agent: states, actions, BFS, independent plan validation |
| `test_planner.py` | Task 3 — Tests A, B and C plus eight more (42 checks) |
| `experiments.py` | The measurements behind §5, §6 and §7 |
| `prompts.md` | Appendix: every prompt issued to the LLM, and what came back |
| `planner.pl`, `reasoning.pl` | Tasks 6–8 — the independent Prolog knowledge bases |
| `prolog_engine.py`, `run_prolog.py` | A minimal SLD-resolution engine, and the query session |
| `planner_output.txt`, `test_results.txt`, `results.txt`, `prolog_session.txt` | Raw output reproducing every figure below |

Reproduce everything (standard library only, Python 3.8+):

```
python planner.py         # the warehouse problem solved
python test_planner.py    # Task 3        -> 42 checks passed, 0 failed
python experiments.py     # §5, §6, §7
python run_prolog.py      # Tasks 6, 7, 8
```

---

## 1. Specification of the planning problem (Task 0)

Full version in `task0_1_specification_and_plan.md`. In summary:

| Component | Specification |
|---|---|
| **I** | `{ At(Robot,A), At(Package,A) }` |
| **G** | `{ At(Package,C) }` |
| **A** | 10 ground actions: 4 × `Move`, 3 × `PickUp`, 3 × `Drop` |
| **Applicability** | *S* ⊨ Pre(*a*) ⟺ Pre⁺ ⊆ *S* and Pre⁻ ∩ *S* = ∅ |
| **Transition** | *S′* = (*S* − Del(*a*)) ∪ Add(*a*) — delete first, then add |
| **Goal test** | *G* ⊆ *S*, **not** *S* = *G* |

The warehouse is a corridor, `A — B — C`; **A and C are not connected**. That
single fact lives *outside* the action descriptions — it determines which
`Move` actions exist at all — and it turns out to be the fact that the LLM
dropped. It is also the fact the Prolog verifier of §8 holds independently.

| Action | Pre⁺ | Pre⁻ | Add | Del |
|---|---|---|---|---|
| `Move(x,y)`, *x*–*y* connected | `At(Robot,x)` | — | `At(Robot,y)` | `At(Robot,x)` |
| `PickUp(Package,x)` | `At(Robot,x)`, `At(Package,x)` | `Holding(Package)` | `Holding(Package)` | `At(Package,x)` |
| `Drop(Package,x)` | `At(Robot,x)`, `Holding(Package)` | — | `At(Package,x)` | `Holding(Package)` |

A state is a **set of true propositions**; anything absent is false — the
closed-world assumption. `Move` deliberately does not touch the package: if the
package is held, `Holding(Package)` is true and it has no `At(...)` proposition
to update, so it travels with the robot automatically.

### Which actions are applicable in *I*? (the Task 0 question)

**Exactly two: `Move(A,B)` and `PickUp(Package,A)`.** Confirmed by the program
(`planner_output.txt`) and by tests D1–D4.

> **Is `PickUp(Package,A)` applicable?** **Yes.** Its preconditions are
> `At(Robot,A)` and `At(Package,A)`. Both are in *I*, so *I* ⊨ Pre. Its
> negative precondition `Holding(Package)` is absent from *I*, and absent means
> false, so that is satisfied too.

> **Is `Drop(Package,C)` applicable?** **No**, and it fails on *both*
> preconditions: `At(Robot,C)` is false (the robot is at A) and
> `Holding(Package)` is false (the robot is carrying nothing).

The program's own account, from `planner_output.txt`:

```
applicable in I  : Move(A,B), PickUp(Package,A)
    blocked: Move(B,A)              missing At(Robot,B)
    blocked: Move(B,C)              missing At(Robot,B)
    blocked: Move(C,B)              missing At(Robot,C)
    blocked: PickUp(Package,B)      missing At(Package,B), At(Robot,B)
    blocked: PickUp(Package,C)      missing At(Package,C), At(Robot,C)
    blocked: Drop(Package,A)        missing Holding(Package)
    blocked: Drop(Package,B)        missing At(Robot,B), Holding(Package)
    blocked: Drop(Package,C)        missing At(Robot,C), Holding(Package)
```

---

## 2. The plan constructed by hand (Task 1)

### The suggested ordering is a trap — and that is the point

The handout says you "might need to reason about" `Move(A,B)`,
`PickUp(Package,B)`, `Move(B,C)`, `Drop(Package,C)`. **That sequence is not a
valid plan.**

| Step | Action | State before | Applicable? |
|---|---|---|---|
| 1 | `Move(A,B)` | `{At(Robot,A), At(Package,A)}` | yes |
| 2 | `PickUp(Package,B)` | `{At(Robot,B), At(Package,A)}` | **no — `At(Package,B)` is false** |

The robot walked to B without the package, because `Move` does not move the
package. The sequence mentions all the right actions in a plausible order and
is wrong at the second step. `test_planner.py::test_f` rejects it at step 2.

This is worth dwelling on: **the "looks reasonable but is invalid" failure
appears before an LLM is involved at all.** It is a property of plans, not of
language models.

### The correct plan, with the state after every action

```
    a₁ = PickUp(Package,A)      a₂ = Move(A,B)
    a₃ = Move(B,C)              a₄ = Drop(Package,C)
```

| State | Facts | Why the action producing it was applicable |
|---|---|---|
| *S₀* | `At(Robot,A)`, `At(Package,A)` | (the given initial state) |
| *S₁* | `At(Robot,A)`, `Holding(Package)` | `PickUp(Package,A)`: `At(Robot,A)` ✓, `At(Package,A)` ✓, `Holding` absent ✓ |
| *S₂* | `At(Robot,B)`, `Holding(Package)` | `Move(A,B)`: `At(Robot,A)` ✓ |
| *S₃* | `At(Robot,C)`, `Holding(Package)` | `Move(B,C)`: `At(Robot,B)` ✓ |
| *S₄* | `At(Robot,C)`, `At(Package,C)` | `Drop(Package,C)`: `At(Robot,C)` ✓, `Holding(Package)` ✓ |

*S₄* ⊇ *G*, so *S₄* ⊨ *G*. Note that *S₄* ≠ *G* — the robot is still at C.
An equality goal test would reject this correct plan.

**Four actions is optimal.** One `PickUp` and one `Drop` are unavoidable
(`At(Package,C)` is added only by `Drop`, which needs `Holding`, added only by
`PickUp`), and two `Move`s are unavoidable (A and C are not adjacent). 2 + 2 = 4.

---

## 3. The generated program (Task 2)

`planner.py`. The prompt is **Prompt 1** in `prompts.md`; it is the design table
from `task0_1_specification_and_plan.md` transcribed, not a request to solve the
problem.

The three ideas from the specification, and where each landed in the code:

| Specification idea | Where it appears |
|---|---|
| **Preconditions** → when is an action applicable? | `Action.applicable`: `pos_pre <= state and not (neg_pre & state)` |
| **Effects** → how does the state change? | `Action.apply`: `(state - neg_eff) \| pos_eff` |
| **Goal** → when does planning terminate? | `Problem.satisfies_goal`: `goal <= state` |
| **BFS** → how are alternative plans explored? | `bfs_plan`: FIFO `deque`, goal test on pop, `visited` set |

Result on the warehouse problem (`planner_output.txt`):

```
plan found       : True          states expanded  : 8
plan length      : 4             states generated : 16
                                 peak frontier    : 3

plan:
  1. PickUp(Package,A)     3. Move(B,C)
  2. Move(A,B)             4. Drop(Package,C)
```

which is exactly the hand-built plan of §2. The program then re-executes it
independently and prints every precondition it checked.

The reachable state space is **12 states** out of 10 ground actions
(`results.txt` §1) — small enough that the search is exhaustive and small
enough that *scale is never the source of an error here*. Every defect in §7
is an error of **modelling**.

---

## 4. Test results (Task 3)

`test_planner.py` — **42 checks, 0 failures** (`test_results.txt`). The handout
asks for at least three tests; there are eleven, because the required three all
passed on a version of the planner that was nevertheless broken (see §7).

Every test that expects a plan additionally sends it through `validate_plan`,
which re-executes it from *I* and checks each precondition itself. A plan of the
right *length* is not evidence.

### The three required tests, recorded as the handout asks

| | **Test A — solvable** | **Test B — impossible** | **Test C — irrelevant actions** |
|---|---|---|---|
| **Initial state** | `{At(Robot,A), At(Package,A)}` | `{At(Robot,A), At(Package,A)}` | `{At(Robot,A), At(Package,A)}` |
| **Goal** | `{At(Package,C)}` | `{At(Package,C)}` | `{At(Package,C)}` |
| **Change** | none — the original problem | `PickUp` removed | `PickUp` **and** `Drop` removed; robot may still roam freely |
| **Plan found?** | **yes** | **no** | **no** |
| **Plan** | `PickUp(Package,A) → Move(A,B) → Move(B,C) → Drop(Package,C)` | — | — |
| **Valid?** | **yes** — re-executed from *I*, all 4 preconditions verified, final state ⊨ *G* | n/a — reported "No plan found" after 3 expansions rather than inventing an action | n/a |

Test C's specific worry — *does the planner treat the robot reaching C as the
package reaching C?* — is checked directly:

```
{At(Robot,C), At(Package,A)}  ⊨  {At(Package,C)}  ?     False
```

and structurally: with `PickUp`/`Drop` removed the robot can still reach C
(verified by an independent reachability check, B3) and the planner still
correctly reports no plan. Adding a genuinely irrelevant action (`Wiggle`)
changes neither the plan nor its length (C3, C4).

### The full suite

| Test | What it establishes | Checks |
|---|---|---|
| **A** | solvable problem: 4-action plan, independently re-executable, `PickUp` before departure, all `Move`s between connected locations | 7 |
| **B** | `PickUp` removed → "no plan", and it *terminates* | 3 |
| **B2** | `Drop` removed → "no plan" (package can be held, never released) | 1 |
| **B3** | C disconnected entirely → "no plan" | 1 |
| **C** | robot at C ≠ package at C; irrelevant actions do not perturb the plan | 4 |
| **D** | applicability in *I*: `PickUp(Package,A)` yes, `Drop(Package,C)` no, exactly two applicable | 4 |
| **D2** | the **negative** precondition is enforced: no `PickUp` while `Holding` | 2 |
| **E** | goal test is entailment, not equality — and `S₄ ≠ G`, so `==` *would* have failed | 3 |
| **F** | the handout's suggested ordering is rejected, at step 2, for a missing precondition | 2 |
| **G** | delete-then-add ordering: a proposition in both lists survives | 2 |
| **H** | degenerate cases: goal already true → empty plan; no actions → no plan | 2 |
| **I** | BFS returns a **shortest** plan, confirmed against an independently written exhaustive depth-limited-search oracle; DFS returns a valid but unguaranteed one | 4 |
| **J** | the unsound domain returns a 3-action plan that passes *every internal check* | 4 |
| **K** | duplicate detection is required for **termination**, and its absence still passes Test A | 3 |
| | | **42** |

---

## 5. Logic and search (Task 4)

### Completing the diagram

```
                    Current state
                          ↓
              Check action preconditions
                          ↓
        ┌─────────────────────────────────────┐
        │   Is  S ⊨ Preconditions(a)  ?       │   ←  the missing box
        │   the action is APPLICABLE          │
        └─────────────────────────────────────┘
                          ↓
                Generate successor state
                  S′ = (S − Del) ∪ Add
                          ↓
                Search over alternatives
                          ↓
                    S′ ⊨ G ?
```

The missing step is the **applicability decision**: the logical question of
whether the current state entails the action's preconditions. Everything above
it is logic; everything below it is search.

### Where each is used, concretely

| | **Logical reasoning** | **Search** |
|---|---|---|
| **Question it answers** | *Can this action be done here, and what would the world look like afterwards?* | *Which of the things I can do should I try next?* |
| **In the code** | `Action.applicable`, `Action.apply`, `Problem.satisfies_goal` | `bfs_plan` — the `deque`, the `visited` set, the parent map |
| **Formally** | *S* ⊨ Pre(*a*); *S′* = Apply(*S*, *a*); *S* ⊨ *G* | order of expansion over the state graph |
| **If you change it** | the *set of legal plans* changes | *which* legal plan you find, and how fast |

### How they work together

Logic defines a **graph** without ever building it: the nodes are states, and
there is an edge *S* → *S′* labelled *a* exactly when *S* ⊨ Pre(*a*) and
*S′* = Apply(*S*, *a*). This graph is enormous and mostly irrelevant, and it is
never materialised — the applicability test *generates* the outgoing edges of a
node, on demand, the moment search asks for them.

Search then walks that graph looking for a node satisfying *G*. It contributes
no knowledge about the world at all; it only decides the order of questions.

`results.txt` §3 makes the division visible by swapping the search strategy and
leaving the logic untouched:

| Problem | Algorithm | Plan length | Expanded | Generated | Peak frontier |
|---|---|---|---|---|---|
| warehouse | BFS | **4** | 8 | 16 | 3 |
| warehouse | DFS | 4 | 7 | 13 | 2 |
| corridor, 6 locations | BFS | **7** | 27 | 58 | 8 |
| corridor, 6 locations | DFS | 7 | 13 | 28 | 5 |
| corridor, 8 locations | BFS | **9** | 47 | 101 | 11 |
| corridor, 8 locations | DFS | 9 | 17 | 38 | 7 |

Both return **valid** plans — because both use the same applicability test.
Only BFS returns a **shortest** plan, because it explores in order of increasing
plan length and every action costs 1. DFS happens to match it here only because
a corridor offers almost no wrong turns; on a branching map it need not.

This is the same relationship as in the previous module: BFS, DFS, UCS and A\*
differ only in the order they take nodes off the frontier. What is new in
planning is that the successor function is not given by a map — it is *computed
by a logical test*.

---

## 6. Can the LLM verify its own plan? (Task 5)

The handout asks which to trust: **(a)** the LLM's explanation, or **(b)** the
independently executed state transitions. The obvious answer is (b), and it is
right — but this run produced a case where **(b) was also not enough**, which is
a sharper version of the same lesson.

### What happened

At the point Prompt 4 was issued, the program still had Defect 2 (below), and
was returning

```
PickUp(Package,A) → Move(A,C) → Drop(Package,C)          (3 actions)
```

Asked to justify it, the LLM produced a step-by-step precondition check. **Every
line of it was true.** `PickUp(Package,A)` needs `At(Robot,A)` and
`At(Package,A)`: both hold in *S₀*. `Move(A,C)` needs `At(Robot,A)`: it holds in
*S₁*. `Drop(Package,C)` needs `At(Robot,C)` and `Holding(Package)`: both hold in
*S₂*. The final state contains `At(Package,C)`.

The independent re-execution in `validate_plan` agreed. BFS additionally
certified the plan as the shortest one. **Three confirmations, all correct, all
useless** — because `Move(A,C)` should never have been an action in the first
place, and all three checks were conducted against the action set that contained
it.

### The ordering of trust

1. **An independent check against an independent source of knowledge** —
   Prolog's `valid_route(a, [move(a,c)])` → `false` (§8). This is the only thing
   that caught it.
2. **Independently executed state transitions** — catches every error *within*
   the model: wrong preconditions applied, effects mis-sequenced, a plan whose
   steps do not join up. Cannot catch an error *in* the model.
3. **A generated explanation** — evidence of nothing. It is text conditioned on
   the plan, produced by the same process that produced the plan, and it will
   be just as fluent when the plan is wrong.

> **A generated explanation is not the same as an independent verification.**
> And an independent *execution* is only as good as the model it executes.

---

## 7. Reflection on the use of the LLM

Three defects reached working code. They are listed in increasing order of how
hard they were to find, which is the reverse of how serious they look.

### Defect 0 — goal test written as `state == G`

**Symptom:** "No plan found" on the original, obviously solvable problem.
**Cause:** the goal is a *partial* description of the world. *S₄* is
`{At(Package,C), At(Robot,C)}`; *G* is `{At(Package,C)}`. Equality fails; subset
succeeds (`results.txt` §2).
**Found by:** Test A, immediately.
**Note:** this had been predicted in writing in `task0_1_specification_and_plan.md`
before any prompt was issued, and Prompt 1 stated the subset test explicitly.
Stating it in the prompt is what made it a one-line fix instead of a puzzle.

### Defect 1 — no duplicate detection

**Symptom:** on the **unsolvable** problem the program never terminates.
**Cause:** `Move(A,B)` and `Move(B,A)` form a 2-cycle. The frontier refills
faster than it drains, so BFS never runs out of states and failure is never
reported.

| | corrected `bfs_plan` | defective version |
|---|---|---|
| solvable problem | 4-action plan, 8 expansions | 4-action plan, 25 expansions |
| unsolvable problem | **"no plan found", 3 expansions** | **still expanding at 50,000** |

**Found by:** Test B. **Test A cannot tell the two versions apart** — the
defective search returns the same correct 4-action plan.
**Worth recording:** the LLM initially described the fix as "an efficiency
improvement". It is not. It is a **termination requirement**, and the comment in
`planner.py` was rewritten by hand to say so.

### Defect 2 — `Move` instantiated over every pair of locations

**Symptom: none, from the inside.**

| | correct domain | defective domain |
|---|---|---|
| ground actions | 10 | 12 |
| plan | `PickUp(Package,A) → Move(A,B) → Move(B,C) → Drop(Package,C)` | `PickUp(Package,A) → Move(A,C) → Drop(Package,C)` |
| length | 4 | **3** |
| passes `validate_plan`? | yes | **yes** |
| shortest, per BFS? | yes | **yes** |
| supported by the warehouse? | yes | **no** |

**Cause:** `Move` was generated over all ordered pairs of locations rather than
over the connectivity list. The prompt said "for connected x and y only" and
separately said "A is not connected to C". Both were ignored.

**Why nothing internal caught it.** Preconditions, effects, the goal test, the
re-execution and the optimality argument are all evaluated *relative to the
action set*. The action set was the thing that was wrong. There is no test you
can write in Python, against this model, that rejects this plan — the search is
exhaustively correct over a state space that was described wrongly.

**Found by:** reading the output and noticing **three** actions where the
hand-built plan of Task 1 needed **four**. Not by a test. By a *number* that
disagreed with something worked out beforehand.

**Caught mechanically by:** the Prolog verifier, §8 — which holds the
connectivity independently and answers `false`.

### The pattern

| | Defect 0 | Defect 1 | Defect 2 |
|---|---|---|---|
| kind of error | logical | algorithmic | **modelling** |
| detectable from inside the code? | yes | yes | **no** |
| symptom | wrong answer | hang | **none** |
| found by | Test A | Test B | a human comparing with Task 1 |
| LLM's own explanation | silent | called the fix an optimisation | **confidently confirmed the wrong plan** |

The LLM was reliable on everything whose correctness is judged **from inside
the code**, and unreliable on the one thing whose correctness is judged
**against the world** — and it was *most* confident precisely there. That
asymmetry, not unreliability in general, is the finding.

**What was done about it:** the connectivity of the warehouse is now written
down twice — as `CONNECTED` in `planner.py` and as `connected/2` facts in
`planner.pl` — and `run_prolog.py` checks one against the other. The point is
not redundancy for its own sake; it is that the check is conducted **from
outside** the artefact being checked.

---

## 8. Optional extension — Prolog as a logical verifier (Tasks 6–8)

> **Note on execution.** SWI-Prolog is not installed on the machine used for
> this laboratory. `planner.pl` and `reasoning.pl` are standard Prolog and load
> unchanged in `swipl` or SWISH. Rather than quote output that was never
> produced, they are executed by `prolog_engine.py` — a minimal SLD-resolution
> engine (unification, backtracking, definite clauses, `\+`) written for this
> laboratory. Every answer in `prolog_session.txt` is a real answer computed
> from the real `.pl` files.

### Task 6 — `can_move/2`

```prolog
connected(a,b).   connected(b,a).   connected(b,c).   connected(c,b).

can_move(X,Y) :- connected(X,Y).
```

| Query | Answer |
|---|---|
| `?- can_move(a,b).` | `true.` |
| `?- can_move(a,c).` | `false.` |
| `?- can_move(b,X).` | `X = a ;  X = c.` |
| `?- connected(a,c).` | `false.` |

**(a) Why does `can_move(a,b)` succeed?** Two resolution steps. The goal
`can_move(a,b)` unifies with the head of the rule under {X↦a, Y↦b}, leaving the
body `connected(a,b)`, which unifies with a fact. The derivation reaches the
empty goal, so the query succeeds.

**(b) Why does `can_move(a,c)` fail?** There is no fact `connected(a,c)`, and
`can_move/2` has exactly one clause whose body is a single `connected/2` goal —
it is **not recursive and not transitive**. So no derivation of `can_move(a,c)`
exists. Prolog then reports `false`, which under the closed-world assumption
means *"not derivable"*, not *"proved false"*. This is **negation as failure**,
and it is precisely the property that lets the verifier reject an action: an
action the knowledge base cannot justify is treated as forbidden.

**(c) Relation to the implication.** The clause `can_move(X,Y) :- connected(X,Y)`
is the definite clause `Connected(X,Y) → CanMove(X,Y)`, universally quantified —
Prolog writes implications backwards, head-first. Two differences from classical
logic are worth naming:

- Prolog's *completion* semantics reads the set of clauses for `can_move/2` as
  an **if-and-only-if**: `CanMove(X,Y) ↔ Connected(X,Y)`. Classical logic reads
  the single implication only, and would leave `CanMove(a,c)` **unknown**.
- Resolution is a *proof procedure*, not the entailment relation itself. It is
  goal-directed (SLD), depth-first and clause-ordered.

The distinction is not pedantry: it is exactly what makes `false` a usable
verdict for a verifier.

### `can_move` vs. reachability

Added by hand, because it names the very error the Python planner made:

```prolog
reachable(X,Y) :- route(X, Y, [X], _).
route(X, X, V, V).
route(X, Y, V, Out) :- connected(X,Z), \+ member(Z,V), route(Z, Y, [Z|V], Out).
```

| Query | Answer | |
|---|---|---|
| `?- can_move(a,c).` | `false.` | a and c are **not adjacent** |
| `?- reachable(a,c).` | `true.` | but c **is reachable** from a, via b |

*Adjacent* and *reachable* are different questions. Defect 2 is exactly the
error of treating the second as though it were the first.

### Task 7 — checking a proposed action, and a proposed plan

```prolog
valid_move(X,Y) :- connected(X,Y).

valid_route(_, []).
valid_route(X, [move(X,Y)|Rest]) :- connected(X,Y), valid_route(Y, Rest).
```

| Query | Answer |
|---|---|
| `?- valid_move(a,b).` | `true.` |
| `?- valid_move(b,c).` | `true.` |
| `?- valid_move(a,c).` | `false.` ← the handout's Challenge |

`valid_route/2` catches a second class of error the single-action check cannot:
moves that are individually legal but **do not join up**, because the head
`move(X,Y)` shares the variable `X` with the route's current location.

### The loop closed (`run_prolog.py`)

The Python plan is translated into a Prolog goal and checked against knowledge
the planner never saw:

```
the corrected planner
    Python plan            : PickUp(Package,A) -> Move(A,B) -> Move(B,C) -> Drop(Package,C)
    Python self-validation : VALID
    translated Prolog goal : valid_route(a, [move(a,b),move(b,c)]).
    Prolog answer          : true.
    >>> AGREEMENT.

the defective planner (Move over every pair of locations)
    Python plan            : PickUp(Package,A) -> Move(A,C) -> Drop(Package,C)
    Python self-validation : VALID
    translated Prolog goal : valid_route(a, [move(a,c)]).
    Prolog answer          : false.
    >>> DISAGREEMENT.
            valid_move(a,c) -> FALSE  <-- unsupported
```

The second block is the whole laboratory in six lines. Python says the plan is
consistent with its own action model; Prolog says the action model is not
consistent with the warehouse. **The verifier is right.**

The two sides share no code and no data — the connectivity of the warehouse is
written down twice, once in each — and the verifier earns its keep exactly where
the two copies disagree.

### Task 8 — Prolog and logical reasoning

```prolog
wet_road.
slippery     :- wet_road.
reduce_speed :- slippery.

?- reduce_speed.        true.
```

Reading the clauses as implications and reasoning forward:

```
   WetRoad                          (fact)
   WetRoad  → Slippery              (rule)
   ───────────────────── modus ponens
   Slippery
   Slippery → ReduceSpeed           (rule)
   ───────────────────── modus ponens
   ReduceSpeed
```

i.e. **WetRoad ⇒ Slippery ⇒ ReduceSpeed**, in the `Fact ⇒ Rule ⇒ Rule ⇒
Conclusion` form the handout asks for.

Prolog travels the same chain in the **opposite direction**. It starts from the
*goal* `reduce_speed`, replaces it via the third clause with `slippery`,
replaces that via the second with `wet_road`, and finds `wet_road` as a fact,
reaching the empty goal. Forward reasoning proves the conclusion from the facts;
SLD resolution reduces the goal to the facts. Same theorem, opposite direction
of travel.

The same shape, from §7.1 of the handout:
`Penguin(Polly) ⇒ Bird(Polly) ⇒ Animal(Polly)`, and `?- animal(polly).` → `true.`

And the boundary: `?- animal(rex).` → `false.` — not "rex is provably not an
animal" but "rex is not provably an animal". Prolog reports failure to prove as
falsity. Classical logic would say *unknown*.

### Answers to §7.2 Reflection Questions (Prolog as a Logical Verifier)

**1. What is the difference between a Prolog fact and a Prolog rule?**
- A **fact** is an unconditional assertion (a Horn clause with an empty body, e.g., `connected(a, b).` or `wet_road.`), stating directly that a specific relation holds unconditionally in the domain.
- A **rule** is a conditional implication (a Horn clause with a non-empty body, e.g., `can_move(X, Y) :- connected(X, Y).` or `reduce_speed :- slippery.`), stating that the head relationship holds *if* all premises in its body can be established from the knowledge base. In formal notation, a fact is of the form $P$, whereas a rule is $Q_1 \land \dots \land Q_k \to P$.

**2. How does a Prolog query correspond to asking whether something follows from a knowledge base?**
- A query `?- Q.` asks whether the goal $Q$ is a logical consequence of the knowledge base, i.e., whether $KB \models Q$.
- Prolog attempts to prove this by refutation using SLD resolution: it assumes the negation $\neg Q$ and searches backward from goals to subgoals, attempting to derive the empty clause (contradiction). If a derivation succeeds, Prolog answers `true` along with the variable unifiers that satisfy the query. Under Prolog's Closed World Assumption (CWA), if all derivation branches terminate in failure, it returns `false` (negation as failure: not provable from $KB$).

**3. Why might it be useful to use a Prolog program to verify a plan generated by a Python program?**
- It introduces an independent representation and execution mechanism for domain validation.
- In Python, if the domain model is flawed (such as instantiating `Move(A, C)` without respecting physical connectivity), an internal re-execution in Python will simply validate the plan against the same flawed action model.
- A Prolog verifier holds an independent, declarative axiomatization of the environment (e.g., ground topological facts `connected/2`). When the Python planner outputs candidate actions, Prolog checks them against facts the planner cannot mutate. If the planner invents an unsupported shortcut, Prolog fails the query immediately.

**4. What advantage does an independent verifier provide when the original plan was generated with the help of an LLM?**
- An LLM generates candidate outputs through probabilistic token prediction; it produces answers that look plausible and sound convincing, but it does not perform strict logical deduction.
- When asked to justify a flawed plan, an LLM will produce a persuasive explanation that confirms it. In Task 5 every line of its justification of the `Move(A,C)` plan was true relative to the flawed action model — and the plan was still physically impossible, so the explanation was no evidence of validity.
- An independent, deterministic logical verifier (like Prolog) provides rigorous truth-checking: it evaluates the plan against non-negotiable formal axioms without conversational bias, prompt susceptibility, or hallucination. This operationalizes the core AI engineering principle: **Generate (LLM / Heuristic Search) $\to$ Independently Verify (Formal Logic).**

---

## 9. Answers to the reflection questions (§5 of the handout)

**1. Why specify preconditions and effects before asking an LLM to write the
planner?**

Three reasons, all of which this run demonstrates. *First*, the specification
is the only thing the output can be judged against — without it there is no
difference between "the program does what I meant" and "the program does what it
does", and a fluent program that plans in a world you did not describe is
indistinguishable from a correct one. *Second*, writing it down surfaces the
decisions the LLM would otherwise make silently: the subset goal test, the
delete-then-add order and the connectivity restriction were all fixed in Task 0,
and each corresponds to a defect that either did not happen or was a one-line
fix when it did. *Third*, the specification is what lets you notice the LLM
ignoring it — Defect 2 was found by comparing a 3-action plan against a
hand-built 4-action plan, and without Task 1 there would have been nothing to
compare against.

**2. An error that could occur if the planner failed to check preconditions.**

It would accept `Move(A,B)` then `PickUp(Package,B)` — the handout's own
suggested ordering. The robot walks to B, the package stays at A, and the
planner "picks up" a package that is not there. The resulting state contains
`Holding(Package)` **and** `At(Package,A)` simultaneously: the package is in two
places at once. Every subsequent state is nonsense, and the plan will be
delivered with complete confidence, because nothing downstream re-checks it.
More generally, skipping the precondition test deletes the *logic* from
"Logic + Search" and leaves a search over a graph with edges that do not exist.

**3. Why is a plan that "looks reasonable" not necessarily valid?**

Because "reasonable" is a judgement about the *sequence of action names* —
they are the right actions, in a sensible order, ending with the one that
achieves the goal — while validity is a property of the sequence **together
with the states it passes through**. `Move(A,B), PickUp(Package,B), Move(B,C),
Drop(Package,C)` reads perfectly and is invalid at step 2. The only way to tell
is to carry the state along and test each precondition where the action is
actually used. This laboratory produced a sharper version too: the 3-action plan
of §6 was not merely *plausible*, it was **provably valid relative to the action
model** — and still impossible, because the model was wrong.

**4. What did the LLM contribute?**

The engineering. The `Action`/`Problem` class structure; `applicable` and
`apply` as one-line set operations; the BFS driver with its parent map and path
reconstruction; the state-trajectory printer; the `frozenset` fix and its
explanation; the `visited` set once the symptom was described; the first draft
of `planner.pl`. This is real work and it was done quickly and idiomatically.
Notably it also *diagnosed* Defect 1 correctly once told the symptom. What it
did not contribute is anything requiring knowledge of the warehouse that was not
already in the code in front of it.

**5. What did you have to verify independently?**

Everything that matters, and the list is specific:

- that the plan **re-executes** — `validate_plan` walks it from *I* and checks
  each precondition itself, rather than trusting the states the search recorded;
- that the planner **terminates** on an unsolvable problem — Test B, which is
  the only thing that found Defect 1;
- that the plan is **shortest** — checked against an independently written
  exhaustive depth-limited-search oracle (Test I), not against BFS's own claim;
- that the **action model matches the warehouse** — and this could not be done
  in Python at all. It required a second, independent statement of the
  connectivity, in `planner.pl`, and a query engine that had never seen the
  planner.

The last one is the important entry. The first three verify the *program*; only
the fourth verifies the *problem*.

**6. Where is logical reasoning being used?**

In four places, of increasing distance from the code:

- **Applicability**: *S* ⊨ Pre(*a*) — a decidable entailment check, evaluated
  once per action per state — 70 times in solving the warehouse.
- **State update**: *S′* = (*S* − Del) ∪ Add — the effects, as a truth
  assignment update under the closed-world assumption.
- **The goal test**: *S* ⊨ *G* — entailment again, and the reason it is `⊆` and
  not `=`.
- **Verification**: the Prolog program of §8, where logical reasoning is no
  longer a subroutine inside the agent but an **independent judge of the agent's
  output**.

**7. How is planning related to the search algorithms of the previous module?**

Planning *is* graph search — with the graph supplied logically rather than
given. In the search module the successor function was a map: read the grid,
return the neighbouring cells. Here the successor function is
`{Apply(S,a) : a ∈ A, S ⊨ Pre(a)}`, computed on demand by a logical test.
Everything downstream is unchanged: frontier, visited set, parent map, goal
test on pop, and the fact that BFS returns a shortest solution because every
step costs 1. `results.txt` §3 swaps BFS for DFS with no change to the logic and
gets valid plans with no shortest-plan guarantee, exactly as in the previous
module (on these corridors DFS happens to find plans of the same length).

Two differences are worth naming. The state space is **implicit and vast** —
here 12 reachable states, but in general exponential in the number of
propositions — which is why real planners use heuristics derived from the action
descriptions themselves (relaxed-plan heuristics ignore delete lists) rather
than a hand-supplied `h`, as A\* did. And the *shape* of the graph is now
something you can get wrong: a grid map is given to you, whereas an action set
is something you wrote — which is how Defect 2 was possible at all.

---

## 10. Takeaway

```
        Understand  →  Specify  →  Generate  →  Execute  →  Verify
```

Every arrow earned its place in this run:

| Stage | What it caught |
|---|---|
| **Understand** | that the goal is partial, so the goal test is `⊆` |
| **Specify** | Prompt 1 made Defect 0 a one-line fix rather than a puzzle |
| **Generate** | the LLM wrote a correct BFS planner quickly |
| **Execute** | Test B found Defect 1 — a hang, invisible to Test A |
| **Verify** | Prolog found Defect 2 — invisible to *everything* inside Python |

And the one line to keep:

> **A generated explanation is not the same as an independent verification** —
> and an independent execution is only as good as the model it executes. The
> check has to come from outside the thing being checked.
