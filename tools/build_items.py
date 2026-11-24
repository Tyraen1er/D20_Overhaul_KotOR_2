#!/usr/bin/env python3
"""KotOR 2 Overhaul — Jalon 2 : Générateur des items .uti.

Lit directement nos CSV utilisateur + les ressources TSLRCM/vanilla du jeu et génère
dans `mods/overhaul/Override/*.uti` :
  1. Tous les équipements modifiés des 6 CSV (Casques, Implants, Gants, Ceintures,
     Brassards, Armures items) : plafonds stats primaires (+1/+2/+3), ajouts lore 6 stats,
     et plafonds secondaires (RD, Immunités %, Dégâts gants, Saves, CA, Atq).
  2. Verrouillage `upgrade_level` des armures intermédiaires (= 6) pour réserver
     les 24 upgrades combinées intermédiaires (`u_a_over_19..30`, `u_a_unde_19..30`).
  3. Génération des 24 `.uti` d'upgrades combinées intermédiaires (depuis `Améliorations.csv`).
  4. Génération des variantes `.uti` 1M Gamoréen II pour les armes 2M/Doubles de base
     (utilisant `mods/overhaul/baseitem_1m_map.json` issu du Jalon 1).
"""

from __future__ import annotations

import csv
import json
import re
import unicodedata
from pathlib import Path

from pykotor.common.language import Gender, Language, LocalizedString
from pykotor.extract.installation import Installation
from pykotor.resource.generics.uti import UTIProperty, read_uti, write_uti
from pykotor.resource.type import ResourceType

ROOT = Path(__file__).resolve().parent.parent
GAME_PATH = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Knights of the Old Republic II")
OVR_DIR = ROOT / "mods" / "overhaul" / "Override"
MIRROR_MAP_FILE = ROOT / "mods" / "overhaul" / "baseitem_1m_map.json"

GEAR_CSVS = [
    "Kotor 2 - rééquilibrage - Casques.csv",
    "Kotor 2 - rééquilibrage - Implants.csv",
    "Kotor 2 - rééquilibrage - Gants.csv",
    "Kotor 2 - rééquilibrage - Ceintures.csv",
    "Kotor 2 - rééquilibrage - Brassards.csv",
    "Kotor 2 - rééquilibrage - Armures items.csv",
]
CSV_UPGRADES = ROOT / "Kotor 2 - rééquilibrage - Améliorations.csv"

STAT_TO_SUB = {"FOR": 0, "DEX": 1, "CON": 2, "INT": 3, "SAG": 4, "CHA": 5}
DMG_COST_MAP = {
    "1": 1, "2": 2, "3": 3, "4": 4, "5": 5,
    "1d2": 14, "1d3": 14, "1d4": 6, "1d6": 7, "1d8": 8, "1d10": 9,
    "2d6": 10, "1d12": 11, "2d8": 12, "2d10": 13,
}
DMG_TYPE_SUB = {
    "slashing": 2, "cold": 5, "electrical": 7, "fire": 8,
    "sonic": 10, "ion": 11, "energy": 12,
}
ABILITY_EN_SUB = {
    "strength": 0, "dexterity": 1, "constitution": 2,
    "intelligence": 3, "wisdom": 4, "charisma": 5,
}
ONHIT_FR_SUB = {
    "etourdissement": 1, "paralysie": 2, "horreur": 4, "lenteur": 5,
}
IMM_COST_MAP = {5: 1, 10: 2, 15: 8, 20: 9, 25: 3, 30: 10}
# iprp_resistcost.2da : 1=5/-, 2=10/-, 3=15/- (paliers natifs moteur)
RD_TO_COST = {2: 1, 3: 1, 5: 1, 10: 2, 12: 2, 15: 3}

