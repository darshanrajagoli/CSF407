# Appendix — Prompts used with the LLM

Recorded verbatim, in the order they were issued.

---

## Prompt 1 — Task 2: generate the A* agent

> I am implementing a goal-based search agent in Python for a warehouse robot
> navigation problem. I have already formulated the search problem and designed
> the agent; I want you to translate that design into code, not to redesign it.
>
> **Problem.** The warehouse is a grid given as an ASCII map. `#` is an obstacle,
> `.` is a free cell, `S` is the start, `G` is the goal. The robot moves one cell
> at a time — Up, Down, Left or Right — and every move costs 1. Find a path from
> `S` to `G`.
>
> **My design, which the code must follow:**
>
> 1. A state is the robot's position as a tuple `(row, col)`, 0-indexed, row
>    increasing downward. Position alone is a complete state — do not put the path
>    so far, the step count, or the cost into the state.
> 2. The map is a list of strings indexed `grid[row][col]`. Parse it once to find
>    `S` and `G`; leave walls in place as `'#'` rather than building a separate
>    obstacle set. Keep the raw text so the path can be printed over the map.
> 3. A successor is valid only if it is inside the grid **and** not `#`. Check
>    bounds explicitly — do not rely on the map having a wall border, and do not
>    let a negative index wrap around. Use `len(grid[r])` for the row actually
>    being indexed, in case rows are ragged.
> 4. Generate successors in a fixed order: Up, Down, Left, Right. I need runs to
>    be reproducible so that expansion counts can be compared between algorithms.
> 5. Test for the goal **when a node is popped from the frontier**, not when it is
>    generated. I want the optimality guarantee.
> 6. The frontier is a `heapq` min-heap of `(f, tie_break, state)` where
>    `f = g + h`. `tie_break` is a monotonically increasing counter so that ties
>    are FIFO and the heap never compares two state tuples. Keep `best_g`,
>    `parent` and `closed` outside the heap — do not store the path inside
>    frontier entries.
> 7. Avoid re-expanding states: skip stale entries on pop (lazy deletion, since
>    `heapq` has no decrease-key), and push a successor only if it is unseen or
>    strictly cheaper than the best cost recorded for it.
> 8. Reconstruct the path at the end by following `parent` from the goal back to
>    the start and reversing.
>
> **Heuristic.** Manhattan distance, `h(n) = |x − x_G| + |y − y_G|`. Pass it in as
> a function parameter rather than hard-coding it — I need to swap it later for
> `h = 0`, Euclidean distance, and `2 × Manhattan` without touching the search.
>
> **The program must report**, on termination: whether a solution was found; the
> path; the path length defined as the **number of moves** (`len(path) - 1`); the
> number of states expanded; and, additionally, the number of states generated and
> the peak frontier size. Also print the warehouse with the path drawn on it.
>
> If the frontier empties before the goal is reached, report failure explicitly —
> it must not loop forever or crash.
>
> Keep the implementation simple and readable, and explain the main components.
> Where a line implements a specific concept from the formulation (state, action,
> transition, goal test, g, h, f, frontier, visited set, path reconstruction),
> mark it with a comment, because I have to identify those locations afterwards.

**Result:** produced `astar_warehouse.py`. Reviewed and tested in Task 3; the
outcome of that review is recorded in Task 7.

---

## Prompt 2 — Task 3: reviewing a suspicious measurement

> On my open-plan test map, A* with Manhattan distance expands exactly the same
> number of states as BFS: 116 out of 130 free cells, with the same peak frontier
> size. Both return an optimal 25-move path, and my path validator passes. Why
> would an informed search expand exactly as many states as a blind one? Is my
> heuristic being ignored?

**Answer given:** the heuristic is not being ignored — it is being cancelled out
by ties. On a 4-connected grid with unit step costs, every cell on a detour-free
route from `S` to `G` has `g + h = h(s0)` exactly, so `f` is *constant* across the
whole map. I verified this directly: all 116 reachable cells on that map have `f = 25`
(the other 14 free cells are sealed inside the block).
With `f` tied everywhere, the ordering is decided entirely by the tie-break, and a
FIFO tie-break visits nodes in insertion order — which is exactly BFS order.
The fix is to break `f`-ties in favour of the **larger** `g`, i.e. push
`(f, -g, counter, state)`. See Task 7.

---

## Prompt 3 — Task 5: the BFS comparison agent

> Add a breadth-first version of the same agent for comparison. It must reuse the
> identical map parsing, successor generation (same fixed Up/Down/Left/Right
> order), parent table and path reconstruction, so that the only difference
> between the two algorithms is the frontier — a FIFO `deque` with no g, h or f.
> Test for the goal on pop, exactly as A* does, so the two "states expanded"
> figures are measured on the same basis and are genuinely comparable.

---

## Prompt 4 — Task 6: why Manhattan?

> Explain why Manhattan distance is the appropriate heuristic for this warehouse,
> given that the robot can only move horizontally and vertically.

**Answer given:** because it is exactly the cost of the cheapest possible route in
a *relaxed* version of the problem — the same warehouse with all the shelves
removed. With only 4-connected moves at cost 1, closing a vertical gap of `dr`
rows and a horizontal gap of `dc` columns needs at least `dr + dc` moves; no move
reduces both at once, and no diagonal shortcut exists. Adding obstacles back can
only ever make the real path longer, never shorter, so
`h(n) = |dr| + |dc| <= h*(n)` for every `n` — the heuristic is **admissible**, and
A* is therefore guaranteed to return an optimal path. It is also **consistent**:
each move changes `h` by at most 1, which equals the step cost, so
`h(n) <= c(n,n') + h(n')`. Consistency is what lets the closed set be safe without
ever reopening a state.
>
> Note the contrast with Euclidean distance, which is also admissible here but
> strictly weaker: it is the exact cost only if the robot could move in a
> straight line in any direction, which it cannot. Being a looser lower bound, it discriminates less between
> states and therefore expands more of them — which the Task 6 measurements
> confirm (92 expansions against 26 on the open map).
