# Definition

Coordonner l'organisation globale du projet KotOR 2 D20-Overhaul : maintenir une architecture de fichiers saine, structurer le projet en nids cohérents sans doublon d'information et répartir les tâches entre eux.

## Lasting features

- [x] Le dépôt dispose d'une architecture de fichiers saine, lisible et synchronisée avec tous les scripts de build et de vérification.
- [x] Les différents aspects du projet sont répartis dans 6 nids opérationnels dédiés (`Mod-Moteur`, `Utilitaire`, `Equilibrage`, `Rédacteur-en-chef`, `Distribution`, `Retours-Utilisateurs`) aux périmètres stricts et sans duplication.
- [x] Les tâches ouvertes du projet sont identifiées et distribuées dans les nids qui en ont la responsabilité.

## Working rules

- Une information ne vit qu'à un seul endroit : dans le nid qui en est directement responsable ; les autres nids utilisent des liens.
- Ne jamais modifier le contenu des fichiers CSV de rééquilibrage (couche utilisateur) sans validation directe de l'utilisateur.
- Tout déplacement ou renommage de fichier du dépôt doit être accompagné de la mise à jour des chemins dans `tools/paths.py` (et scripts associés) puis validé par `tools/verify_passes123.py` et `tools/dpr_check.py --selftest`.
- Frontières clés : `Organisateur` gouverne la structure des fichiers et des nids ; `Distribution` gère la fabrication du produit fini sans toucher au code du mod ; `Retours-Utilisateurs` filtre et route les retours joueurs.
- Politique Git : aucun nid ne fait de `git commit` ni de `git push` sans demande explicite de l'utilisateur ; `Organisateur` coordonne les commits propres et les pushs sur GitHub à la demande (sauf commits/tags de release gérés par `Distribution` à la demande).

## One-off tasks
