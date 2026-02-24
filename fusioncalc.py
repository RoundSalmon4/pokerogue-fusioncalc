# PokéRogue Fusion Calculator — build 2026-02-24
import tkinter as tk
from tkinter import ttk, messagebox
import csv
import logging
import sys
import webbrowser
import time
from typing import Dict, Any, Optional
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
BUILD_TAG = "2026-02-24"

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

def open_pokedex(): webbrowser.open("https://ydarissep.github.io/PokeRogue-Pokedex/")

# ===== Ability rule mapping =====
ABILITY_EFFECTS = {
    'LEVITATE': {'immunities': ['Ground']},
    'EARTH EATER': {'immunities': ['Ground']},
    'WATER ABSORB': {'immunities': ['Water']},
    'DRY SKIN': {'immunities': ['Water']},
    'STORM DRAIN': {'immunities': ['Water']},
    'FLASH FIRE': {'immunities': ['Fire']},
    'WELL-BAKED BODY': {'immunities': ['Fire']},
    'VOLT ABSORB': {'immunities': ['Electric']},
    'LIGHTNING ROD': {'immunities': ['Electric']},
    'MOTOR DRIVE': {'immunities': ['Electric']},
    'SAP SIPPER': {'immunities': ['Grass']},
    'SAPSIPPER': {'immunities': ['Grass']},
    'PURIFYING SALT': {'immunities': ['Ghost']},
    'THICK FAT': {'halve': ['Fire', 'Ice']},
    'HEATPROOF': {'halve': ['Fire']},
    'WATER BUBBLE': {'halve': ['Fire']},
}

def _normalize_ability(name: str) -> str:
    return (name or '').strip().upper()

