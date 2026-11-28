# Plan — Mod-Moteur

1. Implémenter dans `Ov_RefreshPassives()` (`tools/build_scripts.py`) le différentiel `CHA - DEX` à la CA lorsque le personnage porte la *Tenue de danse* (`Slave_Outfit` / `g_danceroutfit`, baseitem `100`) et que `CHA > DEX` (cf. `nests/Equilibrage/documentation/equipement_etabli_et_armures.md` §3), recompiler avec `build_scripts.py`, ajouter un test dédié dans `tools/verify_passes123.py` et notifier `Distribution` via `inbox.md` pour resynchroniser l'installateur.
2. Mettre en place un test en jeu ciblé (VFX/retour visuel) pour confirmer la fiabilité du compteur `OnAttacked - OnDamage` sur les attaques manquées (**test T3**, punition de *Maîtrise Matukai III*).
