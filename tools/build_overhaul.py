#!/usr/bin/env python3
"""KotOR 2 Overhaul — Jalon 1 : Générateur des tables .2da + dialog.tlk.

Génère dans `mods/overhaul/` (sans jamais modifier le jeu directement) :
  - `dialog.tlk` (copie du backup FR + entrées ajoutées pour dons & pouvoirs)
  - `Override/feat.2da` (245 lignes TSLRCM intactes + 73 nouveaux dons + 5 marqueurs internes, 33 supprimés masqués)
  - `Override/featgain.2da` (budgets Niv. 30 : 22 / 18 / 15 dons)
  - `Override/classpowergain.2da` (budgets Niv. 30 : 12 / 16 / 24 pouvoirs, Gardien +2 au Niv. 1)
  - `Override/baseitems.2da` (armes d20, armures CA/DEX, variantes 1M Gamoréen II)
  - `Override/spells.2da` (forbiditemmask, coûts PF, descriptions VF, noms prestige, Festin de mort L3, Cicatrice de Force I–III)
  - `Override/itemcreate.2da` & `Override/itemcreatemira.2da` (verrous 1/10/15/20, armes base onglet 4, roquettes Mira)
  - `Override/forceshields.2da` (paliers ×1,25 / ×2 / ×2,5 / ×3 / ×3,75 pour Armure Tactique II–III & Affranchi II)
  - `Override/autobalance.2da` (calibrage boss Set_5)
  - `feat_ids.json`, `spell_ids.json` & `baseitem_1m_map.json` (index pour Jalons 2, 3 & 4)

Règles strictes (README.md §2–§3) :
  - Cellules vides `pykotor.TwoDA` = `""` (JAMAIS `"****"`).
  - Base TSLRCM depuis `_reference/2da/*_tslrcm.2da` et `mods/04-engine-tests/backup/dialog.tlk.bak`.
  - Aucune ligne vanilla supprimée dans `feat.2da` ni `spells.2da` (compatibilité sauvegardes).
"""

from __future__ import annotations

import csv
import json
import re
import unicodedata
from pathlib import Path

from pykotor.resource.formats.tlk import read_tlk, write_tlk
from pykotor.resource.formats.twoda import TwoDA, read_2da, write_2da

ROOT = Path(__file__).resolve().parent.parent
REF_2DA = ROOT / "_reference" / "2da"
OUT_DIR = ROOT / "mods" / "overhaul"
OVR_DIR = OUT_DIR / "Override"

# Backup FR propre du dialog.tlk (TSLRCM)
BASE_TLK = ROOT / "mods" / "04-engine-tests" / "backup" / "dialog.tlk.bak"
if not BASE_TLK.exists():
    BASE_TLK = ROOT / "mods" / "00-test-feat" / "backup" / "dialog.tlk.bak"

CSV_FEATS = ROOT / "Kotor 2 - rééquilibrage - WIP Feats.csv"
CSV_WEAPONS = ROOT / "Kotor 2 - rééquilibrage - armes.csv"
CSV_ARMORS = ROOT / "Kotor 2 - rééquilibrage - Armures.csv"
CSV_POWERS = ROOT / "Kotor 2 - rééquilibrage - Spé Pouvoirs.csv"
CSV_CRAFT = ROOT / "Kotor 2 - rééquilibrage - Craft.csv"

_CP1252_FALLBACKS = str.maketrans({
    "\u2192": "->",   # →
    "\u2194": "<->",  # ↔
    "\u2264": "<=",   # ≤
    "\u2265": ">=",   # ≥
    "\u2212": "-",    # −
})


def sanitize_tlk(text: str) -> str:
    """Remplace les caractères Unicode absents de CP1252 pour éviter les '?' en jeu."""
    return text.translate(_CP1252_FALLBACKS)


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.replace("'", " ").replace("\u2019", " ")
    return re.sub(r"\s+", " ", s.lower()).strip()


def read_csv_rows(path: Path) -> list[list[str]]:
    with open(path, encoding="utf-8-sig", newline="") as fh:
        return list(csv.reader(fh))


def assert_no_literal_stars(table: TwoDA, name: str) -> None:
    """Vérifie la règle Bug #6 : aucune cellule ne doit contenir la chaîne littérale '****'."""
    for i, row in enumerate(table):
        for h in table.get_headers():
            if row.get_string(h) == "****":
                raise ValueError(f"{name} row {i} col '{h}' contains literal '****' (must be '')")


# ============================================================================
# 1. featgain.2da (budgets 22 / 18 / 15 sur 30 niveaux)
# ============================================================================

def _distribute_points(total_15: int, total_30: int, n_rows: int = 50, lvl1_val: int = 1) -> list[int]:
    """Répartit `total_15` points sur les niveaux 1..15 et `total_30 - total_15` sur 16..30
    (avec `lvl1_val` points garantis au niv. 1, puis cadence régulière)."""
    vals = [0] * n_rows
    vals[0] = lvl1_val
    rem15 = total_15 - lvl1_val
    for k in range(rem15):
        idx = 1 + int(round((k + 0.5) * 14 / rem15)) - 1
        idx = max(1, min(14, idx))
        while vals[idx] > 0 and idx < 14:
            idx += 1
        vals[idx] += 1
    rem30 = total_30 - total_15
    for k in range(rem30):
        idx = 15 + int(round((k + 0.5) * 15 / rem30)) - 1
        idx = max(15, min(29, idx))
        while vals[idx] > 0 and idx < 29:
            idx += 1
        vals[idx] += 1
    for idx in range(30, n_rows):
        vals[idx] = 1 if (idx % 2 == 0) else 0
    assert sum(vals[:15]) == total_15, (sum(vals[:15]), total_15)
    assert sum(vals[:30]) == total_30, (sum(vals[:30]), total_30)
    return vals


def build_featgain() -> TwoDA:
    fg = read_2da(REF_2DA / "featgain_tslrcm.2da")
    n = len(fg)
    # Budgets actés (§6) : Gardien/Maître/Maraudeur = 22 (11+11), Sentinelle/Prot./Assassin = 18 (9+9), Consulaire/MaîtreJedi/Seigneur = 15 (8+7)
    plan = {
        "jgd_reg": (11, 22),
        "jwm_reg": (11, 22),
        "sma_reg": (11, 22),
        "jsn_reg": (9, 18),
        "jwa_reg": (9, 18),
        "sas_reg": (9, 18),
        "jcn_reg": (8, 15),
        "jma_reg": (7, 15),
        "sld_reg": (7, 15),
    }
    for col, (t15, t30) in plan.items():
        if col in fg.get_headers():
            dist = _distribute_points(t15, t30, n)
            for i in range(n):
                fg.get_row(i).set_string(col, str(dist[i]))
    assert_no_literal_stars(fg, "featgain.2da")
    write_2da(fg, OVR_DIR / "featgain.2da")
    return fg


# ============================================================================
# 2. classpowergain.2da (budgets 12 / 16 / 24 sur 30 niveaux)
# ============================================================================

def build_classpowergain() -> TwoDA:
    pg = read_2da(REF_2DA / "classpowergain_tslrcm.2da")
    n = len(pg)
    # (total_15, total_30, lvl1_val) — Gardien : +2 pouvoirs au Niv. 1 (decisions_finales.md §1)
    plan = {
        "jgd": (6, 12, 2),
        "jwm": (6, 12, 1),
        "sma": (6, 12, 1),
        "jsn": (8, 16, 1),
        "jwa": (8, 16, 1),
        "sas": (8, 16, 1),
        "jcn": (12, 24, 2),
        "jma": (12, 24, 1),
        "sld": (12, 24, 1),
    }
    for col, (t15, t30, l1) in plan.items():
        if col in pg.get_headers():
            dist = _distribute_points(t15, t30, n, lvl1_val=l1)
            for i in range(n):
                pg.get_row(i).set_string(col, str(dist[i]))
    assert_no_literal_stars(pg, "classpowergain.2da")
    write_2da(pg, OVR_DIR / "classpowergain.2da")
    return pg


