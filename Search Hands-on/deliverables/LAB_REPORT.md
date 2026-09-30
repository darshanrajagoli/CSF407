# Laboratory Report — Search and A\*

**CS F407 Artificial Intelligence** · Warehouse Robot Navigation
Using an LLM as an engineering assistant

**Files accompanying this report**

| File | Contents |
|---|---|
| `task0_1_formulation_and_design.md` | Tasks 0 and 1 — problem formulation and agent design, written *before* any LLM prompt |
| `astar_warehouse.py` | The final program: A\*, BFS, the four heuristics, reporting |
| `test_search.py` | Task 3 test suite (20 checks) |
| `experiments.py` | Tasks 5 and 6 measurements |
| `prompts.md` | Appendix: every prompt issued to the LLM |
| `results.txt`, `test_results.txt` | Raw output, reproducing the tables below |
| `warehouse.txt` | The supplied map as plain text |

Reproduce everything with:

```
python astar_warehouse.py     # solve the warehouse
python test_search.py         # Task 3
python experiments.py         # Tasks 5 and 6
```

---

## 1. Formulation of the search problem (Task 0)

Full version in `task0_1_formulation_and_design.md`. In summary:

| Component | Specification |
|---|---|
| **S** | Robot position `(r, c)` with `grid[r][c] != '#'`. 64 such cells on this map. Position alone is a complete state. |
| **A** | `{Up, Down, Left, Right}` = `{(-1,0), (1,0), (0,-1), (0,1)}` |
| **T** | `T((r,c),(dr,dc)) = (r+dr, c+dc)` if in bounds and not `#`; otherwise inapplicable |
| **s₀** | `(1, 1)` |
| **G** | `{(7, 15)}` |
| **c** | 1 per move |

The key modelling decision is what is *excluded* from the state: the route so
far, the step count and the accumulated cost are **history**, and belong to the
search node, not the state. Two robots reaching the same cell by different routes
face an identical remaining problem, which is exactly the property that makes
duplicate detection sound.

Since `h(s₀) = |1−7| + |1−15| = 20`, no solution can be shorter than 20 moves —
a free sanity check used in testing.

---

## 2. Design of the agent (Task 1)

Full version in `task0_1_formulation_and_design.md`. The decisions that mattered:

- **State** = a `(row, col)` tuple — hashable, so usable directly as a `dict` key
  and `set` member; immutable, so it cannot be mutated after being stored.
- **Map** = list of strings, walls left in place as `'#'` so the obstacle test is
  an O(1) lookup with no separate obstacle set to fall out of sync.
- **Successors** generated in a fixed order (Up, Down, Left, Right) so runs are
  reproducible and expansion counts are comparable between algorithms.
- **Goal test on pop, not on generation** — this is what makes A\* optimal.
  Applied to BFS as well, so both "states expanded" figures are measured on the
  same basis.
- **Frontier** = `heapq` min-heap of `(f, tie, state)`, with `best_g`, `parent`
  and `closed` held outside the heap. *(This is the design as written before
  prompting. The tuple gained a `−g` tie-break during Task 7 — see §8, item 2;
  leaving the tie-break underspecified here is precisely what caused the defect.)* Storing the whole path inside each frontier
  entry was considered and rejected: it costs memory proportional to path length
  for every node in the frontier.
- **Duplicate handling** = lazy deletion (skip stale entries on pop, since
  `heapq` has no decrease-key) plus a `ng < best_g[state]` test before pushing.
- **Heuristic passed in as a parameter**, so Task 6 needs no edit to the search.
- **`path_length` defined as the number of moves** (`len(path) − 1`), fixed in
  advance so BFS and A\* could not disagree by one.

---

## 3. The final program (Task 2)

`astar_warehouse.py`. The prompt used to generate it is Prompt 1 in `prompts.md`
— it encodes the design above rather than asking the LLM to invent one.

Result on the supplied warehouse:

