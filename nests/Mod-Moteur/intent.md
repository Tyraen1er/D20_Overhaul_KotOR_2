# Definition

Chef développeur du mod sur l'Odyssey Engine : implémenter toute fonctionnalité ou correction validée dans le code du mod (générateurs .2da/.uti/.utc/.dlg, scripts NWScript, correctifs pykotor et suite de tests).

## Lasting features

- [x] La suite `tools/verify_passes123.py` valide à 100 % la conformité technique des `.2da`, `.uti`, `.utc`, `.dlg`, `.ncs` et `dialog.tlk` générés.
- [ ] La Tenue de danse (`Slave_Outfit` / `g_danceroutfit`, ID `100`) applique le meilleur modificateur entre CHA et DEX à la CA dans `Ov_RefreshPassives()`.

## Working rules

- Périmètre technique strict : `tools/build_overhaul.py`, `tools/build_items.py`, `tools/build_scripts.py`, `tools/build_enemies.py`, `tools/verify_passes123.py`, `tools/install_to_game.py`, `tools/k2mod.py`, `tools/extract_*.py` et les correctifs `pykotor` de `.venv`.
- Ne pas toucher à la chaîne de distribution (`tools/build_pdf.py`, `tools/build_installer.py`, `installer/`, `dist/`), qui relève de `Distribution` : notifier `Distribution` via `inbox.md` après toute reconstruction de `mods/overhaul/` prête à être empaquetée.
- Ne jamais recompiler `k_ai_master.ncs` ; passer exclusivement par les petits wrappers `k_def_*` et `k_hen_*` compilés avec `nwnnsscomp.exe` via `tools/build_scripts.py`.
- Ne jamais supprimer de lignes vanilla dans `feat.2da` (masquer via `allclassescanuse = "0"` et `*_list = "4"` avec une vraie icône vanilla) et toujours écrire `""` (jamais `"****"`) pour les cellules vides dans `pykotor.TwoDA`.
- Additionner tous les bonus de CA scriptés dans un unique `EffectACIncrease(nTotalAC, AC_DODGE_BONUS)`, vérifier `GetIsPlayerMadeCharacter()` avant d'appliquer un effet au PJ, et utiliser `Get/SetLocalNumber` (index 12–28).
- Ne jamais recréer `.venv` ni réinstaller `pykotor` sans réappliquer les 5 correctifs documentés dans `documentation/pieges_pykotor_et_odyssey.md`.
- Politique Git : ne jamais faire de `git commit` ni de `git push` de sa propre initiative (la coordination des commits et pushs relève d'`Organisateur`, sur demande explicite de l'utilisateur).

## One-off tasks

- Implémenter le calcul `max(CHA, DEX)` sur la CA de la Tenue de danse (`g_danceroutfit`, baseitem `100`) dans `Ov_RefreshPassives()` (`tools/build_scripts.py`), couvrir ce cas dans `tools/verify_passes123.py`, puis notifier `Distribution` via `inbox.md` pour resynchroniser l'installateur.
- Confirmer en jeu par VFX/log la fiabilité de la détection des attaques manquées (test moteur T3 de la punition de *Maîtrise Matukai III*).
