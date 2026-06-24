# Pacing, flow, teaching, and guidance

Geometry is the medium; the goal is a felt rhythm. This reference goes deeper on
the curve, the teaching loop, guiding the player, and reviewing a blockout.

## The difficulty / tension curve

Plot intended intensity against progress. Two principles:

- **Overall rise with local dips.** Difficulty and tension trend upward toward a
  climax, but in a *sawtooth*: spikes (combat, platforming gauntlets, bosses)
  separated by rests (exploration, story, safe rooms). A monotone high flatlines
  the player's stress response; a monotone low bores them.
- **Rest before climax.** Place a clear breather — a save point, a vista, a
  resource cache — right before the hardest beat. The calm sharpens the spike.

A useful rhythm: **introduce → build → peak → release → (repeat, higher)**. Each
cycle's peak exceeds the last; each release sits a little above the previous
baseline.

## The teaching loop (mechanic introduction)

Players learn by doing, in escalating safety-to-stakes:

1. **Introduce** the mechanic in isolation, where failure is harmless (a spike
   you can see and step over; an enemy that can't yet hurt you).
2. **Develop** it — combine with movement or a second element so the player
   practices deliberately.
3. **Twist** — change context so they apply the idea, not a memorized motion.
4. **Test** — under time/health pressure, where the skill genuinely matters.

This is why the first room is calm and the boss is last: the level *is* a lesson
plan. New mechanics meet the player before, never during, a lethal test.

## The critical path, golden path, and branches

- **Critical path**: the minimal route from start to goal. Must always be
  solvable with abilities/keys obtainable in order (validate it).
- **Golden path**: the route most players will actually take. Design pacing along
  this, not just the shortest line.
- **Branches**: optional loops for exploration and reward. Keep them short enough
  to rejoin the golden path without losing momentum; reward the detour.

Loops and shortcuts (unlock a door back to an earlier hub) reduce backtracking
fatigue and make the space feel coherent.

## Gating tools

- **Locks and keys** — explicit, readable order control.
- **Ability gates** — a chasm needs the double-jump found later; revisiting opens
  it (the Metroidvania pattern). Validate the acquisition order.
- **One-way drops / collapsing paths** — enforce direction; telegraph them so the
  player chooses knowingly.
- **Soft gates** — enemies, environmental hazards, or difficulty that suggest
  "not yet" without a hard wall.

## Readability and guidance (lead without walls)

Players follow attention, not signs. Direct the eye with:

- **Light and contrast** — the bright doorway reads as "go here"; shadows read as
  optional or dangerous.
- **Leading lines** — architecture, rails, and paths that point toward the
  objective.
- **Landmarks** — a tall, unique silhouette visible from afar orients the player
  across the whole level.
- **Color and material** — a consistent color for "interactive/exit" teaches the
  player to scan for it (climbable ledges painted the same hue, etc.).
- **Framing** — compose vistas so the next goal is visible from a high point
  before the player descends to it.

When players get lost in playtests, the fix is usually guidance (a sightline, a
light), not a wall.

## 2D vs 3D considerations

- **2D**: think in the tile grid and the camera window. The player sees a fixed
  slice; telegraph off-screen threats (audio, approach time) so hits feel fair.
  Sightlines and reachable platform spacing dominate.
- **3D**: think in sightlines, verticality, and navigation. Players can get lost
  in three dimensions; landmarks and framed vistas matter more. Mind the camera —
  tight interiors and the player's view cone change what's "reachable" perceptually.

## Blockout review checklist

- Critical path solvable with the keys/abilities available *in order* (no
  soft-lock).
- Every required jump/traversal within metrics (`SAFE_GAP`, reach, camera).
- Pacing reads as a rising sawtooth; a rest precedes each major spike.
- Each mechanic is introduced safely before it's tested.
- The eye is guided toward the path (light/lines/landmarks); test for "lost".
- Optional content rewards the detour and rejoins smoothly.
- Plays well as untextured geometry — dressing would not rescue a bad layout.
- Validated with players, not just the designer.