# Variantes 1M Gamoréen II : resref vanilla -> (baseitem_label_2m, resref_1m)
GAMORREAN_WEAPONS = [
    ("w_melee_04",    "Quarter_Staff",            "m_w_qtrstf_1m"),
    ("w_melee_07",    "Double_Bladed_Sword",      "m_w_dblswd_1m"),
    ("w_melee_12",    "Vibro_Double_Blade",       "m_w_vbrdbl_1m"),
    ("g_w_dblsbr001", "Double_Bladed_Lightsaber", "m_w_dblsbr_1m"),
    ("w_brifle_01",   "Blaster_Rifle",            "m_w_blsrfl_1m"),
    ("w_brifle_05",   "Blaster_Carbine",          "m_w_blscrb_1m"),
    ("w_brifle_03",   "Repeating_Blaster",        "m_w_rptbls_1m"),
    ("w_brifle_13",   "Heavy_Repeating_Blaster",  "m_w_hvyrpt_1m"),
    ("w_brifle_08",   "Sonic_Rifle",              "m_w_sncrfl_1m"),
    ("w_brifle_17",   "Bowcaster",                "m_w_bowcst_1m"),
]


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.replace("'", " ").replace("\u2019", " ")
    return re.sub(r"\s+", " ", s.lower()).strip()


def set_uti_desc(uti, desc_txt: str) -> None:
    """Injecte une description VF (depuis `Description (mod)` des CSV) dans un UTI."""
    if not desc_txt:
        return
    ls = LocalizedString.from_invalid()
    ls.set_data(Language.FRENCH, Gender.MALE, desc_txt)
    ls.set_data(Language.ENGLISH, Gender.MALE, desc_txt)
    uti.description = ls


def make_prop(prop_id: int, subtype: int, cost_table: int, cost_value: int) -> UTIProperty:
    p = UTIProperty()
    p.property_name = prop_id
    p.subtype = subtype
    p.cost_table = cost_table
    p.cost_value = cost_value
    p.param1 = 255
    p.param1_value = 0
    p.chance_appear = 100
    return p


def _parse_stat_pairs(txt: str) -> dict[str, int]:
    out: dict[str, int] = {}
    for k, v in re.findall(r"\b(FOR|DEX|CON|INT|SAG|CHA)\s*([+-]\d+)", txt):
        out[k] = int(v)
    return out


