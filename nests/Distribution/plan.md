# Plan — Distribution

Aucune publication immédiate en attente : les PDF, l'installateur `installer/` et l'archive `dist/` sont synchronisés et `verify_passes123.py` est à 100 % (`187 PASSED, 0 FAILED`).

À la prochaine demande de release (notifiée via `inbox.md` par `Mod-Moteur`, `Rédacteur-en-chef` ou `Utilitaire`) :

1. Régénérer les PDF si les guides Markdown ont changé (`.\.venv\Scripts\python.exe tools\build_pdf.py`).
2. Reconstruire l'installateur et l'archive finale (`.\.venv\Scripts\python.exe tools\build_installer.py -z`).
3. Vérifier `.\.venv\Scripts\python.exe tools\verify_passes123.py` (`0 FAILED`) et contrôler le contenu de l'archive dans `dist/`.
