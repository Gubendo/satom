import hashlib
import random
from datetime import date

def daily_seed(day: date) -> int:
    h = hashlib.sha256(f"enclose-{day.isoformat()}".encode()).hexdigest()
    return int(h[:16], 16)

def generate_puzzle(day):
    rng = random.Random(daily_seed(day))

    size = 9
    grid = [["empty"] * size for _ in range(size)]

    # placer cheval
    #hx, hy = rng.randrange(size), rng.randrange(size)
    grid[4][4] = "horse"

    # obstacles naturels
    for _ in range(10):
        x, y = rng.randrange(size), rng.randrange(size)
        if grid[y][x] == "empty":
            grid[y][x] = rng.choice(["water", "mountain"])

    return {
        "size": size,
        "grid": grid,
        "horse": [4, 4],
        "max_walls": 30,
    }

def generate_water(size: int, density: float = 0.25):
    center = size // 2
    water = set()

    for y in range(size):
        for x in range(size):
            if (x, y) == (center, center):
                continue
            if abs(x - center) + abs(y - center) <= 1:
                continue  # voisins directs du cheval

            if random.random() < density:
                water.add((x, y))

    return water