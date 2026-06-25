---
name: puzzle
description: >
  Build a puzzle game: grid/board state, move input, rule-based resolution (match-3 cascades, sokoban
  pushes, tile logic), scoring, and undo. Use for a match-3, sokoban, or grid-logic puzzle.
license: Apache-2.0
compatibility: Engine-agnostic design patterns; snippets are pseudocode (port to your engine)
metadata:
  engine: none
  category: genres
  difficulty: intermediate
---

# Puzzle

A playbook for grid/board puzzle games — the board model, move input, rule resolution
(matching, pushing, logic), scoring, undo, and level progression. This is a **compositional**
skill: it models board state and rules and presents them through a tilemap/UI. It does not
re-teach tilemaps; it defines the resolution loop and the correctness rules (clean state,
deterministic resolution, undo) that keep a puzzle fair and bug-free.

## When to use

- Use when the game is a **discrete board** the player changes with moves, and the board
  **resolves by rules**: match-3/tile-matching, sokoban/block-pusher, sliding puzzle, logic grid.
- Use when designing match/cascade resolution, undo, level progression, or solvability.

**When *not* to use:** real-time grid action with permadeath → `roguelike`. Card zones/turns →
`card-game`. Physics-based "puzzle platformer" → `platformer` + `physics-tuning`. For the tile
rendering, use `godot-tilemap` / `unity-tilemap-2d`.

## Core loop

**Read the board → plan a move → make the move → the board resolves by its rules (match, push,
fall, fill, cascade) → see progress toward the objective → repeat until solved/failed.** The
fun is the *planning*; the engine's job is to resolve each move **deterministically** and
present it clearly.

## Must-have systems

1. **Board model** — a grid of cells holding pieces; the single source of truth (logic, not visuals).
2. **Move input** — swap, push, drag, rotate, or place; validate legality before applying.
3. **Rule resolution** — detect and apply the genre's rule (matches, pushes, logic) until stable.
4. **Cascades/chains** — when resolution changes the board, re-resolve until no more changes.
5. **Objectives + scoring** — win/lose conditions (score, clear all, reach goal); move/time limits.
6. **Undo** — revert the last move (and its resolution) exactly; essential for thinky puzzles.
7. **Level progression + (often) generation** — hand-authored or generated **solvable** boards.
8. **Feedback ("juice")** — clear, satisfying animation/sound for matches, falls, and chains.

## Design knobs

| Knob | Effect | Notes |
|------|--------|-------|
| Grid size / shape | complexity | Square is standard; hex/irregular change feel. |
| Match/push rule | genre identity | 3-in-a-row, shapes, push-into-goal, etc. |
| Cascade scoring | reward depth | Bigger chains = exponential payoff. |
| Move / time limit | pressure | Move-limited = puzzly; time = arcade. |
| Difficulty curve | learning | Introduce one mechanic at a time. |
| Undo depth | forgiveness | Single-step vs. full history. |
| Solvability guarantee | fairness | Generated boards must be solvable. |
| Deadlock handling | no dead ends | Detect no-moves; shuffle or end (refs). |

## Patterns

### 1. Board model + match detection (logic separate from visuals)

```python
# Pseudocode. The board is the truth; rendering reads from it. (0,0) top-left, y grows down.
board = [[piece_or_empty for _ in range(W)] for _ in range(H)]

def find_matches(board):
    matched = set()
    for y in range(H):                       # horizontal runs of >= 3 equal pieces
        run = 1
        for x in range(1, W):
            if board[y][x] and board[y][x] == board[y][x-1]: run += 1
            else:
                if run >= 3: matched |= {(y, k) for k in range(x-run, x)}
                run = 1
        if run >= 3: matched |= {(y, k) for k in range(W-run, W)}
    # ... repeat the same scan vertically (columns) ...
    return matched
```

### 2. Resolve → collapse → refill → cascade (repeat to stability)

```python
# Pseudocode. One player move can trigger a chain; loop until the board stops changing.
def resolve(board):
    chain = 0
    while True:
        matches = find_matches(board)
        if not matches: break                 # stable: resolution complete
        chain += 1
        score += score_for(matches, chain)    # later chain steps score more (see refs)
        clear(board, matches)                  # remove matched pieces
        apply_gravity(board)                   # pieces fall into the gaps
        refill(board, rng)                      # spawn new pieces at the top (seeded RNG)
    return chain
```

### 3. Undo via state snapshot or command

```python
# Pseudocode. Snapshot before each move; undo restores it exactly (board + score + counters).
def make_move(move):
    history.append(snapshot(board, score, moves_left))   # push BEFORE applying
    apply(move); resolve(board); moves_left -= 1

def undo():
    if history:
        board, score, moves_left = history.pop()         # exact revert, including resolution
```

For large boards prefer the **command** pattern (store the move + enough to invert it) over full
snapshots to save memory; snapshots are simplest and fine for small boards.

## Pitfalls / failure modes

- **Mixing logic and visuals** → animations desync from state and cause bugs. The board model is
  the single source of truth; the view only renders it.
- **Resolving only once** → cascades/chains are missed. Loop resolution until the board is stable
  (Pattern 2).
- **Undo that doesn't restore everything** → score/move-count/random-state drift. Snapshot *all*
  state, or make the move fully invertible.
- **Unseeded refill RNG** → can't reproduce a level / no deterministic undo or daily puzzle. Seed it.
- **Generated boards that aren't solvable** → unfair dead ends. Generate-and-verify, or generate
  from a known solution backward (refs).
- **No deadlock detection** (match-3) → board with no valid moves softlocks. Detect "no moves"
  and shuffle or end the level (refs).
- **Difficulty spikes** → too many mechanics at once. Teach one mechanic per level before combining.
- **Resolution mid-animation accepts input** → double-moves/corruption. Lock input until the
  board is stable.

## Composition (build it from these skills)

- **Board rendering:** `godot-tilemap` / `unity-tilemap-2d` for the grid; `godot-ui-control` for HUD, score, and menus.
- **Levels:** `level-design` for hand-authored puzzles and difficulty pacing; `procedural-gen` for solvable generated boards.
- **Persistence:** `save-systems` for level progress, high scores, and seeded daily puzzles.
- **Juice:** `game-feel` for match/cascade pop, screen shake, and chain feedback; the engine animation/`Tween` skill for swaps/falls/clears; `audio-design` for match and chain cues.
- **Scripting:** `godot-gdscript` / `unity-csharp-scripting` for the resolution loop and rules.

## References

- For match-3 detection/gravity/refill/cascade detail, deadlock detection and reshuffles,
  sokoban/rule-based puzzles, undo strategies, solvable generation, and scoring, read
  `references/board-and-resolution.md`.
