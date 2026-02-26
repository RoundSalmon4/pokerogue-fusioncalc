
# PokéRogue Fusion Calculator — build 2026-02-25 (patched)
import tkinter as tk
from tkinter import ttk, messagebox
import csv
import logging
import sys
import webbrowser
import time
import re
from typing import Dict, Any, Optional
from tkinter import font as tkfont

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
BUILD_TAG = "2026-02-26"

# -------- Data store --------
pokemon_stats: Dict[str, Dict[str, Any]] = {}

def load_pokemon_data_into(pstore: Dict[str, Dict[str, Any]]) -> int:
    logging.info("Loading Pokemon data from CSV file")
    pstore.clear()
    count = 0
    try:
        with open('pokemon_data.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                raw_name = (row.get('name') or '').strip()
                display_name = raw_name if raw_name else "Unknown"

                def to_int(v, default=0):
                    try:
                        return int(str(v).strip())
                    except Exception:
                        return default

                stats = {
                    'ID': to_int(row.get('id', 0)),
                    'HP': to_int(row.get('hp', 0)),
                    'Attack': to_int(row.get('attack', 0)),
                    'Defense': to_int(row.get('defense', 0)),
                    'Sp. Atk': to_int(row.get('spAttack', 0)),
                    'Sp. Def': to_int(row.get('spDefense', 0)),
                    'Speed': to_int(row.get('speed', 0)),
                    'BST': to_int(row.get('bst', 0)),
                    'Type_1': (row.get('type1') or 'Unknown').strip() or 'Unknown',
                    'Type_2': (row.get('type2') or '').strip(),
                    'Abilities': [a for a in (row.get('abilities') or '').split(', ') if a],
                    'Passive': (row.get('passive') or '').strip(),
                    'evolution line': (row.get('evolution line') or '').strip(),
                }
                if stats['Type_2'] == stats['Type_1']:
                    stats['Type_2'] = ''
                pstore[display_name] = stats
                count += 1
        logging.info(f"Successfully loaded {count} Pokemon (keys={len(pstore)})")
        return count
    except FileNotFoundError:
        logging.error("pokemon_data.csv not found.")
        try:
            messagebox.showerror("Error", "pokemon_data.csv not found in the working directory.")
        except Exception:
            pass
        sys.exit(1)
    except Exception as e:
        logging.error(f"Error loading Pokemon data: {str(e)}", exc_info=True)
        try:
            messagebox.showerror("Error", f"Failed to load Pokemon data: {str(e)}")
        except Exception:
            pass
        sys.exit(1)

def open_pokemondb(): webbrowser.open("https://pokemondb.net/")

def open_type_calculator(): webbrowser.open("https://www.pkmn.help/defense/")

def open_pokedex(): webbrowser.open("https://wiki.pokerogue.net/dex:pokedex")

# --- Rounding helper for fusion stats (nearest tenth per PokéRogue example) ---
def avg_round_tenth(a: float, b: float) -> float:
    return round((float(a) + float(b)) / 2.0, 1)

# --- Formatting helpers (trim trailing .0 and align stat lines) ---
def format_number_trim(x) -> str:
    try:
        fx = float(x)
    except Exception:
        return str(x)
    s = f"{fx:.1f}".rstrip('0').rstrip('.')
    return s

# --- Stat block writer (bold labels, right-aligned values with tab stops) ---
# We align using a tab stop measured in PIXELS so the first digit vertically lines up.

def _ensure_stat_tags(text: tk.Text):
    # Create tags once; safe to call repeatedly.
    try:
        text.tag_config('stat_label', font=('TkFixedFont', 10, 'bold'))
        text.tag_config('stat_value', font=('TkFixedFont', 10))
        text.tag_config('strong_label', font=('TkFixedFont', 10, 'bold'))
        text.tag_config('hr', foreground='#888888')
    except Exception:
        pass


def _apply_stat_tabs(text: tk.Text, items):
    """Compute a right-aligned tab position so numbers start in the same column."""
    # Determine the maximum label width including colon and space
    labels = [str(lbl) + ':' for (lbl, _v) in items]
    try:
        fnt = tkfont.Font(text, text.cget('font'))  # respect the Text's font
    except Exception:
        fnt = tkfont.nametofont('TkFixedFont')
    max_label_pixels = max((fnt.measure(lbl + ' ') for lbl in labels), default=120)
    # Place a RIGHT-aligned tab stop where values will end; add small padding.
    tab_pos = max_label_pixels + 2  # pixels
    text.tag_config('stat_tabs', tabs=(tab_pos, 'right'))


def write_stat_block(text: tk.Text, items):
    _ensure_stat_tags(text)
    _apply_stat_tabs(text, items)
    for label, value in items:
        val = format_number_trim(value)
        # Insert label (bold), then a tab, then the value (right-aligned at tab)
        text.insert(tk.END, f"{label}:", 'stat_label')
        text.insert(tk.END, "\t")
        text.insert(tk.END, f"{val}\n", ('stat_value', 'stat_tabs'))


def insert_hr(text: tk.Text, width_chars: int = 24):
    _ensure_stat_tags(text)
    text.insert(tk.END, '-' * width_chars + "\n", 'hr')


# --- Flip Stat Challenge mapping ---
# HP->Speed, Attack->Sp. Def, Defense->Sp. Atk, Sp. Atk->Defense, Sp. Def->Attack, Speed->HP
FLIP_MAP = {
    'HP': 'Speed',
    'Attack': 'Sp. Def',
    'Defense': 'Sp. Atk',
    'Sp. Atk': 'Defense',
    'Sp. Def': 'Attack',
    'Speed': 'HP',
}

def flip_stats_dict(stats_like: dict) -> dict:
    """Return a dict with the six battle stats remapped per FLIP_MAP."""
    flipped = {}
    for k in ['HP','Attack','Defense','Sp. Atk','Sp. Def','Speed']:
        v = stats_like.get(k, 0)
        target = FLIP_MAP.get(k, k)
        flipped[target] = v
    for k in ['HP','Attack','Defense','Sp. Atk','Sp. Def','Speed']:
        flipped.setdefault(k, 0)
    return flipped

# Compose a stat section with a left-aligned numeric column and aligned total
# Ensures the first digit of every number (including Total BST) starts at the same x-position
from tkinter import font as tkfont  # already imported above, but safe

def write_stat_section(text: tk.Text, items, total_label: str, total_value):
    _ensure_stat_tags(text)
    try:
        fnt = tkfont.Font(text, text.cget('font'))
    except Exception:
        fnt = tkfont.nametofont('TkFixedFont')
    labels = [f'{lbl}:' for (lbl, _v) in items] + [f'{total_label}:']
    max_label_pixels = max((fnt.measure(lbl + ' ') for lbl in labels), default=120)
    tab_pos = max_label_pixels + 2
    text.tag_config('stat_tabs_left', tabs=(tab_pos, 'left'))
    for label, value in items:
        text.insert(tk.END, f'{label}:', ('stat_label','stat_tabs_left'))
        text.insert(tk.END, '	', 'stat_tabs_left')
        text.insert(tk.END, f"{format_number_trim(value)}\n", ('stat_value','stat_tabs_left'))
    text.insert(tk.END, "\n")
    text.insert(tk.END, f'{total_label}:', ('strong_label','stat_tabs_left'))
    text.insert(tk.END, '	', 'stat_tabs_left')
    text.insert(tk.END, f"{format_number_trim(total_value)}\n", ('stat_value','stat_tabs_left'))

# ===== Ability rule mapping (subset for UI effects) =====
ABILITY_EFFECTS = {
    'LEVITATE': {'immunities': ['Ground']},
    'EARTH EATER': {'immunities': ['Ground']},
    'WATER ABSORB': {'immunities': ['Water']},
    'DRY SKIN': {'immunities': ['Water'], 'multiply': {'Fire': 1.25}},
    'STORM DRAIN': {'immunities': ['Water']},
    'FLASH FIRE': {'immunities': ['Fire']},
    'WELL-BAKED BODY': {'immunities': ['Fire']},
    'VOLT ABSORB': {'immunities': ['Electric']},
    'LIGHTNING ROD': {'immunities': ['Electric']},
    'MOTOR DRIVE': {'immunities': ['Electric']},
    'SAP SIPPER': {'immunities': ['Grass']},
    'SAPSIPPER': {'immunities': ['Grass']},
    'PURIFYING SALT': {'halve': ['Ghost']},
    'THICK FAT': {'halve': ['Fire', 'Ice']},
    'HEATPROOF': {'halve': ['Fire']},
    'WATER BUBBLE': {'halve': ['Fire']},
}


def _normalize_ability(name: str) -> str:
    return (name or '').strip().upper()

# ===== Type chart =====
# (unchanged)
type_effectiveness = {
    'Normal': {'weaknesses': ['Fighting'], 'resistances': [], 'immunities': ['Ghost']},
    'Fire': {'weaknesses': ['Water', 'Ground', 'Rock'], 'resistances': ['Fire', 'Grass', 'Ice', 'Bug', 'Steel', 'Fairy'], 'immunities': []},
    'Water': {'weaknesses': ['Electric', 'Grass'], 'resistances': ['Fire', 'Water', 'Ice', 'Steel'], 'immunities': []},
    'Grass': {'weaknesses': ['Fire', 'Ice', 'Poison', 'Flying', 'Bug'], 'resistances': ['Water', 'Electric', 'Grass', 'Ground'], 'immunities': []},
    'Electric': {'weaknesses': ['Ground'], 'resistances': ['Electric', 'Flying', 'Steel'], 'immunities': []},
    'Ice': {'weaknesses': ['Fire', 'Fighting', 'Rock', 'Steel'], 'resistances': ['Ice'], 'immunities': []},
    'Fighting': {'weaknesses': ['Flying', 'Psychic', 'Fairy'], 'resistances': ['Bug', 'Rock', 'Dark'], 'immunities': []},
    'Poison': {'weaknesses': ['Ground', 'Psychic'], 'resistances': ['Grass', 'Fighting', 'Poison', 'Bug', 'Fairy'], 'immunities': []},
    'Ground': {'weaknesses': ['Water', 'Grass', 'Ice'], 'resistances': ['Poison', 'Rock'], 'immunities': ['Electric']},
    'Flying': {'weaknesses': ['Electric', 'Ice', 'Rock'], 'resistances': ['Grass', 'Fighting', 'Bug'], 'immunities': ['Ground']},
    'Psychic': {'weaknesses': ['Bug', 'Ghost', 'Dark'], 'resistances': ['Fighting', 'Psychic'], 'immunities': []},
    'Bug': {'weaknesses': ['Fire', 'Flying', 'Rock'], 'resistances': ['Grass', 'Fighting', 'Ground'], 'immunities': []},
    'Rock': {'weaknesses': ['Water', 'Grass', 'Fighting', 'Ground', 'Steel'], 'resistances': ['Normal', 'Fire', 'Poison', 'Flying'], 'immunities': []},
    'Ghost': {'weaknesses': ['Ghost', 'Dark'], 'resistances': ['Poison', 'Bug'], 'immunities': ['Normal', 'Fighting']},
    'Dragon': {'weaknesses': ['Ice', 'Dragon', 'Fairy'], 'resistances': ['Fire', 'Water', 'Grass', 'Electric'], 'immunities': []},
    'Dark': {'weaknesses': ['Fighting', 'Bug', 'Fairy'], 'resistances': ['Ghost', 'Dark'], 'immunities': ['Psychic']},
    'Steel': {'weaknesses': ['Fire', 'Fighting', 'Ground'], 'resistances': ['Normal', 'Grass', 'Ice', 'Flying', 'Psychic', 'Bug', 'Rock', 'Dragon', 'Steel', 'Fairy'], 'immunities': ['Poison']},
    'Fairy': {'weaknesses': ['Poison', 'Steel'], 'resistances': ['Fighting', 'Bug', 'Dark'], 'immunities': ['Dragon']}
}


def calculate_type_effectiveness(type1, type2=None, active_ability=None, passive_ability=None):
    logging.debug(f"Calculating type effectiveness for {type1} and {type2}")
    effectiveness = {t: 1.0 for t in type_effectiveness.keys()}
    types = [type1.title()]
    if type2 and type2.title() != type1.title():
        types.append(type2.title())
    for t in types:
        if t not in type_effectiveness:
            logging.error(f"Unknown type: {t}")
            continue
        for weakness in type_effectiveness[t]['weaknesses']:
            effectiveness[weakness] *= 2
        for resistance in type_effectiveness[t]['resistances']:
            effectiveness[resistance] *= 0.5
        for immunity in type_effectiveness[t]['immunities']:
            effectiveness[immunity] = 0

    act = _normalize_ability(active_ability)
    pas = _normalize_ability(passive_ability)

    def apply_effects(which):
        eff = ABILITY_EFFECTS.get(which)
        if not eff:
            return
        for immu in eff.get('immunities', []):
            if immu in effectiveness:
                effectiveness[immu] = 0
        for half in eff.get('halve', []):
            if half in effectiveness:
                effectiveness[half] *= 0.5
        # General multipliers (e.g., Dry Skin vs Fire = 1.25x)
        for _t, _mult in eff.get('multiply', {}).items():
            if _t in effectiveness:
                effectiveness[_t] *= float(_mult)

    if act:
        apply_effects(act)
    if pas:
        apply_effects(pas)
    if act == 'WONDER GUARD' or pas == 'WONDER GUARD':
        for k, v in list(effectiveness.items()):
            if v < 2:
                effectiveness[k] = 0
    logging.debug(f"Calculated effectiveness: {effectiveness}")
    return effectiveness


def format_type_effectiveness(effectiveness):
    result = "Damage Taken:\n"
    grouped = {}
    for t, value in effectiveness.items():
        key = round(float(value), 3)
        grouped.setdefault(key, []).append(t)
    for k in grouped:
        grouped[k].sort()
    if 0.0 in grouped:
        result += f"Immune: {', '.join(grouped[0.0])}\n"
    keys = sorted([k for k in grouped.keys() if k != 0.0], reverse=True)
    def _fmt_mult(x):
        return (f"{x:.3f}").rstrip('0').rstrip('.')
    for k in keys:
        result += f"{_fmt_mult(k)}x damage: {', '.join(grouped[k])}\n"
    return result.strip()


# ===== Small helpers for UI reuse =====

def fill_side_panel(name: str, info_text: tk.Text, id_label: tk.Label, name_label: tk.Label):
    if not name or name not in pokemon_stats:
        return
    name_label.config(text=name)
    stats = pokemon_stats[name]
    t1, t2 = stats['Type_1'], stats['Type_2']
    ptype = t1 if (not t2 or t2 == t1) else f"{t1}/{t2}"

    info_text.delete('1.0', tk.END)

    # Bold Type label
    _ensure_stat_tags(info_text)
    info_text.insert(tk.END, 'Type: ', 'strong_label')
    info_text.insert(tk.END, f"{ptype}\n\n")

    # Passives/Abilities section (explicitly show Passive)
    abilities = list(dict.fromkeys(stats.get('Abilities', [])))
    hidden_ability = abilities[1] if len(abilities) > 1 else ''
    visible_abilities = [a for i, a in enumerate(abilities) if i != 1] if abilities else []
    if visible_abilities:
        info_text.insert(tk.END, 'Abilities: ', 'strong_label')
        info_text.insert(tk.END, f"{', '.join(visible_abilities)}\n")
    if hidden_ability:
        info_text.insert(tk.END, 'Hidden Ability: ', 'strong_label')
        info_text.insert(tk.END, f"{hidden_ability}\n")
    if stats.get('Passive'):
        info_text.insert(tk.END, 'Passive: ', 'strong_label')
        info_text.insert(tk.END, f"{stats['Passive']}\n")
    info_text.insert(tk.END, "\n")
    info_text.insert(tk.END, "\n")

    # Base stats block with alignment and separator line
    info_text.insert(tk.END, 'BST:', 'strong_label')
    info_text.insert(tk.END, "\n")
    insert_hr(info_text)
    orig = {'HP': stats['HP'], 'Attack': stats['Attack'], 'Defense': stats['Defense'], 'Sp. Atk': stats['Sp. Atk'], 'Sp. Def': stats['Sp. Def'], 'Speed': stats['Speed']}
    items_dict = flip_stats_dict(orig) if flip_stat_var.get() else orig
    items = [('HP', items_dict['HP']), ('Attack', items_dict['Attack']), ('Defense', items_dict['Defense']), ('Sp. Atk', items_dict['Sp. Atk']), ('Sp. Def', items_dict['Sp. Def']), ('Speed', items_dict['Speed'])]
    write_stat_section(info_text, items, 'Total BST', stats['BST'])
    info_text.insert(tk.END, "\n")

    # Evolution line (clickable)
    evo_line = (stats.get('evolution line') or '').strip()
    if evo_line:
        info_text.insert(tk.END, 'Evolution: ', 'strong_label')
        parts = [p.strip() for p in evo_line.split(',') if p.strip()]
        for _idx, _pname in enumerate(parts):
            tag = f"evo_{id(info_text)}_{_idx}"
            info_text.tag_config(tag, foreground='#1a73e8', underline=True)
            info_text.tag_bind(tag, '<Button-1>', lambda e, n=_pname, w=info_text: on_click_evo(n, w))
            info_text.tag_bind(tag, '<Enter>', lambda e, w=info_text: w.config(cursor='hand2'))
            info_text.tag_bind(tag, '<Leave>', lambda e, w=info_text: w.config(cursor=''))
            info_text.insert(tk.END, _pname, tag)
            if _idx != len(parts) - 1:
                info_text.insert(tk.END, ', ')
        info_text.insert(tk.END, '\n')
    info_text.insert(tk.END, '\n')

    eff = calculate_type_effectiveness(t1, t2, active_ability=None, passive_ability=stats['Passive'])
    info_text.insert(tk.END, 'Damage Taken: ', 'strong_label')
    info_text.insert(tk.END, "\n")
    info_text.insert(tk.END, "\n")
    _eff_str = format_type_effectiveness(eff)
    _eff_body = _eff_str.split('\n',1)[1] if '\n' in _eff_str else ''
    info_text.insert(tk.END, _eff_body)
    id_label.config(text=f"Pokedex ID: {stats['ID']}")


def populate_active_abilities_for(pokemon2_name: str):
    try:
        if pokemon2_name in pokemon_stats:
            abilities_list = list(dict.fromkeys(pokemon_stats[pokemon2_name].get('Abilities', [])))
        else:
            abilities_list = []
        if not abilities_list:
            abilities_list = ['']
        active_ability_combo['values'] = abilities_list
        current = active_ability_var.get()
        active_ability_var.set(current if current in abilities_list else abilities_list[0])
    except Exception:
        pass

# ===== FUSION + RECALC =====

def calculate_fusion_stats(p1, p2):
    t0 = time.perf_counter()
    logging.info(f"Calculating fusion stats for {p1} and {p2}")
    try:
        if p1 in pokemon_stats and p2 in pokemon_stats:
            fusion_stats = {
                'HP': avg_round_tenth(pokemon_stats[p1]['HP'], pokemon_stats[p2]['HP']),
                'Attack': avg_round_tenth(pokemon_stats[p1]['Attack'], pokemon_stats[p2]['Attack']),
                'Defense': avg_round_tenth(pokemon_stats[p1]['Defense'], pokemon_stats[p2]['Defense']),
                'Sp. Atk': avg_round_tenth(pokemon_stats[p1]['Sp. Atk'], pokemon_stats[p2]['Sp. Atk']),
                'Sp. Def': avg_round_tenth(pokemon_stats[p1]['Sp. Def'], pokemon_stats[p2]['Sp. Def']),
                'Speed': avg_round_tenth(pokemon_stats[p1]['Speed'], pokemon_stats[p2]['Speed']),
            }
            fused_bst = round(sum(fusion_stats.values()), 1)
            fused_type1 = pokemon_stats[p1]['Type_1']
            fused_type2 = (
                pokemon_stats[p2]['Type_2'] if pokemon_stats[p2]['Type_2'] != '' and pokemon_stats[p2]['Type_2'] != pokemon_stats[p1]['Type_1']
                else pokemon_stats[p2]['Type_1'] if pokemon_stats[p2]['Type_1'] != pokemon_stats[p1]['Type_1']
                else ''
            )

            fusion_info.delete('1.0', tk.END)
            fused_type = fused_type1 if fused_type2 == '' or fused_type2 == fused_type1 else f"{fused_type1}/{fused_type2}"

            fusion_info.insert(tk.END, 'Fused Type: ', 'strong_label')

            fusion_info.insert(tk.END, f"{fused_type}\n")

            fusion_info.insert(tk.END, "\n")
            fusion_info.insert(tk.END, "\n")

            fusion_info.insert(tk.END, 'BST:', 'strong_label')
            fusion_info.insert(tk.END, "\n")
            insert_hr(fusion_info)
            items_dict = flip_stats_dict(fusion_stats) if flip_stat_var.get() else fusion_stats
            items = [('HP', items_dict['HP']), ('Attack', items_dict['Attack']), ('Defense', items_dict['Defense']), ('Sp. Atk', items_dict['Sp. Atk']), ('Sp. Def', items_dict['Sp. Def']), ('Speed', items_dict['Speed'])]
            write_stat_section(fusion_info, items, 'Total BST', fused_bst)
            fusion_info.insert(tk.END, "\n")
            # Differences vs. originals
            diff1 = fused_bst - float(pokemon_stats[p1]['BST'])
            diff2 = fused_bst - float(pokemon_stats[p2]['BST'])
            fusion_info.insert(tk.END, f"Difference from {p1}: {format_number_trim(diff1)}\n")
            fusion_info.insert(tk.END, f"Difference from {p2}: {format_number_trim(diff2)}\n\n")

            # Abilities
            abilities = list(dict.fromkeys(pokemon_stats[p2]['Abilities']))
            visible_abilities = [a for i, a in enumerate(abilities) if i != 1] if abilities else []
            fusion_info.insert(tk.END, 'Abilities: ', 'strong_label')
            fusion_info.insert(tk.END, f"{', '.join(visible_abilities)}\n")
            active_ability = (active_ability_var.get() or (abilities[0] if abilities else '')).strip()
            hidden_ability = abilities[1] if len(abilities) > 1 else ''
            if active_ability:
                fusion_info.insert(tk.END, 'Active Ability: ', 'strong_label')
                fusion_info.insert(tk.END, f"{active_ability}\n")
            if hidden_ability and active_ability == hidden_ability:
                fusion_info.insert(tk.END, 'Hidden Ability: ', 'strong_label')
                fusion_info.insert(tk.END, f"{hidden_ability}\n")

            passive_ability = pokemon_stats[p1]['Passive']
            passive_on = passive_active_var.get()
            if passive_ability and passive_on:
                fusion_info.insert(tk.END, 'Passive (from Pokémon 1): ', 'strong_label')
                fusion_info.insert(tk.END, f"{passive_ability} (active)\n")

            # Effects: show only if they actually change type-chart results
            def _ability_effect_summary_line(label: str, ability_name: str):
                abil = _normalize_ability(ability_name)
                eff = ABILITY_EFFECTS.get(abil, {})
                parts = []
                if eff.get('immunities'):
                    parts.append(f"immunities: {', '.join(eff['immunities'])}")
                if eff.get('halve'):
                    parts.append(f"halves: {', '.join(eff['halve'])}")
                if abil == 'WONDER GUARD':
                    parts.append('wonder guard: immune to all non-super-effective')
                if not parts:
                    parts.append('no type-chart effects')
                return f"{label}: " + '; '.join(parts)

            ae = _ability_effect_summary_line('Active effect', active_ability)
            if active_ability and 'no type-chart effects' not in ae:
                fusion_info.insert(tk.END, ae + '\n')
            pe = _ability_effect_summary_line('Passive effect', (passive_ability if passive_on else ''))
            if passive_ability and passive_on and 'no type-chart effects' not in pe:
                fusion_info.insert(tk.END, pe + '\n')
            fusion_info.insert(tk.END, '\n')

            eff = calculate_type_effectiveness(
                fused_type1, fused_type2,
                active_ability=active_ability,
                passive_ability=(passive_ability if passive_on else None)
            )
            fusion_info.insert(tk.END, 'Damage Taken: ', 'strong_label')
            fusion_info.insert(tk.END, "\n")
            fusion_info.insert(tk.END, "\n")
            _eff_str = format_type_effectiveness(eff)
            _eff_body = _eff_str.split('\n',1)[1] if '\n' in _eff_str else ''
            fusion_info.insert(tk.END, _eff_body)
            dt_ms = (time.perf_counter() - t0) * 1000.0
            status_text.set(f"Fused Type: {fused_type} Active: {active_ability or '—'} Passive: {'ON' if passive_on else 'OFF'} Flip: {'ON' if flip_stat_var.get() else 'OFF'} Calc: {dt_ms:.1f} ms")
        else:
            fusion_info.delete('1.0', tk.END)
            fusion_info.insert(tk.END, 'Pokémon not found.')
            status_text.set('Ready.')
    except Exception as e:
        logging.error(f"Error in calculate_fusion_stats: {str(e)}", exc_info=True)
        messagebox.showerror('Error', f"An error occurred during fusion: {str(e)}")


def recalc_if_ready():
    p1 = pokemon1_var.get().strip()
    p2 = pokemon2_var.get().strip()
    if p1 in pokemon_stats and p2 in pokemon_stats:
        calculate_fusion_stats(p1, p2)


def refresh_side_panels():
    try:
        p1 = pokemon1_var.get().strip()
        if p1 in pokemon_stats:
            fill_side_panel(p1, pokemon1_info, pokemon1_id, pokemon1_name)
        p2 = pokemon2_var.get().strip()
        if p2 in pokemon_stats:
            fill_side_panel(p2, pokemon2_info, pokemon2_id, pokemon2_name)
    except Exception:
        pass

# ===== Debouncer =====
class Debouncer:
    def __init__(self, root: tk.Tk, delay_ms=150):
        self.root = root
        self.delay = delay_ms
        self.after_id: Optional[str] = None

    def call(self, func):
        if self.after_id:
            try:
                self.root.after_cancel(self.after_id)
            except Exception:
                pass
        self.after_id = self.root.after(self.delay, func)

# ===== Tooltips (minimal) =====
class Tooltip:
    def __init__(self, widget, text, delay_ms=300):
        self.widget = widget
        self.text = text
        self.delay = delay_ms
        self.tip: Optional[tk.Toplevel] = None
        self.after_id: Optional[str] = None
        widget.bind('<Enter>', self._enter)
        widget.bind('<Leave>', self._leave)

    def _enter(self, _):
        self.after_id = self.widget.after(self.delay, self._show)

    def _leave(self, _):
        if self.after_id:
            try:
                self.widget.after_cancel(self.after_id)
            except Exception:
                pass
            self.after_id = None
        self._hide()

    def _show(self):
        if self.tip or not self.widget.winfo_ismapped():
            return
        x = self.widget.winfo_rootx() + 10
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 8
        self.tip = tk.Toplevel(self.widget)
        self.tip.overrideredirect(True)
        self.tip.attributes('-topmost', True)
        lbl = tk.Label(self.tip, text=self.text, background='#ffffe0', relief=tk.SOLID, borderwidth=1, justify='left')
        lbl.pack(ipadx=6, ipady=4)
        self.tip.geometry(f'+{x}+{y}')

    def _hide(self):
        if self.tip:
            try:
                self.tip.destroy()
            except Exception:
                pass
            self.tip = None

# ===== Selection handlers & search =====

def filter_pokemon(event, filter_var, pokemon_entry, filtered_listbox):
    q = (pokemon_entry.get() or '').strip()
    ql = q.lower()
    tokens = [t for t in re.split(r'\s+', ql) if t] if q else []

    def match_row(name, stats):
        if not tokens:
            return True
        for t in tokens:
            if ':' in t:
                key, val = t.split(':', 1)
                val = val.strip()
                if key == 'type':
                    if val not in (stats.get('Type_1','').lower(), stats.get('Type_2','').lower()):
                        return False
                elif key == 'ability':
                    if not any(val in (a or '').lower() for a in stats.get('Abilities', [])):
                        return False
                elif key == 'passive':
                    if val not in (stats.get('Passive','').lower()):
                        return False
                elif key == 'name':
                    if val not in name.lower():
                        return False
                elif key in ('id', '#'):
                    if not str(stats.get('ID','')).startswith(val):
                        return False
                else:
                    return False
            else:
                # numeric comparator, e.g., bst>300, hp>=100, speed<120
                m = re.match(r'(hp|attack|defense|sp\. atk|sp\. def|speed|bst)\s*(<=|>=|==|=|<|>)\s*(\d+(?:\.\d+)?)', t)
                if m:
                    k, op, sval = m.groups()
                    keymap = {'hp':'HP','attack':'Attack','defense':'Defense','sp. atk':'Sp. Atk','sp. def':'Sp. Def','speed':'Speed','bst':'BST'}
                    skey = keymap.get(k)
                    left = float(stats.get(skey, 0))
                    right = float(sval)
                    ok = ((op == '>' and left > right) or
                          (op == '<' and left < right) or
                          (op in ('=','==') and left == right) or
                          (op == '>=') and left >= right or
                          (op == '<=') and left <= right)
                    if not ok:
                        return False
                else:
                    id_term = t.lstrip('#')
                    if id_term.isdigit():
                        if int(id_term) != stats.get('ID', -999999):
                            return False
                    elif (t not in name.lower() and
                          t not in stats.get('Type_1','').lower() and
                          (t not in stats.get('Type_2','').lower() if stats.get('Type_2') else True) and
                          not any(t in (a or '').lower() for a in stats.get('Abilities', [])) and
                          t not in (stats.get('Passive','').lower())):
                        return False
        return True

    filtered_names = [name for name, stats in pokemon_stats.items() if match_row(name, stats)]
    filtered_listbox.delete(0, tk.END)
    for name in filtered_names:
        filtered_listbox.insert(tk.END, name)


def on_select(event, selected_var, filter_var, pokemon_name, pokemon_info, pokemon_id, sticky_filters_var):
    selection = event.widget.curselection()
    if not selection:
        return
    selected_pokemon = event.widget.get(selection[0])
    selected_var.set(selected_pokemon)
    # Optionally mirror selection into the search box if sticky is OFF
    if not sticky_filters_var.get():
        filter_var.set(selected_pokemon)
    fill_side_panel(selected_pokemon, pokemon_info, pokemon_id, pokemon_name)
    if event.widget == pokemon2_filtered_listbox:
        populate_active_abilities_for(selected_pokemon)
        recalc_if_ready()
    elif event.widget == pokemon1_filtered_listbox:
        recalc_if_ready()

# Clickable evolution names

def on_click_evo(pokemon_name: str, source_text_widget: tk.Text):
    try:
        name = (pokemon_name or '').strip()
        if name not in pokemon_stats:
            try:
                messagebox.showwarning('Not found', "'{}' was not found in the data.".format(name))
            except Exception:
                pass
            return
        if 'pokemon1_info' in globals() and source_text_widget is pokemon1_info:
            pokemon1_var.set(name)
            fill_side_panel(name, pokemon1_info, pokemon1_id, pokemon1_name)
            recalc_if_ready()
        elif 'pokemon2_info' in globals() and source_text_widget is pokemon2_info:
            pokemon2_var.set(name)
            fill_side_panel(name, pokemon2_info, pokemon2_id, pokemon2_name)
            populate_active_abilities_for(name)
            recalc_if_ready()
        else:
            pokemon1_var.set(name)
            fill_side_panel(name, pokemon1_info, pokemon1_id, pokemon1_name)
            recalc_if_ready()
    except Exception as e:
        logging.error(f'Error handling evolution click: {e}', exc_info=True)


def swap_pokemon():
    p1 = pokemon1_var.get().strip()
    p2 = pokemon2_var.get().strip()
    pokemon1_var.set(p2)
    pokemon2_var.set(p1)

    if p2 in pokemon_stats:
        fill_side_panel(p2, pokemon1_info, pokemon1_id, pokemon1_name)
    else:
        pokemon1_info.delete('1.0', tk.END)
        pokemon1_name.config(text='')
        pokemon1_id.config(text='')

    if p1 in pokemon_stats:
        fill_side_panel(p1, pokemon2_info, pokemon2_id, pokemon2_name)
    else:
        pokemon2_info.delete('1.0', tk.END)
        pokemon2_name.config(text='')
        pokemon2_id.config(text='')

    populate_active_abilities_for(p1)
    recalc_if_ready()



def show_filter_help():
    try:
        message = """Search filters:
  name:TERM      — match name substring
  type:TYPE      — match type1 or type2 (e.g., type:fire)
  ability:NAME   — match any listed ability
  passive:NAME   — match passive ability
  id:NNN or #NNN — match Pokédex ID prefix or exact with #
  Numeric: hp|attack|defense|sp. atk|sp. def|speed|bst with >, <, >=, <=, =
    examples: hp>=100  speed<120  bst>500
"""
        messagebox.showinfo('Search Filter Help', message)
    except Exception:
        pass

# ===== GUI =====
load_pokemon_data_into(pokemon_stats)
root = tk.Tk()
root.title(f"PokéRogue Fusion Calculator — build {BUILD_TAG}")
root.geometry('1550x540')

menubar = tk.Menu(root)
root.config(menu=menubar)
file_menu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label='File', menu=file_menu)
file_menu.add_command(label='Exit', command=root.quit)

