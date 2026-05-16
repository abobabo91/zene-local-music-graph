# zene-local-music-graph

Walks the local music library, parses filenames/folders, and builds structured graph outputs for Hungarian and US rap/trap.

## First read

Read `README.md` for project structure, workflow, data layout, and normalized schema.

## Critical rules

- Never commit secrets, caches, or logs.
- Do not mix YouTube scraping/downloading logic into this project.
- The local vault is external to this repo.

## Data integrity

- **US:** `build_us_graph.py` scans disk and regenerates normalized output. The mappings file (`data/us/us_rap_trap_mappings.md`) drives alias/group/label resolution.
- **Hungarian:** The normalized JSONs in `data/hungarian/normalized/` ARE the source of truth. There is no disk scanner — edit the normalized files directly.

## Git expectations

Good to commit: code, docs, graph outputs, mappings, visualization.

Do not commit: `__pycache__`, machine-specific temp files.