def apply_mod_to_uti(uti, mod_txt: str) -> bool:
    """Applique les directives de `Changement (mod)` sur un objet UTI. Retourne True si modifié."""
    changed = False
    if not mod_txt:
        return False

    # Découper les directives multiples séparées par ';'
    segments = [seg.strip() for seg in mod_txt.split(";") if seg.strip()]
    for seg in segments:
        seg_n = norm(seg)

        # 1. Stats primaires : remplacement "→ ..." ou "Ajout : ..."
        if "→" in seg and any(k in seg for k in STAT_TO_SUB):
            rhs = seg.split("→", 1)[1]
            if "+1 aux 6 caracs" in rhs:
                new_stats = {k: 1 for k in STAT_TO_SUB}
            else:
                new_stats = _parse_stat_pairs(rhs)
            if new_stats:
                uti.properties = [p for p in uti.properties if p.property_name != 0]
                for k, v in new_stats.items():
                    uti.properties.append(make_prop(0, STAT_TO_SUB[k], 1, v))
                changed = True
                continue
        elif seg_n.startswith("ajout") and any(k in seg for k in STAT_TO_SUB):
            add_stats = _parse_stat_pairs(seg)
            for k, v in add_stats.items():
                sub = STAT_TO_SUB[k]
                uti.properties = [p for p in uti.properties if not (p.property_name == 0 and p.subtype == sub)]
                uti.properties.append(make_prop(0, sub, 1, v))
                changed = True
            continue

        # 2. CA : "CA +X → CA +Y"
        m_ac = re.search(r"ca \+\d+ → ca \+(\d+)", seg_n)
        if m_ac:
            new_ac = int(m_ac.group(1))
            for p in uti.properties:
                if p.property_name == 1:
                    p.cost_value = new_ac
                    changed = True

        # 3. Attaque : "Atq +X → Atq +Y"
        m_atk = re.search(r"atq \+\d+ → atq \+(\d+)", seg_n)
        if m_atk:
            new_atk = int(m_atk.group(1))
            for p in uti.properties:
                if p.property_name == 38:
                    p.cost_value = new_atk
                    changed = True

        # 4. Saves : "Saves +X → Saves +Y"
        m_sv = re.search(r"saves \+\d+ → saves \+(\d+)", seg_n)
        if m_sv:
            new_sv = int(m_sv.group(1))
            for p in uti.properties:
                if p.property_name in (26, 27):
                    p.cost_value = new_sv
                    changed = True

        # 5. Dégâts sur Gants : "Dégâts +X → +Y"
        m_dmg = re.search(r"degats \+(?:\d+d\d+|\d+) → \+(\d+d\d+|\d+)", seg_n)
        if m_dmg:
            new_cv = DMG_COST_MAP.get(m_dmg.group(1))
            if new_cv is not None:
                for p in uti.properties:
                    if p.property_name == 11:
                        p.cost_value = new_cv
                        changed = True

        # 6. Immunités % : "Immunité +75% → +30%" ou "+50%/+50% → +25%/+25%"
        m_imm = re.search(r"immunite .*?→ \+(\d+)%", seg_n)
        if m_imm:
            cap_pct = int(m_imm.group(1))
            cap_cv = IMM_COST_MAP.get(cap_pct, 10)
            for p in uti.properties:
                if p.property_name == 14 and p.cost_value in (4, 5, 6, 7):  # >= 50%
                    p.cost_value = cap_cv
                    changed = True

        # 7. RD : "RD ... → RD +Y/-" ou "→ +Y/-"
        m_rd = re.search(r"rd .*?→ (?:rd )?\+(\d+)/-", seg_n)
        if m_rd:
            target_rd = int(m_rd.group(1))
            target_cv = RD_TO_COST.get(target_rd, 1)
            for p in uti.properties:
                if p.property_name == 17 and p.cost_value > target_cv:
                    p.cost_value = target_cv
                    changed = True

    return changed


def build_gear_utis(inst: Installation) -> tuple[int, int]:
    modified_items = 0
    tiered_armors = 0
    for fname in GEAR_CSVS:
        path = ROOT / fname
        with open(path, encoding="utf-8-sig", newline="") as fh:
            rows = list(csv.reader(fh))
        h = {c.strip(): i for i, c in enumerate(rows[0])}
        is_armor_csv = "Armures items" in fname

        for r in rows[1:]:
            if not r or not r[0].strip():
                continue
            resref = r[h["ResRef"]].strip().lower()
            mod_txt = r[h["Changement (mod)"]].strip() if "Changement (mod)" in h and len(r) > h["Changement (mod)"] else ""
            desc_txt = r[h["Description (mod)"]].strip() if "Description (mod)" in h and len(r) > h["Description (mod)"] else ""
            target_ulvl: int | None = None
            if is_armor_csv:
                tcol = r[h["Type (2DA)"]].strip()
                if tcol in ("Armor Class 4", "Armor Class 5", "Armor Armd Flight Suit", "Armor Zeison Sha"):
                    target_ulvl = 1  # Légère : 1 slot (sous-couches Légère level=1 uniquement)
                elif tcol in ("Armor Class 8", "Armor Class 9"):
                    target_ulvl = 2  # Lourde : 1 slot (sous-couches Lourde level=2 + Légère level=1)
                elif tcol in ("Armor Class 6", "Armor Class 7"):
                    target_ulvl = 6  # Intermédiaire : 2 slots + 24 combinées (level=6)
                elif any(k in tcol for k in ("Robe", "Clothing", "Revan")):
                    target_ulvl = 0  # Robes : 0 slot

            if not mod_txt and not desc_txt and target_ulvl is None:
                continue

            res = inst.resource(resref, ResourceType.UTI)
            if not res:
                continue
            uti = read_uti(res.data)
            dirty = apply_mod_to_uti(uti, mod_txt)
            # Armures-bures (Zeison Sha/Jal Shey/Malak bi=102) & Ubèse/Flight Suit (bi=98) :
            # migrer vers Armor_Class_4 (bi=38) en conservant body_variation & texture_variation
            # pour le grisé natif des pouvoirs interdits (0x003f) sans casser les modèles 3D.
            if is_armor_csv and uti.base_item in (98, 102):
                uti.base_item = 38
                dirty = True
            if desc_txt:
                set_uti_desc(uti, desc_txt)
                dirty = True
            if target_ulvl is not None and uti.upgrade_level != target_ulvl:
                uti.upgrade_level = target_ulvl
                dirty = True
                tiered_armors += 1
            if dirty:
                write_uti(uti, OVR_DIR / f"{resref}.uti")
                modified_items += 1
    return modified_items, tiered_armors