# ============================================================================
# 3. feat.2da + dialog.tlk (245 lignes TSLRCM intactes + 73 dons + 5 marqueurs)
# ============================================================================

ALL_LIST_COLS = [
    "scd_list", "sol_list", "sct_list",
    "jcn_list", "jgd_list", "jsn_list",
    "sas_list", "sld_list", "sma_list",
    "jwa_list", "jma_list", "jwm_list",
    "tec_list", "drx_list", "drc_list",
]
ALL_GRANT_COLS = [c.replace("_list", "_granted") for c in ALL_LIST_COLS] + [
    "jcn_pc_granted", "jgd_pc_granted", "jsn_pc_granted",
    "handmaiden", "baodur",
]

MARTIAL_PRESTIGE = ["jwm_list", "sma_list"]
HYBRID_PRESTIGE = ["jwa_list", "sas_list"]
CASTER_PRESTIGE = ["jma_list", "sld_list"]
ALL_JEDI_BASE = ["jgd_list", "jsn_list", "jcn_list"]
ALL_NON_MAGE = [
    "jgd_list", "jsn_list", "jwm_list", "sma_list", "jwa_list", "sas_list",
    "sol_list", "sct_list", "scd_list", "tec_list", "drc_list", "drx_list",
]
ALL_NON_DROID = [c for c in ALL_LIST_COLS if c not in ("drc_list", "drx_list")]
ALL_NON_MAGE_NON_DROID = [c for c in ALL_NON_MAGE if c not in ("drc_list", "drx_list")]


def _parse_min_level(prereq_txt: str) -> int:
    m = re.search(r"Niv\.\s*(\d+)\+", prereq_txt, re.I)
    return int(m.group(1)) if m else 0


def _allowed_classes_for_new_feat(label: str, cat: str, prereq_txt: str) -> tuple[list[str], int]:
    """Détermine les colonnes `*_list` autorisées et `minattackbonus` selon decisions_finales.md §6."""
    lbl = label.upper()
    c_n = norm(cat)
    p_n = norm(prereq_txt)
    rank = 3 if lbl.endswith("_3") else (2 if lbl.endswith("_2") else 1)

    # Affranchi de la Force : accordé automatiquement aux niv. 1/5/9 du Jedi Protecteur (jamais sélectionnable)
    if "UNBOUND_FORCE" in lbl:
        return [], 0

    # Spécialisations de caractéristique : ouvertes à toutes les classes (paliers Niv. 1 / 8 / 15)
    if "caracteristique" in c_n:
        return ALL_LIST_COLS, 0

    # Postures (Styles de combat)
    if "styles de combat" in c_n:
        if rank <= 2 or "DUEL" in lbl:
            return ALL_LIST_COLS, 0
        return ALL_NON_MAGE, 0

    # Éveil de Force (R3 : JMA/SLD + JCN bloqué par orreqfeat0=MOD_PRESTIGE_MAGE pour Kreia Niv. 15+)
    if "metamagie" in c_n or "eveil de force" in c_n:
        if "PROLONG" in lbl or rank == 1:
            return ALL_JEDI_BASE + MARTIAL_PRESTIGE + HYBRID_PRESTIGE + CASTER_PRESTIGE, 0
        if rank == 2:
            return ["jcn_list"] + CASTER_PRESTIGE, 0
        return CASTER_PRESTIGE + ["jcn_list"], 0

    # Spécialisations d'arme (8 familles) — gating strict Sabres / Mêlée / Distance / Droïdes
    if "specialisations" in c_n and "arme" in c_n or "spec_" in lbl.lower():
        if "SPEC_LASER" in lbl:
            if rank == 1:
                return ALL_JEDI_BASE + MARTIAL_PRESTIGE + HYBRID_PRESTIGE + CASTER_PRESTIGE, 0
            if rank == 2:
                return ["jgd_list", "jsn_list"] + MARTIAL_PRESTIGE + HYBRID_PRESTIGE, 0
            return MARTIAL_PRESTIGE, 0
        if any(k in lbl for k in ("SPEC_BLUNT", "SPEC_PRIM", "SPEC_VIBRO")):
            if rank == 1:
                return ALL_NON_DROID, 0
            if rank == 2:
                return ALL_NON_MAGE_NON_DROID, 0
            return MARTIAL_PRESTIGE + ["sol_list", "sct_list", "scd_list", "tec_list"], 0
        # 4 familles Distance (ASSAULT, HEAVY, TAC, ASSASSIN) : drx jusqu'à R2, drc jusqu'à R3
        if rank == 1:
            return ALL_LIST_COLS, 0
        if rank == 2:
            return ALL_NON_MAGE, 0
        return MARTIAL_PRESTIGE + ["sol_list", "sct_list", "scd_list", "tec_list", "drc_list"], 0

    # Armures (Juggernaut, Armure Tactique, Esquive Balistique)
    # Note : jsn_list sur Armure Tactique III et Esquive Balistique III est verrouillé via
    # orreqfeat0=MOD_PRESTIGE_HYBRID (octroyé à Visas Niv. 15+, bloquant un PJ Sentinelle non prestige).
    if "armure" in c_n or "ARMOR_" in lbl:
        if rank == 1:
            return ALL_LIST_COLS, 0
        if "HEAVY" in lbl:  # Juggernaut
            if rank == 2:
                return ["jgd_list", "jwm_list", "sma_list", "sol_list"], 0
            return MARTIAL_PRESTIGE + ["sol_list"], 0
        if "MED" in lbl:  # Armure Tactique
            if rank == 2:
                return ["jsn_list", "jwa_list", "sas_list", "sct_list", "scd_list", "tec_list"], 0
            return HYBRID_PRESTIGE + ["jsn_list", "sct_list", "scd_list", "tec_list"], 0
        if "LIGHT" in lbl:  # Esquive Balistique
            if rank == 2:
                return ["jgd_list", "jsn_list", "jwm_list", "sma_list", "jwa_list", "sas_list", "sol_list", "sct_list", "scd_list"], 0
            return MARTIAL_PRESTIGE + HYBRID_PRESTIGE + ["jsn_list", "sol_list", "sct_list", "scd_list"], 0

    if "tous sauf mages" in p_n:
        return ALL_NON_MAGE, 0
    return ALL_LIST_COLS, 0


def _pick_real_icon(label: str, cat: str) -> str:
    """Choisit une vraie icône vanilla existante (évite carré gris en jeu et crash KSE TPC.pm)."""
    lbl = label.upper()
    rank = "03" if lbl.endswith("_3") else ("02" if lbl.endswith("_2") else "01")
    if "AMBIDEXTRY" in lbl or "DOUBLE_WEAPON" in lbl:
        return f"if_2weap{rank}"
    if "DUEL" in lbl:
        return f"if_duel{rank}"
    if "HEAVY_WEAPON" in lbl:
        return f"if_pattack{rank}"
    if "SPEC_LASER" in lbl:
        return f"if_jedidef{rank}"
    if any(k in lbl for k in ("SPEC_ASSAULT", "SPEC_HEAVY", "SPEC_TAC", "SPEC_ASSASSIN")):
        return f"if_preshot{rank}"
    if "SPEC_" in lbl:
        return f"if_pattack{rank}"
    if "ARMOR_" in lbl:
        return f"if_armprof{rank}"
    if "META_EMPOWER" in lbl:
        return "if_focalter"
    if "META_PENETRATE" in lbl:
        return "if_focmaster"
    if "META_EXTEND" in lbl:
        return "if_foccontr"
    if "ECHANI" in lbl:
        return "if_finesse02" if rank != "01" else "if_finesse01"
    if "GAMORREAN" in lbl:
        return f"if_pattack{rank}"
    if "KRAITH" in lbl:
        return "if_focboost"
    if "GAND" in lbl:
        return "if_focdemo"
    if "MATUKAI" in lbl:
        return "if_focsense"
    if "NOMI" in lbl:
        return "if_battlemed"
    if "UNBOUND_FORCE" in lbl:
        return "if_focaware"
    return f"if_duel{rank}"


