---
name: visual-novel
description: >
  Build a visual novel: a branching script, character and background display, a text box with choices,
  save/load, backlog, and skip/auto. Use for a VN, dating sim, or branching story game.
license: Apache-2.0
compatibility: Engine-agnostic design patterns; snippets are pseudocode (port to your engine)
metadata:
  engine: none
  category: genres
  difficulty: beginner
---

# Visual Novel

A playbook for visual novels — the branching script, the presentation (text box, characters,
backgrounds), choices, and the quality-of-life systems players expect (save anywhere, backlog,
skip, auto). This is a **compositional** skill: it drives a dialogue engine and a UI layer. It
does not re-teach the dialogue engine or UI nodes; it defines the script model and the player
conveniences that make a VN pleasant to read.

## When to use

- Use when the game is **mostly reading branching text** with character art and backgrounds:
  visual novel, dating sim, branching interactive fiction, story-choice game.
- Use when designing a choice/route structure, story flags, or VN conveniences (backlog,
  skip, auto-advance, save-anywhere).

**When *not* to use:** dialogue as one feature inside a larger game → `rpg` consuming
`dialogue-systems`. Card/board play → other genres. For the branching-script engine itself,
use `dialogue-systems` (Ink / Yarn Spinner).

## Core loop

**Read a line → advance → (at a branch) make a choice → the story branches on flags/choices →
read on → reach an ending.** The "game" is the *shape of the branching* and whether choices
feel consequential; everything else is presentation and convenience.

## Must-have systems

1. **Branching script** — ordered lines + choices + jumps, with conditions and variables (Ink/Yarn).
2. **Text box** — speaker name, body text, typewriter reveal, advance on click/key.
3. **Characters** — sprites with expressions/poses, positions, show/hide transitions.
4. **Backgrounds + transitions** — scene images, fades/dissolves.
5. **Choices** — present options, gate some on flags, record the pick.
6. **Story state** — flags/variables that branch the script and unlock content.
7. **Save/load (save-anywhere)** — full script position + state; multiple slots; quick save.
8. **VN conveniences** — backlog/history, skip (read text), auto-advance, text-speed setting.
9. **Audio** — music per scene, SFX, optional voice clips.

## Design knobs

| Knob | Effect | Notes |
|------|--------|-------|
| Text speed / instant | reading comfort | Always allow instant + a skip. |
| Auto-advance delay | hands-free reading | Tunable; pause on choices. |
| Skip scope | re-reading | Skip *read* text only by default. |
| Branch breadth/depth | replay value vs. cost | Branches multiply writing/art work. |
| Flag-gated content | reactivity | Lines/choices that check past decisions. |
| Route structure | story shape | Branch-and-merge vs. distinct routes (refs). |
| Choice visibility | fairness | Show locked choices vs. hide them. |
| Backlog length | convenience | Keep enough to re-read recent context. |

## Patterns

### 1. Script as data the engine walks

```python
# Pseudocode. Lines, choices, and jumps as data — usually authored in Ink/Yarn and stepped
# through by that runtime. The engine asks the script for "the next thing to show".
node = script.current()
if node.kind == "line":
    show_text(node.speaker, node.text)        # wait for advance input
elif node.kind == "choice":
    options = [o for o in node.options if condition_met(o.condition, flags)]  # gate by flags
    show_choices(options)                      # wait for selection
elif node.kind == "set":
    flags[node.var] = eval_expr(node.expr, flags)
script.advance(selected_option_or_none)
```

### 2. Typewriter reveal + advance (skippable)

```python
# Pseudocode. Reveal characters over time; a click first completes the line, then advances.
def show_text(speaker, text):
    name_label.text = speaker
    revealed = 0
    while revealed < len(text):
        if advance_pressed():                  # first press: reveal the whole line instantly
            revealed = len(text); break
        revealed += chars_per_second * dt
        body_label.text = text[:int(revealed)]
        push_to_backlog_when_complete(speaker, text)
    wait_for_advance()                          # second press: go to the next line
```

### 3. Choice sets a flag that branches later content

```python
# Pseudocode. Choices write flags; later conditions read them — that is "reactivity".
def on_choice(option):
    if option.set: flags[option.set] = True     # e.g. flags["helped_npc"] = True
    script.jump(option.target)                   # follow the branch

# Elsewhere, a line/choice/ending checks the flag:
if flags.get("helped_npc"): play_route("good_ending") else: play_route("neutral_ending")
```

## Pitfalls / failure modes

- **Save that only stores a checkpoint** → VNs need **save-anywhere**. Persist the exact script
  position *and* all flags/variables (and seen-text data) so a load resumes the same line.
- **Presentation logic baked into the script** → unmaintainable. Keep *content* (text, choices)
  in the script and *how it looks* (sprites, transitions) in the engine layer.
- **No skip/auto/backlog** → readers feel trapped, especially on replays. These are expected
  baseline features, not extras.
- **Skipping unread text** → players miss content. Skip should fast-forward **read** text only.
- **Choices with no consequence** → branches that reconverge instantly feel fake. Set flags that
  visibly change later lines, choices, or endings.
- **Combinatorial branch explosion** → unshippable. Prefer branch-and-merge with a few flagged
  variations over fully distinct trees (refs).
- **Lost reading context** → no backlog to re-read the last lines. Keep a history buffer.
- **Hardcoded language** → no localization path. Keep text in data keyed for translation.

## Composition (build it from these skills)

- **Script engine:** `dialogue-systems` (Ink / Yarn Spinner) — branching, conditions, variables, localization hooks.
- **Presentation:** `game-ui-ux` for text-box/choice-menu layout, scaling, and safe areas; `godot-ui-control` for the concrete text box, choice menu, name plate, and backlog UI.
- **Persistence:** `save-systems` for save-anywhere slots, seen-text/skip data, and settings.
- **Audio:** `audio-design` for per-scene music, SFX, and voice playback.
- **Visuals:** the engine animation/`Tween` skill for sprite/background transitions; `shader-programming` for dissolves.
- **Process:** `prototype-fast` to test the branch structure in plain text before adding art.

## References

- For the branching data model, route structures (branch-and-merge vs. routes), flags/variables,
  save-anywhere + backlog/skip data, and the content/presentation split, read
  `references/script-and-flow.md`.
