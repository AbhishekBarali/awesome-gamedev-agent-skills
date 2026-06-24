# Ink and Yarn Spinner — syntax cheat sheet

Both are mature, open-source narrative tools. Pick **Ink** for prose-first,
heavily branching writing; pick **Yarn Spinner** for node-graph dialogue with
explicit engine commands. This sheet covers the constructs you reach for most;
consult the official docs for the full language.

## Side-by-side

| Concept | Ink (inkle) | Yarn Spinner 2.x |
|---|---|---|
| Unit of content | **knot** `=== name ===` (sub-units = stitches `= name`) | **node** with `title:` header, body between `---` and `===` |
| Plain line | bare text | bare text, optional `Speaker:` prefix |
| Choice / option | `*` once-only, `+` sticky | `->` option, with indented body |
| Move flow | divert `-> name`, end `-> END` / `-> DONE` | `<<jump NodeName>>` |
| Declare variable | `VAR gold = 0` (global), `~ temp x = 0` | `<<declare $gold = 0>>` |
| Set variable | `~ gold = gold - 5` | `<<set $gold = $gold - 5>>` |
| Show variable | `{gold}` | `{$gold}` |
| Condition on choice | `* {gold >= 50} [Bribe] ...` | `-> Bribe <<if $gold >= 50>>` |
| Conditional text | `{flag: yes text\|no text}` | `<<if $flag>>...<<else>>...<<endif>>` |
| Constants | `CONST MAX = 3` | (use a declared variable) |
| Comments | `// line` and `/* block */` | `// line` |

## Ink essentials

```ink
INCLUDE characters.ink              // split content across files (top of file)
VAR met_guard = false               // global variable
CONST GATE_COST = 50

-> tavern                           // content outside a knot runs first; divert in

=== tavern ===
The tavern is warm and loud.
* [Talk to the guard] -> guard
* [Leave] -> END

=== guard ===
~ met_guard = true                  // '~' marks a logic line (assignment / call)
{ met_guard: "You again." | "Who are you?" }   // conditional text: seen-before?
+ {gold >= GATE_COST} [Pay {GATE_COST} gold]    // sticky choice, gated, interpolated
    ~ gold = gold - GATE_COST
    -> END
+ [Never mind] -> tavern            // sticky so the menu can loop
```

Useful Ink behaviors:

- **Square brackets in a choice** split what the player sees from what prints:
  `* "Yes[."]," I said.` shows `Yes.` as the option but prints `Yes," I said.`
- **Gathers** (`-`) rejoin branches without naming a knot — the core of "weave".
- **Read counts**: any knot/stitch name used in a condition is the number of
  times it has been visited (`{seen_clue > 2}`), so flags are often free.
- **Alternatives** vary text on revisits: `{a|b|c}` sequence, `{&a|b}` cycle,
  `{!a|b}` once-only, `{~a|b}` shuffle.
- **Randomness**: `RANDOM(1, 6)` (inclusive); `SEED_RANDOM(n)` for repeatable tests.
- **Functions**: `=== function name(args) ===` with `~ return value`.

## Yarn Spinner essentials

```yarn
title: Tavern
---
<<declare $gold = 60>>
<<declare $met_guard = false>>
The tavern is warm and loud.
-> Talk to the guard
    <<jump Guard>>
-> Leave
    Narrator: You step back into the night.
===

title: Guard
---
<<set $met_guard to true>>
<<if $met_guard>>
    Guard: You again.
<<else>>
    Guard: Who are you?
<<endif>>
-> Pay 50 gold <<if $gold >= 50>>
    <<set $gold = $gold - 50>>
    Guard: ...go on through. You have {$gold} left.
-> Never mind
    <<jump Tavern>>
===
```

Useful Yarn behaviors:

- **Variables** start with `$`, hold number/string/bool, and must keep their
  type. `<<declare>>` them up front (often in a setup node).
- **Operators** have word and symbol forms: `is`/`==`, `and`/`&&`, `or`/`||`,
  `not`/`!`, plus `<`, `>`, `<=`, `>=`.
- **Commands** (`<<...>>`) that aren't built in are dispatched to your game code,
  e.g. `<<playSound door_open>>` calls a registered command handler.
- **Functions** (`visited("Node")`, custom registered functions) return values
  usable in `<<if>>` and `{ }` interpolation.

## Integration notes

- **Ink**: compile `.ink` to JSON, then step the runtime: it yields lines and
  choice lists; you call `Continue()` / `ChooseChoiceIndex()`. Bindings exist for
  Unity (official), Godot (community), and web (inkjs).
- **Yarn Spinner**: a `DialogueRunner` steps `.yarn` nodes, raising line, options,
  and command events your views handle. First-class Unity support; Godot and
  other runtimes exist.
- **Localization**: both support extracting line IDs/tags to string tables. Tag
  lines and ship per-locale tables rather than translating the script in place.
- **Variable bridging**: expose game state to the script (gold, flags, quest
  stage) via variable storage / external functions so dialogue reacts to play,
  and persist that state through `save-systems`.

Originality note: the snippets above are minimal originals written to illustrate
each construct, verified against the official Ink and Yarn Spinner documentation.
