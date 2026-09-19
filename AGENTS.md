# Noisemaker for Python

Pure-Python CPU implementation of the Noisemaker shader engine, ported from and verified against `noisemaker-for-cpu`.

## Strict Rules

HARD, PERMANENT, INVIOLABLE BAN: BANNED FROM SYMLINKS. Never create, introduce, or use symbolic links anywhere in checkouts, repositories, configuration, scripts, or documentation. All files must be regular files. Zero exceptions.

HARD, PERMANENT, INVIOLABLE BAN: Research documents must be written and presented strictly in the established technical whitepaper style. Banned from slop headlines, promotional/slogan headers, parenthetical subtitles in titles, stat cards, metric cards, decorative callouts, marketing-speak, and invented report layouts. Zero exceptions.

## Testing & Parity Verification

- **Routine test suite**: `.venv/bin/pytest`
- **Fast cross-language parity**: `.venv/bin/python scripts/parity.py` (compares all eligible catalog effects byte-exact against sibling `noisemaker-for-cpu`; optionally override checkout location with `NOISEMAKER_CPU_DIR`)
- **Full cross-language DSL / volume parity**: `.venv/bin/pytest tests/test_parity.py`
