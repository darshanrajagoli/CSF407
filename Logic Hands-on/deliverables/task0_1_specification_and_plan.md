# Tasks 0 and 1 — Specification of the Planning Problem, and a Plan by Hand

**CS F407 Artificial Intelligence** · Laboratory: Logical Reasoning for Planning

> This document was written **before** any LLM was prompted. The handout is
> explicit about the order: *"Before using an LLM, write down the planning
> problem"* (Task 0) and *"Before writing any program, try to construct a valid
> plan manually"* (Task 1). Task 2's prompt is derived from this document; it
> is not the other way round.

---

## Task 0 — Understand the planning problem

### (a) The initial state *I*

A **state** is the set of propositions that are true of the world at a moment
in time. Anything not listed is false — the *closed-world assumption*.

```
I = { At(Robot, A),  At(Package, A) }
```

Two things are being said here, and one thing is being said by omission:

| Proposition | Status in *I* | Meaning |
|---|---|---|
| `At(Robot, A)` | true | the robot is at A |
| `At(Package, A)` | true | the package is on the floor at A |
| `Holding(Package)` | *absent, so false* | the robot is not carrying anything |
| `At(Robot, B)`, `At(Robot, C)` | absent, so false | the robot is nowhere else |
| `At(Package, B)`, `At(Package, C)` | absent, so false | the package is nowhere else |

### (b) The goal *G*

```
G = { At(Package, C) }
```

*G* is a **partial** description of the world. It constrains the package and
says nothing whatever about the robot: a final state in which the package is at
C and the robot is also at C satisfies *G*, and so would a final state in which
the package is at C and the robot has wandered back to A.

**This has a direct consequence for the program.** The goal test must be

```
    G ⊆ S            "S entails G"
```

and **not** `S == G`. Writing equality would demand that the final state
contain the goal proposition *and nothing else* — which is unachievable, since
the robot is always somewhere. This is recorded here in advance because it is
the single most likely place for generated code to be wrong.

### (c) The actions available to the robot

The warehouse is a corridor:

```
        A -------- B -------- C
```

A and C are **not** directly connected. This fact lives outside the action
descriptions — it is what determines *which* `Move` actions exist at all — and
it is the piece of knowledge that the Prolog verifier in Task 7 holds
independently.

Three action *schemas*, which instantiate to eleven — no, to **ten** — ground
actions:

| Schema | Ground instances | Count |
|---|---|---|
| `Move(x, y)` for **connected** *x*, *y* | `Move(A,B)`, `Move(B,A)`, `Move(B,C)`, `Move(C,B)` | 4 |
| `PickUp(Package, x)` | at A, B, C | 3 |
| `Drop(Package, x)` | at A, B, C | 3 |

**Move is instantiated over the four connected pairs, not over all six ordered
pairs.** `Move(A,C)` and `Move(C,A)` must not exist. Writing this down
explicitly, before generating code, is what later made it possible to *notice*
that the generated version had got it wrong.

### (d) Preconditions and effects

Written in the positive/negative form the program will use. `Pre⁺` must be
present in the state, `Pre⁻` must be absent; `Add` is made true, `Del` is made
false.

#### `Move(x, y)` — for connected *x*, *y*

| | |
|---|---|
| **Pre⁺** | `At(Robot, x)` |
| **Pre⁻** | — |
| **Add** | `At(Robot, y)` |
| **Del** | `At(Robot, x)` |

Note what `Move` does **not** do: it does not touch the package. If the package
is on the floor at A and the robot walks to B, the package stays at A. If the
robot is *holding* the package, the package has no `At(...)` proposition at all,
so there is nothing to update and it travels with the robot automatically.

That is a deliberate modelling decision, and it is why the representation uses
`Holding(Package)` rather than, say, `At(Package, Robot)`: the package's
location is *either* a place *or* the robot's hand, never both, and making
those two cases mutually exclusive propositions removes a whole class of
inconsistent states from the space.

#### `PickUp(Package, x)`

| | |
|---|---|
| **Pre⁺** | `At(Robot, x)`, `At(Package, x)` |
| **Pre⁻** | `Holding(Package)` |
| **Add** | `Holding(Package)` |
| **Del** | `At(Package, x)` |

The negative precondition is an addition to the handout's description. Without
it, the robot can execute `PickUp` twice, which is physically meaningless; the
handout's prompt in Task 2 asks for negative preconditions, so there should be
at least one action that actually has one.

#### `Drop(Package, x)`

| | |
|---|---|
| **Pre⁺** | `At(Robot, x)`, `Holding(Package)` |
| **Pre⁻** | — |
| **Add** | `At(Package, x)` |
| **Del** | `Holding(Package)` |

