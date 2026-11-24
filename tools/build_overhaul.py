#!/usr/bin/env python3
"""KotOR 2 Overhaul — Jalon 1 : Générateur des tables .2da + dialog.tlk.

Génère dans `mods/overhaul/` (sans jamais modifier le jeu directement) :
  - `dialog.tlk` (copie du backup FR + entrées ajoutées pour tous les nouveaux dons)
  - `Override/feat.2da` (245 lignes TSLRCM intactes + 73 nouveaux dons, 29 supprimés masqués)
  - `Override/featgain.2da` (budgets Niv. 30 : 22 / 18 / 15 dons)
  - `Override/classpowergain.2da` (budgets Niv. 30 : 12 / 16 / 24 pouvoirs)
  - `Override/baseitems.2da` (armes d20, armures CA/DEX, variantes 1M Gamoréen II)
  - `Override/spells.2da` (forbiditemmask par armure + coûts PF évolutifs)
  - `Override/itemcreate.2da` (verrous level 1/10/15/20 + armes base + 24 upgrades combinées)
  - `Override/autobalance.2da` (calibrage boss Set_5)
  - `feat_ids.json` & `baseitem_1m_map.json` (index pour Jalons 2 & 3)

Règles strictes (README.md §2–§3) :
  - Cellules vides `pykotor.TwoDA` = `""` (JAMAIS `"****"`).
  - Base TSLRCM depuis `_reference/2da/*_tslrcm.2da` et `mods/04-engine-tests/backup/dialog.tlk.bak`.
  - Aucune ligne vanilla supprimée dans `feat.2da` (compatibilité sauvegardes).
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
CSV_WEAPONS = ROOT / "Kotor 2 - rééquilibrage - Armes.csv"
CSV_ARMORS = ROOT / "Kotor 2 - rééquilibrage - Armures.csv"
CSV_POWERS = ROOT / "Kotor 2 - rééquilibrage - Spé Pouvoirs.csv"
CSV_CRAFT = ROOT / "Kotor 2 - rééquilibrage - Craft.csv"


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

def _distribute_points(total_15: int, total_30: int, n_rows: int = 50) -> list[int]:
    """Répartit `total_15` points sur les niveaux 1..15 et `total_30 - total_15` sur 16..30
    (avec 1 point garanti au niv. 1, puis cadence régulière)."""
    vals = [0] * n_rows
    # Niveaux 1..15 (indices 0..14)
    vals[0] = 1
    rem15 = total_15 - 1
    for k in range(rem15):
        # Répartition uniforme sur indices 1..14
        idx = 1 + int(round((k + 0.5) * 14 / rem15)) - 1
        idx = max(1, min(14, idx))
        while vals[idx] > 0 and idx < 14:
            idx += 1
        vals[idx] += 1
    # Niveaux 16..30 (indices 15..29)
    rem30 = total_30 - total_15
    for k in range(rem30):
        idx = 15 + int(round((k + 0.5) * 15 / rem30)) - 1
        idx = max(15, min(29, idx))
        while vals[idx] > 0 and idx < 29:
            idx += 1
        vals[idx] += 1
    # Niveaux 31..50 (indices 30..49) : rythme standard (1 tous les 2 niveaux)
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
    plan = {
        "jgd": (6, 12),
        "jwm": (6, 12),
        "sma": (6, 12),
        "jsn": (8, 16),
        "jwa": (8, 16),
        "sas": (8, 16),
        "jcn": (12, 24),
        "jma": (12, 24),
        "sld": (12, 24),
    }
    for col, (t15, t30) in plan.items():
        if col in pg.get_headers():
            dist = _distribute_points(t15, t30, n)
            for i in range(n):
                pg.get_row(i).set_string(col, str(dist[i]))
    assert_no_literal_stars(pg, "classpowergain.2da")
    write_2da(pg, OVR_DIR / "classpowergain.2da")
    return pg


# ============================================================================
# 3. feat.2da + dialog.tlk (245 lignes TSLRCM intactes + 73 nouveaux dons)
# ============================================================================

ALL_LIST_COLS = [
    "scd_list", "sol_list", "sct_list",
    "jcn_list", "jgd_list", "jsn_list",
    "sas_list", "sld_list", "sma_list",
    "jwa_list", "jma_list", "jwm_list",
    "tec_list", "drx_list", "drc_list",
]
ALL_GRANT_COLS = [c.replace("_list", "_granted") for c in ALL_LIST_COLS] + [
    "jcn_pc_granted", "jgd_pc_granted", "jsn_pc_granted"
]

MARTIAL_PRESTIGE = ["jwm_list", "sma_list"]
HYBRID_PRESTIGE = ["jwa_list", "sas_list"]
CASTER_PRESTIGE = ["jma_list", "sld_list"]
ALL_JEDI_BASE = ["jgd_list", "jsn_list", "jcn_list"]
ALL_NON_MAGE = [
    "jgd_list", "jsn_list", "jwm_list", "sma_list", "jwa_list", "sas_list",
    "sol_list", "sct_list", "scd_list", "tec_list", "drc_list", "drx_list",
]


def _parse_min_level(prereq_txt: str) -> int:
    m = re.search(r"Niv\.\s*(\d+)\+", prereq_txt, re.I)
    return int(m.group(1)) if m else 0


def _allowed_classes_for_new_feat(label: str, cat: str, prereq_txt: str) -> tuple[list[str], int]:
    """Détermine les colonnes `*_list` autorisées et `minattackbonus` selon decisions_finales.md §6."""
    lbl = label.upper()
    c_n = norm(cat)
    p_n = norm(prereq_txt)
    rank = 3 if lbl.endswith("_3") else (2 if lbl.endswith("_2") else 1)

    # Affranchi de la Force (pouvoir passif exclusif Jedi protecteur)
    if "UNBOUND_FORCE" in lbl:
        return ["jwa_list"], 0

    # Spécialisations de caractéristique : ouvertes à toutes les classes (paliers Niv. 1 / 8 / 15)
    if "caracteristique" in c_n:
        return ALL_LIST_COLS, 0

    # Postures (Styles de combat)
    if "styles de combat" in c_n:
        if rank <= 2 or "DUEL" in lbl:
            return ALL_LIST_COLS, 0
        # R3 Ambidextrie / Arme Lourde / Haute cadence : Tous sauf Mages
        return ALL_NON_MAGE, 0

    # Métamagie
    if "metamagie" in c_n:
        if "PROLONG" in lbl or rank == 1:
            return ALL_JEDI_BASE + MARTIAL_PRESTIGE + HYBRID_PRESTIGE + CASTER_PRESTIGE, 0
        if rank == 2:
            return ["jcn_list"] + CASTER_PRESTIGE, 0
        return CASTER_PRESTIGE, 0

    # Spécialisations d'arme (8 familles)
    if "specialisations" in c_n and "arme" in c_n or "spec_" in lbl.lower():
        if rank == 1:
            return ALL_LIST_COLS, 0
        if rank == 2:
            return ALL_NON_MAGE, 0
        # R3 : Maître d'Armes / Maraudeur + non-Jedi (SOL/SCT/SCD/TEC/DRC via minattackbonus=15)
        return MARTIAL_PRESTIGE + ["sol_list", "sct_list", "scd_list", "tec_list", "drc_list"], 0

    # Armures (Juggernaut, Armure Tactique, Esquive Ballistique)
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
            return HYBRID_PRESTIGE + ["sct_list", "scd_list", "tec_list"], 0
        if "LIGHT" in lbl:  # Esquive Ballistique
            if rank == 2:
                return ["jgd_list", "jsn_list", "jwm_list", "sma_list", "jwa_list", "sas_list", "sol_list", "sct_list", "scd_list"], 0
            return MARTIAL_PRESTIGE + HYBRID_PRESTIGE + ["sol_list", "sct_list", "scd_list"], 0

    # Fallback sûr
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


def build_feats_and_tlk() -> tuple[TwoDA, dict[str, int]]:
    feat = read_2da(REF_2DA / "feat_tslrcm.2da")
    tlk = read_tlk(BASE_TLK)
    rows = read_csv_rows(CSV_FEATS)

    # Template de ligne propre (cellules vides = "", *_list = "4" = NON DISPONIBLE par défaut, allclassescanuse = "0")
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

    # 1. Masquer les 28 dons supprimés SANS supprimer leurs lignes (compatibilité sauvegardes !)
    # En KotOR 2 feat.2da : *_list = "4" + allclassescanuse = "0" masque complètement le don.
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
            tlk.add(r[desc_col_idx].strip())
            feat.get_row(fid).set_string("description", str(desc_ref))
            vanilla_desc_updated += 1

    # 2. Ajouter les 73 nouveaux dons à partir de l'index 245+
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
        tlk.add(nom)
        desc_ref = len(tlk)
        tlk.add(desc_mod)

        entry = dict(tmpl)
        entry["label"] = label
        entry["name"] = str(name_ref)
        entry["description"] = str(desc_ref)
        entry["icon"] = _pick_real_icon(label, cat)

        min_lvl = _parse_min_level(prereq)
        if min_lvl > 1:
            entry["mincharlevel"] = str(min_lvl)

        # Chaînage exact vanilla KotOR 2 :
        #   Rang I  : pre1="", pre2="", succ=Rang II
        #   Rang II : pre1=Rang I, pre2="", succ=Rang III
        #   Rang III: pre1=Rang I, pre2=Rang II, succ="" (obligatoire pour l'affichage UI!)
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

        allowed_cols, min_bab = _allowed_classes_for_new_feat(label, cat, prereq)
        for c in allowed_cols:
            if c in entry:
                entry[c] = "1"
        if min_bab > 0:
            entry["minattackbonus"] = str(min_bab)

        feat.add_row(str(fid), entry)

    assert_no_literal_stars(feat, "feat.2da")
    write_2da(feat, OVR_DIR / "feat.2da")
    write_tlk(tlk, OUT_DIR / "dialog.tlk")
    (OUT_DIR / "feat_ids.json").write_text(json.dumps(feat_ids, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"[OK] feat.2da ({len(feat)} rows: {hidden_count} masqués, {len(new_rows_data)} ajoutés) + dialog.tlk ({len(tlk)} entrées)")
    return feat, feat_ids


# ============================================================================
# 4. baseitems.2da (Armes.csv + Armures.csv + Variantes 1M Gamoréen II)
# ============================================================================

ARMOR_BASEITEM_MAP = {
    "Armor_Class_4": (6, 10),
    "Armor_Class_5": (7, 8),
    "Armor_Class_6": (5, 6),
    "Armor_Class_7": (6, 4),
    "Armor_Class_8": (7, 2),
    "Armor_Class_9": (8, 0),
    "Armor_Armd_Flight_Suit": (6, 9),
    "Armor_Zeison_Sha": (6, 10),
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
    "Disruptor_Rifle",
    "Sonic_Rifle",
    "Ion_Rifle",
    "Bowcaster",
]


WEAPON_CSV_TO_BASEITEM = {
    "blaster carbines": "Blaster_Carbine",
    "blaster rifles": "Blaster_Rifle",
    "bowcasters": "Bowcaster",
    "repeating blasters": "Repeating_Blaster",
    "lourde repeating blasters": "Heavy_Repeating_Blaster",
    "disruptor rifles": "Disruptor_Rifle",
    "ion rifles": "Ion_Rifle",
    "sonic rifles": "Sonic_Rifle",
    "blaster pistols": "Blaster_Pistol",
    "lourde blasters": "Heavy_Blaster",
    "hold out blasters": "Hold_Out_Blaster",
    "disruptor pistols": "Disruptor_Pistol",
    "ion blasters": "Ion_Blaster",
    "sonic pistols": "Sonic_Pistol",
    "stun batons": "Stun_Baton",
    "short swords (craftable)": "Short_Sword",
    "vibroblades": "Vibro_Blade",
    "long swords (craftable)": "Long_Sword",
    "gamorrean battleaxes": "Gamorrean_Battleaxe",
    "vibroswords (craftable)": "Vibro_Sword",
    "quarterstaffs": "Quarter_Staff",
    "force pikes": "Force_Pike",
    "double-bladed sword": "Double_Bladed_Sword",
    "vibro double-blades (craftable)": "Vibro_Double_Blade",
    "wookie warblades": "Wookiee_Warblade",
    "short light saber": "Short_Lightsaber",
    "light saber": "Lightsaber",
    "double light saber": "Double_Bladed_Lightsaber",
}


def build_baseitems(feat_ids: dict[str, int]) -> TwoDA:
    bi = read_2da(REF_2DA / "baseitems_tslrcm.2da")
    by_label = {bi.get_row(i).get_string("label"): i for i in range(len(bi))}

    # 1. Armures : CA base & DEX max actés (22/11)
    arm_updated = 0
    for lbl, (ac, max_dex) in ARMOR_BASEITEM_MAP.items():
        if lbl in by_label:
            r = bi.get_row(by_label[lbl])
            r.set_string("baseac", str(ac))
            r.set_string("dexbonus", str(max_dex))
            arm_updated += 1

    # 2. Armes : dégâts d20 & critique depuis Armes.csv (mapping exact 1-à-1)
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

    # 3. Variantes miroirs 1M pour Gamoréen II (validé T1 + T2)
    gam2_id = feat_ids.get("MOD_GAMORREAN_2") or feat_ids.get("MOD_GAMORRAN_2")
    assert gam2_id is not None, f"MOD_GAMORREAN_2 introuvable dans {list(feat_ids.keys())[:10]}"
    mirror_map: dict[str, int] = {}
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
        new_dict["weaponwield"] = "5" if is_ranged else "2"
        new_dict["weaponsize"] = "3"
        new_dict["reqfeat0"] = str(gam2_id)
        new_idx = len(bi)
        bi.add_row(str(new_idx), new_dict)
        mirror_map[lbl] = new_idx

    # 4. Baseitem dédié pour la Torche à plasma (dégâts vanilla 1d1 + 1d6 Feu de l'UTI, sans toucher aux Matraques 1d8)
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
# 5. spells.2da (forbiditemmask + coûts PF évolutifs depuis Spé Pouvoirs.csv)
# ============================================================================

ARMOR_MASK_MAP = [
    (("armure interdite", "interdite", "robe"), "0x003f"),
    (("armure legere", "legere"), "0x003c"),
    (("armure moyenne", "intermediaire", "moyenne"), "0x0030"),
    (("armure lourde", "lourde"), "0x0000"),
]


# Mapping explicite ligne Spé Pouvoirs.csv (clé VO normalisée) -> [L1, L2, L3] labels exacts dans spells.2da
POWER_FAMILY_SPELLS: list[tuple[str, list[str]]] = [
    ("force aura",         ["FORCE_POWER_FORCE_AURA", "FORCE_POWER_FORCE_SHIELD", "FORCE_POWER_FORCE_ARMOR"]),
    ("force barrier",      ["FORCE_POWER_FORCE_BARRIER", "FORCE_POWER_IMPROVED_FORCE_BARRIER", "FORCE_POWER_MASTER_FORCE_BARRIER"]),
    ("force valor",        ["FORCE_POWER_FORCE_VALOR", "FORCE_POWER_KNIGHT_VALOR", "FORCE_POWER_MASTER_VALOR"]),
    ("cure / heal",        ["FORCE_POWER_CURE", "FORCE_POWER_HEAL", "FORCE_POWER_MASTER_HEAL"]),
    ("revitalize",         ["FORCE_POWER_REVITALIZE", "FORCE_POWER_IMPROVED_REVITALIZE", "FORCE_POWER_MASTER_REVITALIZE"]),
    ("stun / stasis",      ["FORCE_POWER_STUN", "FORCE_POWER_STASIS", "FORCE_POWER_STASIS_FIELD"]),
    ("stun droid",         ["FORCE_POWER_STUN_DROID", "FORCE_POWER_DISABLE_DROID", "FORCE_POWER_DESTROY_DROID"]),
    ("inspire followers",  ["FORCE_POWER_INSPIRE_FOLLOWERS_I", "FORCE_POWER_INSPIRE_FOLLOWERS_II", "FORCE_POWER_INSPIRE_FOLLOWERS_III"]),
    ("force enlightenment",["FORCE_POWER_FORCE_ENLIGHTENMENT"]),
    ("burst of speed",     ["FORCE_POWER_SPEED_BURST", "FORCE_POWER_KNIGHT_SPEED", "FORCE_POWER_MASTER_SPEED"]),
    ("energy resistance",  ["FORCE_POWER_ENERGY_RESISTANCE", "FORCE_POWER_IMPROVED_ENERGY_RESISTANCE", "FORCE_POWER_MASTER_ENERGY_RESISTANCE"]),
    ("force resistance",   ["FORCE_POWER_FORCE_RESISTANCE", "FORCE_POWER_FORCE_IMMUNITY"]),
    ("force suppression",  ["FORCE_POWER_SUPPRESS_FORCE", "FORCE_POWER_FORCE_BREACH"]),
    ("battle meditation",  ["FORCE_POWER_BATTLE_MEDITATION", "FORCE_POWER_IMPROVED_BATTLE_MEDITATION", "FORCE_POWER_MASTER_BATTLE_MEDITATION"]),
    ("force push",         ["FORCE_POWER_FORCE_PUSH", "FORCE_POWER_FORCE_WHIRLWIND", "FORCE_POWER_FORCE_WAVE"]),
    ("throw lightsaber",   ["FORCE_POWER_LIGHT_SABER_THROW", "FORCE_POWER_LIGHT_SABER_THROW_ADVANCED"]),
    ("affect mind",        ["FORCE_POWER_AFFECT_MIND", "FORCE_POWER_DOMINATE_MIND"]),
    ("force confusion",    ["FORCE_POWER_CONFUSION"]),
    ("beast trick",        ["FORCE_POWER_BEAST_TRICK", "FORCE_POWER_BEAST_CONFUSION"]),
    ("breath control",     ["FORCE_POWER_BREATH_CONTROL"]),
    ("force camouflage",   ["FORCE_POWER_FORCE_CAMOFLAGE", "FORCE_POWER_IMPROVED_FORCE_CAMOFLAGE", "FORCE_POWER_MASTER_FORCE_CAMOFLAGE"]),
    ("force sight",        ["FORCE_POWER_FORCE_SIGHT"]),
    ("drain force",        ["FORCE_POWER_DRAIN_FORCE", "FORCE_POWER_IMPROVED_DRAIN_FORCE", "FORCE_POWER_MASTER_DRAIN_FORCE"]),
    ("drain life",         ["FORCE_POWER_DRAIN_LIFE", "FORCE_POWER_DEATH_FIELD"]),
    ("fear / horror",      ["FORCE_POWER_FEAR", "FORCE_POWER_HORROR", "FORCE_POWER_INSANITY"]),
    ("force scream",       ["FORCE_POWER_FORCE_SCREAM", "FORCE_POWER_IMPROVED_FORCE_SCREAM", "FORCE_POWER_MASTER_FORCE_SCREAM"]),
    ("shock / force",      ["FORCE_POWER_SHOCK", "FORCE_POWER_FORCE_LIGHTNING", "FORCE_POWER_FORCE_STORM"]),
    ("slow / affliction",  ["FORCE_POWER_SLOW", "FORCE_POWER_AFFLICTION", "FORCE_POWER_PLAGUE"]),
    ("wound / choke",      ["FORCE_POWER_WOUND", "FORCE_POWER_CHOKE", "FORCE_POWER_KILL"]),
    ("crush opposition",   ["FORCE_POWER_CRUSH_OPPOSITION_I", "FORCE_POWER_CRUSH_OPPOSITION_II", "FORCE_POWER_CRUSH_OPPOSITION_III"]),
    ("force crush",        ["FORCE_POWER_FORCE_CRUSH"]),
    ("fury / improved",    ["FORCE_POWER_FURY", "FORCE_POWER_IMPROVED_FURY", "FORCE_POWER_MASTER_FURY"]),
]


def build_spells() -> TwoDA:
    sp = read_2da(REF_2DA / "spells_tslrcm.2da")
    tlk = read_tlk(OUT_DIR / "dialog.tlk")
    by_label = {sp.get_row(i).get_string("label"): i for i in range(len(sp))}
    rows = read_csv_rows(CSV_POWERS)
    desc_idx = rows[0].index("Description (mod)") if rows and "Description (mod)" in rows[0] else -1
    updated = 0
    desc_updated = 0
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
                desc_ref: int | None = None
                if desc_mod:
                    desc_ref = len(tlk)
                    tlk.add(desc_mod)
                for tier_i, slbl in enumerate(spell_labels):
                    if slbl not in by_label:
                        continue
                    srow = sp.get_row(by_label[slbl])
                    if mask is not None:
                        srow.set_string("forbiditemmask", mask)
                    if pf_vals:
                        cost = pf_vals[min(tier_i, len(pf_vals) - 1)]
                        srow.set_string("forcepoints", str(cost))
                    if desc_ref is not None and "spelldesc" in sp.get_headers():
                        srow.set_string("spelldesc", str(desc_ref))
                        desc_updated += 1
                    updated += 1
                break

    assert_no_literal_stars(sp, "spells.2da")
    write_2da(sp, OVR_DIR / "spells.2da")
    write_tlk(tlk, OUT_DIR / "dialog.tlk")
    print(f"[OK] spells.2da ({len(sp)} rows, {updated} pouvoirs synchronisés, {desc_updated} descriptions dans dialog.tlk)")
    return sp


# ============================================================================
# 6. itemcreate.2da (verrous level 1/10/15/20 depuis Craft.csv)
# ============================================================================

def build_itemcreate() -> TwoDA:
    ic = read_2da(REF_2DA / "itemcreate_tslrcm.2da")
    by_label = {ic.get_row(i).get_string("label").lower(): i for i in range(len(ic))}
    rows = read_csv_rows(CSV_CRAFT)
    updated = 0
    added = 0
    seen_new: set[str] = set()
    for r in rows[1:]:
        if len(r) < 6:
            continue
        resref = r[0].strip().lower()
        if not resref or resref.startswith("—"):
            continue
        # Éviter le doublon c01..c12 (on garde u_a_over_19..30 / u_a_unde_19..30)
        if "_c0" in resref or "_c1" in resref:
            continue
        lvl_txt = r[4].strip() if len(r) > 4 else ""
        m_lvl = re.search(r"(\d+)", lvl_txt)
        lvl = int(m_lvl.group(1)) if m_lvl else 0
        if lvl == 1:
            lvl = 0  # Niv. 1+ = disponible dès le début (0 dans itemcreate.2da)

        if resref in by_label:
            ic.get_row(by_label[resref]).set_string("level", str(lvl))
            updated += 1
        elif resref not in seen_new and (resref.startswith("u_a_over_") or resref.startswith("u_a_unde_") or resref.startswith("w_")):
            seen_new.add(resref)
            skill_val = "10" if lvl == 0 else ("16" if lvl <= 10 else ("22" if lvl <= 15 else "26"))
            grp = "2" if resref.startswith("u_a_") else "0"
            ic.add_row(str(len(ic)), {
                "label": resref,
                "skill": skill_val,
                "group": grp,
                "level": str(lvl),
                "align": "0",
                "base_skill": "5",
                "dunno": "0",
                "overridetag": "",
            })
            added += 1

    assert_no_literal_stars(ic, "itemcreate.2da")
    write_2da(ic, OVR_DIR / "itemcreate.2da")
    print(f"[OK] itemcreate.2da ({len(ic)} rows: {updated} paliers mis à jour, {added} recettes ajoutées)")
    return ic


# ============================================================================
# 7. autobalance.2da (calibrage boss Set_5)
# ============================================================================

def build_autobalance() -> TwoDA:
    ab = read_2da(REF_2DA / "autobalance_tslrcm.2da")
    # Set_5 (ligne 5) : vpmult 0.80 -> 0.95 (rehausse PV Boss Mid/Late), damagemult 0.175 -> 0.155
    r5 = ab.get_row(5)
    r5.set_string("vpmult", "0.95")
    r5.set_string("damagemult", "0.155")
    assert_no_literal_stars(ab, "autobalance.2da")
    write_2da(ab, OVR_DIR / "autobalance.2da")
    print("[OK] autobalance.2da (Set_5 vpmult=0.95, damagemult=0.155)")
    return ab


def main() -> None:
    OVR_DIR.mkdir(parents=True, exist_ok=True)
    print(f"=== Build Jalon 1 -> {OUT_DIR} ===")
    build_featgain()
    build_classpowergain()
    _, feat_ids = build_feats_and_tlk()
    build_baseitems(feat_ids)
    build_spells()
    build_itemcreate()
    build_autobalance()
    print("=== Jalon 1 BUILD OK (0 erreur, 0 '****' littéral) ===")


if __name__ == "__main__":
    main()
