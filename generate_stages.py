import json

GRID_COLS, GRID_ROWS = 30, 22

def new_grid():
    return [[0 for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]

def gen_stage2():
    g = new_grid()

    midx = GRID_COLS // 2 

    for y in range(2, GRID_ROWS - 2):
        g[y][midx] = 3
    for y in (4, 10, 16):
        g[y][midx] = 0
    for x in range(2, midx - 1):
        g[3][x] = 3
    for x in range(midx + 2, GRID_COLS - 2):
        g[5][x] = 3
    for x in range(2, midx - 3):
        g[9][x] = 3
    for x in range(midx + 3, GRID_COLS - 2):
        g[11][x] = 3
    for x in range(2, midx - 2):
        g[15][x] = 3
    for x in range(midx + 2, GRID_COLS - 3):
        g[17][x] = 3

    start = [2, 2]
    goal = [GRID_COLS - 3, GRID_ROWS - 3]

    return {
        "cols": GRID_COLS,
        "rows": GRID_ROWS,
        "grid": g,
        "start": start,
        "goal": goal,
    }

def gen_stage3():
    g = new_grid()

    def rect_lock(x1, y1, x2, y2):
        for y in range(y1, y2 + 1):
            for x in range(x1, x2 + 1):
                g[y][x] = 3

    rect_lock(10, 6, 19, 9)
    rect_lock(10, 12, 19, 15) 
    rect_lock(3, 3, 6, 7)
    rect_lock(3, 14, 7, 18)
    rect_lock(22, 3, 26, 7)
    rect_lock(22, 13, 27, 18)

    for y in range(0, GRID_ROWS):
        g[y][9] = 0

    for y in range(0, GRID_ROWS):
        g[y][20] = 0

    for x in range(0, GRID_COLS):
        g[11][x] = 0

    g[6][9]  = 0
    g[8][9]  = 0
    g[13][9] = 0
    g[15][9] = 0

    g[7][20]  = 0
    g[9][20]  = 0
    g[13][20] = 0

    for x in range(11, 19):
        g[7][x]  = 0
        g[14][x] = 0

    start = [2, 2]
    goal = [GRID_COLS - 3, GRID_ROWS - 3]

    return {
        "cols": GRID_COLS,
        "rows": GRID_ROWS,
        "grid": g,
        "start": start,
        "goal": goal,
    }

def save_stage(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)
    print("Saved", filename)

if __name__ == "__main__":
    save_stage("stage2.json", gen_stage2())
    save_stage("stage3.json", gen_stage3())