# Sous-couches standard réservées aux Armures Lourdes (RD/blindage/CON -> level=2, bloquées sur Légère level=1)
HEAVY_ONLY_UNDERLAYS = {4, 5, 10, 11, 16, 17}


def _load_upgrade_descs() -> dict[str, str]:
    """Charge la colonne `Description (mod)` de `Améliorations.csv` par resref."""
    out: dict[str, str] = {}
    if not CSV_UPGRADES.exists():
        return out
    with open(CSV_UPGRADES, encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.reader(fh))
    if not rows or "Description (mod)" not in rows[0]:
        return out
    d_idx = rows[0].index("Description (mod)")
    for r in rows[1:]:
        if len(r) > d_idx and r[0].strip() and r[d_idx].strip():
            out[r[0].strip().lower()] = r[d_idx].strip()
    return out


def build_standard_armor_upgrades_partition(inst: Installation) -> int:
    """Cloisonne les 36 upgrades d'armure standard (u_a_over_01..18, u_a_unde_01..18) :
      - u_a_over_01..18 -> upgrade_level = 6 (exclusif Intermédiaires : 0 sur-couche sur Légère/Lourde)
      - u_a_unde_01..18 -> upgrade_level = 2 pour RD/blindage Lourde, 1 pour Légère."""
    descs = _load_upgrade_descs()
    count = 0
    for n in range(1, 19):
        # Sur-couches -> réservées Intermédiaires (level = 6)
        rr_o = f"u_a_over_{n:02d}"
        res_o = inst.resource(rr_o, ResourceType.UTI)
        if res_o:
            u = read_uti(res_o.data)
            u.upgrade_level = 6
            set_uti_desc(u, descs.get(rr_o, ""))
            write_uti(u, OVR_DIR / f"{rr_o}.uti")
            count += 1
        # Sous-couches -> 2 (Lourde) ou 1 (Légère)
        rr_u = f"u_a_unde_{n:02d}"
        res_u = inst.resource(rr_u, ResourceType.UTI)
        if res_u:
            u = read_uti(res_u.data)
            u.upgrade_level = 2 if n in HEAVY_ONLY_UNDERLAYS else 1
            set_uti_desc(u, descs.get(rr_u, ""))
            write_uti(u, OVR_DIR / f"{rr_u}.uti")
            count += 1
    return count


