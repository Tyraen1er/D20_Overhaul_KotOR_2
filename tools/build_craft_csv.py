# -*- coding: utf-8 -*-
"""Génère « Kotor 2 - rééquilibrage - Craft.csv » :
toutes les recettes craftables en vanilla (Établi : itemcreate.2da + itemcreatemira.2da ;
Laboratoire : chemicalcreate.2da), avec noms FR résolus depuis les .uti et dialog.tlk,
PLUS :
  - les paliers de niveau joueur actés (Mk I = Niv. 1, Mk II = Niv. 10, Mk III = Niv. 15, Mk IV/T5 = Niv. 20 ;
    lignées 3 tiers : Niv. 1 / 10 / 18) dans la colonne « Changement (mod) » ;
  - l'ajout des armes de base non-laser manquantes (toutes armes de base hors Sabres Laser craftables) ;
  - l'ajout des 24 upgrades doubles exclusives aux armures intermédiaires.

Usage : .venv\\Scripts\\python.exe tools\\build_craft_csv.py
"""
from __future__ import annotations

import csv
import re
from pathlib import Path

from pykotor.extract.installation import Installation
from pykotor.resource.formats.gff import read_gff
from pykotor.resource.formats.tlk import read_tlk
from pykotor.resource.formats.twoda import read_2da
from pykotor.resource.type import ResourceType

from paths import CSV_CRAFT as DST, CSV_UPGRADES as UPG_CSV, ROOT

GAME = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Knights of the Old Republic II")

SKILL_FR = {
    "0": "Informatique",
    "1": "Démolition",
    "2": "Discrétion",
    "3": "Vigilance",
    "4": "Persuasion",
    "5": "Réparation",
    "6": "Sécurité",
    "7": "Premiers secours",
}

WORKBENCH_GROUP_FR = {
    "0": "Armures (sur/sous-couches)",
    "1": "Armes à distance (upgrades)",
    "2": "Armes de mêlée (upgrades)",
    "3": "Sabres laser (upgrades)",
    "4": "Utilitaires, armes & roquettes",
}

LAB_GROUP_FR = {
    "0": "Médipacs & Implants",
    "1": "Stims",
    "2": "Mines",
    "3": "Grenades",
    "5": "Objets de quête / coupés (seuil 50)",
}

ALIGN_FR = {
    "0": "—",
    "1": "Côté Lumineux",
    "2": "Côté Obscur",
}

# Armes de base non-laser manquantes dans itemcreate.2da (Group 4)
# (Toutes les autres — Epée longue, Pistolet de survie, Fusil blaster, Vibro-épée,
#  Blaster à répétition, Fusil désintégrateur, Vibro-double-lame — sont déjà dans itemcreate.2da)
EXTRA_BASE_WEAPONS = [
    ("w_melee_01",      "Épée courte (base)",               "Réparation", "2", "1"),
    ("w_melee_03",      "Matraque électrique (base)",       "Réparation", "3", "1"),
    ("w_melee_04",      "Bâton de combat (base)",           "Réparation", "2", "1"),
    ("w_melee_05",      "Vibro-lame (base)",                "Réparation", "4", "1"),
    ("w_melee_07",      "Double-lame traditionnelle (base)","Réparation", "5", "1"),
    ("w_melee_09",      "Hache gamorréenne (base)",         "Réparation", "6", "1"),
    ("w_melee_14",      "Pique de Force (base)",            "Réparation", "6", "1"),
    ("w_melee_ww_base", "Lame de guerre wookie (base mod)", "Réparation", "6", "1"),
    ("w_blaste_01",     "Pistolet blaster (base)",          "Réparation", "2", "1"),
    ("w_blaste_02",     "Pistolet ionique (base)",          "Réparation", "4", "1"),
    ("w_blaste_04",     "Pistolet sonique (base)",          "Réparation", "4", "1"),
    ("w_blaste_05",     "Pistolet désintégrateur (base)",   "Réparation", "6", "1"),
    ("w_blaste_06",     "Blaster lourd (base)",             "Réparation", "5", "1"),
    ("w_brifle_01",     "Carabine blaster (base)",          "Réparation", "4", "1"),
    ("w_brifle_02",     "Fusil ionique (base)",             "Réparation", "5", "1"),
    ("w_brifle_03",     "Fusil sonique (base)",             "Réparation", "5", "1"),
    ("w_brifle_05",     "Arbalète wookie (base)",           "Réparation", "6", "1"),
    ("w_brifle_hr_base","Blaster lourd à répétition (base mod)", "Réparation", "8", "1"),
]