# 5 dons marqueurs internes (ajoutés APRÈS les 73 dons CSV pour préserver tous les index 245..317)
INTERNAL_MARKER_FEATS: list[tuple[str, str, str, str, dict[str, str]]] = [
    (
        "MOD_PRESTIGE_MAGE",
        "Voie des Arcanes",
        "[Mod D20-Overhaul]\nMaîtrise avancée de la Force ouvrant l'accès au Rang III d'Éveil de Force (Maître Jedi, Seigneur Sith et Kreia Niv. 15+).",
        "if_focmaster",
        {"jma_granted": "1", "sld_granted": "1"},
    ),
    (
        "MOD_PRESTIGE_HYBRID",
        "Voie de l'Ombre",
        "[Mod D20-Overhaul]\nMaîtrise tactique et furtive ouvrant l'accès aux dons de prestige hybrides (Protecteur, Assassin, Visas Niv. 15+ et spécialistes).",
        "if_focaware",
        {"jwa_granted": "1", "sas_granted": "1", "sct_granted": "1", "scd_granted": "1", "tec_granted": "1"},
    ),
    (
        "MOD_PRESTIGE_MARTIAL",
        "Voie Martiale",
        "[Mod D20-Overhaul]\nMaîtrise martiale avancée ouvrant l'accès aux spécialisations d'armure de Rang III (Maître d'Armes, Maraudeur et Soldat).",
        "if_pattack03",
        {"jwm_granted": "1", "sma_granted": "1", "sol_granted": "1"},
    ),
    (
        "MOD_BOSS_RD",
        "Endurance d'Élite",
        "[Mod D20-Overhaul]\nRésistance aux dégâts passive de sous-boss et de boss (RD 2 / 5 / 8 selon le palier de niveau).",
        "if_armprof03",
        {},
    ),
    (
        "MOD_BATTLE_PRECOG",
        "Prémonition du combat (Echani)",
        "[Mod D20-Overhaul]\nEnseignement de la Servante : accorde passivement +10 % d'esquive au corps à corps (remplace le bonus SAG à la CA).",
        "if_finesse02",
        {},
    ),
]


