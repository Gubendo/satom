def compute_area(puzzle, walls):
    size = puzzle["size"]
    grid = puzzle["grid"]

    visited = set()
    stack = [tuple(puzzle["horse"])]

    def inside(x, y):
        return 0 <= x < size and 0 <= y < size

    while stack:
        x, y = stack.pop()
        if (x, y) in visited:
            continue
        visited.add((x, y))

        for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
            nx, ny = x + dx, y + dy
            if not inside(nx, ny):
                continue
            if grid[ny][nx] in ("water", "mountain"):
                continue
            if (nx, ny) in walls:
                continue
            stack.append((nx, ny))

    return len(visited)

def write_puzzle(path, size, water, max_walls):
    grid = []
    center = size // 2

    for y in range(size):
        row = ""
        for x in range(size):
            if (x, y) == (center, center):
                row += "H"
            elif (x, y) in water:
                row += "W"
            else:
                row += "."
        grid.append(row)

    data = {
        "id": path.stem,
        "size": size,
        "max_walls": max_walls,
        "grid": grid,
    }

    path.write_text(json.dumps(data, indent=2))
