"""Tasks 5 and 6 -- comparing search strategies and investigating the heuristic.

Task 5: BFS versus A* on the supplied warehouse (the warehouse is not changed).
Task 6: A* with h = 0, Manhattan, Euclidean and 2 x Manhattan.

Two maps are measured throughout.  The supplied warehouse is almost entirely
single-width corridor, which leaves the search no choices to make and therefore
hides the difference between the strategies.  The open-plan map is included as a
control, to show what the corridors conceal.

A* is reported under both f-tie-breaking rules, because on this problem that
choice turns out to matter more than the choice of heuristic.
"""

from __future__ import annotations

from astar_warehouse import (
    WAREHOUSE_MAP,
    SearchResult,
    Warehouse,
    astar,
    bfs,
    euclidean,
    manhattan,
    manhattan_x2,
    zero,
)

OPEN_ROOM = """\
#####################
#S..................#
#...................#
#....#########......#
#....#.......#......#
#....#.......#......#
#....#########......#
#...................#
#..................G#
#####################
"""

# A cluttered room, found by randomised search over maps for a case in which the
# inadmissible heuristic actually returns a suboptimal path.  On the two maps
# above, 2 x Manhattan happens to stay optimal -- inadmissibility removes the
# guarantee, it does not force a violation.  This map shows the violation.
CLUTTERED_ROOM = """\
#####################
#S..................#
#...#...##..........#
#....##........##...#
##........#.........#
#....##.........#..##
#......#.#......###.#
#..#...#......##...##
#.......#.....#....##
#.........#.....#..G#
#####################
"""


def free_cells(wh: Warehouse) -> int:
    return sum(1 for row in wh.grid for ch in row if ch != "#")


HEADER = (f"{'':<28} {'found':<7} {'length':>6} {'expanded':>9}"
          f" {'generated':>10} {'frontier':>9}")


def line(name: str, r: SearchResult, optimum: int | None = None) -> str:
    length = "-" if r.path_length is None else str(r.path_length)
    flag = ""
    if optimum is not None and r.path_length is not None:
        flag = ("  optimal" if r.path_length == optimum
                else f"  SUBOPTIMAL (+{r.path_length - optimum})")
    return (f"{name:<28} {str(r.found):<7} {length:>6} {r.nodes_expanded:>9}"
            f" {r.nodes_generated:>10} {r.max_frontier:>9}{flag}")


def task5(label: str, text: str) -> None:
    wh = Warehouse.from_text(text)
    n = free_cells(wh)
    print(f"\n{label}   ({n} free cells, h(s0) = {manhattan(wh.start, wh.goal):.0f})")
    print("-" * 88)
    print(HEADER)

    b = bfs(wh)
    a_fifo = astar(wh, h=manhattan, tie_break="fifo")
    a_deep = astar(wh, h=manhattan, tie_break="deep")
    print(line("BFS", b))
    print(line("A* Manhattan, FIFO ties", a_fifo))
    print(line("A* Manhattan, prefer deeper", a_deep))

    print()
    print(f"  (a) both found a solution      : {b.found and a_deep.found}")
    print(f"  (b) same path length           : "
          f"{b.path_length == a_deep.path_length == a_fifo.path_length} "
          f"({b.path_length} moves)")
    saved = b.nodes_expanded - a_deep.nodes_expanded
    pct = 100.0 * saved / b.nodes_expanded if b.nodes_expanded else 0.0
    print(f"  (c) fewest states expanded     : "
          f"{'A*' if saved > 0 else 'tied'}  "
          f"(BFS {b.nodes_expanded}, A* {a_deep.nodes_expanded})")
    print(f"      states saved by A*         : {saved}  ({pct:.1f}% fewer)")
    print(f"      of {n} free cells, BFS reached {100.0 * b.nodes_expanded / n:.0f}%"
          f" and A* reached {100.0 * a_deep.nodes_expanded / n:.0f}%")


def task6(label: str, text: str) -> None:
    wh = Warehouse.from_text(text)
    print(f"\n{label}   ({free_cells(wh)} free cells)")
    print("-" * 88)
    print(HEADER)
    optimum = astar(wh, h=manhattan).path_length
    for name, h in (("h = 0 (uniform cost)", zero),
                    ("h = Manhattan", manhattan),
                    ("h = Euclidean", euclidean),
                    ("h = 2 x Manhattan", manhattan_x2)):
        print(line(name, astar(wh, h=h, tie_break="deep"), optimum))
    print("  (all rows use the 'prefer deeper' tie-break, so that the heuristic is")
    print("   the only thing varying between them)")


def main() -> None:
    print("=" * 88)
    print("Task 5 -- A* compared with blind search (BFS)")
    print("=" * 88)
    task5("Supplied warehouse", WAREHOUSE_MAP)
    task5("Open-plan map (control)", OPEN_ROOM)

    print("\n\n" + "=" * 88)
    print("Task 6 -- Investigating the heuristic")
    print("=" * 88)
    task6("Supplied warehouse", WAREHOUSE_MAP)
    task6("Open-plan map (control)", OPEN_ROOM)
    task6("Cluttered room -- where inadmissibility bites", CLUTTERED_ROOM)


if __name__ == "__main__":
    main()
