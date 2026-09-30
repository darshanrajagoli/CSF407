# Laboratory: Search and A* — Tasks 0 & 1

**Course:** CS F407 Artificial Intelligence
**Scenario:** Warehouse Robot Navigation

> Written before any code was generated and before any LLM was prompted for an
> implementation. The only computation performed at this stage was measuring the
> supplied map (size, free-cell count, position of `S` and `G`).

---

## The warehouse map

```
#################
#S....#.........#
#.###.#.#######.#
#...#.#.......#.#
###.#.#######.#.#
#...#.........#.#
#.###########.#.#
#.............#G#
#################
```

9 rows × 17 columns, fully enclosed by a wall border.
64 non-wall cells. `S` = (row 1, col 1), `G` = (row 7, col 15).
Manhattan distance from start to goal = |1−7| + |1−15| = **20**, so no solution
can be shorter than 20 moves.

---

# Task 0 — Understand the Search Problem

## Formulation as P = (S, A, T, s₀, G, c)

| Component | Specification |
|---|---|
| **State S** | The set of grid cells the robot may occupy. A state is an ordered pair `(r, c)` with `0 ≤ r < 9`, `0 ≤ c < 17`, and `grid[r][c] != '#'`. Position alone is a complete state — the warehouse is static and the robot has no load, orientation, or battery. For this map, size of S = 64. |
| **Actions A** | `A = {Up, Down, Left, Right}`, represented as row/column offsets `Up=(-1,0)`, `Down=(+1,0)`, `Left=(0,-1)`, `Right=(0,+1)`. The same four actions are nominally available everywhere; whether each is *applicable* depends on the state. |
| **Transition T** | `T((r,c), (dr,dc)) = (r+dr, c+dc)` **if** the target is inside the grid and is not `#`; otherwise the action is not applicable in that state and generates no successor. Every applicable (state, action) pair yields exactly one successor. |
| **Initial state s₀** | `(1, 1)` — the cell marked `S`. |
| **Goal G** | `G = {(7, 15)}`, the single cell marked `G`. Goal test: `state == (7, 15)`. |
| **Cost c** | `c(s, a, s') = 1` for every applicable action. The cost of a path is therefore its number of moves, and "cheapest path" = "fewest moves". |

## (a) What information is necessary to specify a state?

Only the robot's coordinates `(row, col)`. Nothing else in the world changes: the
shelves are fixed, the robot carries nothing, and moving does not alter the
environment. So the pair `(r, c)` fully determines what the robot can do next and
what it costs.

It is worth being explicit about what must *not* go into the state. The route
taken so far, the number of steps used, and the accumulated cost are all
**history**, not state. Two robots that arrive at the same cell by different
routes face an identical remaining problem, and folding history into the state
would make them look like different states — destroying exactly the property that
lets the search discard duplicates. That distinction matters for the
implementation: `g(n)`, the parent pointer, and `f(n)` belong to the **search
node**, whereas the **state** is just the cell.

## (b) What makes an action invalid?

An action is inapplicable when its target cell either

1. falls outside the grid (`r` or `c` out of range), or
2. contains an obstacle (`#`).

On this particular map the border is a solid ring of `#`, so condition 2 already
guarantees condition 1 can never be triggered from a legal state. The
implementation should still test both, because the smaller test maps written for
Task 3 need not have a closed border, and an unchecked negative index in Python
silently wraps around to the far end of the row rather than raising an error.

There is no third category: an invalid action does not "fail" or waste a step —
it is simply never generated as a successor, so the robot cannot attempt it.

## (c) Is this a deterministic search problem?

Yes. `T` is a function: each applicable (state, action) pair has exactly one
successor, known in advance. The environment is additionally fully observable
(the whole map is given up front), static (nothing changes while the robot
deliberates), and discrete (finitely many cells, four actions).

The practical consequence is that the entire route can be planned **offline**,
before the robot moves at all. A solution can therefore be a fixed sequence of
actions; no policy, no contingency branching, and no re-planning during execution
is required. If movement could slip, or if shelves could be moved by other
robots, a plain action sequence would no longer be sufficient.

## (d) What would constitute a solution?

