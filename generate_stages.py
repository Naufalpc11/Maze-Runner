import json

GRID_COLS, GRID_ROWS = 30, 22

def new_grid():
    # 0 = kosong (jalan biasa)
    # 1 = wall biasa (bisa diubah user)
    # 2 = cost 2 (gunung)  -> TIDAK dipakai di sini
    # 3 = wall permanen (tidak bisa diubah user)
    return [[0 for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]

def gen_stage2():
    g = new_grid()

    # >>> TIDAK ADA LAGI WALL DI PINGGIR GRID <<<

    midx = GRID_COLS // 2  # 15

    # dinding vertikal permanen di tengah
    for y in range(2, GRID_ROWS - 2):
        g[y][midx] = 3

    # bikin celah di 3 tempat (koridor)
    for y in (4, 10, 16):
        g[y][midx] = 0

    # dinding horizontal zig-zag (permanen)
    # bagian atas kiri
    for x in range(2, midx - 1):
        g[3][x] = 3
    # bagian atas kanan
    for x in range(midx + 2, GRID_COLS - 2):
        g[5][x] = 3

    # bagian tengah
    for x in range(2, midx - 3):
        g[9][x] = 3
    for x in range(midx + 3, GRID_COLS - 2):
        g[11][x] = 3

    # bagian bawah
    for x in range(2, midx - 2):
        g[15][x] = 3
    for x in range(midx + 2, GRID_COLS - 3):
        g[17][x] = 3

    # >>> SEMUA CLUSTER COST=2 DIHAPUS (tidak ada lagi tile 2) <<<

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

    # >>> TIDAK ADA LAGI WALL DI PINGGIR GRID <<<
    # (border dibiarkan 0 / kosong)

    def rect_lock(x1, y1, x2, y2):
        # blok wall permanen
        for y in range(y1, y2 + 1):
            for x in range(x1, x2 + 1):
                g[y][x] = 3

    # blok-blok permanen di tengah map
    rect_lock(10, 6, 19, 9)    # blok tengah atas
    rect_lock(10, 12, 19, 15)  # blok tengah bawah
    rect_lock(3, 3, 6, 7)      # kiri atas
    rect_lock(3, 14, 7, 18)    # kiri bawah
    rect_lock(22, 3, 26, 7)    # kanan atas
    rect_lock(22, 13, 27, 18)  # kanan bawah

    # koridor utama (dibuka = 0) di antara blok-blok permanen
    # koridor vertikal kiri (x = 9)
    for y in range(0, GRID_ROWS):
        g[y][9] = 0

    # koridor vertikal kanan (x = 20)
    for y in range(0, GRID_ROWS):
        g[y][20] = 0

    # koridor horizontal tengah (y = 11)
    for x in range(0, GRID_COLS):
        g[11][x] = 0

    # beberapa "pintu" tambahan dari koridor ke area lain
    g[6][9]  = 0
    g[8][9]  = 0
    g[13][9] = 0
    g[15][9] = 0

    g[7][20]  = 0
    g[9][20]  = 0
    g[13][20] = 0

    # pintu horizontal di blok tengah
    for x in range(11, 19):
        g[7][x]  = 0
        g[14][x] = 0

    # >>> SEMUA CLUSTER COST=2 DIHAPUS (tidak ada loop yang set g[y][x] = 2) <<<

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