challenges_menu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label='Challenges', menu=challenges_menu)


resources_menu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label='Resources', menu=resources_menu)
resources_menu.add_command(label='Pokémon Database', command=open_pokemondb)
resources_menu.add_command(label='Type Calculator', command=open_type_calculator)
resources_menu.add_command(label='PokeRogue Pokedex', command=open_pokedex)
help_menu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label='Help', menu=help_menu)
help_menu.add_command(label='Search Filters…', command=show_filter_help)

options_menu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label='Options', menu=options_menu)
sticky_filters_var = tk.BooleanVar(value=True)


options_menu.add_checkbutton(label='Keep search text when selecting', variable=sticky_filters_var, onvalue=True, offvalue=False)

flip_stat_var = tk.BooleanVar(value=False)
challenges_menu.add_checkbutton(label='Flip Stat Challenge', onvalue=True, offvalue=False, variable=flip_stat_var, command=lambda: (refresh_side_panels(), recalc_if_ready()))

main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True, padx=10)

for i in range(20):
    main_frame.grid_rowconfigure(i, weight=1)
for i in range(5):
    main_frame.grid_columnconfigure(i, weight=1)

search_info_label = tk.Label(main_frame, text='Search by name, type, ability, or passive', font=('Arial', 10, 'bold'))
search_info_label.grid(row=0, column=0, columnspan=5, pady=5)

