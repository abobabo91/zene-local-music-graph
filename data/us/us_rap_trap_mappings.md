# US Rap/Trap Mappings

This file is the editable structure for the US local music graph pass.

Purpose:

- capture artist aliases and spelling normalization
- define groups and crews
- define labels where useful
- define person <-> group membership
- define person <-> label affiliation when it matters

This does not need to be complete before extraction starts. It should grow as the graph is built and reviewed.

## Region normalization

Use these normalized display labels:

- `_usa other` -> `USA Other`
- `_usa random` -> `USA`
- `new york` -> `New York`
- `philly` -> `Philadelphia`
- `phily` -> `Philadelphia`
- `luisiana` -> `Louisiana`
- `louisiana` -> `Louisiana`
- `dc` -> `DC`
- `2Pac` -> `California`

## Alias normalization

Use this section for spelling/style merges.

Format:

`canonical: alias 1, alias 2, alias 3`

Examples to expand later:

- `G-Eazy: G Eazy`
- `Lil Uzi Vert: Lil Uzi`
- `Young Thug: Thugger`
- `2Pac: Tupac, Tupac Shakur`
- `50 Cent: 50cent`
- `Drake: DRAKE`
- `Young Dolph: young dolph`
- `Cam'ron: Cam ron`
- `21 Savage: 21Savage`
- `XXXTentacion: XXXTENTACION`
- `YoungBoy Never Broke Again: NBA YoungBoy, NBA Youngboy, NBA YOUNG BOY, YoungBoy`
- `Yeat: YEAT`
- `Jedi Mind Tricks / Vinnie Paz: Jedi Mind Tricks, Vinnie Paz`
- `Capone-N-Noreaga: Capone n Noreaga`
- `N.O.R.E.: Noreaga, NORE`
- `Offset: OFFSETYRN`

## Groups

Format:

`Group Name: member 1, member 2, member 3`

Fill this in as we review the graph.

Starter examples:

- `Migos: Quavo, Offset, Takeoff`
- `Rae Sremmurd: Swae Lee, Slim Jxmmi`
- `G-Unit: 50 Cent, Lloyd Banks, Tony Yayo, Young Buck`
- `D-Block Europe: Young Adz, Dirtbike LB`
- `Capone-N-Noreaga: Capone, N.O.R.E.`
- `Clipse: Pusha T, No Malice`
- `Mobb Deep: Prodigy, Havoc`
- D12: Kuniva, Proof, Kon Artis, Bizarre, Swifty
- `Wu-Tang Clan: RZA, GZA, Ol' Dirty Bastard, Method Man, Raekwon, Ghostface Killah, Inspectah Deck, U-God, Masta Killa`

## Labels

Format:

`Label Name: artist 1, artist 2, artist 3`

Only use labels that are actually useful for later cleanup or browsing.

Starter examples:

- `CMG: Yo Gotti, Moneybagg Yo, 42 Dugg, EST Gee`
- `YSL: Young Thug, Gunna, Lil Keed`
- `OTF: Lil Durk, King Von`
- `QC: Migos, Lil Baby`
- `Griselda: Westside Gunn, Conway the Machine, Benny the Butcher`

## Person entries

Use this section for artist-specific notes that do not fit cleanly into aliases/groups/labels.

Suggested format:

```md
### Artist Name
- aliases:
- groups:
- labels:
- notes:
```

Examples:

### 2Pac
- aliases: Tupac, Tupac Shakur
- groups:
- labels:
- notes: dedicated `_rap/2Pac` folder should still map to region `California`

### Playboi Carti
- aliases: Carti
- groups:
- labels: Opium
- notes:

## Folder-specific cleanup notes

Use this area for one-off rules that come from messy folder names.

Examples:

- `_rap/luisiana` is a typo folder and should normalize to `Louisiana`
- `_trap/phily` should normalize to `Philadelphia`
- some folders are artist names mixed with “best of”, “videos”, or album titles
- some loose files in `_usa random` and `_usa other` must infer artist from filename, not folder
