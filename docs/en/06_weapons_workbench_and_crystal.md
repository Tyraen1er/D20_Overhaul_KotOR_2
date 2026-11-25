# 6. Weapons, Upgrades, Workbench & The Exile's Crystal

[← Previous: Feat Access & Companions](05_feat_access_and_companions.md) | [Introduction](README.md) | [Next: Combat & Enemies →](07_combat_and_enemies.md)

---

## New General Wielding Rules

1. **Ranged weapons now add your Dexterity (DEX) to damage!**
   - In vanilla KotOR 2, DEX added zero damage to blasters.
   - In **D20 Overhaul**, ranged weapons scale with DEX: **`150% DEX`** with a single one-handed pistol (Dueling) or a two-handed rifle, **`100% / 50% DEX`** when dual-wielding (Ambidexterity), and **`150% / 50% DEX`** on repeating blasters. *(Or **INT** with **Gand Findsman II**).*
2. **New Category: Two-Handed Weapons (2H)**
   - Heavy weapons (e.g., *Vibrosword*, *Gamorrean Battleaxe*, *Force Pike*, *Blaster Rifles*, *Bowcaster*, *Disruptor Rifle*…) are now true Two-Handed weapons: no extra off-hand attack, but base damage scales at **`200% STR`** in melee or **`150% DEX`** at range (up to `250% STR` / `200% DEX` with *Heavy Weapon Handling*).
3. **High-Rate Weapons (`HR` — Double-Bladed Weapons & Repeating Blasters)**
   - All double-bladed weapons and repeating blasters are now **balanced** and no longer suffer the vanilla `-6/-10` two-weapon attack penalty. Instead, they carry a **native `-5 AC` penalty**, reducible down to `-1 AC` via *High-Rate Weapon Handling*.

---

## Weapon Catalog (Melee, Lightsabers & Ranged)

