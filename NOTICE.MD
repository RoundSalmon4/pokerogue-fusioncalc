## 1) Credits

- **PokéRogue** — core inspiration and data semantics: <https://github.com/pagefaultgames/pokerogue>
- **Search Dex by Sandstormer** — source used to build `pokemon_data.csv`: <https://github.com/Sandstormer>

If you maintain either upstream, thank you! Please open an issue if any attribution or link needs adjustment.

---

## 2) License Note

This project is licensed under the **GNU Affero General Public License, version 3.0 (AGPL‑3.0)**.  
See **LICENSE.md** in the repository for the full license text and any supplemental notices.

---

## 3) How the build & component hashing work (verifiable)

The application embeds reproducible hashes at the top of `fusioncalc_test.py` to make each published build and its components independently verifiable.

### 3.1 Header layout (at a glance)
The file begins with comment lines, for example:

```
# BUILD_HASH: HHHHHHHHHHHH
# COMPONENT_HASHES: generated below
# func:NAME <12-hex>
# var:NAME  <12-hex>
# menu:METHOD
label=...
variable=...
command=... <12-hex>
# defaults:marker <12-hex>
# defaults:schema <12-hex>
# defaults:wiring <12-hex>
```

- `BUILD_HASH` is a **12‑hex** short SHA‑1 fingerprint of the post‑edit buffer, computed with the **first header line removed** and with `BUILD_TAG` normalized to the empty string during hashing.  
- Each `func:*`, `var:*`, and `menu:*` line is a component‑level **12‑hex** hash over that symbol’s exact text/signature.  
- `defaults:*` are **structure‑only** presence hashes that prove the Startup‑Defaults section exists and is wired correctly while being immune to simple on/off flips inside the defaults mapping.

> The file also contains `BUILD_TAG = "HHHHHHHHHHHH"` inside the module, which is set equal to `BUILD_HASH` at publish time.

### 3.2 Recomputing `BUILD_HASH` locally
To verify a distributed `fusioncalc_test.py`:

1. **Read the file bytes** and split off the first line (the `# BUILD_HASH: ...` header).  
2. In the remaining text, **normalize** the line that assigns `BUILD_TAG` to:
   
   ```
   BUILD_TAG = ""
   ```
3. Compute `H = short_sha1(remaining_text)`, where `short_sha1(x)` is the first 12 hex characters of `sha1(x)`.  
4. Confirm that the served header’s value equals `H`, **and** that the in‑file `BUILD_TAG` equals `H`.

### 3.3 Verifying component hashes
- Parse the module with a Python AST and, for every **top‑level** function and variable, re‑extract the original text slice and compute the 12‑hex short SHA‑1. Compare to the corresponding `# func:*` / `# var:*` header lines.  
- For menu entries, re‑scan the module for calls to `add_command`, `add_checkbutton`, `add_radiobutton`, and `add_cascade`. For each call, reconstruct the normalized signature string:
  
  ```
  menu:METHOD
label=...
variable=...
command=...
  ```
  
  and verify its short SHA‑1 matches the `# menu:*` line.

### 3.4 Verifying Startup‑Defaults presence (value‑agnostic)
The header includes three presence hashes that do **not** change when you merely toggle defaults True/False:
- `defaults:marker` — proves the section header text and function name anchors exist.  
- `defaults:schema` — hashes the **key and type shape** of the `DEFAULTS` dict (values normalized to their types), so it changes only if keys/nesting/types change.  
- `defaults:wiring` — proves there is exactly one `apply_defaults()` call, **after** `display_vars = init_display_vars()`.

Recomputing these three lines requires only AST‑level inspection and simple string hashing (no execution).

---

## 4) Repro notes

- Hashing uses standard **SHA‑1** truncated to 12 hex characters to keep headers compact.  
- The exact normalization steps (remove first line; set `BUILD_TAG = ""` during hashing) ensure you can reproduce `BUILD_HASH` from the published source without circularity.

If you need ready‑to‑run verifier snippets (Python) or CI examples, open an issue and we will include them here.
