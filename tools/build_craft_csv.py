# -*- coding: utf-8 -*-
"""Génère « Kotor 2 - rééquilibrage - WIP Craft.csv » :
toutes les recettes craftables en vanilla (Établi : itemcreate.2da + itemcreatemira.2da ;
Laboratoire : chemicalcreate.2da), avec noms FR résolus depuis les .uti et dialog.tlk.

Usage : .venv\\Scripts\\python.exe tools\\build_craft_csv.py
"""
from __future__ import annotations

import csv
from pathlib import Path

from pykotor.extract.installation import Installation
from pykotor.resource.formats.gff import read_gff
from pykotor.resource.formats.tlk import read_tlk
from pykotor.resource.formats.twoda import read_2da
from pykotor.resource.type import ResourceType

GAME = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Knights of the Old Republic II")
ROOT = Path(__file__).resolve().parent.parent
DST = ROOT / "Kotor 2 - rééquilibrage - WIP Craft.csv"

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


def main() -> None:
    inst = Installation(GAME)
    tlk = read_tlk(GAME / "dialog.tlk")

    def uti_info(resref: str) -> tuple[str, str]:
        """Retourne (nom_fr, cout_base) depuis le .uti."""
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

    # Regrouper par groupe 2DA puis trier par compétence + seuil
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
            "",
        ])

    # 2. Laboratoire (chemicalcreate.2da)
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

    print(f"OK : {DST} ({len(wb_entries)} Établi + {len(lab_entries)} Labo = {len(wb_entries)+len(lab_entries)} recettes)")


if __name__ == "__main__":
    main()
