"""A* search agent for the warehouse robot navigation problem.

CS F407 Artificial Intelligence -- Laboratory: Search and A*

Implements the design fixed in Task 1.  Concept markers of the form
``[CONCEPT] name`` appear against the lines that realise each element of the
formulation P = (S, A, T, s0, G, c); Task 4 refers to them.
"""

from __future__ import annotations

import heapq
import itertools
import math
from collections import deque
from dataclasses import dataclass
from typing import Callable, Iterator, Optional

# A state is the robot's position.  Position alone is a complete state: the
# warehouse is static and the robot carries nothing.        [CONCEPT] State
State = tuple[int, int]

# The four actions, as (name, d_row, d_col).  Fixed order -- Up, Down, Left,
# Right -- so that f-ties resolve identically on every run.  [CONCEPT] Action
MOVES: tuple[tuple[str, int, int], ...] = (
    ("Up", -1, 0),
    ("Down", 1, 0),
    ("Left", 0, -1),
    ("Right", 0, 1),
)

STEP_COST = 1  # every movement costs 1                      [CONCEPT] Cost c


# --------------------------------------------------------------------------
# The environment
# --------------------------------------------------------------------------

class Warehouse:
    """An ASCII grid map, plus the start and goal it declares."""

    def __init__(self, grid: list[str], start: State, goal: State) -> None:
        self.grid = grid
        self.start = start  # s0                             [CONCEPT] Initial state
        self.goal = goal    # the single member of G         [CONCEPT] Goal

    @classmethod
    def from_text(cls, text: str) -> "Warehouse":
        """Parse a map, locating S and G in a single pass."""
        grid = [line.rstrip("\n") for line in text.splitlines() if line.strip()]
        if not grid:
            raise ValueError("map is empty")

        start: Optional[State] = None
        goal: Optional[State] = None
        for r, row in enumerate(grid):
            for c, ch in enumerate(row):
                if ch == "S":
                    start = (r, c)
                elif ch == "G":
                    goal = (r, c)
        if start is None:
            raise ValueError("map contains no start cell 'S'")
        if goal is None:
            raise ValueError("map contains no goal cell 'G'")
        return cls(grid, start, goal)

    @classmethod
    def from_file(cls, path: str) -> "Warehouse":
        with open(path, encoding="utf-8") as handle:
            return cls.from_text(handle.read())

    def is_free(self, r: int, c: int) -> bool:
        """An action is invalid if its target is out of bounds or an obstacle.

        Both conditions are tested.  The supplied warehouse has a closed wall
        border, but the small test maps need not, and in Python a negative
        index would silently wrap to the far end of the row.
        """
        return (
            0 <= r < len(self.grid)
            and 0 <= c < len(self.grid[r])   # per-row: rows may be ragged
            and self.grid[r][c] != "#"
        )

    def successors(self, state: State) -> Iterator[tuple[str, State]]:
        """T(s, a) for every action applicable in `state`.  [CONCEPT] Transition"""
        r, c = state
        for name, dr, dc in MOVES:
            nr, nc = r + dr, c + dc
            if self.is_free(nr, nc):
                yield name, (nr, nc)


# --------------------------------------------------------------------------
# Heuristics -- h(state, goal).  Passed into the search as a parameter so that
# Task 6 can swap them without editing the algorithm.        [CONCEPT] h(n)
# --------------------------------------------------------------------------

def manhattan(s: State, goal: State) -> float:
    """|x - x_G| + |y - y_G|.  Admissible on a 4-connected unit-cost grid."""
    return abs(s[0] - goal[0]) + abs(s[1] - goal[1])


def zero(s: State, goal: State) -> float:
    """h = 0.  Reduces A* to uniform-cost search."""
    return 0.0


def euclidean(s: State, goal: State) -> float:
    """Straight-line distance.  Admissible here, but weaker than Manhattan."""
    return math.hypot(s[0] - goal[0], s[1] - goal[1])