# ===== Type chart =====
type_effectiveness = {
    'Normal':  {'weaknesses': ['Fighting'], 'resistances': [], 'immunities': ['Ghost']},
    'Fire':    {'weaknesses': ['Water', 'Ground', 'Rock'], 'resistances': ['Fire', 'Grass', 'Ice', 'Bug', 'Steel', 'Fairy'], 'immunities': []},
    'Water':   {'weaknesses': ['Electric', 'Grass'], 'resistances': ['Fire', 'Water', 'Ice', 'Steel'], 'immunities': []},
    'Grass':   {'weaknesses': ['Fire', 'Ice', 'Poison', 'Flying', 'Bug'], 'resistances': ['Water', 'Electric', 'Grass', 'Ground'], 'immunities': []},
    'Electric':{'weaknesses': ['Ground'], 'resistances': ['Electric', 'Flying', 'Steel'], 'immunities': []},
    'Ice':     {'weaknesses': ['Fire', 'Fighting', 'Rock', 'Steel'], 'resistances': ['Ice'], 'immunities': []},
    'Fighting':{'weaknesses': ['Flying', 'Psychic', 'Fairy'], 'resistances': ['Bug', 'Rock', 'Dark'], 'immunities': []},
    'Poison':  {'weaknesses': ['Ground', 'Psychic'], 'resistances': ['Grass', 'Fighting', 'Poison', 'Bug', 'Fairy'], 'immunities': []},
    'Ground':  {'weaknesses': ['Water', 'Grass', 'Ice'], 'resistances': ['Poison', 'Rock'], 'immunities': ['Electric']},
    'Flying':  {'weaknesses': ['Electric', 'Ice', 'Rock'], 'resistances': ['Grass', 'Fighting', 'Bug'], 'immunities': ['Ground']},
    'Psychic': {'weaknesses': ['Bug', 'Ghost', 'Dark'], 'resistances': ['Fighting', 'Psychic'], 'immunities': []},
    'Bug':     {'weaknesses': ['Fire', 'Flying', 'Rock'], 'resistances': ['Grass', 'Fighting', 'Ground'], 'immunities': []},
    'Rock':    {'weaknesses': ['Water', 'Grass', 'Fighting', 'Ground', 'Steel'], 'resistances': ['Normal', 'Fire', 'Poison', 'Flying'], 'immunities': []},
    'Ghost':   {'weaknesses': ['Ghost', 'Dark'], 'resistances': ['Poison', 'Bug'], 'immunities': ['Normal', 'Fighting']},
    'Dragon':  {'weaknesses': ['Ice', 'Dragon', 'Fairy'], 'resistances': ['Fire', 'Water', 'Grass', 'Electric'], 'immunities': []},
    'Dark':    {'weaknesses': ['Fighting', 'Bug', 'Fairy'], 'resistances': ['Ghost', 'Dark'], 'immunities': ['Psychic']},
    'Steel':   {'weaknesses': ['Fire', 'Fighting', 'Ground'], 'resistances': ['Normal', 'Grass', 'Ice', 'Flying', 'Psychic', 'Bug', 'Rock', 'Dragon', 'Steel', 'Fairy'], 'immunities': ['Poison']},
    'Fairy':   {'weaknesses': ['Poison', 'Steel'], 'resistances': ['Fighting', 'Bug', 'Dark'], 'immunities': ['Dragon']}
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
    result = "Type Effectiveness:\n"
    grouped: Dict[float, list] = {}
    for t, value in effectiveness.items():
        grouped.setdefault(value, []).append(t)
    for value in sorted(grouped.keys(), reverse=True):
        types = grouped[value]
        if value == 0:
            result += f"Immune: {', '.join(types)}\n"
        elif value == 0.25:
            result += f"1/4x damage: {', '.join(types)}\n"
        elif value == 0.5:
            result += f"1/2x damage: {', '.join(types)}\n"
        elif value == 1:
            result += f"1x damage: {', '.join(types)}\n"
        elif value == 2:
            result += f"2x damage: {', '.join(types)}\n"
        elif value == 4:
            result += f"4x damage: {', '.join(types)}\n"
    return result.strip()

def _ability_effect_summary_line(label: str, ability_name: str):
    abil = _normalize_ability(ability_name)
    eff = ABILITY_EFFECTS.get(abil, {})
    parts = []
    if eff.get('immunities'):
        parts.append(f"immunities: {', '.join(eff['immunities'])}")
    if eff.get('halve'):
        parts.append(f"halves: {', '.join(eff['halve'])}")
    if abil == 'WONDER GUARD':
        parts.append("wonder guard: immune to all non-super-effective")
    if not parts:
        parts.append("no type-chart effects")
    return f"{label}: " + "; ".join(parts)

# ===== Small helpers for UI reuse =====

def fill_side_panel(name: str, info_text: tk.Text, id_label: tk.Label, name_label: tk.Label):
    if not name or name not in pokemon_stats:
        return
    name_label.config(text=name)
    stats = pokemon_stats[name]
    t1, t2 = stats['Type_1'], stats['Type_2']
    ptype = t1 if (not t2 or t2 == t1) else f"{t1}/{t2}"

    info_text.delete('1.0', tk.END)
    info_text.insert(tk.END, f"Type: {ptype}\n\n")
    info_text.insert(tk.END, f"HP: {stats['HP']}\n")
    info_text.insert(tk.END, f"Attack: {stats['Attack']}\n")
    info_text.insert(tk.END, f"Defense: {stats['Defense']}\n")
    info_text.insert(tk.END, f"Sp. Atk: {stats['Sp. Atk']}\n")
    info_text.insert(tk.END, f"Sp. Def: {stats['Sp. Def']}\n")
    info_text.insert(tk.END, f"Speed: {stats['Speed']}\n\n")
    info_text.insert(tk.END, f"BST: {stats['BST']}\n\n")

    abilities = list(dict.fromkeys(stats.get('Abilities', [])))
    info_text.insert(tk.END, f"Abilities: {', '.join(abilities)}\n")
    hidden_ability = abilities[1] if len(abilities) > 1 else ''
    if hidden_ability:
        info_text.insert(tk.END, f"Hidden Ability: {hidden_ability}\n")

    passive_ability = stats['Passive']
    if passive_ability and passive_ability not in abilities:
        info_text.insert(tk.END, f"Passive: {passive_ability}\n")
    else:
        info_text.insert(tk.END, "\n")

    # Evolution line (clickable) under Passive
    evo_line = (stats.get('evolution line') or '').strip()
    if evo_line:
        info_text.insert(tk.END, 'Evolution: ')
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

    eff = calculate_type_effectiveness(t1, t2, active_ability=None, passive_ability=passive_ability)
    info_text.insert(tk.END, format_type_effectiveness(eff))
    id_label.config(text=f"Pokedex ID: {stats['ID']}")


def populate_active_abilities_for(pokemon2_name: str):
    try:
        if pokemon2_name in pokemon_stats:
            abilities_list = list(dict.fromkeys(pokemon_stats[pokemon2_name].get('Abilities', [])))
        else:
            abilities_list = []
        if not abilities_list:
            abilities_list = [""]
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
                'HP': (pokemon_stats[p1]['HP'] + pokemon_stats[p2]['HP']) // 2,
                'Attack': (pokemon_stats[p1]['Attack'] + pokemon_stats[p2]['Attack']) // 2,
                'Defense': (pokemon_stats[p1]['Defense'] + pokemon_stats[p2]['Defense']) // 2,
                'Sp. Atk': (pokemon_stats[p1]['Sp. Atk'] + pokemon_stats[p2]['Sp. Atk']) // 2,
                'Sp. Def': (pokemon_stats[p1]['Sp. Def'] + pokemon_stats[p2]['Sp. Def']) // 2,
                'Speed': (pokemon_stats[p1]['Speed'] + pokemon_stats[p2]['Speed']) // 2,
            }
            fused_bst = sum(fusion_stats.values())

            fused_type1 = pokemon_stats[p1]['Type_1']
            fused_type2 = (
                pokemon_stats[p2]['Type_2'] if pokemon_stats[p2]['Type_2'] != '' and pokemon_stats[p2]['Type_2'] != pokemon_stats[p1]['Type_1']
                else pokemon_stats[p2]['Type_1'] if pokemon_stats[p2]['Type_1'] != pokemon_stats[p1]['Type_1']
                else ''
            )

            fusion_info.delete('1.0', tk.END)
            fused_type = fused_type1 if fused_type2 == '' or fused_type2 == fused_type1 else f"{fused_type1}/{fused_type2}"
            fusion_info.insert(tk.END, 'Fusion Summary\n')
            fusion_info.insert(tk.END, f"Fused Type: {fused_type}\n\n")
            for stat, value in fusion_stats.items():
                fusion_info.insert(tk.END, f"{stat}: {value}\n")
            fusion_info.insert(tk.END, f"\nBST: {fused_bst}\n")
            fusion_info.insert(tk.END, f"Difference from {p1}: {fused_bst - pokemon_stats[p1]['BST']}\n")
            fusion_info.insert(tk.END, f"Difference from {p2}: {fused_bst - pokemon_stats[p2]['BST']}\n\n")

            abilities = list(dict.fromkeys(pokemon_stats[p2]['Abilities']))
            fusion_info.insert(tk.END, f"Abilities: {', '.join(abilities)}\n")
            active_ability = (active_ability_var.get() or (abilities[0] if abilities else '')).strip()
            hidden_ability = abilities[1] if len(abilities) > 1 else ''
            if active_ability:
                fusion_info.insert(tk.END, f"Active Ability (from Pokémon 2): {active_ability}\n")
            if hidden_ability:
                fusion_info.insert(tk.END, f"Hidden Ability (2nd listed): {hidden_ability}\n")

            passive_ability = pokemon_stats[p1]['Passive']
            passive_on = passive_active_var.get()
            if passive_ability:
                fusion_info.insert(tk.END, f"Passive (from Pokémon 1): {passive_ability}{' (active)' if passive_on else ' (inactive)'}\n")

            fusion_info.insert(tk.END, _ability_effect_summary_line('Active effect', active_ability) + '\n')
            fusion_info.insert(tk.END, _ability_effect_summary_line('Passive effect', (passive_ability if passive_on else '')) + '\n\n')

            eff = calculate_type_effectiveness(
                fused_type1, fused_type2,
                active_ability=active_ability,
                passive_ability=(passive_ability if passive_on else None)
            )
            fusion_info.insert(tk.END, format_type_effectiveness(eff))

            dt_ms = (time.perf_counter() - t0) * 1000.0
            status_text.set(f"Fused Type: {fused_type} | Active: {active_ability or '—'} | Passive: {'ON' if passive_on else 'OFF'} | Calc: {dt_ms:.1f} ms")
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

