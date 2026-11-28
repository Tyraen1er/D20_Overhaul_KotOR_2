# Handoff — Distribution

- Initialisation du nid effectuée : lecture complète des 6 fichiers canoniques et audit de la chaîne (`tools/build_pdf.py`, `tools/build_installer.py`, `tools/paths.py`, `docs/`, `installer/`, `dist/`).
- Vérifications confirmées :
  - Dépendances présentes : Chrome & Edge headless, `K2CP_v1.6.3/INSTALL.exe` et `_reference/.../TSLPatcher.exe`, `.venv`.
  - Livrables synchronisés : PDFs FR/EN (`docs/`), `installer/`, `dist/KotOR2_D20_Overhaul_v1.0.zip` (1 008 entrées).
  - Contrôle qualité : `tools/verify_passes123.py` → `187 PASSED, 0 FAILED`.
- `documentation.md` complété avec les dépendances exactes (Chrome/Edge headless), l'exclusion des fichiers locaux `installer/backup/` et `installlog.txt` dans le zip, et les emplacements de bump de version dans `build_installer.py`.
- Piste d'un auto-update GitHub explorée en discussion (wrapper `.exe` / `.bat` autour de `INSTALL.exe`), puis écartée par l'utilisateur.
- Aucune tâche en attente ni décision ouverte (`inbox.md` et `choices.md` vides).
