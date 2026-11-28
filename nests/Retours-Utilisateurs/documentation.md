# Documentation — Triage des Retours Utilisateurs & Routage Inter-Nids

## Annuaire de routage vers les nids métier

- **[Equilibrage](../Equilibrage/intent.md)** : valeurs chiffrées, scripts de test de builds (`dpr_check.py`), courbes DPR/TTK, durées des boss, budgets et statistiques d'armes/armures/ennemis.
- **[Mod-Moteur](../Mod-Moteur/intent.md)** : chef développeur — bugs en jeu, scripts `.ncs`, générateurs `.2da`/`.uti`/`.utc`/`.dlg`, prérequis, compatibilité TSLRCM.
- **[Rédacteur-en-chef](../Rédacteur-en-chef/intent.md)** : descriptions ambiguës ou erronées en jeu (`dialog.tlk`), ton et cohérence lore Star Wars / KotOR, traductions EN, guides joueur Markdown.
- **[Distribution](../Distribution/intent.md)** : responsable du produit fini — génération des PDF FR/EN, installateur `INSTALL.exe` / TSLPatcher, dépendances de packaging et archive `dist/`.
- **[Utilitaire](../Utilitaire/intent.md)** : dev externe — outils hors-jeu (conversion de sauvegardes `Vanilla ↔ Overhaul`, respec, scripts d'édition de sauvegardes).
- **[Organisateur](../Organisateur/intent.md)** : uniquement si un retour révèle un besoin de nouveau nid ou de réorganisation structurelle du dépôt.

## Grille de diagnostic rapide d'un bug signalé par un joueur

Avant de conclure à un bug du mod, vérifier les causes classiques sur KotOR 2 :

1. **Sauvegarde entamée en Vanilla** : supprimer ou décaler des dons existants sur une partie en cours crée des incohérences tant que l'utilitaire de Conversion/Respec n'a pas été utilisé (nouvelle partie recommandée en v1.0).
2. **Mode d'installation** : le joueur a-t-il bien lancé `INSTALL.exe` (TSLPatcher, choix de langue EN ou FR) sur la racine KotOR 2, après TSLRCM ?
3. **Conflits `Override/`** : présence d'autres mods écrasant `feat.2da`, `spells.2da`, `baseitems.2da`, `k_sp1_generic.ncs`, `k_def_*` ou `k_hen_*`.
4. **Comportements intentionnels souvent pris pour des bugs** :
   - Les 5 autres arbres de *Spécialisation de Caractéristique* restent cliquables au level-up (limite moteur de `exclusion` dans `feat.2da`), mais seul le **premier arbre acquis** produit ses effets (documenté dans le guide).
   - Le critique confirmé en embuscade furtive affiche ses dégâts doublés sur une **seconde ligne** dans le journal de combat.
   - Les armures *Ubese* et *Zeison Sha / Jal Shey* suivent désormais les mêmes restrictions de pouvoirs que les armures légères standard (décision volontaire, plus d'exception « Force-friendly »).
