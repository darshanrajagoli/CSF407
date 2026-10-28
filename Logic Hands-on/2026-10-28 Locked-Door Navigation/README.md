# Locked-Door Navigation (lab of 28 Oct 2026)

Section 4 of a revised logic-lab handout, shown in class (the PDF has not been
shared yet). Code: `locked_door.py`.

```bash
python locked_door.py      # plan + failing conditions -> "All checks passed."
```

---

## The question

*Transcribed from the projected slide.*

> **4 Second Planning Domain: A Locked-Door Navigation Problem**
>
> The warehouse example combines movement with transporting an object. In this
> second domain, the agent must obtain a resource before it can access a
> location. Use the same state-transition and BFS machinery; change only the
> problem description.
>
> There are three rooms *A, B, C*. The passages *A ↔ B* and *B ↔ C* are the
> only passages. The passage between *B* and *C* is initially locked. The robot
> starts in *A*; a key is in *A*. The goal is to reach *C*. The robot may carry
> the key, and unlocking the door permanently opens it. There is no action to
> drop the key or relock the door.
>
> Represent states using the propositions
> `At(A), At(B), At(C), KeyAt(A), HasKey, Unlocked`.
>
> Exactly one `At(·)` proposition is true in a reachable state. The initial
> state and goal are
> **I** = `{At(A), KeyAt(A)}`, **G** = `{At(C)}`.
>
> | Action | Preconditions | Effects |
> |---|---|---|
> | `Move(A,B)` | `At(A)` | delete `At(A)`; add `At(B)` |
> | `Move(B,A)` | `At(B)` | delete `At(B)`; add `At(A)` |
> | `PickKey` | `At(A)`, `KeyAt(A)` | delete `KeyAt(A)`; add `HasKey` |
> | `Unlock` | `At(B)`, `HasKey` | add `Unlocked` |
> | `Move(B,C)` | `At(B)`, `Unlocked` | delete `At(B)`; add `At(C)` |
> | `Move(C,B)` | `At(C)`, `Unlocked` | delete `At(C)`; add `At(B)` |

**Failing condition (given in class):** if the robot does not pick up the key
and goes A → B → C, the plan must fail. Without the key the door cannot be
unlocked, and `Move(B,C)` needs `Unlocked`.

---

## Solution

**Applicable in I:** `Move(A,B)` and `PickKey` only. `Unlock` needs `At(B)` and
`HasKey`; `Move(B,C)` needs `At(B)` and `Unlocked`.

### The plan

| State | True facts | After |
|---|---|---|
| S0 | `At(A)`, `KeyAt(A)` | start |
| S1 | `At(A)`, `HasKey` | `PickKey` |
| S2 | `At(B)`, `HasKey` | `Move(A,B)` |
| S3 | `At(B)`, `HasKey`, `Unlocked` | `Unlock` |
| S4 | `At(C)`, `HasKey`, `Unlocked` | `Move(B,C)` |

S4 contains `At(C)`, so S4 ⊨ G. The plan is valid.

**Four is the minimum.** The only way into C is `Move(B,C)`, which needs
`Unlocked`. Only `Unlock` adds it, and it needs `HasKey`. Only `PickKey` adds
that, and it happens in A. Getting from A to B takes one `Move`. That makes
four actions, and BFS finds exactly these four.

S4 ≠ G, because the robot also still holds the key and the door is open. That
is why the goal test is G ⊆ S, not S = G.

### The failing condition: no key, A → B → C

| State | True facts | After |
|---|---|---|
| S0 | `At(A)`, `KeyAt(A)` | start |
| S1 | `At(B)`, `KeyAt(A)` | `Move(A,B)` |
| — | `Move(B,C)` **fails: `Unlocked` is false** | |

The key is still in A, so `Unlock` cannot run either. There is no way through
the door without going back for the key.

### Every action in the plan is needed

Leaving out any one of the four actions breaks the plan:

| Left out | Fails at | Because |
|---|---|---|
| `PickKey` | `Unlock` | `HasKey` is false |
| `Move(A,B)` | `Unlock` | `At(B)` is false |
| `Unlock` | `Move(B,C)` | `Unlocked` is false |
| `Move(B,C)` | end of plan | robot is still in B, goal not reached |

Removing `PickKey` or `Unlock` from the problem altogether makes it unsolvable,
and BFS reports **No plan found** instead of inventing a way through.
