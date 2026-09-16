"""
Tasks 6, 7 and 8 -- the Prolog session, executed.

Runs every query the handout asks for against the real `planner.pl` and
`reasoning.pl`, then closes the loop the laboratory is actually about:

    the Python planner GENERATES a plan
    -> the plan is translated into a Prolog goal
    -> Prolog VERIFIES it against knowledge the planner never saw

The Python side (planner.py) and the Prolog side (planner.pl) share no code
and no data.  The connectivity of the warehouse is written down twice, once in
each, and the verifier's job is to disagree when they differ.

Run:  python run_prolog.py            (or  python run_prolog.py > prolog_session.txt)
"""

import os
from prolog_engine import Database, ask, query
import planner


def banner(title):
    print("=" * 78)
    print(title)
    print("=" * 78)
    print("")


def section(title):
    print("-" * 78)
    print(title)
    print("-" * 78)
    print("")


# ---------------------------------------------------------------------------

def task6(db):
    section("Task 6 -- Prolog as a plan verifier: can_move/2")
    print("Knowledge base (planner.pl):")
    print("    connected(a,b).  connected(b,a).  connected(b,c).  connected(c,b).")
    print("    can_move(X,Y) :- connected(X,Y).")
    print("")

    ask(db, "can_move(a,b).", expect=True,
        note="one resolution step: can_move(a,b) reduces to connected(a,b), "
             "which is a fact.")
    ask(db, "can_move(a,c).", expect=False,
        note="there is no fact connected(a,c) and the rule is not recursive, "
             "so the goal\n   is not derivable.  Under the closed-world "
             "assumption Prolog answers false.")
    ask(db, "can_move(b,X).", expect=True,
        note="the same rule run 'backwards' -- Prolog enumerates every "
             "destination.")
    ask(db, "connected(a,c).", expect=False,
        note="the missing fact itself.")


def task6_reachability(db):
    section("Task 6 (extension) -- one move vs. reachability")
    print("can_move/2 is a SINGLE step and is deliberately not transitive.")
    print("reachable/2 is its transitive closure and needs recursion.")
    print("")
    ask(db, "can_move(a,c).", expect=False,
        note="a and c are not adjacent ...")
    ask(db, "reachable(a,c).", expect=True,
        note="... but c IS reachable from a, via b.  These are different "
             "questions,\n   and conflating them is exactly the error the "
             "Python planner made.")


def task7(db):
    section("Task 7 -- checking proposed actions: valid_move/2")
    print("Suppose the Python planner proposes  Move(a,b), Move(b,c).")
    print("")
    ask(db, "valid_move(a,b).", expect=True)
    ask(db, "valid_move(b,c).", expect=True)
    ask(db, "valid_move(a,c).", expect=False,
        note="the Challenge in the handout: Move(a,c) is NOT supported by the "
             "warehouse\n   knowledge, so the proposed action is rejected.")


def task8(reasoning_db):
    section("Task 8 -- Prolog and logical reasoning")
    print("Knowledge base (reasoning.pl):")
    print("    wet_road.")
    print("    slippery     :- wet_road.")
    print("    reduce_speed :- slippery.")
    print("")
    ask(reasoning_db, "reduce_speed.", expect=True)
    print("   The corresponding classical derivation:")
    print("")
    print("       WetRoad                                  (fact)")
    print("       WetRoad  -> Slippery                      (rule)")
    print("       ------------------------------- modus ponens")
    print("       Slippery")
    print("       Slippery -> ReduceSpeed                   (rule)")
    print("       ------------------------------- modus ponens")
    print("       ReduceSpeed")
    print("")
    print("       i.e.   WetRoad => Slippery => ReduceSpeed.")
    print("")
    print("   Prolog travels the chain in the opposite direction: it reduces")
    print("   the GOAL reduce_speed to slippery, then to wet_road, then finds")
    print("   wet_road as a fact.  Forward proof, backward search, same theorem.")
    print("")

    ask(reasoning_db, "animal(polly).", expect=True,
        note="Penguin(Polly) => Bird(Polly) => Animal(Polly).")
    ask(reasoning_db, "animal(rex).", expect=False,
        note="not 'rex is provably not an animal' but 'rex is not provably an "
             "animal'.\n   Prolog reports failure to prove as falsity: "
             "the closed-world assumption.")


# ---------------------------------------------------------------------------
# The generate -> verify loop
# ---------------------------------------------------------------------------

def plan_to_route_goal(result):
    """Translate the Move actions of a Python plan into a Prolog goal."""
    moves = []
    for action in result.plan:
        if action.name.startswith("Move("):
            x, y = action.name[len("Move("):-1].split(",")
            moves.append("move(%s,%s)" % (x.lower(), y.lower()))
    start = "a"      # the robot starts at A in every problem here
    return "valid_route(%s, [%s])." % (start, ",".join(moves)), moves


def verification_loop(db):
    section("Generate -> independent verification")

    for label, problem in [
        ("the corrected planner", planner.warehouse()),
        ("the defective planner (Move over every pair of locations)",
         planner.warehouse(connected_moves=False)),
    ]:
        result = planner.bfs_plan(problem)
        ok_python, _ = planner.validate_plan(problem, result.plan, result.states)
        goal, moves = plan_to_route_goal(result)

        print("%s" % label)
        print("    Python plan            : %s"
              % " -> ".join(a.name for a in result.plan))
        print("    Python self-validation : %s"
              % ("VALID" if ok_python else "INVALID"))
        print("    translated Prolog goal : %s" % goal)
        ok_prolog, _ = query(db, goal)
        print("    Prolog answer          : %s"
              % ("true." if ok_prolog else "false."))
        if ok_python and not ok_prolog:
            print("    >>> DISAGREEMENT.  Python says the plan is consistent with "
                  "its own")
            print("        action model; Prolog says the action model itself is "
                  "not consistent")
            print("        with the warehouse.  The verifier is right and the "
                  "planner is wrong.")
            for m in moves:
                x, y = m[len("move("):-1].split(",")
                sub, _ = query(db, "valid_move(%s,%s)." % (x, y))
                print("            valid_move(%s,%s) -> %s"
                      % (x, y, "true" if sub else "FALSE  <-- unsupported"))
        elif ok_python and ok_prolog:
            print("    >>> AGREEMENT.  Both the executed transitions and the "
                  "independent")
            print("        knowledge base accept this plan.")
        print("")


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    db = Database.consult(os.path.join(here, "planner.pl"))
    reasoning_db = Database.consult(os.path.join(here, "reasoning.pl"))

    banner("Optional Extension -- Prolog as a Logical Verifier\n"
           "(executed by prolog_engine.py; planner.pl and reasoning.pl are\n"
           "standard Prolog and load unchanged in SWI-Prolog)")

    task6(db)
    task6_reachability(db)
    task7(db)
    verification_loop(db)
    task8(reasoning_db)

    section("Summary")
    print("An AI system can generate a candidate solution,")
    print("while a separate logical system checks it.")
    print("")
    print("The two must not share the knowledge being checked.  Here the")
    print("connectivity of the warehouse is written down twice -- as Python")
    print("action instances and as Prolog facts -- and the verifier earns its")
    print("keep precisely at the point where the two copies disagree.")


if __name__ == "__main__":
    main()
