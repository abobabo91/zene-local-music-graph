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
- `50 Cent: 50cent, Cent`
- `Drake: DRAKE`
- `Young Dolph: young dolph`
- `Cam'ron: Cam ron, Camron`
- `21 Savage: 21Savage, Savage, Savage Metro Boomin`
- `XXXTentacion: XXXTENTACION`
- `YoungBoy Never Broke Again: NBA YoungBoy, NBA Youngboy, NBA YOUNG BOY, YoungBoy`
- `Yeat: YEAT`
- `Jedi Mind Tricks / Vinnie Paz: Jedi Mind Tricks, Vinnie Paz`
- `Capone-N-Noreaga: Capone n Noreaga`
- `N.O.R.E.: Noreaga, NORE`
- `Offset: OFFSETYRN`
- `6ix9ine: 69tekashi, Tekashi69, Tekashi 69, TEKASHI69`
- `A Boogie Wit da Hoodie: aboogie, A Boogie`
- `Big K.R.I.T.: Big K.R.I.T, BIG KRIT`
- `LL Cool J: L.L. Cool J`
- `M.O.P.: M.O.P, MOP`
- `N.W.A: NWA`
- `Ol' Dirty Bastard: Ol Dirty Bastard, ODB`
- `Pusha T: pusha t`
- `The Notorious B.I.G.: The Notorious B.I.G, The Notorious BIG, Notorious B.I.G., Biggie`
- `Snoop Dogg: Snoop Doggy Dogg`
- `Soulja Boy: Soulja Boy Tell em`
- `Lil Keke: LIl' Keke Classics`
- `Eazy-E: Eazy E, Eazy-e`
- `Dr. Dre: Dr Dre, Dr.Dre Discography @320, 01 Dr Dre`
- `The Game: Game`
- `Raekwon: Reakwon`
- `Polo G: polo g`
- `King Von: king von`
- `DaBaby: dababy`
- `DJ Khaled: dj khaled`
- `Killy: KIlly`
- `Pop Smoke: POP SMOKE`
- `Boosie Badazz: boosie, Lil Boosie`
- `Webbie: webbie hits`
- `Lil Tecca: lil tecca bangers`
- `Speaker Knockerz: speaker knockerz`
- `Yungeen Ace: yungeen ace`
- `SpaceGhostPurrp: spaceghostpurrp`
- `Smokepurpp: smokepurpp`
- `Saweetie: saweetie`
- `Ice Spice: ice spice`
- `Saint Jhn: saint jhn`
- `J Dilla: j dilla`
- `Jackboy: jackboy`
- `Soulja Slim: soulja slim`
- `Boonk: boonk`
- `Internet Money: internet money`
- `T.I.: T.I`
- `Royce Da 5'9": Royce Da 5 9`
- `SchoolBoy Q: Schoolboy Q`
- `A$AP Rocky: A$AP`
- `Dilated Peoples: Dilated Peoples Discography @320, Dilated Peoples - 20 20, Dilated Peoples - Expansion Team, Dilated Peoples - The Platform`
- `Chief Keef: Cheif Keef`
- `A$AP Ferg: AAP Ferg`
- `DJ Clue: DJ Clue - The Professional, DJ Clue - The Professional 2, DJ Clue Backstage Mixtape`
- `Calboy: Calboy - Long Live The Kings`
- `SpaceGhostPurrp: SpaceGhostPurrp - Blackland Radio 66 6 BLVCKLVND RVDIX 66 6`
- `scarlxrd: scarlxrd`
- `Xzibit: xzibit-concentrate, xzibit-invade my space, xzibit-thank you`
- `Mike WiLL Made-It: Mike Will Made It, Mike WiLL Made It`
- `DaBaby: 024. DaBaby`
- `Lil Ugly Mane: Lil Ugly Mane - Mista Thug Isolation`
- `Logic: Logic - Young Sinatra`
- `Dame D.O.L.L.A.: Dame D O L L A - Confirmed`
- `Fes Taylor: Fes Taylor - The Fes Taylor Sessions`
- `Shiloh Dynasty: shiloh dynasty - all songs`
- `Morbski: Morbski - Rebel Rouzah`
- `NF: NF - Mansion`
- `Desiigner: Desiigner - New English`
- `Nav: Nav Metro Boomin - Perfect Timing`
- `Skengdo: #410 Skengdo`
- `Iggy Azalea: Iggy Azalea The New Classic 2014`
- `XXXTentacion: XXXTENTACION`
- `Desiigner: Desiigner - New English`
- `Metro Boomin: Metro Boomin - Not All Heroes Wear Capes Mp3`
- `OmenXIII: Mix - OmenXIII`
- `Project Pat: Mix - Project Pat`
- `THOUXANBANFAUNI: Mix - THOUXANBANFAUNI`

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
- `Geto Boys: Scarface, Willie D, Bushwick Bill`
- `N.W.A: Ice Cube, Dr. Dre, Eazy-E, MC Ren, DJ Yella`
- `Big Tymers: Birdman, Mannie Fresh`
- `Outkast: Andre 3000, Big Boi`
- `UGK: Bun B, Pimp C`
- `Three 6 Mafia: Juicy J, DJ Paul`
- `Dead Prez: stic.man, M-1`
- `$uicideboy$: Ruby da Cherry, $crim`

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
- `Yo Gotti: Yo Gotti Mike WiLL Made It`
- `Gucci Mane: Gucci Mane Young Thug`
- `BHAD BHABIE: Danielle Bregoli is BHAD BHABIE`
- `Moneybagg Yo: Moneybagg Yo NBA Youngboy`
- `French Montana: French Montana Chinx Drugz, French Montana Kodak Black`
- `G Herbo: G Herbo aka Lil Herb`
- `Joey Bada$$: Joey Bada$$-Summer Knights 320 Badass`
- `Sauce Walka: Sauce Walka best songs available on`
- `Swollen Members: Swollen Members-Beautiful Death Machine-2013`
- `Young Thug: Young Thug- Stoner @YoungThugWorld`
- `Fabolous: Fabolous There Is No Competition 3`
- `iLoveMakonnen: ILOVEMAKONNEN No Ma am`
- `Scarcity Budapest: Scarcity Budapest-Back to Business-2012`
- `Dom Pachino: Dom Pachino Neplatna Identita`
- `Run The Jewels: Run The Jewels 2`
- `Three 6 Mafia: sippin on some syrup by three 6 mafia`
- `Wu-Tang Clan: wu-tang killa bees-the beggaz`
- `8Ball & MJG: 8Ball MJG, 8Ball`
- `Chingy: 15Chinx French Montana`

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
