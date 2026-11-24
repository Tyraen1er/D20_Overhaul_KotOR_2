# Cahier des charges — Utilitaire autonome de Conversion & Respec (`KotOR 2 D20-Overhaul`)

**Statut :** Acté le 24/11/2026  
**Format cible :** Application Windows autonome (`.exe`), totalement séparée du jeu (aucune injection DLL, aucun risque de conflit avec Steam ou TSLRCM).

---

## 1. Objectif général

Fournir aux joueurs un outil graphique simple et sûr permettant :
1. De **convertir une sauvegarde** entre le jeu **Vanilla (TSLRCM)** et le mod **D20-Overhaul** (dans les deux sens).
2. De **réinitialiser et reconstruire un personnage (Respec)** niveau par niveau — caractéristiques, classe, compétences, dons, pouvoirs et multiclassage — sans avoir à manipuler KSE manuellement.

---

## 2. Parcours utilisateur

### Étape 1 — Sélection de la sauvegarde
- Détection automatique du répertoire `saves/` de l'installation KotOR 2 (avec possibilité de parcourir manuellement un autre dossier).
- Liste des sauvegardes triées par date (nom de la sauvegarde, zone, niveau, date), avec **détection automatique du profil** de la sauvegarde : **`D20-Overhaul`** ou **`Vanilla`**.
- Sélection du personnage à éditer (**Exilé** par défaut, ou l'un des compagnons présents dans la sauvegarde).
- **Sécurité obligatoire :** création automatique d'un **backup complet horodaté** de la sauvegarde avant toute écriture.

### Étape 2 — Choix de l'action
Trois boutons principaux :
1. **Conversion → D20-Overhaul** :
   - Adapte une sauvegarde vanilla au mod : retire les dons supprimés par le mod (`DUELING`, `TWO_WEAPON_FIGHTING`, `WEAPON_FOCUS/SPEC`, `FINESSE_*`…), recalibre les quotas (dons/pouvoirs) et ouvre directement l'assistant de respec en mode **D20-Overhaul** pour réallouer proprement les points libérés.
2. **Conversion → Vanilla** :
   - Adapte une sauvegarde D20-Overhaul pour revenir au jeu vanilla : retire les dons custom (`ID 245+`), nettoie les variables locales spécifiques au mod et ouvre l'assistant de respec en mode **Vanilla** pour reconstruire un personnage 100 % compatible vanilla.
3. **Respec** :
   - Détecte automatiquement si la sauvegarde courante est en **D20-Overhaul** ou en **Vanilla** (avec possibilité de confirmer le mode détecté), puis applique les tables et règles correspondantes (`feat.2da`, `featgain.2da`, `classpowergain.2da`, `spells.2da`).

---

## 3. Fonctionnement de l'assistant de Respec

L'utilitaire reproduit un parcours complet de création + montée de niveau, du **Niveau 1** jusqu'au **niveau actuel** du personnage (XP total, inventaire, alignement, apparence et état des quêtes intégralement conservés) :

### A. Base du personnage (Niveau 1)
- **Répartition des caractéristiques de départ** (budget standard de création, modificateurs et coûts d20 respectés).
- **Choix de la classe de base** (Gardien, Sentinelle, Consulaire, ou classe de compagnon).

### B. Montée de niveau pas-à-pas (`Niv. 1 → Niv. N`)
Pour chaque niveau :
- **Point de caractéristique** (tous les 4 niveaux).
- **Points de compétences** (selon classe + modificateur d'Intelligence, plafonds `Niv + 3` classe / `(Niv + 3)/2` hors classe).
- **Choix de dons** (respectant les prérequis de niveau, de classe et d'arbre du mode actif : Overhaul ou Vanilla).
- **Choix de pouvoirs de la Force** (respectant les prérequis et quotas `classpowergain.2da` du mode actif).

### C. Bouton « Multiclassage »
- Un bouton **`Multiclassage`** est accessible à tout moment durant la montée de niveau dans l'utilitaire.
- Il permet au joueur de basculer vers une **classe de prestige** (Maître d'Armes, Maraudeur Sith, Jedi protecteur, Assassin Sith, Maître Jedi, Seigneur Sith) ou toute autre classe disponible à partir du niveau de son choix.
- **Liberté assumée :** ce bouton ne verrouille pas les restrictions scénaristiques ou d'alignement vanilla (il autorise donc volontairement des combinaisons/multiclassages inaccessibles en vanilla si le joueur le souhaite).

### D. Pré-sélection par défaut des choix précédents
- **Principe clé :** par défaut, toutes les options (caractéristiques de départ, classe, compétences, dons, pouvoirs, niveau de multiclassage) sont **pré-sélectionnées avec les choix que le joueur avait déjà faits** sur sa sauvegarde.
  - *Exemple :* si le joueur avait pris *Robustesse* au niveau 5, *Robustesse* apparaît déjà pré-sélectionnée à l'étape du niveau 5 dans l'utilitaire ; valider toutes les étapes sans rien changer restitue un personnage identique à l'original.
- **Note technique sur l'ordre historique :** le format `.utc` de KotOR 2 stocke la liste globale des dons/pouvoirs acquis mais pas le niveau exact auquel chacun a été choisi. L'outil reconstruira donc automatiquement une affectation niveau par niveau **déterministe et valide** (respectant l'ordre des prérequis et niveaux minimums de chaque don/pouvoir existant), de sorte que tous les dons/pouvoirs déjà possédés soient pré-cochés à des niveaux légaux et prêts à être conservés ou remplacés en un clic.

---

## 4. Architecture technique envisagée

- **Langage & librairies :** Python 3 + `pykotor` (lecture/écriture native des sauvegardes `SAVEGAME.sav`, `PARTYTABLE.res`, `GLOBALVARS.res`, `.utc`, `.2da`, `dialog.tlk`) + interface graphique légère (`CustomTkinter` ou `PySide6`).
- **Détection Overhaul vs Vanilla :** basée sur la présence de dons `ID >= 245` dans le `.utc` du personnage et/ou la présence des fichiers Overhaul dans `Override/` (avec sélecteur manuel de secours).
- **Distribution :** compilé en exécutable autonome Windows (`.exe`) via `PyInstaller` (`--onefile --windowed`), livré à part du dossier `Override/`.
