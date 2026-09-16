"""Task 3 -- systematic testing of the LLM-generated A* agent.

Each test states the expected behaviour independently of the program, so that a
plausible-looking answer cannot pass by accident.  Every successful result is
additionally put through `validate_path`, which checks that the returned path is
a real path rather than merely a list of the right length.
"""

from __future__ import annotations

from astar_warehouse import (
    WAREHOUSE_MAP,
    SearchResult,
    Warehouse,
    astar,
    manhattan,
    render,
)

PASSED = 0
FAILED = 0


def check(label: str, condition: bool, detail: str = "") -> None:
    global PASSED, FAILED
    if condition:
        PASSED += 1
        print(f"    PASS  {label}")
    else:
        FAILED += 1
        print(f"    FAIL  {label}   {detail}")


def validate_path(wh: Warehouse, result: SearchResult) -> tuple[bool, str]:
    """Is the returned path an actual, legal, contiguous route from S to G?"""
    path = result.path
    if not path:
        return False, "path is empty"
    if path[0] != wh.start:
        return False, f"path starts at {path[0]}, not at S={wh.start}"
    if path[-1] != wh.goal:
        return False, f"path ends at {path[-1]}, not at G={wh.goal}"
    if len(set(path)) != len(path):
        return False, "path revisits a cell"
    for a, b in zip(path, path[1:]):
        if abs(a[0] - b[0]) + abs(a[1] - b[1]) != 1:
            return False, f"{a} and {b} are not 4-adjacent"
        if not wh.is_free(*b):
            return False, f"{b} is an obstacle or out of bounds"
    if result.path_length != len(path) - 1:
        return False, "reported length disagrees with the path"
    return True, ""


def run(label: str, text: str, *, expect_found: bool, expect_length: int | None,
        show_map: bool = False) -> SearchResult:
    print(f"\n{label}")
    wh = Warehouse.from_text(text)
    result = astar(wh, h=manhattan)

    print(f"    found={result.found}  length={result.path_length}  "
          f"expanded={result.nodes_expanded}  generated={result.nodes_generated}  "
          f"peak frontier={result.max_frontier}")

    check("solution found matches expectation",
          result.found == expect_found,
          f"got {result.found}, expected {expect_found}")

    if expect_found:
        check(f"path length is {expect_length} moves",
              result.path_length == expect_length,
              f"got {result.path_length}")
        ok, why = validate_path(wh, result)
        check("returned path is legal and contiguous", ok, why)
        if show_map:
            print()
            for line in render(wh, result.path).splitlines():
                print(f"      {line}")
    else:
        check("path is empty on failure", result.path == [], f"got {result.path}")

    return result


# --------------------------------------------------------------------------

print("=" * 70)
print("Task 3 -- Testing the generated A* program")
print("=" * 70)

# Test 1 ------------------------------------------------------------------
# The supplied warehouse.  Expected length derived by hand from the map: the
# route is forced -- (1,1)->(1,5) 4, down to (5,5) 4, right to (5,13) 8,
# up to (3,13) 2, left to (3,7) 6, up to (1,7) 2, right to (1,15) 8,
# down to (7,15) 6  =  40 moves.
run("Test 1: original warehouse", WAREHOUSE_MAP,
    expect_found=True, expect_length=40, show_map=True)

# Test 2 ------------------------------------------------------------------
# Goal immediately adjacent to the start: the one-step solution.
TRIVIAL = """\
#####
#SG##
#####
"""
r2 = run("Test 2: trivial case (goal adjacent to start)", TRIVIAL,
         expect_found=True, expect_length=1)
check("expanded exactly 2 states (start, then goal)",
      r2.nodes_expanded == 2, f"got {r2.nodes_expanded}")

# Test 3 ------------------------------------------------------------------
# Goal walled off completely.  Must report failure, not loop and not crash.
NO_SOLUTION = """\
#######
#S....#
###.###
#...#G#
#######
"""
r3 = run("Test 3: no solution (goal sealed off)", NO_SOLUTION,
         expect_found=False, expect_length=None)
check("terminated having expanded only the reachable region",
      r3.nodes_expanded < 12, f"expanded {r3.nodes_expanded}")

# Test 4 ------------------------------------------------------------------
# Two routes exist: straight along the top corridor (6 moves), or the long way
# round the bottom (10 moves).  A* must return the shorter one.
TWO_PATHS = """\
#########
#S.....G#
#.#####.#
#.......#
#########
"""
r4 = run("Test 4: alternative paths (6 via the top, 10 round the bottom)",
         TWO_PATHS, expect_found=True, expect_length=6, show_map=True)
check("chose the top corridor, not the detour",
      all(cell[0] == 1 for cell in r4.path),
      f"path leaves row 1: {r4.path}")

# Test 5 (extra) ----------------------------------------------------------
# No wall border at all.  Checks that bounds are tested explicitly and that a
# negative index does not wrap around to the far end of a row.
NO_BORDER = """\
S.
.G
"""
run("Test 5 (extra): map with no wall border", NO_BORDER,
    expect_found=True, expect_length=2)

# Test 6 (extra) ----------------------------------------------------------
# Ragged rows -- trailing whitespace stripped from a map file.
RAGGED = "\n".join(["####", "#S.", "#.G#", "####"])
run("Test 6 (extra): ragged rows (unequal line lengths)", RAGGED,
    expect_found=True, expect_length=2)

# --------------------------------------------------------------------------

print("\n" + "=" * 70)
print(f"{PASSED} passed, {FAILED} failed")
print("=" * 70)
raise SystemExit(1 if FAILED else 0)
