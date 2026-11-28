# Handoff — Session du 28/11/2026

## Ce qui a été fait

- Restructuration complète du dépôt (`D1`–`D4`) : racine épurée, `csv/fr/` & `csv/en/`, `tools/paths.py` + `BASE_TLK` sécurisé dans `_reference/tlk/`, suppression des reliquats Jalon 0, éclatement des monolithes `decisions_*.md` / `equilibrage_ennemis.md` en 4 fiches modulaires (`Equilibrage`) + `architecture_odyssey_et_limites.md` (`Mod-Moteur`) + `tableau_ennemis.md` (`_reference/analyses_kotor/`).
- Corrections techniques réalisées par les nids : rapport DPR réparé en UTF-8 (`Equilibrage`), `verify_passes123.py` 100 % au vert `187 PASSED, 0 FAILED` (`Mod-Moteur`), `HOW_TO_TRANSLATE.md` + `Fury` CP1252 + resync `installer/` & `dist/`.
- Clarification finale des responsabilités suite au renommage de `Lore-et-Distribution` en **`Rédacteur-en-chef`** :
  - Création du 7e nid **`Distribution`** via `create_nest` (responsable du produit fini : PDF, installateur TSLPatcher, dépendances de packaging et zippage final `dist/`, sans toucher au code interne du mod).
  - Réécriture coordonnée des 7 `intent.md` (`Organisateur`, `Mod-Moteur`, `Utilitaire`, `Equilibrage`, `Rédacteur-en-chef`, `Distribution`, `Retours-Utilisateurs`), ajout de la zone grise `build_pdf.py` (`Rédacteur-en-chef` ↔ `Distribution`), de la politique Git (commits/pushs coordonnés par `Organisateur` uniquement sur demande explicite, releases par `Distribution`), et nettoyage de toutes les références obsolètes à `Lore-et-Distribution`.
  - Nettoyage des `choices.md` : `D4` d'`Utilitaire` retiré et tranché (`tools/utilitaire/` + `.venv` commun, consigné dans `Utilitaire/documentation.md` et `Organisateur/documentation.md`) ; projet en réserve « Renommage de `verify_passes123.py` » rapatrié de `Mod-Moteur` vers `Organisateur/choices.md`.

## État pour la suite

- `Distribution` est prêt sur le canevas ; l'ensemble de la restructuration, des 7 nids et des corrections techniques est committé et poussé sur GitHub.
