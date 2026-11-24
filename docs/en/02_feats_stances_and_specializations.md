# 2. Feats: Stances, Weapon Specializations, Attributes & Force Awakening

[← Previous: Classes & Progression](01_classes_and_progression.md) | [Table of Contents](README.md) | [Next: Armor & Defenses →](03_armor_and_defenses.md)

---

## Removed Vanilla Feats

To make room for the new system and remove redundant or outdated feats, the following vanilla feats have been **removed** from selection:
- **Dueling I, II, and III** *(replaced by the new **Dueling** stance)*
- **Two-Weapon Fighting I, II, and III** and **Superior Two-Weapon Fighting I, II, and III** *(replaced by **Ambidexterity** and **High-Rate Weapon Handling**)*
- **Finesse: Melee Weapons** and **Finesse: Lightsabers** *(replaced by the **Echani Techniques** DEX tree)*
- **Weapon Focus**, **Superior Weapon Focus**, and **Weapon Specialization** *(blaster pistols, rifles, melee, lightsabers — replaced by the **8 Weapon Specialization families**)*

> Classic active attack feats (*Flurry*, *Power Attack*, *Critical Strike*, *Rapid Shot*, *Power Blast*, *Sniper Shot*, *Dual Strike*, *Precise Shot*, *Close Combat*), *Toughness I–III*, *Conditioning I–III*, skill feats, and unique companion feats are **kept**.

---

## The 4 Combat Stances

Each stance has **3 tiers** (available at **Levels 1, 4, and 8**) and enhances how you wield your weapons **in both melee and ranged combat**.

| Stance | Eligible Weapons | Base Rule *(without feats)* | Tier I (Lvl 1+) | Tier II (Lvl 4+) | Tier III (Lvl 8+) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Dueling** | 1 one-handed weapon *(off-hand empty)* **or unarmed** | Damage: **150% STR** (melee) or **150% DEX** (ranged) | `+2` Attack<br>Crit threat **+1** | `+4` Attack<br>Crit threat **+2** | `+6` Attack<br>Crit threat **+3** *(all classes)* |
| **Ambidexterity** | 2 weapons *(one in each hand)* | Damage: **100% / 50%** STR (melee) or DEX (ranged)<br>Attack penalty `-6 / -10` *(or `-4 / -10` with balanced off-hand)* | Penalty reduced to **`-6 / -6`**<br>**+1 AC** | Penalty reduced to **`-4 / -4`**<br>**+2 AC** | Penalty reduced to **`-2 / -2`**<br>**+3 AC** *(except Force classes)* |
| **Heavy Weapon Handling** | **Two-handed** non-double weapon *(melee or ranged)* | Damage: **200% STR** (melee) or **150% DEX** (ranged) | `+1` Attack<br>Melee **215% STR**<br>Ranged **165% DEX** | `+2` Attack<br>Melee **235% STR**<br>Ranged **185% DEX** | `+3` Attack<br>Melee **250% STR**<br>Ranged **200% DEX** *(except Force classes)* |
| **High-Rate Weapon Handling** | **Double-bladed** melee weapons & **repeating blasters** | Damage: **150% / 50%** STR (melee) or DEX (ranged)<br>All balanced; native **`-5 AC`** penalty *(no two-weapon attack penalty)* | Damage **`+1 / +1`**<br>AC penalty **`-3`** | Damage **`+2 / +2`**<br>AC penalty **`-2`** | Damage **`+3 / +3`**<br>AC penalty **`-1`** *(except Force classes)* |

> **Tactical note:**
> - **Dueling** focuses on high accuracy and frequent critical hits.
> - **Ambidexterity** turns dual-wielding into a defensive parrying style that boosts your AC.
> - **Heavy Weapon Handling** delivers the hardest single hits in the game (ideal for punching through boss DR).
> - **High-Rate Weapon Handling** trades a bit of Defense for relentless attack volume.

---

## The 8 Weapon Specialization Families