def build_feats_and_tlk() -> tuple[TwoDA, dict[str, int]]:
    feat = read_2da(REF_2DA / "feat_tslrcm.2da")
    tlk = read_tlk(BASE_TLK)
    rows = read_csv_rows(CSV_FEATS)

    tmpl = {h: "" for h in feat.get_headers()}
    tmpl["icon"] = "if_duel01"
    tmpl["gainmultiple"] = "0"
    tmpl["effectsstack"] = "0"
    tmpl["allclassescanuse"] = "0"
    tmpl["toolscategories"] = "6"
    tmpl["hostilefeat"] = "0"
    tmpl["exclusion"] = "0x00"
    tmpl["pips"] = "1"
    for c in ALL_LIST_COLS:
        tmpl[c] = "4"

    # 1. Masquer les 28/29 dons supprimés SANS supprimer leurs lignes (compatibilité sauvegardes !)
    hidden_count = 0
    desc_col_idx = rows[0].index("Description (mod)") if rows and "Description (mod)" in rows[0] else -1
    vanilla_desc_updated = 0
    for r in rows[1:]:
        if len(r) < 7 or not r[0].strip().isdigit():
            continue
        fid = int(r[0].strip())
        mod_txt = r[6].strip().lower()
        if "supprim" in mod_txt and fid < len(feat):
            frow = feat.get_row(fid)
            for c in ALL_LIST_COLS:
                if c in feat.get_headers():
                    frow.set_string(c, "4")
            for c in ALL_GRANT_COLS:
                if c in feat.get_headers():
                    frow.set_string(c, "")
            frow.set_string("allclassescanuse", "0")
            hidden_count += 1
        elif desc_col_idx >= 0 and len(r) > desc_col_idx and r[desc_col_idx].strip() and fid < len(feat):
            desc_ref = len(tlk)
            tlk.add(sanitize_tlk(r[desc_col_idx].strip()))
            feat.get_row(fid).set_string("description", str(desc_ref))
            vanilla_desc_updated += 1

    # 1b. Calibrage B4-1 : Spécialiste combat à mains nues plafonné au Rang III (+3d4) et harmonisé Prestige
    unarmed_schedule = {
        212: (4, 1),   # UNARMED_SPECIALIST_I (+1d4)
        213: (12, 1),  # UNARMED_SPECIALIST_II (+2d4)
        214: (19, 4),  # UNARMED_SPECIALIST_III (+3d4 — plafond final)
    }
    base_jedi_grants = ("jcn_granted", "jgd_granted", "jsn_granted", "handmaiden", "baodur")
    prestige_grants = ("sas_granted", "sld_granted", "sma_granted", "jwa_granted", "jma_granted", "jwm_granted")
    for fid, (base_lvl, prest_lvl) in unarmed_schedule.items():
        if fid < len(feat):
            frow = feat.get_row(fid)
            for c in base_jedi_grants:
                if c in feat.get_headers():
                    frow.set_string(c, str(base_lvl))
            for c in prestige_grants:
                if c in feat.get_headers():
                    frow.set_string(c, str(prest_lvl))

    # 1c. Renommer les anciens dons XXXFORCE_CAMOFLAGE (97, 141, 142) en Spectre de la Force I-III par cohérence TLK
    for fid, nm in ((97, "Spectre de la Force I"), (141, "Spectre de la Force II"), (142, "Spectre de la Force III")):
        if fid < len(feat):
            nref = len(tlk)
            tlk.add(nm)
            feat.get_row(fid).set_string("name", str(nref))

    # 2. Recenser les 73 nouveaux dons + 5 marqueurs internes afin de connaître tous les IDs avant chaînage
    feat_ids: dict[str, int] = {}
    new_rows_data: list[tuple[int, list[str]]] = []
    next_id = len(feat)
    for r in rows[1:]:
        if not r or not r[0].startswith("nouveau"):
            continue
        label = r[1].strip()
        feat_ids[label] = next_id
        new_rows_data.append((next_id, r))
        next_id += 1

    marker_rows_data: list[tuple[int, tuple[str, str, str, str, dict[str, str]]]] = []
    for mspec in INTERNAL_MARKER_FEATS:
        feat_ids[mspec[0]] = next_id
        marker_rows_data.append((next_id, mspec))
        next_id += 1

    id_prest_mage = feat_ids["MOD_PRESTIGE_MAGE"]
    id_prest_hyb = feat_ids["MOD_PRESTIGE_HYBRID"]
    id_prest_mart = feat_ids["MOD_PRESTIGE_MARTIAL"]

    # 2b. Esquive Totale (FEAT_EVASION, ligne 125) :
    #     Sélectionnable dès Niv. 15 pour JWA, SAS et Visas (jsn_list=1 verrouillé par MOD_PRESTIGE_HYBRID).
    #     Mira conserve sct_granted="6".
    if len(feat) > 125:
        ev_row = feat.get_row(125)
        ev_row.set_string("jwa_list", "1")
        ev_row.set_string("sas_list", "1")
        ev_row.set_string("jsn_list", "1")
        ev_row.set_string("mincharlevel", "15")
        ev_row.set_string("prereqfeat1", str(id_prest_hyb))

    # Prérequis Rang I (port d'armure 4/5/6 & maîtrise d'arme 39/40/43/44)
    r1_prereq_exact: dict[str, str] = {
        "MOD_ARMOR_LIGHT_1": "5",   # ARMOUR_PROF_LIGHT
        "MOD_ARMOR_MED_1":   "6",   # ARMOUR_PROF_MEDIUM
        "MOD_ARMOR_HEAVY_1": "4",   # ARMOUR_PROF_HEAVY
        "MOD_SPEC_BLUNT_1":  "44",  # WEAPON_PROF_MELEE_WEAPONS
        "MOD_SPEC_PRIM_1":   "44",  # WEAPON_PROF_MELEE_WEAPONS
        "MOD_SPEC_VIBRO_1":  "44",  # WEAPON_PROF_MELEE_WEAPONS
        "MOD_SPEC_LASER_1":  "43",  # WEAPON_PROF_LIGHTSABER
    }
    r1_prereq_or_ranged = {
        "MOD_SPEC_ASSAULT_1", "MOD_SPEC_HEAVY_1", "MOD_SPEC_TAC_1", "MOD_SPEC_ASSASSIN_1",
    }
    unbound_grant_lvls = {
        "MOD_UNBOUND_FORCE_1": "1",
        "MOD_UNBOUND_FORCE_2": "5",
        "MOD_UNBOUND_FORCE_3": "9",
    }

    for fid, r in new_rows_data:
        label = r[1].strip()
        nom = r[2].strip()
        cat = r[3].strip()
        prereq = r[4].strip()
        desc_mod = (
            r[desc_col_idx].strip()
            if desc_col_idx >= 0 and len(r) > desc_col_idx and r[desc_col_idx].strip()
            else (r[6].strip() or r[5].strip())
        )

        name_ref = len(tlk)
        tlk.add(sanitize_tlk(nom))
        desc_ref = len(tlk)
        tlk.add(sanitize_tlk(desc_mod))

        entry = dict(tmpl)
        entry["label"] = label
        entry["name"] = str(name_ref)
        entry["description"] = str(desc_ref)
        entry["icon"] = _pick_real_icon(label, cat)

        min_lvl = _parse_min_level(prereq)
        if min_lvl > 1 and label not in unbound_grant_lvls:
            entry["mincharlevel"] = str(min_lvl)

        # Chaînage exact vanilla KotOR 2
        if label.endswith("_1") and (label[:-2] + "_2") in feat_ids:
            entry["successor"] = str(feat_ids[label[:-2] + "_2"])
            entry["pips"] = "1"
        elif label.endswith("_2") and (label[:-2] + "_1") in feat_ids:
            entry["prereqfeat1"] = str(feat_ids[label[:-2] + "_1"])
            if (label[:-2] + "_3") in feat_ids:
                entry["successor"] = str(feat_ids[label[:-2] + "_3"])
            entry["pips"] = "2"
        elif label.endswith("_3") and (label[:-2] + "_2") in feat_ids:
            if (label[:-2] + "_1") in feat_ids:
                entry["prereqfeat1"] = str(feat_ids[label[:-2] + "_1"])
                entry["prereqfeat2"] = str(feat_ids[label[:-2] + "_2"])
            else:
                entry["prereqfeat1"] = str(feat_ids[label[:-2] + "_2"])
            entry["pips"] = "3"
        else:
            entry["pips"] = "1"

        # Prérequis R1 (armures & armes)
        if label in r1_prereq_exact:
            entry["prereqfeat1"] = r1_prereq_exact[label]
        elif label in r1_prereq_or_ranged:
            entry["orreqfeat0"] = "39"  # WEAPON_PROF_BLASTER
            entry["orreqfeat1"] = "40"  # WEAPON_PROF_BLASTER_RIFLE

        # Verrous prestige compagnons Kreia / Visas (via orreqfeat0 / orreqfeat1)
        if label in ("MOD_META_EMPOWER_3", "MOD_META_PENETRATE_3"):
            entry["orreqfeat0"] = str(id_prest_mage)
        elif label == "MOD_ARMOR_MED_3":
            entry["orreqfeat0"] = str(id_prest_hyb)
        elif label == "MOD_ARMOR_LIGHT_3":
            entry["orreqfeat0"] = str(id_prest_hyb)
            entry["orreqfeat1"] = str(id_prest_mart)

        # Affranchi de la Force I–III : octroyé automatiquement au Jedi Protecteur aux niv. 1 / 5 / 9
        if label in unbound_grant_lvls:
            entry["jwa_granted"] = unbound_grant_lvls[label]

        allowed_cols, min_bab = _allowed_classes_for_new_feat(label, cat, prereq)
        for c in allowed_cols:
            if c in entry:
                entry[c] = "1"
        if min_bab > 0:
            entry["minattackbonus"] = str(min_bab)

        feat.add_row(str(fid), entry)

    # 3. Ajouter les 5 dons marqueurs internes
    for fid, (mlbl, mname, mdesc, micon, mgrants) in marker_rows_data:
        name_ref = len(tlk)
        tlk.add(mname)
        desc_ref = len(tlk)
        tlk.add(mdesc)
        entry = dict(tmpl)
        entry["label"] = mlbl
        entry["name"] = str(name_ref)
        entry["description"] = str(desc_ref)
        entry["icon"] = micon
        for gcol, glvl in mgrants.items():
            if gcol in entry:
                entry[gcol] = glvl
        feat.add_row(str(fid), entry)

    assert_no_literal_stars(feat, "feat.2da")
    write_2da(feat, OVR_DIR / "feat.2da")
    write_tlk(tlk, OUT_DIR / "dialog.tlk")
    (OUT_DIR / "feat_ids.json").write_text(json.dumps(feat_ids, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        f"[OK] feat.2da ({len(feat)} rows: {hidden_count} masqués, {len(new_rows_data)} dons + "
        f"{len(marker_rows_data)} marqueurs ajoutés) + dialog.tlk ({len(tlk)} entrées)"
    )
    return feat, feat_ids


# ============================================================================
# 4. baseitems.2da (Armes.csv + Armures.csv + Variantes 1M Gamoréen II)
# ============================================================================

ARMOR_BASEITEM_MAP = {
    "Armor_Class_4": (4, 16),
    "Armor_Class_5": (5, 14),
    "Armor_Class_6": (6, 4),
    "Armor_Class_7": (7, 3),
    "Armor_Class_8": (10, 1),
    "Armor_Class_9": (11, 0),
    "Armor_Armd_Flight_Suit": (5, 15),
    "Armor_Zeison_Sha": (4, 16),
}

GAMORREAN_MIRROR_LABELS = [
    "Quarter_Staff",
    "Double_Bladed_Sword",
    "Vibro_Double_Blade",
    "Double_Bladed_Lightsaber",
    "Blaster_Rifle",
    "Blaster_Carbine",
    "Repeating_Blaster",
    "Heavy_Repeating_Blaster",
    "Disrupter_Rifle",
    "Sonic_Rifle",
    "Ion_Rifle",
    "Bowcaster",
    "Vibro_Sword",
    "Gammorean_Battleaxe",
    "Force_Pike",
    "Wookie_Warblade",
]

MELEE_2H_BASEITEMS = (
    "Vibro_Sword",
    "Gammorean_Battleaxe",
    "Force_Pike",
)

WEAPON_CSV_TO_BASEITEM = {
    "blaster carbines": "Blaster_Carbine",
    "blaster rifles": "Blaster_Rifle",
    "bowcasters": "Bowcaster",
    "repeating blasters": "Repeating_Blaster",
    "heavy repeating blasters": "Heavy_Repeating_Blaster",
    "disruptor rifles": "Disrupter_Rifle",
    "ion rifles": "Ion_Rifle",
    "sonic rifles": "Sonic_Rifle",
    "blaster pistols": "Blaster_Pistol",
    "heavy blasters": "Heavy_Blaster",
    "hold out blasters": "Hold_Out_Blaster",
    "disruptor pistols": "Disrupter_Pistol",
    "ion blasters": "Ion_Blaster",
    "sonic pistols": "Sonic_Pistol",
    "stun batons": "Stun_Baton",
    "short swords (craftable)": "Short_Sword",
    "vibroblades": "Vibro_Blade",
    "long swords (craftable)": "Long_Sword",
    "gamorrean battleaxes": "Gammorean_Battleaxe",
    "vibroswords (craftable)": "Vibro_Sword",
    "quarterstaffs": "Quarter_Staff",
    "force pikes": "Force_Pike",
    "double-bladed sword": "Double_Bladed_Sword",
    "vibro double-blades (craftable)": "Vibro_Double_Blade",
    "wookiee warblades": "Wookie_Warblade",
    "short light saber": "Short_Lightsaber",
    "light saber": "Lightsaber",
    "double light saber": "Double_Bladed_Lightsaber",
}


def build_baseitems(feat_ids: dict[str, int]) -> TwoDA:
    bi = read_2da(REF_2DA / "baseitems_tslrcm.2da")
    by_label = {bi.get_row(i).get_string("label"): i for i in range(len(bi))}

    arm_updated = 0
    for lbl, (ac, max_dex) in ARMOR_BASEITEM_MAP.items():
        if lbl in by_label:
            r = bi.get_row(by_label[lbl])
            r.set_string("baseac", str(ac))
            r.set_string("dexbonus", str(max_dex))
            if lbl == "Armor_Zeison_Sha":
                r.set_string("itemtype", "31")
            arm_updated += 1

    weap_rows = read_csv_rows(CSV_WEAPONS)
    weap_updated = 0
    for r in weap_rows[1:]:
        if len(r) < 4:
            continue
        key = r[0].strip().lower()
        lbl = WEAPON_CSV_TO_BASEITEM.get(key)
        if not lbl or lbl not in by_label:
            continue
        m_dice = re.search(r"(\d+)d(\d+)", r[1])
        m_crit = re.search(r"(\d+)-20\s*,\s*x(\d+)", r[3])
        brow = bi.get_row(by_label[lbl])
        if m_dice:
            brow.set_string("numdice", m_dice.group(1))
            brow.set_string("dietoroll", m_dice.group(2))
        if m_crit:
            threat = 21 - int(m_crit.group(1))
            brow.set_string("critthreat", str(threat))
            brow.set_string("crithitmult", m_crit.group(2))
        weap_updated += 1

    for lbl in MELEE_2H_BASEITEMS:
        if lbl in by_label:
            brow = bi.get_row(by_label[lbl])
            brow.set_string("equipableslots", "0x00010")
            brow.set_string("weaponwield", "2")
            brow.set_string("weaponsize", "4")

    if len(bi) > 81:
        bi.get_row(81).set_string("droidorhuman", "0")

    mirror_map: dict[str, int] = {}
    if "Blaster_Pistol" in by_label:
        src_row = bi.get_row(by_label["Blaster_Pistol"])
        ml_dict = {h: src_row.get_string(h) for h in bi.get_headers()}
        ml_dict.update({
            "name": "74505",
            "label": "Mining_Laser",
            "defaulticon": "iw_gun",
            "numdice": "1",
            "dietoroll": "7",
            "critthreat": "1",
            "crithitmult": "2",
            "basecost": "0.2",
            "storepanelsort": "40",
        })
        ml_idx = len(bi)
        bi.add_row(str(ml_idx), ml_dict)
        mirror_map["Mining_Laser"] = ml_idx

    if "Blaster_Rifle" in by_label:
        src_row = bi.get_row(by_label["Blaster_Rifle"])
        aml_dict = {h: src_row.get_string(h) for h in bi.get_headers()}
        aml_dict.update({
            "name": "74333",
            "label": "Adv_Mining_Laser",
            "defaulticon": "iw_gun",
            "numdice": "1",
            "dietoroll": "11",
            "critthreat": "2",
            "crithitmult": "2",
            "basecost": "0.2",
            "storepanelsort": "45",
        })
        aml_idx = len(bi)
        bi.add_row(str(aml_idx), aml_dict)
        mirror_map["Adv_Mining_Laser"] = aml_idx

    gam2_id = feat_ids.get("MOD_GAMORREAN_2") or feat_ids.get("MOD_GAMORRAN_2")
    assert gam2_id is not None, f"MOD_GAMORREAN_2 introuvable dans {list(feat_ids.keys())[:10]}"
    for lbl in GAMORREAN_MIRROR_LABELS:
        if lbl not in by_label:
            continue
        src_idx = by_label[lbl]
        src_row = bi.get_row(src_idx)
        new_dict = {h: src_row.get_string(h) for h in bi.get_headers()}
        new_lbl = f"{lbl}_1M"
        new_dict["label"] = new_lbl
        new_dict["equipableslots"] = "0x00030"
        is_ranged = new_dict.get("rangedweapon") == "1"
        new_dict["weaponwield"] = "4" if is_ranged else "2"  # 4 = pistolet 1M (distance), 2 = lame 1M (mêlée)
        new_dict["weaponsize"] = "3"
        new_dict["reqfeat0"] = str(gam2_id)
        for rf_col in ("reqfeat1", "reqfeat2", "reqfeat3", "reqfeat4"):
            if rf_col in new_dict:
                new_dict[rf_col] = ""
        new_idx = len(bi)
        bi.add_row(str(new_idx), new_dict)
        mirror_map[lbl] = new_idx

    # Variante 1M dédiée pour Adv_Mining_Laser (Laser de forage évolué, 101per.mod)
    if "Adv_Mining_Laser" in mirror_map:
        aml_src = bi.get_row(mirror_map["Adv_Mining_Laser"])
        aml_1m = {h: aml_src.get_string(h) for h in bi.get_headers()}
        aml_1m["label"] = "Adv_Mining_Laser_1M"
        aml_1m["equipableslots"] = "0x00030"
        aml_1m["weaponwield"] = "4"
        aml_1m["weaponsize"] = "3"
        aml_1m["reqfeat0"] = str(gam2_id)
        for rf_col in ("reqfeat1", "reqfeat2", "reqfeat3", "reqfeat4"):
            if rf_col in aml_1m:
                aml_1m[rf_col] = ""
        aml_1m_idx = len(bi)
        bi.add_row(str(aml_1m_idx), aml_1m)
        mirror_map["Adv_Mining_Laser_1M"] = aml_1m_idx

    if "Stun_Baton" in by_label:
        src_row = bi.get_row(by_label["Stun_Baton"])
        pt_dict = {h: src_row.get_string(h) for h in bi.get_headers()}
        pt_dict["label"] = "Plasma_Torch"
        pt_dict["numdice"] = "1"
        pt_dict["dietoroll"] = "1"
        pt_dict["critthreat"] = "1"
        pt_dict["crithitmult"] = "2"
        pt_idx = len(bi)
        bi.add_row(str(pt_idx), pt_dict)
        mirror_map["Plasma_Torch"] = pt_idx

    assert_no_literal_stars(bi, "baseitems.2da")
    write_2da(bi, OVR_DIR / "baseitems.2da")
    (OUT_DIR / "baseitem_1m_map.json").write_text(json.dumps(mirror_map, indent=2) + "\n", encoding="utf-8")
    print(f"[OK] baseitems.2da ({len(bi)} rows: {arm_updated} armures, {weap_updated} armes, {len(mirror_map)} variantes 1M Gamoréen II reqfeat0={gam2_id})")
    return bi


# ============================================================================
# 5. spells.2da (forbiditemmask + coûts PF + Festin de mort L3 + Cicatrice I–III)
# ============================================================================

ARMOR_MASK_MAP = [
    (("armure interdite", "interdite", "robe"), "0x003f"),
    (("armure legere", "legere"), "0x003c"),
    (("armure moyenne", "intermediaire", "moyenne"), "0x0030"),
    (("armure lourde", "lourde"), "0x0000"),
]

ALL_SPELL_CLASS_COLS = (
    "guardian", "consular", "sentinel",
    "weapmstr", "jedimaster", "watchman",
    "marauder", "sithlord", "assassin",
)

# Mapping exhaustif & vérifié : clé VO normalisée (Spé Pouvoirs.csv) -> labels EXACTS dans spells.2da
POWER_FAMILY_SPELLS: list[tuple[str, list[str]]] = [
    ("force aura",            ["FORCE_POWER_FORCE_AURA", "FORCE_POWER_FORCE_SHIELD", "FORCE_POWER_FORCE_ARMOR"]),
    ("force barrier",         ["FORCE_POWER_FORCE_BARRIER", "FORCE_POWER_IMPROVED_FORCE_BARRIER", "FORCE_POWER_MASTER_FORCE_BARRIER"]),
    ("force valor",           ["FORCE_POWER_FORCE_VALOR", "FORCE_POWER_KNIGHT_VALOR", "FORCE_POWER_MASTER_VALOR"]),
    ("cure / heal",           ["FORCE_POWER_CURE", "FORCE_POWER_HEAL", "FORCE_POWER_MASTER_HEAL"]),
    ("revitalize",            ["FORCE_POWER_REVITALIZE", "FORCE_POWER_IMPROVED_REVITALIZE", "FORCE_POWER_MASTER_REVITALIZE"]),
    ("stun / stasis",         ["FORCE_POWER_STUN", "FORCE_POWER_STASIS", "FORCE_POWER_MASS_STASIS"]),
    ("stun droid",            ["FORCE_POWER_DROID_STUN", "FORCE_POWER_DROID_DISABLE", "FORCE_POWER_DROID_DESTROY"]),
    ("battle precognition",   ["FORCE_POWER_BATTLE_PRECOGNITION"]),
    ("force enlightenment",   ["FORCE_POWER_FORCE_ENLIGHTENMENT"]),
    ("inspire followers",     ["FORCE_POWER_INSPIRE_FOLLOWERS_I", "FORCE_POWER_INSPIRE_FOLLOWERS_II", "FORCE_POWER_INSPIRE_FOLLOWERS_III"]),
    ("affect mind",           ["FORCE_POWER_AFFECT_MIND", "FORCE_POWER_DOMINATE"]),
    ("battle meditation",     ["FORCE_POWER_BATTLE_MEDITATION_PC", "FORCE_POWER_IMPROVED_BATTLE_MEDITATION_PC", "FORCE_POWER_MASTER_BATTLE_MEDITATION_PC"]),
    ("burst of speed",        ["FORCE_POWER_SPEED_BURST", "FORCE_POWER_KNIGHT_SPEED", "FORCE_POWER_SPEED_MASTERY"]),
    ("energy resistance",     ["FORCE_POWER_RESIST_ENERGY_1", "FORCE_POWER_RESIST_ENERGY_2", "FORCE_POWER_MASTER_ENERGY_RESISTANCE"]),
    ("force body",            ["FORCE_POWER_FORCE_BODY", "FORCE_POWER_IMPROVED_FORCE_BODY", "FORCE_POWER_MASTER_FORCE_BODY"]),
    ("force deflection",      ["FORCE_POWER_FORCE_REPULSION", "FORCE_POWER_FORCE_REDIRECTION"]),
    ("force push",            ["FORCE_POWER_FORCE_PUSH", "FORCE_POWER_FORCE_WHIRLWIND", "FORCE_POWER_FORCE_WAVE"]),
    ("force resistance",      ["FORCE_POWER_RESIST_FORCE", "FORCE_POWER_FORCE_IMMUNITY"]),
    ("force suppression",     ["FORCE_POWER_SUPRESS_FORCE", "FORCE_POWER_FORCE_BREACH"]),
    ("mind trick / confusion",["FORCE_POWER_MIND_TRICK", "FORCE_POWER_CONFUSION"]),
    ("throw lightsaber",      ["FORCE_POWER_LIGHT_SABER_THROW", "FORCE_POWER_LIGHT_SABER_THROW_ADVANCED"]),
    ("beast trick",           ["FORCE_POWER_BEAST_TRICK", "FORCE_POWER_BEAST_CONFUSION"]),
    ("breath control",        ["FORCE_POWER_BREATH_CONTROL"]),
    ("force camouflage",      ["FORCE_POWER_FORCE_CAMOUFLAGE", "FORCE_POWER_IMPROVED_FORCE_CAMOUFLAGE", "FORCE_POWER_MASTER_FORCE_CAMOUFLAGE"]),
    ("force sight",           ["FORCE_POWER_FORCE_SIGHT"]),
    ("precognition (",        ["FORCE_POWER_PRECOGNITION"]),
    ("drain force",           ["FORCE_POWER_DRAIN_FORCE", "FORCE_POWER_IMPROVED_DRAIN_FORCE", "FORCE_POWER_MASTER_DRAIN_FORCE"]),
    ("drain life",            ["FORCE_POWER_DRAIN_LIFE", "FORCE_POWER_DEATH_FIELD", "FORCE_POWER_DEATH_FEAST"]),
    ("fear / horror",         ["FORCE_POWER_FEAR", "FORCE_POWER_HORROR", "FORCE_POWER_INSANITY"]),
    ("force scream",          ["FORCE_POWER_FORCE_SCREAM", "FORCE_POWER_IMPROVED_FORCE_SCREAM", "FORCE_POWER_MASTER_FORCE_SCREAM"]),
    ("shock / force",         ["FORCE_POWER_SHOCK", "FORCE_POWER_LIGHTNING", "FORCE_POWER_FORCE_STORM"]),
    ("slow / affliction",     ["FORCE_POWER_SLOW", "FORCE_POWER_AFFLICTION", "FORCE_POWER_PLAGUE"]),
    ("wound / choke",         ["FORCE_POWER_WOUND", "FORCE_POWER_CHOKE", "FORCE_POWER_KILL"]),
    ("crush opposition",      ["FORCE_POWER_CRUSH_OPPOSITION_I", "FORCE_POWER_CRUSH_OPPOSITION_II", "FORCE_POWER_CRUSH_OPPOSITION_III"]),
    ("force crush",           ["FORCE_POWER_FORCE_CRUSH"]),
    ("fury / improved",       ["FORCE_POWER_FURY", "FORCE_POWER_IMPROVED_FURY", "FORCE_POWER_MASTER_FURY"]),
    ("force scar",            ["FORCE_POWER_FORCE_SCAR_I", "FORCE_POWER_FORCE_SCAR_II", "FORCE_POWER_FORCE_SCAR_III"]),
]

SPELL_RENAME_FR: dict[str, str] = {
    "FORCE_POWER_INSPIRE_FOLLOWERS_I":       "Écho des Liens I",
    "FORCE_POWER_INSPIRE_FOLLOWERS_II":      "Écho des Liens II",
    "FORCE_POWER_INSPIRE_FOLLOWERS_III":     "Écho des Liens III",
    "FORCE_POWER_CRUSH_OPPOSITION_I":        "Déchirure de la Force I",
    "FORCE_POWER_CRUSH_OPPOSITION_II":       "Déchirure de la Force II",
    "FORCE_POWER_CRUSH_OPPOSITION_III":      "Déchirure de la Force III",
    "FORCE_POWER_FURY":                      "Stigmate de Force I",
    "FORCE_POWER_IMPROVED_FURY":             "Stigmate de Force II",
    "FORCE_POWER_MASTER_FURY":               "Stigmate de Force III",
    "FORCE_POWER_FORCE_CAMOUFLAGE":          "Spectre de la Force I",
    "FORCE_POWER_IMPROVED_FORCE_CAMOUFLAGE": "Spectre de la Force II",
    "FORCE_POWER_MASTER_FORCE_CAMOUFLAGE":   "Spectre de la Force III",
    "FORCE_POWER_FORCE_SCAR_I":              "Cicatrice de Force I",
    "FORCE_POWER_FORCE_SCAR_II":             "Cicatrice de Force II",
    "FORCE_POWER_FORCE_SCAR_III":            "Cicatrice de Force III",
    "FORCE_POWER_DEATH_FEAST":               "Festin de mort",
}


def build_spells() -> tuple[TwoDA, dict[str, int]]:
    sp = read_2da(REF_2DA / "spells_tslrcm.2da")
    tlk = read_tlk(OUT_DIR / "dialog.tlk")
    headers = sp.get_headers()
    spell_ids: dict[str, int] = {}

    # 1. Ajouter Festin de mort (L3 de Absorption de vie / Champ de mort)
    df_row = sp.get_row(11)  # FORCE_POWER_DEATH_FIELD
    for col in ALL_SPELL_CLASS_COLS + ("inate",):
        if col in headers:
            df_row.set_string(col, "15")  # L2 Niv. 15 (Spé Pouvoirs.csv)
    df_row.set_string("pips", "2")

    feast_dict = {h: df_row.get_string(h) for h in headers}
    feast_dict["label"] = "FORCE_POWER_DEATH_FEAST"
    feast_dict["prerequisites"] = "15_11"
    feast_dict["pips"] = "3"
    feast_dict["forcepoints"] = "55"
    feast_dict["forbiditemmask"] = "0x003f"
    for col in ALL_SPELL_CLASS_COLS + ("inate",):
        if col in feast_dict:
            feast_dict[col] = "18"
    feast_idx = len(sp)
    sp.add_row(str(feast_idx), feast_dict)
    spell_ids["FORCE_POWER_DEATH_FEAST"] = feast_idx

    # 2. Ajouter Cicatrice de Force I–III (miroir LS Maître d'Armes de Stigmate de Force / Fury)
    scar_icons = [
        sp.get_row(135).get_string("iconresref") or "ip_forcebar01",
        sp.get_row(136).get_string("iconresref") or "ip_forcebar02",
        sp.get_row(137).get_string("iconresref") or "ip_forcebar03",
    ]
    scar_lvls = ("1", "5", "9")
    scar_fps = ("20", "30", "40")
    scar_src_rows = (164, 165, 166)
    scar_created: list[int] = []
    for i, (src_r, slbl) in enumerate(zip(scar_src_rows, ("FORCE_POWER_FORCE_SCAR_I", "FORCE_POWER_FORCE_SCAR_II", "FORCE_POWER_FORCE_SCAR_III"))):
        base_r = sp.get_row(src_r)
        sdict = {h: base_r.get_string(h) for h in headers}
        sdict["label"] = slbl
        sdict["goodevil"] = "G"
        sdict["forbiditemmask"] = "0x0000"
        sdict["forcepoints"] = scar_fps[i]
        sdict["iconresref"] = scar_icons[i]
        sdict["pips"] = str(i + 1)
        for col in ALL_SPELL_CLASS_COLS:
            if col in sdict:
                sdict[col] = scar_lvls[i] if col == "weapmstr" else "-1"
        if i == 0:
            sdict["prerequisites"] = ""
        elif i == 1:
            sdict["prerequisites"] = str(scar_created[0])
        else:
            sdict["prerequisites"] = f"{scar_created[0]}_{scar_created[1]}"
        new_idx = len(sp)
        sp.add_row(str(new_idx), sdict)
        scar_created.append(new_idx)
        spell_ids[slbl] = new_idx

    # 2b. Ajouter le sort utilitaire ITEM_ABILITY_GAMORREAN_ADAPT (bascule 2M / 1M Gamorréen II)
    # Cloné de row 75 (ITEM_ABILITY_COMBAT_SHOT_1, category=0x1808) — JAMAIS d'un medpac (bloqué à 100% PV) !
    gam_src = sp.get_row(75)
    gam_dict = {h: gam_src.get_string(h) for h in headers}
    gam_name_ref = len(tlk)
    tlk.add("Adaptation Gamorréenne (2M / 1M)")
    gam_desc_ref = len(tlk)
    tlk.add(
        "[Mod D20-Overhaul]\nPermet à un personnage possédant Raffinement Gamorréen II d'ouvrir en posture "
        "hors combat l'établi d'amélioration portatif à tout moment (indépendamment de l'arme équipée) ou de "
        "convertir l'arme 2M / Double tenue en main droite vers son équivalent à une main (1M), et inversement."
    )
    gam_dict["label"] = "ITEM_ABILITY_GAMORREAN_ADAPT"
    gam_dict["name"] = str(gam_name_ref)
    gam_dict["spelldesc"] = str(gam_desc_ref)
    gam_dict["impactscript"] = "ov_gam_use"
    gam_dict["conjtime"] = "100"
    gam_dict["casttime"] = "200"
    gam_dict["forbiditemmask"] = "0x0000"
    gam_dict["hostilesetting"] = "0"
    gam_idx = len(sp)
    sp.add_row(str(gam_idx), gam_dict)
    spell_ids["ITEM_ABILITY_GAMORREAN_ADAPT"] = gam_idx

    # 3. Harmoniser les paliers 1/5/9 des pouvoirs de prestige & masquer les rangs IV–VI obsolètes
    prestige_schedules = [
        ((167, 168, 169), "jedimaster"),  # Écho des Liens I–III
        ((144, 145, 146), "sithlord"),    # Déchirure de la Force I–III
        ((164, 165, 166), "marauder"),    # Stigmate de Force I–III
        ((156, 157, 158), "assassin"),    # Spectre de la Force I–III (retiré à watchman)
    ]
    for r_ids, target_col in prestige_schedules:
        for idx_i, rid in enumerate(r_ids):
            srow = sp.get_row(rid)
            for col in ALL_SPELL_CLASS_COLS:
                if col in headers:
                    srow.set_string(col, ("1", "5", "9")[idx_i] if col == target_col else "-1")
            srow.set_string("pips", str(idx_i + 1))

    # Masquer rangs IV–VI (147–149 Crush Opposition IV–VI, 170–172 Inspire Followers IV–VI)
    for dead_rid in (147, 148, 149, 170, 171, 172):
        if dead_rid < len(sp):
            drow = sp.get_row(dead_rid)
            drow.set_string("prerequisites", "")
            for col in ALL_SPELL_CLASS_COLS + ("inate",):
                if col in headers:
                    drow.set_string(col, "-1")

    # Grâce du côté Lumineux (180) : lancer instantané (conjtime=0, casttime=0)
    if len(sp) > 180:
        enl = sp.get_row(180)
        enl.set_string("conjtime", "0")
        enl.set_string("casttime", "0")

    # 4. Synchroniser 100 % des lignes de Spé Pouvoirs.csv (vérification stricte d'existence de chaque label)
    by_label = {sp.get_row(i).get_string("label"): i for i in range(len(sp))}
    for _, slbls in POWER_FAMILY_SPELLS:
        for slbl in slbls:
            assert slbl in by_label, f"Label spells.2da introuvable : {slbl}"

    # Renommage TLK VF des pouvoirs de prestige et nouveaux sorts
    renamed = 0
    for slbl, fr_name in SPELL_RENAME_FR.items():
        if slbl in by_label:
            nref = len(tlk)
            tlk.add(fr_name)
            sp.get_row(by_label[slbl]).set_string("name", str(nref))
            renamed += 1

    rows = read_csv_rows(CSV_POWERS)
    desc_idx = rows[0].index("Description (mod)") if rows and "Description (mod)" in rows[0] else -1
    updated = 0
    desc_updated = 0
    matched_families: set[str] = set()
    for r in rows[1:]:
        if len(r) < 3:
            continue
        name_n = norm(r[0])
        armor_n = norm(r[1])
        pf_col = r[2].strip()
        desc_mod = r[desc_idx].strip() if desc_idx >= 0 and len(r) > desc_idx else ""

        mask = None
        for needles, m_hex in ARMOR_MASK_MAP:
            if any(n in armor_n for n in needles):
                mask = m_hex
                break

        pf_vals = [int(x) for x in re.findall(r"\d+", pf_col)]

        for needle, spell_labels in POWER_FAMILY_SPELLS:
            if needle in name_n:
                matched_families.add(needle)
                desc_ref: int | None = None
                if desc_mod:
                    desc_ref = len(tlk)
                    tlk.add(sanitize_tlk(desc_mod))
                for tier_i, slbl in enumerate(spell_labels):
                    srow = sp.get_row(by_label[slbl])
                    if mask is not None:
                        srow.set_string("forbiditemmask", mask)
                    if pf_vals:
                        cost = pf_vals[min(tier_i, len(pf_vals) - 1)]
                        srow.set_string("forcepoints", str(cost))
                    if desc_ref is not None and "spelldesc" in headers:
                        srow.set_string("spelldesc", str(desc_ref))
                        desc_updated += 1
                    updated += 1
                break

    missing_fam = {n for n, _ in POWER_FAMILY_SPELLS} - matched_families
    assert not missing_fam, f"Familles Spé Pouvoirs non matchées : {missing_fam}"

    assert_no_literal_stars(sp, "spells.2da")
    write_2da(sp, OVR_DIR / "spells.2da")
    write_tlk(tlk, OUT_DIR / "dialog.tlk")
    (OUT_DIR / "spell_ids.json").write_text(json.dumps(spell_ids, indent=2) + "\n", encoding="utf-8")
    print(
        f"[OK] spells.2da ({len(sp)} rows, {updated} pouvoirs synchronisés sur {len(matched_families)} familles, "
        f"{renamed} renommés, {desc_updated} descriptions, {len(spell_ids)} nouveaux sorts)"
    )
    return sp, spell_ids


# ============================================================================
# 6. itemcreate.2da & itemcreatemira.2da (verrous 1/10/15/20 + armes onglet 4)
# ============================================================================

def _apply_craft_csv_to_table(ic: TwoDA, include_mira_rockets: bool) -> tuple[int, int]:
    by_label = {ic.get_row(i).get_string("label").lower(): i for i in range(len(ic))}
    rows = read_csv_rows(CSV_CRAFT)
    mod_idx = rows[0].index("Changement (mod)") if rows and "Changement (mod)" in rows[0] else 9
    updated = 0
    added = 0
    seen_new: set[str] = set()
    for r in rows[1:]:
        if len(r) < 6:
            continue
        resref = r[0].strip().lower()
        if not resref or resref.startswith("—"):
            continue
        if "_c0" in resref or "_c1" in resref:
            continue
        station = r[2].strip().lower()
        is_mira_only = "mira" in station
        if is_mira_only and not include_mira_rockets:
            continue

        lvl_txt = r[mod_idx].strip() if len(r) > mod_idx else ""
        m_lvl = re.search(r"Niv\.\s*(\d+)", lvl_txt, re.I)
        lvl = int(m_lvl.group(1)) if m_lvl else 0
        if lvl == 1:
            lvl = 0

        if resref in by_label:
            ic.get_row(by_label[resref]).set_string("level", str(lvl))
            updated += 1
        elif resref not in seen_new and resref.startswith("w_") and not is_mira_only:
            seen_new.add(resref)
            skill_txt = r[5].strip()
            skill_val = skill_txt if skill_txt.isdigit() else "4"
            ic.add_row(str(len(ic)), {
                "label": resref,
                "skill": skill_val,
                "group": "4",      # Onglet 4 : Armes & Utilitaires (PAS 0 = Armures !)
                "level": str(lvl),
                "align": "0",
                "base_skill": "5", # Réparation
                "dunno": "0",
                "overridetag": "",
            })
            added += 1
    return updated, added


def build_itemcreate() -> TwoDA:
    ic = read_2da(REF_2DA / "itemcreate_tslrcm.2da")
    updated, added = _apply_craft_csv_to_table(ic, include_mira_rockets=False)
    assert_no_literal_stars(ic, "itemcreate.2da")
    write_2da(ic, OVR_DIR / "itemcreate.2da")
    print(f"[OK] itemcreate.2da ({len(ic)} rows: {updated} paliers mis à jour, {added} armes base onglet 4 ajoutées)")
    return ic


def build_itemcreatemira() -> TwoDA:
    icm = read_2da(REF_2DA / "itemcreatemira_tslrcm.2da")
    updated, added = _apply_craft_csv_to_table(icm, include_mira_rockets=True)
    assert_no_literal_stars(icm, "itemcreatemira.2da")
    write_2da(icm, OVR_DIR / "itemcreatemira.2da")
    print(f"[OK] itemcreatemira.2da ({len(icm)} rows: {updated} paliers dont roquettes Mira, {added} armes base ajoutées)")
    return icm


# ============================================================================
# 7. forceshields.2da (paliers ×1,25 / ×2 / ×2,5 / ×3 / ×3,75 pour boucliers)
# ============================================================================

def build_forceshields() -> TwoDA:
    """Duplique les 21 boucliers vanilla en 5 blocs (+21 chacun) pour Armure Tactique II–III
    et Affranchi de la Force II (+25 %) :
      - rows   0..20 : base (×1.00)
      - rows  21..41 : Affranchi II (+25 % -> ×1.25)
      - rows  42..62 : Armure Tactique II (×2.00)
      - rows  63..83 : Armure Tactique II + Affranchi II (×2.50)
      - rows  84..104 : Armure Tactique III (×3.00)
      - rows 105..125 : Armure Tactique III + Affranchi II (×3.75)"""
    fs = read_2da(REF_2DA / "forceshields_tslrcm.2da")
    base_len = len(fs)
    assert base_len == 21, f"forceshields_tslrcm.2da attendu 21 lignes, trouvé {base_len}"
    headers = fs.get_headers()
    base_rows = [{h: fs.get_row(i).get_string(h) for h in headers} for i in range(base_len)]

    tiers = [
        ("OV_UNB2_",       1.25),
        ("OV_TACT2_",      2.00),
        ("OV_TACT2_UNB2_", 2.50),
        ("OV_TACT3_",      3.00),
        ("OV_TACT3_UNB2_", 3.75),
    ]
    for prefix, mult in tiers:
        for base_d in base_rows:
            d = dict(base_d)
            d["label"] = prefix + base_d["label"]
            amt = int(base_d["amount"]) if base_d["amount"].isdigit() else 0
            d["amount"] = str(int(round(amt * mult)))
            fs.add_row(str(len(fs)), d)

    assert_no_literal_stars(fs, "forceshields.2da")
    write_2da(fs, OVR_DIR / "forceshields.2da")
    print(f"[OK] forceshields.2da ({len(fs)} rows: 21 base + 5 blocs ×1.25/×2/×2.5/×3/×3.75)")
    return fs


# ============================================================================
# 8. iprp_resistcost.2da (paliers RD exacts +2/-, +3/-, +4/-, +6/-, +12/-)
# ============================================================================

def build_iprp_resistcost() -> TwoDA:
    """Étend iprp_resistcost.2da (lignes vanilla 0..6 intactes) avec les paliers exacts :
      - row  7 : Resist_2/-  (amount=2)
      - row  8 : Resist_3/-  (amount=3)
      - row  9 : Resist_4/-  (amount=4, bêtes Mid)
      - row 10 : Resist_6/-  (amount=6, bêtes Late)
      - row 11 : Resist_12/- (amount=12, armures élémentaires)"""
    rc = read_2da(REF_2DA / "iprp_resistcost_tslrcm.2da")
    tlk = read_tlk(OUT_DIR / "dialog.tlk")
    extra_rows = [
        ("Resist_2/-",  "2",  "0.3",  "Résistance 2/-"),
        ("Resist_3/-",  "3",  "0.45", "Résistance 3/-"),
        ("Resist_4/-",  "4",  "0.6",  "Résistance 4/-"),
        ("Resist_6/-",  "6",  "0.9",  "Résistance 6/-"),
        ("Resist_12/-", "12", "1.6",  "Résistance 12/-"),
    ]
    for lbl, amt, cost, fr_name in extra_rows:
        nref = len(tlk)
        tlk.add(fr_name)
        rc.add_row(str(len(rc)), {
            "name": str(nref),
            "label": lbl,
            "amount": amt,
            "cost": cost,
        })
    assert_no_literal_stars(rc, "iprp_resistcost.2da")
    write_2da(rc, OVR_DIR / "iprp_resistcost.2da")
    write_tlk(tlk, OUT_DIR / "dialog.tlk")
    print(f"[OK] iprp_resistcost.2da ({len(rc)} rows: +2/-, +3/-, +4/-, +6/-, +12/- ajoutés)")
    return rc


# ============================================================================
# 9. autobalance.2da (calibrage boss Set_5)
# ============================================================================

def build_autobalance() -> TwoDA:
    ab = read_2da(REF_2DA / "autobalance_tslrcm.2da")
    r5 = ab.get_row(5)
    r5.set_string("vpmult", "0.95")
    r5.set_string("damagemult", "0.155")
    assert_no_literal_stars(ab, "autobalance.2da")
    write_2da(ab, OVR_DIR / "autobalance.2da")
    print("[OK] autobalance.2da (Set_5 vpmult=0.95, damagemult=0.155)")
    return ab


def main() -> None:
    OVR_DIR.mkdir(parents=True, exist_ok=True)
    print(f"=== Build Jalon 1 (.2da + dialog.tlk) -> {OUT_DIR} ===")
    build_featgain()
    build_classpowergain()
    _, feat_ids = build_feats_and_tlk()
    build_baseitems(feat_ids)
    build_spells()
    build_itemcreate()
    build_itemcreatemira()
    build_forceshields()
    build_iprp_resistcost()
    build_autobalance()
    print("=== Jalon 1 BUILD OK ===")


if __name__ == "__main__":
    main()