```
start s0 = (1, 1)    goal G = (7, 15)
h(s0)    = 20  (lower bound on the solution cost)

solution found   : True
path length      : 40 moves
states expanded  : 64
states generated : 64
peak frontier    : 3

#################
#S****#*********#
#.###*#*#######*#
#...#*#*******#*#
###.#*#######*#*#
#...#*********#*#
#.###########.#*#
#.............#G#
#################
```

The route is forced: 4 moves right, 4 down, 8 right, 2 up, 6 left, 2 up, 8 right,
6 down = **40 moves**.

---

## 4. Test results (Task 3)

All six tests pass — 20 individual checks. Every successful result is additionally
put through `validate_path`, which re-walks the returned path and confirms it
starts at `S`, ends at `G`, is 4-adjacent at every step, never crosses an
obstacle, never revisits a cell, and has the length the program reported. A path
of the right *length* is not enough; it must be a real path.

| Test | Map | Expected | Found | Length | Expanded | Result |
|---|---|---|---|---|---|---|
| 1 | Supplied warehouse | solution, 40 moves | yes | 40 | 64 | pass |
| 2 | Goal adjacent to start | solution, 1 move | yes | 1 | 2 | pass |
| 3 | Goal sealed off | **failure** | no | — | 9 | pass |
| 4 | Two routes (6 vs 10) | the 6-move route | yes | 6 | 7 | pass |
| 5 | No wall border | solution, 2 moves | yes | 2 | 3 | pass |
| 6 | Ragged rows | solution, 2 moves | yes | 2 | 3 | pass |

Tests 5 and 6 are additions of my own. They exist because the design made two
specific claims — that bounds are tested explicitly rather than relying on the
map's wall border, and that ragged rows are handled — and an untested claim is
just an intention. Test 3 confirms the program reports failure and terminates
rather than looping; it expanded only the 9 reachable cells.

Test 1's expansion count is the first sign of something interesting: **64 of 64
free cells**, with a peak frontier of 3. The heuristic saved nothing at all.

---

## 5. Where each concept appears in the code (Task 4)

Line numbers refer to `astar_warehouse.py`, where each is marked with a
`[CONCEPT]` comment.

| Concept | Where it appears |
|---|---|
| **State** | line 21 — `State = tuple[int, int]`; the robot's `(row, col)` |
| **Action** | lines 25–30 — `MOVES`, the four `(name, dr, dc)` offsets in fixed order |
| **Transition** | lines 86–92 — `Warehouse.successors()`, applying each offset and keeping the legal results; validity tested by `is_free()` at lines 73–84 |
| **Goal test** | line 223 — `if state == goal:` inside the pop loop, *after* the node is removed from the frontier |
| **g(n)** | line 202 — `best_g`, cheapest known cost from the start; updated at line 232 as `ng = g + STEP_COST` |
| **h(n)** | lines 100–117 — the four heuristic functions, passed in as the `h` parameter |
| **f(n)** | line 236 — `f = ng + h(nxt, goal)` |
| **Frontier** | lines 197–200 — `heapq` min-heap of `(f, −g, tie, state)`; the BFS `deque` is at line 259 |
| **Visited states** | line 204 — `closed`, checked on pop (line 216) and before generating a successor (line 230) |
| **Path reconstruction** | lines 143–155 — `reconstruct()`, walking `parent` back from the goal and reversing |
| **Initial state s₀ / Goal G** | lines 44–45, set during parsing |
| **Cost c** | line 32 — `STEP_COST = 1` |

**(a) What data structure is used for the A\* frontier?** A binary min-heap
(`heapq`), holding tuples `(f, −g, tie, state)`. The negated `g` and the counter
are tie-breaks, not part of the evaluation function.

**(b) How does the program select the next state to expand?** `heapq.heappop`
removes the entry with the smallest `f`. Ties on `f` go to the *largest* `g`
(hence `−g`), and remaining ties are FIFO via the counter. The counter also
guarantees the heap never has to compare two `state` tuples, which would impose an
arbitrary geographical ordering.

