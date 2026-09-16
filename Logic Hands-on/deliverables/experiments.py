"""
Experiments -- the evidence behind sections 5, 6 and 7 of LAB_REPORT.md.

Three parts:

  1. Reachable state space and applicability, for the warehouse.
  2. The three defects, demonstrated rather than asserted.
  3. BFS vs DFS -- what the choice of search strategy buys.

Run:  python experiments.py            (or  python experiments.py > results.txt)
"""

import time
from collections import deque

from planner import (
    Action, Problem, make_state, show_state,
    bfs_plan, dfs_plan, bfs_plan_no_visited, validate_plan,
    warehouse, move_action, pickup_action, drop_action,
    CONNECTED,
)


def section(title):
    print("")
    print("=" * 78)
    print(title)
    print("=" * 78)
    print("")


# ---------------------------------------------------------------------------
# 1. The state space
# ---------------------------------------------------------------------------

def experiment_state_space():
    section("1. The reachable state space of the warehouse")

    p = warehouse()
    seen, order, frontier = {p.initial}, [p.initial], deque([p.initial])
    while frontier:
        s = frontier.popleft()
        for a in p.actions:
            if a.applicable(s):
                t = a.apply(s)
                if t not in seen:
                    seen.add(t)
                    order.append(t)
                    frontier.append(t)

    print("3 locations, 1 robot, 1 package.")
    print("Ground actions            : %d" % len(p.actions))
    print("Reachable states from I   : %d" % len(seen))
    print("")
    print("Every reachable state, with the actions applicable in it:")
    print("")
    print("    %-42s %s" % ("state", "applicable actions"))
    print("    %-42s %s" % ("-" * 42, "-" * 30))
    for s in order:
        names = ", ".join(a.name for a in p.applicable_actions(s))
        goal_mark = "  <- goal" if p.satisfies_goal(s) else ""
        print("    %-42s %s%s" % (show_state(s), names, goal_mark))
    print("")
    print("The state space is tiny -- which is why the errors in this")
    print("laboratory are errors of MODELLING, not of scale.  A planner can be")
    print("exhaustively correct over a state space it has described wrongly.")


# ---------------------------------------------------------------------------
# 2. The defects
# ---------------------------------------------------------------------------

def experiment_defects():
    section("2. The three defects, demonstrated")

    # -- Defect 0: goal test by equality --------------------------------------
    print("Defect 0 -- goal test written as state == G instead of G subset of S")
    print("")
    p = warehouse()
    r = bfs_plan(p)
    final = r.states[-1]
    print("    final state reached : %s" % show_state(final))
    print("    the goal            : %s" % show_state(p.goal))
    print("    G subset of S       : %s   <- the correct test, plan found" %
          (p.goal <= final))
    print("    S == G              : %s   <- the buggy test, 'No plan found'" %
          (final == p.goal))
    print("")
    print("    Symptom: the planner reports failure on a problem that is")
    print("    obviously solvable.  Loud, and caught by Test A immediately.")
    print("")

    # -- Defect 1: missing duplicate detection --------------------------------
    print("Defect 1 -- no duplicate detection (the visited set)")
    print("")
    solvable = warehouse()
    unsolvable = warehouse(with_pickup=False)

    r_ok = bfs_plan_no_visited(solvable, max_expansions=50000)
    print("    SOLVABLE problem, defective search  : plan of %d actions, "
          "%d expansions" % (r_ok.length, r_ok.expanded))
    r_fix = bfs_plan(solvable)
    print("    SOLVABLE problem, corrected search  : plan of %d actions, "
          "%d expansions" % (r_fix.length, r_fix.expanded))
    print("    -> identical answers.  Test A cannot tell them apart.")
    print("")

    r_fix2 = bfs_plan(unsolvable)
    print("    UNSOLVABLE problem, corrected search: %s after %d expansions"
          % ("no plan found" if not r_fix2.found else "plan?!", r_fix2.expanded))
    limits = [1000, 10000, 50000]
    for limit in limits:
        t0 = time.time()
        try:
            bfs_plan_no_visited(unsolvable, max_expansions=limit)
            outcome = "terminated"
        except RuntimeError:
            outcome = "still running"
        print("    UNSOLVABLE problem, defective search: %s at %6d expansions "
              "(%.2fs)" % (outcome, limit, time.time() - t0))
    print("")
    print("    Cause: Move(A,B) and Move(B,A) form a 2-cycle.  The frontier")
    print("    refills faster than it drains, so failure is never reported.")
    print("    Symptom: a hang, not a wrong answer -- and only on the")
    print("    unsolvable problem.  Test B is what exposes it.")
    print("")

    # -- Defect 2: unrestricted Move ------------------------------------------
    print("Defect 2 -- Move instantiated over every pair of locations")
    print("")
    bad = warehouse(connected_moves=False)
    rb = bfs_plan(bad)
    ok, _ = validate_plan(bad, rb.plan, rb.states)
    good = warehouse()
    rg = bfs_plan(good)

    print("    correct domain   : %2d ground actions, plan of %d: %s"
          % (len(good.actions), rg.length,
             " -> ".join(a.name for a in rg.plan)))
    print("    defective domain : %2d ground actions, plan of %d: %s"
          % (len(bad.actions), rb.length,
             " -> ".join(a.name for a in rb.plan)))
    print("")
    print("    Is the short plan internally consistent?  %s" % ok)
    print("    Every precondition of every step is satisfied in the state where")
    print("    the step is taken; the final state entails the goal; BFS even")
    print("    proves it is the SHORTEST such plan.  Re-executing it confirms")
    print("    all of that.  It is still nonsense: there is no corridor from A")
    print("    to C.")
    print("")
    print("    Symptom: none, from inside.  The action model is wrong, and no")
    print("    amount of checking the plan against that model can reveal it.")
    print("    Only a check against an independent description of the")
    print("    warehouse -- planner.pl -- rejects it.  See run_prolog.py.")
    print("")
    print("    Moves used, checked against the connectivity facts:")
    for a in rb.plan:
        if not a.name.startswith("Move("):
            continue
        x, y = a.name[len("Move("):-1].split(",")
        supported = (x, y) in CONNECTED
        print("        %-12s connected(%s,%s) = %s%s"
              % (a.name, x.lower(), y.lower(), supported,
                 "" if supported else "    <-- UNSUPPORTED"))


