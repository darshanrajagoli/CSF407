"""Goal-based warehouse agent. Run: python agents.py (standard library only)."""
from collections import deque

WAREHOUSE = """#####################
#S....#............G#
#.##....##########..#
#....##.............#
#.######.###.#.###..#
#........#..........#
#####################"""

MOVES = [(-1, 0, "Up"), (1, 0, "Down"), (0, -1, "Left"), (0, 1, "Right")]


def parse_map(text):
    """Read a rectangular map with exactly one start and one goal."""
    grid = text.splitlines()
    if not grid or not grid[0] or any(len(row) != len(grid[0]) for row in grid):
        raise ValueError("Map must be a nonempty rectangle.")
    if any(cell not in "#.SG" for row in grid for cell in row):
        raise ValueError("Use only #, ., S and G.")
    starts = [(r, c) for r, row in enumerate(grid) for c, cell in enumerate(row) if cell == "S"]
    goals = [(r, c) for r, row in enumerate(grid) for c, cell in enumerate(row) if cell == "G"]
    if len(starts) != 1 or len(goals) != 1:
        raise ValueError("Map needs exactly one S and one G.")
    return grid, starts[0], goals[0]


def bfs(grid, start, goal):
    """Find a shortest path; return None when the goal is unreachable.

    BFS explores positions in increasing number of moves. Every move costs
    one, so the first goal removed from the queue has a shortest path.
    The parent dictionary also records visited positions, preventing loops.
    """
    queue = deque([start])
    parent = {start: None}
    while queue:
        current = queue.popleft()
        if current == goal:
            path = []
            while current is not None:
                path.append(current)
                current = parent[current]
            return path[::-1]
        r, c = current
        for dr, dc, _ in MOVES:
            nr, nc = r + dr, c + dc
            nxt = (nr, nc)
            if (0 <= nr < len(grid) and 0 <= nc < len(grid[nr])
                    and grid[nr][nc] != "#" and nxt not in parent):
                parent[nxt] = current
                queue.append(nxt)
    return None


def actions(path):
    names = {(dr, dc): name for dr, dc, name in MOVES}
    return [names[(b[0] - a[0], b[1] - a[1])] for a, b in zip(path, path[1:])]


def display_path(grid, path):
    marked = [list(row) for row in grid]
    for r, c in path:
        if marked[r][c] not in "SG":
            marked[r][c] = "*"
    return "\n".join("".join(row) for row in marked)


def main():
    grid, start, goal = parse_map(WAREHOUSE)
    print("Goal-based warehouse agent")
    print("BFS finds a shortest path because all moves cost one.")
    print(f"Start: {start}; goal: {goal} (zero-based row, column)")
    path = bfs(grid, start, goal)
    if path is None:
        print("No collision-free path exists.")
        return
    print(f"Moves: {len(path) - 1}")
    print("Path:", " -> ".join(map(str, path)))
    print("Actions:", " -> ".join(actions(path)))
    print(display_path(grid, path))


if __name__ == "__main__":
    main()
