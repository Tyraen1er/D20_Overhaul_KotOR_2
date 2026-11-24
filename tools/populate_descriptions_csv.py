#!/usr/bin/env python3
"""Génère et remplit la colonne `Description (mod)` dans les 7 CSV d'équipement/améliorations.

Conserve le paragraphe lore VF vanilla (extrait de `dialog.tlk`) et remplace l'en-tête
de statistiques obsolète par les vraies statistiques moddées issues de `Changement (mod)`.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

from pykotor.extract.installation import Installation
from pykotor.resource.formats.tlk import read_tlk
from pykotor.resource.generics.uti import read_uti
from pykotor.resource.type import ResourceType

ROOT = Path(__file__).resolve().parent.parent
GAME_PATH = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Knights of the Old Republic II")

UPGRADES_CSV = ROOT / "Kotor 2 - rééquilibrage - Améliorations.csv"
GEAR_CSVS = [
    ROOT / "Kotor 2 - rééquilibrage - Casques.csv",
    ROOT / "Kotor 2 - rééquilibrage - Implants.csv",
    ROOT / "Kotor 2 - rééquilibrage - Gants.csv",
    ROOT / "Kotor 2 - rééquilibrage - Ceintures.csv",
    ROOT / "Kotor 2 - rééquilibrage - Brassards.csv",
    ROOT / "Kotor 2 - rééquilibrage - Armures items.csv",
]

STAT_LINE_PREFIXES = (
    "spécial", "special", "bonus", "malus", "dégâts", "degats", "attaque",
    "défense", "defense", "acéré", "acere", "restriction", "uniquement",
    "coups critiques", "résistance", "resistance", "immunité", "immunite",
    "régénération", "regeneration", "jets de sauvegarde", "parade",
    "en cas de coup", "don requis", "amélioration", "amelioration",
    "dex", "for", "con", "int", "sag", "cha", "classe d'armure",
)


def extract_lore_paragraph(vanilla_desc: str) -> str:
    """Extrait le(s) paragraphe(s) lore de la description vanilla en retirant l'en-tête de stats."""
    if not vanilla_desc:
        return ""
    paras = [p.strip() for p in re.split(r"\r?\n\s*\r?\n", vanilla_desc.strip()) if p.strip()]
    lore_paras: list[str] = []
    for p in paras:
        first_line = p.splitlines()[0].strip().lower()
        # Si le paragraphe est court et commence par un mot-clé de stat, c'est l'en-tête stats
        if len(p) < 120 and any(first_line.startswith(pref) for pref in STAT_LINE_PREFIXES):
            continue
        lore_paras.append(re.sub(r"\s+", " ", p))
    return "\n\n".join(lore_paras)


def format_upgrade_desc(rr: str, emplacement: str, mod_txt: str, lore: str) -> str:
    """Construit la description VF propre d'une amélioration modifiée."""
    if rr.startswith("u_a_over_"):
        header = "Spécial : Amélioration d'armure (Sur-couche — Armure intermédiaire uniquement)"
    elif rr.startswith("u_a_unde_"):
        num = int(rr.split("_")[-1]) if rr.split("_")[-1].isdigit() else 0
        if num >= 19:
            header = "Spécial : Amélioration d'armure (Sous-couche — Armure intermédiaire uniquement)"
        elif num in {4, 5, 10, 11, 16, 17}:
            header = "Spécial : Amélioration d'armure (Sous-couche — Armure lourde / intermédiaire)"
        else:
            header = "Spécial : Amélioration d'armure (Sous-couche — Armure légère / lourde / intermédiaire)"
    elif rr.startswith("u_l_crys_"):
        header = "Spécial : Cristal d'amélioration, sabre laser"
    elif rr.startswith("u_l_"):
        header = f"Spécial : Amélioration, sabre laser ({emplacement})"
    elif rr.startswith("u_m_"):
        header = f"Spécial : Amélioration, arme de mêlée ({emplacement})"
    elif rr.startswith("u_r_"):
        header = f"Spécial : Amélioration, arme à distance ({emplacement})"
    else:
        header = f"Spécial : Amélioration ({emplacement})"

    stats_lines = "\n".join(f"• {part.strip()}" for part in mod_txt.split(",") if part.strip())
    parts = [header, stats_lines]
    if lore:
        parts.append(lore)
    return "\n\n".join(p for p in parts if p)


def format_gear_desc(nom: str, mod_txt: str, lore: str) -> str:
    """Construit la description VF propre d'un équipement modifié (6 CSV)."""
    header = f"Effets (Overhaul) :\n• " + "\n• ".join(seg.strip() for seg in mod_txt.split(";") if seg.strip())
    if lore:
        return f"{header}\n\n{lore}"
    return header


def populate_csv(csv_path: Path, inst: Installation, tlk, is_upgrades: bool) -> int:
    with open(csv_path, encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.reader(fh))
    if not rows:
        return 0
    header = rows[0]
    if "Description (mod)" not in header:
        header.append("Description (mod)")
    desc_idx = header.index("Description (mod)")
    h = {c.strip(): i for i, c in enumerate(header)}
    mod_idx = h["Changement (mod)"]
    emp_idx = h.get("Emplacement")

    updated = 0
    for r in rows[1:]:
        while len(r) <= desc_idx:
            r.append("")
        rr = r[0].strip().lower()
        mod_txt = r[mod_idx].strip() if len(r) > mod_idx else ""
        if not rr or not mod_txt or mod_txt.lower() in ("inchangé", "inchange", "-"):
            continue
        if is_upgrades and not rr.startswith("u_"):
            continue

        # Récupérer le lore VF vanilla depuis l'UTI du jeu
        lore = ""
        res = inst.resource(rr, ResourceType.UTI)
        if res:
            uti = read_uti(res.data)
            if uti.description.stringref >= 0:
                entry = tlk.get(uti.description.stringref)
                if entry:
                    lore = extract_lore_paragraph(entry.text)
        elif is_upgrades and rr.startswith(("u_a_over_", "u_a_unde_")):
            lore = (
                "Amélioration combinée conçue exclusivement pour les armures intermédiaires. "
                "Nécessite un établi équipé des outils adéquats."
            )

        if is_upgrades:
            emp = r[emp_idx].strip() if emp_idx is not None and len(r) > emp_idx else ""
            r[desc_idx] = format_upgrade_desc(rr, emp, mod_txt, lore)
        else:
            nom = r[1].strip() if len(r) > 1 else rr
            r[desc_idx] = format_gear_desc(nom, mod_txt, lore)
        updated += 1

    with open(csv_path, "w", encoding="utf-8-sig", newline="") as fh:
        csv.writer(fh).writerows(rows)
    return updated


def main() -> None:
    inst = Installation(GAME_PATH)
    tlk = read_tlk(GAME_PATH / "dialog.tlk")
    n_up = populate_csv(UPGRADES_CSV, inst, tlk, is_upgrades=True)
    print(f"[OK] {UPGRADES_CSV.name} : {n_up} descriptions remplies dans `Description (mod)`")
    total_gear = 0
    for path in GEAR_CSVS:
        n = populate_csv(path, inst, tlk, is_upgrades=False)
        print(f"[OK] {path.name} : {n} descriptions remplies dans `Description (mod)`")
        total_gear += n
    print(f"=== TOTAL : {n_up + total_gear} descriptions générées dans les CSV ===")


if __name__ == "__main__":
    main()
