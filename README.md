# PokéRogue Fusion Calculator

A fast, Tkinter-based GUI tool for exploring **PokéRogue** fusions. Pick two Pokémon, see the fused stats and typing, preview ability effects on defensive matchups, and jump to helpful resources—all in one window.

![PokeRogue Fusion Calculator](https://i.postimg.cc/Y9RGNyCs/Screenshot-2026-02-26-103231.jpg)


---

## Key Features

- **Filter-as-you-type search** for each side, with support for:
  - `name:`, `type:`, `ability:`, `passive:`, `id:` / `#`
  - Numeric filters: `hp|attack|defense|sp. atk|sp. def|speed|bst` with `>`, `<`, `>=`, `<=`, `=`
  - Example: `hp>=100 speed<120 bst>500` 
- **Sticky search option** (Options → *Keep search text when selecting*) so your search terms remain when you pick a Pokémon.
- **Ability controls**:
  - **Active Ability** drop-down (from Pokémon 2)
  - **Passive Active** toggle (from Pokémon 1), centered in the options pane
  - Defensive matchup effects shown when abilities meaningfully change the type chart (e.g., immunities or halved damage). 
- **Flip Stat Challenge** (Challenges menu) to view stats under the in-game Flip Stat rule. 
- **Clickable evolution line** in each side panel—jump to any stage with a click.
- **Helpful resource links** in the menu (Pokémon Database, Type Calculator, PokéRogue Pokédex).
- Lightweight status bar with fuse timing and current options summary.

---

## Getting Started

### Requirements
- **Python 3.x**
- The standard library’s **tkinter** module (ships with most CPython installers)

### Installation
1. Download **`fusioncalc.py`** and **`pokemon_data.csv`** into the **same directory**.
2. Ensure Python can import `tkinter` on your system.