A finite sequence of actions ⟨a₁, …, a_k⟩ such that each `aᵢ` is applicable in the
state reached by its predecessors, the sequence starts at `s₀ = (1,1)`, and the
final state lies in `G`. Equivalently, and more readably, the corresponding
sequence of cells from `S` to `G` in which consecutive cells are 4-adjacent and no
cell is a wall.

Because every action costs 1, the cost of that solution is `k`, its number of
moves. An **optimal** solution is one with minimum `k` — a shortest path. Several
distinct optimal paths may exist; the task asks for one of them, not all. Since
`h(s₀) = 20`, any optimal solution has `k ≥ 20`.

If no such sequence exists, the correct output is not an empty path or a crash
but an explicit report of **failure** — the case deliberately tested in Task 3,
Test 3.

---

# Task 1 — Plan the Agent

Design fixed before prompting the LLM. Each decision is recorded together with
its reason, so that Task 7 can distinguish what was designed here from what the
LLM later contributed.

## 1. How a state is represented in Python

A tuple of two integers, `(row, col)`.

Tuples are **hashable**, so a state can be used directly as a `dict` key or a
`set` member — which is exactly what duplicate detection and the parent table
need. They are also **immutable**, so a state cannot be mutated by accident after
being stored. A list `[row, col]` provides neither property, and a custom class
would require `__hash__` and `__eq__` to be written by hand for no gain.

Convention: `row` increases downward, `col` increases rightward, both 0-indexed,
so that `grid[row][col]` indexes the map directly and no coordinate translation
is needed anywhere in the program.

## 2. How the warehouse is represented

The map is read as a list of strings, `grid`, indexed `grid[row][col]`.

A single parsing pass scans the grid, records the coordinates of `S` and `G` as
`start` and `goal`, and otherwise leaves the characters untouched. Walls stay in
place as `'#'`, which makes the obstacle test an O(1) character lookup and avoids
maintaining a separate set of obstacle coordinates that could drift out of sync
with the map.

The raw text is retained so that the final path can be printed overlaid on the
warehouse, which is far easier to check by eye than a list of dozens of
coordinate pairs.

One hazard to guard against: if a map file has trailing whitespace stripped, its
rows can end up ragged (of differing lengths). The bounds test should therefore
use `len(grid[r])` for the row actually being indexed, rather than assuming every
row has the same width.

## 3. How valid actions are determined

For a state `(r, c)`, iterate over the four offsets and keep `(r+dr, c+dc)` when

```
0 <= nr < len(grid)  and  0 <= nc < len(grid[nr])  and  grid[nr][nc] != '#'
```

Successors are generated in a **fixed order** — Up, Down, Left, Right. This is
deliberate. When several nodes tie on `f`, the order in which they were pushed
decides which is expanded first, which in turn changes both the particular path
returned and the number of states expanded. Fixing the order makes every run
reproducible, and makes the BFS/A* comparison in Task 5 and the heuristic
comparison in Task 6 meaningful rather than noisy.

## 4. How the agent recognises it has reached the goal

By testing `state == goal` **when a node is removed from the frontier**, not when
it is generated.

This is the design decision most easily got wrong. Testing at generation time
returns the first path that happens to touch `G`, which is not necessarily the
cheapest one; A* guarantees optimality only when the goal is recognised at
expansion time, because only then is it certain that no cheaper route to `G`
remains in the frontier. Applying the same rule to BFS as well — even though BFS
with unit costs would be safe either way — keeps the "states expanded" figures in
Task 5 measured on the same basis and therefore genuinely comparable.

## 5. What information must be stored in the frontier

A **priority queue** (binary min-heap, `heapq`) whose entries are tuples:

```
(f, tie_break, state)        where f = g + h
```

- `f = g(n) + h(n)` is the ordering key — the node with smallest `f` is expanded next.
- `tie_break` is a strictly increasing counter, incremented on every push. It
  serves two purposes: it makes ties resolve first-in-first-out and therefore
  deterministic, and it guarantees that Python's tuple comparison never has to
  compare two `state` tuples, which would silently impose an arbitrary
  geographical ordering on the search.
- `state` is the cell itself.

Supporting structures held **outside** the heap:

- `best_g : dict[state → int]` — cheapest cost-from-start known so far per state.
- `parent : dict[state → state]` — the predecessor on that cheapest known route.
- `closed : set[state]` — states already expanded.