Every weapon in the game now belongs to one of **8 families** (4 melee, 4 ranged). Each family has a **3-tier tree** (Levels 1, 8, and 15):
- **Tier I** *(all families)*: **`+2` Attack and `+2` Damage** with weapons in that family.
- **Tiers II & III**: a **signature tactical effect** unique to the family!

> **How Specialization Saving Throws Work:**
> - The **DC** scales with your character: **`10 + Level + Weapon Attribute Modifier`** when the effect triggers based on critical threat range (`threat range / 20` per hit), or **`5 + Level + Weapon Attribute Modifier`** when it triggers on every hit.

### Melee Families

| Family | Included Weapons | Tier II (Lvl 8+) | Tier III (Lvl 15+) |
| :--- | :--- | :--- | :--- |
| **Impact Weapons** | Unarmed, Stun baton, Quarterstaff, Force pike | **Knockdown** (1 round) — *Fort negates (DC 10 + Lvl + Attr; chance = threat range / 20 per hit)* | Knockdown extended to **2 rounds** |
| **Traditional Weapons** | Short sword, Long sword, Double-bladed sword, Gamorrean battleaxe, Wookiee warblade | **Armor Break**: `-3 AC` for 2 rounds — *Fort negates (DC 5 + Lvl + Attr, on every hit)* | Armor Break **stacks** and lasts **+1 round** |
| **Resonance Weapons** | Vibroblade, Vibrosword, Double-bladed vibrosword | **Rattle**: `-4` Attack & `-4` Damage for 1 round — *Ref negates (DC 5 + Lvl + Attr, on every hit)* | **Stacks**: `-2` per trigger (up to **`-8`**), refreshes duration |
| **Laser Weapons** | Short lightsaber, Lightsaber, Double-bladed lightsaber | **Will Break**: `-4` to all saving throws for 2 rounds — *Will negates (DC 5 + Lvl + Attr, on every hit)* | Will Break applies **with no saving throw** |

### Ranged Families

