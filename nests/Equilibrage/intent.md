# Definition

Gérer les scripts de test de builds, la viabilité des changements d'équilibrage et le contrat mathématique du mod (progression, dons, pouvoirs, équipements, ennemis et valeurs mécaniques des CSV).

## Lasting features

- [x] Les postures, spécialisations d'armes, spécialisations de caractéristique et armures respectent les cibles DPR/TTK et de survie du contrat mathématique (combats de boss en 5 à 10 rounds).
- [x] Chaque grande famille d'ennemis impose une réponse tactique distincte avec un scaling continu indexé sur le niveau du personnage joueur.

## Working rules

- Périmètre technique strict : outils de simulation et d'analyse de builds (`tools/dpr_check.py`, `tools/dpr_data.json`, `tools/dpr_review.py`, `tools/k2balance.py`) et valeurs mécaniques des 12 CSV de `csv/fr/`. Ne jamais modifier le code de génération du mod (`Mod-Moteur`) ni la distribution (`Distribution`).
- Les fichiers CSV constituent la couche utilisateur : ne jamais modifier leurs valeurs mécaniques sans validation directe de l'utilisateur.
- Frontière avec `Rédacteur-en-chef` : `Equilibrage` gouverne les valeurs mécaniques, formules et paliers des CSV ; `Rédacteur-en-chef` gouverne les noms, descriptions littéraires, cohérence lore et traductions.
- Simuler tout ajustement chiffré avec `tools/dpr_check.py` et `tools/dpr_review.py`, mettre à jour la fiche concernée dans `documentation/`, puis notifier `Mod-Moteur` et `Rédacteur-en-chef` via leur `inbox.md` si une implémentation ou une mise à jour de texte est requise.
- Politique Git : ne jamais faire de `git commit` ni de `git push` de sa propre initiative (la coordination des commits et pushs relève d'`Organisateur`, sur demande explicite de l'utilisateur).

## One-off tasks
