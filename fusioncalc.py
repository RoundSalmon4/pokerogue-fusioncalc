# BUILD_HASH: 8f80b4b35fa2


import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import logging
import sys
import webbrowser
import time
import re
from typing import Dict, Any, Optional
from tkinter import font as tkfont
def log_calc(message: str):
 try:
  if 'logs_master_var' in globals() and 'calc_logs_var' in globals() and logs_master_var.get() and calc_logs_var.get():
   lvl = logging.DEBUG if ('verbose_logs_var' in globals() and verbose_logs_var.get()) else logging.INFO
   logging.log(lvl, message)
 except Exception:
  pass

def dump_ui_layout_metrics(root_widget=None):
    try:
        if root_widget is None and 'root' in globals():
            root_widget = root
        if not root_widget:
            return
        widgets = []
        def walk(w):
            widgets.append(w)
            for c in w.winfo_children():
                walk(c)
        walk(root_widget)
        lvl = logging.DEBUG if ('verbose_logs_var' in globals() and verbose_logs_var.get()) else logging.INFO
        logging.log(lvl, f"[UILayout] total_widgets={len(widgets)}")
        for w in widgets[:500]:
            try:
                cls = w.winfo_class()
                geom = (w.winfo_x(), w.winfo_y(), w.winfo_width(), w.winfo_height())
                vis = w.winfo_ismapped()
                logging.log(lvl, f"[UILayout] {str(w)} class={cls} mapped={vis} geom={geom}")
            except Exception as e:
                logging.log(lvl, f"[UILayout] {str(w)} error={e}")
    finally:
        try:
            if 'ui_layout_logs_var' in globals():
                ui_layout_logs_var.set(False)
        except Exception:
            pass

def dump_widget_font_tag_logs():
    try:
        lvl = logging.DEBUG if ('verbose_logs_var' in globals() and verbose_logs_var.get()) else logging.INFO
        targets = []
        for name in ('fusion_info','pokemon1_info','pokemon2_info'):
            if name in globals():
                targets.append((name, globals()[name]))
        for (nm, w) in targets:
            try:
                fonts = _get_or_build_fonts(w)
                logging.log(lvl, f"[FontTags] {nm} fonts start")
                _debug_dump_fonts('audit', w, fonts)
            except Exception as e:
                logging.log(lvl, f"[FontTags] {nm} error: {e}")
    finally:
        try:
            if 'widget_font_tag_logs_var' in globals():
                widget_font_tag_logs_var.set(False)
        except Exception:
            pass

def _apply_verbose_level():
    lvl = logging.DEBUG if ('verbose_logs_var' in globals() and verbose_logs_var.get()) else logging.INFO
    try:
        logging.getLogger().setLevel(lvl)
    except Exception:
        pass

def on_toggle_master_logs():
    try:
        master_on = logs_master_var.get() if 'logs_master_var' in globals() else False
        def set_state(label: str, state):
            try:
                view_menu.entryconfig(label, state=state)
            except Exception:
                pass
        if not master_on:
            for v in ('verbose_logs_var','calc_logs_var','ui_layout_logs_var','widget_font_tag_logs_var'):
                try:
                    globals()[v].set(False)
                except Exception:
                    pass
            for lbl in ('Verbose Logs','Show Calculation Logs','Show UI Layout Logs','Show Widget Font/Tag Logs'):
                set_state(lbl, tk.DISABLED)
            if 'status_text' in globals():
                status_text.set('Logging (Master) OFF — all logging toggles disabled')
        else:
            for lbl in ('Verbose Logs','Show Calculation Logs','Show UI Layout Logs','Show Widget Font/Tag Logs'):
                set_state(lbl, tk.NORMAL)
            if 'status_text' in globals():
                status_text.set('Logging (Master) ON')
        _apply_verbose_level()
    except Exception:
        pass

# Verbose toggle handler (global level only)

def on_toggle_verbose_logs():
    try:
        global VERBOSE_BOLD_LOGS
        VERBOSE_BOLD_LOGS = bool('verbose_logs_var' in globals() and verbose_logs_var.get())
        try:
            logging.getLogger().setLevel(logging.DEBUG if VERBOSE_BOLD_LOGS else logging.INFO)
        except Exception:
            pass
        if 'status_text' in globals() and 'verbose_logs_var' in globals():
            try:
                status_text.set('Verbose Logs ON (DEBUG level)' if verbose_logs_var.get() else 'Verbose Logs OFF (INFO level)')
            except Exception:
                pass
    except Exception:
        pass

VERBOSE_BOLD_LOGS = False  # runtime-controlled via View → Verbose Logs
AUTO_RECALC_ON_SELECT = False
BUILD_TAG = "8f80b4b35fa2"
HAS_FUSION = False

_FUSION_CACHE = {}
__fusion_option_buttons__ = []  # runtime registry for Display Options fusion-column controls
def update_fusion_option_states():
    """Enable fusion panel toggles only after a fusion has occurred; disable after Clear. Idempotent.
    This is a lightweight UI guard (Rule 58 + request 2a/conditions reset)."""
    try:
        desired_enabled = bool(globals().get('HAS_FUSION', False))
        for btn in list(__fusion_option_buttons__):
            try:
                if desired_enabled:
                    btn.state(['!disabled'])
                else:
                    btn.state(['disabled'])
            except Exception:
                try:
                    import tkinter as tk
                    btn['state'] = tk.NORMAL if desired_enabled else tk.DISABLED
                except Exception:
                    pass
    except Exception:
        pass

# Fonts
HEADING_FONT_DEF = ("Arial", 11, "bold")   # headings
BODY_FONT_DEF    = ("Arial", 10)            # non-numeric body
VALUE_FONT_DEF   = ("Consolas", 11)         # all numeric values (monospace)
VALUE_FALLBACKS  = [("Courier New", 11), ("TkFixedFont", 11)]

# Logging (runtime adjustable)
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

# Startup defaults (script-only)
DEFAULTS = {
    'view': {
        'logs_master': True,
        'verbose_logs': False,
        'show_calc_logs': True,
        'show_status_bar': True,
        'quick_compare_target': 'p2',
        'passive_active': True,
        'flip_stat_challenge': False,
    },
    'display': {
        'p1': { 'type': True, 'abilities': True, 'hidden_ability': True, 'passive': True, 'bst': True, 'evolution': True, 'damage': True },
        'p2': { 'type': True, 'abilities': True, 'hidden_ability': True, 'passive': True, 'bst': True, 'evolution': True, 'damage': True },
        'fusion': { 'fused_type': True, 'bst': True, 'diffs': True, 'abilities': True, 'ability_effects': True, 'damage': True, 'quick_compare': True },
    },
}

def apply_defaults():
    try:
        if 'logs_master_var' in globals(): logs_master_var.set(bool(DEFAULTS['view']['logs_master']))
        if 'verbose_logs_var' in globals(): verbose_logs_var.set(bool(DEFAULTS['view']['verbose_logs']))
        if 'calc_logs_var' in globals(): calc_logs_var.set(bool(DEFAULTS['view']['show_calc_logs']))
        if 'show_status_bar_var' in globals(): show_status_bar_var.set(bool(DEFAULTS['view']['show_status_bar']))
        if 'quick_compare_target_var' in globals(): quick_compare_target_var.set(str(DEFAULTS['view']['quick_compare_target']))
        if 'passive_active_var' in globals(): passive_active_var.set(bool(DEFAULTS['view']['passive_active']))
        if 'flip_stat_var' in globals(): flip_stat_var.set(bool(DEFAULTS['view']['flip_stat_challenge']))
        try:
            display_vars
        except NameError:
            pass
        ensure_display_vars()
        for panel, mapping in DEFAULTS['display'].items():
            for key, val in mapping.items():
                try:
                    display_vars[panel][key].set(bool(val))
                except Exception:
                    pass
    except Exception as e:
        try: logging.debug(f"[Defaults] apply failed: {e}")
        except Exception: pass
# Internationalization (static strings)
STR = {
    'display_options_title': 'Display Options',
    'section': 'Section',
    'p1': 'Pokémon 1',
    'p2': 'Pokémon 2',
    'fusion': 'Fusion',
    'type': 'Type',
    'abilities': 'Abilities',
    'hidden_ability': 'Hidden Ability',
    'passive': 'Passive',
    'bst_stats': 'BST & Stats',
    'evolution': 'Evolution',
    'damage_taken': 'Damage Taken',
    'ability_effect_summary': 'Ability Effect Summary',
    'quick_compare': 'Quick Compare',
    'compare_vs': 'Compare vs:',
    'close': 'Close',
    'select_all': 'Select All',
    'select_none': 'Select None',
    'restore_defaults': 'Restore Defaults',
    'copy_fusion_summary': 'Copy Fusion Summary',
    'export_fusion_summary': 'Export Fusion Summary…',
    'nothing_to_copy': 'Nothing to copy yet. Fuse two Pokémon first.',
    'nothing_to_export': 'Nothing to export yet. Fuse two Pokémon first.',
    'pokedex_id': 'Pokedex ID: {}',
    'fused_type_label': 'Fused Type: ',
    'bst_label': 'BST:',
    'total_bst': 'Total BST',
    'difference_from': 'Difference from {}: ',
    'active_ability': 'Active Ability: ',
    'hidden_ability_label': 'Hidden Ability: ',
    'passive_from_p1': 'Passive (from Pokémon 1): ',
    'active_effect': 'Active effect',
    'passive_effect': 'Passive effect',
    'new_imm': ' New immunities: ',
    'lost_imm': ' Lost immunities: ',
    'new_wk':  ' Gained weaknesses (≥2×): ',
    'lost_wk': ' Lost weaknesses (≥2×): ',
    'new_res': ' Gained resistances (≤½×): ',
    'lost_res':' Lost resistances (≤½×): ',
    'no_changes': ' No changes in immunities/weaknesses/resistances vs baseline.',
    'ready': 'Ready.',
    'pokemon_not_found': 'Pokémon not found.',
}
# Data loading
pokemon_stats: Dict[str, Dict[str, Any]] = {}

