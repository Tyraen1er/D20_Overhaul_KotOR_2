# Documentation — Moteur Odyssey, Scripts & Pipeline de Build

## Chaîne de compilation et de test

Toutes les commandes s'exécutent depuis la racine du projet avec `.venv\Scripts\python.exe` :

1. `tools/build_overhaul.py` : génère les `.2da` modifiés (`feat.2da`, `spells.2da`, `baseitems.2da`, `itemcreate.2da`, `itemcreatemira.2da`, `featgain.2da`, `classpowergain.2da`, `autobalance.2da`, `forceshields.2da`, `iprp_resistcost.2da`) et `dialog.tlk` FR dans `mods/overhaul/` + tables d'IDs (`feat_ids.json`, `spell_ids.json`, `baseitem_1m_map.json`).
2. `tools/build_items.py` : génère les `.uti` rééquilibrés (équipements, armes, 226 améliorations, 90 cristaux de l'Exilé, 69 jumeaux 1M `ov1m_*.uti` + `gamorrean_swap_map.json`) et le système d'Adaptateur Gamorréen (`ov_gam_adapt.uti`, `ov_gam_term.utp`, `ov_gam_conv.dlg`).
3. `tools/build_scripts.py` : génère et compile les scripts NWScript (`ov_inc_core.nss`, `ov_inc_powers.nss`, `ov_inc_gamswap.nss`, wrappers `k_def_*`/`k_hen_*`, `k_sp1_generic.ncs`, `k_sup_bands.ncs`, `k_sup_grenade.ncs`, `a_q_cryst_change.ncs`) via `nwnnsscomp.exe` dans `mods/overhaul/_compile_stage/`.
4. `tools/build_enemies.py` : applique l'habillage et les profils aux templates `.utc` ennemis.
5. `tools/verify_passes123.py` : exécute les 187 tests de non-régression (doit afficher `ALL CHECKS PASSED 100%!`).
6. `tools/install_to_game.py` : déploie dans le dossier Steam local pour test en jeu rapide.

## Références techniques essentielles (`documentation/`)

- **Correctifs `.venv` (`pykotor`) & pièges d'exécution en jeu** → lire [`documentation/pieges_pykotor_et_odyssey.md`](documentation/pieges_pykotor_et_odyssey.md) avant toute intervention sur `.venv`, `pykotor`, les `.2da` ou les scripts NWScript.
- **Ce qui est moddable vs hardcodé dans `swkotor2.exe` (offsets établi, `UpgradeLevel`, `forbiditemmask`, hooks `1005`/`1006`, `classes.2da`, leviers ennemis)** → lire [`documentation/architecture_odyssey_et_limites.md`](documentation/architecture_odyssey_et_limites.md).
- Chemins centralisés du dépôt : `tools/paths.py` (utilisé par les scripts de build).
- Ressources vanilla extraites : `_reference/scripts/` (638 `.nss`), `_reference/2da/` et `_reference/tlk/dialog.tlk.bak`.