# Left search (label next to entry)
pokemon1_label = tk.Label(main_frame, text='Search Pokémon 1:', font=('Arial', 10))
pokemon1_label.grid(row=2, column=0, padx=6, sticky='e')

# Separate filter (search box) variables from selected Pokémon variables (sticky filters)
pokemon1_var = tk.StringVar()         # selected name (used for fusion)
pokemon1_filter_var = tk.StringVar()  # search box text

pokemon1_entry = ttk.Entry(main_frame, textvariable=pokemon1_filter_var, width=20)
pokemon1_entry.grid(row=2, column=1, padx=6, sticky='w')

# Buttons (keep above the options row)
button_frame = tk.Frame(main_frame)
button_frame.grid(row=1, column=2)

fusion_button = tk.Button(button_frame, text='Fuse', command=lambda: calculate_fusion_stats(pokemon1_var.get(), pokemon2_var.get()))
fusion_button.pack(side=tk.LEFT, padx=5)

swap_button = tk.Button(button_frame, text='Swap', command=swap_pokemon)
swap_button.pack(side=tk.LEFT, padx=5)


def clear_selections():
    pokemon1_var.set('')
    pokemon2_var.set('')
    pokemon1_filter_var.set('')
    pokemon2_filter_var.set('')

    pokemon1_filtered_listbox.selection_clear(0, tk.END)
    pokemon2_filtered_listbox.selection_clear(0, tk.END)

    pokemon1_name.config(text='')
    pokemon2_name.config(text='')

    pokemon1_info.delete('1.0', tk.END)
    pokemon2_info.delete('1.0', tk.END)
    fusion_info.delete('1.0', tk.END)

    pokemon1_id.config(text='')
    pokemon2_id.config(text='')

    pokemon1_filtered_listbox.delete(0, tk.END)
    pokemon2_filtered_listbox.delete(0, tk.END)

    for name in pokemon_stats:
        pokemon1_filtered_listbox.insert(tk.END, name)
        pokemon2_filtered_listbox.insert(tk.END, name)

    try:
        active_ability_combo['values'] = ['']
        active_ability_var.set('')
    except Exception:
        pass
    try:
        status_text.set('Ready.')
    except Exception:
        pass

