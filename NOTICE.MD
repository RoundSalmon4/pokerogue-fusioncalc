# NOTICE

## Acknowledgments

- **PokéRogue** — core inspiration and data semantics: <https://github.com/pagefaultgames/pokerogue>
- **Search Dex by Sandstormer** — source used to build `pokemon_data.csv`: <https://github.com/Sandstormer>

If you maintain either upstream, thank you! Please open an issue if any attribution or link needs adjustment.

## How to Verify

1. **Download both files**
   - `fusioncalc.py`
   - `fusioncalc_verify.py`

2. **Run the verifier locally**
   ```bash
   python fusioncalc_verify.py fusioncalc.py
   ```

3. **Interpret the output**
   - "ok": true → The file’s contents exactly match its embedded BUILD_HASH and BUILD_TAG. Your copy is authentic and unchanged.
   - "ok": false → The file does not match its declared hash, indicating corruption, modification, or an incomplete download.

### What Verification Means

Verification ensures:
- The file is byte‑for‑byte identical to the official version from this repository.
- The internal integrity markers (BUILD_HASH and BUILD_TAG) are consistent.
- The script has passed a full AST parse (i.e., it's syntactically valid).

If verification passes, you can confidently use the file knowing it has not been modified.

## License

This project is licensed under the **GNU Affero General Public License, version 3.0 (AGPL‑3.0)**.  
See  `LICENSE` in the repository for the full license text and any supplemental notices.