def build_combined_armor_upgrades(inst: Installation) -> int:
    """Génère les 24 upgrades combinées intermédiaires (u_a_over_19..30, u_a_unde_19..30)
    exclusives aux armures intermédiaires (upgrade_level = 6)."""
    res_over = inst.resource("u_a_over_01", ResourceType.UTI)
    res_unde = inst.resource("u_a_unde_01", ResourceType.UTI)
    if not res_over or not res_unde:
        return 0
    descs = _load_upgrade_descs()
    count = 0
    for prefix, base_res in (("u_a_over_", res_over), ("u_a_unde_", res_unde)):
        for num in range(19, 31):
            rr = f"{prefix}{num:02d}"
            uti = read_uti(base_res.data)
            uti.resref.set_data(rr)
            uti.tag = rr
            uti.upgrade_level = 6
            # Tier Mk I (19..22), Mk II (23..26), Mk III (27..30)
            tier = 1 if num <= 22 else (2 if num <= 26 else 3)
            uti.properties = [
                make_prop(1, 0, 2, tier),                      # CA +1 / +2 / +3
                make_prop(14, 12, 5, {1: 2, 2: 8, 3: 10}[tier]),  # Immunité Énergie 10% / 15% / 30%
            ]
            set_uti_desc(uti, descs.get(rr, ""))
            write_uti(uti, OVR_DIR / f"{rr}.uti")
            count += 1
    return count


def build_gamorrean_1m_utis(inst: Installation) -> int:
    """Génère les variantes .uti 1M réservées à Gamoréen II (via baseitem_1m_map.json)."""
    if not MIRROR_MAP_FILE.exists():
        return 0
    mirror_map: dict[str, int] = json.loads(MIRROR_MAP_FILE.read_text(encoding="utf-8"))
    count = 0
    for src_rr, bi_label, dst_rr in GAMORREAN_WEAPONS:
        if bi_label not in mirror_map:
            continue
        res = inst.resource(src_rr, ResourceType.UTI)
        if not res:
            continue
        uti = read_uti(res.data)
        uti.base_item = mirror_map[bi_label]
        uti.resref.set_data(dst_rr)
        uti.tag = dst_rr
        write_uti(uti, OVR_DIR / f"{dst_rr}.uti")
        count += 1
    return count