clear_button = tk.Button(button_frame, text='Clear', command=clear_selections)
clear_button.pack(side=tk.LEFT, padx=5)

# Options row
options_frame = tk.Frame(main_frame)
options_frame.grid(row=2, column=2, sticky='n', pady=2)
options_frame.grid_columnconfigure(0, weight=1)
options_frame.grid_columnconfigure(1, weight=1)

active_ability_var = tk.StringVar(value='')
passive_active_var = tk.BooleanVar(value=True)

active_ability_label = tk.Label(options_frame, text='Active Ability:')
active_ability_label.grid(row=0, column=0, sticky='e', padx=5, pady=(0, 2))

active_ability_combo = ttk.Combobox(options_frame, textvariable=active_ability_var, width=22, state='readonly')
active_ability_combo.grid(row=0, column=1, sticky='w', padx=5, pady=(0, 2))

passive_check = ttk.Checkbutton(options_frame, text='Passive Active', variable=passive_active_var)
passive_check.grid(row=1, column=0, columnspan=2, padx=5, pady=(2,0), sticky='n')

active_ability_combo.bind('<<ComboboxSelected>>', lambda e: recalc_if_ready())
passive_check.configure(command=recalc_if_ready)

# Right search (label next to entry)
pokemon2_label = tk.Label(main_frame, text='Search Pokémon 2:', font=('Arial', 10))
pokemon2_label.grid(row=2, column=3, padx=6, sticky='e')