# ===== Selection handlers =====

def filter_pokemon(event, pokemon_var, pokemon_entry, filtered_listbox):
    search_term = (pokemon_entry.get() or '').lower().strip()
    filtered_names = []
    id_term = search_term.lstrip('#')
    is_id = id_term.isdigit()
    for name, stats in pokemon_stats.items():
        name_l = name.lower()
        t1 = stats.get('Type_1', '')
        t2 = stats.get('Type_2', '')
        abils = stats.get('Abilities', [])
        passive = stats.get('Passive', '')
        match = False
        if search_term and search_term in name_l:
            match = True
        elif is_id and int(id_term) == stats.get('ID', -999999):
            match = True
        elif search_term and (search_term in t1.lower() or (t2 and search_term in t2.lower())):
            match = True
        elif search_term and any(search_term in (a or '').lower() for a in abils):
            match = True
        elif search_term and search_term in (passive or '').lower():
            match = True
        elif search_term == '':
            match = True
        if match:
            filtered_names.append(name)
    filtered_listbox.delete(0, tk.END)
    for name in filtered_names:
        filtered_listbox.insert(tk.END, name)

def on_select(event, pokemon_var, pokemon_name, pokemon_info, pokemon_id):
    selection = event.widget.curselection()
    if not selection:
        return
    selected_pokemon = event.widget.get(selection[0])
    pokemon_var.set(selected_pokemon)
    fill_side_panel(selected_pokemon, pokemon_info, pokemon_id, pokemon_name)
    if event.widget == pokemon2_filtered_listbox:
        populate_active_abilities_for(selected_pokemon)
        recalc_if_ready()
    elif event.widget == pokemon1_filtered_listbox:
        recalc_if_ready()

