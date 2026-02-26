# PokéRogue Fusion Calculator

A modern, lightweight GUI tool for exploring **PokéRogue** fusion combinations. Quickly search Pokémon, analyze fusion results, inspect abilities, evaluate defensive matchups, and navigate key PokéRogue resources — all in one interface.

<p align="center">
  <img src="https://i.postimg.cc/Y9RGNyCs/Screenshot-2026-02-26-103231.jpg" width="600">
</p>

## ✨ Features

### 🔍 Powerful Search & Filters
- Instant filter‑as‑you‑type search for both Pokémon slots
- Advanced query filters:
  - `name:term`
  - `type:fire`
  - `ability:levitate`
  - `passive:clear body`
  - `id:12` or `#025`
  - Numeric filters like:
    - `hp>=100`
    - `speed<120`
    - `bst>500`
- Optional **“Keep search text when selecting”** toggle

### 🔗 Clickable Evolution Chains
Every evolution entry is clickable — select any stage instantly.

### ⚔️ Fusion Results
- Fused type
- Combined stat block with Total BST
- Differences vs. each base Pokémon
- Active Ability (from Pokémon 2)
- Passive Ability toggle (from Pokémon 1)
- Hidden Ability awareness
- Ability effect summaries when they alter defensive matchups

### 🛡️ Damage Taken Overview
A clean, easy‑to‑scan defensive chart:
- Immunities, resistances, and weaknesses
- Bold **Damage Taken:** header
- A blank line separating the header from the list for readability

### 🌀 Flip Stat Challenge Mode
Instantly apply the Flip Stat Challenge ruleset to both base Pokémon and the fusion.

### 🔄 Quick Utilities
- **Swap** Pokémon 1 ↔ 2  
- **Clear** all selections and searches  
- **Fuse** instantly

### 📚 Resource Shortcuts
Accessible via the menu bar:
- Pokémon Database
- Type Calculator
- PokéRogue Pokédex

### 📝 Status Bar
Displays:
- Calculated fuse time (ms)
- Current Active / Passive / Flip Stat toggle states

---

## 🚀 Installation

### Requirements
- Python 3.x  
- `tkinter` (bundled with most Python installations)

### Setup
1. Download:
   - `fusioncalc.py`
   - `pokemon_data.csv`
2. Place both files in the **same directory**

### Run
```bash
python fusioncalc_test.py