**(c) Where is the heuristic calculated?** In the heuristic functions at lines
100–117, called at line 236 when a successor is pushed and once at line 199 for
the start state — so `h` is evaluated once per push, not repeatedly.

**(d) Does the program explicitly calculate f = g + h?** Yes, at line 236:
`f = ng + h(nxt, goal)`, where `ng` is `g(n)`.

**(e) How does the program prevent unnecessary repeated exploration?** Three
mechanisms. A state already in `closed` is skipped when popped (line 216) —
lazy deletion of entries made stale by a later, cheaper push, needed because
`heapq` has no decrease-key. A successor already in `closed` is not regenerated
(line 230). And a successor is pushed only if it is unseen or strictly cheaper
than its recorded `best_g` (line 233). Together these guarantee each state is
expanded at most once, which is also what makes termination on an unsolvable map
provable: `closed` only grows, and the grid is finite.

---

## 6. BFS compared with A\* (Task 5)

The warehouse is unchanged. An open-plan map is measured alongside it as a
control, because the warehouse turned out to be a degenerate case.

**Supplied warehouse** (64 free cells, h(s₀) = 20)

| Measure | BFS | A\* |
|---|---|---|
| Solution found | yes | yes |
| Path length | 40 | 40 |
| States expanded | 64 | 64 |
| Peak frontier | 3 | 3 |

**Open-plan control map** (130 free cells, h(s₀) = 25)

| Measure | BFS | A\* (FIFO ties) | A\* (prefer deeper) |
|---|---|---|---|
| Solution found | yes | yes | yes |
| Path length | 25 | 25 | 25 |
| States expanded | 116 | 116 | **26** |
| Peak frontier | 8 | 8 | 24 |

**(a) Did both algorithms find a solution?** Yes, on every map.

**(b) Did they find paths of the same length?** Yes — 40 on the warehouse, 25 on
the control. Expected: Manhattan distance is admissible on a 4-connected
unit-cost grid, so A\* is guaranteed optimal, and BFS is optimal because every
step costs the same.

**(c) Which expanded fewer states?** On the warehouse, **neither** — both expanded
all 64 free cells. On the control map A\* expanded 26 against BFS's 116, a 78%
reduction: BFS reached 89% of the map, A\* only 20%.

**(d) Why might A\* expand fewer states?** BFS uses only `g`, so it grows a
uniform ring outward from the start and reaches cells in every direction at the
same rate, including directly away from the goal. A\* orders by `f = g + h`, so a
cell that is equally far from the start but further from the goal has a higher
`f` and waits. The heuristic supplies information about the *remaining* problem,
which `g` alone cannot.

**Why the warehouse shows no benefit.** The supplied map is almost entirely
single-width corridor. A peak frontier of 3 means the search essentially never
had a choice to make. Where there are no alternatives to rank, a heuristic that
ranks alternatives cannot help. Both algorithms must traverse both branches of
the maze, so both expand all 64 cells. **A\* is not faster because it is "more
intelligent" — it is faster only when the map offers choices and the heuristic
can discriminate between them.** The warehouse offers almost none.

---

## 7. Investigating the heuristic (Task 6)

Why Manhattan is appropriate: it is the exact cost of the cheapest route in the
*relaxed* problem — the same warehouse with the shelves removed. With only
4-connected unit-cost moves, closing a gap of `dr` rows and `dc` columns needs at
least `dr + dc` moves, since no move reduces both and no diagonal exists. Putting
the obstacles back can only lengthen the real path, so `h(n) ≤ h*(n)` always:
the heuristic is **admissible**, and A\* is therefore optimal. It is also
**consistent** — each move changes `h` by at most 1, which equals the step cost —
and consistency is what makes the closed set safe without ever reopening a state.

**Supplied warehouse** (64 free cells)

| Heuristic | Found | Length | Expanded | Optimal? |
|---|---|---|---|---|
| h = 0 | yes | 40 | 64 | yes |
| Manhattan | yes | 40 | 64 | yes |
| Euclidean | yes | 40 | 64 | yes |
| 2 × Manhattan | yes | 40 | 64 | yes |

