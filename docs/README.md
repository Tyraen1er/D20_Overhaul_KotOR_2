# Guide du Joueur — *KotOR 2 Overhaul*

Bienvenue dans la documentation francophone du mod de rééquilibrage de **Star Wars: Knights of the Old Republic II — The Sith Lords**.

Ce guide a été conçu pour les **joueurs habituels de KotOR 2** : il ne contient aucun jargon technique ni détail de programmation. Il présente, **point par point**, tout ce que le mod change par rapport au jeu de base afin de vous aider à planifier vos personnages, choisir vos équipements et adapter vos tactiques de combat.

> **Note de l'auteur :** J'ai développé ce nouveau système seul, donc tous vos retours sont les bienvenus afin de continuer à l'améliorer. L'ensemble du projet est librement accessible sur mon GitHub ([github.com/Tyraen1er/Kotor-2--Remastered-Tyr](https://github.com/Tyraen1er/Kotor-2--Remastered-Tyr)) : j'autorise quiconque à utiliser mon travail (à but non lucratif), à en faire un fork ou à proposer des contributions (PR).

---

## Pourquoi ce mod ? (Philosophie générale)

Ce mod répond avant tout à **deux problèmes majeurs** du jeu d'origine :
1. **Des dégâts absurdes qui permettent d'éliminer les boss en un seul tour (one-shot)** : entre le cumul de bonus à l'établi et quelques combinaisons surpuissantes, certains builds pulvérisent les affrontements majeurs en 1 ou 2 tours, supprimant toute tension tactique.
2. **Un fort manque de diversité de builds** : les bures Jedi, le sabre laser et une poignée de pouvoirs (*Tempête de Force*, *Insanité*, *Vitesse de maître*) écrasent toutes les alternatives. Les armures, les armes à distance, les armes non-laser et plusieurs caractéristiques deviennent vite secondaires, d'autant que la moitié des ennemis organiques n'ont aucune défense particulière (la même stratégie fonctionne de Péragus à Malachor V).

**L'objectif du mod** est de retrouver des **combats tendus et tactiques** tout en rendant **chaque style de jeu viable, distinct et gratifiant** du niveau 1 au niveau 30 :
- Des **classes aux identités marquées** (combattant, hybride, utilisateur de Force).
- Des **armures utiles et spécialisées** (esquive en légère, technologie et boucliers en intermédiaire, tank pur en lourde).
- **8 familles d'armes** et **4 postures de combat** réellement différentes, au corps-à-corps comme à distance.
- **6 spécialisations de caractéristique** exclusives qui encouragent les builds originaux.
- Des **combats de boss tendus** (5 à 10 rounds) et des **familles d'ennemis** qui demandent de vraies adaptations tactiques.

---

## Petit lexique des abréviations utilisées

Si vous n'avez pas joué depuis longtemps, voici les abréviations que vous croiserez dans ce guide :
- **PV / PF** : Points de Vie / Points de Force.
- **CA** : Classe d'Armure (votre Défense : plus elle est haute, plus les ennemis vous ratent).
- **Atq / Dég** : Bonus d'Attaque (chance de toucher) / Bonus de Dégâts.
- **RD** : Réduction de Dégâts (ex. `RD 4/-` soustrait 4 points de dégâts à chaque coup reçu).
- **DD** : Degré de Difficulté d'un jet de sauvegarde (le score que la cible doit atteindre sur `1d20 + sa sauvegarde` pour résister à un effet).
- **Vig / Réf / Vol** : Les trois jets de sauvegarde — *Vigueur*, *Réflexes* et *Volonté*.
- **Notation en dés (`1d8`, `2d6`, etc.)** : Le mod remplace les plages du jeu de base (`1-8`, `2-12`) par la notation standard en dés : `2d6` signifie « lancer 2 dés à 6 faces » (soit de 2 à 12, avec une moyenne de 7).
- **FOR / DEX / CON / INT / SAG / CHA** : Force, Dextérité, Constitution, Intelligence, Sagesse, Charisme.
- **1M / 2M / D** : Arme à une main / Arme à deux mains / Arme double ou à répétition.
- **R1 / R2 / R3** : Rang 1, 2 ou 3 d'un don ou d'un pouvoir de la Force.
- **AoE** : Pouvoir ou attaque à effet de zone (touche plusieurs ennemis à la fois).

---

## Résumé express des plus gros changements

| Domaine | Dans le jeu de base | Avec le mod |
| :--- | :--- | :--- |
| **Classes (Niv. 30)** | Les combattants ont presque autant de pouvoirs que les Consulaires | Symétrie claire : **22 dons / 12 pouvoirs** (Gardien), **18 / 16** (Sentinelle), **15 / 24** (Consulaire) |
| **Styles de combat** | *Duel* et *Combat à 2 armes* dominent tout | Anciens dons remplacés par **4 postures** (*Duel*, *Ambidextrie*, *Arme Lourde*, *Haute cadence*) |
| **Spécialisations d'armes** | Simple +1 Attaque / +2 Dégâts | **8 familles** avec effets tactiques uniques (Renversement, Bris d'armure, Ébranlement, Étourdissement…) |
| **Armes à distance** | La DEX n'ajoute aucun dégât | La **DEX ajoute aux dégâts à distance** (comme la FOR en mêlée) |
| **Caractéristiques** | Peu de façons de valoriser CON, INT ou CHA en combat | **6 arbres exclusifs** (un par caractéristique) pour créer des archétypes uniques |
| **Armures** | Peu d'intérêt pour un Jedi | **RD native** (Interm. 2 / Lourde 4), **3 arbres de dons**, pièces combinées pour armures intermédiaires |
| **Pouvoirs de Force** | Coûts plats, *Tempête* et *Insanité* surpuissants | Coûts évolutifs par rang, pouvoirs rééquilibrés, **Éveil de Force**, **6 pouvoirs de prestige** refondus |
| **Établi & Améliorations** | Cumul massif de dégâts dès le milieu de partie | **1 seul emplacement de dégâts bruts** par arme, paliers de niveau à l'établi, toutes les armes de base fabricables |
| **Furtivité** | Peu rentable hors Attaque sournoise | La première attaque depuis la furtivité est un **critique confirmé** |
| **Ennemis & Boss** | Peu de résistances, boss tués en 2 rounds | **6 familles d'ennemis** aux défenses distinctes, combats de boss de **5 à 10 rounds** |

---

## Règles de base modifiées (actives dès le niveau 1, sans don)

Avant même de choisir le moindre don ou pouvoir, le mod modifie plusieurs règles fondamentales du moteur de combat et d'équipement par rapport au jeu d'origine :

- **Apparition des armes à deux mains (`2M`)** : les armes lourdes de mêlée (*Vibro-épée*, *Hache gamorréenne*, *Pique de Force*) et les fusils/arbalètes occupent les deux mains sans donner d'attaque supplémentaire, mais infligent de base **`200 % FOR`** en mêlée et **`150 % DEX`** à distance.
- **Armes à distance indexées sur la Dextérité (`DEX`)** : contrairement au jeu de base où la DEX n'ajoutait aucun dégât aux blasters, vos tirs ajoutent désormais votre modificateur de DEX aux dégâts (**`150 % DEX`** en arme 1M seule ou 2M, **`100 % / 50 % DEX`** à deux armes, **`150 % / 50 % DEX`** sur les blasters à répétition).
- **Armes doubles & blasters à répétition : malus de CA au lieu du malus d'attaque** : toutes les armes doubles et armes à répétition sont désormais équilibrées et perdent l'ancien malus d'attaque à deux armes (`-6 / -10`). À la place, elles appliquent un **malus natif de `-5 CA`** et infligent **`150 % / 50 %`** FOR (mêlée) ou DEX (distance).
- **Critique confirmé garanti en furtivité** : la **première attaque** portée dans les **6 secondes** suivant la sortie du mode furtif bénéficie d'un bonus de **`+50` en Attaque** (garantissant la touche) et **duplique la totalité de ses dégâts (Attaque sournoise comprise)** afin de simuler un coup critique confirmé. En jeu, ces dégâts doublés s'affichent sur une **seconde ligne de dégâts** dans le journal de combat, juste après l'impact initial.
- **Mains nues comptées comme une arme à une main** : combattre à mains nues profite nativement des règles d'une arme 1M seule (`150 % FOR` en mêlée et compatibilité avec la posture *Duel*).
- **Réduction de Dégâts (RD) native sur les armures** : porter une **armure intermédiaire** confère nativement **`RD 2/-`** et une **armure lourde** **`RD 4/-`** (physique & énergie). De plus, chaque type d'armure possède ses propres emplacements à l'établi (1 Sur-couche en légère, 2 pièces combinées exclusives en intermédiaire, 1 Sous-couche en lourde).
- **DD évolutifs pour les grenades, roquettes et effets sur coup** : fin des DD fixes inutiles en fin de partie — les grenades suivent **`10 + Niveau + Mod. INT`**, les fléchettes/roquettes **`12 + Niveau + Mod. INT`**, et les effets sur coup des armes **`3 / 5 / 7 / 9 + Niveau + Mod. Caractéristique de l'arme`**.
- **Établi cloisonné et verrouillé par niveau** : un seul emplacement par arme ajoute des dégâts réguliers, toutes les armes de base non-laser sont fabricables dès le niveau 1, et les améliorations se débloquent par paliers de niveau du personnage (`Mk I : Niv. 1`, `Mk II : Niv. 10`, `Mk III : Niv. 15/18`, `Mk IV / Mk V : Niv. 20`).
- **Coûts en PF évolutifs et fin des plafonds au rang R3** : chaque rang de pouvoir coûte davantage en Points de Force (`R1 < R2 < R3`), et les pouvoirs de rang R3 progressent sans limite de dés jusqu'au niveau 30.
- **Notation des dégâts en dés (`1d8`, `2d6`, etc.)** : toutes les descriptions en jeu remplacent les plages d'origine (`1-8`, `2-12`) par la notation standard en dés.

---