# ---------------------------------------------------------------------------
# 3. Search strategy
# ---------------------------------------------------------------------------

def experiment_search_strategies():
    section("3. Where the SEARCH half of 'Logic + Search' shows up")

    problems = [
        ("warehouse", warehouse()),
        ("warehouse, 6 locations in a line", _corridor(6)),
        ("warehouse, 8 locations in a line", _corridor(8)),
    ]

    print("%-34s %-6s %-8s %-10s %-10s %s"
          % ("problem", "algo", "plan len", "expanded", "generated", "peak frontier"))
    print("%-34s %-6s %-8s %-10s %-10s %s"
          % ("-" * 34, "-" * 6, "-" * 8, "-" * 10, "-" * 10, "-" * 13))
    for name, p in problems:
        for label, fn in (("BFS", bfs_plan), ("DFS", dfs_plan)):
            r = fn(p)
            ok, _ = validate_plan(p, r.plan) if r.found else (None, None)
            print("%-34s %-6s %-8s %-10d %-10d %d%s"
                  % (name, label, r.length, r.expanded, r.generated,
                     r.peak_frontier, "" if ok else "   INVALID"))
    print("")
    print("Both are complete here and both return valid plans.  BFS additionally")
    print("returns a SHORTEST plan, because it explores in order of increasing")
    print("plan length and every action costs 1.  DFS has no such guarantee: it")
    print("returns the first plan it reaches, and it only matches BFS on these")
    print("problems because the corridor leaves it almost no wrong turns to take.")
    print("")
    print("Note what does NOT change between the rows: the applicability test.")
    print("Logic decides what is possible; search only decides what to try next.")


def _corridor(n):
    """A line of n locations, package at one end, goal at the other."""
    locs = [chr(ord("A") + i) for i in range(n)]
    edges = []
    for i in range(n - 1):
        edges.append((locs[i], locs[i + 1]))
        edges.append((locs[i + 1], locs[i]))
    actions = [move_action(x, y) for x, y in edges]
    actions += [pickup_action(x) for x in locs]
    actions += [drop_action(x) for x in locs]
    return Problem(
        initial=make_state("At(Robot,%s)" % locs[0], "At(Package,%s)" % locs[0]),
        actions=actions,
        goal=make_state("At(Package,%s)" % locs[-1]),
        name="corridor-%d" % n,
    )


# ---------------------------------------------------------------------------

def main():
    print("=" * 78)
    print("Experiments -- CS F407 Logical Reasoning for Planning")
    print("=" * 78)
    experiment_state_space()
    experiment_defects()
    experiment_search_strategies()


if __name__ == "__main__":
    main()