pokemon2_var = tk.StringVar()         # selected name (used for fusion)
pokemon2_filter_var = tk.StringVar()  # search box text

pokemon2_entry = ttk.Entry(main_frame, textvariable=pokemon2_filter_var, width=20)
pokemon2_entry.grid(row=2, column=4, padx=6, sticky='w')

# Left column
pokemon1_filtered_label = tk.Label(main_frame, text='Pokémon 1:', font=('Arial', 10, 'bold'))
pokemon1_filtered_label.grid(row=3, column=0, sticky=tk.N, padx=10)

pokemon1_filtered_listbox = tk.Listbox(main_frame, width=26)
pokemon1_filtered_listbox.grid(row=4, column=0, rowspan=10, sticky=tk.NSEW, padx=10)

pokemon1_name = tk.Label(main_frame, font=('Arial', 12, 'bold'))
pokemon1_name.grid(row=3, column=1, sticky=tk.N, padx=10)

pokemon1_info = tk.Text(main_frame, width=50, height=20, font=('TkFixedFont', 10))
pokemon1_info.grid(row=4, column=1, rowspan=10, sticky=tk.NSEW, padx=10)

pokemon1_id = tk.Label(main_frame, font=('Arial', 10))
pokemon1_id.grid(row=14, column=1, sticky=tk.N, padx=10)