`PickUp` and `Drop` are exact inverses. `Holding(Package)` and
`At(Package, x)` are never both true, and never both false — this is an
invariant of the domain and a cheap thing to assert in testing.

---

### Which actions are applicable in *I*?

The question the handout asks. The test is *S ⊨ Pre(a)*: **every** positive
precondition present, **every** negative precondition absent.

| Action | Pre⁺ | Present in *I*? | Pre⁻ | Absent from *I*? | Applicable |
|---|---|---|---|---|---|
| `Move(A,B)` | `At(Robot,A)` | yes | — | — | **yes** |
| `Move(B,A)` | `At(Robot,B)` | **no** | — | — | no |
| `Move(B,C)` | `At(Robot,B)` | **no** | — | — | no |
| `Move(C,B)` | `At(Robot,C)` | **no** | — | — | no |
| `PickUp(Package,A)` | `At(Robot,A)`, `At(Package,A)` | both yes | `Holding(Package)` | yes | **yes** |
| `PickUp(Package,B)` | `At(Robot,B)`, `At(Package,B)` | **neither** | `Holding(Package)` | yes | no |
| `PickUp(Package,C)` | `At(Robot,C)`, `At(Package,C)` | **neither** | — | — | no |
| `Drop(Package,A)` | `At(Robot,A)`, `Holding(Package)` | **`Holding` missing** | — | — | no |
| `Drop(Package,B)` | `At(Robot,B)`, `Holding(Package)` | **neither** | — | — | no |
| `Drop(Package,C)` | `At(Robot,C)`, `Holding(Package)` | **neither** | — | — | no |

**Exactly two actions are applicable in *I*: `Move(A,B)` and
`PickUp(Package,A)`.**

### The handout's two specific questions

> **Is `PickUp(Package, A)` applicable in *I*?**

**Yes.** Its preconditions are `At(Robot, A)` and `At(Package, A)`. Both are
members of *I*, so *I* ⊨ Pre(`PickUp(Package,A)`). Its negative precondition
`Holding(Package)` is absent from *I*, and absent means false, so it is
satisfied too.

> **Is `Drop(Package, C)` applicable in *I*?**

**No**, and it fails on *both* of its preconditions:

- `At(Robot, C)` — the robot is at A, and `At(Robot, C)` is not in *I*.
- `Holding(Package)` — the robot is not holding anything; the proposition is
  not in *I*.

Note *why* it is tempting to say yes: `Drop(Package, C)` is the action that
achieves the goal, and it is in the list of available actions. Neither of those
facts is the applicability test. **Being useful and being listed are not being
applicable.** The only question is whether *S* ⊨ Pre(*a*), and here *S* does
not.

### "Think About It" — the logical reading

> *An action should not be considered applicable merely because it appears in
> the list of available actions. Ask: are all of its preconditions satisfied in
> the current state?*

The list of available actions is a description of the *domain* — what kinds of
thing the robot can ever do. Applicability is a property of an action **and a
state together**. The bridge between them is an entailment check:

```
    S ⊨ Preconditions(a)
```

For the propositional STRIPS representation used here, that entailment check is
cheap and decidable — it is a subset test on a set of propositions. That is the
sense in which "logical reasoning" appears in this laboratory: not a theorem
prover, but a small model-checking step performed once per action per state,
several hundred times per search.

---

## Task 1 — Construct a plan by hand

A plan is a sequence *a₁, …, aₙ* with

```
    I --a₁--> S₁ --a₂--> S₂ --> ... --> Sₙ        and       Sₙ ⊨ G.
```

Two conditions, and both matter: every action must be applicable **where it is
used**, and the *final* state must entail the goal.

### First attempt — and why it fails

The handout suggests you "might need to reason about"

```
    Move(A,B),  PickUp(Package,B),  Move(B,C),  Drop(Package,C)
```

That sequence is **not a valid plan**, and working out why is the most useful
thing in Task 1.

| Step | Action | State before | Applicable? |
|---|---|---|---|
| 1 | `Move(A,B)` | `{At(Robot,A), At(Package,A)}` | yes |
| 2 | `PickUp(Package,B)` | `{At(Robot,B), At(Package,A)}` | **no** |

`PickUp(Package,B)` requires `At(Package, B)`. The package is still at **A** —
the robot walked to B *without it*, because `Move` has no effect on the
package's location. The plan reads plausibly, mentions all the right actions in
a sensible-looking order, and is wrong at the second step.

This is precisely the failure mode the laboratory is built around, and it is
worth noticing that it appears *before* any LLM is involved. A sequence of
actions that "looks reasonable" is not a plan; it becomes a plan only when
every precondition is checked against the actual state at that point.

