from enclose.game.logic import compute_area

"""
criteria = (
    result["max"] >= 12 and
    result["variety"] >= 3 and
    result["max"] - result["min"] >= 5
)
"""

def validate_solution(puzzle, walls):
    if len(walls) > puzzle["max_walls"]:
        return False, 0

    score = compute_area(puzzle, walls)
    return True, score

def evaluate_puzzle(grid, horse, max_walls):
    """
    Retourne :
    - aire_min
    - aire_max
    - diversité (nombre de scores distincts)
    """
    # ⚠️ Version volontairement heuristique
    possible_areas = set()

    for _ in range(200):  # essais aléatoires
        walls = random_wall_set(grid, max_walls)
        area = compute_area(grid, horse, walls)
        if area:
            possible_areas.add(area)

    if not possible_areas:
        return None

    return {
        "min": min(possible_areas),
        "max": max(possible_areas),
        "variety": len(possible_areas),
    }