# Player Guide — *D20 Overhaul*

Welcome to the English player documentation for **D20 Overhaul**, the rebalancing mod for **Star Wars: Knights of the Old Republic II — The Sith Lords**.

This guide is written specifically for **regular KotOR 2 players**: it contains zero programming jargon or technical clutter. It walks you **point by point** through every change introduced by the mod so you can plan your builds, pick your gear, and adapt your combat tactics.

> **Author's note:** I developed **D20 Overhaul** solo, so all feedback is warmly appreciated to help keep improving it. The entire project is publicly available on my GitHub ([github.com/Tyraen1er/Kotor-2--Remastered-Tyr](https://github.com/Tyraen1er/Kotor-2--Remastered-Tyr)): anyone is welcome to use my work (for non-commercial purposes), fork it, or submit Pull Requests (PRs).

---

## Why This Mod? (Design Philosophy)

**D20 Overhaul** addresses **two core issues** in the vanilla game:
1. **Absurd damage spikes that let certain builds one-shot bosses**: between unchecked workbench stacking and a handful of broken synergies, optimized builds melt major bosses in 1 or 2 rounds, removing all tension from the game's biggest fights.
2. **A severe lack of build diversity**: Jedi robes, lightsabers, and a few dominant powers (*Force Storm*, *Insanity*, *Master Speed*) overshadow every alternative. Armor, ranged weapons, non-lightsaber melee weapons, and several attributes quickly fall behind — made worse by the fact that half of all organic enemies have no defensive profile at all, so the exact same tactic works from Peragus to Malachor V.

**The goal of D20 Overhaul** is to restore **tense, tactical combat** while making **every playstyle viable, distinct, and rewarding** from level 1 to level 30:
- **Clearly defined class identities** (martial specialist, tactical hybrid, Force master).
- **Meaningful, specialized armor** (evasion in light, shields & tech in medium, pure tanking in heavy).
- **8 weapon families** and **4 combat stances** that feel genuinely different in both melee and ranged combat.
- **6 mutually exclusive attribute specializations** that reward creative builds.
- **Tense boss fights** (5 to 10 rounds) and **distinct enemy families** that reward tactical adaptation.

---

## Quick Glossary

- **VP / FP**: Vitality Points (HP) / Force Points.
- **AC / Defense**: Armor Class (higher means enemies miss you more often).
- **Atk / Dmg**: Attack bonus (chance to hit) / Damage bonus.
- **DR**: Damage Reduction (e.g., `DR 4/-` subtracts 4 damage from every hit you take).
- **DC**: Difficulty Class of a saving throw (the target number `1d20 + save` must beat to resist an effect).
- **Fort / Ref / Will**: The three saving throws — *Fortitude*, *Reflex*, and *Will*.
- **Dice notation (`1d8`, `2d6`, etc.)**: Replaces vanilla ranges (`1-8`, `2-12`). `2d6` means rolling two 6-sided dice (2 to 12, average 7).
- **STR / DEX / CON / INT / WIS / CHA**: Strength, Dexterity, Constitution, Intelligence, Wisdom, Charisma.
- **1H / 2H / D**: One-Handed / Two-Handed / Double-Bladed or Repeating weapon.
- **T1 / T2 / T3**: Tier (rank) 1, 2, or 3 of a feat or Force power.
- **AoE**: Area of Effect power or attack (hits multiple enemies at once).

---

## Quick Summary of Major Changes

