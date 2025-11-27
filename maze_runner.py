import pygame
import json
import heapq
from collections import deque
from time import perf_counter

WIDTH, HEIGHT = 1400, 700
GRID_COLS, GRID_ROWS = 30, 22
CELL_SIZE = 28

MARGIN_X = (WIDTH - GRID_COLS * CELL_SIZE) // 2
MARGIN_Y = (HEIGHT - GRID_ROWS * CELL_SIZE) // 2

FPS = 60
NPC_SPEED = 8

BG = (15, 16, 20)
GRID_LINE = (35, 38, 44)
WALL = (70, 74, 82)
START_C = (80, 200, 120)
GOAL_C = (220, 90, 90)
PATH_C = (255, 220, 120)
EXPLORED_C = (90, 130, 220)
NPC_C = (240, 240, 240)
TEXT_C = (220, 220, 220)
COST2_C = (160, 140, 60)

def in_bounds(x, y):
    return 0 <= x < GRID_COLS and 0 <= y < GRID_ROWS

def neighbors(pos, grid):
    x, y = pos
    dirs = [(1,0),(-1,0),(0,1),(0,-1)]
    out = []
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if in_bounds(nx, ny) and grid[ny][nx] != 1:
            out.append((nx, ny))
    return out

def manhattan(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

def reconstruct(came_from, start, goal):
    if goal not in came_from:
        return []
    cur = goal
    path = [cur]
    while cur != start:
        cur = came_from[cur]
        path.append(cur)
    path.reverse()
    return path

def compute_path_cost(grid, path):
    """
    Cost dihitung per langkah:
    - Masuk ke tile {0 atau lain} = 1
    - Masuk ke tile {2}          = 2
    Start tile dianggap cost 0.
    """
    if not path:
        return 0

    total = 0
    # mulai dari index 1, karena cost dibayar saat MASUK ke tile berikutnya
    for (x, y) in path[1:]:
        tile = grid[y][x]
        if tile == 2:
            total += 2
        else:
            total += 1
    return total


#metode
def bfs(grid, start, goal):
    t0 = perf_counter()
    q = deque([start])
    came = {start: None}
    explored = set([start])

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

def gbfs(grid, start, goal):
    t0 = perf_counter()
    pq = []
    heapq.heappush(pq, (manhattan(start, goal), start))
    came = {start: None}
    explored = set([start])

    while pq:
        _, cur = heapq.heappop(pq)
        if cur == goal:
            break
        for nb in neighbors(cur, grid):
            if nb not in came:
                came[nb] = cur
                explored.add(nb)
                heapq.heappush(pq, (manhattan(nb, goal), nb))

    path = reconstruct(came, start, goal)
    t1 = perf_counter()
    return path, explored, (t1 - t0) * 1000

def astar(grid, start, goal):
    t0 = perf_counter()
    pq = []
    heapq.heappush(pq, (0, start))
    came = {start: None}
    g = {start: 0}
    explored = set([start])

    while pq:
        _, cur = heapq.heappop(pq)
        if cur == goal:
            break

        for nb in neighbors(cur, grid):
            nx, ny = nb
            tile = grid[ny][nx]

            # cost dasar 1, cost2 jadi 2
            step_cost = 1
            if tile == 2:
                step_cost = 2

            ng = g[cur] + step_cost

            if nb not in g or ng < g[nb]:
                g[nb] = ng
                f = ng + manhattan(nb, goal)
                came[nb] = cur
                explored.add(nb)
                heapq.heappush(pq, (f, nb))

    path = reconstruct(came, start, goal)
    t1 = perf_counter()
    return path, explored, (t1 - t0) * 1000


def save_level(grid, start, goal, filename="level.json"):
    data = {
        "cols": GRID_COLS,
        "rows": GRID_ROWS,
        "grid": grid,
        "start": start,
        "goal": goal,
    }
    with open(filename, "w") as f:
        json.dump(data, f)
    print("Saved:", filename)

def load_level(filename="level.json"):
    with open(filename, "r") as f:
        data = json.load(f)
    return data["grid"], tuple(data["start"]), tuple(data["goal"])

STAGE_FILES = ["stage1.json", "stage2.json", "stage3.json"]
current_stage = 0      # index stage aktif (0 = stage1, 1 = stage2, 2 = stage3)

LOCK_WALLS = False     # kalau nanti mau freeze tembok, ganti ke True

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Maze Runner AI - BFS vs GBFS vs A*")
clock = pygame.time.Clock()
font = pygame.font.SysFont("consolas", 18)

grid = [[0 for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
start = (2, 2)
goal = (GRID_COLS-3, GRID_ROWS-3)

path = []
explored = set()
last_algo = "-"
last_time_ms = 0.0
last_cost = 0

mode = "wall"

npc_path_index = 0
npc_tick_accum = 0.0
npc_pos = start
mouse_down = False      # lagi tahan klik kiri atau nggak
paint_value = None      # True = isi wall (1), False = hapus wall (0)

def load_stage(index):
    global grid, start, goal, current_stage
    global path, explored, npc_pos, npc_path_index, npc_tick_accum, last_algo, last_time_ms, last_cost

    current_stage = index

    try:
        grid_loaded, s_loaded, g_loaded = load_level(STAGE_FILES[index])
        grid = grid_loaded
        start = tuple(s_loaded)
        goal = tuple(g_loaded)
        print(f"Loaded {STAGE_FILES[index]}")
    except FileNotFoundError:
        print(f"{STAGE_FILES[index]} belum ada, pakai grid kosong dulu.")
        grid = [[0 for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
        start = (2, 2)
        goal = (GRID_COLS-3, GRID_ROWS-3)

    # reset state pathfinding + NPC
    path.clear()
    explored.clear()
    npc_pos = start
    npc_path_index = 0
    npc_tick_accum = 0.0
    last_algo = "-"
    last_time_ms = 0.0
    last_cost = 0



def grid_to_screen(x, y):
    return (MARGIN_X + x * CELL_SIZE, MARGIN_Y + y * CELL_SIZE)

def draw():
    screen.fill(BG)

    for y in range(GRID_ROWS):
        for x in range(GRID_COLS):
            rect = pygame.Rect(
                MARGIN_X + x * CELL_SIZE,
                MARGIN_Y + y * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE
            )

            val = grid[y][x]

            if val == 1:
                base_color = WALL
            elif val == 2:
                base_color = COST2_C
            else:
                base_color = (22, 24, 30)

            # kalau sudah dieksplor, warnai explored (biar kelihatan)
            if (x, y) in explored:
                base_color = EXPLORED_C

            pygame.draw.rect(screen, base_color, rect)
            pygame.draw.rect(screen, GRID_LINE, rect, 1)

    for (px, py) in path:
        rect = pygame.Rect(*grid_to_screen(px, py), CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, PATH_C, rect)

    sx, sy = start
    gx, gy = goal
    pygame.draw.rect(screen, START_C, pygame.Rect(*grid_to_screen(sx, sy), CELL_SIZE, CELL_SIZE))
    pygame.draw.rect(screen, GOAL_C, pygame.Rect(*grid_to_screen(gx, gy), CELL_SIZE, CELL_SIZE))

    nx, ny = npc_pos
    npc_rect = pygame.Rect(*grid_to_screen(nx, ny), CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(screen, NPC_C, npc_rect, border_radius=6)

    info_lines = [
        f"Stage: {current_stage+1} (F1/F2/F3, TAB next)",
        f"Mode: {mode.upper()} | Click to edit",
        f"[S] + Click = Start",
        f"[G] + Click = Goal",
        f"Click = Toggle Wall/Cost2",
        f"",
        f"W = Wall mode",
        f"H = Cost2 mode",
        f"",
        f"Run:",
        f"1 = BFS | 2 = GBFS | 3 = A*",
        f"R = Reset path",
        f"C = Clear walls",
        f"",
        f"CTRL+S Save | CTRL+L Load",
        f"",
        f"Algo: {last_algo}",
        f"Time: {last_time_ms:.4f} ms",
        f"Path length: {len(path)}",
        f"Path cost: {last_cost}",
        f"Explored: {len(explored)}"
    ]
    y0 = 8
    for line in info_lines:
        surf = font.render(line, True, TEXT_C)
        screen.blit(surf, (8, y0))
        y0 += 20

    pygame.display.flip()

def run_algo(which):
    global path, explored, last_algo, last_time_ms, last_cost, npc_pos, npc_path_index, npc_tick_accum

    explored.clear()
    path.clear()
    npc_pos = start

    npc_path_index = 0
    npc_tick_accum = 0.0

    if which == "BFS":
        p, ex, t = bfs(grid, start, goal)
    elif which == "GBFS":
        p, ex, t = gbfs(grid, start, goal)
    else:
        p, ex, t = astar(grid, start, goal)

    path[:] = p
    explored |= ex
    last_algo = which
    last_time_ms = t

    # hitung total cost berdasarkan grid saat ini
    last_cost = compute_path_cost(grid, path)

def handle_mouse(pos, paint_on=None):
    global grid, start, goal, npc_pos
    mx, my = pos
    gx = (mx - MARGIN_X) // CELL_SIZE
    gy = (my - MARGIN_Y) // CELL_SIZE
    if not in_bounds(gx, gy):
        return

    cell = (gx, gy)

    if mode == "start":
        if cell != goal and grid[gy][gx] != 1:
            start = cell
            npc_pos = start

    elif mode == "goal":
        if cell != start and grid[gy][gx] != 1:
            goal = cell

    elif mode == "wall":
        if not LOCK_WALLS and cell != start and cell != goal:
            if paint_on is None:
                # toggle 0 <-> 1
                grid[gy][gx] = 0 if grid[gy][gx] == 1 else 1
            else:
                grid[gy][gx] = 1 if paint_on else 0

    elif mode == "cost":
        # tile cost 2 (gunung), tidak tergantung LOCK_WALLS atau bisa kamu ikutkan juga kalau mau lock full map
        if cell != start and cell != goal:
            if paint_on is None:
                # toggle 0 <-> 2
                grid[gy][gx] = 0 if grid[gy][gx] == 2 else 2
            else:
                grid[gy][gx] = 2 if paint_on else 0



load_stage(0)  # mulai dari stage 1

running = True
while running:
    dt = clock.tick(FPS) / 1000.0

    keys = pygame.key.get_pressed()
    ctrl_down = keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                run_algo("BFS")
            elif event.key == pygame.K_2:
                run_algo("GBFS")
            elif event.key == pygame.K_3:
                run_algo("A*")

            elif event.key == pygame.K_r:
                path.clear()
                explored.clear()
                npc_pos = start
                npc_path_index = 0
                npc_tick_accum = 0.0
                last_cost = 0

            elif event.key == pygame.K_c:
                for y in range(GRID_ROWS):
                    for x in range(GRID_COLS):
                        grid[y][x] = 0
                path.clear()
                explored.clear()
                npc_pos = start
                npc_path_index = 0
                npc_tick_accum = 0.0
                last_cost = 0

            elif event.key == pygame.K_s and ctrl_down:
                save_level(grid, start, goal, STAGE_FILES[current_stage])
                print(f"Saved {STAGE_FILES[current_stage]}")
                

            elif event.key == pygame.K_l and ctrl_down:
                load_stage(current_stage)

            elif event.key == pygame.K_s:
                mode = "start"
            elif event.key == pygame.K_g:
                mode = "goal"
            elif event.key == pygame.K_w:
                mode = "wall"
            elif event.key == pygame.K_h:
                mode = "cost"   # mode terrain cost=2

            # ==== GANTI STAGE (KEYBIND) ====
            elif event.key == pygame.K_F1:
                load_stage(0)  # Stage 1
            elif event.key == pygame.K_F2:
                load_stage(1)  # Stage 2
            elif event.key == pygame.K_F3:
                load_stage(2)  # Stage 3
            elif event.key == pygame.K_TAB:
                # next stage (cycle)
                next_index = (current_stage + 1) % len(STAGE_FILES)
                load_stage(next_index)

        elif event.type == pygame.KEYUP:
            if event.key in (pygame.K_s, pygame.K_g):
                mode = "wall"

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                mouse_down = False
                paint_value = None

        elif event.type == pygame.MOUSEMOTION:
            # drag untuk mode wall / cost saja
            if mouse_down and mode in ("wall", "cost") and event.buttons[0]:
                handle_mouse(event.pos, paint_on=paint_value)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_down = True

                local_paint = None  # default toggle (klik sekali)

                mx, my = event.pos
                gx = (mx - MARGIN_X) // CELL_SIZE
                gy = (my - MARGIN_Y) // CELL_SIZE

                if in_bounds(gx, gy):
                    if mode == "wall":
                        if not LOCK_WALLS and (gx, gy) != start and (gx, gy) != goal:
                            # kalau sekarang kosong → drag = gambar wall
                            # kalau sekarang wall → drag = hapus wall
                            local_paint = (grid[gy][gx] == 0)

                    elif mode == "cost":
                        if (gx, gy) != start and (gx, gy) != goal:
                            # kalau sekarang cost2 → drag = hapus (jadi 0)
                            # kalau sekarang bukan cost2 → drag = jadikan cost2
                            local_paint = (grid[gy][gx] != 2)

                paint_value = local_paint
                handle_mouse(event.pos, paint_on=paint_value)


    if path:
        npc_tick_accum += dt
        step_time = 1.0 / NPC_SPEED
        while npc_tick_accum >= step_time and npc_path_index < len(path):
            npc_pos = path[npc_path_index]
            npc_path_index += 1
            npc_tick_accum -= step_time

    draw()

pygame.quit()