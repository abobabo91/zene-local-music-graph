# My Music Collection

Song-by-song graph of a ~15,000-track personal music library. Parses filenames and folder structures to build structured artist credit data across 9 genre areas, with an interactive visualization dashboard.

**[Live Dashboard](https://abobabo91.github.io/zene-local-music-graph/)**

## What it does

1. Walks the local music folder tree (mp3/wma/m4a/flac)
2. Extracts artist names, song titles, and featuring credits from filenames and folder names
3. Resolves aliases, merges duplicates, expands group memberships
4. Computes normalized and adjusted song credit scores
5. Generates a self-contained HTML dashboard with interactive tables, maps, and folder browsers

## Areas

| Area | Songs | Artists | Source folders |
|---|---|---|---|
| US Rap/Trap | 6,753 | 1,128 | `_rap/`, `_trap/` |
| Hungarian Rap | 2,201 | ~460 | `_magyar rap/`, `_magyar trap/` |
| R&B | 731 | 181 | `_other/_rnb/` |
| Rock | 627 | 145 | `_other/_rock/` |
| Magyar (HU other) | 718 | 257 | `_other/_magyar/` |
| Electronic | 1,131 | 761 | `_other/_elektro/` |
| Pop | 1,452 | 586 | `_other/_pop/` |
| Alternative | 512 | 167 | `_other/_alternate/` |
| Latin Music | 263 | 124 | `_other/_latino/` |

## Visualization

The dashboard ([index.html](index.html)) is a self-contained HTML file with:
- **10 genre tabs** + combined R&B+Pop+Alt view
- **Sortable artist tables** with search, region filter, label filter
- **US and Hungary maps** with region bubbles and top artists per city
- **Click any artist** to browse their full folder/album/song tree on disk
- **Ctrl+click** hint on chart title for keyboard shortcuts

## How it was built

### Parsing pipeline

The core challenge: extract structured artist credits from messy, inconsistent filenames and folder names. The pipeline handles:

- **Track number stripping**: `05. 50 Cent - In Da Club.mp3` → artist: "50 Cent", title: "In Da Club" (without interpreting "50" as a track number and leaving "Cent" as the artist)
- **Feature extraction**: `Drake feat. Rihanna - Take Care.mp3` → primary: Drake, featuring: Rihanna
- **Folder context**: files in `_trap/atlanta/Young Thug/Punk/` inherit "Young Thug" as artist context
- **Compilation detection**: folders like `HIPHOPTXL`, `_random`, `Billboard`, `DatPiff` are recognized as compilations where each file's artist comes from the filename, not the folder
- **YouTube artifact cleanup**: strip "(Official Video)", "[HD]", "WSHH Exclusive", "- YouTube" suffixes
- **Billboard catalog prefixes**: strip `2006-005 Shakira` → "Shakira"
- **Accent normalization**: Hungarian characters (á→a, ő→o, ű→u) for consistent matching

### Alias resolution

Each area has a mappings file (`data/<area>/<area>_mappings.md`) that defines:
- **Aliases**: `6ix9ine: 69tekashi, Tekashi69, TEKASHI69` — merged 6 separate entries into one (17→45 songs)
- **Groups**: `Migos: Quavo, Offset, Takeoff` — members get individual credit for group songs
- **Weight overrides**: `Scarface: Geto Boys → 1/2` — Scarface gets half credit for Geto Boys songs instead of the default 1/N

### Cleanup process

4 rounds of parallel AI agent review (10 agents per round) identified and fixed:
- **601 junk/duplicate person entries removed** (track numbers as artists, album titles, concatenated names, compilation folder names, encoding artifacts)
- **213 duplicate audio files deleted** (verified by duration + file size + spectral audio analysis using librosa and chromaprint)
- **592 songs moved** from compilation/playlist folders to their correct artist folders
- **200+ alias mappings** across all areas
- **Accent normalization** for Hungarian names via transliteration map

### Scoring

Two scoring methods for artist rankings:
- **Normalized**: each song's credit is split equally among all credited persons (1/N per song)
- **Adjusted**: solo primary artists get full credit (1.0), group members divide, features get 1/N. Weight overrides customize this per artist-group pair (e.g., Eminem gets 1/3 for D12 songs, 50 Cent gets 1/2 for G-Unit songs)

## Scripts

| Script | Purpose |
|---|---|
| `common.py` | Shared constants and text utilities (imported by all scripts) |
| `build_us_graph.py` | Scan `_rap/` + `_trap/`, resolve aliases/groups/labels/regions |
| `build_other_graph.py <area>` | Generic scanner for any `_other/` subfolder |
| `build_toplists.py` | Rebuild `toplists.md` for Hungarian and US |
| `build_visualization.py` | Build the `index.html` dashboard from all area data |

## Data layout

```
data/<area>/
  <area>_mappings.md          # alias/group definitions
  normalized/
    songs.json                # song-by-song credits (source of truth)
    persons.json              # artist index with song references
    metadata.json             # counts
    groups.json               # group definitions (US/Hungarian only)
    labels.json, regions.json # US only
    toplists.md               # human-readable rankings (US/Hungarian only)
```

## Tech

- Python (pathlib, json, re, collections)
- mutagen — audio metadata/duration reading
- librosa + chromaprint (fpcalc) — spectral audio fingerprinting for duplicate detection
- Chart.js — not used here but in the sibling genre-timeline project
- Zero external dependencies for the visualization (self-contained HTML + inline data)
