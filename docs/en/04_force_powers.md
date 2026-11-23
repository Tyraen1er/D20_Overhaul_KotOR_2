# 4. Force Powers

[← Previous: Armor & Defenses](03_armor_and_defenses.md) | [Table of Contents](README.md) | [Next: Feat Access & Companions →](05_feat_access_and_companions.md)

---

## Force Rebalancing Philosophy

1. **No new standard selectable powers**: every existing selectable power has been tuned, while the **6 Prestige Class powers** have been completely overhauled (including 2 brand-new powers) so each prestige path has a unique signature.
2. **No dice caps at Tier III**: Tier III powers scale cleanly all the way to Level 30.
3. **Scaling Force Point (FP) costs**: in vanilla, higher tiers often cost the same (or less) than Tier I. Now each tier scales up (`T1: 10–20 FP`, `T2: 20–35 FP`, `T3: 35–65 FP`), making cross-alignment Tier III spam genuinely expensive.
4. **Power restored through Metamagic**: overpowered vanilla outliers (*Force Storm*, *Kill*, *Insanity*…) have been toned down at baseline; Consulars, Jedi Masters, and Sith Lords can reclaim devastating output through **Metamagic** (*Empower*, *Penetrate*, *Extend*).
5. **Clear armor restrictions**: every power clearly indicates the heaviest armor allowed (*Robes only*, *Light*, *Medium*, or *Heavy*).

---

## Light Side Powers

| Power | Max Armor | FP Cost (T1/T2/T3) | Changes from Vanilla |
| :--- | :---: | :---: | :--- |
| **Force Aura / Shield / Armor** | Robes only | `15 / 25 / 35` | Effects unchanged (`+2 / +4 / +6` Defense & saves, 20 s). FP cost updated. |
| **Force Barrier** *(I / II / III)* | **Medium Armor** | `15 / 25 / 35` | Physical DR adjusted to **`4 / 8 / 12`** (self only, **60 s** at all tiers) and now usable in **Medium armor**. |
| **Force / Knight / Master Valor** | **Light Armor** | `15 / 30 / 45` | Bonus adjusted to **`+2 / +3 / +4`** to all 6 attributes (party) + Poison immunity at T2/T3. Now usable in **Light armor**. |
| **Cure / Heal / Master Heal** | Medium Armor | `20 / 35 / 50` | Effects unchanged. FP cost updated. |
| **Revitalize** *(I / II / III)* | Medium Armor | `35 / 50 / 65` | **Buffed:** revives with **`10%`** VP (nearest ally at T1), **`20%`** VP (2 nearest at T2), **`30%`** VP (entire party at T3). |
| **Stun / Stasis / Stasis Field** | Robes only | `15 / 30 / 50` | **T3 (*Stasis Field*, 10 m radius):** max duration raised to **36 s** (6 rounds), with a Fortitude save each round at a **decaying DC (`-3` per round)** to break free *(if initial save succeeds: slowed 12 s)*. |
| **Stun / Disable / Destroy Droid** | Medium Armor | `10 / 20 / 35` | Effects unchanged. FP cost updated. |

---

## Universal (Neutral) Powers