| Area | Vanilla Game | With D20 Overhaul |
| :--- | :--- | :--- |
| **Classes (Lvl 30)** | Martial classes get nearly as many powers as Consulars | Clear inverse symmetry: **22 feats / 12 powers** (Guardian), **18 / 16** (Sentinel), **15 / 24** (Consular) |
| **Combat Styles** | *Dueling* and *Two-Weapon Fighting* dominate everything | Old feats replaced by **4 stances** (*Dueling*, *Ambidexterity*, *Heavy Weapon*, *High-Rate Weapon*) |
| **Weapon Specializations** | Flat +1 Attack / +2 Damage | **8 families** with unique tactical effects (Knockdown, Armor Break, Rattle, Stun…) |
| **Ranged Weapons** | DEX adds zero damage | **DEX adds to ranged damage** (just like STR in melee) |
| **Attributes** | Few ways to leverage CON, INT, or CHA in combat | **6 mutually exclusive trees** (one per attribute) for unique archetypes |
| **Armor** | Rarely worth wearing for a Jedi | **Native DR** (Medium 2 / Heavy 4), **3 feat trees**, combined upgrades exclusive to Medium armor |
| **Force Powers** | Flat FP costs; *Force Storm* & *Insanity* overpower everything | Scaling FP costs by tier, rebalanced powers, **Force Awakening**, **6 overhauled prestige powers** |
| **Workbench & Upgrades** | Massive flat damage stacking by mid-game | **Only 1 flat damage slot** per weapon, character-level crafting gates, all base non-saber weapons craftable |
| **Stealth** | Low payoff outside Sneak Attack | First attack from stealth is a **confirmed critical hit** |
| **Enemies & Bosses** | Few defenses; bosses melt in 2 rounds | **6 enemy families** with distinct defenses; **5–10 round** boss fights |

---

## Modified Core Rules (Active from Level 1, Without Feats)

Even before picking a single feat or Force power, **D20 Overhaul** changes several foundational combat and equipment rules compared to vanilla KotOR 2:

- **New Two-Handed Weapons (`2H`)**: heavy melee weapons (*Vibrosword*, *Gamorrean Battleaxe*, *Force Pike*) and rifles/bowcasters now occupy both hands with no extra off-hand attack, dealing **`200% STR`** in melee and **`150% DEX`** at range by default.
- **Ranged Weapons Scale with Dexterity (`DEX`)**: unlike vanilla where DEX added zero damage to blasters, ranged attacks now add your DEX modifier to damage (**`150% DEX`** with a single 1H pistol or 2H rifle, **`100% / 50% DEX`** dual-wielding, **`150% / 50% DEX`** with repeating blasters).
- **Double-Bladed & Repeating Weapons: AC Penalty Instead of Attack Penalty**: all double weapons and repeating blasters are now balanced and no longer suffer the vanilla `-6 / -10` two-weapon attack penalty. Instead, they carry a **native `-5 AC` penalty** and deal **`150% / 50%`** STR (melee) or DEX (ranged).
- **Guaranteed Confirmed Critical from Stealth**: your **first attack** made within **6 seconds** of leaving stealth receives **`+50` Attack** (guaranteeing a hit) and **duplicates its entire damage roll (including Sneak Attack dice)** to simulate a confirmed critical hit. In game, this bonus damage appears on a **second damage line** in the combat log right after the initial hit.
- **Unarmed Counts as One-Handed**: fighting unarmed natively follows single 1H weapon rules (`150% STR` in melee and full compatibility with the *Dueling* stance).
- **Native Armor Damage Reduction (DR)**: wearing **Medium armor** natively grants **`DR 2/-`** and **Heavy armor** grants **`DR 4/-`** (physical & energy). Each armor category also has its own workbench slot rules (1 Overlay for Light, 2 exclusive combined slots for Medium, 1 Underlay for Heavy).
- **Scaling DCs for Grenades, Rockets & Weapon On-Hit Effects**: no more obsolete flat DCs — grenades use **`10 + Level + INT Mod`**, darts/rockets use **`12 + Level + INT Mod`**, and weapon on-hit effects use **`3 / 5 / 7 / 9 + Level + Weapon Attribute Mod`**.
- **Strict Workbench Slot Roles & Level Gates**: only one slot per weapon adds regular flat damage, all base non-lightsaber weapons are craftable from Level 1, and upgrades unlock by character level (`Mk I: Lvl 1`, `Mk II: Lvl 10`, `Mk III: Lvl 15/18`, `Mk IV / Mk V: Lvl 20`).
- **Scaling FP Costs & Uncapped Tier 3 Powers**: Force Point costs now rise with each tier (`T1 < T2 < T3`), and Tier 3 powers scale without dice caps all the way to Level 30.
- **Dice Notation (`1d8`, `2d6`, etc.)**: all in-game descriptions replace vanilla ranges (`1-8`, `2-12`) with standard dice notation.

---
