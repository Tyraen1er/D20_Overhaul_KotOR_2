# Documentation — Chaîne de Fabrication & Distribution

## Périmètre du nid

`Distribution` est le **responsable du produit fini** : il transforme les sources produites par `Mod-Moteur` (`mods/overhaul/`), `Rédacteur-en-chef` (`docs/*.md`, `csv/en/`, `HOW_TO_TRANSLATE.md`) et `Utilitaire` (futurs `.exe`) en livrables prêts à publier (`docs/*.pdf`, `installer/`, `dist/`), sans toucher au code interne du mod.

## Chaîne de fabrication

1. **Guides PDF FR & EN (`tools/build_pdf.py`)** :
   - Commande : `.\.venv\Scripts\python.exe tools\build_pdf.py`
   - Convertisseur Markdown → HTML autonome (stdlib Python uniquement, HTML temporaire purgé après rendu) puis impression A4 via Chrome/Edge headless (`--headless=new --print-to-pdf`).
   - Produit `docs/KotOR2_D20_Overhaul_Guide_Joueur_FR.pdf` et `docs/KotOR2_D20_Overhaul_Player_Guide_EN.pdf` à partir des Markdown de `docs/` et `docs/en/`.
2. **Installateur TSLPatcher & archive de release (`tools/build_installer.py`)** :
   - Commande : `.\.venv\Scripts\python.exe tools\build_installer.py -z` *(ne pas passer `-f` : la reconstruction de `mods/overhaul/` relève de `Mod-Moteur`)*.
   - Nettoie et régénère `installer/tslpatchdata/` (`namespaces.ini` EN par défaut + FR, `changes_en/fr.ini`, `append_en/fr.tlk`, 10 `.2da` TSLRCM, dialogues localisés, `.uti` bilingues EN+FR, validations structurelles automatiques), copie `INSTALL.exe` et `HOW_TO_TRANSLATE.md`, génère `Readme.rtf` et l'archive `dist/KotOR2_D20_Overhaul_v1.0.zip` (1 008 entrées sous `KotOR2_D20_Overhaul/`).
   - `build_release_zip()` exclut volontairement les artefacts locaux de test présents dans `installer/` (`backup/`, `installlog.txt`).
   - Textes générés à l'assemblage dans `tools/build_installer.py` (jamais éditer `installer/` à la main) : `generate_info_rtf()` (`info_en.rtf`, `info_fr.rtf`, `Readme.rtf`), `generate_usage_readme_txt()` (`README.txt` du zip), `EN_TLK_FALLBACK_MAP` (33 chaînes) et `EN_DLG_MAP` (`kreia.dlg`, `ov_gam_conv.dlg`).
   - **Bump de version** : la version (`v1.0` / `Version 1.0`) est en dur dans `tools/build_installer.py` (`RELEASE_ZIP_NAME`, `generate_info_rtf()`, `generate_usage_readme_txt()`).
   - **Garde CP1252** : les chaînes anglaises de `append_en.tlk` passent par `sanitize_tlk` (importé de `build_overhaul.py`) afin qu'aucun caractère hors Windows-1252 (`≤`, `≥`, `→`) n'apparaisse en `?` en jeu.
   - Miniature de présentation : `docs/assets/D20 Overhaul Thumbnail.jpg`.
3. **Contrôle final avant publication** :
   - Exécuter `.\.venv\Scripts\python.exe tools\verify_passes123.py` et vérifier `VERIFICATION SUMMARY: ... 0 FAILED` (le script retourne un code de sortie `0` même en cas d'échec ; état actuel : `187 PASSED, 0 FAILED`).

## Dépendances de packaging

- **Rendu PDF** : Google Chrome (`C:\Program Files\Google\Chrome\Application\chrome.exe`, présent) ou fallback Microsoft Edge (`msedge.exe`, présent) ; aucune dépendance Python externe.
- **`TSLPatcher.exe`** : source prioritaire `C:\Users\emman\Desktop\kotor 2 updates\K2CP_v1.6.3\INSTALL.exe` (présente), repli dans `_reference/autres_mods/Content Pack-57-1-67-1616632489/TSLPatcher.exe` (présent).
- **Environnement `.venv` partagé** : utilisé par `build_installer.py` (`pykotor`) et `verify_passes123.py` (attention : contient 5 patchs locaux sur `pykotor`, gérés par `Mod-Moteur` — ne jamais réinstaller `pykotor` ni recréer `.venv`).