`test_planner.py::test_f_handout_ordering_is_invalid` runs this sequence
through the validator and confirms it is rejected at step 2.

### The correct plan

The fix is to **pick up the package before moving**:

```
    a₁ = PickUp(Package, A)
    a₂ = Move(A, B)
    a₃ = Move(B, C)
    a₄ = Drop(Package, C)
```

### The state after every action

| State | Facts | Justification for the action that produced it |
|---|---|---|
| *S₀* | `At(Robot,A)`, `At(Package,A)` | the given initial state |
| *S₁* | `At(Robot,A)`, `Holding(Package)` | `PickUp(Package,A)`: Pre⁺ `At(Robot,A)` ✓, `At(Package,A)` ✓; Pre⁻ `Holding(Package)` absent ✓. Del `At(Package,A)`, Add `Holding(Package)`. |
| *S₂* | `At(Robot,B)`, `Holding(Package)` | `Move(A,B)`: Pre⁺ `At(Robot,A)` ✓. Del `At(Robot,A)`, Add `At(Robot,B)`. The package rides along — it has no `At` proposition to update. |
| *S₃* | `At(Robot,C)`, `Holding(Package)` | `Move(B,C)`: Pre⁺ `At(Robot,B)` ✓. Del `At(Robot,B)`, Add `At(Robot,C)`. |
| *S₄* | `At(Robot,C)`, `At(Package,C)` | `Drop(Package,C)`: Pre⁺ `At(Robot,C)` ✓, `Holding(Package)` ✓. Del `Holding(Package)`, Add `At(Package,C)`. |

*S₄* ⊇ *G* = `{At(Package,C)}`, so *S₄* ⊨ *G*. **The plan is valid.**

Observe that *S₄* ≠ *G*: the final state also contains `At(Robot, C)`. The
equality goal test predicted in Task 0(b) would reject this correct plan.

### Is four actions optimal?

Yes, and it is worth being able to say why without running anything:

- One `PickUp` and one `Drop` are unavoidable — `At(Package,C)` is added by
  `Drop` alone, and `Drop` requires `Holding(Package)`, which is added by
  `PickUp` alone. That is 2 actions minimum.
- The robot must be at C when it drops, and it starts at A. Since A and C are
  not connected, no single `Move` gets it there; the shortest route is
  A→B→C, so 2 `Move`s minimum.
- 2 + 2 = 4, and the plan above achieves 4.

So the plan is optimal, which is what BFS should return.
`experiments.py` confirms this by exhaustive search, and
`test_planner.py::test_i_optimality` asserts it against an independently
written iterative-deepening oracle.

---

## The design of the agent, fixed before prompting

These decisions were made here, not by the LLM. They became the specification
in `prompts.md`, Prompt 1.

| Decision | Choice | Reason |
|---|---|---|
| **Proposition** | a string, `"At(Robot,A)"` | no term structure is needed; the domain is propositional once actions are ground |
| **State** | `frozenset` of true propositions | closed-world assumption; **frozen** because states must be hashable to serve as dictionary keys and set members for duplicate detection |
| **Action** | five fields: name, Pre⁺, Pre⁻, Add, Del | matches the specification exactly, so a reviewer can read the code against this table |
| **Applicability** | `Pre⁺ ⊆ S and Pre⁻ ∩ S = ∅` | the entailment check, in one line |
| **Effects** | `(S − Del) ∪ Add` | **delete first, then add**, so a proposition in both lists survives. Fixed in advance so the generated code could not choose for itself |
| **Goal test** | `G ⊆ S` | entailment, not equality — see Task 0(b) |
| **Goal test timing** | on **pop**, not on generation | makes `states expanded` mean the same thing for BFS and any other strategy compared later |
| **Search** | BFS with a `visited` set | BFS returns a shortest plan because every action costs 1. The `visited` set is **required for termination**, not an optimisation: `Move(A,B)`/`Move(B,A)` is a cycle, so without it an unsolvable problem never reports failure |
| **Ground actions** | `Move` over **connected pairs only** | the connectivity of the warehouse is domain knowledge and must be applied at instantiation time |
| **Plan length** | number of actions | fixed in advance so two algorithms cannot disagree by one |
| **Validation** | a separate `validate_plan` that re-executes the plan from *I* | the search must not be allowed to grade its own work |

### Three things to be able to defend

1. **The goal is entailed, not equalled.** `G ⊆ S`. The goal is a partial
   description of the world.
2. **`Move` does not move the package** — unless the package is held, in which
   case it has no location proposition at all. That is what makes the
   handout's suggested action ordering invalid.
3. **Duplicate detection is a correctness requirement, not a speed
   optimisation.** Without it the planner does not terminate on an unsolvable
   problem, which is exactly what Test B asks it to handle.
