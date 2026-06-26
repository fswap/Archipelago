# Elden Ring AP — Check-Name Legend

> Auto-derived from `worlds/eldenring/locations.py` (region prefixes + subarea codes pulled
> straight from the `lean` location set, not invented). Regenerate after large location edits.

Lean check names are compact by design. Every name follows one shape:

```
REGION/SUBAREA: Item name - directional hint
        e.g.  CL/(SCT): Somber Smithing Stone [7] - scarab to NE near the lift
```
- **REGION** — the coarse area (table below). ~50 codes.
- **SUBAREA** — a grace, landmark, or sub-dungeon *inside* that region. A code in
  **(parentheses)** is almost always a named sub-dungeon (catacomb / cave / tunnel /
  hero's grave / legacy dungeon) that has its own region entry; a **bare** code is a Site of
  Grace or overworld landmark within the parent region.
- **directional hint** — `N/S/E/W` and combos (`NE`, `SW`, …) are compass directions from the
  named grace/landmark; relative terms (`up`, `behind`, `across`) are literal.

This legend covers all **57 region prefixes** and **264 subarea codes** that
appear across the **443 lean checks**.

---

## 1. Region prefixes

### Limgrave

| Prefix | Region | Lean checks |
|---|---|---|
| `LG` | Limgrave | 25 |
| `SV` | Stormveil Castle  ⚠ also reused for DLC Scaduview — disambiguate by item/region | 12 |

### Weeping

| Prefix | Region | Lean checks |
|---|---|---|
| `WP` | Weeping Peninsula | 16 |
| `WP(CBC)` | Weeping Peninsula / Callu Baptismal Church | 1 |

### Liurnia

| Prefix | Region | Lean checks |
|---|---|---|
| `AR` | Ainsel River (entrance) | 1 |
| `LL` | Liurnia of the Lakes | 43 |
| `RLA` | Raya Lucaria Academy | 7 |
| `RSP` | Ruin-Strewn Precipice | 2 |

### Caelid

| Prefix | Region | Lean checks |
|---|---|---|
| `CL` | Caelid | 28 |
| `DB` | Greyoll's Dragonbarrow | 16 |

### Underground

| Prefix | Region | Lean checks |
|---|---|---|
| `DD` | Deeproot Depths | 3 |
| `LR` | Lake of Rot | 2 |
| `MA` | Moonlight Altar | 3 |
| `NR` | Nokron, Eternal City | 5 |
| `NS` | Nokstella, Eternal City (within Ainsel River Main) | 1 |
| `SR` | Siofra River | 3 |

### Altus

| Prefix | Region | Lean checks |
|---|---|---|
| `(VM)` | Volcano Manor Prison-Town Dungeon (RLA-warp variant) | 1 |
| `AP` | Altus Plateau | 29 |
| `MtG` | Mt. Gelmir | 13 |
| `TSC` | The Shaded Castle (Altus Plateau) | 2 |
| `VM` | Volcano Manor | 5 |

### Capital

| Prefix | Region | Lean checks |
|---|---|---|
| `CO` | Capital Outskirts | 18 |
| `DTEA` | Divine Tower of East Altus | 1 |
| `LAC` | Leyndell, Ashen Capital | 6 |
| `LRC` | Leyndell, Royal Capital | 4 |
| `SSG` | Subterranean Shunning-Grounds | 2 |

### Mountaintops

| Prefix | Region | Lean checks |
|---|---|---|
| `FL` | Forbidden Lands | 4 |
| `FP` | Flame Peak | 9 |
| `MotG` | Mountaintops of the Giants | 17 |

### Snowfield

| Prefix | Region | Lean checks |
|---|---|---|
| `CS` | Consecrated Snowfield | 16 |
| `MP` | Mohgwyn Palace | 3 |

### Haligtree

| Prefix | Region | Lean checks |
|---|---|---|
| `EBH` | Elphael, Brace of the Haligtree | 5 |
| `MH` | Miquella's Haligtree | 2 |

### Endgame

| Prefix | Region | Lean checks |
|---|---|---|
| `ET` | Erdtree (final) | 1 |
| `FA` | Crumbling Farum Azula | 6 |

### DLC: Gravesite

| Prefix | Region | Lean checks |
|---|---|---|
| `BTS` | Belurat, Tower Settlement | 6 |
| `CE` | Castle Ensis | 4 |
| `CHG` | Charo's Hidden Grave | 4 |
| `GP` | Gravesite Plain | 19 |
| `JP` | Jagged Peak | 8 |

### DLC: Scadu Altus

| Prefix | Region | Lean checks |
|---|---|---|
| `ARR` | Ancient Ruins of Rauh | 5 |
| `CC` | Cerulean Coast | 10 |
| `ER` | Ellac River | 2 |
| `FRM` | Finger Ruins of Miyr | 2 |
| `RB` | Rauh Base | 9 |
| `SA` | Scadu Altus | 21 |
| `SCF` | Stone Coffin Fissure | 2 |

### DLC: Shadow Keep

| Prefix | Region | Lean checks |
|---|---|---|
| `HL` | Hinterland | 3 |
| `SK` | Shadow Keep (also Scadutree Base via TWS) | 11 |

### DLC: Abyss

| Prefix | Region | Lean checks |
|---|---|---|
| `AW` | Abyssal Woods | 2 |
| `MM` | Midra's Manse | 2 |
| `RR` | Recluses' River | 9 |

### DLC: Finale

| Prefix | Region | Lean checks |
|---|---|---|
| `EI` | Enir Ilim | 6 |

### anomaly

| Prefix | Region | Lean checks |
|---|---|---|
| `LG(TCM)` | Limgrave / Third Church of Marika (suffix form, no slash) | 3 |
| `LRC|LAC` | Royal Capital→Ashen Capital transition (compound phase tag) | 1 |

### DLC: anomaly

| Prefix | Region | Lean checks |
|---|---|---|
| `BTS|EI` | Belurat→Enir Ilim transition (compound phase tag) | 1 |
| `SA?FR` | TYPO for SA/FR — Scadu Altus / Finger Ruins (fix the '?' to '/') | 1 |

---

## 2. Subarea codes, by region

Each code below is shown with the **exact region entry it resolves to** in `locations.py`
(authoritative — taken from the table the check lives in). Parenthesised = sub-dungeon;
bare = grace/landmark within the listed region.

**`LG` — Limgrave**

| Subarea | Resolves to |
|---|---|
| `(CC)` | Coastal Cave |
| `(DC)` | Deathtouched Catacombs |
| `(FH)` | Limgrave |
| `(FHE)` | Limgrave |
| `(FHG)` | Fringefolk Hero's Grave |
| `(GC)` | Groveside Cave |
| `(HC)` | Highroad Cave |
| `(LT)` | Limgrave Tunnels |
| `(MCC)` | Murkwater Catacombs |
| `(SC)` | Stormfoot Catacombs |
| `(SE)` | Stormhill |
| `(SWV)` | Limgrave |
| `(WS)` | Stormhill |
| `ALN` | Limgrave |
| `DBR` | Limgrave |
| `FHW` | Limgrave |
| `ME` | Limgrave |
| `SS` | Stormhill |
| `TFS` | Limgrave |
| `WS` | Stormhill |

**`SV` — Stormveil Castle**

| Subarea | Resolves to |
|---|---|
| `(SC)` | Scaduview |
| `CT` | Stormveil Start |
| `SKBG` | Scaduview |
| `SeC` | Stormveil Castle |
| `StC` | Stormveil Start |

**`WP` — Weeping Peninsula**

| Subarea | Resolves to |
|---|---|
| `(CM)` | Weeping Peninsula |
| `(CP)` | Weeping Peninsula |
| `(EC)` | Earthbore Cave |
| `(FCM)` | Weeping Peninsula |
| `(IC)` | Impaler's Catacombs |
| `(MT)` | Morne Tunnel |
| `(TCC)` | Tombsward Catacombs |
| `(TCV)` | Tombsward Cave |
| `(WE)` | Weeping Peninsula |
| `CM` | Weeping Peninsula |
| `CMR` | Weeping Peninsula |
| `DHFR` | Weeping Peninsula |
| `ME` | Weeping Peninsula |

**`AR` — Ainsel River (entrance)**

| Subarea | Resolves to |
|---|---|
| `ARD` | Ainsel River |

**`LL` — Liurnia of the Lakes**

| Subarea | Resolves to |
|---|---|
| `(ACC)` | Academy Crystal Cave |
| `(AGT)` | Liurnia of The Lakes |
| `(BC)` | Bellum Highway |
| `(BKC)` | Black Knife Catacombs |
| `(CC)` | Cliffbottom Catacombs |
| `(CE)` | Liurnia of The Lakes |
| `(CIn)` | Bellum Highway |
| `(CIr)` | Liurnia of The Lakes |
| `(CM)` | Liurnia of The Lakes |
| `(CV)` | Liurnia of The Lakes |
| `(DV)` | Carian Study Hall (Inverted) |
| `(LCC)` | Lakeside Crystal Cave |
| `(ME)` | Liurnia of The Lakes |
| `(REC)` | Road's End Catacombs |
| `(RGE)` | Caria Manor |
| `(RLCT)` | Raya Lucaria Crystal Tunnel |
| `(SC)` | Stillwater Cave |
| `(TFB)` | Liurnia of The Lakes |
| `(TFB/CA)` | The Four Belfries (Chapel of Anticipation) |
| `(VA)` | Liurnia of The Lakes |
| `AS` | Liurnia of The Lakes |
| `BC` | Bellum Highway |
| `BS` | Liurnia of The Lakes |
| `EME` | Bellum Highway |
| `GTB` | Liurnia of The Lakes |
| `GTN` | Liurnia of The Lakes |
| `MEW` | Liurnia of The Lakes |
| `RM` | Liurnia of The Lakes |
| `RVV` | Liurnia of The Lakes |
| `SeI` | Liurnia of The Lakes |
| `TQ` | Liurnia of The Lakes |
| `VA` | Liurnia of The Lakes |

**`RLA` — Raya Lucaria Academy**

| Subarea | Resolves to |
|---|---|
| `DB` | Raya Lucaria Academy Main |
| `MAG` | Raya Lucaria Academy |
| `RLGL` | Raya Lucaria Academy Chest |
| `SC` | Raya Lucaria Academy |

**`RSP` — Ruin-Strewn Precipice**

| Subarea | Resolves to |
|---|---|
| `RSPO` | Ruin-Strewn Precipice |

**`CL` — Caelid**

| Subarea | Resolves to |
|---|---|
| `(AC)` | Abandoned Cave |
| `(CCC)` | Caelid Catacombs |
| `(CP)` | Caelid |
| `(GC)` | Gaol Cave |
| `(GT)` | Gale Tunnel |
| `(MEC)` | Minor Erdtree Catacombs |
| `(RC)` | Redmane Castle Post Radahn |
| `(SCT)` | Sellia Crystal Tunnel |
| `(STS)` | Caelid |
| `(WD)` | Wailing Dunes |
| `(WDC)` | War-Dead Catacombs |
| `CHS` | Caelid |
| `IA` | Caelid |
| `MEW` | Caelid |
| `SASB` | Caelid |

**`DB` — Greyoll's Dragonbarrow**

| Subarea | Resolves to |
|---|---|
| `(DC)` | Dragonbarrow Cave |
| `(DT)` | Divine Tower of Caelid |
| `(FF)` | Dragonbarrow |
| `(IMS)` | Dragonbarrow |
| `(SE)` | Dragonbarrow |
| `(SH)` | Sellia Hideaway |
| `BS` | Dragonbarrow |
| `FG` | Dragonbarrow |
| `LR` | Dragonbarrow |
| `MEE` | Dragonbarrow |

**`DD` — Deeproot Depths**

| Subarea | Resolves to |
|---|---|
| `AR` | Deeproot Depths |
| `PDT` | Deeproot Depths Boss |
| `TNEC` | Deeproot Depths |

**`LR` — Lake of Rot**

| Subarea | Resolves to |
|---|---|
| `LRS` | Lake of Rot |

**`MA` — Moonlight Altar**

| Subarea | Resolves to |
|---|---|
| `(RE)` | Moonlight Altar |
| `MA` | Moonlight Altar |

**`NR` — Nokron, Eternal City**

| Subarea | Resolves to |
|---|---|
| `(HG)` | Nokron, Eternal City |
| `(SA)` | Nokron, Eternal City |
| `NEC` | Nokron, Eternal City Start |

**`NS` — Nokstella, Eternal City (within Ainsel River Main)**

| Subarea | Resolves to |
|---|---|
| `NEC` | Ainsel River Main |

**`SR` — Siofra River**

| Subarea | Resolves to |
|---|---|
| `(HG)` | Siofra River |
| `BW` | Siofra River |
| `WW` | Siofra River |

**`(VM)` — Volcano Manor Prison-Town Dungeon (RLA-warp variant)**

| Subarea | Resolves to |
|---|---|
| `SIC` | Volcano Manor Dungeon |

**`AP` — Altus Plateau**

| Subarea | Resolves to |
|---|---|
| `(AT)` | Altus Tunnel |
| `(DWV)` | Altus Plateau |
| `(OAT)` | Old Altus Tunnel |
| `(PG)` | Perfumer's Grotto |
| `(SC)` | Altus Plateau / Sage's Cave |
| `(SCM)` | Altus Plateau |
| `(SHG)` | Sainted Hero's Grave |
| `(UC)` | Unsightly Catacombs |
| `AHJ` | Altus Plateau |
| `EGH` | Altus Plateau |
| `GLE` | Altus Plateau |
| `ME` | Altus Plateau |
| `RP` | Altus Plateau |
| `SHG` | Altus Plateau |
| `VW` | Altus Plateau |
| `WhR` | Altus Plateau |

**`MtG` — Mt. Gelmir**

| Subarea | Resolves to |
|---|---|
| `(GHG)` | Gelmir Hero's Grave |
| `(SC)` | Seethewater Cave |
| `(VC)` | Volcano Cave |
| `(WC)` | Wyndham Catacombs |
| `FL` | Mt. Gelmir |
| `ME` | Mt. Gelmir |
| `NMGC` | Mt. Gelmir |
| `PSA` | Mt. Gelmir |
| `SR` | Mt. Gelmir |
| `VM` | Mt. Gelmir |

**`TSC` — The Shaded Castle (Altus Plateau)**

| Subarea | Resolves to |
|---|---|
| `SCIG` | Altus Plateau |

**`VM` — Volcano Manor**

| Subarea | Resolves to |
|---|---|
| `AP` | Volcano Manor Upper |
| `GH` | Volcano Manor |
| `VM` | Volcano Manor Entrance |

**`CO` — Capital Outskirts**

| Subarea | Resolves to |
|---|---|
| `(AHG)` | Auriza Hero's Grave |
| `(AST)` | Auriza Side Tomb |
| `(HMS)` | Capital Outskirts |
| `(ME)` | Capital Outskirts |
| `(ST)` | Sealed Tunnel |
| `HMS` | Capital Outskirts |
| `OWPT` | Capital Outskirts |

**`LAC` — Leyndell, Ashen Capital**

| Subarea | Resolves to |
|---|---|
| `LCA` | Leyndell, Ashen Capital |
| `QB` | Leyndell, Ashen Capital Throne |

**`LRC` — Leyndell, Royal Capital**

| Subarea | Resolves to |
|---|---|
| `ET` | Leyndell, Royal Capital Throne |
| `LAC|WCR` | Leyndell, Royal Capital Unmissable |
| `QB` | Leyndell, Royal Capital Throne |
| `WCR` | Leyndell, Royal Capital Throne |

**`SSG` — Subterranean Shunning-Grounds**

| Subarea | Resolves to |
|---|---|
| `(LC)` | Leyndell Catacombs |
| `FD` | Subterranean Shunning-Grounds |

**`FL` — Forbidden Lands**

| Subarea | Resolves to |
|---|---|
| `FL` | Forbidden Lands |
| `GLR` | Forbidden Lands |

**`FP` — Flame Peak**

| Subarea | Resolves to |
|---|---|
| `(CR)` | Flame Peak |
| `(GCHG)` | Giant-Conquering Hero's Grave |
| `FF` | Flame Peak |

**`MotG` — Mountaintops of the Giants**

| Subarea | Resolves to |
|---|---|
| `(CS)` | Mountaintops of the Giants |
| `(FCM)` | Mountaintops of the Giants |
| `(GMC)` | Giants' Mountaintop Catacombs |
| `(LCE)` | Mountaintops of the Giants |
| `(ME)` | Mountaintops of the Giants |
| `(SC)` | Spiritcaller Cave |
| `CSMG` | Mountaintops of the Giants |
| `FR` | Mountaintops of the Giants |

**`CS` — Consecrated Snowfield**

| Subarea | Resolves to |
|---|---|
| `(CF)` | Cave of the Forlorn |
| `(CSC)` | Consecrated Snowfield Catacombs |
| `(HPH)` | Hidden Path to the Haligtree |
| `(YAT)` | Yelough Anix Tunnel |
| `AD` | Consecrated Snowfield |
| `CF` | Consecrated Snowfield |
| `CS` | Consecrated Snowfield |
| `ICS` | Consecrated Snowfield |
| `ME` | Consecrated Snowfield |
| `OLT` | Consecrated Snowfield |

**`MP` — Mohgwyn Palace**

| Subarea | Resolves to |
|---|---|
| `(MDM)` | Mohgwyn Palace |
| `PALR|(MDM)` | Mohgwyn Palace |

**`EBH` — Elphael, Brace of the Haligtree**

| Subarea | Resolves to |
|---|---|
| `EIW` | Elphael, Brace of the Haligtree |
| `HR` | Elphael, Brace of the Haligtree |
| `PR` | Elphael, Brace of the Haligtree |

**`MH` — Miquella's Haligtree**

| Subarea | Resolves to |
|---|---|
| `HTP` | Miquella's Haligtree |

**`FA` — Crumbling Farum Azula**

| Subarea | Resolves to |
|---|---|
| `BGB` | Farum Azula Main |
| `DTL` | Farum Azula Main |
| `DTR` | Farum Azula Main |
| `DTT` | Farum Azula |

**`BTS` — Belurat, Tower Settlement**

| Subarea | Resolves to |
|---|---|
| `BTS` | Belurat |
| `EI|SR` | Enir Ilim |
| `SF` | Belurat |
| `SPA` | Belurat |
| `TDB` | Belurat |

**`CE` — Castle Ensis**

| Subarea | Resolves to |
|---|---|
| `(FRF)` | Fog Rift Fort |
| `CEC` | Castle Ensis |
| `CLC` | Castle Ensis |

**`CHG` — Charo's Hidden Grave**

| Subarea | Resolves to |
|---|---|
| `(LG)` | Lamenter's Gaol (Entrance) / Lamenter's Gaol (Lower) / Lamenter's Gaol (Upper) |
| `CHG` | Charo's Hidden Grave |

**`GP` — Gravesite Plain**

| Subarea | Resolves to |
|---|---|
| `(AAV)` | Gravesite Plain |
| `(BG)` | Belurat Gaol |
| `(CC)` | Gravesite Plain |
| `(DP)` | Dragon's Pit |
| `(FRC)` | Fog Rift Catacombs |
| `(WNM)` | Gravesite Plain |
| `BG` | Gravesite Plain |
| `CF` | Gravesite Plain |
| `CRT` | Gravesite Plain |
| `MGC` | Gravesite Plain |
| `PPC` | Gravesite Plain |
| `SR` | Gravesite Plain |
| `TPC` | Gravesite Plain |

**`JP` — Jagged Peak**

| Subarea | Resolves to |
|---|---|
| `DPT` | Jagged Peak Foot |
| `FJP` | Jagged Peak / Jagged Peak Foot |
| `JPM` | Jagged Peak |
| `JPS` | Jagged Peak |

**`ARR` — Ancient Ruins of Rauh**

| Subarea | Resolves to |
|---|---|
| `ARGS` | Ancient Ruins of Rauh |
| `CBME` | Ancient Ruins of Rauh |
| `RARE` | Ancient Ruins of Rauh |
| `RARW` | Ancient Ruins of Rauh |

**`CC` — Cerulean Coast**

| Subarea | Resolves to |
|---|---|
| `CC` | Cerulean Coast |
| `CCC` | Cerulean Coast |
| `CCW` | Cerulean Coast |

**`ER` — Ellac River**

| Subarea | Resolves to |
|---|---|
| `(RC)` | Rivermouth Cave |
| `ERC` | Ellac River |

**`RB` — Rauh Base**

| Subarea | Resolves to |
|---|---|
| `(NNM)` | Rauh Base |
| `(SRC)` | Scorpion River Catacombs |
| `(TTR)` | Rauh Base |
| `RN` | Rauh Base |

**`SA` — Scadu Altus**

| Subarea | Resolves to |
|---|---|
| `(BG)` | Bonny Gaol |
| `(BV)` | Scadu Altus |
| `(CC)` | Scadu Altus |
| `(CMM)` | Finger Ruins of Miyr / Scadu Altus |
| `BV` | Scadu Altus |
| `HC` | Scadu Altus |
| `MR` | Scadu Altus |
| `SC` | Scadu Altus |

**`SCF` — Stone Coffin Fissure**

| Subarea | Resolves to |
|---|---|
| `FC` | Stone Coffin Fissure |
| `FD` | Stone Coffin Fissure |

**`HL` — Hinterland**

| Subarea | Resolves to |
|---|---|
| `FH` | Hinterland |
| `HL` | Hinterland |

**`SK` — Shadow Keep (also Scadutree Base via TWS)**

| Subarea | Resolves to |
|---|---|
| `CDE` | Shadow Keep, Church District |
| `DCE` | Shadow Keep Storehouse |
| `SFiF` | Shadow Keep Storehouse |
| `SFoF` | Shadow Keep Storehouse |
| `SKMG` | Shadow Keep |
| `SSF` | Shadow Keep Storehouse |
| `TWS` | Scadutree Base |

**`AW` — Abyssal Woods**

| Subarea | Resolves to |
|---|---|
| `(AC)` | Abyssal Woods |
| `AW` | Abyssal Woods |

**`MM` — Midra's Manse**

| Subarea | Resolves to |
|---|---|
| `SFC` | Midra's Manse |

**`RR` — Recluses' River**

| Subarea | Resolves to |
|---|---|
| `(DC)` | Darklight Catacombs |
| `(ENM)` | Recluses' River |
| `(VF)` | Recluses' River |
| `RRD` | Recluses' River |
| `RU` | Recluses' River |

**`EI` — Enir Ilim**

| Subarea | Resolves to |
|---|---|
| `CCA` | Enir Ilim |
| `DGFS` | Enir Ilim |
| `FR` | Enir Ilim |
| `SR` | Enir Ilim |

---

## 3. Worked examples

- `CL/(SCT): Somber Smithing Stone [7] - scarab to NE`
  - CL = Caelid; (SCT) = a parenthesised sub-dungeon resolving to **Sellia Crystal Tunnel**; item is a Somber Smithing Stone [7], dropped by a scarab to the north-east of the grace.
- `SV/SeC: Godrick's Great Rune - mainboss drop`
  - SV = Stormveil Castle; SeC = the Secluded Cell grace area; reward is Godrick's Great Rune from the main boss.
- `LL/SeI: Glass Shard - to S on isle`
  - LL = Liurnia of the Lakes; SeI = a grace/landmark within Liurnia (a lake isle); item is to the south on that isle.
- `SA?FR: Aspects of the Crucible: Wings - boss drop`
  - Reads as a typo: `SA?FR` should be `SA/FR` = Scadu Altus / Finger Ruins. Recommend fixing the `?` to `/` in locations.py.

---

## 4. Known data anomalies (candidates to clean up later)

These are non-standard prefixes found in the lean set. They decode fine but are worth
normalising if a verbatim rename pass ever happens:

- **`SV` is overloaded** — Stormveil Castle (base) *and* DLC **Scaduview / Scadutree Base**
  (`SV/SKBG`, `SV/(SC)` carry Scadutree Fragments). Disambiguate by item/region; the DLC ones
  are clearly Shadow-Realm content.
- **`SA?FR`** — a literal `?` where a `/` belongs. Single occurrence (Aspects of the Crucible:
  Wings). Should be `SA/FR`.
- **Compound `|` tags** (`BTS|EI`, `LRC|LAC`, `MP/PALR|(MDM)`) — mark a check that straddles two
  phases/regions (e.g. Royal→Ashen Capital). The `|` separates the two state tags.
- **Suffix form without slash** (`LG(TCM)`, `WP(CBC)`) — region code immediately followed by a
  parenthesised landmark (Third Church of Marika; Callu Baptismal Church) instead of `REGION/SUB`.
- **`BS:` and `Cross:`** — `BS` = Bestial Sanctum (a landmark, filed under Dragonbarrow);
  `Cross:` is the DLC *Message from Leda* questline series, found at roadside crosses — not a region.