| Family | Included Weapons | Tier II (Lvl 8+) | Tier III (Lvl 15+) |
| :--- | :--- | :--- | :--- |
| **Assault Fire** | Blaster pistol, Blaster carbine, Repeating blaster | **No melee range penalty** (shoot point-blank safely) | **`+1` attack per round** with main hand |
| **Penetrating Fire** | Heavy blaster, Blaster rifle, Bowcaster, Heavy repeating blaster | **Knockback 3 m** — *Fort negates (DC 5 + Lvl + Attr; rolled per hit, max 1 knockback per round)* | **`+5` flat Damage** per shot |
| **Tactical Fire** | Ion blaster, Ion rifle, Sonic pistol, Sonic rifle | **Stun** (1 round; also stuns droids) — *Fort negates (DC 10 + Lvl + Attr; chance = threat range / 20)* | Stun extended to **2 rounds** |
| **Assassin Fire** | Hold-out blaster, Disruptor pistol, Disruptor rifle | **Sneak Attack `+2d6`** *(grants Sneak Attack even if your class doesn't have it)* | **Critical multiplier `+1`** *(e.g., ×2 → ×3, ×3 → ×4)* |

> **What about Unarmed Combat?**
> Unarmed strikes belong to the **Impact Weapons** family (gaining access to *Impact Weapon Specialization I–III* and Knockdown). Unarmed builds also use the **Dueling** stance (fists count as 1H), the automatic **Unarmed Specialist I–VIII** progression, unarmed gloves, and optionally the **Matukai Mastery** attribute tree.

---

## The 6 Attribute Specializations (Mutually Exclusive)

The mod adds **6 specialization trees** — one for each attribute (**STR, DEX, CON, INT, WIS, CHA**).
- **Open to all classes** at **Levels 1, 8, and 15**.
- **Mutually exclusive:** once you pick Tier I of one tree, **the other five trees are locked out** for the rest of your playthrough.

| Tree (Attribute) | Tier I (Lvl 1+) | Tier II (Lvl 8+) | Tier III (Lvl 15+) |
| :--- | :--- | :--- | :--- |
| **Gamorrean Refinement** *(STR)* | **+1 STR**<br>Adds **1/2 STR mod** as bonus ranks to **all skills** | **+2 STR**<br>Can **wield any weapon one-handed** *(including 2H and double weapons, melee & ranged; permanently locks out Heavy Weapon and High-Rate Weapon stances)* | **+3 STR**<br>**Immunity to Mind-Affecting effects** |
| **Echani Techniques** *(DEX)* | **+1 DEX**<br>Uses **DEX instead of STR** for **melee attack rolls** *(if DEX > STR)* | **+2 DEX**<br>Uses **DEX instead of STR** for **melee damage** *(if DEX > STR)* | **+3 DEX**<br>**Removes the Max DEX cap on all armor** |
| **Way of the Krayt Dragon** *(CON)* | **+1 CON**<br>**DR `+ 1/2 CON mod`** *(rounded up)* | **+2 CON**<br>**Transfusion**: every 6 s, converts **5% max VP into 5% max FP** if FP < 50% *(stops if VP drops to 75%)* | **+3 CON**<br>Adds **CON mod to all saving throws** |
| **Gand Findsman** *(INT)* | **+1 INT**<br>**Grenades and mines deal `+5%` damage per total Demolitions rank** | **+2 INT**<br>Uses **INT instead of DEX** for **ranged attack & damage** *(if INT > DEX)* | **+3 INT**<br>**Master Sapper**: grenade radius **4 m → 6 m**, pierces *Total Evasion* (min half damage), **50% chance** not to consume the grenade |
| **Matukai Mastery** *(WIS)* | **+1 WIS**<br>**Adds** WIS mod to **attack rolls** *(on top of your primary weapon attribute)* | **+2 WIS**<br>Saves **`+ 1/2 WIS mod`**; **succeeding on a saving throw** deals your WIS mod as direct damage to the attacker | **+3 WIS**<br>**WIS replaces DEX for AC**; any enemy that **misses you** takes your WIS mod as direct damage |
| **Legacy of Nomi** *(CHA)* | **+1 CHA**<br>**Companions earn 100% XP** | **+2 CHA**<br>**Entire party** gains **`+ CHA mod`** to all saving throws | **+3 CHA**<br>**Defense (AC) `+ CHA mod`** |

---

## Force Awakening & Total Evasion

### Force Awakening (7 New Feats for Force Users)
Designed to give Consulars, Jedi Masters, and Sith Lords meaningful feat investments that directly supercharge their Force powers:

| Feat | Tiers | Access | Effect |
| :--- | :---: | :--- | :--- |
| **Empower Power** | 3 | T1: All Jedi/Sith (Lvl 1+)<br>T2: Consular / Jedi Master / Sith Lord (Lvl 8+)<br>T3: Jedi Master / Sith Lord / Kreia (Lvl 15+) | Increases **offensive Force power damage** by **`+15% / +30% / +50%`** *(extra cost: `+2 / +4 / +6 FP`)* |
| **Penetrate Power** | 3 | Same access as *Empower Power* | Adds **`+2 / +4 / +6` to the DC** of offensive and control Force powers |
| **Extend Power** | 1 | All Jedi/Sith (Lvl 1+) | **Doubles the duration (`×2`)** of all Force buffs |

### Total Evasion (Overhaul of *Evasion*)
- **Vanilla:** exclusive to Mira (Scout Lvl 6); a successful Reflex save vs. an AoE dealt 0 damage, but a failed save dealt full (100%) damage.
- **D20 Overhaul:**
  - **Successful** Reflex save against an AoE (grenade, *Force Storm*, *Force Wave*…): **0 damage**.
  - **Failed** Reflex save: **half damage only**.
- **Who gets it?**
  - Free for **Mira** at Scout Level 6.
  - Selectable at Level 15+ by **Jedi Watchman**, **Sith Assassin**, and **Visas Marr**.
  - Watch out: **enemy Jedi and Sith at Level 20+** also have this feat!

---

[← Previous: Classes & Progression](01_classes_and_progression.md) | [Table of Contents](README.md) | [Next: Armor & Defenses →](03_armor_and_defenses.md)