# Center result
fusion_caption = tk.Label(main_frame, text='Fusion Result', font=('Arial', 12, 'bold'))
fusion_caption.grid(row=3, column=2, sticky=tk.N, padx=10)

fusion_info = tk.Text(main_frame, width=50, height=20, font=('TkFixedFont', 10))
fusion_info.grid(row=4, column=2, rowspan=10, sticky=tk.NSEW, padx=10)

# Right column
pokemon2_name = tk.Label(main_frame, font=('Arial', 12, 'bold'))
pokemon2_name.grid(row=3, column=3, sticky=tk.N, padx=10)

pokemon2_info = tk.Text(main_frame, width=50, height=20, font=('TkFixedFont', 10))
pokemon2_info.grid(row=4, column=3, rowspan=10, sticky=tk.NSEW, padx=10)

pokemon2_id = tk.Label(main_frame, font=('Arial', 10))
pokemon2_id.grid(row=14, column=3, sticky=tk.N, padx=10)

pokemon2_filtered_label = tk.Label(main_frame, text='Pokémon 2:', font=('Arial', 10, 'bold'))
pokemon2_filtered_label.grid(row=3, column=4, sticky=tk.N, padx=10)

pokemon2_filtered_listbox = tk.Listbox(main_frame, width=26)
pokemon2_filtered_listbox.grid(row=4, column=4, rowspan=10, sticky=tk.NSEW, padx=10)

