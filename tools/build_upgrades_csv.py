# -*- coding: utf-8 -*-
"""Génère « Kotor 2 - rééquilibrage - WIP Améliorations.csv » :
tous les items d'amélioration d'armes (mêlée, distance, sabres, cristaux) et d'armures.

Sources : cache de tools/extract_items.py (items.json + loot.json dans itemdb/).
Usage : .venv\\Scripts\\python.exe tools\\build_upgrades_csv.py
"""
import json
import os

CACHE = r"C:\Users\emman\AppData\Local\Temp\opencode\itemdb"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DST = os.path.join(ROOT, "Kotor 2 - rééquilibrage - WIP Améliorations.csv")

items = json.load(open(os.path.join(CACHE, "items.json"), encoding="utf-8"))
loot = json.load(open(os.path.join(CACHE, "loot.json"), encoding="utf-8"))

# familles : (titre de section, fonction de tri interne)
def num(rr):
    tail = rr.rsplit("_", 1)[-1]
    return int(tail) if tail.isdigit() else 999

FAMILIES = [
    ("ARMES DE MÊLÉE — LAMES", lambda k: k.startswith("u_m_edge")),
    ("ARMES DE MÊLÉE — CELLULES D'ÉNERGIE", lambda k: k.startswith("u_m_cell")),
    ("ARMES DE MÊLÉE — POIGNÉES (GARDES)", lambda k: k.startswith("u_m_grip")),
    ("ARMES À DISTANCE — CHAMBRAGES", lambda k: k.startswith("u_r_firi")),
    ("ARMES À DISTANCE — CELLULES D'ÉNERGIE", lambda k: k.startswith("u_r_powe")),
    ("ARMES À DISTANCE — LUNETTES", lambda k: k.startswith("u_r_targ")),
    ("SABRES LASER — ÉMETTEURS", lambda k: k.startswith("u_l_emit")),
    ("SABRES LASER — LENTILLES", lambda k: k.startswith("u_l_lens")),
    ("SABRES LASER — CELLULES D'ÉNERGIE", lambda k: k.startswith("u_l_cell")),
    ("SABRES LASER — CRISTAUX DE COULEUR", lambda k: k.startswith("u_l_colo")),
    ("SABRES LASER — CRISTAUX D'AMÉLIORATION", lambda k: k.startswith("u_l_crys")),
    ("ARMURES — SURCOUCHES", lambda k: k.startswith("u_a_over")),
    ("ARMURES — SOUS-COUCHES", lambda k: k.startswith("u_a_unde")),
]

def loot_cell(rr):
    L = loot.get(rr)
    if not L:
        return "—"
    t = L.get("tier", "")
    n = L.get("plvl_normal")
    r = L.get("plvl_rare")
    if n is None and r is None:
        return "—"
    txt = "palier %s" % t
    if n is not None:
        txt += " niv. %s+" % n
        if r is not None:
            txt += " (rare dès %s)" % r
    elif r is not None:
        txt += " rare dès %s" % r
    return txt

rows = [["ResRef", "Nom", "Emplacement", "Tier", "Effets (vanilla)", "Loot aléatoire", "Changement (mod)"]]
seen = set()
for title, pred in FAMILIES:
    keys = sorted([k for k in items if pred(k)], key=num)
    if not keys:
        continue
    rows.append([title, "", "", "", "", "", ""])
    for k in keys:
        it = items[k]
        L = loot.get(k, {})
        effets = ", ".join(it.get("props", [])) or "—"
        rows.append([
            k,
            it.get("nom", ""),
            L.get("sub", ""),
            str(L.get("tier", "")) or "—",
            effets,
            loot_cell(k),
            "",
        ])
        seen.add(k)

# reste éventuel (ex : pièces non couvertes ci-dessus)
reste = sorted([k for k in items if k.startswith("u_") and k not in seen])
if reste:
    rows.append(["AUTRES PIÈCES D'AMÉLIORATION", "", "", "", "", "", ""])
    for k in reste:
        it = items[k]
        L = loot.get(k, {})
        rows.append([k, it.get("nom", ""), L.get("sub", ""), str(L.get("tier", "")) or "—",
                     ", ".join(it.get("props", [])) or "—", loot_cell(k), ""])

import csv
with open(DST, "w", encoding="utf-8-sig", newline="") as f:
    csv.writer(f).writerows(rows)
print("OK :", DST, "-", len(rows) - 1, "lignes")
