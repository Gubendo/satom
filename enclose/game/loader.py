import json
from pathlib import Path

PUZZLES_DIR = Path(__file__).resolve().parent.parent / "puzzles"

def load_puzzle(puzzle_id: str):
    path = PUZZLES_DIR / f"{puzzle_id}.json"
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    # transformer le format texte → grille exploitable
    grid = []

    size = data["size"]

    # 🔒 taille impaire obligatoire
    if size % 2 == 0:
        raise ValueError("La taille de la grille doit être impaire")

    center = size // 2
    horse = [center, center]

    grid = []
    horse_found = False

    for y, row in enumerate(data["grid"]):
        grid_row = []
        for x, c in enumerate(row):
            if c == ".":
                grid_row.append("empty")
            elif c == "W":
                grid_row.append("water")
            elif c == "H":
                if [x, y] != horse:
                    raise ValueError("Le cheval doit être au centre")
                grid_row.append("horse")
                horse_found = True
            else:
                raise ValueError(f"Caractère invalide : {c}")
        grid.append(grid_row)

    if not horse_found:
        raise ValueError("Cheval manquant dans la grille")

    return {
        "id": data["id"],
        "size": size,
        "grid": grid,
        "horse": horse,
        "max_walls": data["max_walls"],
    }