**Open-plan control map** (130 free cells)

| Heuristic | Found | Length | Expanded | Optimal? |
|---|---|---|---|---|
| h = 0 | yes | 25 | 116 | yes |
| Manhattan | yes | 25 | **26** | yes |
| Euclidean | yes | 25 | 92 | yes |
| 2 × Manhattan | yes | 25 | 26 | yes |

**Cluttered room** (143 free cells) — a map found by randomised search
specifically to test whether inadmissibility can actually break optimality

| Heuristic | Found | Length | Expanded | Optimal? |
|---|---|---|---|---|
| h = 0 | yes | 28 | 142 | yes |
| Manhattan | yes | 28 | 133 | yes |
| Euclidean | yes | 28 | 137 | yes |
| 2 × Manhattan | yes | **30** | **31** | **no, +2 moves** |

**1. What happens with h = 0?** A\* degenerates to uniform-cost search. With unit
costs that is BFS by another name: it still returns an optimal path, but expands
the most states of any variant (116 and 142 on the two larger maps). `f = g`
carries no information about where the goal is.

**2. What happens with Euclidean distance?** Still admissible — it can never
exceed Manhattan when diagonal movement is unavailable — so the path stays
optimal. But it is a *weaker* lower bound, so it discriminates less between
states and expands substantially more of them: 92 against Manhattan's 26 on the
control map. Being admissible is necessary for the guarantee; being *close* to
`h*` is what makes the search efficient. The two are separate properties.

**3. What happens with 2 × Manhattan?** This is the interesting one, and the
answer is not the same on every map. On the warehouse and the open control map it
returned an optimal path anyway — inadmissibility **removes the guarantee, it does
not force a violation**. So I searched randomly over maps for a case where it
actually breaks, and found one: on the cluttered room it expanded **31 states
instead of 133 — a 77% saving — but returned a 30-move path where the optimum is
28.**

To check that this map was not a freak, I ran the same comparison over 2,754
randomly generated solvable maps: `2 x Manhattan` returned a **suboptimal path on
25.9% of them**, with a worst case of 8 moves longer than optimal. So it is not a
rare pathology — roughly one map in four punishes the inflated heuristic, and the
supplied warehouse simply happens not to be one of them.

That single row is the whole lesson of the task. Doubling the heuristic makes A\*
strongly goal-directed and very fast, and it buys that speed by overestimating
the remaining cost. Because `h` can now exceed `h*`, A\* may pop the goal while a
cheaper route is still sitting in the frontier with a wrongly inflated `f`, and
it stops there. Both runs return a plausible-looking path over the same map; only
comparing them against a known-optimal baseline reveals that one is worse. **An
answer that looks correct is not evidence that it is.**

---

## 8. Evaluating the LLM-generated agent (Task 7)

**1. What was correct immediately?** The overall skeleton, and more of it than I
expected: the heap-based frontier, the `(f, tie_break, state)` tuple with a
counter to stop the heap comparing state tuples, lazy deletion of stale entries,
the `best_g` relaxation test, `parent`-dictionary path reconstruction, explicit
failure when the frontier empties, and correct handling of both the trivial and
the unsolvable map. All 20 tests passed on the first run.

**2. Did I find any bugs or design problems?** Yes — one significant, and it
passed every test. **A\* with a FIFO tie-break expanded exactly as many states as
BFS: 116 of 130.** On a 4-connected unit-cost grid, every cell on a detour-free
route satisfies `g + h = h(s₀)`, so `f` is *constant*; I confirmed that all 116
reachable cells on the control map have `f = 25`. When everything ties on `f`, the
ordering is decided entirely by the tie-break, and FIFO order is precisely BFS
order. The heuristic was computed correctly and then thrown away.

This is a genuine design defect, not a cosmetic one: the entire point of Task 5
is to show A\* expanding fewer states, and the program would have shown a saving
of exactly zero while returning perfectly correct answers.

