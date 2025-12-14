"""Pathfinding logic for Maze Runner.

Kept in a separate module to make maintenance easier.

Grid encoding (as used by the main game):
  0 = empty (cost 1)
  1 = wall (blocked)
  2 = cost2 tile (cost 2)
  3 = locked wall (blocked)
"""

from __future__ import annotations

import heapq
from collections import deque
from time import perf_counter
from typing import Dict, List, Set, Tuple

Pos = Tuple[int, int]
Grid = List[List[int]]


def _in_bounds(x: int, y: int, grid: Grid) -> bool:
    return 0 <= y < len(grid) and 0 <= x < len(grid[0])


def neighbors(pos: Pos, grid: Grid) -> List[Pos]:
    """4-neighborhood (no diagonals). Blocks on tiles 1 and 3."""
    x, y = pos
    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    out: List[Pos] = []
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if _in_bounds(nx, ny, grid) and grid[ny][nx] not in (1, 3):
            out.append((nx, ny))
    return out


def manhattan(a: Pos, b: Pos) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def reconstruct(came_from: Dict[Pos, Pos | None], start: Pos, goal: Pos) -> List[Pos]:
    if goal not in came_from:
        return []
    cur: Pos = goal
    path: List[Pos] = [cur]
    while cur != start:
        parent = came_from.get(cur)
        if parent is None:
            # Shouldn't happen if there's a valid chain back to start.
            return []
        cur = parent
        path.append(cur)
    path.reverse()
    return path


def step_cost(grid: Grid, to_pos: Pos) -> int:
    x, y = to_pos
    return 2 if grid[y][x] == 2 else 1


def compute_path_cost(grid: Grid, path: List[Pos]) -> int:
    """Total cost along the path, ignoring the start tile (same as the UI).

    Empty tiles cost 1, 'cost2' tiles cost 2.
    """
    if not path:
        return 0
    total = 0
    for pos in path[1:]:
        total += step_cost(grid, pos)
    return total


def bfs(grid: Grid, start: Pos, goal: Pos):
    """Breadth First Search (unweighted shortest path by steps)."""
    t0 = perf_counter()
    q = deque([start])
    came: Dict[Pos, Pos | None] = {start: None}
    explored: Set[Pos] = {start}

    while q:
        cur = q.popleft()
        if cur == goal:
            break
        for nb in neighbors(cur, grid):
            if nb not in came:
                came[nb] = cur
                explored.add(nb)
                q.append(nb)

    path = reconstruct(came, start, goal)
    t1 = perf_counter()
    return path, explored, (t1 - t0) * 1000


def ucs(grid: Grid, start: Pos, goal: Pos):
    """Uniform Cost Search (Dijkstra) for weighted grids."""
    t0 = perf_counter()
    pq: List[Tuple[int, Pos]] = []
    heapq.heappush(pq, (0, start))

    came: Dict[Pos, Pos | None] = {start: None}
    cost_so_far: Dict[Pos, int] = {start: 0}
    explored: Set[Pos] = {start}

    while pq:
        cur_cost, cur = heapq.heappop(pq)

        # Skip stale queue entries.
        if cur_cost != cost_so_far.get(cur, cur_cost):
            continue

        if cur == goal:
            break

        for nb in neighbors(cur, grid):
            new_cost = cur_cost + step_cost(grid, nb)
            if nb not in cost_so_far or new_cost < cost_so_far[nb]:
                cost_so_far[nb] = new_cost
                came[nb] = cur
                explored.add(nb)
                heapq.heappush(pq, (new_cost, nb))

    path = reconstruct(came, start, goal)
    t1 = perf_counter()
    return path, explored, (t1 - t0) * 1000


def astar(grid: Grid, start: Pos, goal: Pos):
    """A* Search (UCS + Manhattan heuristic)."""
    t0 = perf_counter()
    pq: List[Tuple[int, Pos]] = []
    heapq.heappush(pq, (0, start))
    came: Dict[Pos, Pos | None] = {start: None}
    g: Dict[Pos, int] = {start: 0}
    explored: Set[Pos] = {start}

    while pq:
        _, cur = heapq.heappop(pq)
        if cur == goal:
            break

        for nb in neighbors(cur, grid):
            ng = g[cur] + step_cost(grid, nb)
            if nb not in g or ng < g[nb]:
                g[nb] = ng
                f = ng + manhattan(nb, goal)
                came[nb] = cur
                explored.add(nb)
                heapq.heappush(pq, (f, nb))

    path = reconstruct(came, start, goal)
    t1 = perf_counter()
    return path, explored, (t1 - t0) * 1000
