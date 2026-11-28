# Documentation — Rédaction, Lore & Traduction

## Périmètre éditorial

1. **Textes et lore en jeu (FR & EN)** :
   - Colonnes descriptives des CSV FR (`csv/fr/`) et équivalents anglais dans `csv/en/` (`Kotor 2 - Rebalancing - *.csv`).
   - Identité narrative spécifique au mod : les 6 pouvoirs de prestige (*Stigmate de Force*, *Cicatrice de Force*, *Spectre de la Force*, *Affranchi de la Force*, *Déchirure de la Force*, *Écho des Liens*) s'adossent à la philosophie de Kreia et aux blessures de la Force propres à KotOR 2.
   - **Contrainte d'encodage en jeu** : n'employer que des caractères Windows-1252 (CP1252) dans les descriptions destinées au jeu (`<=`, `>=`, `->` plutôt que `≤`, `≥`, `→`), en particulier pour les descriptions d'items (`.uti`) et dialogues EN.
2. **Guides du joueur et traduction** :
   - Sources Markdown FR : `docs/README.md` et `docs/01_*.md` à `08_*.md`.
   - Sources Markdown EN : `docs/en/README.md` et `docs/en/01_*.md` à `08_*.md`.
   - Guide pour traducteurs tiers : `docs/HOW_TO_TRANSLATE.md`.
3. **Passage de relais vers la fabrication** :
   - Toute génération de PDF (`build_pdf.py`), assemblage d'installateur (`build_installer.py`, `installer/`) et création d'archive (`dist/`) est assurée par le nid **[Distribution](../Distribution/intent.md)** : lui écrire dans son `inbox.md` dès que des textes ou guides sont prêts à être publiés.
