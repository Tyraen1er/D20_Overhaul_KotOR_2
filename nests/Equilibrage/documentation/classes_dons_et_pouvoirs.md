# Classes, Dons, Postures & Pouvoirs de la Force

> Source opérationnelle : `csv/fr/Kotor 2 - rééquilibrage - WIP Feats.csv` et `Spé Pouvoirs.csv`. En cas de divergence, les CSV font foi.

## 1. Progression des classes (`featgain.2da` & `classpowergain.2da`)

Symétrie inverse Combattants ↔ Mages (calibrée sur les budgets Niv. 30, avec `BAB 1.0` `CLS_ATK_1` pour toutes les classes) :

| Famille de classes | Pouvoirs (Niv. 30) | Dons (Niv. 30) | Ports d'armure Niv. 1 |
| :--- | :---: | :---: | :--- |
| **Gardien / Maître d'Armes / Maraudeur Sith** | **12** (`1/3` + 2 Niv. 1) | **22** (`~2/3` + bonus) | Légère, Intermédiaire, Lourde |
| **Sentinelle / Jedi protecteur / Assassin Sith** | **16** (`1/2`) | **18** (`~3/5`) | Légère, Intermédiaire |
| **Consulaire / Maître Jedi / Seigneur Sith** | **24** (`4/5`) | **15** (`1/2`) | Légère |

## 2. Paliers de niveau, gating & compagnons