def load_pokemon_data_into(pstore: Dict[str, Dict[str, Any]]) -> int:
    logging.info("Loading Pokemon data from CSV file")
    pstore.clear()
    count = 0
    issues = []
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
                if not display_name:
                    issues.append('Row with missing name.')
                if stats['ID'] <= 0:
                    issues.append(f"{display_name}: suspicious ID {stats['ID']}")
                if not stats['Abilities']:
                    issues.append(f"{display_name}: no abilities listed")
                if any(',' in a for a in stats['Abilities']):
                    issues.append(f"{display_name}: malformed ability list")
                if display_name in pstore:
                    issues.append(f"Duplicate name detected: {display_name}")
                pstore[display_name] = stats
                count += 1
        logging.info(f"Successfully loaded {count} Pokemon (keys={len(pstore)})")
        if issues:
            logging.info(f"[CSV Lint] Found {len(issues)} potential issues (non-blocking). Showing first 5…")
            for msg in issues[:5]:
                logging.info(f"[CSV Lint] {msg}")
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

# Quick launchers
open_pokemondb = lambda: webbrowser.open("https://pokemondb.net/")
open_type_calculator = lambda: webbrowser.open("https://www.pkmn.help/defense/")
open_pokedex = lambda: webbrowser.open("https://wiki.pokerogue.net/dex:pokedex")
# Export utilities
def get_fusion_summary_text() -> str:
    try:
        return (fusion_info.get('1.0', tk.END) or '').strip()
    except Exception:
        return ''

def copy_fusion_summary():
    try:
        txt = get_fusion_summary_text()
        if not txt.strip():
            try: messagebox.showinfo(STR['copy_fusion_summary'], STR['nothing_to_copy'])
            except Exception: pass
            return
        root.clipboard_clear(); root.clipboard_append(txt)
        try: status_text.set('Fusion summary copied to clipboard.')
        except Exception: pass
    except Exception as e:
        logging.error('[Export] copy failed: %s' % e, exc_info=True)

def export_fusion_summary():
    try:
        txt = get_fusion_summary_text()
        if not txt.strip():
            try: messagebox.showinfo(STR['export_fusion_summary'], STR['nothing_to_export'])
            except Exception: pass
            return
        path = filedialog.asksaveasfilename(title=STR['export_fusion_summary'], defaultextension='.md', filetypes=[('Markdown','*.md'), ('Text','*.txt'), ('All files','*.*')])
        if not path:
            return
        with open(path, 'w', encoding='utf-8') as f:
            f.write(txt + '\n')
        try: status_text.set('Fusion summary exported: ' + str(path))
        except Exception: pass
    except Exception as e:
        logging.error('[Export] save failed: %s' % e, exc_info=True)
# Utility helpers
def avg_round_tenth(a: float, b: float) -> float: return round((float(a) + float(b)) / 2.0, 1)

def format_number_trim(x) -> str:
    try: fx = float(x)
    except Exception: return str(x)
    return f"{fx:.1f}".rstrip('0').rstrip('.')
# Text widget font/tag helpers
_FONT_CACHE = {}

def _create_font_safely(family, size, weight='normal', slant='roman'):
    try:
        return tkfont.Font(family=family, size=size, weight=weight, slant=slant)
    except Exception:
        return None

def _get_or_build_fonts(text: tk.Text):
    wid = str(text)
    cache = _FONT_CACHE.get(wid, {})
    if cache:
        return cache
    heading = _create_font_safely(*HEADING_FONT_DEF)
    body = _create_font_safely(*BODY_FONT_DEF)
    value = _create_font_safely(*VALUE_FONT_DEF)
    if value is None:
        for fam, size in VALUE_FALLBACKS:
            value = _create_font_safely(fam, size)
            if value: break
    if heading is None:
        try:
            base = tkfont.Font(text, text.cget('font'))
        except Exception:
            base = tkfont.nametofont('TkDefaultFont')
        heading = tkfont.Font(font=base); heading.configure(weight='bold', size=11)
    if body is None:
        try:
            body = tkfont.Font(text, text.cget('font'))
        except Exception:
            body = tkfont.nametofont('TkDefaultFont')
    if value is None:
        value = tkfont.nametofont('TkFixedFont')
    fonts = {'heading': heading, 'body': body, 'value': value}
    _FONT_CACHE[wid] = fonts
    return fonts

def _debug_dump_fonts(prefix: str, text: tk.Text, fonts: dict):
    if not VERBOSE_BOLD_LOGS:
        return
    try:
        wf = text.cget('font')
        logging.debug(f"[BOLD][{prefix}] widget_font={wf}")
        for key in ('heading','body','value'):
            f = fonts.get(key)
            if f:
                logging.debug(f"[BOLD][{prefix}] {key}={{'family': '{f.actual('family')}', 'size': {f.actual('size')}, 'weight': '{f.actual('weight')}', 'slant': '{f.actual('slant')}', 'underline': {f.actual('underline')}, 'overstrike': {f.actual('overstrike')}}}")
        for tag in ('strong_label','stat_label','stat_value','hr'):
            try:
                val = text.tag_cget(tag, 'font')
                if val:
                    try:
                        fn = tkfont.Font(name=val, exists=True)
                        logging.debug(f"[BOLD][{prefix}] tag {tag} -> font name '{val}', actual={{'family': '{fn.actual('family')}', 'size': {fn.actual('size')}, 'weight': '{fn.actual('weight')}', 'slant': '{fn.actual('slant')}', 'underline': {fn.actual('underline')}, 'overstrike': {fn.actual('overstrike')}}}")
                    except Exception:
                        logging.debug(f"[BOLD][{prefix}] tag {tag} -> font '{val}' (not a named font?)")
                else:
                    logging.debug(f"[BOLD][{prefix}] tag {tag} has no explicit 'font' set")
            except Exception as e:
                logging.debug(f"[BOLD][{prefix}] tag_cget({tag},font) failed: {e}")
    except Exception as e:
        logging.debug(f"[BOLD][{prefix}] dump failed: {e}")

def _assert_and_raise_core_tags(text: tk.Text):
    fonts = _get_or_build_fonts(text)
    text.tag_config('strong_label', font=fonts['heading'])
    text.tag_config('stat_label',   font=fonts['heading'])
    text.tag_config('stat_value',   font=fonts['value'])
    text.tag_config('hr',           foreground='#888888')
    try:
        text.tag_raise('hr'); text.tag_raise('stat_value'); text.tag_raise('stat_label'); text.tag_raise('strong_label')
    except Exception:
        pass
    _debug_dump_fonts('assert', text, fonts)

from tkinter import font as tkfont  # safe repeat

def _apply_stat_tabs(text: tk.Text, items):
    labels = [str(lbl) + ':' for (lbl, _v) in items]
    try:
        fnt = _get_or_build_fonts(text)['body']
    except Exception:
        fnt = tkfont.nametofont('TkFixedFont')
    max_label_pixels = max((fnt.measure(lbl + ' ') for lbl in labels), default=120)
    text.tag_config('stat_tabs', tabs=(max_label_pixels + 2, 'right'))

# \ Ability rule mapping (UI) /
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

# \ Display options (stateless)/

def init_display_vars():
    vars = {
        'p1': {k: tk.BooleanVar(value=True) for k in ['type','abilities','hidden_ability','passive','bst','evolution','damage']},
        'p2': {k: tk.BooleanVar(value=True) for k in ['type','abilities','hidden_ability','passive','bst','evolution','damage']},
        'fusion': {k: tk.BooleanVar(value=True) for k in ['fused_type','bst','diffs','abilities','ability_effects','damage','quick_compare']},
    }
    return vars

# ensure_display_vars helper

def ensure_display_vars():
    global display_vars
    try:
        display_vars
    except NameError:
        display_vars = init_display_vars()

def is_section_enabled(panel: str, key: str) -> bool:
    try:
        return bool(display_vars[panel][key].get())
    except Exception:
        return True
# Panels & writers
def write_stat_block(text: tk.Text, items):
    _assert_and_raise_core_tags(text)
    _apply_stat_tabs(text, items)
    for label, value in items:
        val = format_number_trim(value)
        text.insert(tk.END, f"{label}:", 'stat_label'); text.insert(tk.END, "\t"); text.insert(tk.END, f"{val}\n", ('stat_value', 'stat_tabs'))
    _assert_and_raise_core_tags(text)

def insert_hr(text: tk.Text, width_chars: int = 24):
    _assert_and_raise_core_tags(text)
    text.insert(tk.END, '-' * width_chars + "\n", 'hr')
    _assert_and_raise_core_tags(text)

FLIP_MAP = {'HP':'Speed','Attack':'Sp. Def','Defense':'Sp. Atk','Sp. Atk':'Defense','Sp. Def':'Attack','Speed':'HP'}

def flip_stats_dict(stats_like: dict) -> dict:
    flipped = {}
    for k in ['HP','Attack','Defense','Sp. Atk','Sp. Def','Speed']:
        flipped[FLIP_MAP.get(k,k)] = stats_like.get(k,0)
    for k in ['HP','Attack','Defense','Sp. Atk','Sp. Def','Speed']:
        flipped.setdefault(k,0)
    return flipped

# Side panel renderer