def _parse_upgrade_props(mod_txt: str, old_props: list[UTIProperty]) -> list[UTIProperty]:
    """Convertit la colonne `Changement (mod)` de `Améliorations.csv` en liste UTIProperty."""
    old_skill_sub = next((p.subtype for p in old_props if p.property_name == 36), 0)
    out: list[UTIProperty] = []
    for raw in [s.strip() for s in mod_txt.split(",") if s.strip()]:
        s = norm(raw)
        if s == "acere":
            out.append(make_prop(28, 0, 0, 0))
            continue
        m = re.match(r"bonus aux degats \((\w+)\) \+(\d+d\d+|\d+)", s)
        if m:
            sub = DMG_TYPE_SUB.get(m.group(1), 12)
            cv = DMG_COST_MAP.get(m.group(2), 1)
            out.append(make_prop(11, sub, 4, cv))
            continue
        m = re.match(r"bonus aux degats contre (?:droides|race) \+(\d+d\d+|\d+)", s)
        if m:
            p = make_prop(13, 5, 4, DMG_COST_MAP.get(m.group(1), 6))
            p.param1, p.param1_value = 0, 11
            out.append(p)
            continue
        m = re.match(r"bonus aux degats contre cote obscur \+(\d+d\d+|\d+)", s)
        if m:
            p = make_prop(12, 3, 4, DMG_COST_MAP.get(m.group(1), 8))
            p.param1, p.param1_value = 0, 0
            out.append(p)
            continue
        m = re.match(r"coups critiques plus importants \+(\d+d\d+|\d+)", s)
        if m:
            out.append(make_prop(49, 0, 4, DMG_COST_MAP.get(m.group(1), 6)))
            continue
        m = re.match(r"bonus d attaque \+(\d+)", s)
        if m:
            out.append(make_prop(38, 0, 2, int(m.group(1))))
            continue
        m = re.match(r"malus a l attaque -(\d+)", s)
        if m:
            out.append(make_prop(8, 0, 20, int(m.group(1))))
            continue
        m = re.match(r"bonus defense \+(\d+)", s)
        if m:
            out.append(make_prop(1, 0, 2, int(m.group(1))))
            continue
        m = re.match(r"malus de defense -(\d+)", s)
        if m:
            out.append(make_prop(20, 0, 20, int(m.group(1))))
            continue
        m = re.match(r"jets de sauvegarde ameliores \+(\d+)", s)
        if m:
            out.append(make_prop(27, 0, 2, int(m.group(1))))
            continue
        m = re.match(r"parade tirs de blaster \+(\d+)", s)
        if m:
            out.append(make_prop(55, 0, 1, int(m.group(1))))
            continue
        m = re.match(r"bonus de caracteristique \((\w+)\) \+(\d+)", s)
        if m:
            out.append(make_prop(0, ABILITY_EN_SUB.get(m.group(1), 0), 1, int(m.group(2))))
            continue
        m = re.match(r"bonus de competence \+(\d+)", s)
        if m:
            out.append(make_prop(36, old_skill_sub, 1, int(m.group(1))))
            continue
        m = re.match(r"regeneration de points de force \+(\d+)", s)
        if m:
            out.append(make_prop(54, 0, 2, int(m.group(1))))
            continue
        m = re.match(r"regeneration \+(\d+)", s)
        if m:
            out.append(make_prop(35, 0, 2, int(m.group(1))))
            continue
        m = re.match(r"resistance aux degats \((\w+)\) \+(\d+)/-", s)
        if m:
            out.append(make_prop(17, DMG_TYPE_SUB.get(m.group(1), 8), 7, RD_TO_COST.get(int(m.group(2)), 1)))
            continue
        if "restriction d alignement (lumineux)" in s:
            out.append(make_prop(43, 2, 0, 0))
            continue
        if "restriction d alignement (obscur)" in s:
            out.append(make_prop(43, 3, 0, 0))
            continue
        m = re.match(r"en cas de coup au but \((\w+)\s*:\s*dd\s*(\d+)", s)
        if m:
            sub = ONHIT_FR_SUB.get(m.group(1), 1)
            base_dc = int(m.group(2))
            cv = 1 if base_dc <= 4 else (2 if base_dc <= 6 else 4)
            p = make_prop(32, sub, 25, cv)
            p.param1, p.param1_value = 1, 0
            out.append(p)
            continue
    return out


def build_weapon_upgrades(inst: Installation) -> int:
    """Applique le cloisonnement et le calibrage des 156 améliorations d'armes/sabres (`Améliorations.csv`)."""
    if not CSV_UPGRADES.exists():
        return 0
    with open(CSV_UPGRADES, encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.reader(fh))
    d_idx = rows[0].index("Description (mod)") if rows and "Description (mod)" in rows[0] else -1
    count = 0
    for r in rows[1:]:
        if len(r) < 7:
            continue
        rr = r[0].strip().lower()
        mod_txt = r[6].strip()
        if not rr.startswith(("u_m_", "u_r_", "u_l_")) or not mod_txt or norm(mod_txt) == "inchange":
            continue
        res = inst.resource(rr, ResourceType.UTI)
        if not res:
            continue
        uti = read_uti(res.data)
        new_props = _parse_upgrade_props(mod_txt, uti.properties)
        if new_props:
            uti.properties = new_props
            if d_idx >= 0 and len(r) > d_idx and r[d_idx].strip():
                set_uti_desc(uti, r[d_idx].strip())
            write_uti(uti, OVR_DIR / f"{rr}.uti")
            count += 1
    return count