# NEW: handler for clickable evolution names

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

# ===== GUI =====
load_pokemon_data_into(pokemon_stats)
root = tk.Tk()
root.title(f"PokéRogue Fusion Calculator — build {BUILD_TAG}")
root.geometry('1550x500')

menubar = tk.Menu(root)
root.config(menu=menubar)
file_menu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label='File', menu=file_menu)
file_menu.add_command(label='Exit', command=root.quit)
theme_menu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label='Theme', menu=theme_menu)
resources_menu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label='Resources', menu=resources_menu)
resources_menu.add_command(label='Pokémon Database', command=open_pokemondb)
resources_menu.add_command(label='Type Calculator', command=open_type_calculator)
resources_menu.add_command(label='PokeRogue Pokedex', command=open_pokedex)

main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True, padx=10)
for i in range(20):
    main_frame.grid_rowconfigure(i, weight=1)
for i in range(5):
    main_frame.grid_columnconfigure(i, weight=1)
search_info_label = tk.Label(main_frame, text='Search by name, type, ability, or passive', font=('Arial', 10, 'bold'))
search_info_label.grid(row=0, column=0, columnspan=5, pady=5)

# Left search
pokemon1_label = tk.Label(main_frame, text='Search Pokémon 1:')
pokemon1_label.grid(row=1, column=1, padx=10, sticky='w')
pokemon1_var = tk.StringVar()
pokemon1_entry = ttk.Entry(main_frame, textvariable=pokemon1_var, width=20)
pokemon1_entry.grid(row=2, column=1, padx=10, sticky='w')