def manhattan_x2(s: State, goal: State) -> float:
    """2 x Manhattan.  Deliberately inadmissible -- see Task 6."""
    return 2.0 * manhattan(s, goal)


# --------------------------------------------------------------------------
# Result record
# --------------------------------------------------------------------------

@dataclass
class SearchResult:
    algorithm: str
    found: bool
    path: list[State]
    nodes_expanded: int
    nodes_generated: int
    max_frontier: int

    @property
    def path_length(self) -> Optional[int]:
        """Number of MOVES, not number of cells visited (see Task 1)."""
        return len(self.path) - 1 if self.found else None


# --------------------------------------------------------------------------
# Path reconstruction                                  [CONCEPT] Path reconstruction
# --------------------------------------------------------------------------

def reconstruct(parent: dict[State, Optional[State]], goal: State) -> list[State]:
    """Walk parent pointers back from the goal, then reverse.

    Terminates: a node's parent is always a node that was closed strictly
    earlier, so the chain cannot contain a cycle.
    """
    path: list[State] = []
    node: Optional[State] = goal
    while node is not None:
        path.append(node)
        node = parent[node]
    path.reverse()
    return path


# --------------------------------------------------------------------------
# A* search
# --------------------------------------------------------------------------

def astar(
    wh: Warehouse,
    h: Callable[[State, State], float] = manhattan,
    tie_break: str = "deep",
) -> SearchResult:
    """A* on the warehouse grid, evaluating f(n) = g(n) + h(n).

    `tie_break` decides what happens when two nodes have equal f:

    * ``"deep"``  -- prefer the node with the LARGER g, i.e. the one further
      along a route.  This matters enormously here.  On a 4-connected grid
      with unit costs, Manhattan distance makes f constant along every
      detour-free route, so almost the whole map ties on f.  Under FIFO those
      ties are resolved in insertion order, which is precisely BFS order, and
      A* then expands exactly as many states as BFS.  Preferring larger g
      drives the search along one route to the goal instead of fanning out.
    * ``"fifo"`` -- first-in, first-out.  Retained so that Task 5 can measure
      the effect above rather than merely assert it.

    Both settings return an optimal path when h is admissible; they differ
    only in how many states are expanded on the way.
    """
    if tie_break not in ("deep", "fifo"):
        raise ValueError("tie_break must be 'deep' or 'fifo'")

    start, goal = wh.start, wh.goal

    tie = itertools.count()          # stops the heap ever comparing two
                                     # state tuples, and makes ties FIFO
                                     # once f and g are equal

    def entry(f: float, g: int, state: State) -> tuple[float, int, int, State]:
        # Negated g, so that the smaller heap key is the larger g.
        return (f, -g if tie_break == "deep" else 0, next(tie), state)

    # The frontier: a min-heap ordered by f.               [CONCEPT] Frontier
    frontier: list[tuple[float, int, int, State]] = [
        entry(h(start, goal), 0, start)
    ]

    best_g: dict[State, int] = {start: 0}                 # [CONCEPT] g(n)
    parent: dict[State, Optional[State]] = {start: None}
    closed: set[State] = set()                            # [CONCEPT] Visited states

    expanded = 0
    generated = 0
    max_frontier = len(frontier)

    while frontier:
        max_frontier = max(max_frontier, len(frontier))
        _f, _negg, _t, state = heapq.heappop(frontier)

        # Lazy deletion: heapq has no decrease-key, so an improved route was
        # pushed as a second entry.  The stale one is discarded here.
        if state in closed:
            continue
        closed.add(state)
        expanded += 1

        # Goal test on POP, not on generation -- this is what makes A*
        # optimal under an admissible heuristic.           [CONCEPT] Goal test
        if state == goal:
            return SearchResult(
                f"A* [{tie_break}]", True, reconstruct(parent, goal), expanded, generated, max_frontier
            )

        g = best_g[state]
        for _action, nxt in wh.successors(state):
            if nxt in closed:
                continue
            ng = g + STEP_COST
            if nxt not in best_g or ng < best_g[nxt]:
                best_g[nxt] = ng
                parent[nxt] = state
                f = ng + h(nxt, goal)                     # [CONCEPT] f(n) = g(n) + h(n)
                heapq.heappush(frontier, entry(f, ng, nxt))
                generated += 1

    # Frontier exhausted: the goal is unreachable.  Report failure rather than
    # looping.  Terminates because `closed` only grows and the grid is finite.
    return SearchResult(f"A* [{tie_break}]", False, [], expanded, generated, max_frontier)


