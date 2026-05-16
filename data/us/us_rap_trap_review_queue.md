# US Rap/Trap Review Queue

This file is for the next phase of the US local graph pass.

At this point, broad extraction is already working. The next step should not be more generic string matching. It should be targeted, song-by-song review of the remaining bad buckets and split artist identities.

## Priority order

1. Numeric pseudo-artists like `01`, `02`, `03`, `05`, `06`, `07`
2. Split real artists, especially `NBA YoungBoy` vs `YoungBoy Never Broke Again`
3. `Unknown Artist`
4. `Various Artists`
5. Lower-priority casing/style cleanup

## Numeric pseudo-artists

These are clearly wrong and usually come from numbered album tracks where the parser incorrectly treated the track number as the artist.

High-impact examples:

- `05` -> `77` songs
- `02` -> `68` songs
- `07` -> `66` songs
- `06` -> `65` songs

These should be reviewed from the actual files and reassigned song by song.

## Split artist: YoungBoy

Currently split across:

- `YoungBoy Never Broke Again`
- `NBA YoungBoy`

Folder evidence suggests these are part of the same real artist bucket in:

- `_trap/louisiana/NBA Youngboy`

This should be reviewed by looking at the actual filenames and then merged deliberately, not by loose global regex.

## Unknown Artist

Current count after cleanup: `23`

Main remaining locations:

- `_rap/texas/_random`
- `_rap/_usa other/_random`
- loose files in `_trap/_usa random`
- a small amount in `_trap/atlanta/_random`
- a small amount in `_trap/chicago/_random`

These are mostly files where there is genuinely weak metadata. If there is no reliable artist signal, it is okay to leave them unresolved.

## Various Artists

Current count: `40`

This should be reviewed by checking whether:

- the file is part of a true compilation
- the real primary artist is visible in the filename
- the artist should instead be inferred from a deeper folder context

## Lower-priority casing/style review

Examples:

- `DRAKE`
- `young dolph`
- `21Savage`
- `Cam ron`

These are normal cleanup items after the big bad buckets above.
