# Handoff — Session du 28/11/2026

## Ce qui a été fait

- Initialisation du nid, puis corrections demandées par l'utilisateur (relais `Organisateur`), toutes réalisées et vérifiées :
  - `docs/HOW_TO_TRANSLATE.md` : chemin `csv/en/` corrigé (l.82) et 6 réponses au menu gamorréen au lieu de 3 (l.47) ;
  - description EN de *Fury* : `≤` remplacé par `<=` dans le CSV EN, et `sanitize_tlk` appliqué aux chaînes EN de `append_en.tlk` dans `tools/build_installer.py` (garde anti-récidive) ;
  - écran d'accueil de l'installateur (`generate_info_rtf()`, EN et FR) : 6 pouvoirs de classe de prestige refondus dont 2 inédits, comme dans les guides ;
  - installateur et archive `dist/` resynchronisés par `tools\build_installer.py -z`.
- Vérifications : archive de 1008 fichiers tous identiques au dépôt ; parité FR/EN intacte (232 chaînes TLK, 51 + 9 nœuds de dialogue traduits) ; `verify_passes123.py` inchangé (179 réussites, les 6 mêmes échecs, suivis par `Mod-Moteur`).
- PDF non régénérés : ils étaient déjà postérieurs à la dernière modification des Markdown.
- Le problème d'encodage ne touchait qu'une cellule : bilan fait sur les colonnes lues par l'installateur dans les 9 CSV EN et sur les textes de `tools/build_installer.py`.

## État pour la suite

- Aucune tâche en cours. `intent.md` volontairement inchangé.
- Fichiers modifiés, non commités : `csv/en/Kotor 2 - Rebalancing - Force Powers.csv`, `docs/HOW_TO_TRANSLATE.md`, `tools/build_installer.py`, 5 fichiers d'`installer/` (`HOW_TO_TRANSLATE.md`, `Readme.rtf`, `tslpatchdata/append_en.tlk`, `info_en.rtf`, `info_fr.rtf`) et `dist/KotOR2_D20_Overhaul_v1.0.zip`.
- La chaîne `build_installer.py -z` a été validée pour la première fois depuis la migration des chemins (`tools/paths.py`).
- L'utilisateur attend qu'un nid reste dans le périmètre demandé.
