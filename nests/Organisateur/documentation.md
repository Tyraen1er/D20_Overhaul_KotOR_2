# Documentation — Architecture & Organisation du Projet

## 1. Topologie des nids (mise à jour le 28/11/2026)

Le projet est structuré en **7 nids** (1 méta-nid d'architecture + 6 nids opérationnels aux frontières strictes) :

- **[Organisateur](intent.md)** : architecture des fichiers du dépôt (`tools/paths.py`, dossiers), cohérence globale des nids et règles transverses.
- **[Mod-Moteur](../Mod-Moteur/intent.md)** : chef développeur du mod — implémentation Odyssey/NWScript, générateurs Python (`build_overhaul.py`, `build_items.py`, `build_scripts.py`, `build_enemies.py`), extraction (`k2mod.py`, `extract_*.py`), correctifs `.venv` de `pykotor` et suite de vérification (`verify_passes123.py`). Ne touche pas au packaging `installer/`/`dist/`/PDF.
- **[Utilitaire](../Utilitaire/intent.md)** : dev externe — outils compagnons hors-jeu (scripts d'édition de sauvegardes, convertisseur `Vanilla ↔ Overhaul`, assistant Respec `.exe`, futurs outils).
- **[Equilibrage](../Equilibrage/intent.md)** : game design chiffré, scripts de test de builds (`dpr_check.py`, `dpr_data.json`, `dpr_review.py`, `k2balance.py`), viabilité des changements et valeurs mécaniques des 12 CSV FR (`csv/fr/`).
- **[Rédacteur-en-chef](../Rédacteur-en-chef/intent.md)** : rédacteur & gardien du lore Star Wars / KotOR — descriptions en jeu, dialogues, cohérence narrative, traduction EN (`csv/en/`), guides joueur Markdown (`docs/*.md`, `docs/en/*.md`, `HOW_TO_TRANSLATE.md`). Aucun code Python de build ni packaging.
- **[Distribution](../Distribution/intent.md)** : responsable du produit fini — gère la chaîne de fabrication sans toucher au code interne du mod : génération des PDF (`tools/build_pdf.py`), assemblage de l'installateur TSLPatcher (`tools/build_installer.py`, `installer/`), dépendances de packaging et zippage final (`dist/`).
- **[Retours-Utilisateurs](../Retours-Utilisateurs/intent.md)** : filtre communauté — juge la pertinence des retours joueurs avec l'utilisateur et, après validation, dispatche les tâches dans les `inbox.md` des 5 autres nids opérationnels.

### Frontières clés anti-collision

- **Code du mod vs Produit fini (`Mod-Moteur` vs `Distribution`)** : `Mod-Moteur` code et génère `mods/overhaul/` + maintient `verify_passes123.py` ; `Distribution` possède tous les scripts de génération finale et de packaging (`build_installer.py`, `build_pdf.py`, futurs scripts d'export/packaging comme Excel, évolutions de l'installateur) et produit `installer/` + `dist/` (sans `-f`, avec `verify_passes123.py` en contrôle seul).
- **Zone grise assumée sur `tools/build_pdf.py` (`Rédacteur-en-chef` ↔ `Distribution`)** : `Rédacteur-en-chef` est autorisé à modifier `build_pdf.py` pour l'aspect éditorial/mise en page des guides ; `Distribution` gère sa régénération, ses dépendances et l'empaquetage final.
- **Textes & Lore vs Mécaniques (`Rédacteur-en-chef` vs `Equilibrage`)** : `Equilibrage` gouverne les valeurs chiffrées et tests de builds ; `Rédacteur-en-chef` gouverne la plume, le lore, les descriptions, les guides Markdown et les traductions EN.
- **Architecture vs Retours (`Organisateur` vs `Retours-Utilisateurs`)** : `Organisateur` gère la structure du dépôt et des nids ; `Retours-Utilisateurs` évalue et route les retours joueurs.

## 2. Architecture assainie du dépôt

- **Racine (2 fichiers)** : `README.md` (vitrine GitHub et carte du dépôt) et `.gitignore` (ignore `logs/*.log`, `.trieste-nests/`, `mods/overhaul/`, `installer/backup/`, `.venv/`, `tools/KSE_353/`).
- **`csv/fr/` & `csv/en/`** : 12 CSV français (couche utilisateur) et 12 CSV anglais (`Kotor 2 - Rebalancing - *.csv`).
- **`tools/`** : `paths.py` (source unique des chemins du dépôt) + 17 scripts actifs (les 3 scripts obsolètes ont été retirés) + futur paquet `tools/utilitaire/` (acté le 28/11/2026, partageant le `.venv` commun pour embarquer les 5 patchs `pykotor` sans duplication) + `KSE_353/` (ignoré).
- **`docs/`** : guides joueur FR (`docs/*.md`), EN (`docs/en/*.md`), PDF générés, `HOW_TO_TRANSLATE.md` et `docs/assets/D20 Overhaul Thumbnail.jpg`.
- **`mods/`** : uniquement `mods/overhaul/` (sortie de build ignorée + 4 mappings `.json` suivis par Git). Les anciens bacs à sable Jalon 0 ont été supprimés.
- **`installer/` & `dist/`** : installateur TSLPatcher EN/FR et archive `v1.0`.
- **`_reference/`** : ressources vanilla (`2da/`, `scripts/`, `tlk/dialog.tlk.bak` + `feat.2da.bak`, `autres_mods/` avec `nwnnsscomp.exe` et `TSLPatcher.exe`), analyses extraites (`analyses_kotor/`, dont `tableau_ennemis.md` généré par `tools/extract_enemies.py`) et synthèses JdR unifiées (`jdr/`).
- **`nests/`** *(suivi dans Git)* : les 6 nids contenant leurs documents de référence modulaires sans doublon :
  - `Equilibrage/documentation/` : 4 fiches courtes (`classes_dons_et_pouvoirs.md`, `equipement_etabli_et_armures.md`, `ennemis_et_boss.md`, `contrat_mathematique.md`) + rapport `content/dpr_review_2026-11-26.md`.
  - `Mod-Moteur/documentation/` : `pieges_pykotor_et_odyssey.md` et `architecture_odyssey_et_limites.md`.
  - `Utilitaire/documentation/` : `specs_utilitaire_respec.md`.

## 3. Invariants techniques

- **Chemins centralisés** : `tools/paths.py` définit `BASE_TLK`, `CSV_FR_DIR`, `CSV_EN_DIR`, `REF_2DA`, `REF_ANALYSES_KOTOR`, `REF_JDR`, `TABLEAU_ENNEMIS_MD`, `OUT_MOD`, `OVR_DIR`, `INSTALLER_DIR`, `DIST_DIR`.
- **Environnement `.venv` critique** : `pykotor 2.3.12` contient 5 patchs locaux dans `.venv/Lib/site-packages/pykotor/` — ne jamais le recréer sans réappliquer ces correctifs (cf. `nests/Mod-Moteur/documentation/pieges_pykotor_et_odyssey.md`).
