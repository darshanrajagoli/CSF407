"""
Task 3 -- test the generated planner.

"Do not assume the LLM-generated program is correct."

The handout asks for at least three tests (A: solvable, B: impossible,
C: irrelevant actions).  This file runs those three plus eight more, because
the three required ones all PASSED on a version of the planner that was
nevertheless broken -- see LAB_REPORT.md section 7.

Every test that expects a plan additionally puts the plan through
`validate_plan`, which re-executes it from the initial state and checks each
precondition itself.  A plan of the right *length* is not evidence; it has to
be a plan whose every action is genuinely applicable where it is used.

Run:  python test_planner.py
"""

from planner import (
    Action, Problem, make_state, show_state,
    bfs_plan, dfs_plan, bfs_plan_no_visited, validate_plan,
    warehouse, move_action, pickup_action, drop_action,
    LOCATIONS, CONNECTED,
)

PASS = 0
FAIL = 0
LOG = []


def check(label, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        LOG.append("    [ok]   %s" % label)
    else:
        FAIL += 1
        LOG.append("    [FAIL] %s   %s" % (label, detail))


def header(title):
    LOG.append("")
    LOG.append(title)
    LOG.append("-" * len(title))


def record(problem, result):
    """The record the handout asks for: I, G, plan found?, plan, valid?"""
    LOG.append("    initial state : %s" % show_state(problem.initial))
    LOG.append("    goal          : %s" % show_state(problem.goal))
    LOG.append("    plan found    : %s" % result.found)
    if result.found:
        LOG.append("    plan          : %s"
                   % " -> ".join(a.name for a in result.plan))
        ok, _ = validate_plan(problem, result.plan, result.states)
        LOG.append("    plan valid    : %s" % ok)
        return ok
    LOG.append("    plan          : -")
    LOG.append("    plan valid    : n/a")
    return None


# ---------------------------------------------------------------------------
# Test A -- the original, solvable warehouse problem
# ---------------------------------------------------------------------------

def test_a_solvable():
    header("Test A -- solvable problem (the original warehouse)")
    p = warehouse()
    r = bfs_plan(p)
    valid = record(p, r)

    check("A1 a plan is found", r.found)
    check("A2 plan has 4 actions", r.length == 4, "got %s" % r.length)
    check("A3 plan is independently re-executable and reaches the goal", valid)
    check("A4 final state entails At(Package,C)",
          p.satisfies_goal(r.states[-1]))
    check("A5 the package is picked up before the robot leaves A",
          r.plan[0].name == "PickUp(Package,A)",
          "first action was %s" % r.plan[0].name)
    check("A6 every action in the plan is a declared action of the problem",
          all(a in p.actions for a in r.plan))
    check("A7 every Move in the plan is between connected locations",
          all(_move_pair(a) in CONNECTED for a in r.plan if _is_move(a)))


# ---------------------------------------------------------------------------
# Test B -- impossible problem
# ---------------------------------------------------------------------------

def test_b_impossible_no_pickup():
    header("Test B -- impossible problem (PickUp removed)")
    p = warehouse(with_pickup=False)
    r = bfs_plan(p)
    record(p, r)

    check("B1 reports no plan rather than inventing one", not r.found)
    check("B2 search terminated (finite expansions)", r.expanded < 10000)
    check("B3 the robot can still reach C -- the domain is not trivially dead",
          _robot_can_reach_c(p))


def test_b2_impossible_no_drop():
    header("Test B2 -- impossible problem (Drop removed)")
    p = warehouse(with_drop=False)
    r = bfs_plan(p)
    record(p, r)
    check("B4 reports no plan when the package can be held but never released",
          not r.found)


def test_b3_impossible_unreachable_goal():
    header("Test B3 -- impossible problem (goal mentions a location "
           "with no connection)")
    actions = [move_action("A", "B"), move_action("B", "A")]
    actions += [pickup_action(x) for x in ("A", "B")]
    actions += [drop_action(x) for x in ("A", "B")]
    p = Problem(initial=make_state("At(Robot,A)", "At(Package,A)"),
                actions=actions,
                goal=make_state("At(Package,C)"),
                name="A-B only, goal at C")
    r = bfs_plan(p)
    record(p, r)
    check("B5 reports no plan when C is disconnected", not r.found)


# ---------------------------------------------------------------------------
# Test C -- irrelevant actions
# ---------------------------------------------------------------------------

def test_c_irrelevant_actions():
    header("Test C -- irrelevant actions "
           "(robot reaching C is not the package reaching C)")

    # C(i): the robot can travel to C freely, but there is no PickUp/Drop.
    p = warehouse(with_pickup=False, with_drop=False)
    r = bfs_plan(p)
    record(p, r)
    check("C1 moving the robot to C alone does not satisfy the goal",
          not r.found)

    # C(ii): the state in which the robot is at C but the package is still at A
    at_c_package_at_a = make_state("At(Robot,C)", "At(Package,A)")
    full = warehouse()
    check("C2 {At(Robot,C), At(Package,A)} does NOT entail the goal",
          not full.satisfies_goal(at_c_package_at_a))
    LOG.append("    state %s |= G ?  %s"
               % (show_state(at_c_package_at_a),
                  full.satisfies_goal(at_c_package_at_a)))

    # C(iii): add a genuinely irrelevant action and check the plan is unchanged.
    idle = Action(name="Wiggle", pos_pre=["At(Robot,A)"],
                  pos_eff=["Wiggled"], neg_eff=[])
    noisy = Problem(initial=full.initial,
                    actions=full.actions + [idle],
                    goal=full.goal,
                    name="warehouse + irrelevant Wiggle action")
    rn = bfs_plan(noisy)
    record(noisy, rn)
    check("C3 an irrelevant extra action does not change the plan length",
          rn.length == 4, "got %s" % rn.length)
    check("C4 the irrelevant action does not appear in the plan",
          all(a.name != "Wiggle" for a in rn.plan))


# ---------------------------------------------------------------------------
# Test D -- the logical component in isolation (Task 0's question)
# ---------------------------------------------------------------------------

def test_d_applicability_in_I():
    header("Test D -- applicability in the initial state (Task 0)")
    p = warehouse()
    I = p.initial
    pickup_a = _find(p, "PickUp(Package,A)")
    drop_c = _find(p, "Drop(Package,C)")
    move_ab = _find(p, "Move(A,B)")

    LOG.append("    I = %s" % show_state(I))
    LOG.append("    PickUp(Package,A) applicable in I : %s"
               % pickup_a.applicable(I))
    LOG.append("    Drop(Package,C)   applicable in I : %s   (%s)"
               % (drop_c.applicable(I), drop_c.why_inapplicable(I)))

    check("D1 PickUp(Package,A) IS applicable in I", pickup_a.applicable(I))
    check("D2 Drop(Package,C) is NOT applicable in I", not drop_c.applicable(I))
    check("D3 Move(A,B) IS applicable in I", move_ab.applicable(I))
    check("D4 exactly two actions are applicable in I",
          len(p.applicable_actions(I)) == 2,
          "got %s" % [a.name for a in p.applicable_actions(I)])


def test_d2_negative_preconditions():
    header("Test D2 -- negative preconditions are actually enforced")
    p = warehouse()
    pickup_a = _find(p, "PickUp(Package,A)")
    holding = make_state("At(Robot,A)", "At(Package,A)", "Holding(Package)")
    check("D5 PickUp is blocked while already Holding(Package)",
          not pickup_a.applicable(holding))
    check("D6 the block is attributed to the negative precondition",
          "forbidden Holding(Package)" in pickup_a.why_inapplicable(holding),
          pickup_a.why_inapplicable(holding))


# ---------------------------------------------------------------------------
# Test E -- the goal test is entailment, not equality
# ---------------------------------------------------------------------------

def test_e_goal_is_subset_not_equality():
    header("Test E -- goal test is entailment (subset), not state equality")
    p = warehouse()
    final = make_state("At(Package,C)", "At(Robot,C)")
    check("E1 a superset of G satisfies G", p.satisfies_goal(final))
    check("E2 G itself satisfies G", p.satisfies_goal(p.goal))
    check("E3 the final state is NOT equal to G (so == would have failed)",
          final != p.goal)


# ---------------------------------------------------------------------------
# Test F -- the handout's suggested action order is a trap
# ---------------------------------------------------------------------------

def test_f_handout_ordering_is_invalid():
    header("Test F -- the ordering hinted at in Task 1 is NOT a valid plan")
    p = warehouse()
    tempting = [_find(p, "Move(A,B)"),
                _find(p, "PickUp(Package,B)"),
                _find(p, "Move(B,C)"),
                _find(p, "Drop(Package,C)")]
    ok, lines = validate_plan(p, tempting)
    for line in lines:
        LOG.append("    " + line)
    check("F1 Move,PickUp,Move,Drop is rejected", not ok)
    check("F2 it is rejected at step 2 for a missing precondition",
          any("step 2" in ln and "NOT applicable" in ln for ln in lines))


# ---------------------------------------------------------------------------
# Test G -- effect application order
# ---------------------------------------------------------------------------

def test_g_effect_order():
    header("Test G -- delete-then-add ordering")
    a = Action(name="Refresh", pos_pre=["P"], pos_eff=["P", "Q"], neg_eff=["P"])
    out = a.apply(make_state("P"))
    LOG.append("    Refresh: add {P,Q}, del {P};  apply to {P} -> %s"
               % show_state(out))
    check("G1 a proposition in both add and delete survives (add wins)",
          "P" in out)
    check("G2 the other add-effect is present", "Q" in out)


# ---------------------------------------------------------------------------
# Test H -- trivial and degenerate problems
# ---------------------------------------------------------------------------

def test_h_degenerate():
    header("Test H -- degenerate problems")
    p = warehouse()
    already = Problem(initial=make_state("At(Robot,A)", "At(Package,C)"),
                      actions=p.actions,
                      goal=make_state("At(Package,C)"),
                      name="goal already true in I")
    r = bfs_plan(already)
    record(already, r)
    check("H1 a goal already true in I yields the empty plan",
          r.found and r.length == 0, "got %s" % r.length)

    empty = Problem(initial=make_state("At(Robot,A)"), actions=[],
                    goal=make_state("At(Package,C)"), name="no actions at all")
    r2 = bfs_plan(empty)
    check("H2 no actions and an unsatisfied goal yields no plan", not r2.found)


# ---------------------------------------------------------------------------
# Test I -- BFS returns a SHORTEST plan
# ---------------------------------------------------------------------------

def test_i_optimality():
    header("Test I -- BFS optimality, and DFS as a contrast")
    p = warehouse()
    rb = bfs_plan(p)
    rd = dfs_plan(p)
    LOG.append("    BFS plan (%d): %s"
               % (rb.length, " -> ".join(a.name for a in rb.plan)))
    LOG.append("    DFS plan (%d): %s"
               % (rd.length, " -> ".join(a.name for a in rd.plan)))
    okd, _ = validate_plan(p, rd.plan)
    check("I1 no plan shorter than 4 exists (exhaustive check)",
          _shortest_by_brute_force(p, limit=4) == 4)
    check("I2 BFS returns a shortest plan", rb.length == 4)
    check("I3 DFS also returns a *valid* plan", okd)
    check("I4 DFS's plan is no shorter than BFS's", rd.length >= rb.length)


# ---------------------------------------------------------------------------
# Test J -- the soundness defect: unrestricted Move
# ---------------------------------------------------------------------------

def test_j_unrestricted_move_is_unsound():
    header("Test J -- unrestricted Move produces a plan that is internally "
           "consistent but physically impossible")
    p = warehouse(connected_moves=False)
    r = bfs_plan(p)
    record(p, r)

    ok, _ = validate_plan(p, r.plan, r.states)
    check("J1 the planner returns a 3-action plan", r.length == 3,
          "got %s" % r.length)
    check("J2 every step of it satisfies its own preconditions", ok)
    check("J3 the plan uses Move(A,C)",
          any(a.name == "Move(A,C)" for a in r.plan))
    bad = [a.name for a in r.plan if _is_move(a) and _move_pair(a) not in CONNECTED]
    LOG.append("    moves not supported by the connectivity facts: %s" % bad)
    check("J4 an EXTERNAL connectivity check rejects it", bad == ["Move(A,C)"])
    LOG.append("    -> re-execution alone cannot catch this: the model itself"
               " is wrong,")
    LOG.append("       so the plan is valid with respect to it.  Only a check"
               " against an")
    LOG.append("       independent source of knowledge (Task 7's Prolog"
               " program) rejects it.")


# ---------------------------------------------------------------------------
# Test K -- the termination defect
# ---------------------------------------------------------------------------

def test_k_visited_set_is_required():
    header("Test K -- duplicate detection is required for termination")
    p = warehouse(with_pickup=False)          # unsolvable

    good = bfs_plan(p)
    check("K1 with duplicate detection: terminates and reports no plan",
          (not good.found) and good.expanded < 10000,
          "expanded %d" % good.expanded)
    LOG.append("    with visited set   : terminated after %d expansions"
               % good.expanded)

    looped = False
    try:
        bfs_plan_no_visited(p, max_expansions=20000)
    except RuntimeError:
        looped = True
    check("K2 without duplicate detection: does NOT terminate", looped)
    LOG.append("    without visited set: still expanding after 20000 states"
               " (2-cycle A<->B)")

    # ... and it still passes Test A, which is the whole problem.
    solvable = warehouse()
    r = bfs_plan_no_visited(solvable, max_expansions=20000)
    check("K3 the defective version still passes Test A",
          r.found and r.length == 4)
    LOG.append("    the defective version answers the SOLVABLE problem"
               " correctly (4 actions),")
    LOG.append("    which is exactly why Test A alone would not have found it.")


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _find(problem, name):
    for a in problem.actions:
        if a.name == name:
            return a
    raise KeyError(name)


def _is_move(action):
    return action.name.startswith("Move(")


def _move_pair(action):
    body = action.name[len("Move("):-1]
    x, y = body.split(",")
    return (x, y)


def _robot_can_reach_c(problem):
    """Independent reachability check over robot position only."""
    seen, frontier = {"A"}, ["A"]
    while frontier:
        loc = frontier.pop()
        for a in problem.actions:
            if _is_move(a) and _move_pair(a)[0] == loc:
                nxt = _move_pair(a)[1]
                if nxt not in seen:
                    seen.add(nxt)
                    frontier.append(nxt)
    return "C" in seen


def _shortest_by_brute_force(problem, limit):
    """Independent oracle: exhaustive depth-limited search, written without reference to
    bfs_plan.  Returns the shortest plan length up to `limit`, or None."""
    def rec(state, depth):
        if problem.satisfies_goal(state):
            return 0
        if depth == 0:
            return None
        best = None
        for a in problem.actions:
            if not a.applicable(state):
                continue
            sub = rec(a.apply(state), depth - 1)
            if sub is not None and (best is None or sub + 1 < best):
                best = sub + 1
        return best
    return rec(problem.initial, limit)


# ---------------------------------------------------------------------------

TESTS = [
    test_a_solvable,
    test_b_impossible_no_pickup,
    test_b2_impossible_no_drop,
    test_b3_impossible_unreachable_goal,
    test_c_irrelevant_actions,
    test_d_applicability_in_I,
    test_d2_negative_preconditions,
    test_e_goal_is_subset_not_equality,
    test_f_handout_ordering_is_invalid,
    test_g_effect_order,
    test_h_degenerate,
    test_i_optimality,
    test_j_unrestricted_move_is_unsound,
    test_k_visited_set_is_required,
]


def main():
    print("=" * 78)
    print("Task 3 -- testing the generated planner")
    print("=" * 78)
    for t in TESTS:
        t()
    for line in LOG:
        print(line)
    print("")
    print("=" * 78)
    print("%d checks passed, %d failed" % (PASS, FAIL))
    print("=" * 78)
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