Parent pointers are kept in a dictionary rather than pushed into the heap
entries. The obvious alternative — storing the whole path so far inside each
frontier entry — was considered and rejected: it costs memory proportional to
path length for *every* node in the frontier, whereas one parent pointer per
state is constant. It also makes each heap entry expensive to copy during sift
operations.

**Avoiding repeated expansion.** Two checks working together:

- *On pop*: if the state is already in `closed`, discard the entry and continue.
  This is *lazy deletion* — `heapq` offers no decrease-key operation, so an
  improved route to a state is handled by pushing a second entry and ignoring the
  stale one when it later surfaces.
- *On generating a successor* with `ng = g + 1`: push it only if the state is
  unseen or `ng < best_g[state]`, updating `best_g` and `parent` at the same
  time.

A consequence worth anticipating when reporting results: *generated* can exceed
*expanded*, and the heap may briefly hold more entries than there are distinct
states.

## 6. How the final path is reconstructed

`parent[start]` is set to `None`. Whenever a successor is pushed as an
improvement, `parent[successor] = current`. When `goal` is popped, walk backwards
`goal → parent[goal] → …` until `None` is reached, collecting states, then
reverse the list.

The result is the cell sequence from `S` to `G`. Consecutive pairs can be
differenced to recover the action names (`Up`/`Down`/`Left`/`Right`) for a more
readable report.

## Heuristic

```
h((r, c)) = |r − goal_r| + |c − goal_c|          (Manhattan distance)
```

The heuristic is passed into the search as a **function parameter**, not
hard-coded inside it. This is planned now because Task 6 requires running the
same search with `h = 0`, with Euclidean distance, and with `2 × Manhattan`;
making it a parameter means those experiments need no edit to the algorithm and
therefore cannot accidentally change anything else at the same time.

## What the program reports on termination

| Field | Meaning |
|---|---|
| `found` | Boolean — whether a solution was reached |
| `path` | List of cells from `S` to `G`; empty when `found` is false |
| `path_length` | **Number of moves** = `len(path) − 1` = path cost |
| `nodes_expanded` | Number of non-stale pops from the frontier |
| `nodes_generated` | Number of successors pushed (extra, for Tasks 5–6) |
| `max_frontier_size` | Peak heap size (extra, for Tasks 5–6) |
| rendered map | The warehouse printed with the path marked, for visual checking |

`path_length` is defined here as the **number of moves**, not the number of cells
visited — the two differ by exactly one, and fixing the definition in advance
avoids an off-by-one when BFS and A* results are compared in Task 5.

## Failure and termination

If the frontier empties before `goal` is popped, the agent returns
`found = False`. Termination is guaranteed because `closed` only ever grows, no
state is expanded twice, and the number of non-wall cells is finite (64 here) —
so the loop cannot run forever even when the goal is unreachable. This is
precisely the property Test 3 of Task 3 is designed to check.

## BFS variant (planned now, for Task 5)

The BFS agent reuses the identical map parsing, successor generation, goal test,
parent table and path reconstruction, changing only the frontier: a
`collections.deque` used first-in-first-out, with no `g`, `h`, or `f`. Sharing
everything except the frontier discipline is deliberate — it ensures that any
difference observed in Task 5 is attributable to the search strategy alone, and
not to some incidental difference in how the two programs happened to be written.

---

## Predictions recorded before implementation

Stated in advance so that Tasks 5 and 6 test them rather than rationalise them
afterwards.

1. BFS and A* will find paths of the **same length**, since Manhattan distance
   never overestimates the true cost on a 4-connected unit-cost grid and is
   therefore admissible.
2. A* will expand **fewer** states, because `h` steers expansion toward the goal
   instead of growing a uniform ring outward from the start.
3. With `h = 0`, A* degenerates to uniform-cost search and should expand roughly
   as many states as BFS, while still returning an optimal path.
4. Euclidean distance is admissible here but weaker than Manhattan (it can never
   exceed it, and Manhattan is itself admissible), so it should expand
   somewhat more states than Manhattan while still returning an optimal path.
5. `2 × Manhattan` is **not** admissible. It should expand noticeably fewer
   states — and may well return a path longer than optimal. This is the trade-off
   the "Think About It" box points at: speed bought at the cost of the optimality
   guarantee.
