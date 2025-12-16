import json
from pathlib import Path
from typing import Any, Dict, List, Sequence

import pygame

# Location for storing evaluation results. Kept alongside the scripts.
EVAL_FILE = Path(__file__).resolve().parent / "evaluation_results.json"

# Colors for the table panel; kept here so maze_runner stays thin.
PANEL_BG = (26, 28, 34)


def load_results() -> List[Dict[str, Any]]:
    if not EVAL_FILE.exists():
        return []

    try:
        raw = EVAL_FILE.read_text(encoding="utf-8")
        data = json.loads(raw)
        if isinstance(data, list):
            return data
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Gagal membaca {EVAL_FILE.name}: {exc}")
    return []


def save_results(rows: List[Dict[str, Any]]) -> None:
    try:
        EVAL_FILE.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    except OSError as exc:
        print(f"Gagal menyimpan {EVAL_FILE.name}: {exc}")


def clear_results() -> List[Dict[str, Any]]:
    """Remove all stored evaluation rows."""
    save_results([])
    return []


def build_rows(history: List[Dict[str, Any]], method_order: Sequence[str]) -> List[Dict[str, Any]]:
    """Return up to one row per method, in the given order."""
    latest = {rec.get("algo"): rec for rec in history}
    rows: List[Dict[str, Any]] = []
    for idx, algo in enumerate(method_order, 1):
        rec = latest.get(algo, {})
        rows.append(
            {
                "no": idx,
                "algo": algo[:3],
                "stage": rec.get("stage", "-"),
                "len": rec.get("path_length", "-"),
                "cost": rec.get("path_cost", "-"),
                "time": f"{rec.get('time_ms', 0.0):.2f}" if rec else "-",
                "nodes": rec.get("explored", "-"),
            }
        )
    return rows


def draw_table(
    screen,
    font,
    history: List[Dict[str, Any]],
    method_order: Sequence[str],
    width: int,
    height: int,
    text_color,
    grid_color,
):
    """Render the evaluation table at the top-right with grid lines."""
    rows = build_rows(history, method_order)

    title = "Evaluasi tiap Methd"
    cols = [
        ("No", 36),
        ("Al", 40),
        ("S", 26),
        ("Ln", 36),
        ("Ct", 36),
        ("Time", 72),
        ("N", 56),
    ]

    pad = 10
    row_h = 22
    table_w = sum(width for _, width in cols) + pad * 2
    table_h = pad + row_h * (2 + max(len(rows), 1)) + pad  # title + header + rows

    table_x = width - table_w - 16
    table_y = 12

    panel_rect = pygame.Rect(table_x - 6, table_y - 6, table_w + 12, table_h + 12)
    pygame.draw.rect(screen, PANEL_BG, panel_rect, border_radius=8)

    cursor_y = table_y + pad
    title_surf = font.render(title, True, text_color)
    screen.blit(title_surf, (table_x + pad, cursor_y))
    cursor_y += row_h

    header_y = cursor_y
    grid_top = header_y
    grid_bottom = table_y + table_h - pad

    pygame.draw.line(screen, grid_color, (table_x, header_y), (table_x + table_w, header_y), 1)

    x = table_x
    for _, width in cols:
        pygame.draw.line(screen, grid_color, (x, header_y), (x, grid_bottom), 1)
        x += width
    pygame.draw.line(screen, grid_color, (table_x + table_w, header_y), (table_x + table_w, grid_bottom), 1)

    # Header labels
    col_x = table_x + pad
    for col_title, width in cols:
        surf = font.render(col_title, True, text_color)
        screen.blit(surf, (col_x, header_y + 2))
        col_x += width

    cursor_y = header_y + row_h
    if rows:
        for row in rows:
            col_x = table_x + pad
            for (key, width) in zip(("no", "algo", "stage", "len", "cost", "time", "nodes"), [w for _, w in cols]):
                txt = str(row.get(key, ""))
                surf = font.render(txt, True, text_color)
                screen.blit(surf, (col_x, cursor_y + 2))
                col_x += width
            cursor_y += row_h

    # Horizontal lines for rows
    y_line = header_y + row_h
    for _ in rows[:-1]:
        pygame.draw.line(screen, grid_color, (table_x, y_line), (table_x + table_w, y_line), 1)
        y_line += row_h
