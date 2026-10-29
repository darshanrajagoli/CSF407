"""Checks for the handout map and cases that can expose search errors."""
import unittest
from agents import WAREHOUSE, parse_map, bfs, actions, display_path


class AgentTests(unittest.TestCase):
    def test_handout_map(self):
        grid, start, goal = parse_map(WAREHOUSE)
        path = bfs(grid, start, goal)
        self.assertIsNotNone(path)
        self.assertEqual(path[0], start)
        self.assertEqual(path[-1], goal)
        self.assertEqual(start, (1, 1))
        self.assertEqual(goal, (1, 19))
        # At least 18 horizontal moves are needed. The wall on row 1
        # forces at least one move down and one up: lower bound 20.
        # A valid 20-move path therefore proves optimality on this map.
        self.assertEqual(len(path)-1, 20)
        for a, b in zip(path, path[1:]):
            self.assertEqual(abs(a[0]-b[0]) + abs(a[1]-b[1]), 1)
            self.assertNotEqual(grid[b[0]][b[1]], "#")
        self.assertEqual(len(actions(path)), len(path)-1)
        shown = display_path(grid, path)
        self.assertIn("S", shown)
        self.assertIn("G", shown)
        # Independent repeated relaxation, without a BFS queue.
        distance = {start: 0}
        cells = [(r,c) for r,row in enumerate(grid) for c,ch in enumerate(row) if ch != "#"]
        for _ in cells:
            for r,c in cells:
                for nr,nc in ((r-1,c),(r+1,c),(r,c-1),(r,c+1)):
                    if (nr,nc) in distance:
                        distance[(r,c)] = min(distance.get((r,c), float("inf")), distance[(nr,nc)]+1)
        self.assertEqual(len(path)-1, distance[goal])

    def test_no_path(self):
        grid, start, goal = parse_map("S#G")
        self.assertIsNone(bfs(grid, start, goal))

    def test_open_boundary(self):
        grid, start, goal = parse_map("S.G")
        self.assertEqual(bfs(grid, start, goal), [(0,0),(0,1),(0,2)])
        self.assertEqual(actions(bfs(grid, start, goal)), ["Right", "Right"])

    def test_already_at_goal(self):
        self.assertEqual(bfs(["."], (0,0), (0,0)), [(0,0)])

    def test_invalid_maps(self):
        for text in ("", "S", "G", "SSG", "SGG", "S.\nG", "S?G"):
            with self.subTest(text=text):
                with self.assertRaises(ValueError):
                    parse_map(text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