- **Paliers `mincharlevel`** : dons martiaux de base (Actifs vanilla, Robustesse, **4 Postures**) = **`1 / 4 / 8`** ; grands arbres (**Spé Carac**, **Spé d'arme**, **Armures**, **Éveil de Force** Amplifié/Pénétrant) = **`1 / 8 / 15`** (*Pouvoir Prolongé* = `1+`).
- **Gating Classe / Prestige** :
  - *Éveil de Force* : R1 tous Jedi/Sith · R2 Consulaire/Maître Jedi/Seigneur Sith · R3 Maître Jedi/Seigneur Sith.
  - *Spé d'arme (8 familles)* : R1 tous · R2 Gardien/Sentinelle + prestiges · R3 Maître d'Armes/Maraudeur.
  - *Postures* : R1–R2 tous · R3 *Duel* tous, *Ambidextrie / Arme Lourde / Haute cadence* tous sauf Mages.
  - *Armures* : R1 tous (si port) · *Juggernaut* R2 Gardien/prestiges martiaux, R3 Maître d'Armes/Maraudeur · *Armure Tactique* R2 Sentinelle/prestiges hybrides, R3 Jedi protecteur/Assassin · *Esquive Balistique* R2 Gardien/Sentinelle + prestiges, R3 leurs prestiges.
  - *Spé Carac (6 arbres)* : **ouvertes à toutes les classes** (paliers `1/8/15`).
- **Compagnons** : classes non-Jedi (`SOL`, `SCT`, `SCD`, `TEC`, `DRC`, `DRX`) accèdent aux R3 pertinents au Niv. 15+ (`minattackbonus = 15`). Exceptions level-up Niv. 15+ : **Kreia** = Maître Jedi (tout *Éveil de Force*) ; **Visas** = Assassin Sith (*Armure Tactique III*, *Esquive Balistique III*, *Esquive Totale*). Récompense **Servante** (*Prémonition du combat*) remplacée par `+10 %` d'esquive en mêlée.

## 3. Postures & 8 familles de spécialisation d'armes

Dons vanilla **masqués/supprimés** : `DUELING` I–III, `TWO_WEAPON_FIGHTING` I–III, `FINESSE_MELEE_WEAPONS`, `FINESSE_LIGHTSABERS`, `WEAPON_FOCUS/SPEC` (pistolets, fusils, mêlée, sabres).

| Posture | Base moddée (sans don) | Rangs I → III |
| :--- | :--- | :--- |
| **Duel (`1M` ou mains nues)** | Mêlée `150 % FOR` ; distance `150 % DEX` | `+2/+4/+6 Atq` & plage de critique `+1/+2/+3` |
| **Ambidextrie (`2 armes`)** | Mêlée `100 %/50 % FOR` ; distance `100 %/50 % DEX` (`-6/-10`, `+2/0` si équilibrée) | `-6/-6 & +2 CA` → `-4/-4 & +4 CA` → `-2/-2 & +6 CA` |
| **Arme Lourde (`2M`)** | Mêlée `200 % FOR` ; distance `150 % DEX` | `+1/+2/+3 Atq` ; mêlée `215/235/250 % FOR` ; distance `165/185/200 % DEX` |
| **Arme haute cadence (`HC`)** | Mêlée `150 %/50 % FOR` ; distance `150 %/50 % DEX` ; **toutes `balanced`**, malus **`-5 CA`** | `+1/+1 & -3 CA` → `+2/+2 & -2 CA` → `+3/+3 & -1 CA` |

**8 familles** (Rang I = `+2 Atq & +2 Dégâts` partout) :

- **Impact** *(mains nues, matraque, torche, bâton, pique)* : R2 Renversement 1t (Vig, DD 10, proc `plage/20`) · R3 2t.
- **Traditionnelle** *(épées courte/longue/double, hache gamorréenne, lame wookiee)* : R2 Bris d'armure `-3 CA` 2t (Vig, DD 5, par coup) · R3 cumulable, `+1t`.
- **Résonance** *(vibrolame, vibro-épée, vibrolame double)* : R2 Ébranlement `-4 Atq & Dég` 1t (Réf, DD 5, par coup) · R3 empilable `-2/proc` (cap `-8`, durée rafraîchie).
- **Laser** *(sabre court, sabre, double sabre)* : R2 Bris de volonté `-4` saves 2t (Vol, DD 5, par coup) · R3 sans jet de sauvegarde.
- **Tir d'Assaut** *(pistolet blaster, carabine, blaster à répétition)* : R2 aucun malus en mêlée · R3 `+1 Atq/rd` main directrice.
- **Tir Pénétrant** *(blaster lourd, fusil blaster, arbalète wookiee, blaster lourd à répétition)* : R2 Repousse 3 m (Vig, DD 5, 1×/rd) · R3 `+5 Dégâts`.
- **Tir Tactique** *(ions et soniques)* : R2 Stun 1t + stun droïde (Vig, DD 10, proc `plage/20`) · R3 2t.
- **Tir Assassin** *(blaster de poche, disrupteurs)* : R2 Attaques sournoises `+2d6` (active la capacité) · R3 Multiplicateur de critique `+1`.

*Mains nues* : appartient à la famille **Impact** + posture **Duel** + chaîne *Spécialiste mains nues* plafonnée au Rang III (`+1d4 / +2d4 / +3d4` aux Niv. `4 / 12 / 19` base ou Niv. `4` prestige ; Rangs IV–VIII supprimés).

## 4. Les 6 spécialisations de caractéristique (mutuellement exclusives)

Ordre canonique : `FOR, DEX, CON, INT, SAG, CHA`. Le **premier Rang I acquis** fixe l'arbre actif (les 5 autres restent sélectionnables par limite moteur mais sans effet).

| Arbre | Rang I | Rang II | Rang III |
| :--- | :--- | :--- | :--- |
| **Raffinement Gamorréen** (`FOR`) | `+1 FOR` ; `+½ mod. FOR` toutes compétences | `+2 FOR` ; **Adaptateur Gamorréen** (établi portatif + bascule `2M/HC ↔ 1M`, mêlée & distance) ; arme `HC 1M` en main droite = `+1 atq/rd` (`0` CA, rien en main gauche) ; **n'interdit plus** les postures `2M`/`HC` | `+3 FOR` ; immunité au mental |
| **Techniques Echanis** (`DEX`) | `+1 DEX` ; Atq mêlée `FOR/DEX` | `+2 DEX` ; Dég mêlée `FOR/DEX` | `+3 DEX` ; supprime le plafond DEX des armures |
| **Voie du dragon Krayt** (`CON`) | `+1 CON` ; `RD +½ mod. CON` (sup.) | `+2 CON` ; transfusion : toutes les `6 s`, `5 % PV max → 5 % PF max` si `PF < 50 %` (jamais sous `75 % PV`, rituel complet `25 % ↔ 25 %`) | `+3 CON` ; toutes saves `+mod. CON` |
| **Chasseur de prime Gand** (`INT`) | `+1 INT` ; grenades & mines `+5 %` dég / rang total Démolition | `+2 INT` ; Atq & Dég distance `DEX/INT` | `+3 INT` ; rayon grenades `4 → 6 m`, perce *Esquive Totale*, `50 %` non-consommation |
| **Maîtrise Matukai** (`SAG`) | `+1 SAG` ; **ajoute** `mod. SAG` à l'attaque | `+2 SAG` ; saves `+½ SAG` ; réussir une save inflige `SAG` dégâts à l'attaquant | `+3 SAG` ; `SAG` remplace `DEX` pour la CA ; ennemi qui rate subit `SAG` dégâts (contournent RD, pas de crit) |
| **Héritage de Nomi** (`CHA`) | `+1 CHA` ; compagnons `100 % XP` | `+2 CHA` ; groupe : saves `+mod. CHA` | `+3 CHA` ; `CA +mod. CHA` |

## 5. Dons transversaux & Pouvoirs de la Force

- **Éveil de Force (7 dons)** : *Pouvoir Amplifié I–III* (`+15/+30/+50 %` dégâts offensifs, coût `+2/+4/+6 PF`) · *Pouvoir Pénétrant I–III* (`+2/+4/+6 DD` offensifs/contrôle) · *Pouvoir Prolongé* (durée buffs `×2`).
- **Esquive Totale** (`FEAT_EVASION`) : réussite save AoE → `0` dégât ; échec → `÷ 2` (Jedi protecteur / Assassin / Visas Niv. 15+, Mira Niv. 6, Jedi/Sith ennemis Niv. 20+).
- **Pouvoirs standards (`Spé Pouvoirs.csv`)** : aucun pouvoir classique ajouté ; **aucun cap de dés en L3** ; **coûts PF évolutifs** `L1 10–20 / L2 20–35 / L3 35–65 PF` (calibrés sur réserves Niv. 25 `200/300/500 PF`). Nerf du haut du panier (*Tempête* `1d6/Niv` Réf sans drain PF, *Mise à mort* `1d8/Niv` sans `50 %` PV max, *Insanité* DoT mental `Niv/rd` + `-4/-6/-8 Atq` sans perte d'action, *Champ de stase* `36 s` DD Vig `-3/rd`, *Vague* = Tourbillon AoE `6 m / 12 s` Réf ½, *Festin de mort* L3 excédent de soin → PV temporaires `24 s`, *Barrière* & *Résist. Énergie* alignés en Armure intermédiaire `RD 4/8/12` personnel `60 s` `15/25/35 PF`).
- **6 Pouvoirs de Prestige (uniformisés `L1/L2/L3` aux niv. 1/5/9) & Ultimes d'alignement** :
  - *Stigmate de Force* (Maraudeur, Lourde, `30 s`) : `+2/+4/+6` FOR/DEX, imm. Stase/Paralysie, `+1 atq/rd` dès L1 (non cum. Vitesse), `-5 % PV max/rd` (arrêt ≤ `25 %`).
  - *Cicatrice de Force* (Maître d'Armes, Lourde, `30 s`) : soin `+2/+4/+6 % PV max/rd`, `+1/+2/+3` saves, imm. Peur/Stun (L2) et Paralysie (L3).
  - *Spectre de la Force* (Assassin, Interm., passif) : furtivité sans ceinture + Course furtive + `+4/+8/+12` Discrétion ; L2 embuscade `+2d6`/Stun 1t ; L3 kill → crit confirmé + `+25 %` esquive 2t.
  - *Affranchi de la Force* (Jedi protecteur, Lourde, passif) : `+1` / 8 rangs combinés sur 4 paires de compétences → Atq/Dég/CA/Saves (cap `+3/+5/+7`) ; L2 `+25 %` consommables ; L3 SR `15 + Niv`.
  - *Déchirure de la Force* (Seigneur Sith, Lourde, `45 s`, `15 m`) : `-2/-4/-6` Atq/Saves/CA (Vol annule).
  - *Écho des Liens* (Maître Jedi, Lourde) : partage buffs personnels avec allié proche (L1 `30 s`), groupe (L2 `45 s`), + soins partagés (L3 `60 s`, sans restriction d'armure).
  - *Grâce du côté Lumineux* (Interm., `50 PF`, instantané, *Vitesse* cap `+1 atq/rd` sous armure) · *Écrasement de Force* (Légère, `60 PF`, `1d8/Niv` purs sans cap + immo `6 s`, Vig ½ et annule).
