# Local Music Graph

Walks a ~15k-song local music library, parses filenames/folders, and builds structured song-by-song graphs with artist credit resolution.

## Areas

| Area | Script | Songs | Persons |
|---|---|---|---|
| US Rap/Trap | `build_us_graph.py` | 6,753 | 1,128 |
| Hungarian Rap | *(edit data directly)* | 2,201 | ~460 |
| R&B | `build_other_graph.py rnb` | 731 | 181 |
| Rock | `build_other_graph.py rock` | 627 | 145 |
| Magyar (HU other) | `build_other_graph.py magyar` | 718 | 257 |
| Electronic | `build_other_graph.py elektro` | 1,131 | 761 |
| Pop | `build_other_graph.py pop` | 1,452 | 586 |
| Alternative | `build_other_graph.py alternate` | 512 | 167 |
| Latin Music | `build_other_graph.py latino` | 263 | 124 |

## Scripts

- `build_us_graph.py` — scans `_rap/` + `_trap/`, resolves aliases/groups/labels/regions
- `build_other_graph.py <area>` — generic scanner for all `_other/` subfolders (rnb, rock, magyar, elektro, pop, alternate, latino)
- `build_toplists.py` — rebuilds `toplists.md` for Hungarian and US
- `build_visualization.py` — builds `visualization.html` with 10 tabs + combined view + artist folder browser

## Workflow

```
# Rebuild a specific area
python build_us_graph.py
python build_other_graph.py rnb

# Rebuild toplists + visualization (after any area rebuild)
python build_toplists.py
python build_visualization.py
```

## Mappings

Each area has an editable mappings file (`data/<area>/<area>_mappings.md`) with:
- **Alias normalization** — merge spelling variants, folder names, case differences
- **Groups** — define group→member relationships (US rap has weight overrides)

Edit mappings, then re-run the build script.

## Hungarian Rap

No disk scanner — the normalized JSONs in `data/hungarian/normalized/` ARE the source of truth. Edit `songs.json` and `persons.json` directly.

## Visualization

`visualization.html` is a self-contained dashboard with:
- 10 genre tabs + combined R&B+Pop+Alt tab
- Sortable artist tables with search, region filter, label filter
- US and Hungary maps with region bubbles
- Click any artist name → folder/song tree browser