def fill_side_panel(name: str, info_text: tk.Text, id_label: tk.Label, name_label: tk.Label):
    if not name or name not in pokemon_stats: return
    name_label.config(text=name)
    stats = pokemon_stats[name]
    t1, t2 = stats['Type_1'], stats['Type_2']
    ptype = t1 if (not t2 or t2 == t1) else f"{t1}/{t2}"

    info_text.delete('1.0', tk.END)
    try: info_text.configure(font=BODY_FONT_DEF)
    except Exception: pass
    _assert_and_raise_core_tags(info_text)

    panel_key = 'p1' if info_text is pokemon1_info else 'p2'

    if is_section_enabled(panel_key, 'type'):
        info_text.insert(tk.END, STR['type'] + ': ', 'strong_label'); info_text.insert(tk.END, f"{ptype}\n\n")

    abilities = list(dict.fromkeys(stats.get('Abilities', [])))
    hidden_ability = abilities[1] if len(abilities) > 1 else ''
    visible_abilities = [a for i, a in enumerate(abilities) if i != 1] if abilities else []

    if is_section_enabled(panel_key, 'abilities') and visible_abilities:
        info_text.insert(tk.END, STR['abilities'] + ': ', 'strong_label'); info_text.insert(tk.END, f"{', '.join(visible_abilities)}\n")
    if is_section_enabled(panel_key, 'hidden_ability') and hidden_ability:
        info_text.insert(tk.END, STR['hidden_ability_label'], 'strong_label'); info_text.insert(tk.END, f"{hidden_ability}\n")
    if is_section_enabled(panel_key, 'passive') and stats.get('Passive'):
        info_text.insert(tk.END, STR['passive'] + ': ', 'strong_label'); info_text.insert(tk.END, f"{stats['Passive']}\n")

    if ((is_section_enabled(panel_key, 'abilities') and visible_abilities) or
        (is_section_enabled(panel_key, 'hidden_ability') and hidden_ability) or
        (is_section_enabled(panel_key, 'passive') and stats.get('Passive'))):
        info_text.insert(tk.END, "\n")

    if is_section_enabled(panel_key, 'bst'):
        info_text.insert(tk.END, STR['bst_label'], 'strong_label'); info_text.insert(tk.END, "\n")
        insert_hr(info_text)
        orig = {'HP': stats['HP'], 'Attack': stats['Attack'], 'Defense': stats['Defense'], 'Sp. Atk': stats['Sp. Atk'], 'Sp. Def': stats['Sp. Def'], 'Speed': stats['Speed']}
        items_dict = flip_stats_dict(orig) if flip_stat_var.get() else orig
        items = [('HP', items_dict['HP']), ('Attack', items_dict['Attack']), ('Defense', items_dict['Defense']), ('Sp. Atk', items_dict['Sp. Atk']), ('Sp. Def', items_dict['Sp. Def']), ('Speed', items_dict['Speed'])]
        write_stat_block(info_text, items)
        info_text.insert(tk.END, "\n")
        info_text.insert(tk.END, f"{STR['total_bst']}:\t", 'stat_label'); info_text.insert(tk.END, f"{format_number_trim(stats['BST'])}\n", 'stat_value')

        info_text.insert(tk.END, '\n')
    if is_section_enabled(panel_key, 'evolution') and (stats.get('evolution line') or '').strip():
        evo_line = (stats.get('evolution line') or '').strip()
        info_text.insert(tk.END, STR['evolution'] + ': ', 'strong_label')
        parts = [p.strip() for p in evo_line.split(',') if p.strip()]
        for _idx, _pname in enumerate(parts):
            tag = f"evo_{id(info_text)}_{_idx}"
            info_text.tag_config(tag, foreground='#1a73e8', underline=True)
            info_text.tag_bind(tag, '<Button-1>', lambda e, n=_pname, w=info_text: on_click_evo(n, w))
            info_text.tag_bind(tag, '<Enter>', lambda e, w=info_text: w.config(cursor='hand2'))
            info_text.tag_bind(tag, '<Leave>', lambda e, w=info_text: w.config(cursor=''))
            info_text.insert(tk.END, _pname, tag)
            if _idx != len(parts) - 1: info_text.insert(tk.END, ', ')
        info_text.insert(tk.END, '\n\n')

    if is_section_enabled(panel_key, 'damage'):
        eff = calculate_type_effectiveness(t1, t2, active_ability=None, passive_ability=stats['Passive'])
        info_text.insert(tk.END, STR['damage_taken'] + ': ', 'strong_label'); info_text.insert(tk.END, "\n\n")
        _eff_str = format_type_effectiveness(eff); _eff_body = _eff_str.split('\n',1)[1] if '\n' in _eff_str else ''
        info_text.insert(tk.END, _eff_body)

    id_label.config(text=STR['pokedex_id'].format(stats['ID']))

    _assert_and_raise_core_tags(info_text)

# ===== Fusion helpers that were missing in 1.2a =====

def populate_active_abilities_for(pokemon2_name: str):
    """Populate the Active Ability combobox with Pokémon 2's available abilities"""
    try:
        if pokemon2_name in pokemon_stats:
            abilities_list = list(dict.fromkeys(pokemon_stats[pokemon2_name].get('Abilities', [])))
        else:
            abilities_list = []
        if not abilities_list:
            abilities_list = ['']
        active_ability_combo['values'] = abilities_list
        current = active_ability_var.get(); active_ability_var.set(current if current in abilities_list else abilities_list[0])
    except Exception:
        pass

def compute_fused_typing(p1_t1: str, p1_t2: str, p2_t1: str, p2_t2: str):
    """Derive fused typing using P1 primary + P2 contribution rules."""
    fused_type1 = p1_t1; fused_type2 = ''
    p2_is_dual = bool(p2_t2)
    if p2_is_dual:
        if p2_t2 == p1_t1:
            fused_type2 = p2_t1 if p2_t1 != p1_t1 else ''
        else:
            fused_type2 = p2_t2 if p2_t2 != p1_t1 else (p2_t1 if p2_t1 != p1_t1 else '')
    else:
        if p2_t1 == p1_t1:
            fused_type2 = p1_t2 if (p1_t2 and p1_t2 != p1_t1) else ''
        else:
            fused_type2 = p2_t1
    return fused_type1, fused_type2

# Fusion helpers and nav

def on_click_evo(pokemon_name: str, source_text_widget: tk.Text):
    try:
        name = (pokemon_name or '').strip()
        if name not in pokemon_stats:
            try: messagebox.showwarning('Not found', f"'{name}' was not found in the data.")
            except Exception: pass
            return
        if source_text_widget is pokemon1_info:
            pokemon1_var.set(name); fill_side_panel(name, pokemon1_info, pokemon1_id, pokemon1_name); maybe_recalc_if_ready()
        elif source_text_widget is pokemon2_info:
            pokemon2_var.set(name); fill_side_panel(name, pokemon2_info, pokemon2_id, pokemon2_name); populate_active_abilities_for(name); maybe_recalc_if_ready()
        else:
            pokemon1_var.set(name); fill_side_panel(name, pokemon1_info, pokemon1_id, pokemon1_name); maybe_recalc_if_ready()
    except Exception as e:
        logging.error(f'Error handling evolution click: {e}', exc_info=True)

# Define swap_pokemon BEFORE UI uses it

def swap_pokemon():
    try:
        p1 = pokemon1_var.get().strip(); p2 = pokemon2_var.get().strip()
        pokemon1_var.set(p2); pokemon2_var.set(p1)
        if p2 in pokemon_stats: fill_side_panel(p2, pokemon1_info, pokemon1_id, pokemon1_name)
        else:
            pokemon1_info.delete('1.0', tk.END); pokemon1_name.config(text=''); pokemon1_id.config(text='')
        if p1 in pokemon_stats: fill_side_panel(p1, pokemon2_info, pokemon2_id, pokemon2_name)
        else:
            pokemon2_info.delete('1.0', tk.END); pokemon2_name.config(text=''); pokemon2_id.config(text='')
        populate_active_abilities_for(p1); maybe_recalc_if_ready()
    except Exception as e:
        logging.error(f'Error in swap_pokemon: {e}', exc_info=True)

# Fusion calculation/render

