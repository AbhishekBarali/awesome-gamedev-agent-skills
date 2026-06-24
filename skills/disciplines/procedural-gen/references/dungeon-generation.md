# Dungeon and level generation

Three families cover most 2D level generation. All write into a plain grid
(`0 = wall`, `1 = floor`) that a tile pass renders later. All take a seeded RNG.

## A. Rooms and corridors

Simple, readable, gives recognizable rooms. Place rectangles, then connect.

```python
def generate(W, H, rng, attempts=200, rmin=4, rmax=9):
    grid = [[0]*W for _ in range(H)]          # 0 = wall
    rooms = []
    for _ in range(attempts):
        w = rng.randint(rmin, rmax); h = rng.randint(rmin, rmax)
        x = rng.randint(1, W - w - 1); y = rng.randint(1, H - h - 1)
        new = (x, y, w, h)
        if any(_overlap(new, o, pad=1) for o in rooms):
            continue                          # keep at least one tile between rooms
        _carve_room(grid, new)
        if rooms:                             # connect to the previously placed room
            (cx, cy), (px, py) = _center(new), _center(rooms[-1])
            _carve_h(grid, px, cx, py)        # horizontal leg
            _carve_v(grid, py, cy, cx)        # vertical leg -> L-shaped corridor
        rooms.append(new)
    return grid, rooms
```

For more interesting connectivity than "chain the rooms", connect rooms via a
minimum spanning tree of their centers, then add a few extra edges for loops.

## B. BSP (binary space partitioning)

Splits space recursively, guaranteeing rooms never overlap and tile the map. Good
for structured, building-like dungeons.

```python
def bsp(node, rng, depth, min_size=8):
    if depth == 0 or (node.w < min_size*2 and node.h < min_size*2):
        node.room = _random_room_inside(node, rng)   # leaf: place one room
        return
    if node.w > node.h:                               # split the longer axis
        cut = rng.randint(min_size, node.w - min_size)
        left, right = node.split_vertical(cut)
    else:
        cut = rng.randint(min_size, node.h - min_size)
        left, right = node.split_horizontal(cut)
    bsp(left, rng, depth-1, min_size); bsp(right, rng, depth-1, min_size)
    node.children = (left, right)
    _connect(left.room_or_subroom(), right.room_or_subroom(), rng)  # join siblings
```

Connect siblings as the recursion unwinds, so every region links to its sibling
and the whole tree stays connected.

## C. Random-walk / cellular caves

Organic caverns. Either carve with a drunkard's walk, or seed noise then smooth
with cellular automata.

```python
# Drunkard's walk: a digger wanders, carving floor, until enough is open.
def drunkard(W, H, rng, target_ratio=0.45):
    grid = [[0]*W for _ in range(H)]
    x, y = W//2, H//2; carved = 0; goal = int(W*H*target_ratio)
    while carved < goal:
        if grid[y][x] == 0: grid[y][x] = 1; carved += 1
        x = clamp(x + rng.choice([-1,0,1]), 1, W-2)   # random step, stay in bounds
        y = clamp(y + rng.choice([-1,0,1]), 1, H-2)
    return grid

# Cellular automata smoothing: a cell becomes wall if most neighbors are walls.
def smooth(grid, W, H, steps=4):
    for _ in range(steps):
        new = [row[:] for row in grid]
        for y in range(1, H-1):
            for x in range(1, W-1):
                walls = sum(1 for dy in (-1,0,1) for dx in (-1,0,1)
                            if grid[y+dy][x+dx] == 0)
                new[y][x] = 0 if walls >= 5 else 1   # 5/9 majority rule
        grid = new
    return grid
```

## Connectivity validation (do this every time)

Generation can isolate regions. Flood-fill from the spawn; if floor tiles remain
unreached, either discard the map, dig a tunnel to the nearest reached tile, or
keep only the largest region.

```python
def reachable_floor(grid, start):
    seen, stack = set(), [start]
    while stack:
        x, y = stack.pop()
        if (x, y) in seen or grid[y][x] == 0: continue
        seen.add((x, y))
        stack += [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]
    return seen        # compare len(seen) to total floor count; reconnect the rest
```

Also validate: a path from spawn to exit exists (reuse `game-ai` A*), the spawn
tile is safe, and key items aren't behind locks they themselves gate.

## Distribution control for loot/spawns

Pure weighted rolls produce streaks (ten commons in a row). Two fixes:

- **Bag / deck**: fill a bag with items in proportion to weights, shuffle, draw
  without replacement, refill when empty. Guarantees the rate over a window.
- **Pity timer**: track rolls since the last rare; once a threshold is passed,
  force or boost the rare's chance. Common in gacha/loot systems.

Keep these in the seeded RNG too, so drop sequences stay reproducible.
