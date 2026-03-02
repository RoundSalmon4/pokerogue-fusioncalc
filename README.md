# PokéRogue Fusion Calculator

A modern, lightweight GUI tool for exploring **PokéRogue** fusion combinations. 

This calculator mirrors the core mechanics described in the official PokéRogue Fusion rules — including **stat averaging**, **typing inheritance**, **ability behavior**, and **defensive effectiveness** — based on authoritative sources such as the PokéRogue Wiki and the game’s upstream GitHub repository.  

<p align="center">
  <img src="https://i.postimg.cc/R0wy9Mrv/Screenshot-2026-03-02-124326.jpg" width="600">
</p>

---

## ✨ Features

### 🔍 Powerful Search & Filters
- Instant filter‑as‑you‑type search for both Pokémon slots  
- Full advanced token system:
  - `name:char`
  - `type:fire`
  - `ability:levitate`
  - `passive:regenerator`
  - `id:12` or `#025`
  - Numeric filters such as:
    - `hp>=100`
    - `speed<120`
    - `bst>500`
- **Sticky Filters** option to keep or clear search boxes when selecting

---

## 🧬 Fusion Engine

### Types
Implements PokéRogue’s official fusion typing rules:
- **Primary Type** → from Pokémon 1  
- **Secondary Type** → from Pokémon 2  
- Intelligent duplication handling for mono/dual‑type edge cases  
- Fully matches Fusion Mechanics definitions from the official wiki

### Stats
- All six base stats are **independently averaged**
- Total BST calculated live
- Differences vs both source Pokémon

### Abilities
- **Active Ability** = main ability from Pokémon 2  
- **Passive Ability** = from Pokémon 1 (toggleable just like in‑game)  
- Hidden Ability recognition  
- Ability effects applied to defensive matchups when relevant (e.g., Dry Skin, Levitate, Flash Fire, Purifying Salt, Thick Fat)

---

## 🛡️ Defensive Analysis (Type Chart + Ability Effects)

Includes:
- Full **Gen 6+ Pokémon type chart** baseline  
- Ability‑driven adjustments:
  - Immunities (e.g., **Levitate → Ground**, **Water Absorb → Water**)  
  - Halves (e.g., **Thick Fat → Fire/Ice**, **Purifying Salt → Ghost**)  
  - Multipliers (e.g., **Dry Skin → Fire ×1.25**)  
  - Wonder Guard special rule (immune to all non‑super‑effective)

### Output presentation
- Clean grouped format:
  - **Immune**
  - **1/4×**
  - **1/2×**
  - **1×**
  - **2×**
  - **4×**
- Additional non‑standard values (e.g., **0.62× Fire**) shown separately

---

## 🔄 Quick Compare (vs Pokémon 1 or Pokémon 2)
Shows exactly how the fused creature changes defensive profile:
- New immunities  
- Lost immunities  
- Gained weaknesses (≥2×)  
- Lost weaknesses  
- Gained resistances (≤1/2×)  
- Lost resistances  
- Fully ability‑aware (Active + optional Passive)

---

## 🌀 Flip Stat Challenge Mode
Instantly flips stat mapping (HP↔Speed, Atk↔Sp.Def, Def↔Sp.Atk) for:
- Pokémon 1  
- Pokémon 2  
- Fused Pokémon  

Perfect for the **Flip Stat Challenge** mode.

---

## 📊 Logging System (enhanced)
- **Master Logging** toggle  
- **Calculation Logs** now work **independently of Verbose Logs**  
  - Verbose OFF → logs print at INFO  
  - Verbose ON → logs print at DEBUG  
- UI Layout & Widget Font/Tag debugging options  
- Updated help text reflects new logging behavior

---

## 🔄 Quick Utilities
- **Fuse**  
- **Swap** Pokémon 1 ↔ 2  
- **Clear** all selections & filters  

---

## 🔗 Clickable Evolution Chains
- Every evolution stage is selectable in the side panels

---

## 📚 Resource Shortcuts
Links open in browser:
- Pokémon Database  
- Type Calculator  
- PokéRogue Pokédex  
- Filter Help  
- Toolbar Overview  

---

## 📝 Status Bar
Shows:
- Fusion time (ms)  
- Active Ability  
- Passive toggle (ON/OFF)  
- Flip Stat toggle  
- Build HASH tag  

---

# 🚀 Installation

### Requirements
- Python 3.x  
- `tkinter` (bundled with most Python installations)

### Setup
1. Download:
   - `fusioncalc.py`
   - `pokemon_data.csv`
2. Place both files in the **same folder**

### Run
```bash
python fusioncalc.py