def calculate_fusion_stats(p1, p2):
    t0 = time.perf_counter()
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
            p1_t1 = pokemon_stats[p1]['Type_1']; p1_t2 = pokemon_stats[p1]['Type_2']
            p2_t1 = pokemon_stats[p2]['Type_1']; p2_t2 = pokemon_stats[p2]['Type_2']
            fused_type1, fused_type2 = compute_fused_typing(p1_t1, p1_t2, p2_t1, p2_t2)
            fused_type = fused_type1 if fused_type2 == '' or fused_type2 == fused_type1 else f"{fused_type1}/{fused_type2}"

            fusion_info.delete('1.0', tk.END)
            try: fusion_info.configure(font=BODY_FONT_DEF)
            except Exception: pass
            _assert_and_raise_core_tags(fusion_info)

            if is_section_enabled('fusion', 'fused_type'):
                fusion_info.insert(tk.END, STR['fused_type_label'], 'strong_label'); fusion_info.insert(tk.END, f"{fused_type}\n\n")

            abilities = list(dict.fromkeys(pokemon_stats[p2]['Abilities']))
            visible_abilities = [a for i,a in enumerate(abilities) if i!=1] if abilities else []

            active_ability = (active_ability_var.get() or (abilities[0] if abilities else '')).strip()
            hidden_ability = abilities[1] if len(abilities) > 1 else ''
            passive_ability = pokemon_stats[p1]['Passive']
            passive_on = passive_active_var.get()

            if is_section_enabled('fusion', 'abilities'):
                fusion_info.insert(tk.END, STR['abilities'] + ': ', 'strong_label'); fusion_info.insert(tk.END, f"{', '.join(visible_abilities)}\n")
                if is_section_enabled('fusion','abilities') and active_ability:
                    fusion_info.insert(tk.END, STR['active_ability'], 'strong_label'); fusion_info.insert(tk.END, f"{active_ability}\n")
                if is_section_enabled('fusion','abilities') and hidden_ability and active_ability == hidden_ability:
                    fusion_info.insert(tk.END, STR['hidden_ability_label'], 'strong_label'); fusion_info.insert(tk.END, f"{hidden_ability}\n")
                if is_section_enabled('fusion','abilities') and passive_ability and passive_on:
                    fusion_info.insert(tk.END, STR['passive_from_p1'], 'strong_label'); fusion_info.insert(tk.END, f"{passive_ability} (active)\n")

            if is_section_enabled('fusion', 'bst'):
                fusion_info.insert(tk.END, "\n"); fusion_info.insert(tk.END, STR['bst_label'], 'strong_label'); fusion_info.insert(tk.END, "\n")
                insert_hr(fusion_info)
                items_dict = flip_stats_dict(fusion_stats) if flip_stat_var.get() else fusion_stats
                items = [('HP', items_dict['HP']), ('Attack', items_dict['Attack']), ('Defense', items_dict['Defense']), ('Sp. Atk', items_dict['Sp. Atk']), ('Sp. Def', items_dict['Sp. Def']), ('Speed', items_dict['Speed'])]
                write_stat_block(fusion_info, items)
                fusion_info.insert(tk.END, "\n")
                fusion_info.insert(tk.END, f"{STR['total_bst']}:\t", 'stat_label'); fusion_info.insert(tk.END, f"{format_number_trim(fused_bst)}\n", 'stat_value')

            if is_section_enabled('fusion', 'diffs'):
                diff1 = fused_bst - float(pokemon_stats[p1]['BST']); diff2 = fused_bst - float(pokemon_stats[p2]['BST'])
                fusion_info.insert(tk.END, STR['difference_from'].format(p1)); fusion_info.insert(tk.END, f"{format_number_trim(diff1)}\n", 'stat_value')
                fusion_info.insert(tk.END, STR['difference_from'].format(p2)); fusion_info.insert(tk.END, f"{format_number_trim(diff2)}\n\n", 'stat_value')

            def _ability_effect_summary_line(label: str, ability_name: str):
                abil = (ability_name or '').strip().upper(); eff = ABILITY_EFFECTS.get(abil, {}); parts = []
                if eff.get('immunities'): parts.append(f"immunities: {', '.join(eff['immunities'])}")
                if eff.get('halve'): parts.append(f"halves: {', '.join(eff['halve'])}")
                if abil == 'WONDER GUARD': parts.append('wonder guard: immune to all non-super-effective')
                if not parts: parts.append('no type-chart effects')
                return f"{label}: " + '; '.join(parts)

            if is_section_enabled('fusion', 'ability_effects'):
                ae = _ability_effect_summary_line(STR['active_effect'], active_ability)
                if active_ability and 'no type-chart effects' not in ae: fusion_info.insert(tk.END, ae + '\n')
                pe = _ability_effect_summary_line(STR['passive_effect'], (passive_ability if passive_on else ''))
                if passive_ability and passive_on and 'no type-chart effects' not in pe: fusion_info.insert(tk.END, pe + '\n')
                fusion_info.insert(tk.END, '\n')

            if is_section_enabled('fusion', 'quick_compare'):
                try:
                    target_key = quick_compare_target_var.get() if 'quick_compare_target_var' in globals() else 'p2'
                    if target_key == 'p1': bt1, bt2, target_name = pokemon_stats[p1]['Type_1'], pokemon_stats[p1]['Type_2'], p1
                    else: bt1, bt2, target_name = pokemon_stats[p2]['Type_1'], pokemon_stats[p2]['Type_2'], p2
                    eff_fused_raw = calculate_type_effectiveness(fused_type1, fused_type2, active_ability=active_ability, passive_ability=(passive_ability if passive_on else None))
                    eff_base_raw  = calculate_type_effectiveness(bt1, bt2, active_ability=None, passive_ability=None)
                    def group_effects(eff):
                        groups = {0.0:set(), 0.25:set(), 0.5:set(), 1.0:set(), 2.0:set(), 4.0:set()}
                        for t,v in eff.items():
                            if v <= 0.0: groups[0.0].add(t)
                            elif v <= 0.25: groups[0.25].add(t)
                            elif v <= 0.5: groups[0.5].add(t)
                            elif v >= 4.0: groups[4.0].add(t)
                            elif v >= 2.0: groups[2.0].add(t)
                            else: groups[1.0].add(t)
                        return groups
                    gf = group_effects(eff_fused_raw); gb = group_effects(eff_base_raw)
                    new_imm = sorted(gf[0.0] - gb[0.0]); lost_imm = sorted(gb[0.0] - gf[0.0])
                    new_wk  = sorted((gf[2.0] | gf[4.0]) - (gb[2.0] | gb[4.0]))
                    lost_wk = sorted((gb[2.0] | gb[4.0]) - (gf[2.0] | gf[4.0]))
                    new_res = sorted((gf[0.25] | gf[0.5]) - (gb[0.25] | gb[0.5]))
                    lost_res= sorted((gb[0.25] | gb[0.5]) - (gf[0.25] | gf[0.5]))
                    fusion_info.insert(tk.END, f"Quick Compare vs {target_name}: ", 'strong_label'); fusion_info.insert(tk.END, "\n")
                    if new_imm: fusion_info.insert(tk.END, STR['new_imm'] + f"{', '.join(new_imm)}\n")
                    if lost_imm: fusion_info.insert(tk.END, STR['lost_imm'] + f"{', '.join(lost_imm)}\n")
                    if new_wk:  fusion_info.insert(tk.END, STR['new_wk']  + f"{', '.join(new_wk)}\n")
                    if lost_wk: fusion_info.insert(tk.END, STR['lost_wk'] + f"{', '.join(lost_wk)}\n")
                    if new_res: fusion_info.insert(tk.END, STR['new_res'] + f"{', '.join(new_res)}\n")
                    if lost_res:fusion_info.insert(tk.END, STR['lost_res']+ f"{', '.join(lost_res)}\n")
                    if not (new_imm or lost_imm or new_wk or lost_wk or new_res or lost_res): fusion_info.insert(tk.END, STR['no_changes'] + "\n")
                    fusion_info.insert(tk.END, "\n")
                except Exception as _e:
                    logging.debug(f"[QuickCompare] error: {_e}")

            if is_section_enabled('fusion', 'damage'):
                eff = calculate_type_effectiveness(fused_type1, fused_type2, active_ability=active_ability, passive_ability=(passive_ability if passive_on else None))
                fusion_info.insert(tk.END, STR['damage_taken'] + ': ', 'strong_label'); fusion_info.insert(tk.END, "\n\n")
                _eff_str = format_type_effectiveness(eff); _eff_body = _eff_str.split('\n',1)[1] if '\n' in _eff_str else ''
                fusion_info.insert(tk.END, _eff_body)

            _assert_and_raise_core_tags(fusion_info)

            dt_ms = (time.perf_counter() - t0) * 1000.0
            global _FUSION_CACHE
            _FUSION_CACHE = {'p1': p1, 'p2': p2, 'fused_type1': fused_type1, 'fused_type2': fused_type2, 'fusion_stats': fusion_stats, 'fused_bst': fused_bst, 'active_ability': active_ability, 'passive_ability': passive_ability, 'passive_on': passive_on, 'flip_on': bool(flip_stat_var.get()), 'inverse_on': bool(inverse_battle_var.get())}

            global HAS_FUSION

            HAS_FUSION = True
            try:
                _v = bool('verbose_logs_var' in globals() and verbose_logs_var.get())
                if _v:
                    log_calc(f"[Cache] stored (p1={p1}, p2={p2}, type={fused_type}, active={active_ability or '-'}, passive={'ON' if passive_on else 'OFF'}, flip={'ON' if flip_stat_var.get() else 'OFF'}, inv={'ON' if inverse_battle_var.get() else 'OFF'})")
                else:
                    log_calc(f"[Cache] stored (p1={p1}, p2={p2}, type={fused_type})")
            except Exception:
                pass
            try:
                update_fusion_option_states()
            except Exception:
                pass
            status_text.set(f"Fused Type: {fused_type} Active: {active_ability or '—'} Passive: {'ON' if passive_on else 'OFF'} Flip: {'ON' if flip_stat_var.get() else 'OFF'} Inv: {'ON' if inverse_battle_var.get() else 'OFF'} Calc: {dt_ms:.1f} ms")

            try:
                try:
                    log_calc(f"[Calc] {p1}+{p2} -> {fused_type} bst={fused_bst} dt={dt_ms:.1f}ms")
                except Exception:
                    pass
            except Exception:
                pass
        else:
            fusion_info.delete('1.0', tk.END); _assert_and_raise_core_tags(fusion_info); fusion_info.insert(tk.END, STR['pokemon_not_found']); status_text.set(STR['ready'])
    except Exception as e:
        logging.error(f"Error in calculate_fusion_stats: {str(e)}", exc_info=True)
        messagebox.showerror('Error', f"An error occurred during fusion: {str(e)}")
# UI helpers & dialog
def refresh_side_panels():
    try:
        p1 = pokemon1_var.get().strip();
        if p1 in pokemon_stats: fill_side_panel(p1, pokemon1_info, pokemon1_id, pokemon1_name)
        p2 = pokemon2_var.get().strip();
        if p2 in pokemon_stats: fill_side_panel(p2, pokemon2_info, pokemon2_id, pokemon2_name)
    except Exception:
        pass

class Debouncer:
    def __init__(self, root: tk.Tk, delay_ms=150): self.root = root; self.delay = delay_ms; self.after_id: Optional[str] = None
    def call(self, func):
        if self.after_id:
            try: self.root.after_cancel(self.after_id)
            except Exception: pass
        self.after_id = self.root.after(self.delay, func)

class Tooltip:
    def __init__(self, widget, text, delay_ms=300):
        self.widget = widget; self.text = text; self.delay = delay_ms; self.tip: Optional[tk.Toplevel] = None; self.after_id: Optional[str] = None
        widget.bind('<Enter>', self._enter); widget.bind('<Leave>', self._leave)
    def _enter(self, _): self.after_id = self.widget.after(self.delay, self._show)
    def _leave(self, _):
        if self.after_id:
            try: self.widget.after_cancel(self.after_id)
            except Exception: pass
        self.after_id = None; self._hide()
    def _show(self):
        if self.tip or not self.widget.winfo_ismapped(): return
        x = self.widget.winfo_rootx() + 10; y = self.widget.winfo_rooty() + self.widget.winfo_height() + 8
        self.tip = tk.Toplevel(self.widget); self.tip.overrideredirect(True); self.tip.attributes('-topmost', True)
        lbl = ttk.Label(self.tip, text=self.text, background='#ffffe0', relief=tk.SOLID, borderwidth=1, justify='left'); lbl.pack(ipadx=6, ipady=4)
        self.tip.geometry(f'+{x}+{y}')
    def _hide(self):
        if self.tip:
            try: self.tip.destroy()
            except Exception: pass
        self.tip = None

# Search & selection filter (missing in 1.2a)

