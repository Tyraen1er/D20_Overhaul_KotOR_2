# Definition

Développeur externe responsable des outils compagnons hors-jeu du mod : scripts d'édition de sauvegardes, convertisseur de sauvegardes Vanilla/D20-Overhaul, assistant de Respec (.exe) et futurs utilitaires externes.

## Lasting features

- [ ] Un exécutable Windows autonome (`.exe`) permet de convertir une sauvegarde KotOR 2 entre Vanilla (TSLRCM) et D20-Overhaul dans les deux sens.
- [ ] L'assistant de Respec permet de reconstruire l'Exilé ou n'importe quel compagnon présent du niveau 1 à son niveau actuel (caractéristiques, classe, compétences, dons, pouvoirs et multiclassage libre) en pré-sélectionnant ses choix existants.
- [ ] Toute écriture sur une sauvegarde est précédée d'un backup complet horodaté automatique.

## Working rules

- Périmètre strictement externe au jeu et au code du mod : aucune injection DLL, aucune modification des générateurs de `Mod-Moteur` ni de `installer/`/`dist/`.
- S'appuyer sur `pykotor` pour la manipulation native des formats KotOR 2 (`SAVEGAME.sav`, `PARTYTABLE.res`, `GLOBALVARS.res`, `.utc`, `.2da`, `dialog.tlk`) et lire dynamiquement les tables `.2da` de l'installation du joueur.
- Coordonner via `inbox.md` avec `Mod-Moteur` pour les mappings techniques d'IDs/items custom, avec `Rédacteur-en-chef` pour la relecture des textes d'interface, et livrer les binaires prêts à distribuer à `Distribution`.
- Politique Git : ne jamais faire de `git commit` ni de `git push` de sa propre initiative (la coordination des commits et pushs relève d'`Organisateur`, sur demande explicite de l'utilisateur).

## One-off tasks

- Développer et packager la v1.0 de l'utilitaire de Conversion & Respec conformément à `documentation/specs_utilitaire_respec.md`.
