# Décisions Finales d'Équilibrage — Synthèse (*KotOR 2 Overhaul*)

Ce document est le **contrat de game design** : chaque décision actée y figure sous forme condensée.
Les justifications, la recherche (JdR papier, D&D, consensus communauté) et les notes d'implémentation sont dans **[`decisions_annexes.md`](decisions_annexes.md)**.

> **Hiérarchie des sources (README §0)** : les CSV `Kotor 2 - rééquilibrage - *.csv` sont la référence opérationnelle côté utilisateur — ce contrat en est la **consolidation**. En cas de divergence, les CSV font foi ; ce document doit alors être resynchronisé.
> **Dernière grosse consolidation : 19/11/2026** (cloisonnement strict des rôles par slot d'amélioration d'arme, *Tir d'Assaut* verrouillé à 2 slots, scaling des DD fixes grenades/fléchettes/armes ; scaling DEX `100 % / 50 %` et armures le 18/11 ; arbres d'armures le 17/11 ; refonte postures/spé d'arme/spé carac le 15/11/2026). Journal des arbitrages : annexes §9.

| Domaine | Décision (résumé) | Détail |
| :--- | :--- | :---: |
| Progression des classes | Symétrie inverse Combattants ↔ Mages (dons ↔ pouvoirs) | §1 |
| Pouvoirs de la Force | Aucun ajout ; nerf du haut du panier, buff des alternatives, restauration via Métamagie | §2 |
| Établi & Boss | Plafonds `+2/+5/+10`, cloisonnement strict des rôles par slot (1 seul slot de dégâts bruts par catégorie), RD boss **`2/5/8`**, combats 5–10 rounds | §3 |
| Postures & spécialisations d'armes | 4 postures (Duel, Ambidextrie, Arme Lourde, Arme haute cadence) × 8 familles (4 mêlée + 4 tir) ; dons vanilla Duel/TWF/Finesse/Focus/Spec **supprimés** | §4 |
| Spécialisations de caractéristique | 6 arbres exclusifs (FOR, DEX, CON, INT, SAG, CHA) — un par caractéristique, ordre canonique | §5 |
| Architecture de dons | Posture (3) + famille (3) + spé carac (3) + défenses ; budgets Niv. 30 : **22 / 18 / 15** dons (pouvoirs **12 / 16 / 24**), gating par classe/prestige sur Rangs II–III | §6 |
| Dons transversaux | 7 dons de Métamagie + *Esquive Totale* (anti-AoE) | §7 |
| Armures & Défenses | RD native (Interm. 2 / Lourde 4), upgrades combinées exclusives aux intermédiaires (`UpgradeLevel`), 3 arbres de dons par type, dégradé de pouvoirs, *Condition physique III* supprimé | §8 |
| Contrat mathématique | DPR nets et durées de boss cibles par phase de jeu (colonnes à remapper sur la nouvelle architecture) | §9 |
| Furtivité | Embuscade : première attaque depuis la furtivité = critique confirmé (simulation scriptée) | §10 |
| Conventions & principes | DD Spé d'arme (`10`/`5` + Niv + carac), grenades (`10` + Niv + INT), fléchettes/roquettes (`12` + Niv + INT), *On-Hit* armes (`3/5/7/9` + Niv + carac à définir), procs `plage/20`, ordre canonique, « les synergies se trouvent » | §11 |

---

## Partie 1 : Décisions Actées

### 1. Progression des Classes (`spellgain.2da` & `featgain.2da`)

Symétrie inverse calibrée sur le volume réel de pouvoirs utiles (révisée le 19/11 : Consulaire ramené de 31 à 24 pouvoirs pour éliminer les fillers de fin de jeu, et identités protégées par les prérequis de classe/prestige) :

| Famille de Classes | Gain de Pouvoirs | Total Pouvoirs (Niv. 30) | Gain de Dons | Total Dons (Niv. 30) | Identité |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Gardien / Maître d'Armes / Maraudeur Sith** | `1/3` niveaux (+2 Niv. 1) | **12** | `~2/3` niveaux + bonus | **22** | Maître Martial |
| **Sentinelle / Jedi protecteur / Assassin Sith** | `1/2` niveaux | **16** | `~3/5` niveaux | **18** | Hybride Tactique |
| **Consulaire / Maître Jedi / Seigneur Sith** | `4/5` niveaux | **24** | `1/2` niveaux | **15** | Archimage |

### 2. Philosophie des Pouvoirs de la Force

1. **Aucun nouveau pouvoir de sélection classique** : rééquilibrage à 100 % dans `k_inc_force.nss` et `spells.csv` *(seuls les 6 pouvoirs de prestige sont refondus/complétés pour doter chaque classe de prestige d'une identité propre)*.
2. **Hiérarchie :** *Éclair/Tempête* (zone) et *Blessure/Étranglement/Mise à mort* (monocible) restent les meilleurs DPS de Force — **nerfés à la base**, restaurables via **Métamagie**. Les alternatives sont boostées sans jamais dépasser ce plafond.
3. **Alignement :** *Champ de Stase* reste un pouvoir du Côté Lumineux.
4. **Pouvoirs de Prestige (uniformisés `L1 / L2 / L3` aux niv. 1/5/9 de prestige) & Ultimes d'alignement** *(source : `Spé Pouvoirs.csv`)* :

| Classe de Prestige | Pouvoir (L1 → L3) | Armure max | Effet synthétique |
| :--- | :--- | :---: | :--- |
| **Maraudeur Sith** | **Stigmate de Force** *(ex Fureur)* | Lourde | `30 s` : `+2/+4/+6` FOR & DEX, immunité Stase/Paralysie, `+1 atq/rd` dès L1 *(non cumulable Vitesse)* ; `-5 %` PV max/rd *(arrêt ≤ 25 % PV)* |
| **Maître d'Armes Jedi** | **Cicatrice de Force** *(nouveau)* | Lourde | `30 s` : soin `+2/+4/+6 %` PV max/rd, `+1/+2/+3` sauvegardes, immunité Peur/Étourdissement (L2) et Paralysie (L3) |
| **Assassin Sith** | **Spectre de la Force** *(ex Camouflage)* | Moyenne | Passif : furtivité sans ceinture + Course furtive + `+4/+8/+12` Discrétion ; L2 embuscade `+2d6`/Stun 1t ; L3 kill → crit confirmé + `+25 %` esquive (2t) |
| **Jedi protecteur** | **Affranchi de la Force** *(nouveau)* | Lourde | Passif : `+1` par 8 rangs combinés sur 4 paires de compétences → Atq, Dég, CA, Saves *(cap `+3/+5/+7`)* ; L2 `+25 %` objets profanes ; L3 Résist. Force `15 + Niv` |
| **Seigneur Sith** | **Déchirure de la Force** *(ex Annihilation)* | Lourde | `45 s`, zone `15 m` : `-2/-4/-6` Atq, Sauvegardes et CA *(Volonté annule)* |
| **Maître Jedi** | **Écho des Liens** *(ex Inspiration)* | Lourde | Partage les buffs personnels avec l'allié le plus proche (L1, `30 s`), tout le groupe (L2, `45 s`), + soins partagés (L3, `60 s`, sans restriction d'armure) |

*Ultimes d'alignement :* **Grâce du côté Lumineux** (*Armure moyenne*, `50 PF`, instantané, *Vitesse* plafonnée à `+1 atq/rd` sous armure) · **Écrasement de Force** (*Armure légère*, `60 PF`, `1d8/Niv` dégâts purs sans cap + immo `6 s`, Vig ½ et annule).

### 3. Établi & Boss (Rythme des Combats)

**A. Plafond des améliorations d'armes** (pièces `u_r_*`, `u_m_*`, `u_l_*` retravaillées — inventaire de référence : CSV *Améliorations*, 226 pièces) :
- Early (Niv. 1–10, Mk I) : max **`+2` dégâts moyens/coup** • Mid (Niv. 11–18, Mk II) : max **`+5`** • Late (Niv. 19+, Mk III) : max **`+10`** *(valeurs max pour une arme disposant de tous ses emplacements d'amélioration).*
- **Slots autorisés par famille d'arme** (*Armes.csv*, via hiérarchie `UpgradeLevel`) :
  - **Mêlée (`Poignée < Lame < Cellule`)** : *Mains nues* (0 slot) · *Impact* (1 : Poignée) · *Traditionnelle* (2 : Poignée, Lame) · *Résonance* (3 : Poignée, Lame, Cellule) · *Laser* (Cristal de couleur + 2 Cristaux d'amélioration + Émetteur + Lentille + Cellule). *Bâton Gaffi* retiré du jeu (héritage KotOR 1).
  - **Distance (`Lunette < Pack d'énergie < Chambrage`)** : *Tir Tactique* (1 : Lunette) · ***Tir d'Assaut* & *Tir Assassin*** (2 : Lunette, Pack) · *Tir Pénétrant* (3 : Lunette, Pack, Chambrage). *(Tir d'Assaut verrouillé à 2 slots le 19/11 : combiné au `+1 Atq/round` de Spé III, le Chambrage écraserait Tir Pénétrant.)*
- **Cloisonnement strict des rôles par emplacement** (acté le 19/11 — interdit le cumul de dégâts bruts sur plusieurs slots et amplifie l'identité de chaque famille d'armes) :
  - **Mêlée** : **Poignée** = `+Attaque` / `+CA` uniquement (0 dégât) · **Lame** = `Acéré`, `Critiques massifs`, *On-Hit* scalés, `vs Droïdes` (0 dégât brut régulier) · **Cellule** *(Résonance seule)* = **seul slot à dégâts réguliers** (physiques/élémentaires).
  - **Distance** : **Lunette** = `+Attaque`, `Acéré`, ***On-Hit* scalés** (réintroduits sur les lunettes, 0 dégât) · **Pack d'énergie** = `Critiques massifs`, `Ion / vs Droïdes & Boucliers`, ou léger bonus constant (`+1..+3` max) · **Chambrage** *(Tir Pénétrant seul)* = **seul slot à gros dégâts bruts**.
  - **Sabre Laser** : **Émetteur** = `+CA`, `Parade de blasters`, ***On-Hit* scalés** (réintroduits sur les émetteurs, 0 dégât) · **Lentille** = `+Attaque`, `Acéré`, `Critiques massifs` (0 dégât régulier) · **Cellule** = **seul slot à dégâts réguliers du sabre** · **Cristaux (×2 + Cristal personnel)** = `+Caractéristiques` (plafonnées), `Régénération PV/PF`, `+Attaque`, `Parade`, `vs Alignement/Droïdes` (0 dégât brut générique).
- **Principe de compensation** : l'absence de `Cellule` / `Chambrage` sur les familles à 1 ou 2 slots plafonne leurs upgrades plus bas à l'établi, en échange de **dégâts de base plus élevés, d'une plage de critique élargie ou d'un multiplicateur de critique supérieur**.

**B. Boss** :
- **Règle d'or :** aucun boss tué en moins de 4 rounds ; cible **5–10 rounds** (10–15 pour Sion/Traya).
- **RD passive** des Sous-Boss/Boss (`Set_4`/`Set_5`) : **`RD 2`** (Early) / **`RD 5`** (Mid) / **`RD 8`** (Late) *(recalibrée le 19/11 pour débloquer les builds multi-coups et les armures sans toucher aux PV des boss)*.
- **`damagemult` des boss réduit** (`autobalance.2da`) pour que le joueur tienne aussi 5–10 rounds.

### 4. Postures & Spécialisations d'armes (refonte 13–15/11)

**Dons vanilla supprimés** (remplacés par les dons custom ci-dessous, cf. *Feats.csv*) :
`DUELING` I-III, `TWO_WEAPON_FIGHTING` I-III, `FINESSE_MELEE_WEAPONS`, `FINESSE_LIGHTSABERS`, `WEAPON_FOCUS/SPEC` (pistolets, fusils, mêlée, sabres).

**A. Les 4 postures** (*Style de combat.csv* — chacune 3 rangs, recréés **from scratch**) :

| Posture | Base moddée | Rang I → III | Notes |
| :--- | :--- | :--- | :--- |
| **Duel** | Dégâts mêlée `150 % FOR` (règle moteur 1M, main gauche vide) ; **distance 1M `150 % DEX`** | `+2/+4/+6 Atq` et **plage de critique +1/+2/+3** | Prérequis : arme à une main **ou mains nues** ; la plage élargie augmente la fréquence des procs des Spé d'arme (proc = plage/20 par coup) |
| **Ambidextrie** | Dégâts `100 % / 50 % FOR` (mêlée) ou **`100 % / 50 % DEX` (distance)** ; malus 2 armes `-6/-10` (`+2/0` si arme équilibrée en main gauche) | `-6/-6 & +1 CA` → `-4/-4 & +2 CA` → `-2/-2 & +3 CA` | Identité parade/CA ; malus de main gauche remonte mais l'attaque s'achète de la Défense |
| **Arme Lourde (2M)** | Mêlée `200 % FOR` / distance `150 % DEX` | `+1/+2/+3 Atq` ; mêlée **`215→235→250 % FOR`** ; distance **`165→185→200 % DEX`** | Prérequis : arme à deux mains non double — mêlée **et** distance |
| **Arme haute cadence** (ex « Arme Double & Repeating ») | Dégâts `150 % / 50 % FOR` (arme double mêlée) ou **`150 % / 50 % DEX` (répétition distance)**, malus moddé **`-5 CA`** (au lieu de `-6/-10 Atq`) ; **toutes les armes `D` sont équilibrées (`balanced`)** | `+1/+1` & CA `-3` → `+2/+2` & `-2` → `+3/+3` & `-1` | Repeating et lourds à répétition partagent cette posture ; moteur : les repeating **ne sont pas** des armes doubles (`weaponwield 6 ≠ 3`) |

**B. Les 8 familles de spécialisation** (*Spécialisation d'arme.csv* — rang I : `+2 Atq & +2 Dégâts` partout) :

| Famille (armes) | Rang II (effet sur coup) | Rang III |
| :--- | :--- | :--- |
| **Impact** (matraque, bâton, pique de Force) | **Renversement** 1 tour (Vigueur, DD 10, proc plage/20) | Renversement **2 tours** |
| **Traditionnelle** (épées courte/longue/double, hache gamorréenne, lame wookie) | **Bris d'armure** : -3 CA, 2 tours (Vigueur, DD 5, proc par coup) | Bris d'armure cumulable, **+1 tour** |
| **Résonance** (vibrolame, vibro-épée, vibrolame double) | **Mutilation** : -4 Atq & Dégâts, 1 tour (Réflexes, DD 5, proc par coup) | Empilable : -2/proc, **plafond -8**, durée rafraîchie |
| **Laser** (sabre court, sabre, double sabre) | **Bris de volonté** : -4 sauvegardes, 2 tours (Volonté, DD 5, proc par coup) | Bris de volonté **sans jet de sauvegarde** |
| **Tir d'Assaut** (pistolet blaster, carabine, blaster à répétition) | **Aucun malus en mêlée** | **+1 Atq/round** main directrice |
| **Tir Pénétrant** (blaster lourd, fusil blaster, arbalète wookie, blaster lourd à répétition) — *ex « Tir Lourd », renommé 15/11* | **Repousse 3 m** (Vigueur, DD 5 ; sauvegarde par coup qui touche, effet 1×/round même après plusieurs échecs) | **+5 Dégâts** |
| **Tir Tactique** (armes à ions et soniques) | **Stun** 1 tour + stun droïde (Vigueur, DD 10, proc plage/20) | Stun **2 tours** |
| **Tir Assassin** (blaster de poche, disrupteurs) | **Attaques sournoises +2d6**, donne la capacité d'en faire | **Multiplicateur de critique +1** |

*Exception assumée (15/11)* : le `mult. crit. +1` du Tir Assassin touche au critique malgré le principe « les Spé ne touchent pas au critique » — c'est LA spécialité sournoise, et elle n'empiète pas sur Duel (multiplicateur ≠ plage).

**C. Mains nues** (décision 14/11) : la branche dédiée (*Arts Martiaux / Arts Mutaki*) est **supprimée**. L'identité mains nues passe par la **posture Duel** (les poings comptent comme arme 1M) + la chaîne vanilla *Spécialiste mains nues* I-VIII + les Spé de caractéristique (Matukai). Les poings n'appartiennent à aucune famille de Spé d'arme.

**D. L'axe distance/mêlée** : parité de viabilité, asymétrie de coûts — chaque posture/famille distance atteint les cibles DPR du §9 par son propre chemin (`100 % / 50 % DEX` en `1M`/`D`, `150 % → 250 % DEX` via Arme Lourde `2M`, `INT` via Gand II, utilitaires via les familles de tir) ; la mêlée paie en défense et approche, la distance paie en contreurs (boucliers d'énergie, déflexion). Équilibrage fin par le chantier ennemis.

### 5. Spécialisations de Caractéristique (refonte 13–14/11)

**Un arbre par caractéristique, ordre canonique FOR, DEX, CON, INT, SAG, CHA. Les 6 arbres sont mutuellement exclusifs** (chaque rang I interdit les cinq autres — mécanisme : colonne `exclusion` de feat.2da à tester + garde-fou script, cf. annexes §5/§8). Source de vérité : *spé carac.csv*.

| Arbre (carac) | Rang I | Rang II | Rang III (signature) |
| :--- | :--- | :--- | :--- |
| **Raffinement Gamoréen** (FOR) | +1 FOR ; + ½ mod. FOR en rangs sur **toutes** les compétences | +2 FOR ; **tient toutes les armes à 1M** (mêlée et distance) ; postures autorisées : **Duel et Ambidextrie uniquement** | +3 FOR ; immunité au mental |
| **Techniques Echanis** (DEX) | +1 DEX ; attaque mêlée : FOR/DEX (si DEX > FOR) | +2 DEX ; dégâts mêlée : FOR/DEX | +3 DEX ; **supprime le plafond de DEX des armures** |
| **Voie du dragon Kraith** (CON) | +1 CON ; RD + mod. CON | +2 CON ; **transfusion** : toutes les 6 s, 5 % PV max → 5 % PF max si PF < 50 % (jamais sous 75 % PV) | +3 CON ; toutes sauvegardes + mod. CON |
| **Chasseur de prime Gand** (INT) | +1 INT ; **grenades `+5 %` dégâts / rang total de Démolition** | +2 INT ; attaque & dégâts distance : DEX/INT (si INT > DEX) | +3 INT ; **Maître Artificier** : rayon grenades `4→6 m`, perce *Esquive Totale*, `50 %` de non-consommation |
| **Maîtrise Matukai** (SAG) | +1 SAG ; **ajoute** le mod. de SAG à l'attaque (par-dessus la carac directrice) | +2 SAG ; sauvegardes + ½ SAG ; **réussir une sauvegarde inflige SAG dégâts à l'attaquant** | +3 SAG ; **SAG remplace DEX pour la CA** ; tout ennemi vous ratant subit SAG dégâts par attaque échouée |
| **Héritage de Nomi** (CHA) | +1 CHA ; compagnons 100 % de l'XP | +2 CHA ; groupe : sauvegardes + mod. CHA | +3 CHA ; **Défense + mod. CHA** |

Notes d'équilibrage : la transfusion Kraith échange invariablement **25 % PV ↔ 25 % PF** (rituel complet) ; les dégâts de punition Matukai contournent la RD (scriptés) et ne peuvent pas critiquer ; le cumul Nomi/Matukai + Précognition suppose des types de bonus distincts (plafond moteur à vérifier).

### 6. Architecture de Dons & Budgets

**Nouvelle structure (post-15/11)** : chaque personnage combine **une posture** (3 rangs) + **une famille de Spé d'arme par catégorie d'armes utilisées** (3 rangs chacune) + **un arbre de Spé carac** (3 rangs, exclusif) + **défenses** (Robustesse 3, Condition physique 2 ou arbre d'armure 3) + **Métamagie** (7, profil caster) + dons actifs vanilla conservés (Déluge, Attaque en puissance, Coup critique, Décharge, Tir rapide, Sniper).

**Budgets Niv. 30 (actés le 19/11)** : **22** (Gardien) / **18** (Sentinelle) / **15** (Consulaire), pour **12 / 16 / 24** pouvoirs.
- Les arbres restent compacts en **3 rangs marquants** (pas de découpage massif en « demi-dons ») ; seul *Blindage de Combat* est candidat à séparer son volet Furtivité en armure.
- **Gating par classe / classe de prestige** (acté le 19/11 — étend le modèle *Métamagie* aux grands arbres) :
  - **Métamagie** : R1 tous Jedi/Sith · R2 **Consulaire / Maître Jedi / Seigneur Sith** · R3 **Maître Jedi / Seigneur Sith**.
  - **Spécialisations d'arme (8 familles)** : R1 tous · R2 **Gardien / Sentinelle** + leurs prestiges · R3 **Maître d'Armes / Maraudeur Sith**.
  - **Postures** : R1 & R2 tous · R3 *Duel* = tous, *Ambidextrie / Arme Lourde / Haute cadence* = **tous sauf Mages**.
  - **Armures** : R1 tous (si port) · **Juggernaut** R2 Gardien/prestiges martiaux, R3 **Maître d'Armes / Maraudeur Sith** · **Armure Tactique** R2 Sentinelle/prestiges hybrides, R3 **Jedi protecteur / Assassin Sith** · **Esquive Ballistique** R2 Gardien/Sentinelle + prestiges, R3 **Maître d'Armes / Maraudeur / Jedi protecteur / Assassin**.
  - **Spécialisations de Caractéristique (6 arbres)** : **ouvertes à toutes les classes**, paliers par niveau (**Niv. 1+ / Niv. 8+ / Niv. 15+**).
  - **Compagnons (acté le 19/11 — gating par classe + 2 exceptions level-up)** :
    - Classes **non-Jedi** (`SOL`, `SCT`, `SCD`, `TEC`, `DRC`, `DRX`) : accès aux Rangs III martiaux/armures pertinents dès le **Niveau 15+** (`minattackbonus = 15` dans `feat.2da`, exact grâce à `CLS_ATK_1` `BAB 1.0`) — `SOL` (Spé d'arme III, Juggernaut III, Esquive Ballistique III), `SCT/SCD` (Spé d'arme III, Esquive Ballistique III, Armure Tactique III), `TEC` (Armure Tactique III, Spé d'arme III), `DRC` (Spé d'arme distance III), `DRX` (Spé d'arme distance II). Les compagnons convertis en Jedi suivent les règles normales de leur classe Jedi.
    - **Exception Kreia (Niv. 15+)** : considérée comme **Maître Jedi** pour les dons sélectionnables en level-up (accès à toute la **Métamagie**, dont Rangs III).
    - **Exception Visas (Niv. 15+)** : considérée comme **Assassin Sith** pour les dons sélectionnables en level-up (accès aux dons sélectionnables d'Assassin Sith : *Armure Tactique III*, *Esquive Ballistique III*, *Esquive Totale*).

### 7. Dons Transversaux : Métamagie & Esquive Totale

**A. Métamagie (7 dons, calibrés sur le budget du Consulaire)** :

| Don | Rangs | Effet |
| :--- | :---: | :--- |
| **Pouvoir Amplifié** | 3 | Dégâts des pouvoirs offensifs `+15/+30/+50 %` (coût `+2/+4/+6 PF`) |
| **Pouvoir Pénétrant** | 3 | `+2/+4/+6` au DD de sauvegarde des pouvoirs offensifs et de contrôle |
| **Pouvoir Prolongé** | 1 | Durée de tous les buffs de Force `×2` |

**B. Esquive Totale** (`FEAT_EVASION`, ligne 125) — contre-mesure anti-AoE :
- Réussite du jet de sauvegarde face à une AoE → **0 dégât** ; échec → **dégâts ÷ 2**.
- Sélectionnable uniquement à partir d'une classe de prestige (Niv. 15+) ; auto Éclaireur niv. 6 (Mira) ; octroyé à tous les Jedi/Sith ennemis 20+ (via `k_inc_force.nss`).

### 8. Armures : RD Native, 3 Arbres de Dons, Dégradé de Pouvoirs, *Condition physique III* supprimé

Décisions actées (08/11/2026) — justifications dans [`decisions_annexes.md`](decisions_annexes.md#1-armures--recherche-et-justifications) :

**A. Règles natives sans don (par catégorie d'armure)** — CA base et plafonds DEX vanilla *sauf Armure Lourde portée à CA base `10` (calibrage 18/11) et Techniques Echanis III (§5)*. **RD native lourde = `4/-`, intermédiaire = `2/-` ; refonte des 30 sur-couches et 30 sous-couches en 18 standards (`01..18`) + 12 combinées (`19..30`, exclusives intermédiaires via `UpgradeLevel`).**

| Type | CA base | Plafond DEX | **RD Physique & Énergie native** | **Accès Établi (cible refonte upgrades)** |
| :--- | :---: | :---: | :---: | :--- |
| Légère | 4–5 | +4/+5 | **0** | **1 seul slot** : Sur-couche (*overlay*) standard uniquement (`01..18`) |
| Intermédiaire | 6–7 | +2/+3 | **RD 2** | **2 slots exclusifs** : **Upgrades combinées** (1 sur-couche + 1 sous-couche combinant chacune 2 upgrades communes, `19..30`, via `UpgradeLevel` dédié, sans don requis) |
| Lourde | **10** | +0/+1 | **RD 4** | **1 seul slot** : Sous-couche (*underlay*) standard uniquement (`01..18`) |

*Note technique (17–18/11)* : `swkotor2.exe` limite en dur les armures à **1 slot sur-couche + 1 slot sous-couche** (impossible d'ajouter des slots séparés sans patch binaire). Attribuer le `UpgradeLevel` maximal uniquement aux `.uti` d'armures intermédiaires et aux pièces combinées réserve nativement ces dernières aux armures intermédiaires sur simple critère de type d'armure ; à l'inverse, le slot non autorisé des armures légères (sous-couche) et lourdes (sur-couche) est verrouillé pour n'offrir qu'**1 seul emplacement d'upgrade** sur chacune.

**B. Trois arbres de dons** (3 dons chacun, arbitrage du 17/11 — source : *spé Armure.csv*) :

| Arbre | Rang I | Rang II | Rang III | Identité |
| :--- | :--- | :--- | :--- | :--- |
| **Juggernaut** (lourde) | RD 3/-, immunité tous dégâts 10 % | RD 4/-, immunité 20 % | RD 5/-, immunité 30 % | Encaisser les dégâts |
| **Armure Tactique** *(ex Blindage de Combat)* (interm.) | RD 3/-, +1 CA, durée des boucliers +100 %, furtivité sans ceinture (armure moyenne portée) | RD 4/-, +2 CA, efficacité boucliers ×2, accès à Course furtive (armure moyenne portée) | RD 5/-, +3 CA, efficacité boucliers ×3 | Spé ingénieur et craft — boucliers & furtivité |
| **Esquive Ballistique** *(ex Seconde Peau)* (légère) | Esquive +10 %, +1 CA base | Esquive +20 %, +2 CA base | Esquive +30 %, +3 CA base | Esquiver toutes les attaques *(pas d'augmentation de la CA gagnée via caractéristiques)* |

**RD cumulée max** (Juggernaut III + native lourde 4 + Robustesse II 2) : **RD 11 + 30 % d'immunité** (≈ −53 % sur un coup de 23, ≈ −40 % sur un coup de 68). **Pas de cap global d'immunité** (acté le 19/11 ; révisable ultérieurement selon les retours joueurs).

**C. Dégradé des pouvoirs sous armure** (`forbiditemmask`) : robe = tous ; légère = vanilla + Vaillance I + Résistance ; interm. = vanilla + Résistance ; lourde = vanilla strict.

**D. *Condition physique III* (`MASTER_CONDITIONING`)** : **supprimé** (décision 17/11). Seuls les rangs I (+1) et II (+2) sont conservés en vanilla ; le rang III est supprimé.

### 9. Contrat Mathématique (DPR nets & durées de boss cibles)

Avec upgrades cloisonnées  `Améliorations.csv`), armes d20 (`Armes.csv`), parité distance (`150 % DEX` en Duel 1M et `150 %/50 %` en `D`) et RD des boss recalibrée (**`2/5/8`**) — vérifié sous `tools/dpr_check.py` le 19/11 :

| Phase (Boss étalon) | Duel (`1M`) | Ambidextrie (`2 armes`) | Arme Lourde (`2M`) | Haute Cadence (`D`) |
| :--- | :---: | :---: | :---: | :---: |
| **EARLY** — Niv. 8 (120 PV, CA 20, **RD 2**) | 11–23 DPR (5–11 rds) | 9–18 DPR (7–14 rds) | 14–26 DPR (5–8 rds) | 17–30 DPR (4–7 rds) |
| **MID** — Niv. 16 (280 PV, CA 29, **RD 5**) | 26–67 DPR (4–11 rds) | 23–65 DPR (4–12 rds) | 36–66 DPR (4–8 rds) | 36–81 DPR (3,5–8 rds) |
| **LATE** — Niv. 26 (650 PV, CA 44, **RD 8**) | 55–140 DPR (5–12 rds) | 49–150 DPR (4–13 rds) | 86–186 DPR (3,5–8 rds) | 61–170 DPR (4–11 rds) |

*(Survie Late vérifiée sur les 4 armures avec `Déluge de coups 3` + `Robustesse 3` : **Bure** `TTD/TTK = 1,51×` [8,0r / 5,3r], **Légère + Esq. Ballistique** `1,51×` [14,3r / 9,5r], **Moyenne + Armure Tactique** `1,17×` sur 1 bouclier 100×3 [`1,55×` sur 2 boucliers], **Lourde + Juggernaut** `1,54×` [17,2r / 11,2r] et indestructible vs escouades.)*

### 10. Furtivité : l'attaque en embuscade est un critique confirmé

**Décision actée (13/11/2026)** :

- La **première attaque** portée depuis la furtivité est un **critique confirmé** (multiplicateur de l'arme, sans jet de confirmation). L'attaque brise la furtivité.
- Les dés d'**Attaque sournoise** s'appliquent par-dessus (comportement vanilla) ; les effets sur critique maison (Spé d'arme) se déclenchent.
- **Implémentation** : simulation scriptée (le pipeline d'attaque est fermé) — drapeau « embuscade armée » posé par heartbeat tant que `IsStealthed()`, consommé par le hook 1006 de la victime, dégâts `GetTotalDamageDealt() × (multiplicateur − 1)`. Limites documentées en annexes §5.

### 11. Conventions & principes transverses

1. **DD des effets sur coup (Spé d'arme)** : `DD = 10 + Niveau attaquant + mod. de la caractéristique directrice de l'arme` — **base 10 si le proc dépend de la plage de menace, base 5 s'il en est indépendant** (règle générale posée le 15/11).
2. **DD des consommables & effets *On-Hit* d'armes** (acté le 19/11 — contre l'autobalance `savemult 0,80–1,05`) :
   - **Grenades** (toutes, dont Poison via sauvegarde scriptée dans `k_sup_grenade.nss`) : **`10 + Niveau + Mod INT`** (cible : ≥ 40 % sur la Vigueur d'un élite `Set_3` à INT 14).
   - **Fléchettes & Roquettes spécialisées** : **`12 + Niveau + Mod INT`**.
   - **Effets *On-Hit* des armes** (anciens DD fixes `10 / 14 / 18 / 22`, migrés en script hook `1006`) : table graduée **`3 / 5 / 7 / 9 + Niveau + Mod Carac`** *(caractéristique à définir, probablement au cas par cas lors du rééquilibrage des armes)*.
3. **Procs sur coup** : `chance = plage de menace de l'arme / 20 par coup` (évolue avec la posture Duel) ; ou sauvegarde par coup touché selon la famille.
4. **Ordre canonique des caractéristiques** : FOR, DEX, CON, INT, SAG, CHA — dans l'ordre des dons comme dans les descriptions.
5. **« Les synergies doivent être trouvées, pas décrites »** (14/11) : un don dont le texte doit citer les rangs d'un autre don est défectueux par construction ; les descriptions joueurs ne référencent jamais un autre don.
6. **CSV = couche utilisateur** (parcimonie obligatoire), `decisions_*.md` = couche agents (README §0).
7. **Notation des dégâts en dés d20** (acté le 21/11) : toutes les descriptions du mod (CSV colonnes mod + textes en jeu `dialog.tlk` pour armes, pouvoirs, dons et améliorations) utilisent systématiquement la notation en dés (`1d6`, `2d8`, etc.) à la place des plages vanilla (`1-6`, `2-16`).

---

## Partie 2 : TODOs & Chantiers Ouverts

1. **[TODO Tests moteur]** (tracés dans la colonne *Détail technique* du `Feats.csv`) : **T-exclusion** (colonne `exclusion` de `feat.2da`, mutualité des 6 arbres carac), **T1** (arme double en main gauche — Gamoréen II), **T2** (`reqfeat0` sur baseitem d'arme), **T3** (détection des ratés — événement 1005), **plafond CA** (cumul Nomi/Matukai). *(Note : ~~grenades scriptables~~ **VÉRIFIÉ** dans `k_sup_grenade.nss`.)*
2. **[TODO Budgets §6]** : ~~recomposer le socle de dons avec les nouveaux axes.~~ **ACTÉ (19/11) : budgets `22 / 18 / 15` dons (`12 / 16 / 24` pouvoirs) + gating Classe / Prestige / Compagnons.**
3. **[TODO Contrat §9]** : ~~remapper les colonnes DPR sur l'architecture postures × familles.~~ **ACTÉ (18–19/11) dans `dpr_check.py` / `dpr_data.json`.**
4. **[TODO Arbres d'armures §8.B]** : ~~revalider les 9 dons.~~ **ACTÉ (17–19/11) : *Juggernaut*, *Armure Tactique*, *Esquive Ballistique* intégrés dans `Feats.csv`.**
5. **[TODO Servante]** : ~~remplacer son don d'histoire *Prémonition du combat*.~~ **ACTÉ (19/11) : *Prémonition du combat* remplacé par `+10 %` d'esquive en mêlée.**
6. **[TODO Équipement & Loot]** : ~~calibrage des armes & upgrades cloisonnées.~~ **ACTÉ (19/11) dans `armes.csv` et `Améliorations.csv`.** Reste : définir la stat de scaling des *On-Hit* d'armes au cas par cas + plafonner le Cristal personnel (`qcrystal_1..8`).
7. **[TODO Craft & Établi]** : ~~recalibrer les seuils de niveau + ajouter armes de base & 24 upgrades doubles.~~ **ACTÉ (19/11) dans `Craft.csv`** : toutes les armes de base non-laser craftables (hors Sabres Laser), 24 upgrades doubles intermédiaires ajoutées, et verrou de niveau `itemcreate.2da` (**`Mk I = Niv. 1 / Mk II = Niv. 10 / Mk III = Niv. 15 / Mk IV-T5 = Niv. 20`**, `1 / 10 / 18` sur lignées 3 tiers ; test moteur de la colonne `level` à confirmer). *(Nettoyage des anciens tags `[Combinée Interm.]` effectué.)*
8. **[TODO Ennemis]** : trancher les 4 décisions D1–D4 dans `equilibrage_ennemis.md` (profils défensifs par famille, boucliers ennemis, soins, phases de boss).
9. **[TODO Pouvoirs]** : ~~valider *Camouflage par la Force* et rééquilibrer les pouvoirs.~~ **ACTÉ (19–21/11) dans `Spé Pouvoirs.csv`** :
   - **Pouvoirs standards** : aucun cap de dés en L3, hiérarchie offensive par armure, Tempête `1d6/Niv` sans drain PF sur **Réflexes**, Mise à mort `1d8/Niv` sans 50 % PV max, Lancer de sabre `1d4/Niv` + Renversement Vig en L1 / ignore RD en L2, **Lenteur / Affliction / Peste** refondus en maladie contagieuse (`42 s` max, tick `6 s`, propagation `5 m` à la mort, ralenti + `½ Niv` dég/tick + `-3/-6/-9` caracs, jet de Vigueur chaque tick à DD `+0/+4/+8`), **Barrière & Résistance à l'énergie** alignés en **Armure moyenne** (`RD 4/8/12`, personnel, `60 s`, `15/25/35 PF`, sans effet groupe ni Poison), **Contrôle de la respiration** (`+4` saves vs Poison passif + actif immunité `240 s`), Talent `+2/+3/+4`, buffs des pouvoirs faibles ; **rééquilibrage DS/LS & sauvegardes (21/11)** : *Terreur/Horreur/Insanité* (Légère) refondu en DoT mental (`Niv` dég/rd) + `-4/-6/-8 Atq` sans perte d'action (`24 s` échec / `6 s` réussite Volonté), *Champ de stase* (Robe) jusqu'à `36 s` avec DD Vigueur dégressif `-3/rd`, *Vague de Force* (Moyenne) transformé en **Tourbillon AoE `6 m` / `12 s`** (`½` dégâts immédiats sur Réf réussie), *Absorption de vie / Champ de mort / Festin de mort* (`20/40/55 PF`) passé à `1d3/Niv` (soin = 100 % dégâts) avec **L3 *Festin de mort*** convertissant l'excédent en PV temporaires (`24 s`, non cumulable).
   - **Refonte complète des 6 Ultimes de Prestige (uniformisés L1/L2/L3 aux niv. 1/5/9 de prestige, philosophie Kreia) + 2 Ultimes d'alignement** :
     - **Maraudeur Sith — *Stigmate de Force I–III*** *(ex Fureur Sith, `Armure lourde`, 30 s)* : `+2/+4/+6` FOR & DEX, immunité Stase/Paralysie, **`+1 atq/rd` dès L1** (non cumulable *Vitesse*), coût `-5 %` PV max/round (arrêt auto ≤ `25 %` PV max).
     - **Maître d'armes Jedi — *Cicatrice de Force I–III*** (`Armure lourde`, 30 s, nouveau) : soin `+2/+4/+6 %` PV max/round + `+1/+2/+3` sauvegardes + immunité Peur/Étourdissement (L2) et Paralysie (L3).
     - **Assassin Sith — *Spectre de la Force I–III*** *(ex Camouflage par la Force, `Armure moyenne`, passif, exclusif Assassin)* : furtivité sans ceinture + course furtive, embuscade `+2d6`/Stun 1t, L3 kill → crit confirmé + `+25 %` esquive 2t.
     - **Jedi protecteur — *Affranchi de la Force I–III*** (`Armure lourde`, passif, nouveau) : `+1` tous les 8 rangs combinés sur 4 paires (`Informatique+Sécurité` → Atq, `Démolition+Réparation` → Dég, `Vigilance+Discrétion` → CA, `Persuasion+Premiers soins` → Saves ; plafond `+3/+5/+7`) + L2 `+25 %` efficacité objets profanes + L3 Résistance à la Force passive (`15 + Niv`).
     - **Seigneur Sith — *Déchirure de la Force I–III*** *(ex Annihilation de l'opposition, `Armure lourde`, 45 s)* : `-2/-4/-6` Atq, Sauvegardes et CA en zone 15 m (`Volonté` annule).
     - **Maître Jedi — *Écho des Liens I–III*** *(ex Inspiration des disciples, `Armure lourde`)* : L1 (30 s) partage buffs personnels avec l'allié le plus proche ; L2 (45 s) tout le groupe ; L3 (60 s) buffs personnels + soins partagés avec tout le groupe (sans restriction d'armure sur les alliés, comme Kreia).
     - **Alignement** : *Grâce du côté Lumineux* (`Armure moyenne`, lancer instantané 50 PF, *Vitesse* plafonnée à `+1 atq/rd` si armure portée) ; *Écrasement de Force* (`Armure légère`, `1d8/Niv` dégâts purs sans cap + immo 6 s, Vig ½ et annule).
   - **Coûts en PF évolutifs par rang (`Spé Pouvoirs.csv`, acté le 21/11)** : grille complète `L1 / L2 / L3` calibrée sur les réserves réelles Niv. 25 (`Gardien ~200 / Sentinelle ~300 / Consulaire ~500 PF`) — L1 `10–20 PF`, L2 `20–35 PF`, L3 `35–65 PF` (ex. *Tempête* `15/30/50`, *Champ de stase* `15/30/50`, *Insanité* `15/25/45`, *Soins* `20/35/50`, *Grâce* `50`, *Écrasement* `60`), réglant aussi la pénalité d'alignement opposé (`~85–90 PF` en Lumineux pour *Tempête L3*).
   - **Pouvoirs de débuff & sauvegardes (clos le 21/11)** : *Méditation de combat* indexée sur `mod. CHA` non plafonné (L1 groupe, L2 ajoute malus ennemis 10 m Vol annule, L3 `+2` et 15 m), *Subterfuge / Confusion* conservés en vanilla, *Déchirure* conservée en Volonté annule, *Cri de Force* confirmé sur **Volonté** (plus rare que Vigueur : 5 vs 8 lignées ; `½` dégâts et annule le malus), *Blessure L1* harmonisée sur Vigueur `½` dégâts.
10. **[TODO Outil annexe]** : **Convertisseur de sauvegarde vanilla → mod** (permettre de reprendre une partie existante avec la nouvelle structure de dons / pouvoirs / équipements).
11. **[TODO Respec personnage]** : prévoir un moyen de **réinitialiser / respec** son personnage en jeu (**classe de base non comprise** — dons, pouvoirs, compétences, caractéristiques / classe de prestige à préciser), probablement via un **dialogue avec T3-M4** *(faisabilité moteur à vérifier : reset de niveau / dons / pouvoirs via script ou utilitaire externe)*.