def filter_pokemon(event, filter_var, pokemon_entry, filtered_listbox):
    q = (pokemon_entry.get() or '').strip(); ql = q.lower()
    tokens = [t for t in re.split(r'\s+', ql) if t] if q else []
    def match_row(name, stats):
        if not tokens: return True
        for t in tokens:
            if ':' in t:
                key, val = t.split(':', 1); val = val.strip()
                if key == 'type':
                    if val not in (stats.get('Type_1','').lower(), stats.get('Type_2','').lower()): return False
                elif key == 'ability':
                    if not any(val in (a or '').lower() for a in stats.get('Abilities', [])): return False
                elif key == 'passive':
                    if val not in (stats.get('Passive','').lower()): return False
                elif key == 'name':
                    if val not in name.lower(): return False
                elif key in ('id', '#'):
                    if not str(stats.get('ID','')).startswith(val): return False
                else:
                    return False
            else:
                m = re.match(r'(hp|attack|defense|sp\. atk|sp\. def|speed|bst)\s*(<=|>=|==|=|<|>)\s*(\d+(?:\.\d+)?)', t)
                if m:
                    k, op, sval = m.groups(); keymap = {'hp':'HP','attack':'Attack','defense':'Defense','sp. atk':'Sp. Atk','sp. def':'Sp. Def','speed':'Speed','bst':'BST'}
                    skey = keymap.get(k); left = float(stats.get(skey, 0)); right = float(sval)
                    ok = ((op == '>' and left > right) or (op == '<' and left < right) or (op in ('=','==') and left == right) or (op == '>=') and left >= right or (op == '<=') and left <= right)
                    if not ok: return False
                else:
                    id_term = t.lstrip('#')
                    if id_term.isdigit():
                        if int(id_term) != stats.get('ID', -999999): return False
                    elif (t not in name.lower() and t not in stats.get('Type_1','').lower() and (t not in stats.get('Type_2','').lower() if stats.get('Type_2') else True) and not any(t in (a or '').lower() for a in stats.get('Abilities', [])) and t not in (stats.get('Passive','').lower())):
                        return False
        return True
    filtered_names = [name for name, stats in pokemon_stats.items() if match_row(name, stats)]
    filtered_listbox.delete(0, tk.END)
    for name in filtered_names: filtered_listbox.insert(tk.END, name)

# Display Options dialog


def render_fusion_from(p1, p2, fused_type1, fused_type2, fusion_stats, fused_bst,
                        active_ability, passive_ability, passive_on, debug=False):
    """Re-render Fusion pane from cached values (no stat/type recompute).
    Safe to call headless; computes only display-time effects (ability/type chart).
    """
    try:
        fused_type = fused_type1 if (not fused_type2 or fused_type2 == fused_type1) else f"{fused_type1}/{fused_type2}"
        try:
            _v = bool('verbose_logs_var' in globals() and verbose_logs_var.get())
            if _v:
                log_calc(f"[Cache] render_from_cache (p1={p1}, p2={p2}, type={fused_type}, active={active_ability or '-'}, passive={'ON' if passive_on else 'OFF'}, flip={'ON' if flip_stat_var.get() else 'OFF'}, inv={'ON' if inverse_battle_var.get() else 'OFF'})")
            else:
                log_calc(f"[Cache] render_from_cache (p1={p1}, p2={p2}, type={fused_type})")
        except Exception:
            pass
        fusion_info.delete('1.0', tk.END)
        try:
            fusion_info.configure(font=BODY_FONT_DEF)
        except Exception:
            pass
        _assert_and_raise_core_tags(fusion_info)
        if is_section_enabled('fusion', 'fused_type'):
            fusion_info.insert(tk.END, STR['fused_type_label'], 'strong_label'); fusion_info.insert(tk.END, f"{fused_type}\n\n")
        # Abilities / selections
        abilities = list(dict.fromkeys(pokemon_stats.get(p2, {}).get('Abilities', [])))
        visible_abilities = [a for i,a in enumerate(abilities) if i!=1] if abilities else []
        active_ability_eff = (active_ability or (abilities[0] if abilities else '')).strip()
        hidden_ability = abilities[1] if len(abilities) > 1 else ''
        if is_section_enabled('fusion', 'abilities'):
            fusion_info.insert(tk.END, STR['abilities'] + ': ', 'strong_label'); fusion_info.insert(tk.END, f"{', '.join(visible_abilities)}\n")
        if is_section_enabled('fusion','abilities') and active_ability_eff:
            fusion_info.insert(tk.END, STR['active_ability'], 'strong_label'); fusion_info.insert(tk.END, f"{active_ability_eff}\n")
        if is_section_enabled('fusion','abilities') and hidden_ability and active_ability_eff == hidden_ability:
            fusion_info.insert(tk.END, STR['hidden_ability_label'], 'strong_label'); fusion_info.insert(tk.END, f"{hidden_ability}\n")
        if is_section_enabled('fusion','abilities') and passive_ability and passive_on:
            fusion_info.insert(tk.END, STR['passive_from_p1'], 'strong_label'); fusion_info.insert(tk.END, f"{passive_ability} (active)\n")
        if is_section_enabled('fusion', 'bst'):
            fusion_info.insert(tk.END, "\n"); fusion_info.insert(tk.END, STR['bst_label'], 'strong_label'); fusion_info.insert(tk.END, "\n")
            insert_hr(fusion_info)
            items_dict = flip_stats_dict(fusion_stats) if flip_stat_var.get() else fusion_stats
            items = [('HP', items_dict['HP']), ('Attack', items_dict['Attack']), ('Defense', items_dict['Defense']), ('Sp. Atk', items_dict['Sp. Atk']), ('Sp. Def', items_dict['Sp. Def']), ('Speed', items_dict['Speed'])]
            write_stat_block(fusion_info, items)
            fusion_info.insert(tk.END, "\n")
            fusion_info.insert(tk.END, f"{STR['total_bst']}:\t", 'stat_label'); fusion_info.insert(tk.END, f"{format_number_trim(fused_bst)}\n", 'stat_value')
        if is_section_enabled('fusion', 'diffs'):
            try:
                diff1 = float(fused_bst) - float(pokemon_stats.get(p1, {}).get('BST', 0))
                diff2 = float(fused_bst) - float(pokemon_stats.get(p2, {}).get('BST', 0))
            except Exception:
                diff1 = fused_bst; diff2 = fused_bst
            fusion_info.insert(tk.END, STR['difference_from'].format(p1)); fusion_info.insert(tk.END, f"{format_number_trim(diff1)}\n", 'stat_value')
            fusion_info.insert(tk.END, STR['difference_from'].format(p2)); fusion_info.insert(tk.END, f"{format_number_trim(diff2)}\n\n", 'stat_value')
        # Ability effect summary
        def _ability_effect_summary_line(label: str, ability_name: str):
            abil = (ability_name or '').strip().upper(); eff = ABILITY_EFFECTS.get(abil, {}); parts = []
            if eff.get('immunities'): parts.append(f"immunities: {', '.join(eff['immunities'])}")
            if eff.get('halve'): parts.append(f"halves: {', '.join(eff['halve'])}")
            if abil == 'WONDER GUARD': parts.append('wonder guard: immune to all non-super-effective')
            if not parts: parts.append('no type-chart effects')
            return f"{label}: " + '; '.join(parts)
        if is_section_enabled('fusion', 'ability_effects'):
            ae = _ability_effect_summary_line(STR['active_effect'], active_ability_eff)
            if active_ability_eff and 'no type-chart effects' not in ae: fusion_info.insert(tk.END, ae + '\n')
            pe = _ability_effect_summary_line(STR['passive_effect'], (passive_ability if passive_on else ''))
            if passive_ability and passive_on and 'no type-chart effects' not in pe: fusion_info.insert(tk.END, pe + '\n')
            fusion_info.insert(tk.END, '\n')
        # Quick Compare
        if is_section_enabled('fusion', 'quick_compare'):
            try:
                target_key = quick_compare_target_var.get() if 'quick_compare_target_var' in globals() else 'p2'
                if target_key == 'p1':
                    bt1, bt2, target_name = pokemon_stats.get(p1, {}).get('Type_1',''), pokemon_stats.get(p1, {}).get('Type_2',''), p1
                else:
                    bt1, bt2, target_name = pokemon_stats.get(p2, {}).get('Type_1',''), pokemon_stats.get(p2, {}).get('Type_2',''), p2
                eff_fused_raw = calculate_type_effectiveness(fused_type1, fused_type2, active_ability=active_ability_eff, passive_ability=(passive_ability if passive_on else None))
                eff_base_raw = calculate_type_effectiveness(bt1, bt2, active_ability=None, passive_ability=None)
                def group_effects(eff):
                    groups = {0.0:set(), 0.25:set(), 0.5:set(), 1.0:set(), 2.0:set(), 4.0:set()}
                    for t,v in eff.items():
                        if v <= 0.0: groups[0.0].add(t)
                        elif v <= 0.25: groups[0.25].add(t)
                        elif v <= 0.5: groups[0.5].add(t)
                        elif v >= 4.0: groups[4.0].add(t)
                        elif v >= 2.0: groups[2.0].add(t)
                        else: groups[1.0].add(t)
                    return groups
                gf = group_effects(eff_fused_raw); gb = group_effects(eff_base_raw)
                new_imm = sorted(gf[0.0] - gb[0.0]); lost_imm = sorted(gb[0.0] - gf[0.0])
                new_wk = sorted((gf[2.0] | gf[4.0]) - (gb[2.0] | gb[4.0]))
                lost_wk = sorted((gb[2.0] | gb[4.0]) - (gf[2.0] | gf[4.0]))
                new_res = sorted((gf[0.25] | gf[0.5]) - (gb[0.25] | gb[0.5]))
                lost_res= sorted((gb[0.25] | gb[0.5]) - (gf[0.25] | gf[0.5]))
                fusion_info.insert(tk.END, f"Quick Compare vs {target_name}: ", 'strong_label'); fusion_info.insert(tk.END, "\n")
                if new_imm: fusion_info.insert(tk.END, STR['new_imm'] + f"{', '.join(new_imm)}\n")
                if lost_imm: fusion_info.insert(tk.END, STR['lost_imm'] + f"{', '.join(lost_imm)}\n")
                if new_wk: fusion_info.insert(tk.END, STR['new_wk'] + f"{', '.join(new_wk)}\n")
                if lost_wk: fusion_info.insert(tk.END, STR['lost_wk']+ f"{', '.join(lost_wk)}\n")
                if new_res: fusion_info.insert(tk.END, STR['new_res'] + f"{', '.join(new_res)}\n")
                if lost_res:fusion_info.insert(tk.END, STR['lost_res']+ f"{', '.join(lost_res)}\n")
                if not (new_imm or lost_imm or new_wk or lost_wk or new_res or lost_res): fusion_info.insert(tk.END, STR['no_changes'] + "\n")
                fusion_info.insert(tk.END, "\n")
            except Exception as _e:
                logging.debug(f"[QuickCompare] cache-render error: {_e}")
        # Damage taken
        if is_section_enabled('fusion', 'damage'):
            eff = calculate_type_effectiveness(fused_type1, fused_type2, active_ability=active_ability_eff, passive_ability=(passive_ability if passive_on else None))
            fusion_info.insert(tk.END, STR['damage_taken'] + ': ', 'strong_label'); fusion_info.insert(tk.END, "\n\n")
            _eff_str = format_type_effectiveness(eff); _eff_body = _eff_str.split('\n',1)[1] if '\n' in _eff_str else ''
            fusion_info.insert(tk.END, _eff_body)
        _assert_and_raise_core_tags(fusion_info)
        try:
            status_text.set(f"Fused Type: {fused_type} Active: {active_ability_eff or '—'} Passive: {'ON' if passive_on else 'OFF'} Flip: {'ON' if flip_stat_var.get() else 'OFF'} Inv: {'ON' if inverse_battle_var.get() else 'OFF'} CacheRefresh: OK")
        except Exception:
            pass
    except Exception as e:
        logging.debug(f"[CacheRender] failed: {e}")