# Buttons
button_frame = tk.Frame(main_frame)
button_frame.grid(row=1, column=2)
fusion_button = tk.Button(button_frame, text='Fuse', command=lambda: calculate_fusion_stats(pokemon1_var.get(), pokemon2_var.get()))
fusion_button.pack(side=tk.LEFT, padx=5)
swap_button = tk.Button(button_frame, text='Swap', command=swap_pokemon)
swap_button.pack(side=tk.LEFT, padx=5)

def clear_selections():
    pokemon1_var.set('')
    pokemon2_var.set('')
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
active_ability_label = tk.Label(options_frame, text='Active Ability (from Pokémon 2):')
active_ability_label.grid(row=0, column=0, sticky='e', padx=5, pady=(0, 2))
active_ability_combo = ttk.Combobox(options_frame, textvariable=active_ability_var, width=22, state='readonly')
active_ability_combo.grid(row=0, column=1, sticky='w', padx=5, pady=(0, 2))
passive_check = tk.Checkbutton(options_frame, text='Passive Active', variable=passive_active_var)
passive_check.grid(row=1, column=0, columnspan=2, padx=5)
active_ability_combo.bind('<<ComboboxSelected>>', lambda e: recalc_if_ready())
passive_check.configure(command=recalc_if_ready)

# Right search
pokemon2_label = tk.Label(main_frame, text='Search Pokémon 2:')
pokemon2_label.grid(row=1, column=3, padx=10, sticky='e')
pokemon2_var = tk.StringVar()
pokemon2_entry = ttk.Entry(main_frame, textvariable=pokemon2_var, width=20)
pokemon2_entry.grid(row=2, column=3, padx=10, sticky='e')

# Left column
pokemon1_filtered_label = tk.Label(main_frame, text='Pokémon 1:', font=('Arial', 10, 'bold'))
pokemon1_filtered_label.grid(row=3, column=0, sticky=tk.N, padx=10)
pokemon1_filtered_listbox = tk.Listbox(main_frame, width=26)
pokemon1_filtered_listbox.grid(row=4, column=0, rowspan=10, sticky=tk.NSEW, padx=10)
pokemon1_name = tk.Label(main_frame, font=('Arial', 12, 'bold'))
pokemon1_name.grid(row=3, column=1, sticky=tk.N, padx=10)
pokemon1_info = tk.Text(main_frame, width=50, height=20)
pokemon1_info.grid(row=4, column=1, rowspan=10, sticky=tk.NSEW, padx=10)
pokemon1_id = tk.Label(main_frame, font=('Arial', 10))
pokemon1_id.grid(row=14, column=1, sticky=tk.N, padx=10)

# Center result
fusion_caption = tk.Label(main_frame, text='Fusion Result (Hidden Ability = 2nd listed ability)', font=('Arial', 12, 'bold'))
fusion_caption.grid(row=3, column=2, sticky=tk.N, padx=10)
fusion_info = tk.Text(main_frame, width=50, height=20)
fusion_info.grid(row=4, column=2, rowspan=10, sticky=tk.NSEW, padx=10)

# Right column
pokemon2_name = tk.Label(main_frame, font=('Arial', 12, 'bold'))
pokemon2_name.grid(row=3, column=3, sticky=tk.N, padx=10)
pokemon2_info = tk.Text(main_frame, width=50, height=20)
pokemon2_info.grid(row=4, column=3, rowspan=10, sticky=tk.NSEW, padx=10)
pokemon2_id = tk.Label(main_frame, font=('Arial', 10))
pokemon2_id.grid(row=14, column=3, sticky=tk.N, padx=10)

