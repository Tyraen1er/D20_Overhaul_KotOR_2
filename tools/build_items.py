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
DMG_COST_MAP = {"1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "1d4": 6, "1d6": 7, "1d8": 8, "1d10": 9, "2d6": 10}
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
    medium_armors = 0
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
            needs_med_upgrade = False
            if is_armor_csv:
                tcol = r[h["Type (2DA)"]].strip()
                if tcol in ("Armor Class 6", "Armor Class 7"):
                    needs_med_upgrade = True

            if not mod_txt and not needs_med_upgrade:
                continue

            res = inst.resource(resref, ResourceType.UTI)
            if not res:
                continue
            uti = read_uti(res.data)
            dirty = apply_mod_to_uti(uti, mod_txt)
            if needs_med_upgrade and uti.upgrade_level < 6:
                uti.upgrade_level = 6
                dirty = True
                medium_armors += 1
            if dirty:
                write_uti(uti, OVR_DIR / f"{resref}.uti")
                modified_items += 1
    return modified_items, medium_armors


def build_combined_armor_upgrades(inst: Installation) -> int:
    """Génère les 24 upgrades combinées intermédiaires (u_a_over_19..30, u_a_unde_19..30)
    exclusives aux armures intermédiaires (upgrade_level = 6)."""
    res_over = inst.resource("u_a_over_01", ResourceType.UTI)
    res_unde = inst.resource("u_a_unde_01", ResourceType.UTI)
    if not res_over or not res_unde:
        return 0
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


def main() -> None:
    OVR_DIR.mkdir(parents=True, exist_ok=True)
    inst = Installation(GAME_PATH)
    print(f"=== Build Jalon 2 (items .uti) -> {OVR_DIR} ===")
    n_gear, n_med = build_gear_utis(inst)
    print(f"[OK] Équipement (6 CSV) : {n_gear} fichiers .uti générés (dont {n_med} armures intermédiaires upgrade_level=6)")
    n_comb = build_combined_armor_upgrades(inst)
    print(f"[OK] Upgrades combinées intermédiaires : {n_comb} fichiers .uti (u_a_over_19..30, u_a_unde_19..30)")
    n_gam = build_gamorrean_1m_utis(inst)
    print(f"[OK] Variantes 1M Gamoréen II : {n_gam} fichiers .uti (m_w_*_1m.uti)")
    print(f"=== Jalon 2 BUILD OK ({n_gear + n_comb + n_gam} .uti générés) ===")


if __name__ == "__main__":
    main()