def refresh_after_challenge_toggle():
    try:
        refresh_side_panels()
        if globals().get('HAS_FUSION', False) and isinstance(globals().get('_FUSION_CACHE', {}), dict):
            c = globals().get('_FUSION_CACHE', {})
            req = ['p1','p2','fused_type1','fused_type2','fusion_stats','fused_bst','active_ability','passive_ability','passive_on']
            if all(k in c for k in req):
                try:
                    _v = bool('verbose_logs_var' in globals() and verbose_logs_var.get())
                    if _v:
                        log_calc(f"[Cache] refresh_via_challenge_toggle (flip={'ON' if flip_stat_var.get() else 'OFF'}, inv={'ON' if inverse_battle_var.get() else 'OFF'})")
                    else:
                        log_calc('[Cache] refresh_via_challenge_toggle')
                except Exception:
                    pass
                try:
                    _v = bool('verbose_logs_var' in globals() and verbose_logs_var.get())
                    if _v:
                        log_calc(f"[Cache] refresh_via_display_options (flip={'ON' if flip_stat_var.get() else 'OFF'}, inv={'ON' if inverse_battle_var.get() else 'OFF'})")
                    else:
                        log_calc('[Cache] refresh_via_display_options')
                except Exception:
                    pass
                render_fusion_from(c['p1'], c['p2'], c['fused_type1'], c['fused_type2'], c['fusion_stats'], c['fused_bst'], c['active_ability'], c['passive_ability'], c['passive_on'])
    except Exception:
        pass

def show_display_options():
    ensure_display_vars()
    global quick_compare_target_var, __fusion_option_buttons__
    if quick_compare_target_var is None: quick_compare_target_var = tk.StringVar(value='p2')
    try: __fusion_option_buttons__.clear()
    except Exception: pass
    try:
        for w in root.winfo_children():
            if isinstance(w, tk.Toplevel) and str(w.title()) == STR['display_options_title']:
                try: w.lift(); w.focus_set()
                except Exception: pass
                return
    except Exception:
        pass
    dlg = tk.Toplevel(root); dlg.title(STR['display_options_title']); dlg.transient(root); dlg.grab_set()

    def cb_refresh():
        try:
            _assert_and_raise_core_tags(pokemon1_info); _assert_and_raise_core_tags(pokemon2_info); _assert_and_raise_core_tags(fusion_info)
        except Exception:
            pass
        try:
            # Always refresh side panels (they compute their own displays)
            refresh_side_panels()
            # Cache-backed Fusion refresh (no recalculation even if challenge toggles changed)
            if globals().get('HAS_FUSION', False) and isinstance(globals().get('_FUSION_CACHE', {}), dict):
                c = globals().get('_FUSION_CACHE', {})
                req = ['p1','p2','fused_type1','fused_type2','fusion_stats','fused_bst','active_ability','passive_ability','passive_on']
                if all(k in c for k in req):
                    render_fusion_from(c['p1'], c['p2'], c['fused_type1'], c['fused_type2'], c['fusion_stats'], c['fused_bst'], c['active_ability'], c['passive_ability'], c['passive_on'])
            _assert_and_raise_core_tags(pokemon1_info); _assert_and_raise_core_tags(pokemon2_info); _assert_and_raise_core_tags(fusion_info)
        except Exception as e:
            logging.debug(f"[DisplayOptions] refresh error: {e}")


    hdrs = [STR['section'], STR['p1'], STR['fusion'], STR['p2']]
    for i, h in enumerate(hdrs): ttk.Label(dlg, text=h, font=('Arial', 10, 'bold')).grid(row=0, column=i, padx=8, pady=6)

    rows = [
        (STR['type'], 'type', 'type', 'fused_type'),
        (STR['abilities'], 'abilities', 'abilities', 'abilities'),
        (STR['hidden_ability'], 'hidden_ability', 'hidden_ability', None),
        (STR['passive'], 'passive', 'passive', None),
        (STR['bst_stats'], 'bst', 'bst', 'bst'),
        ('Difference from…', None, None, 'diffs'),
        (STR['evolution'], 'evolution', 'evolution', None),
        (STR['damage_taken'], 'damage', 'damage', 'damage'),
        (STR['ability_effect_summary'], None, None, 'ability_effects'),
        (STR['quick_compare'], None, None, 'quick_compare'),
    ]

    def add_row(r, label, k1, k2, kf):
        ttk.Label(dlg, text=label).grid(row=r, column=0, sticky='w', padx=8, pady=2)
        if k1: ttk.Checkbutton(dlg, variable=display_vars['p1'][k1], command=cb_refresh).grid(row=r, column=1)
        else: ttk.Label(dlg, text='—').grid(row=r, column=1)
        if kf:
            _btn = ttk.Checkbutton(dlg, variable=display_vars['fusion'][kf], command=cb_refresh)
            _btn.grid(row=r, column=2)
            try:
                __fusion_option_buttons__.append(_btn)
            except Exception:
                pass
        else: ttk.Label(dlg, text='—').grid(row=r, column=2)
        if k2: ttk.Checkbutton(dlg, variable=display_vars['p2'][k2], command=cb_refresh).grid(row=r, column=3)
        else: ttk.Label(dlg, text='—').grid(row=r, column=3)

    r = 1
    for label, k1, k2, kf in rows:
        add_row(r, label, k1, k2, kf); r += 1

    cmpf = ttk.Frame(dlg); cmpf.grid(row=r, column=0, columnspan=4, sticky='w', padx=8, pady=(6,2))
    ttk.Label(cmpf, text=STR['compare_vs']).pack(side=tk.LEFT, padx=(0,8))
    ttk.Radiobutton(cmpf, text=STR['p1'], value='p1', variable=quick_compare_target_var, command=cb_refresh).pack(side=tk.LEFT, padx=4)
    ttk.Radiobutton(cmpf, text=STR['p2'], value='p2', variable=quick_compare_target_var, command=cb_refresh).pack(side=tk.LEFT, padx=4)

    btns = ttk.Frame(dlg); btns.grid(row=r+1, column=0, columnspan=4, pady=10)

    def do_select_all():
        for panel in ('p1','p2','fusion'):
            for _, var in display_vars[panel].items(): var.set(True)
        cb_refresh()

    def do_select_none():
        for panel in ('p1','p2','fusion'):
            for _, var in display_vars[panel].items(): var.set(False)
        cb_refresh()

    def do_restore_defaults():
        for panel in ('p1','p2','fusion'):
            for _, var in display_vars[panel].items(): var.set(True)
        cb_refresh()

    ttk.Button(btns, text=STR['select_all'], command=do_select_all).pack(side=tk.LEFT, padx=5)
    ttk.Button(btns, text=STR['select_none'], command=do_select_none).pack(side=tk.LEFT, padx=5)
    ttk.Button(btns, text=STR['restore_defaults'], command=do_restore_defaults).pack(side=tk.LEFT, padx=5)
    ttk.Button(btns, text=STR['close'], command=lambda: (dlg.withdraw(), dlg.after(0, dlg.destroy))).pack(side=tk.RIGHT, padx=5)
    try:
        update_fusion_option_states()
    except Exception:
        pass
    try:
        cb_refresh()
    except Exception:
        pass
# Type effectiveness
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

def _normalize_ability(name: str) -> str:
    return (name or '').strip().upper()