pokemon1_filtered_listbox.bind('<<ListboxSelect>>', lambda e: on_select(e, pokemon1_var, pokemon1_filter_var, pokemon1_name, pokemon1_info, pokemon1_id, sticky_filters_var))
pokemon2_filtered_listbox.bind('<<ListboxSelect>>', lambda e: on_select(e, pokemon2_var, pokemon2_filter_var, pokemon2_name, pokemon2_info, pokemon2_id, sticky_filters_var))

for name in pokemon_stats:
    pokemon1_filtered_listbox.insert(tk.END, name)
    pokemon2_filtered_listbox.insert(tk.END, name)

# Debounced search bindings
debounce_p1 = Debouncer(root, delay_ms=150)
debounce_p2 = Debouncer(root, delay_ms=150)

pokemon1_entry.bind('<KeyRelease>', lambda e: debounce_p1.call(lambda: filter_pokemon(e, pokemon1_filter_var, pokemon1_entry, pokemon1_filtered_listbox)))
pokemon2_entry.bind('<KeyRelease>', lambda e: debounce_p2.call(lambda: filter_pokemon(e, pokemon2_filter_var, pokemon2_entry, pokemon2_filtered_listbox)))

# Mini status bar (bottom)
status_text = tk.StringVar(value='Ready.')
status_bar = tk.Label(root, textvariable=status_text, anchor='w', relief='sunken', padx=6)
status_bar.pack(side=tk.BOTTOM, fill=tk.X)



print(f"[FusionCalc] Running build {BUILD_TAG}")
root.mainloop()