def workbench_level_gate(resref: str, skill_str: str) -> str:
    """Calcule le palier de niveau joueur acté (1 / 10 / 15 / 20 ; 3-tiers : 1 / 10 / 18)."""
    rr = resref.lower()
    m = re.search(r"_(\d+)$", rr)
    idx = int(m.group(1)) if m else 0
    sk = int(skill_str) if skill_str.isdigit() else 0

    # Armures (01..30) : 4 tiers sur-couches (1-8, 9-16, 17-24, 25-30), 5 tiers sous-couches (1-6, 7-12, 13-18, 19-24, 25-30)
    if rr.startswith("u_a_over_"):
        if idx <= 8: return "Niv. 1 (Mk I)"
        if idx <= 16: return "Niv. 10 (Mk II)"
        if idx <= 24: return "Niv. 15 (Mk III)"
        return "Niv. 20 (Mk IV)"
    if rr.startswith("u_a_unde_"):
        if idx <= 6: return "Niv. 1 (Mk I)"
        if idx <= 12: return "Niv. 10 (Mk II)"
        if idx <= 18: return "Niv. 15 (Mk III)"
        return "Niv. 20 (Mk IV/T5)"

    # Armes mêlée & distance (01..15)
    if rr.startswith(("u_m_grip_", "u_r_firi_")):  # 3 tiers stricts (1-5, 6-10, 11-15)
        if idx <= 5: return "Niv. 1 (Mk I)"
        if idx <= 10: return "Niv. 10 (Mk II)"
        return "Niv. 18 (Mk III)"
    if rr.startswith(("u_m_edge_", "u_m_cell_", "u_r_targ_", "u_r_powe_")):  # 4-5 tiers
        if idx <= 4: return "Niv. 1 (Mk I)"
        if idx <= 8: return "Niv. 10 (Mk II)"
        if idx <= 12: return "Niv. 15 (Mk III)"
        return "Niv. 20 (Mk IV/T5)"

    # Sabres laser (01..13) : 3-4 tiers
    if rr.startswith(("u_l_emit_", "u_l_lens_", "u_l_cell_")):
        if idx <= 4: return "Niv. 1 (Mk I)"
        if idx <= 8: return "Niv. 10 (Mk II)"
        if idx <= 11: return "Niv. 15 (Mk III)"
        return "Niv. 20 (Mk IV)"

    # Boucliers & Utilitaires & Armes vanilla (Group 4)
    if rr.startswith("a_shield_"):
        if sk <= 5: return "Niv. 1"
        if sk <= 15: return "Niv. 10"
        if sk <= 22: return "Niv. 15"
        return "Niv. 20"
    if rr.startswith(("w_melee_", "w_blaste_", "w_brifle_")):
        return "Niv. 1 (arme de base craftable)"
    if rr.startswith("w_rocket_"):
        if sk <= 5: return "Niv. 1"
        if sk <= 10: return "Niv. 10"
        if sk <= 15: return "Niv. 15"
        return "Niv. 20"
    return ""