def calculate_type_effectiveness(type1, type2=None, active_ability=None, passive_ability=None):
    # Compute base chart first (no abilities)
    base = {t: 1.0 for t in type_effectiveness.keys()}
    types = [type1.title()] if type1 else []
    if type2 and type2.title() != (type1.title() if type1 else ''):
        types.append(type2.title())
    for t in types:
        if t not in type_effectiveness:
            logging.error(f"Unknown type: {t}")
            continue
        for weakness in type_effectiveness[t]['weaknesses']:
            base[weakness] *= 2
        for resistance in type_effectiveness[t]['resistances']:
            base[resistance] *= 0.5
        for immunity in type_effectiveness[t]['immunities']:
            base[immunity] = 0
    # Apply Inverse Battle inversion to the base chart if toggled
    eff = dict(base)
    try:
        inv_on = bool(inverse_battle_var.get())
    except Exception:
        inv_on = False
    if inv_on:
        for k, v in list(eff.items()):
            if v <= 0.0:
                eff[k] = 2.0
            elif v <= 0.25 + 1e-9:
                eff[k] = 4.0
            elif v <= 0.5 + 1e-9:
                eff[k] = 2.0
            elif v >= 4.0 - 1e-9:
                eff[k] = 0.25
            elif v >= 2.0 - 1e-9:
                eff[k] = 0.5
            else:
                eff[k] = 1.0
    # Abilities apply after inversion (ability immunities/resistances are unaffected by Inverse rules)
    act = _normalize_ability(active_ability); pas = _normalize_ability(passive_ability)
    def apply_effects(which):
        e = ABILITY_EFFECTS.get(which)
        if not e:
            return
        for immu in e.get('immunities', []):
            if immu in eff:
                eff[immu] = 0
        for half in e.get('halve', []):
            if half in eff:
                eff[half] *= 0.5
        for mult_t, mult_v in e.get('multiply', {}).items():
            if mult_t in eff:
                eff[mult_t] *= float(mult_v)
    if act:
        apply_effects(act)
    if pas:
        apply_effects(pas)
    # Wonder Guard special-case (post all adjustments): immune to all non-super-effective
    if act == 'WONDER GUARD' or pas == 'WONDER GUARD':
        for k, v in list(eff.items()):
            if v < 2:
                eff[k] = 0
    return eff

def format_type_effectiveness(effectiveness):
    result = STR['damage_taken'] + "\n"
    grouped: Dict[float, list] = {}
    for t, value in effectiveness.items():
        grouped.setdefault(float(value), []).append(t)
    order = [0.0, 0.25, 0.5, 1.0, 2.0, 4.0]
    labels = {0.0:'Immune', 0.25:'1/4x damage', 0.5:'1/2x damage', 1.0:'1x damage', 2.0:'2x damage', 4.0:'4x damage'}
    for val in order:
        types = grouped.get(val, [])
        if types:
            if val == 0.0:
                result += f"Immune: {', '.join(types)}\n"
            else:
                result += f"{labels[val]}: {', '.join(types)}\n"
    others = sorted([k for k in grouped.keys() if k not in order], reverse=True)
    for k in others:
        types = grouped[k]
        s = (f"{k:.2f}" if abs(k - round(k)) > 1e-9 else f"{int(round(k))}").rstrip('0').rstrip('.')
        result += f"{s}x damage: {', '.join(types)}\n"
    return result.strip()
# App setup & menus
load_pokemon_data_into(pokemon_stats)
root = tk.Tk(); root.title(f"PokéRogue Fusion Calculator — build {BUILD_TAG}")
root.geometry('1550x540')

menubar = tk.Menu(root); root.config(menu=menubar)
file_menu = tk.Menu(menubar, tearoff=0); menubar.add_cascade(label='File', menu=file_menu)
file_menu.add_command(label=STR['copy_fusion_summary'], command=copy_fusion_summary)
file_menu.add_command(label=STR['export_fusion_summary'], command=export_fusion_summary)
file_menu.add_separator(); file_menu.add_command(label='Exit', command=root.quit)

challenges_menu = tk.Menu(menubar, tearoff=0); menubar.add_cascade(label='Challenges', menu=challenges_menu)
resources_menu = tk.Menu(menubar, tearoff=0); menubar.add_cascade(label='Resources', menu=resources_menu)
resources_menu.add_command(label='Pokémon Database', command=open_pokemondb)
resources_menu.add_command(label='Type Calculator', command=open_type_calculator)
resources_menu.add_command(label='PokeRogue Pokedex', command=open_pokedex)
help_menu = tk.Menu(menubar, tearoff=0); menubar.add_cascade(label='Help', menu=help_menu)

# Toolbar Integrity Guard — ensure required challenge labels exist (idempotent)
def _verify_challenges_menu_integrity():
    try:
        required = ['Flip Stat Challenge', 'Inverse Battle Challenge']
        present = []
        try:
            count = challenges_menu.index('end') or -1
        except Exception:
            count = -1
        if count >= 0:
            for i in range(count + 1):
                try:
                    lbl = challenges_menu.entrycget(i, 'label')
                    if lbl:
                        present.append(lbl)
                except Exception:
                    pass
        if 'Flip Stat Challenge' not in present:
            challenges_menu.add_checkbutton(label='Flip Stat Challenge', variable=flip_stat_var, onvalue=True, offvalue=False, command=refresh_after_challenge_toggle)
        if 'Inverse Battle Challenge' not in present:
            challenges_menu.add_checkbutton(label='Inverse Battle Challenge', variable=inverse_battle_var, onvalue=True, offvalue=False, command=refresh_after_challenge_toggle)
    except Exception as e:
        logging.debug(f'[ToolbarGuard] Challenges menu audit failed: {e}')


# View menu
view_menu = tk.Menu(menubar, tearoff=0); menubar.add_cascade(label='View', menu=view_menu)
logs_master_var = tk.BooleanVar(value=True)
ui_layout_logs_var = tk.BooleanVar(value=False)
widget_font_tag_logs_var = tk.BooleanVar(value=False)
calc_logs_var = tk.BooleanVar(value=True)   # gated by verbose_logs_var
verbose_logs_var = tk.BooleanVar(value=False)
view_menu.add_checkbutton(label='Logging (Master)', variable=logs_master_var, onvalue=True, offvalue=False, command=on_toggle_master_logs)
view_menu.add_checkbutton(label='Verbose Logs', variable=verbose_logs_var, onvalue=True, offvalue=False, command=lambda: on_toggle_verbose_logs())
# Calculation logs: when ON, logs via log_calc(); level depends on Verbose
view_menu.add_checkbutton(label='Show Calculation Logs', variable=calc_logs_var, onvalue=True, offvalue=False)
# One-shot diagnostic dumps (fire on ON; auto-reset OFF)
view_menu.add_checkbutton(label='Show UI Layout Logs', variable=ui_layout_logs_var, onvalue=True, offvalue=False, command=dump_ui_layout_metrics)
view_menu.add_checkbutton(label='Show Widget Font/Tag Logs', variable=widget_font_tag_logs_var, onvalue=True, offvalue=False, command=dump_widget_font_tag_logs)
view_menu.add_separator()

# Runtime vars
show_status_bar_var = tk.BooleanVar(value=True)
quick_compare_target_var = tk.StringVar(value='p2')
passive_active_var = tk.BooleanVar(value=True)
flip_stat_var = tk.BooleanVar(value=False)

inverse_battle_var = tk.BooleanVar(value=False)
# Display vars
display_vars = init_display_vars()

# Help menu content

def show_help_overview():
    help_text = (
        "\nPokéRogue Fusion Calculator — Toolbar Overview\n"
        "\nFile\n  • " + STR['copy_fusion_summary'] + ": Copy the Fusion pane text.\n"
        "  • " + STR['export_fusion_summary'] + ": Save Fusion pane as .md/.txt.\n"
        "\nView\n  • Display Options: Toggle visibility of sections per panel (auto-applies).\n"
        "  • Quick Compare: Show/hide comparison summary vs P1/P2.\n"
        "  • Compare vs: Choose the baseline used in Quick Compare.\n"
        "  • Passive Active: Toggle whether Pokémon 1's Passive affects fusion typing.\n"
        "  • Logging (Master): Master switch; disables/enables all logging toggles.\n"
        "  • Verbose Logs: Raise log level to DEBUG (more detail).\n"
        "  • Show Calculation Logs: Emit calculation traces (respects Master/Verbose).\n"
        "  • Show UI Layout Logs: Dump a one-shot layout/geometry report.\n"
        "  • Show Widget Font/Tag Logs: Dump fonts/tags used by text widgets.\n"
        "  • Show Status Bar: Show/hide the bottom status strip.\n"
        "\nChallenges\n  • Flip Stat Challenge: Swap stat roles (HP↔Speed, Atk↔Sp.Def, Def↔Sp.Atk).\n"
        "  • Inverse Battle Challenge: Invert type chart (weaknesses/resistances swapped).\n"
        "\nResources\n  • Pokémon Database, Type Calculator, PokeRogue Pokedex (opens in browser).\n"
        "\nTips\n  • Use Search Filters (Help → Search Filters) to narrow lists quickly.\n"
    )

    try: messagebox.showinfo('Help — Toolbar Overview', help_text)
    except Exception: pass

help_menu.add_command(label='Toolbar Overview', command=show_help_overview)

def show_filter_help():
    try:
        message = """Search filters:
 name:TERM — match name substring
 type:TYPE — match type1 or type2 (e.g., type:fire)
 ability:NAME — match any listed ability
 passive:NAME — match passive ability
 id:NNN or #NNN — match Pokédex ID prefix or exact with #
 Numeric: hp/attack/defense/sp. atk/sp. def/speed/bst with >, <, >=, <=, =
 examples: hp>=100 speed<120 bst>500
"""
        messagebox.showinfo('Search Filter Help', message)
    except Exception:
        pass

help_menu.add_command(label='Search Filters', command=show_filter_help)

# Populate View menu
view_menu.add_command(label='Display Options', command=show_display_options, accelerator='Ctrl+Shift+D')
view_menu.add_separator()
view_menu.add_checkbutton(label='Quick Compare', variable=display_vars['fusion']['quick_compare'], onvalue=True, offvalue=False, command=lambda: force_recalc_if_ready())
cmp = tk.Menu(view_menu, tearoff=0)
cmp.add_radiobutton(label='Compare vs Pokémon 1', variable=quick_compare_target_var, value='p1', command=lambda: force_recalc_if_ready())
cmp.add_radiobutton(label='Compare vs Pokémon 2', variable=quick_compare_target_var, value='p2', command=lambda: force_recalc_if_ready())
view_menu.add_cascade(label='Compare vs', menu=cmp)
view_menu.add_separator()
view_menu.add_checkbutton(label='Passive Active', variable=passive_active_var, onvalue=True, offvalue=False, command=lambda: force_recalc_if_ready())
view_menu.add_separator()
# Status bar toggle wiring (normalized)
view_menu.add_checkbutton(label='Show Status Bar', variable=show_status_bar_var, onvalue=True, offvalue=False, command=lambda: (status_bar.pack(side=tk.BOTTOM, fill=tk.X) if show_status_bar_var.get() else status_bar.pack_forget()))
# Initialize Master gating once at startup
on_toggle_master_logs()