pokemon2_filtered_label = tk.Label(main_frame, text='Pokémon 2:', font=('Arial', 10, 'bold'))
pokemon2_filtered_label.grid(row=3, column=4, sticky=tk.N, padx=10)
pokemon2_filtered_listbox = tk.Listbox(main_frame, width=26)
pokemon2_filtered_listbox.grid(row=4, column=4, rowspan=10, sticky=tk.NSEW, padx=10)

pokemon1_filtered_listbox.bind('<<ListboxSelect>>', lambda e: on_select(e, pokemon1_var, pokemon1_name, pokemon1_info, pokemon1_id))
pokemon2_filtered_listbox.bind('<<ListboxSelect>>', lambda e: on_select(e, pokemon2_var, pokemon2_name, pokemon2_info, pokemon2_id))
for name in pokemon_stats:
    pokemon1_filtered_listbox.insert(tk.END, name)
    pokemon2_filtered_listbox.insert(tk.END, name)

# Debounced search bindings
debounce_p1 = Debouncer(root, delay_ms=150)
debounce_p2 = Debouncer(root, delay_ms=150)
pokemon1_entry.bind('<KeyRelease>', lambda e: debounce_p1.call(lambda: filter_pokemon(e, pokemon1_var, pokemon1_entry, pokemon1_filtered_listbox)))
pokemon2_entry.bind('<KeyRelease>', lambda e: debounce_p2.call(lambda: filter_pokemon(e, pokemon2_var, pokemon2_entry, pokemon2_filtered_listbox)))

# Mini status bar (bottom)
status_text = tk.StringVar(value='Ready.')
status_bar = tk.Label(root, textvariable=status_text, anchor='w', relief='sunken', padx=6)
status_bar.pack(side=tk.BOTTOM, fill=tk.X)

# Simple theme

def toggle_theme():
    current_bg = root.cget('background')
    if current_bg == '#f0f0f0':
        apply_dark()
    else:
        apply_light()

def apply_dark():
    bg = '#2b2b2b'
    fg = '#ffffff'
    entry_bg = '#3c3f41'
    btn_bg = '#4e5254'
    btn_fg = '#ffffff'
    root.configure(bg=bg)
    main_frame.configure(bg=bg)
    for w in main_frame.winfo_children():
        if isinstance(w, tk.Label):
            w.configure(bg=bg, fg=fg)
        elif isinstance(w, tk.Button):
            w.configure(bg=btn_bg, fg=btn_fg)
        elif isinstance(w, tk.Listbox):
            w.configure(bg=entry_bg, fg=fg)
        elif isinstance(w, tk.Text):
            w.configure(bg=entry_bg, fg=fg)
        elif isinstance(w, tk.Frame):
            w.configure(bg=bg)
            for c in w.winfo_children():
                if isinstance(c, tk.Button):
                    c.configure(bg=btn_bg, fg=btn_fg)

def apply_light():
    bg = '#f0f0f0'
    fg = '#000000'
    root.configure(bg=bg)
    main_frame.configure(bg=bg)
    for w in main_frame.winfo_children():
        if isinstance(w, tk.Label):
            w.configure(bg=bg, fg=fg)
        elif isinstance(w, tk.Button):
            w.configure(bg=bg, fg=fg)
        elif isinstance(w, tk.Listbox):
            w.configure(bg=bg, fg=fg)
        elif isinstance(w, tk.Text):
            w.configure(bg=bg, fg=fg)
        elif isinstance(w, tk.Frame):
            w.configure(bg=bg)
            for c in w.winfo_children():
                if isinstance(c, tk.Button):
                    c.configure(bg=bg, fg=fg)

theme_menu.add_command(label='Toggle Theme', command=toggle_theme)
apply_light()
print(f"[FusionCalc] Running build {BUILD_TAG}")
root.mainloop()