def main() -> None:
    inst = Installation(GAME)
    tlk = read_tlk(GAME / "dialog.tlk")

    def uti_info(resref: str) -> tuple[str, str]:
        res = inst.resource(resref.lower(), ResourceType.UTI)
        if not res:
            return ("", "")
        try:
            root = read_gff(res.data).root
        except Exception:
            return ("", "")
        name = ""
        if "LocalizedName" in root:
            ls = root["LocalizedName"]
            sr = getattr(ls, "stringref", -1)
            if isinstance(sr, int) and sr >= 0:
                entry = tlk.get(sr)
                if entry and entry.text:
                    name = entry.text.strip()
            if not name:
                for _lang, _gen, txt in ls:
                    if txt:
                        name = txt.strip()
                        break
        cost = ""
        if "Cost" in root:
            c = root["Cost"]
            cost = str(c.value if hasattr(c, "value") else c)
        return (name, cost)

    header = [
        "ResRef",
        "Nom (FR)",
        "Station",
        "Catégorie (groupe 2DA)",
        "Compétence (vanilla)",
        "Seuil compétence (vanilla)",
        "Niveau requis (vanilla)",
        "Alignement (vanilla)",
        "Coût base .uti",
        "Changement (mod)",
    ]
    rows: list[list[str]] = [header]

    # 1. Établi (itemcreate.2da + extras de itemcreatemira.2da)
    ic = read_2da(inst.resource("itemcreate", ResourceType.TwoDA).data)
    icm = read_2da(inst.resource("itemcreatemira", ResourceType.TwoDA).data)
    seen_ic = set()

    wb_entries = []
    for i in range(len(ic)):
        r = ic.get_row(i)
        lbl = r.get_string("label").strip()
        if not lbl or lbl == "****":
            continue
        seen_ic.add(lbl.lower())
        wb_entries.append(("Établi", r))

    for i in range(len(icm)):
        r = icm.get_row(i)
        lbl = r.get_string("label").strip()
        if not lbl or lbl == "****" or lbl.lower() in seen_ic:
            continue
        wb_entries.append(("Établi (Mira)", r))

    wb_entries.sort(key=lambda x: (
        int(x[1].get_string("group")) if x[1].get_string("group").isdigit() else 99,
        x[0],
        int(x[1].get_string("skill")) if x[1].get_string("skill").isdigit() else 999,
        x[1].get_string("label").lower(),
    ))

    cur_grp = None
    for station, r in wb_entries:
        grp = r.get_string("group").strip()
        if grp != cur_grp:
            cur_grp = grp
            title = f"ÉTABLI — {WORKBENCH_GROUP_FR.get(grp, f'Groupe {grp}').upper()}"
            rows.append([title] + [""] * (len(header) - 1))
        lbl = r.get_string("label").strip()
        nom, cost = uti_info(lbl)
        sk_id = r.get_string("base_skill").strip()
        sk_lvl = r.get_string("skill").strip()
        req_lvl = r.get_string("level").strip()
        align = r.get_string("align").strip()
        mod_note = workbench_level_gate(lbl, sk_lvl)
        rows.append([
            lbl,
            nom,
            station,
            WORKBENCH_GROUP_FR.get(grp, f"Groupe {grp}"),
            SKILL_FR.get(sk_id, sk_id),
            sk_lvl,
            req_lvl if req_lvl not in ("", "0") else "—",
            ALIGN_FR.get(align, align),
            cost,
            mod_note,
        ])

    # 2. Ajouts Mod — Armes de base non-laser manquantes
    rows.append(["ÉTABLI — ARMES DE BASE NON-LASER (AJOUTS MOD)"] + [""] * (len(header) - 1))
    for rr, nom_fallback, comp, seuil, lvl in EXTRA_BASE_WEAPONS:
        nom_uti, cost = uti_info(rr)
        rows.append([
            rr,
            nom_uti or nom_fallback,
            "Établi",
            "Armes de base (ajouts mod)",
            comp,
            seuil,
            "—",
            "—",
            cost or "100",
            f"Ajout mod — Niv. {lvl} (seuil {comp} {seuil})",
        ])

    # 3. Ajouts Mod — 24 Upgrades doubles exclusives aux armures intermédiaires (lues depuis Améliorations.csv)
    rows.append(["ÉTABLI — ARMURES INTERMÉDIAIRES DOUBLES (AJOUTS MOD)"] + [""] * (len(header) - 1))
    if UPG_CSV.exists():
        with open(UPG_CSV, encoding="utf-8-sig") as f:
            for r in csv.reader(f):
                if len(r) >= 7 and r[0].startswith(("u_a_over_c", "u_a_unde_c")):
                    rr, nom, empl, tier = r[0], r[1], r[2], int(r[3])
                    comp = "Réparation" if "over" in rr else "Premiers secours"
                    if tier <= 4:
                        seuil, lvl_txt = "6", "Niv. 1 (Mk I)"
                    elif tier <= 8:
                        seuil, lvl_txt = "14", "Niv. 10 (Mk II)"
                    else:
                        seuil, lvl_txt = "22", "Niv. 18 (Mk III)"
                    rows.append([
                        rr,
                        nom,
                        "Établi",
                        empl,
                        comp,
                        seuil,
                        "—",
                        "—",
                        "—",
                        f"Ajout mod — {lvl_txt} (seuil {comp} {seuil})",
                    ])

    # 4. Laboratoire (chemicalcreate.2da)
    cc = read_2da(inst.resource("chemicalcreate", ResourceType.TwoDA).data)
    lab_entries = []
    for i in range(len(cc)):
        r = cc.get_row(i)
        lbl = r.get_string("label").strip()
        if not lbl or lbl == "****":
            continue
        lab_entries.append(r)

    lab_entries.sort(key=lambda r: (
        int(r.get_string("group")) if r.get_string("group").isdigit() else 99,
        int(r.get_string("skilllevel")) if r.get_string("skilllevel").isdigit() else 999,
        r.get_string("label").lower(),
    ))

    cur_grp = None
    for r in lab_entries:
        grp = r.get_string("group").strip()
        if grp != cur_grp:
            cur_grp = grp
            title = f"LABORATOIRE — {LAB_GROUP_FR.get(grp, f'Groupe {grp}').upper()}"
            rows.append([title] + [""] * (len(header) - 1))
        lbl = r.get_string("label").strip()
        nom, cost = uti_info(lbl)
        sk_id = r.get_string("base_skill").strip()
        sk_lvl = r.get_string("skilllevel").strip()
        rows.append([
            lbl,
            nom,
            "Laboratoire",
            LAB_GROUP_FR.get(grp, f"Groupe {grp}"),
            SKILL_FR.get(sk_id, sk_id),
            sk_lvl,
            "—",
            "—",
            cost,
            "",
        ])

    with open(DST, "w", encoding="utf-8-sig", newline="") as f:
        csv.writer(f).writerows(rows)

    print(f"OK : {DST} ({len(rows)-1} lignes totales dont {len(EXTRA_BASE_WEAPONS)} armes de base + 24 armures doubles)")


if __name__ == "__main__":
    main()