# Challenges — Flip Stat
challenges_menu.add_checkbutton(label='Flip Stat Challenge', variable=flip_stat_var, onvalue=True, offvalue=False, command=refresh_after_challenge_toggle)

# Challenges — Inverse Battle
challenges_menu.add_checkbutton(label='Inverse Battle Challenge', variable=inverse_battle_var, onvalue=True, offvalue=False, command=refresh_after_challenge_toggle)
# One-shot toolbar integrity verification (idempotent)
try:
    _verify_challenges_menu_integrity()
except Exception:
    pass


# Main layout
main_frame = ttk.Frame(root); main_frame.pack(fill=tk.BOTH, expand=True, padx=10)
for i in range(20): main_frame.grid_rowconfigure(i, weight=1)
for i in range(5):  main_frame.grid_columnconfigure(i, weight=1)

# Left search
pokemon1_label = ttk.Label(main_frame, text='Search Pokémon 1:', font=('Arial', 10))
pokemon1_label.grid(row=2, column=0, padx=6, sticky='e')
pokemon1_var = tk.StringVar(); pokemon1_filter_var = tk.StringVar()
pokemon1_entry = ttk.Entry(main_frame, textvariable=pokemon1_filter_var, width=20)
pokemon1_entry.grid(row=2, column=1, padx=6, sticky='w')

# Buttons
button_frame = ttk.Frame(main_frame); button_frame.grid(row=1, column=2)
fusion_button = ttk.Button(button_frame, text='Fuse', command=lambda: calculate_fusion_stats(pokemon1_var.get(), pokemon2_var.get()))
fusion_button.pack(side=tk.LEFT, padx=5)
swap_button = ttk.Button(button_frame, text='Swap', command=swap_pokemon)
swap_button.pack(side=tk.LEFT, padx=5)

def clear_selections():
    global HAS_FUSION
    HAS_FUSION = False
    try:
        update_fusion_option_states()
    except Exception:
        pass
    pokemon1_var.set(''); pokemon2_var.set(''); pokemon1_filter_var.set(''); pokemon2_filter_var.set('')
    pokemon1_filtered_listbox.selection_clear(0, tk.END); pokemon2_filtered_listbox.selection_clear(0, tk.END)
    pokemon1_name.config(text=''); pokemon2_name.config(text='')
    pokemon1_info.delete('1.0', tk.END); pokemon2_info.delete('1.0', tk.END); fusion_info.delete('1.0', tk.END)
    pokemon1_id.config(text=''); pokemon2_id.config(text='')
    pokemon1_filtered_listbox.delete(0, tk.END); pokemon2_filtered_listbox.delete(0, tk.END)
    for name in pokemon_stats:
        pokemon1_filtered_listbox.insert(tk.END, name); pokemon2_filtered_listbox.insert(tk.END, name)
    try: active_ability_combo['values'] = ['']; active_ability_var.set('')
    except Exception: pass
    try: status_text.set(STR['ready'])
    except Exception: pass

clear_button = ttk.Button(button_frame, text='Clear', command=clear_selections)
clear_button.pack(side=tk.LEFT, padx=5)

# Options row
options_frame = ttk.Frame(main_frame); options_frame.grid(row=2, column=2, sticky='n', pady=2)
options_frame.grid_columnconfigure(0, weight=1); options_frame.grid_columnconfigure(1, weight=1)
active_ability_var = tk.StringVar(value='')
active_ability_label = ttk.Label(options_frame, text='Active Ability:')
active_ability_label.grid(row=0, column=0, sticky='e', padx=5, pady=(0, 2))
active_ability_combo = ttk.Combobox(options_frame, textvariable=active_ability_var, width=22, state='readonly')
active_ability_combo.grid(row=0, column=1, sticky='w', padx=5, pady=(0, 2))
active_ability_combo.bind('<<ComboboxSelected>>', lambda e: (status_text.set('Active ability changed — press Fuse to recalc') if 'status_text' in globals() else None))

# Right search
pokemon2_label = ttk.Label(main_frame, text='Search Pokémon 2:', font=('Arial', 10))
pokemon2_label.grid(row=2, column=3, padx=6, sticky='e')
pokemon2_var = tk.StringVar(); pokemon2_filter_var = tk.StringVar()
pokemon2_entry = ttk.Entry(main_frame, textvariable=pokemon2_filter_var, width=20)
pokemon2_entry.grid(row=2, column=4, padx=6, sticky='w')

# Columns/panels
pokemon1_filtered_label = ttk.Label(main_frame, text='Pokémon 1:', font=('Arial', 10, 'bold'))
pokemon1_filtered_label.grid(row=3, column=0, sticky=tk.N, padx=10)
pokemon1_filtered_listbox = tk.Listbox(main_frame, width=26)
pokemon1_filtered_listbox.grid(row=4, column=0, rowspan=10, sticky=tk.NSEW, padx=10)

pokemon1_name = ttk.Label(main_frame, font=('Arial', 12, 'bold'))
pokemon1_name.grid(row=3, column=1, sticky=tk.N, padx=10)
pokemon1_info = tk.Text(main_frame, width=50, height=20, font=BODY_FONT_DEF)
pokemon1_info.grid(row=4, column=1, rowspan=10, sticky=tk.NSEW, padx=10)
pokemon1_id = ttk.Label(main_frame, font=('Arial', 10))
pokemon1_id.grid(row=14, column=1, sticky=tk.N, padx=10)

fusion_caption = ttk.Label(main_frame, text='Fusion Result', font=('Arial', 12, 'bold'))
fusion_caption.grid(row=3, column=2, sticky=tk.N, padx=10)
fusion_info = tk.Text(main_frame, width=50, height=20, font=BODY_FONT_DEF)
fusion_info.grid(row=4, column=2, rowspan=10, sticky=tk.NSEW, padx=10)

pokemon2_name = ttk.Label(main_frame, font=('Arial', 12, 'bold'))
pokemon2_name.grid(row=3, column=3, sticky=tk.N, padx=10)
pokemon2_info = tk.Text(main_frame, width=50, height=20, font=BODY_FONT_DEF)
pokemon2_info.grid(row=4, column=3, rowspan=10, sticky=tk.NSEW, padx=10)
pokemon2_id = ttk.Label(main_frame, font=('Arial', 10))
pokemon2_id.grid(row=14, column=3, sticky=tk.N, padx=10)

pokemon2_filtered_label = ttk.Label(main_frame, text='Pokémon 2:', font=('Arial', 10, 'bold'))
pokemon2_filtered_label.grid(row=3, column=4, sticky=tk.N, padx=10)
pokemon2_filtered_listbox = tk.Listbox(main_frame, width=26)
pokemon2_filtered_listbox.grid(row=4, column=4, rowspan=10, sticky=tk.NSEW, padx=10)

# Bind selection

def on_select(event, selected_var, filter_var, pokemon_name, pokemon_info, pokemon_id, sticky_filters_var):
    sel = event.widget.curselection();
    if not sel: return
    selected_pokemon = event.widget.get(sel[0]); selected_var.set(selected_pokemon)
    if not sticky_filters_var.get(): filter_var.set(selected_pokemon)
    fill_side_panel(selected_pokemon, pokemon_info, pokemon_id, pokemon_name)
    if event.widget == pokemon2_filtered_listbox:
        populate_active_abilities_for(selected_pokemon); maybe_recalc_if_ready()
    else:
        maybe_recalc_if_ready()

pokemon1_filtered_listbox.bind('<<ListboxSelect>>', lambda e: on_select(e, pokemon1_var, pokemon1_filter_var, pokemon1_name, pokemon1_info, pokemon1_id, sticky_filters_var))
pokemon2_filtered_listbox.bind('<<ListboxSelect>>', lambda e: on_select(e, pokemon2_var, pokemon2_filter_var, pokemon2_name, pokemon2_info, pokemon2_id, sticky_filters_var))

for name in pokemon_stats:
    pokemon1_filtered_listbox.insert(tk.END, name); pokemon2_filtered_listbox.insert(tk.END, name)

# Debounced search & filter state
sticky_filters_var = tk.BooleanVar(value=True)
debounce_p1 = Debouncer(root, delay_ms=150); debounce_p2 = Debouncer(root, delay_ms=150)
pokemon1_entry.bind('<KeyRelease>', lambda e: debounce_p1.call(lambda: filter_pokemon(e, pokemon1_filter_var, pokemon1_entry, pokemon1_filtered_listbox)))
pokemon2_entry.bind('<KeyRelease>', lambda e: debounce_p2.call(lambda: filter_pokemon(e, pokemon2_filter_var, pokemon2_entry, pokemon2_filtered_listbox)))

# Status bar
status_text = tk.StringVar(value=STR['ready'])
status_bar = ttk.Label(root, textvariable=status_text, anchor='w', relief='sunken', padding=(6, 0))
status_bar.pack(side=tk.BOTTOM, fill=tk.X)

print(f"[FusionCalc] Running build {BUILD_TAG}")

# Key bindings
root.bind_all('<Control-Shift-D>', lambda e: show_display_options())

# Recalc policy

def force_recalc_if_ready():
    try:
        if not (globals().get('HAS_FUSION', False)):
            return
        p1 = pokemon1_var.get().strip() if 'pokemon1_var' in globals() else ''
        p2 = pokemon2_var.get().strip() if 'pokemon2_var' in globals() else ''
        if p1 in pokemon_stats and p2 in pokemon_stats: calculate_fusion_stats(p1, p2)
    except Exception:
        pass

def maybe_recalc_if_ready():
    if not AUTO_RECALC_ON_SELECT:
        return
    try:
        force_recalc_if_ready()
    except Exception:
        pass

root.mainloop()
