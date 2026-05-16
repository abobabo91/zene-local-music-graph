# Local Music Graph

Separate from YouTube scraping. Walks the local music library, parses filenames/folders, and builds structured graph outputs for Hungarian rap/trap and US rap/trap.

## Scripts

- `build_us_graph.py` — scans disk (`_rap/` + `_trap/`), extracts + normalizes into `data/us/normalized/`
- `build_toplists.py` — rebuilds `toplists.md` for both Hungarian and US from normalized data
- `build_visualization.py` — builds `visualization.html` (interactive tables + maps) from normalized data

## Workflow

### US: full rebuild from disk

```
python build_us_graph.py        # scan disk → normalized output
python build_toplists.py        # rebuild toplists.md
python build_visualization.py   # rebuild visualization.html
```

The US graph is fully reproducible from disk. `build_us_graph.py` walks `_rap/` and `_trap/` (excluding `_rap/_other` and `_trap/_other country random`), parses filenames for artist/title/features, applies alias normalization from `us_rap_trap_mappings.md`, resolves groups/labels, and writes the normalized song-first output.

### Hungarian: edit normalized data directly

```
python build_toplists.py        # rebuild toplists.md
python build_visualization.py   # rebuild visualization.html
```

The Hungarian graph was built from a one-time extraction pass. There is no disk scanner — the normalized JSONs in `data/hungarian/normalized/` ARE the source of truth. To add songs or fix credits, edit the normalized files directly (primarily `songs.json` and `persons.json`).

The original extraction pipeline was:
1. A disk scanner (no longer exists) walked `_magyar rap/`, `_magyar trap/`, and `_other/_magyar/_cigany/`
2. It produced a legacy artist-first `graph.json` (persons → songs)
3. A normalizer converted that into the current song-first normalized schema (songs → persons/groups/labels)
4. The legacy file and normalizer were deleted after confirming 100% data coverage in the normalized output

### Editing mappings

- **US:** edit `data/us/us_rap_trap_mappings.md` (aliases, groups, labels), then re-run `build_us_graph.py`
- **Hungarian:** edit `data/hungarian/hungarian_rap_mappings.md` for reference, but the mappings are already baked into the normalized data
- **Region overrides (Hungarian):** edit `data/hungarian/normalized/region_overrides.json` — manual person→city assignments used by toplists and visualization

### Outstanding review items

`data/us/us_rap_trap_review_queue.md` tracks known issues: numeric pseudo-artists (`01`, `02`, etc.), split artist identities (YoungBoy), and unattributed tracks.

## Data layout

```
data/hungarian/
  hungarian_rap_mappings.md          # label/group/person reference
  normalized/
    songs.json                       # source of truth (2,201 songs)
    persons.json, groups.json,       # derived indexes
    labels.json, regions.json
    metadata.json, validation.json   # counts and checks
    toplists.md                      # human-readable rankings
    region_overrides.json            # manual person→city

data/us/
  us_rap_trap_mappings.md            # editable alias/group/label structure
  us_rap_trap_review_queue.md        # outstanding review items
  normalized/
    songs.json                       # source of truth (6,817 songs)
    persons.json, groups.json,       # derived indexes
    labels.json, regions.json
    metadata.json, validation.json
    toplists.md
```

## Normalized schema

Songs are the source of truth. Each song has:
- `song_id`, `file`, `title`
- `primary_artists`, `featuring_artists`, `artists` (all involved)
- `credits` (structured: entity + type + role)
- `source_root` (`_rap` / `_trap`), `folder_region`

Persons, groups, labels, and regions are separate derived indexes with back-references to song IDs.