def build_personal_crystals(inst: Installation) -> int:
    """Génère les 90 variantes .uti du Cristal personnel de l'Exilé (3 paliers × 30 paires de stats) :
    ov_crys_<tier>_<s1><s2>.uti (tier 1: +2/+1/0 ; tier 2: +4/+2/+1 ; tier 3: +6/+4/+2)."""
    res_base = inst.resource("qcrystal_1_2", ResourceType.UTI)
    if not res_base:
        return 0
    tier_bonuses = {1: (2, 1, 0), 2: (4, 2, 1), 3: (6, 4, 2)}
    count = 0
    for tier, (b1, b2, b_other) in tier_bonuses.items():
        for s1 in range(6):
            for s2 in range(6):
                if s1 == s2:
                    continue
                rr = f"ov_crys_{tier}_{s1}{s2}"
                uti = read_uti(res_base.data)
                uti.resref.set_data(rr)
                uti.tag = rr
                props = [make_prop(62, 0, 0, 0)]  # Personal Crystal flag
                for st in range(6):
                    val = b1 if st == s1 else (b2 if st == s2 else b_other)
                    if val > 0:
                        props.append(make_prop(0, st, 1, val))
                uti.properties = props
                write_uti(uti, OVR_DIR / f"{rr}.uti")
                count += 1
    return count


def build_plasma_torch_vanilla() -> int:
    """Restaure les dégâts vanilla (1d1 + 1d6 Feu) de la Torche à plasma (plasmatorch.uti)
    via le baseitem dédié Plasma_Torch (sans affecter les Matraques 1d8)."""
    if not MIRROR_MAP_FILE.exists():
        return 0
    mirror_map: dict[str, int] = json.loads(MIRROR_MAP_FILE.read_text(encoding="utf-8"))
    pt_bi = mirror_map.get("Plasma_Torch")
    if pt_bi is None:
        return 0
    from pykotor.resource.formats.erf import read_erf
    mod_path = GAME_PATH / "Modules" / "101per.mod"
    if not mod_path.exists():
        return 0
    erf = read_erf(mod_path)
    for res in erf:
        if res.restype == ResourceType.UTI and str(res.resref).lower() == "plasmatorch":
            uti = read_uti(res.data)
            uti.base_item = pt_bi
            write_uti(uti, OVR_DIR / "plasmatorch.uti")
            return 1
    return 0


def main() -> None:
    OVR_DIR.mkdir(parents=True, exist_ok=True)
    inst = Installation(GAME_PATH)
    print(f"=== Build Jalon 2 (items .uti) -> {OVR_DIR} ===")
    n_gear, n_arm = build_gear_utis(inst)
    print(f"[OK] Équipement (6 CSV) : {n_gear} fichiers .uti générés (dont {n_arm} armures cloisonnées level 0/1/2/6)")
    n_std = build_standard_armor_upgrades_partition(inst)
    print(f"[OK] Upgrades d'armures standard cloisonnées : {n_std} fichiers .uti (over=6, unde Lourde=2, unde Légère=1)")
    n_comb = build_combined_armor_upgrades(inst)
    print(f"[OK] Upgrades combinées intermédiaires : {n_comb} fichiers .uti (u_a_over_19..30, u_a_unde_19..30)")
    n_gam = build_gamorrean_1m_utis(inst)
    print(f"[OK] Variantes 1M Gamoréen II : {n_gam} fichiers .uti (m_w_*_1m.uti)")
    n_wup = build_weapon_upgrades(inst)
    print(f"[OK] Améliorations d'armes & sabres (Améliorations.csv) : {n_wup} fichiers .uti générés")
    n_crys = build_personal_crystals(inst)
    print(f"[OK] Cristal personnel de l'Exilé (3 paliers × 30 paires) : {n_crys} fichiers .uti (ov_crys_*.uti)")
    n_pt = build_plasma_torch_vanilla()
    print(f"[OK] Torche à plasma vanilla (1d1 + 1d6 Feu) : {n_pt} fichier .uti (plasmatorch.uti)")
    total = n_gear + n_std + n_comb + n_gam + n_wup + n_crys + n_pt
    print(f"=== Jalon 2 BUILD OK ({total} .uti générés) ===")


if __name__ == "__main__":
    main()
