"""
Locked-door navigation: a second planning domain.

CS F407 -- Logical Reasoning for Planning, Section 4 (lab of 28 Oct 2026).

The robot starts in room A, where a key lies.  The door between B and C is
locked.  Goal: reach C.  The planner is the same idea as for the warehouse --
logic decides which actions are applicable, BFS decides which ones to try --
only the problem description is new.

Standard library only.  Run:  python locked_door.py
"""

from collections import deque


# ----------------------------------------------------------------------------
# The planner (works for any problem)
# ----------------------------------------------------------------------------
#
# A state is a frozenset of the propositions that are TRUE.  Anything absent is
# false, so "the door is locked" is simply: Unlocked is not in the state.


class Action:
    def __init__(self, name, pre, add=(), delete=()):
        self.name = name
        self.pre = frozenset(pre)
        self.add = frozenset(add)
        self.delete = frozenset(delete)

    def applicable(self, state):
        """S |= Pre(a): every precondition is true in the state."""
        return self.pre <= state

    def apply(self, state):
        """S' = (S - Delete) | Add."""
        return (state - self.delete) | self.add


def bfs(initial, goal, actions):
    """Return the shortest list of actions that reaches the goal, or None."""
    frontier = deque([(initial, [])])
    visited = {initial}            # without this, Move(A,B)/Move(B,A) loops forever
    while frontier:
        state, plan = frontier.popleft()
        if goal <= state:          # the goal is contained in the state, not equal to it
            return plan
        for action in actions:
            if action.applicable(state):
                successor = action.apply(state)
                if successor not in visited:
                    visited.add(successor)
                    frontier.append((successor, plan + [action]))
    return None


def run(initial, goal, plan):
    """Execute a plan step by step, printing every state.  True if it reaches the goal."""
    state = initial
    print(f"    S0 = {show(state)}")
    for i, action in enumerate(plan, 1):
        if not action.applicable(state):
            missing = ", ".join(sorted(action.pre - state))
            print(f"    step {i}: {action.name} FAILS -- missing {missing}")
            return False
        state = action.apply(state)
        print(f"    S{i} = {show(state)}   after {action.name}")
    if goal <= state:
        print(f"    goal {show(goal)} reached -- VALID")
        return True
    print(f"    goal {show(goal)} not reached -- FAILS")
    return False


def show(state):
    return "{" + ", ".join(sorted(state)) + "}"


def names(plan):
    return " -> ".join(a.name for a in plan)


# ----------------------------------------------------------------------------
# The problem description (the only part that differs from the warehouse)
# ----------------------------------------------------------------------------

I = frozenset({"At(A)", "KeyAt(A)"})
G = frozenset({"At(C)"})

ACTIONS = [
    Action("Move(A,B)", pre={"At(A)"},             delete={"At(A)"},    add={"At(B)"}),
    Action("Move(B,A)", pre={"At(B)"},             delete={"At(B)"},    add={"At(A)"}),
    Action("PickKey",   pre={"At(A)", "KeyAt(A)"}, delete={"KeyAt(A)"}, add={"HasKey"}),
    Action("Unlock",    pre={"At(B)", "HasKey"},                        add={"Unlocked"}),
    Action("Move(B,C)", pre={"At(B)", "Unlocked"}, delete={"At(B)"},    add={"At(C)"}),
    Action("Move(C,B)", pre={"At(C)", "Unlocked"}, delete={"At(C)"},    add={"At(B)"}),
]
ACT = {a.name: a for a in ACTIONS}


# ----------------------------------------------------------------------------
# Solve it, then check the failing conditions
# ----------------------------------------------------------------------------


def main():
    print("Applicable in I:", ", ".join(a.name for a in ACTIONS if a.applicable(I)))

    print("\n1. The plan BFS finds")
    plan = bfs(I, G, ACTIONS)
    print("   ", names(plan))
    assert run(I, G, plan) and len(plan) == 4

    print("\n2. Failing condition: no key, go A -> B -> C")
    assert not run(I, G, [ACT["Move(A,B)"], ACT["Move(B,C)"]])

    print("\n3. Leave one action out of the plan -- every one is needed")
    for skipped in plan:
        print(f"  without {skipped.name}:")
        assert not run(I, G, [a for a in plan if a is not skipped])

    print("\n4. Remove an action from the problem -- BFS finds no plan")
    for name in ("PickKey", "Unlock"):
        result = bfs(I, G, [a for a in ACTIONS if a.name != name])
        print(f"  without {name}: {'No plan found' if result is None else names(result)}")
        assert result is None

    print("\nAll checks passed.")


if __name__ == "__main__":
    main()