| Power | Max Armor | FP Cost (T1/T2/T3) | Changes from Vanilla |
| :--- | :---: | :---: | :--- |
| **Affect Mind / Dominate Mind** | Heavy Armor | `0` | Unchanged (dialogue options). |
| **Battle Meditation** *(I / II / III)* | Medium Armor | `25 / 35 / 50` | **Scales with Charisma:**<br>• **T1:** party **`+ CHA mod`** (Atk, Dmg, Will + VP regen, uncapped).<br>• **T2:** adds **`- CHA mod`** penalty to enemies within 10 m *(Will negates)*.<br>• **T3:** **`+2`** extra to both bonus and penalty, radius **15 m** *(Will negates)*. |
| **Burst / Knight / Master Speed** | Robes only | `15 / 30 / 45` | Effects unchanged (`+2/+4/+4` AC and `0/+1/+2` attacks/round). FP cost updated. |
| **Energy Resistance** *(I / II / III)* | **Medium Armor** | `15 / 25 / 35` | Aligned with *Force Barrier*: **DR `4 / 8 / 12`** (energy, sonic, fire, cold, electrical), **self only**, **60 s**. No longer party-wide or Poison-immune. |
| **Force Body** *(I / II / III)* | Heavy Armor | `0` | **Buffed:** in addition to paying 50/40/30% of power costs with VP, adds **`+2 / +4 / +6` to the DC** of armor-compatible powers! |
| **Force Deflection / Redirection** | Heavy Armor | `0` | **Buffed:** in addition to deflecting/redirecting blaster fire unarmed, grants **`+2 / +4` Defense against ranged attacks**. |
| **Force Push / Whirlwind / Wave** | Medium Armor | `15 / 25 / 40` | • **T2 (*Whirlwind*, single target):** a successful Reflex save now still deals **half damage immediately** (`1 × Lvl`) instead of negating everything.<br>• **T3 (*Force Wave*):** transformed into an **AoE Whirlwind (6 m radius, 12 s)** dealing `1/3 Lvl` every 2 s *(total `2 × Lvl`; Reflex save = half immediate damage and not lifted)*. |
| **Force Resistance / Immunity** | Heavy Armor | `20 / 35` | Effects unchanged. FP cost updated. |
| **Force Suppression / Breach** | Light Armor | `20 / 35` | Effects unchanged. FP cost updated. |
| **Mind Trick / Force Confusion** | Medium Armor | `15 / 35` | Effects unchanged. FP cost updated. |
| **Throw Lightsaber / Advanced** | Heavy Armor | `15 / 30` | **Buffed:**<br>• **T1:** auto-hit, **`1d4 / Lvl`** + **Knockdown 1 round** *(Fort negates)*.<br>• **T2:** chains up to 3 targets, **`1d4 / Lvl`** + **ignores DR**. |

---

## Dark Side Powers

| Power | Max Armor | FP Cost (T1/T2/T3) | Changes from Vanilla |
| :--- | :---: | :---: | :--- |
| **Drain Force** *(I / II / III)* | Heavy Armor | `5 / 10 / 15` | **Buffed:** drains **`15 / 30 / 45 + Level` FP** and deals **half that amount as direct damage** to Force users. |
| **Drain Life / Death Field / Death Feast** | Robes only | `20 / 40 / 55` | • **T1 (Lvl 9, 1 target) & T2 (Lvl 15, 10 m):** **`1d3 / Lvl`** uncapped, 100% of damage heals you *(Fort half)*.<br>• **New T3 — *Death Feast* (Lvl 18, 10 m):** `1d3 / Lvl`, 100% lifesteal, and **any healing above your max VP becomes Temporary VP** for 24 s *(non-stacking, refreshed on recast; Fort half)*. |
| **Fear / Horror / Insanity** | Light Armor | `15 / 25 / 45` | **Reworked (no more full stun-lock):** deals **mental damage over time (`Level` dmg/round)** and a heavy Attack penalty (**`-4` T1 / `-6` T2 in 5 m / `-8` T3 in 10 m**) for **24 s** (4 rounds) on a failed Will save, or **6 s** (1 round) on a successful save. |
| **Force Scream** *(I / II / III)* | Light Armor | `15 / 25 / 40` | **Scaling damage:** **T1 `1d3 / Lvl`** (`-2` attrs), **T2 `1d4 / Lvl`** (`-4` attrs), **T3 `1d4 / Lvl`** uncapped (`-6` attrs). *Will save: half damage and negates attribute penalty.* |
| **Shock / Force Lightning / Force Storm** | Robes only | `15 / 30 / 50` | **`1d6 / Lvl`** uncapped at T3 *(target / cone / 10 m radius)*. **Removed enemy FP drain** from *Force Storm*. Saving throw changed from Will to **Reflex** *(half damage, countered by Total Evasion)*. |
| **Slow / Affliction / Plague** | Medium Armor | `15 / 25 / 35` | **Reworked into a contagious disease** *(no more unsaveable DC 100 Plague)*: lasts up to **42 s** (ticks every 6 s) and **spreads 5 m when the host dies**. Applies slow (`-50%` movement), **`½ Lvl` dmg per tick**, and **`-3 / -6 / -9`** to all 6 attributes. **Fortitude save** each tick to cure *(normal DC at T1, `+4` at T2, `+8` at T3)*. |
| **Wound / Choke / Kill** | Robes only | `15 / 30 / 45` | **Removed 50% max VP loss** on *Kill*.<br>• **T1:** `1d4 / Lvl` *(Fort half)*.<br>• **T2:** `1d6 / Lvl` + stun 6 s.<br>• **T3:** `1d8 / Lvl` uncapped + stun 6 s *(Fort half and negates stun)*. |