> **Family Balance Principle:** Weapon families with **fewer upgrade slots** (1 or 2 instead of 3) compensate with **higher base damage dice**, **wider critical threat ranges**, or **`×3` critical multipliers**. Flat damage bonuses on named/loot weapons are capped by tier (**`+2`** in T1–14, **`+1d4` / `+3`** in T15–22, **`+1d6` / `+4`** in T23–30) while preserving their unique effects, and the **6 endgame legendary relics** (*Arg'garok*, *Freyyr's Warblade*, *Geonosian Electro-Staff*, *Freedon Nadd's Blaster*, *Zabrak Heavy Blaster*, *Onderon Repeating Carbine*) remain non-upgradeable at the workbench with bonuses capped at **`+1d8` / `+1d10`**.

### Melee Weapons & Lightsabers

| Weapon | Family | Wielding | Damage | Critical | Upgrade Slots |
| :--- | :--- | :---: | :--- | :---: | :--- |
| **Unarmed** | Impact | 1H | Physical `1d6` *(+Unarmed Specialist I–III: `+1d4/+2d4/+3d4` at Lvl 4/12/19 or Prestige 4)* | `19-20, ×2` | None *(counts as 1H for Dueling)* |
| **Stun Baton** | Impact | 1H *(bal.)* | Bludgeoning `1d8` | `18-20, ×2` | Grip |
| **Plasma Torch** | Impact | 1H *(bal.)* | Bludgeoning `1d1` + Fire `1d6` *(vanilla damage)* | `20, ×2` | None *(Peragus tool)* |
| **Quarterstaff** | Impact | **HR** *(bal.)* | Bludgeoning `1d8` | `19-20, ×2` | Grip |
| **Force Pike** | Impact | **2H** | Bludgeoning `2d8` | `20, ×3` | Grip |
| **Short Sword** | Traditional | 1H *(bal.)* | Piercing `1d8` | `18-20, ×2` | Grip, Edge |
| **Long Sword** | Traditional | 1H | Slashing `1d12` | `19-20, ×2` | Grip, Edge |
| **Double-Bladed Sword** | Traditional | **HR** *(bal.)* | Slashing `1d8` | `19-20, ×2` | Grip, Edge |
| **Gamorrean Battleaxe** | Traditional | **2H** | Slashing `2d8` | `20, ×3` | Grip, Edge |
| **Wookiee Warblade** | Traditional | **HR** *(bal.)* | Slashing `1d10` | `20, ×3` | Grip, Edge |
| **Vibroblade** | Resonance | 1H *(bal.)* | Piercing `1d6` | `19-20, ×2` | Grip, Edge, Power Cell |
| **Vibrosword** | Resonance | **2H** | Slashing `1d10` | `19-20, ×2` | Grip, Edge, Power Cell |
| **Double-Bladed Vibrosword** | Resonance | **HR** *(bal.)* | Slashing `1d8` | `20, ×2` | Grip, Edge, Power Cell |
| **Short Lightsaber** | Laser | 1H *(bal.)* | Energy `2d6` | `19-20, ×2` | Color, 2 Crystals, Emitter, Lens, Cell |
| **Lightsaber** | Laser | 1H | Energy `2d8` | `19-20, ×2` | Color, 2 Crystals, Emitter, Lens, Cell |
| **Double-Bladed Lightsaber** | Laser | **HR** *(bal.)* | Energy `2d8` | `20, ×2` | Color, 2 Crystals, Emitter, Lens, Cell |

### Ranged Weapons

| Weapon | Family | Wielding | Range | Damage | Critical | Special | Upgrade Slots |
| :--- | :--- | :---: | :---: | :--- | :---: | :--- | :--- |
| **Blaster Pistol** | Assault Fire | 1H *(bal.)* | 23 m | Energy `1d10` | `19-20, ×2` | — | Scope, Power Pack |
| **Blaster Carbine** | Assault Fire | **2H** | 25 m | Energy `1d12` | `19-20, ×2` | — | Scope, Power Pack |
| **Repeating Blaster** | Assault Fire | **HR** *(bal.)* | 28 m | Energy `2d6` | `20, ×2` | — | Scope, Power Pack |
| **Heavy Blaster** | Penetrating Fire | 1H | 23 m | Energy `1d12` | `19-20, ×2` | — | Scope, Power Pack, Firing Chamber |
| **Blaster Rifle** | Penetrating Fire | **2H** | 28 m | Energy `1d12` | `19-20, ×2` | — | Scope, Power Pack, Firing Chamber |
| **Bowcaster** | Penetrating Fire | **2H** | 28 m | Energy `1d10` | `20, ×3` | — | Scope, Power Pack, Firing Chamber |
| **Heavy Repeating Blaster** | Penetrating Fire | **HR** *(bal.)* | 28 m | Energy `2d6` | `20, ×2` | — | Scope, Power Pack, Firing Chamber |
| **Hold-Out Blaster** | Assassin Fire | 1H *(bal.)* | 23 m | Energy `1d6` | `19-20, ×2` | Massive Crit `+1d8` | Scope, Power Pack |
| **Disruptor Pistol** | Assassin Fire | 1H | 23 m | Unstoppable `1d10` | `18-20, ×2` | Ignores DR | Scope, Power Pack |
| **Disruptor Rifle** | Assassin Fire | **2H** | 28 m | Unstoppable `1d12` | `18-20, ×3` | Ignores DR | Scope, Power Pack |
| **Ion Blaster** | Tactical Fire | 1H *(bal.)* | 17 m | Ion `1d10` | `19-20, ×3` | `+1d10` vs Droids | Scope |
| **Ion Rifle** | Tactical Fire | **2H** | 28 m | Ion `2d6` | `19-20, ×3` | `+1d10` vs Droids | Scope |
| **Sonic Pistol** | Tactical Fire | 1H *(bal.)* | 17 m | Sonic `1d10` | `18-20, ×2` | On-Hit `-DEX` *(scaling DC)* | Scope |
| **Sonic Rifle** | Tactical Fire | **2H** | 28 m | Sonic `2d6` | `18-20, ×2` | On-Hit `-DEX` *(scaling DC)* | Scope |

---

## Grenades, Rockets & Weapon On-Hit Effects: Scaling DCs!

In vanilla, grenades and weapon status effects had fixed DCs (such as DC 15) that became useless after the first two planets. Every DC now **scales with your level**:
- **All Grenades** *(Frag, Concussion, Thermal Detonator, Poison, Flash, Plasma, CryoBan, Sonic, Ion)*: **`DC = 10 + Level + INT Mod`** *(Adhesive grenades remain no-save)*.
- **Specialized Darts & Rockets** *(Mira/Mandalore wrist launcher)*: **`DC = 12 + Level + INT Mod`**.
- **Weapon & Upgrade On-Hit Effects** *(Stun, Slow, Horror, Paralysis, Sonic…)*: instead of fixed vanilla DCs `10 / 14 / 18 / 22`, they now scale as **`3 / 5 / 7 / 9 + Level + Weapon Attribute Mod`** *(STR/DEX in melee, DEX/INT at range)*.

---

## Upgrade Overhaul: Strict Roles per Slot

In vanilla, stacking flat damage bonuses across every upgrade slot broke combat pacing. Now, **only one slot per weapon category adds regular flat damage**, and total upgrade damage is capped by game phase (**max `+2` avg damage Early, `+5` Mid, `+10` Late**).

| Category | Upgrade Slot | Strict Role in D20 Overhaul |
| :--- | :--- | :--- |
| **Melee** | **Grip** | `+Attack`, `+AC`, or `+Saves` *(zero flat damage)* |
| **Melee** | **Edge** | `Keen` (doubles crit threat), `Massive Criticals`, **On-Hit effects** (Slow, Stun, Paralysis), `vs Droids` *(zero regular damage)* |
| **Melee** | **Power Cell** *(melee — Resonance only)* | **Only slot for regular flat damage in melee** (Slashing, Energy, Ion, Sonic) |
| **Ranged** | **Scope** | `+Attack`, `Keen`, **On-Hit effects** (Stun, Slow) *(zero flat damage)* |
| **Ranged** | **Power Pack / Energy Cell** *(ranged — except Tactical Fire)* | `Massive Criticals`, `Ion / vs Droids`, or light flat energy (`+1` to `+3` max) |
| **Ranged** | **Firing Chamber** *(Penetrating only)* | **Only slot for heavy flat damage** (up to `+5` / `+1d6`) & accuracy |
| **Lightsaber** | **Emitter** | `+AC`, `Blaster Bolt Deflection`, **On-Hit effects** (Stun, Horror) *(zero flat damage)* |
| **Lightsaber** | **Lens** | `+Attack`, `Keen`, `Massive Criticals`, `Deflection` *(zero regular damage)* |
| **Lightsaber** | **Energy Cell** *(saber)* | **Only slot for regular flat damage** on lightsabers (Energy, Electrical, Ion) |
| **Lightsaber** | **Upgrade Crystals (×2)** | `+Attributes`, `VP/FP Regen`, `+Attack`, `+AC`, `Deflection`, `Keen`, `vs Alignment / Droids`, On-Hit effects *(zero generic flat damage)* |

> **Sample rebalanced lightsaber crystals:** *Adegan* (`+1 Atk`), *Rubat* (`+1 Atk, +1 AC`), *Phond* (`+1 STR, +1 Atk`), *Bondar* (scaling Stun), *Opila* (`Keen, +1 Atk`), *Ultima-Pearl* (`+3 Atk, +2 Saves`), *Solari* (Light Side: `+2 Atk, +1d8 vs Dark Side`), *Barab Ore Ingot* (`+2 STR, Fire DR +10/-`), *Kaiburr* (`+2 CON, +2 WIS, Regen +3`), *Qixoni* (Dark Side: `+2 CHA, FP Regen +2`), *Hurrikaine* (`+2 Atk`, Stun DC `7 + Lvl + Attr`).

---

## Workbench & Lab Crafting Changes

1. **Every base non-lightsaber weapon is craftable from Level 1!**
   - 18 new recipes were added to the workbench (*Repair* thresholds 2–8): *Short Sword*, *Stun Baton*, *Quarterstaff*, *Vibroblade*, *Double-Bladed Sword*, *Gamorrean Battleaxe*, *Force Pike*, *Wookiee Warblade*, *Blaster Pistol*, *Ion Blaster*, *Sonic Pistol*, *Disruptor Pistol*, *Heavy Blaster*, *Blaster Carbine*, *Ion Rifle*, *Sonic Rifle*, *Bowcaster*, and *Heavy Repeating Blaster*.
   - You never have to wait on random loot drops to play your preferred weapon family!
2. **60 Reworked Armor Upgrades at the Workbench**
   - **30 Underlays** (*6 lines, T1→T5*): 15 common underlays available from Light Armor onward (*Environmental*, *Biorestorative*, *Strengthening*) and 15 armored underlays for Heavy & Medium Armor (*Reinforcing*, *Flexible*, *Durasteel*).
   - **30 Reinforced Overlays Exclusive to Medium Armor** (*8 lines, T1→T4*) combining cross-immunities, saving throws, stealth, crowd-control immunities, and defensive reinforcements.
3. **Character-Level Crafting Gates**
   - To prevent crafting endgame upgrades on the very first planet, workbench upgrade, shield, and rocket recipes now unlock progressively by **character level**:
     - **Mk I**: **Level 1**
     - **Mk II**: **Level 10**
     - **Mk III**: **Level 15** *(or **Level 18** on 3-tier lines)*
     - **Mk IV / Mk V**: **Level 20**

---

## Complete Overhaul of the Exile's Personal Crystal

The Exile's personal crystal (found in the Dantooine Crystal Cave) has been redesigned as a **build centerpiece** reflecting both your attributes and your class journey.

### 1. Attribute Bonuses (3 Scaling Tiers)
- No more generic flat damage, random on-hit effects, or flat save bonuses.
- Instead, the crystal boosts your attributes across **3 level tiers**:
  - **Levels 1–14:** **`+2`** to your 1st stat / **`+1`** to your 2nd stat / `0` to the other 4.
  - **Levels 15–21:** **`+4`** to your 1st stat / **`+2`** to your 2nd stat / **`+1`** to the other 4.
  - **Levels 22+:** **`+6`** to your 1st stat / **`+4`** to your 2nd stat / **`+2`** to the other 4.
- **Customizable at any time:** by default, the crystal automatically matches your **2 highest base attributes**, and you can **freely customize your stat pair** by speaking with **Kreia**!

### 2. Unique Class Effects (Up to 2 Stacking Effects)
While the personal crystal is installed in your wielded lightsaber, you gain one bonus from your **base Jedi class** AND a second bonus from your **prestige class**:

| Base Class | Bonus Granted by the Crystal |
| :--- | :--- |
| **Jedi Guardian** | **`+1 VP` per level** and **`+1` Attack** |
| **Jedi Sentinel** | **`+1` Attack**, **`+1` Defense (AC)**, and **`+1` to all saving throws** |
| **Jedi Consular** | **Force Point cost** of all powers reduced by **`-10%`** |

| Prestige Class | Bonus Granted by the Crystal |
| :--- | :--- |
| **Jedi Weapon Master** | On hit: **`+1` Attack & `+1` AC** for 2 rounds *(stacks up to `+5`)* |
| **Sith Marauder** | On hit: heals you for **`+1%` of your max VP** |
| **Jedi Watchman** | **`+3` to all skills** *(synergizes with the class passive)* |
| **Sith Assassin** | **Massive Criticals `+2d6`** and **`+1` critical threat range** |
| **Jedi Master** | **`+2` Force Power DC** and **buff duration `+25%`** |
| **Sith Lord** | **`+2` Force Power DC** and **FP Regeneration `+3`** |

---

[← Previous: Feat Access & Companions](05_feat_access_and_companions.md) | [Introduction](README.md) | [Next: Combat & Enemies →](07_combat_and_enemies.md)
