# Agents: Laboratory Report

**Course:** CS F407 Artificial Intelligence

**Name:** Darshan Prakash Rajagoli

**Topic:** Constructing a goal-based warehouse agent

## 1. Understanding the problem (Task 1)

**1. What is the environment?**

A static warehouse represented by a 7-row, 21-column grid. `#` is a shelf or
wall, `.` is free space, `S` is the start and `G` is the destination. The whole
map is available before planning begins.

```text
#####################
#S....#............G#
#.##....##########..#
#....##.............#
#.######.###.#.###..#
#........#..........#
#####################
```

**2. What is the goal?**

Find a collision-free path from `S` to `G`. In zero-based `(row, column)`
coordinates, the start is `(1, 1)` and the goal is `(1, 19)`.

**3. What actions are available?**

Up, Down, Left and Right, each moving one square. A move is allowed only if
the next square is inside the grid and is not a wall. Each move costs one.

**4. What information must the agent maintain?**

The map, current position, destination, positions waiting to be explored,
and visited positions. A parent pointer for each discovered position lets
the agent reconstruct the path. Position alone is enough to describe a state
because shelves do not move and no other resource changes.

**5. Why is it goal-based rather than a simple reflex agent?**

It uses an explicit destination and searches through possible future moves
before selecting a route. A simple reflex agent chooses an action from the
current percept using fixed condition-action rules, without this search for
a route to the destination.

### Think About It: a warehouse twice as large

BFS still finds a shortest path when all moves cost one, but it must store and
explore more positions. Its time and memory are O(V + E) and O(V), respectively,
where V is the number of reachable cells and E is the number of legal moves.
On this four-direction grid, E is at most 4V, so both are O(V).
If the number of cells doubles, the worst-case work and memory grow roughly
with that number; if both dimensions double, the number of cells quadruples.
The actual effort also depends on obstacles and the destination.
For much larger maps, A* with Manhattan distance can reduce exploration while
preserving shortest paths. Moving obstacles would additionally require updated
map information and replanning; a bigger static map alone does not require that.

## 2. Designing the agent (Task 2)

| Component | Design |
|---|---|
| Environment | The supplied warehouse grid |
| Current state | Robot position `(row, column)` |
| Goal | Position equals the cell marked `G` |
| Available actions | Legal Up, Down, Left and Right moves |
| Decision-making component | Breadth-first search (BFS) |
| Output | A path and action sequence, or a no-path message |

```text
Warehouse map + start + goal
             |
             v
     BFS decision component <--- visited positions + parent pointers
             |
             v
    Check legal neighbouring cells
             |
             v
   Goal reached? -- no --> add unseen cells to queue --> continue BFS
        |
       yes
        v
 Reconstruct path --> movement actions --> destination

If the queue becomes empty first: report that no path exists.
```

The program plans the complete route before movement. It prints the planned
actions; it does not control a physical robot.

## 3. Implementation and algorithm

The complete program is [agents.py](agents.py). It uses only Python's standard
library and runs independently of the Search lab.

1. Read the map and locate its single start and goal.
2. Put the start in a FIFO queue and mark it visited.
3. Remove the oldest position. If it is the goal, reconstruct the path.
4. Otherwise, enqueue its legal, unvisited neighbours and record their parents.
5. Repeat until a path is found or the queue becomes empty.

**Which search algorithm is used, and why is it appropriate?**

BFS explores paths in increasing number of moves. Since every move costs one,
it finds a shortest path. The visited record prevents cycles and ensures the
search terminates even if no path exists. No heuristic is needed for this small
map. The program prints coordinates, named actions and a map with `*` along the
route; if the destination is unreachable, it prints a clear failure message.

## 4. Execution and correctness

From this folder:

```bash
python agents.py
python test_agents.py
```

The complete captured outputs are in [results.txt](results.txt) and
[test_results.txt](test_results.txt).

**Result on the handout map:** a valid path of **20 moves** from `(1, 1)` to
`(1, 19)`.

```text
#####################
#S***.#************G#
#.##****##########..#
#....##.............#
#.######.###.#.###..#
#........#..........#
#####################
```

**Why 20 is optimal:** reaching column 19 from column 1 requires at least
18 horizontal moves. The wall at `(1, 6)` prevents staying on row 1, so at least
one downward and one upward move are necessary. Every solution therefore needs
at least 20 moves. The returned path achieves that bound.

| Check | Result |
|---|---|
| Exact handout map | Correct endpoints, legal steps, no walls, 20 moves |
| Independent shortest-distance calculation | Repeated distance relaxation agrees with BFS |
| Blocked destination (`S#G`) | Returns no path |
| Open map without border walls (`S.G`) | Two Right moves; no out-of-bounds movement |
| Start already equals goal | One-position path, zero moves |
| Empty, ragged, missing/duplicate marker or invalid-character maps | Rejected with a clear error |

All five automated test methods pass. The first method checks the handout path,
its displayed markers and its optimal length; the invalid-map method checks
seven malformed inputs. No extra package installation is needed.