---

## The 6 Prestige Class Powers (Complete Overhaul)

All Prestige Class powers are now standardized to **3 tiers**, automatically granted at **Prestige Levels 1, 5, and 9**.

| Prestige Class | Power (Tiers I → III) | Max Armor | FP Cost | Effects |
| :--- | :--- | :---: | :---: | :--- |
| **Jedi Weapon Master** | **Force Scar** *(new)* | Heavy | `20 / 30 / 40` | **Active (30 s):** heals **`+2% / +4% / +6%` max VP per round**, **`+1 / +2 / +3`** to all saves, immunity to **Fear & Stun** (T2) and **Paralysis** (T3). |
| **Sith Marauder** | **Force Stigma** *(formerly Fury)* | Heavy | `20 / 30 / 40` | **Active (30 s):** **`+2 / +4 / +6` STR & DEX**, immunity to **Stasis & Paralysis**, **`+1` attack/round starting at T1** *(does not stack with Speed)*. Drains **`-5%` max VP per round** *(stops automatically at ≤ 25% VP)*. |
| **Jedi Watchman** | **Unbound from the Force** *(new)* | Heavy | Passive (`0`) | **Passive:** grants **`+1` per 8 combined ranks** across 4 skill pairs:<br>• *Computer Use + Security* → **Attack**<br>• *Demolitions + Repair* → **Damage**<br>• *Awareness + Stealth* → **AC**<br>• *Persuade + Treat Injury* → **Saves**<br>*(Cap per axis: `+3` T1 / `+5` T2 / `+7` T3)*.<br>**T2:** `+25%` effectiveness of mundane items (medpacs, grenades, mines, shields).<br>**T3:** Passive Force Resistance (`15 + Level`). |
| **Sith Assassin** | **Force Wraith** *(formerly Force Camouflage)* | Medium | Passive (`0`) | **Passive (Sith Assassin exclusive):**<br>• **T1:** **`+4` Stealth** + belt-free stealth + auto Stealth Run.<br>• **T2:** **`+8` Stealth** + stealth ambush deals **`+2d6` bonus damage & Stuns 1 round** *(Fort negates, DC 10 + Lvl + Attr)*.<br>• **T3:** **`+12` Stealth** + every kill makes your **next attack a confirmed critical** *(within 2 rounds)* and grants **`+25%` evasion** for 2 rounds. |
| **Jedi Master** | **Echo of Bonds** *(formerly Inspire Followers)* | Heavy | `25 / 35 / 45` | **Active:**<br>• **T1 (30 s):** shares your personal buffs with the nearest ally.<br>• **T2 (45 s):** shares your personal buffs with the **entire party**.<br>• **T3 (60 s):** shares personal buffs **and healing** (powers, medpacs, regen) with the entire party *(ignoring ally armor restrictions)*. |
| **Sith Lord** | **Force Rend** *(formerly Crush Opposition)* | Heavy | `25 / 35 / 45` | **Active (45 s, 15 m radius):** inflicts **`-2 / -4 / -6` Attack, Saves, and Defense (AC)** on all enemies in range *(Will negates)*. |

---

## Alignment Ultimates & Quest Powers

- **Force Enlightenment** *(Max Light Side — Medium Armor, `50 FP`)*: **instant cast** that activates *Speed*, *Force Armor*, and *Force Valor* at your highest known tier. Usable up to **Medium armor** *(while wearing armor, Speed is capped at `+1` attack/round; `+2` attacks/round in Robes only)*.
- **Force Crush** *(Max Dark Side — Light Armor, `60 FP`)*: **`1d8 / Level`** uncapped pure damage (ignores DR and elemental resistances) + immobilizes 6 s *(Fortitude: half damage and negates immobilization)*.
- **Breath Control** *(Nar Shaddaa quest — Heavy Armor, `15 FP`)*: gains a permanent **passive `+4` bonus to saves vs. Poison** in addition to its active 240 s immunity.
- **Battle Precognition** *(Handmaiden quest)*: replaced by **`+10%` melee evasion**.
- *Beast Trick / Confusion*, *Force Sight*, and *Precognition*: unchanged.

---

[← Previous: Armor & Defenses](03_armor_and_defenses.md) | [Table of Contents](README.md) | [Next: Feat Access & Companions →](05_feat_access_and_companions.md)
