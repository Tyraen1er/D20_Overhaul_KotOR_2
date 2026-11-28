# Documentation — Équilibrage & Game Design

## Quand lire quoi (fiches thématiques dans `documentation/`)

- **Couche utilisateur (priorité absolue)** : les 12 fichiers dans `csv/fr/` (`Kotor 2 - rééquilibrage - *.csv`). En cas de divergence entre une fiche ci-dessous et un CSV, **le CSV fait foi** et la fiche doit être resynchronisée.
- **Classes, dons, postures, Spé Carac ou pouvoirs de Force** → lire [`documentation/classes_dons_et_pouvoirs.md`](documentation/classes_dons_et_pouvoirs.md) (budgets `22/18/15` dons & `12/16/24` pouvoirs, gating, 4 postures, 8 familles, 6 Spé Carac, pouvoirs standards & prestige).
- **Armes, établi, craft, Cristal personnel ou armures/RD** → lire [`documentation/equipement_etabli_et_armures.md`](documentation/equipement_etabli_et_armures.md) (plafonds `+2/+5/+10`, cloisonnement des slots, 6 reliques, armures & dégradé de pouvoirs).
- **Bestiaire, familles d'ennemis, boucliers ou boss** → lire [`documentation/ennemis_et_boss.md`](documentation/ennemis_et_boss.md) (principes P1–P5 et matrice de scaling continu sur `Niv. PJ`). Inventaire brut des 367 templates dans `_reference/analyses_kotor/tableau_ennemis.md`.
- **Cibles DPR/TTK/Survie, formules de DD ou choix déjà écartés** → lire [`documentation/contrat_mathematique.md`](documentation/contrat_mathematique.md) (table §9, DD grenades/On-Hit/Spé, garde-fous anti-régression).
- **Analyses d'extraction & références JdR** : `_reference/analyses_kotor/` et `_reference/jdr/`.

## Outils de simulation

- `tools/dpr_check.py` + `tools/dpr_data.json` : simulateur DPR/TTK par build contre les boss étalons Early (Niv. 8, RD 2), Mid (Niv. 16, RD 5) et Late (Niv. 26, RD 8). Toute constante d'essai s'édite dans `dpr_data.json`, jamais dans le moteur Python.
- `tools/dpr_review.py` : matrice `4 postures × 3 phases × contextes mêlée/distance/bure` (dernier rapport : [`content/dpr_review_2026-11-26.md`](content/dpr_review_2026-11-26.md)).
- **Piège d'encodage des rapports** : `dpr_review.py` n'écrit rien, il affiche sur `stdout` (UTF-8 sous `python -X utf8`). Sous Windows PowerShell 5.1, `>` comme `| Out-File -Encoding utf8` décodent d'abord ces octets en CP850 (`[Console]::OutputEncoding`) : accents corrompus, puis UTF-16 LE pour `>` — fichier illisible par les outils (cas du rapport du 26/11, réparé le 28/11). Pour produire un rapport : capturer `stdout` en octets depuis Python (`subprocess.run([...], capture_output=True).stdout` puis `write_bytes`), ce qui donne de l'UTF-8 sans BOM, fins de ligne LF, comme le dépôt.
- `tools/k2balance.py` : constantes et courbes de référence boss/autobalance.