# --------------------------------------------------------------------------
# Breadth-first search -- Task 5
#
# Shares the map parsing, successor generation, goal test, parent table and
# path reconstruction with A*.  The ONLY difference is the frontier: a FIFO
# queue instead of a priority queue, with no g, h or f.  Keeping everything
# else identical ensures the Task 5 comparison measures the search strategy
# and nothing else.
# --------------------------------------------------------------------------

def bfs(wh: Warehouse) -> SearchResult:
    """Breadth-first search: blind, but optimal when every step costs the same."""
    start, goal = wh.start, wh.goal

    frontier: deque[State] = deque([start])          # [CONCEPT] Frontier (FIFO)
    parent: dict[State, Optional[State]] = {start: None}
    seen: set[State] = {start}                       # ever enqueued
    closed: set[State] = set()

    expanded = 0
    generated = 0
    max_frontier = len(frontier)

    while frontier:
        max_frontier = max(max_frontier, len(frontier))
        state = frontier.popleft()

        if state in closed:
            continue
        closed.add(state)
        expanded += 1

        # Goal test on pop, exactly as in A*, so that the two "states
        # expanded" figures are measured on the same basis.
        if state == goal:
            return SearchResult(
                "BFS", True, reconstruct(parent, goal), expanded, generated, max_frontier
            )

        for _action, nxt in wh.successors(state):
            if nxt in seen:
                continue
            seen.add(nxt)
            parent[nxt] = state
            frontier.append(nxt)
            generated += 1

    return SearchResult("BFS", False, [], expanded, generated, max_frontier)


# --------------------------------------------------------------------------
# Presentation
# --------------------------------------------------------------------------

def path_actions(path: list[State]) -> list[str]:
    """Recover the action sequence by differencing consecutive cells."""
    names = {(dr, dc): name for name, dr, dc in MOVES}
    return [names[(b[0] - a[0], b[1] - a[1])] for a, b in zip(path, path[1:])]


def render(wh: Warehouse, path: list[State]) -> str:
    """The warehouse with the path drawn as '*' (S and G left visible)."""
    on_path = set(path) - {wh.start, wh.goal}
    return "\n".join(
        "".join("*" if (r, c) in on_path else ch for c, ch in enumerate(row))
        for r, row in enumerate(wh.grid)
    )


def report(wh: Warehouse, result: SearchResult, show_map: bool = True) -> None:
    print(f"algorithm        : {result.algorithm}")
    print(f"solution found   : {result.found}")
    if result.found:
        print(f"path length      : {result.path_length} moves")
        print(f"path             : {' -> '.join(str(p) for p in result.path)}")
        print(f"actions          : {', '.join(path_actions(result.path))}")
    print(f"states expanded  : {result.nodes_expanded}")
    print(f"states generated : {result.nodes_generated}")
    print(f"peak frontier    : {result.max_frontier}")
    if show_map and result.found:
        print()
        print(render(wh, result.path))


WAREHOUSE_MAP = """\
#################
#S....#.........#
#.###.#.#######.#
#...#.#.......#.#
###.#.#######.#.#
#...#.........#.#
#.###########.#.#
#.............#G#
#################
"""


if __name__ == "__main__":
    warehouse = Warehouse.from_text(WAREHOUSE_MAP)
    print(f"start s0 = {warehouse.start}    goal G = {warehouse.goal}")
    print(f"h(s0)    = {manhattan(warehouse.start, warehouse.goal)}  "
          f"(lower bound on the solution cost)")
    print()
    report(warehouse, astar(warehouse, h=manhattan))