**3. How did I discover it?** Not from a failing test — every test passed. I
found it because the *measurement was implausible*: an informed search cannot
coincidentally expand exactly as many states as a blind one, with an identical
peak frontier, unless it is doing the same thing. My Task 1 design had actually
flagged tie-breaking as a decision to be made and then quietly settled for plain
FIFO, so the flaw was mine as much as the LLM's — it implemented what I specified.
The instrumentation I had designed for a different purpose (`nodes_generated`,
`max_frontier`) is what made the anomaly visible.

**4. Terminology or structures I did not understand at first?** Lazy deletion —
why stale heap entries are left in place and filtered on pop, instead of being
removed. The reason is that `heapq` has no decrease-key operation, so pushing a
duplicate and ignoring the obsolete one later is cheaper than finding and
repairing the existing entry. It also explains why *generated* exceeds
*expanded*, which I would otherwise have read as a bug.

**5. Did I modify the code?** Yes:
- Added the `tie_break` parameter and made `"deep"` (prefer larger `g`) the
  default — the fix for the defect above. Effect: 116 → **26** expansions on the
  control map, with the path length unchanged at 25. I kept `"fifo"` selectable
  so Task 5 can *measure* the effect rather than merely assert it.
- Added `nodes_generated` and `max_frontier` to the reported statistics.
- Added `validate_path` to the test suite, so a returned path is re-walked and
  verified rather than trusted.
- Added tests 5 and 6 (no wall border, ragged rows) to test claims my design made
  but nothing exercised.

**6. Which tests were most useful?** Test 4 (alternative paths), because it is the
only one where a wrong answer is still a *valid* path — every other test can be
passed by accident, but returning the 10-move detour instead of the 6-move route
cannot. And more useful than any single test: recording the expected numbers
*before* running, which is what turned "116 expansions" from a result into a
question.

Beyond the six fixed tests, I also fuzzed the final program against an
independently written BFS oracle over 6,000 random maps (3,372 solvable, 2,628
unsolvable) — 36,000 A* runs across three admissible heuristics and both
tie-break rules. Every run agreed with the oracle on path length, returned a
legal contiguous path, and correctly reported failure where no path existed:
zero disagreements. A fixed test suite shows the cases you thought of; the fuzz
run covers the ones you did not.

**7. Could I have trusted the program without testing it?** No — and this case is
worse than a program that visibly fails. It produced correct, optimal, valid paths
on every map while its central mechanism was inert. No amount of looking at the
output would have revealed it; only a measurement compared against an expectation
did.

**8. What do I understand about A\* now that I did not before?** That
`f = g + h` is only half of the algorithm. The frontier's ordering *policy* — how
it breaks ties, when it tests for the goal, whether it reopens closed states — is
as consequential as the heuristic, and it is invisible in the textbook formula.
I also understand that admissibility and informativeness are separate properties:
`h = 0` and Euclidean and Manhattan are all admissible and all return optimal
paths, but they expand 116, 92 and 26 states respectively. Admissibility buys the
guarantee; closeness to `h*` buys the speed.

**Summary of responsibility**

| | |
|---|---|
| **What I designed** | The formulation; state representation; goal-test-on-pop; frontier contents; lazy deletion; parent-dictionary reconstruction; heuristic as a parameter; the reporting fields; `path_length` as moves |
| **What the LLM suggested** | The concrete Python realisation — heap mechanics, the counter trick, the relaxation test, code structure and comments |
| **What I accepted** | Essentially all of the structure; it matched the design and passed every test |
| **What I changed** | The tie-break rule (the real fix); extra statistics; `validate_path`; two extra tests |
| **What I tested** | Six maps, 20 checks, plus a randomised search over maps to find a case where the inadmissible heuristic actually returns a suboptimal path |

---

## 9. Final Reflection

**1. Why formulate the search problem before writing the algorithm?**
Because the formulation is what determines whether the algorithm can be correct at
all, and it is not recoverable from the code afterwards. Deciding that the state
is *position alone* — and that the route so far is history, not state — is what
makes duplicate detection sound; had I folded the path into the state, every cell
would have looked new on each visit and the search would have degenerated into
enumerating routes. Equally, fixing `path_length` as the number of moves before
writing anything removed an off-by-one that would otherwise have appeared exactly
when BFS and A\* were compared. The formulation is also what let me *test*: I knew
`h(s₀) = 20` was a lower bound and that the forced route was 40 moves before the
program ran, so I had expectations to check against rather than output to admire.
Without a specification, you cannot distinguish a correct program from a plausible
one — you can only observe that it did something.

**2. In what sense is A\* "informed"?**
BFS and uniform-cost search use only `g`, information about the part of the
problem already solved; they cannot distinguish a cell one step from the goal from
one heading into a dead end at the same depth. A\* adds `h`, an estimate of the
cost *remaining*, and orders the frontier by `f = g + h` — the estimated cost of
the best complete solution through each node. That is the entire content of the
word "informed": knowledge about the unexplored part of the problem, obtained
here by solving a relaxed version of it (the warehouse with the shelves removed).
My measurements show what it is worth: on the open map, 26 expansions against 116,
reaching 20% of the map instead of 89%. They also show what it is *not* worth on
the supplied warehouse, where corridors leave no choices to inform and both
algorithms expand all 64 cells. Being informed helps only where there is a
decision to make.

**3. Why does the choice of heuristic matter?**
It controls two different things, and they trade against each other. Admissibility
(`h ≤ h*`) controls **correctness**: keep it and A\* is guaranteed optimal; lose it
and the guarantee goes, as the cluttered-room map showed when 2 × Manhattan
returned 30 moves against an optimum of 28. Closeness to `h*` controls
**efficiency**: `h = 0`, Euclidean and Manhattan are all admissible and all
returned optimal paths, yet expanded 116, 92 and 26 states — a factor of four and
a half between the extremes, purely from how sharply each estimate discriminates.
The tempting reading of `2 × Manhattan` expanding 31 states instead of 133 is that
inflation is simply better; the path length column is what corrects that. A
heuristic is a claim about the remaining cost, and the strength of the claim and
its truth are separate questions.

**4. What did the LLM contribute?**
It was genuinely useful as a translator: given a specification I had already
written, it produced idiomatic, correct, well-structured Python quickly, including
mechanics I would have had to look up — the counter that stops `heapq` comparing
state tuples, the lazy-deletion pattern that works around the absence of
decrease-key. All 20 tests passed on the first run. What it did not do was
question the specification. My design left the tie-break rule underspecified, so
it implemented plain FIFO and silently produced an A\* that behaved exactly like
BFS. It also explained the code back to me accurately when asked, and correctly
diagnosed the tie-break problem once I brought it the anomalous measurement — but
it never volunteered it. It was a good engineer working to my drawings, including
where my drawings were wrong.

**5. What could go wrong if an engineer simply accepted LLM-generated code?**
This laboratory produced the exact failure worth worrying about, and it is not the
one people expect. The code did not crash, throw, or return a wrong path. It
returned optimal, valid, correct paths on every map I gave it while its defining
mechanism was inert — an A\* that was really BFS with extra arithmetic. No amount
of reading the output would have exposed that; the tests all passed; a demo would
have looked perfect. It surfaced only because I had a prior expectation about a
number and noticed the number was implausible. Accept generated code on the basis
that its output looks right and you inherit defects that are invisible precisely
where the code is most sophisticated — and you will find them, if at all, only
when the system is scaled up, or handed a map that punishes the shortcut. The
engineer's job is not to obtain a program that runs, but to know why it is
correct, and that requires a specification to test against and expectations
recorded in advance.

---

### AI Science → AI Engineering

Search is the scientific idea; A\* is one algorithm implementing it; the LLM is a
tool that helped implement the algorithm. What this laboratory showed is that the
tool is reliable exactly up to the boundary of the specification it is given, and
silent beyond it. Responsibility for understanding, testing and validating the
result stays with the engineer.
