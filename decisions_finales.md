# Décisions Finales d'Équilibrage — Synthèse (*D20 Overhaul*)

Ce document est le **contrat de game design** : chaque décision actée y figure sous forme condensée.
Les justifications, la recherche (JdR papier, D&D, consensus communauté) et les notes d'implémentation sont dans **[`decisions_annexes.md`](decisions_annexes.md)**.

> **Hiérarchie des sources (README §0)** : les CSV `Kotor 2 - rééquilibrage - *.csv` sont la référence opérationnelle côté utilisateur — ce contrat en est la **consolidation**. En cas de divergence, les CSV font foi ; ce document doit alors être resynchronisé.
> **Dernière grosse consolidation : 25/11/2026** (validation **Adaptateur Gamorréen II** `2M/HC ↔ 1M` + levée de l'interdiction des postures 2M/HC, extension `iprp_resistcost.2da` aux RD exactes `2/3/4/6/12` ; cloisonnement strict des rôles par slot d'amélioration d'arme le 19/11 ; scaling DEX `100 % / 50 %` et armures le 18/11 ; arbres d'armures le 17/11 ; refonte postures/spé d'arme/spé carac le 15/11/2026). Journal des arbitrages : annexes §9.

| Domaine | Décision (résumé) | Détail |
| :--- | :--- | :---: |
| Progression des classes | Symétrie inverse Combattants ↔ Mages (dons ↔ pouvoirs) | §1 |
| Pouvoirs de la Force | Aucun ajout ; nerf du haut du panier, buff des alternatives, restauration via Éveil de Force | §2 |
| Établi & Boss | Plafonds `+2/+5/+10`, cloisonnement strict des rôles par slot (1 seul slot de dégâts bruts par catégorie), RD boss **`2/5/8`**, combats 5–10 rounds | §3 |
| Postures & spécialisations d'armes | 4 postures (Duel, Ambidextrie, Arme Lourde, Arme haute cadence) × 8 familles (4 mêlée + 4 tir) ; dons vanilla Duel/TWF/Finesse/Focus/Spec **supprimés** | §4 |
| Spécialisations de caractéristique | 6 arbres exclusifs (FOR, DEX, CON, INT, SAG, CHA) — un par caractéristique, ordre canonique | §5 |
| Architecture de dons | Posture (3) + famille (3) + spé carac (3) + défenses ; budgets Niv. 30 : **22 / 18 / 15** dons (pouvoirs **12 / 16 / 24**), gating par classe/prestige sur Rangs II–III | §6 |
| Dons transversaux | 7 dons d'Éveil de Force + *Esquive Totale* (anti-AoE) | §7 |
| Armures & Défenses | RD native (Interm. 2 / Lourde 4), 30 sur-couches renforcées exclusives aux intermédiaires (`UpgradeLevel`), 3 arbres de dons par type, dégradé de pouvoirs, *Condition physique I–III* conservé vanilla | §8 |
| Contrat mathématique | DPR nets et durées de boss cibles par phase de jeu | §9 |
| Furtivité | Embuscade : première attaque depuis la furtivité = critique confirmé (simulation scriptée) | §10 |
| Conventions & principes | DD Spé d'arme (`10`/`5` + Niv + carac), grenades (`10` + Niv + INT), fléchettes/roquettes (`12` + Niv + INT), *On-Hit* armes (`3/5/7/9` + Niv + carac directrice de l'arme), procs `plage/20`, ordre canonique, « les synergies se trouvent » | §11 |

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
2. **Hiérarchie :** *Éclair/Tempête* (zone) et *Blessure/Étranglement/Mise à mort* (monocible) restent les meilleurs DPS de Force — **nerfés à la base**, restaurables via **Éveil de Force**. Les alternatives sont boostées sans jamais dépasser ce plafond.
3. **Alignement :** *Champ de Stase* reste un pouvoir du Côté Lumineux.
4. **Pouvoirs de Prestige (uniformisés `L1 / L2 / L3` aux niv. 1/5/9 de prestige) & Ultimes d'alignement** *(source : `Spé Pouvoirs.csv`)* :

| Classe de Prestige | Pouvoir (L1 → L3) | Armure max | Effet synthétique |
| :--- | :--- | :---: | :--- |
| **Maraudeur Sith** | **Stigmate de Force** *(ex Fureur)* | Lourde | `30 s` : `+2/+4/+6` FOR & DEX, immunité Stase/Paralysie, `+1 atq/rd` dès L1 *(non cumulable Vitesse)* ; `-5 %` PV max/rd *(arrêt ≤ 25 % PV)* |
| **Maître d'Armes Jedi** | **Cicatrice de Force** *(nouveau)* | Lourde | `30 s` : soin `+2/+4/+6 %` PV max/rd, `+1/+2/+3` sauvegardes, immunité Peur/Étourdissement (L2) et Paralysie (L3) |
| **Assassin Sith** | **Spectre de la Force** *(ex Camouflage)* | Intermédiaire | Passif : furtivité sans ceinture + Course furtive + `+4/+8/+12` Discrétion ; L2 embuscade `+2d6`/Stun 1t ; L3 kill → crit confirmé + `+25 %` esquive (2t) |
| **Jedi protecteur** | **Affranchi de la Force** *(nouveau)* | Lourde | Passif : `+1` par 8 rangs combinés sur 4 paires de compétences → Atq, Dég, CA, Saves *(cap `+3/+5/+7`)* ; L2 `+25 %` consommables ; L3 Résist. Force `15 + Niv` |
| **Seigneur Sith** | **Déchirure de la Force** *(ex Annihilation)* | Lourde | `45 s`, zone `15 m` : `-2/-4/-6` Atq, Sauvegardes et CA *(Volonté annule)* |
| **Maître Jedi** | **Écho des Liens** *(ex Inspiration)* | Lourde | Partage les buffs personnels avec l'allié le plus proche (L1, `30 s`), tout le groupe (L2, `45 s`), + soins partagés (L3, `60 s`, sans restriction d'armure) |

*Ultimes d'alignement :* **Grâce du côté Lumineux** (*Armure intermédiaire*, `50 PF`, instantané, *Vitesse* plafonnée à `+1 atq/rd` sous armure) · **Écrasement de Force** (*Armure légère*, `60 PF`, `1d8/Niv` dégâts purs sans cap + immo `6 s`, Vig ½ et annule).

### 3. Établi & Boss (Rythme des Combats)

**A. Plafond des améliorations d'armes** (pièces `u_r_*`, `u_m_*`, `u_l_*` retravaillées — inventaire de référence : CSV *Améliorations*, 226 pièces) :
- Early (Niv. 1–10, Mk I) : max **`+2` dégâts moyens/coup** • Mid (Niv. 11–18, Mk II) : max **`+5`** • Late (Niv. 19+, Mk III) : max **`+10`** *(valeurs max pour une arme disposant de tous ses emplacements d'amélioration).*
- **Slots autorisés par famille d'arme** (*Armes.csv*, via hiérarchie `UpgradeLevel`) :
  - **Mêlée (`Poignée < Lame < Cellule`)** : *Mains nues* (0 slot) · *Impact* (1 : Poignée) · *Traditionnelle* (2 : Poignée, Lame) · *Résonance* (3 : Poignée, Lame, Cellule) · *Laser* (Cristal de couleur + 2 Cristaux d'amélioration + Émetteur + Lentille + Cellule). *Bâton Gaffi* retiré du jeu (héritage KotOR 1).
  - **Distance (`Lunette < Pack d'énergie < Chambrage`)** : *Tir Tactique* (1 : Lunette) · ***Tir d'Assaut* & *Tir Assassin*** (2 : Lunette, Pack) · *Tir Pénétrant* (3 : Lunette, Pack, Chambrage). *(Tir d'Assaut verrouillé à 2 slots le 19/11 : combiné au `+1 Atq/round` de Spé III, le Chambrage écraserait Tir Pénétrant.)*
- **Cloisonnement strict des rôles par emplacement** (acté le 19/11 — interdit le cumul de dégâts bruts sur plusieurs slots et amplifie l'identité de chaque famille d'armes) :
  - **Mêlée** : **Poignée** = `+Attaque` / `+CA` uniquement (0 dégât) · **Lame** = `Acéré`, `Critiques massifs`, *On-Hit* scalés, `vs Droïdes` (0 dégât brut régulier) · **Cellule** *(Résonance seule)* = **seul slot à dégâts réguliers** (physiques/élémentaires).
  - **Distance** : **Lunette** = `+Attaque`, `Acéré`, ***On-Hit* scalés** (réintroduits sur les lunettes, 0 dégât) · **Pack d'énergie** = `Critiques massifs`, `Ion / vs Droïdes & Boucliers`, ou léger bonus constant (`+1..+3` max) · **Chambrage** *(Tir Pénétrant seul)* = **seul slot à gros dégâts bruts**.
  - **Sabre Laser** : **Émetteur** = `+CA`, `Parade de blasters`, ***On-Hit* scalés** (réintroduits sur les émetteurs, 0 dégât) · **Lentille** = `+Attaque`, `Acéré`, `Critiques massifs` (0 dégât régulier) · **Cellule** = **seul slot à dégâts réguliers du sabre** · **Cristaux (×2)** = `+Caractéristiques` (plafonnées), `Régénération PV/PF`, `+Attaque`, `Parade`, `vs Alignement/Droïdes` (0 dégât brut générique) · **Cristal personnel de l'Exilé** *(refonte 22/11)* :
    - **Stats (3 paliers, `0` dégât brut / `0` On-Hit / `0` save)** : **`+2/+1/0`** (`Niv. 1–14`), **`+4/+2/+1`** (`Niv. 15–21`), **`+6/+4/+2`** (`Niv. 22+`) sur `1re stat / 2e stat / 4 autres` ; attribué auto via `GetAbilityScore` (2 meilleures stats de base) et **personnalisable via dialogue avec Kreia** (`30 paires × 3 paliers = 90 .uti` générés par script).
    - **Effets de multiclassage (2 effets cumulables max : classe de base + classe de prestige, scriptés quand le cristal est monté dans le sabre tenu)** :
      - *Base* : **Gardien** (`+1 PV/niv` & `+1 Atq`) · **Sentinelle** (`+1 Atq`, `+1 Défense`, `+1 Sauvegardes`) · **Consulaire** (`coût en PF des pouvoirs -10 %`).
      - *Prestige* : **Maître d'Armes** (On-Hit `+1 Atq` & `+1 CA` 2 rds, cumulable cap `+5`) · **Maraudeur Sith** (On-Hit soigne `+1 % PV max`) · **Jedi protecteur** (`+3` toutes compétences) · **Assassin Sith** (`Critiques massifs +2d6` & `+1` plage de critique) · **Maître Jedi** (`+2 DD` pouvoirs & durée buffs `+25 %`) · **Seigneur Sith** (`+2 DD` pouvoirs & `Régén. PF +3`).
- **Principe de compensation** : l'absence de `Cellule` / `Chambrage` sur les familles à 1 ou 2 slots plafonne leurs upgrades plus bas à l'établi, en échange de **dégâts de base plus élevés, d'une plage de critique élargie ou d'un multiplicateur de critique supérieur** *(ajustements B3-D1 du 24/11 : `Heavy_Blaster` `1d12`, `Hold_Out_Blaster` `1d6`)*.
- **Calibrage des armes nommées / loot & reliques (B2-1a, acté le 25/11)** : retrait des bonus de dégâts gratuits sur les armes craftables Niv. 1 (`w_melee_03`, `w_melee_09`) ; plafonnement des bonus `.uti` (`prop 11`) sur les armes de série/loot par palier (**T1–14 : `+2`** · **T15–22 : `+1d4`/`+3`** · **T23–30 : `+1d6`/`+4`**) en préservant leurs effets d'identité ; **6 reliques légendaires endgame** (*Arg'garok*, *Épée de Freyyr*, *Bâton électrique géonosien*, *Blaster de Freedon Nadd*, *Fusil auto zabrak*, *Fusil à répétition d'Ondéron*) remises à `ulvl = 0` (non modifiables à l'établi) avec bonus unique plafonné à `+1d8` / `+1d10`.

**B. Boss** :
- **Règle d'or :** aucun boss tué en moins de 4 rounds ; cible **5–10 rounds** (10–15 pour Sion/Traya).
- **RD passive** des Sous-Boss/Boss (`Set_4`/`Set_5`) : **`RD 2`** (Early) / **`RD 5`** (Mid) / **`RD 8`** (Late) *(recalibrée le 19/11 pour débloquer les builds multi-coups et les armures sans toucher aux PV des boss)*.
- **`damagemult` des boss réduit** (`autobalance.2da`) pour que le joueur tienne aussi 5–10 rounds.

### 4. Postures & Spécialisations d'armes (refonte 13–15/11)

**Dons vanilla supprimés** (remplacés par les dons custom ci-dessous, cf. *Feats.csv*) :
`DUELING` I-III, `TWO_WEAPON_FIGHTING` I-III, `FINESSE_MELEE_WEAPONS`, `FINESSE_LIGHTSABERS`, `WEAPON_FOCUS/SPEC` (pistolets, fusils, mêlée, sabres).

**A. Les 4 postures** (*WIP Feats.csv* — chacune 3 rangs, recréés **from scratch**) :

| Posture | Base moddée | Rang I → III | Notes |
| :--- | :--- | :--- | :--- |
| **Duel** | Dégâts mêlée `150 % FOR` (règle moteur 1M, main gauche vide) ; **distance 1M `150 % DEX`** | `+2/+4/+6 Atq` et **plage de critique +1/+2/+3** | Prérequis : arme à une main **ou mains nues** ; la plage élargie augmente la fréquence des procs des Spé d'arme (proc = plage/20 par coup) |
| **Ambidextrie** | Dégâts `100 % / 50 % FOR` (mêlée) ou **`100 % / 50 % DEX` (distance)** ; malus 2 armes `-6/-10` (`+2/0` si arme équilibrée en main gauche) | `-6/-6 & +1 CA` → `-4/-4 & +2 CA` → `-2/-2 & +3 CA` | Identité parade/CA ; malus de main gauche remonte mais l'attaque s'achète de la Défense |
| **Arme Lourde (2M)** | Mêlée `200 % FOR` / distance `150 % DEX` | `+1/+2/+3 Atq` ; mêlée **`215→235→250 % FOR`** ; distance **`165→185→200 % DEX`** | Prérequis : arme à deux mains non double — mêlée **et** distance |
| **Arme haute cadence** (ex « Arme Double & Repeating ») | Dégâts `150 % / 50 % FOR` (arme double mêlée) ou **`150 % / 50 % DEX` (répétition distance)**, malus moddé **`-5 CA`** (au lieu de `-6/-10 Atq`) ; **toutes les armes `HC` sont équilibrées (`balanced`)** | `+1/+1` & CA `-3` → `+2/+2` & `-2` → `+3/+3` & `-1` | Repeating et lourds à répétition partagent cette posture ; moteur : les repeating **ne sont pas** des armes doubles (`weaponwield 6 ≠ 3`) |

**B. Les 8 familles de spécialisation** (*WIP Feats.csv* — rang I : `+2 Atq & +2 Dégâts` partout) :

| Famille (armes) | Rang II (effet sur coup) | Rang III |
| :--- | :--- | :--- |
| **Impact** (mains nues, matraque, torche à plasma, bâton, pique de Force) | **Renversement** 1 tour (Vigueur, DD 10, proc plage/20) | Renversement **2 tours** |
| **Traditionnelle** (épées courte/longue/double, hache gamorréenne, lame wookiee) | **Bris d'armure** : -3 CA, 2 tours (Vigueur, DD 5, proc par coup) | Bris d'armure cumulable, **+1 tour** |
| **Résonance** (vibrolame, vibro-épée, vibrolame double) | **Ébranlement** : -4 Atq & Dégâts, 1 tour (Réflexes, DD 5, proc par coup) | Empilable : -2/proc, **plafond -8**, durée rafraîchie |
| **Laser** (sabre court, sabre, double sabre) | **Bris de volonté** : -4 sauvegardes, 2 tours (Volonté, DD 5, proc par coup) | Bris de volonté **sans jet de sauvegarde** |
| **Tir d'Assaut** (pistolet blaster, carabine, blaster à répétition) | **Aucun malus en mêlée** | **+1 Atq/round** main directrice |
| **Tir Pénétrant** (blaster lourd, fusil blaster, arbalète wookiee, blaster lourd à répétition) — *ex « Tir Lourd », renommé 15/11* | **Repousse 3 m** (Vigueur, DD 5 ; sauvegarde par coup qui touche, effet 1×/round même après plusieurs échecs) | **+5 Dégâts** |
| **Tir Tactique** (armes à ions et soniques) | **Stun** 1 tour + stun droïde (Vigueur, DD 10, proc plage/20) | Stun **2 tours** |
| **Tir Assassin** (blaster de poche, disrupteurs) | **Attaques sournoises +2d6**, donne la capacité d'en faire | **Multiplicateur de critique +1** |

*Exception assumée (15/11)* : le `mult. crit. +1` du Tir Assassin touche au critique malgré le principe « les Spé ne touchent pas au critique » — c'est LA spécialité sournoise, et elle n'empiète pas sur Duel (multiplicateur ≠ plage).

**C. Mains nues** (révisé 24/11) : la branche dédiée (*Arts Martiaux / Arts Matukai*) reste **supprimée**. Les mains nues appartiennent désormais à la famille **Armes d'Impact** (accès à *Spécialisation Arme d'Impact I–III* et au Renversement), en plus de la **posture Duel** (les poings comptent comme arme 1M), de la chaîne *Spécialiste mains nues* **plafonnée au Rang III (`+1d4 / +2d4 / +3d4` aux Niv. 4 / 12 / 19 base ou Niv. 4 prestige ; Rangs IV–VIII supprimés)** et des Spé de caractéristique (Matukai).

**D. L'axe distance/mêlée** : parité de viabilité, asymétrie de coûts — chaque posture/famille distance atteint les cibles DPR du §9 par son propre chemin (`150 % DEX` en `1M` seul, `100 % / 50 % DEX` en Ambidextrie, `150 % / 50 % DEX` en `HC`, `150 % → 200 % DEX` via Arme Lourde `2M`, `INT` via Gand II, utilitaires via les familles de tir) ; la mêlée paie en défense et approche, la distance paie en contreurs (boucliers d'énergie, déflexion). Équilibrage fin par le chantier ennemis.

### 5. Spécialisations de Caractéristique (refonte 13–14/11)

**Un arbre par caractéristique, ordre canonique FOR, DEX, CON, INT, SAG, CHA. Les 6 arbres sont mutuellement exclusifs** (chaque rang I interdit les cinq autres — mécanisme : garde-fou scripté, la colonne `exclusion` de `feat.2da` ayant été testée KO le 23/11, cf. Partie 2 #1). Source de vérité : *WIP Feats.csv*.

| Arbre (carac) | Rang I | Rang II | Rang III (signature) |
| :--- | :--- | :--- | :--- |
| **Raffinement Gamorréen** (FOR) | +1 FOR ; + ½ mod. FOR en rangs sur **toutes** les compétences | +2 FOR ; **Adaptateur Gamorréen** (établi portatif toujours accessible + bascule en posture hors combat toute arme 2M/HC en **1M** et inversement, mêlée et distance) ; arme haute cadence 1M en **main principale** = **`+1` atq/round** (`0` CA, aucun bonus en main gauche) ; **n'interdit plus** les postures Arme Lourde (2M) et Haute cadence (HC) | +3 FOR ; immunité au mental |
| **Techniques Echanis** (DEX) | +1 DEX ; attaque mêlée : FOR/DEX (si DEX > FOR) | +2 DEX ; dégâts mêlée : FOR/DEX | +3 DEX ; **supprime le plafond de DEX des armures** |
| **Voie du dragon Krayt** (CON) | +1 CON ; RD + ½ mod. CON (arrondi sup.) | +2 CON ; **transfusion** : toutes les 6 s, 5 % PV max → 5 % PF max si PF < 50 % (jamais sous 75 % PV) | +3 CON ; toutes sauvegardes + mod. CON |
| **Chasseur de prime Gand** (INT) | +1 INT ; **grenades et mines `+5 %` dégâts / rang total de Démolition** | +2 INT ; attaque & dégâts distance : DEX/INT (si INT > DEX) | +3 INT ; **Maître Artificier** : rayon grenades `4→6 m`, perce *Esquive Totale*, `50 %` de non-consommation |
| **Maîtrise Matukai** (SAG) | +1 SAG ; **ajoute** le mod. de SAG à l'attaque (par-dessus la carac directrice) | +2 SAG ; sauvegardes + ½ SAG ; **réussir une sauvegarde inflige SAG dégâts à l'attaquant** | +3 SAG ; **SAG remplace DEX pour la CA** ; tout ennemi vous ratant subit SAG dégâts par attaque échouée |
| **Héritage de Nomi** (CHA) | +1 CHA ; compagnons 100 % de l'XP | +2 CHA ; groupe : sauvegardes + mod. CHA | +3 CHA ; **Défense + mod. CHA** |

Notes d'équilibrage : la transfusion Krayt échange invariablement **25 % PV ↔ 25 % PF** (rituel complet) ; les dégâts de punition Matukai contournent la RD (scriptés) et ne peuvent pas critiquer ; tous les bonus de CA custom (Nomi III, Matukai III, Esquive Balistique, Armure Tactique) sont sommés dans un unique `EffectACIncrease` (cf. Partie 2 #1 T4).

### 6. Architecture de Dons & Budgets

**Nouvelle structure (post-15/11)** : chaque personnage combine **une posture** (3 rangs) + **une famille de Spé d'arme par catégorie d'armes utilisées** (3 rangs chacune) + **un arbre de Spé carac** (3 rangs, exclusif) + **défenses** (Robustesse 3, Condition physique 3 ou arbre d'armure 3) + **Éveil de Force** (7, profil caster) + dons actifs vanilla conservés (Déluge, Attaque en puissance, Coup critique, Décharge, Tir rapide, Sniper).

**Budgets Niv. 30 (actés le 19/11)** : **22** (Gardien) / **18** (Sentinelle) / **15** (Consulaire), pour **12 / 16 / 24** pouvoirs.
- Les arbres restent compacts en **3 rangs marquants** (pas de découpage massif en « demi-dons » ; le volet furtivité est intégré dans *Armure Tactique*).
- **Paliers de niveau minimum (`mincharlevel`, actés le 22/11)** :
  - **Dons martiaux de base** (Actifs vanilla, Robustesse, **4 Postures**) : **`Niv. 1+ / 4+ / 8+`**.
  - **Grands arbres de spécialisation** (**Spé Carac**, **Spé d'arme**, **Armures**, **Éveil de Force** Amplifié/Pénétrant) : **`Niv. 1+ / 8+ / 15+`** *(Pouvoir Prolongé = `Niv. 1+`)*.
- **Gating par classe / classe de prestige** (acté le 19/11 — étend le modèle *Éveil de Force* aux grands arbres) :
  - **Éveil de Force** : R1 tous Jedi/Sith · R2 **Consulaire / Maître Jedi / Seigneur Sith** · R3 **Maître Jedi / Seigneur Sith**.
  - **Spécialisations d'arme (8 familles)** : R1 tous · R2 **Gardien / Sentinelle** + leurs prestiges · R3 **Maître d'Armes / Maraudeur Sith**.
  - **Postures** : R1 & R2 tous · R3 *Duel* = tous, *Ambidextrie / Arme Lourde / Haute cadence* = **tous sauf Mages**.
  - **Armures** : R1 tous (si port) · **Juggernaut** R2 Gardien/prestiges martiaux, R3 **Maître d'Armes / Maraudeur Sith** · **Armure Tactique** R2 Sentinelle/prestiges hybrides, R3 **Jedi protecteur / Assassin Sith** · **Esquive Balistique** R2 Gardien/Sentinelle + prestiges, R3 **Maître d'Armes / Maraudeur / Jedi protecteur / Assassin**.
  - **Spécialisations de Caractéristique (6 arbres)** : **ouvertes à toutes les classes**, paliers par niveau (**Niv. 1+ / Niv. 8+ / Niv. 15+**).
  - **Compagnons (acté le 19/11 — gating par classe + 2 exceptions level-up)** :
    - Classes **non-Jedi** (`SOL`, `SCT`, `SCD`, `TEC`, `DRC`, `DRX`) : accès aux Rangs III martiaux/armures pertinents dès le **Niveau 15+** (`minattackbonus = 15` dans `feat.2da`, exact grâce à `CLS_ATK_1` `BAB 1.0`) — `SOL` (Spé d'arme III, Juggernaut III, Esquive Balistique III), `SCT/SCD` (Spé d'arme III, Esquive Balistique III, Armure Tactique III), `TEC` (Armure Tactique III, Spé d'arme III), `DRC` (Spé d'arme distance III), `DRX` (Spé d'arme distance II). Les compagnons convertis en Jedi suivent les règles normales de leur classe Jedi.
    - **Exception Kreia (Niv. 15+)** : considérée comme **Maître Jedi** pour les dons sélectionnables en level-up (accès à tout **Éveil de Force**, dont Rangs III).
    - **Exception Visas (Niv. 15+)** : considérée comme **Assassin Sith** pour les dons sélectionnables en level-up (accès aux dons sélectionnables d'Assassin Sith : *Armure Tactique III*, *Esquive Balistique III*, *Esquive Totale*).

### 7. Dons Transversaux : Éveil de Force & Esquive Totale

**A. Éveil de Force (7 dons, calibrés sur le budget du Consulaire)** :

| Don | Rangs | Effet |
| :--- | :---: | :--- |
| **Pouvoir Amplifié** | 3 | Dégâts des pouvoirs offensifs `+15/+30/+50 %` (coût `+2/+4/+6 PF`) |
| **Pouvoir Pénétrant** | 3 | `+2/+4/+6` au DD de sauvegarde des pouvoirs offensifs et de contrôle |
| **Pouvoir Prolongé** | 1 | Durée de tous les buffs de Force `×2` |

**B. Esquive Totale** (`FEAT_EVASION`, ligne 125) — contre-mesure anti-AoE :
- Réussite du jet de sauvegarde face à une AoE → **0 dégât** ; échec → **dégâts ÷ 2**.
- Sélectionnable au **Niv. 15+** par **Jedi Protecteur**, **Assassin Sith** et **Visas Marr** ; auto Éclaireur niv. 6 (Mira) ; octroyé à tous les Jedi/Sith ennemis 20+ (via `k_inc_force.nss`).

### 8. Armures : RD Native, 3 Arbres de Dons, Dégradé de Pouvoirs

Décisions actées (08/11/2026) — justifications dans [`decisions_annexes.md`](decisions_annexes.md#1-armures--recherche-et-justifications) :

**A. Règles natives sans don (par catégorie d'armure)** — recalibrage CA & plafonds DEX (source : *Armures.csv*) *(hors Techniques Echanis III §5 qui supprime le plafond)*. **RD native lourde = `4/-`, intermédiaire = `2/-` ; refonte des 60 améliorations d'armures (`30` sous-couches `u_a_unde_01..30` + `30` sur-couches `u_a_over_01..30`, acté 24/11) :**

| Type | CA base | Plafond DEX | **RD Physique & Énergie native** | **Accès Établi (`UpgradeLevel` 0 / 1 / 2 / 6)** |
| :--- | :---: | :---: | :---: | :--- |
| Légère | **4–5** | **+14 à +16** *(AC4/ZS `4/+16`, Ubese `5/+15`, AC5 `5/+14`)* | **0** | **1 seul slot** (`ulvl 1`) : **15 Sous-couches communes** (*Anti-environnement*, *Bio-restaurative*, *Fortificatrice*) |
| Intermédiaire | **6–7** | **+3 à +4** *(AC6 `6/+4`, AC7 `7/+3`)* | **RD 2** | **2 slots** (`ulvl 6`) : **30 Sous-couches communes** *(identiques Lourde)* + **30 Sur-couches exclusives renforcées** (*8 lignées* compensant le retrait des sous-couches doubles) |
| Lourde | **10–11** | **+0 à +1** *(AC8 `10/+1`, AC9 `11/+0`)* | **RD 4** | **1 seul slot** (`ulvl 2`) : **30 Sous-couches complètes** (*communes + Renforçante, Flexible, Duracier*) |

*Hiérarchie CA validée (25/11/2026)* : **Nue** : Légère (`19–20`) > Lourde (`11`) > Intermédiaire (`10`) · **En jeu (upgradée + dons + buffs)** : Légère (`+Esquive Bal.`) ≈ Bure *full buff* (*Armure +6, Vitesse +4, Talent +2*) > Intermédiaire upgradée (`+2 CA Sur-couche +2 DEX Flexible + Armure Tactique`) > Lourde (`RD 11/- + 30 % imm.`). Sans ses buffs temporaires, la Bure chute sous l'Intermédiaire upgradée (viabilité conditionnée aux buffs).

*Note technique (17–24/11)* : `swkotor2.exe` limite en dur les armures à **1 slot sur-couche (`upgradetype 10`) + 1 slot sous-couche (`upgradetype 11`)** et vérifie linéairement `upgrade.UpgradeLevel <= item.UpgradeLevel` (`0x4cbcd0`). En plaçant les sous-couches légères à `1`, les sous-couches blindées à `2`, et **toutes les 30 sur-couches à `6`**, les armures légères (`1`) et lourdes (`2`) n'ont chacune accès qu'à 1 slot (Sous-couche, avec pool réduit sur Légère et complet sur Lourde), tandis que les armures intermédiaires (`6`) partagent le pool complet de sous-couches de la Lourde et détiennent l'exclusivité absolue des 30 sur-couches renforcées (sans aucun don requis).

**B. Trois arbres de dons** (3 dons chacun, arbitrage du 17/11 — source : *WIP Feats.csv*) :

| Arbre | Rang I | Rang II | Rang III | Identité |
| :--- | :--- | :--- | :--- | :--- |
| **Juggernaut** (lourde) | RD 3/-, immunité tous dégâts 10 % | RD 4/-, immunité 20 % | RD 5/-, immunité 30 % | Encaisser les dégâts |
| **Armure Tactique** *(ex Blindage de Combat)* (interm.) | RD 3/-, +1 CA, durée des boucliers +100 %, furtivité sans ceinture (armure intermédiaire portée) | RD 4/-, +2 CA, absorption boucliers ×2, accès à Course furtive (armure intermédiaire portée) | RD 5/-, +3 CA, absorption boucliers ×3 | Spé ingénieur et craft — boucliers & furtivité |
| **Esquive Balistique** *(ex Seconde Peau)* (légère) | Esquive +10 %, +1 CA base | Esquive +20 %, +2 CA base | Esquive +30 %, +3 CA base | Esquiver toutes les attaques *(pas d'augmentation de la CA gagnée via caractéristiques)* |

**RD cumulée max** (Juggernaut III + native lourde 4 + Robustesse II 2) : **RD 11 + 30 % d'immunité** (≈ −53 % sur un coup de 23, ≈ −40 % sur un coup de 68). **Pas de cap global d'immunité** (acté le 19/11 ; révisable ultérieurement selon les retours joueurs).

**C. Dégradé des pouvoirs sous armure** (`forbiditemmask`, source : *Spé Pouvoirs.csv* & *Armures.csv*) : **bure** = tous ; **légère** = autorise *Talent de Force I–III*, *Suppression/Destruction de Force*, *Terreur/Horreur/Insanité*, *Cri de Force*, *Écrasement de Force* + pouvoirs interm./lourde (bloque *Vitesse*, *Armure de Force*, *Stase*, *Tempête*, *Mise à mort*, *Absorption de vie* ; aucune exception Force-friendly sur Ubese / Zeison Sha, décision 23/11) ; **interm.** = *Guérison/Soins*, *Revitalisation*, *Barrière de Force*, *Résistance à l'énergie*, *Peste*, *Poussée/Tourbillon/Vague*, *Méditation de combat*, *Destruction de droïde*, *Subterfuge/Confusion*, *Spectre de la Force*, *Grâce du côté Lumineux* + pouvoirs lourde ; **lourde** = *Corps de Force*, *Lancer de sabre*, *Résistance/Immunité Force*, *Absorption de Force*, *Parade/Renvoi*, *Contrôle de la respiration*, et 5 ultimes de prestige.

**D. *Condition physique I–III* (`CONDITIONING` / `IMPROVED` / `MASTER`)** : **conservé en vanilla** (décision révisée le 23/11 : les 3 rangs `+1/+2/+3` aux sauvegardes restent intacts).

### 9. Contrat Mathématique (DPR nets & durées de boss cibles)

Avec upgrades cloisonnées (`Améliorations.csv`), armes d20 (`Armes.csv`), parité distance (`150 % DEX` en Duel 1M et `150 %/50 %` en `HC`) et RD des boss recalibrée (**`2/5/8`**) — vérifié sous `tools/dpr_check.py` le 19/11 :

| Phase (Boss étalon) | Duel (`1M`) | Ambidextrie (`2 armes`) | Arme Lourde (`2M`) | Haute Cadence (`HC`) |
| :--- | :---: | :---: | :---: | :---: |
| **EARLY** — Niv. 8 (120 PV, CA 20, **RD 2**) | 11–23 DPR (5–11 rds) | 9–18 DPR (7–14 rds) | 14–26 DPR (5–8 rds) | 17–30 DPR (4–7 rds) |
| **MID** — Niv. 16 (280 PV étalon DPR* ; rehaussé à `~380–420 PV` en Jalon 4, CA 29, **RD 5**) | 26–67 DPR (4–11 rds) | 23–65 DPR (4–12 rds) | 36–66 DPR (4–8 rds) | 36–81 DPR (3,5–8 rds) |
| **LATE** — Niv. 26 (650 PV, CA 44, **RD 8**) | 55–140 DPR (5–12 rds) | 49–150 DPR (4–13 rds) | 86–186 DPR (3,5–8 rds) | 61–170 DPR (4–11 rds) |

*(Survie Late vérifiée sur les 4 armures avec `Déluge de coups 3` + `Robustesse 3` : **Bure** `TTD/TTK = 1,51×` [8,0r / 5,3r], **Légère + Esq. Balistique** `1,51×` [14,3r / 9,5r], **Intermédiaire + Armure Tactique** `1,17×` sur 1 bouclier 100×3 [`1,55×` sur 2 boucliers], **Lourde + Juggernaut** `1,54×` [17,2r / 11,2r] et indestructible vs escouades.)*

### 10. Furtivité : l'attaque en embuscade est un critique confirmé

**Décision actée (13/11/2026)** :

- La **première attaque** portée depuis la furtivité est un **critique confirmé** (multiplicateur de l'arme, sans jet de confirmation). L'attaque brise la furtivité.
- Les dés d'**Attaque sournoise** s'appliquent par-dessus (comportement vanilla) ; les effets sur critique maison (Spé d'arme) se déclenchent.
- **Implémentation (validée en jeu le 23/11/2026)** : simulation scriptée dans `ov_inc_core.nss` ([`tools/build_scripts.py`](tools/build_scripts.py)) — tant que `IsStealthed(oPM)` est vrai, un buff moteur **`SupernaturalEffect(EffectAttackIncrease(50))`** de durée **`6,0 s`** est rafraîchi (garantit la touche sur la 1re attaque et expire automatiquement à `6,0 s` après sortie de furtivité sans race condition multi-PNJ). À l'impact dans `Ov_OnDamageHook` (`k_def_damage01` / `k_hen_damage01`), `Ov_ConsumeStealthAmbush(oAtk)` retire immédiatement ce buff (même sur one-shot) et déclenche `VFX_IMP_FORCE_PUSH` + `AssignCommand(oAtk, EffectDamage(GetTotalDamageDealt(), DAMAGE_TYPE_PIERCING))` (2e ligne de dégâts dans le journal de combat). Détails techniques dans [`README.md`](README.md) §3.D.

### 11. Conventions & principes transverses

1. **DD des effets sur coup (Spé d'arme)** : `DD = 10 + Niveau attaquant + mod. de la caractéristique directrice de l'arme` — **base 10 si le proc dépend de la plage de menace, base 5 s'il en est indépendant** (règle générale posée le 15/11).
2. **DD des consommables & effets *On-Hit* d'armes** (acté le 19/11 — contre l'autobalance `savemult 0,80–1,05`) :
   - **Grenades** (toutes, dont Poison via sauvegarde scriptée dans `k_sup_grenade.nss`) : **`10 + Niveau + Mod INT`** (cible : ≥ 40 % sur la Vigueur d'un élite `Set_3` à INT 14).
   - **Fléchettes & Roquettes spécialisées** : **`12 + Niveau + Mod INT`**.
   - **Effets *On-Hit* des armes** (anciens DD fixes `10 / 14 / 18 / 22`, migrés en script hook `1006`) : table graduée **`3 / 5 / 7 / 9 + Niveau + Mod Carac directrice de l'arme`** (`FOR`/`DEX` en mêlée, `DEX`/`INT` à distance — acté le 22/11, uniforme avec les Spé d'arme).
3. **Procs sur coup** : `chance = plage de menace de l'arme / 20 par coup` (évolue avec la posture Duel) ; ou sauvegarde par coup touché selon la famille.
4. **Ordre canonique des caractéristiques** : FOR, DEX, CON, INT, SAG, CHA — dans l'ordre des dons comme dans les descriptions.
5. **« Les synergies doivent être trouvées, pas décrites »** (14/11) : un don dont le texte doit citer les rangs d'un autre don est défectueux par construction ; les descriptions joueurs ne référencent jamais un autre don.
6. **CSV = couche utilisateur** (parcimonie obligatoire), `decisions_*.md` = couche agents (README §0).
7. **Notation des dégâts en dés d20** (acté le 21/11) : toutes les descriptions du mod (CSV colonnes mod + textes en jeu `dialog.tlk` pour armes, pouvoirs, dons et améliorations) utilisent systématiquement la notation en dés (`1d6`, `2d8`, etc.) à la place des plages vanilla (`1-6`, `2-16`).

---

## Partie 2 : TODOs & Chantiers Ouverts

1. **[TODO Tests moteur]** : ~~à tester en jeu.~~ **VÉRIFIÉ EN JEU (23/11 — `mods/04-engine-tests/`)** :
   - **T-excl (`exclusion` dans `feat.2da`)** : **KO** (ne bloque pas au level-up) → mutualité des 6 Spé Carac gérée par **garde-fou scripté** (premier arbre pris prioritaire).
   - **T1 (Gamorréen II)** : **OK & VALIDÉ EN JEU (25/11)** (`equipableslots=0x00030` + `weaponwield=2/4` + `weaponsize=3` → **69** jumeaux exacts `ov1m_*.uti` mêlée & distance, incluant les 3 armes 2M/HC de Péragus `heavymininglaser`, `advancedminingla`, `guidonbeacon`, chacun verrouillé par `reqfeat0` + `Use_Limitation_Feat = MOD_GAMORREAN_2` + **Adaptateur Gamorréen** `ov_gam_adapt.uti` / `ov_gam_conv.dlg` avec 2 actions « Ouvrir l'établi » et « Convertir l'arme équipée » ; n'interdit plus les postures Arme Lourde et Haute cadence).
   - **T2 (`reqfeat0` sur `baseitems.2da`)** : **OK** (bloque réellement l'équipement sans le don → réserve les 69 variantes 1M `ov1m_*.uti` aux porteurs de *Raffinement Gamorréen II*).
   - **RD exactes équipement/bêtes (`iprp_resistcost.2da`)** : **VALIDÉ (25/11)** — lignes `7..11` ajoutées (`2/-`, `3/-`, `4/-`, `6/-`, `12/-`) pour respecter exactement tous les plafonds CSV d'équipement (`Casques`, `Implants`, `Gants`, `Ceintures`, `Brassards`, `Armures items`) et les peaux de bêtes (`4/-`, `6/-`).
   - **T4 (cumul `EffectACIncrease`)** : **non cumulable entre effets séparés** (seul le max s'applique : `+5` au lieu de `+15`) → **sommer tous les bonus de CA custom en un seul `EffectACIncrease(nTotalAC)`** dans le heartbeat.
   - **T5 (`level` dans `itemcreate.2da`)** : **OK** (verrouille nativement les recettes à l'établi par niveau de personnage — valide toute la grille `Craft.csv`).
   - **Architecture scripts (`pykotor`)** : ne jamais recompiler le gros `k_ai_master.ncs` vanilla ; toujours passer par les **petits wrappers `k_def_*` / `k_hen_*`** (`~140–214` instructions) qui appellent ensuite le vrai `k_ai_master` vanilla. *(T3 détection fine des ratés Matukai à confirmer par VFX/log au Jalon 3.)*
2. **[TODO Budgets §6]** : ~~recomposer le socle de dons avec les nouveaux axes.~~ **ACTÉ (19/11) : budgets `22 / 18 / 15` dons (`12 / 16 / 24` pouvoirs) + gating Classe / Prestige / Compagnons.**
3. **[TODO Contrat §9]** : ~~remapper les colonnes DPR sur l'architecture postures × familles.~~ **ACTÉ (18–19/11) dans `dpr_check.py` / `dpr_data.json`.**
4. **[TODO Arbres d'armures §8.B]** : ~~revalider les 9 dons.~~ **ACTÉ (17–19/11) : *Juggernaut*, *Armure Tactique*, *Esquive Balistique* intégrés dans `Feats.csv`.**
5. **[TODO Servante]** : ~~remplacer son don d'histoire *Prémonition du combat*.~~ **ACTÉ (19/11) : *Prémonition du combat* remplacé par `+10 %` d'esquive en mêlée.**
6. **[TODO Équipement & Loot]** : ~~calibrage des armes & upgrades cloisonnées + refonte du Cristal personnel + stat *On-Hit*.~~ **ACTÉ (19–22/11)** dans `Armes.csv`, `Améliorations.csv`, `Armures.csv`, les 6 CSV d'équipement (`Casques`, `Implants`, `Gants`, `Ceintures`, `Brassards`, `Armures items` — plafond strict **`+1/+2`**, max **`+3`** légendaire sur une stat unique, couverture des **6 stats** sur les 5 slots majeurs, respect du lore ; suppression des 4 CSV redondants de dons mineurs), §3.A (Cristal personnel 3 paliers auto + Kreia + 2 effets classe de base/prestige) et §11.2 (*On-Hit* = `3/5/7/9 + Niv + Carac directrice de l'arme`). **Chantier Équipement clos.**
7. **[TODO Craft & Établi]** : ~~recalibrer les seuils de niveau + ajouter armes de base & 24 upgrades doubles.~~ **ACTÉ (19–24/11) dans `Craft.csv`** : toutes les armes de base non-laser craftables (hors Sabres Laser), 30 sur-couches exclusives renforcées pour armures intermédiaires + 30 sous-couches retravaillées, et verrou de niveau `itemcreate.2da` validé en jeu (T5) (**`Mk I = Niv. 1 / Mk II = Niv. 10 / Mk III = Niv. 15 / Mk IV-T5 = Niv. 20`**, `1 / 10 / 18` sur lignées 3 tiers). *(Nettoyage des anciens tags `[Combinée Interm.]` effectué.)*
8. **[TODO Ennemis]** : ~~trancher les décisions dans `equilibrage_ennemis.md`.~~ **ACTÉ (22/11)** dans [`equilibrage_ennemis.md`](equilibrage_ennemis.md) : **aucune phase de boss scriptée supplémentaire** (D4 — compat TSLRCM), **soins ennemis = statu quo vanilla** (D3 — Maîtres Jedi déjà sur *Guérison*, Sith sur *Drain de vie / Champ de mort*), échelle de résistances partielles `25/50/75 %` (100 % réservé aux droïdes), boucliers équipés sur ~1/3 élites soldats/droïdes (Mid+, lootables), **Sith/Jedi obscurs** (bures réelles + Rés. Force `15/20+Niv` + Vol `+2/+4/+6` + *Esquive Totale* 20+ + **Absorption de Force prioritaire si `PF < 30 %`**), **Soldats** (armures légères/intermédiaires réelles + boucliers), **Mandaloriens** (armures lourdes `6/8` + **résistance Laser/Énergie & Feu `25/35 %`** + stim `OnSpawn`), **Bêtes** (`RD 2/4/6/-` grosses bêtes + haute Vig + immunité *Peur* apex + régén hors combat), **Droïdes** (statu quo + déflecteurs ~1/3 élites), **Assassins** (furtivité + Réf élevés + esquive distance `20–25 %`), rehausse PV Boss Mid (`~380–420 PV` Niv. 16). **Chantier Ennemis clos.**
9. **[TODO Pouvoirs]** : ~~valider *Camouflage par la Force* et rééquilibrer les pouvoirs.~~ **ACTÉ (19–21/11) dans `Spé Pouvoirs.csv`** :
   - **Pouvoirs standards** : aucun cap de dés en L3, hiérarchie offensive par armure, Tempête `1d6/Niv` sans drain PF sur **Réflexes**, Mise à mort `1d8/Niv` sans 50 % PV max, Lancer de sabre `1d4/Niv` + Renversement Vig en L1 / ignore RD en L2, **Lenteur / Affliction / Peste** refondus en maladie contagieuse (`42 s` max, tick `6 s`, propagation `5 m` à la mort, ralenti + `½ Niv` dég/tick + `-3/-6/-9` caracs, jet de Vigueur chaque tick à DD `+0/+4/+8`), **Barrière & Résistance à l'énergie** alignés en **Armure intermédiaire** (`RD 4/8/12`, personnel, `60 s`, `15/25/35 PF`, sans effet groupe ni Poison), **Contrôle de la respiration** (`+4` saves vs Poison passif + actif immunité `240 s`), Talent `+2/+3/+4`, buffs des pouvoirs faibles ; **rééquilibrage DS/LS & sauvegardes (21/11)** : *Terreur/Horreur/Insanité* (Légère) refondu en DoT mental (`Niv` dég/rd) + `-4/-6/-8 Atq` sans perte d'action (`24 s` échec / `6 s` réussite Volonté), *Champ de stase* (Bure) jusqu'à `36 s` avec DD Vigueur dégressif `-3/rd`, *Vague de Force* (Intermédiaire) transformé en **Tourbillon AoE `6 m` / `12 s`** (`½` dégâts immédiats sur Réf réussie), *Absorption de vie / Champ de mort / Festin de mort* (`20/40/55 PF`) passé à `1d3/Niv` (soin = 100 % dégâts) avec **L3 *Festin de mort*** convertissant l'excédent en PV temporaires (`24 s`, non cumulable).
   - **Refonte complète des 6 Ultimes de Prestige (uniformisés L1/L2/L3 aux niv. 1/5/9 de prestige, philosophie Kreia) + 2 Ultimes d'alignement** :
     - **Maraudeur Sith — *Stigmate de Force I–III*** *(ex Fureur Sith, `Armure lourde`, 30 s)* : `+2/+4/+6` FOR & DEX, immunité Stase/Paralysie, **`+1 atq/rd` dès L1** (non cumulable *Vitesse*), coût `-5 %` PV max/round (arrêt auto ≤ `25 %` PV max).
     - **Maître d'armes Jedi — *Cicatrice de Force I–III*** (`Armure lourde`, 30 s, nouveau) : soin `+2/+4/+6 %` PV max/round + `+1/+2/+3` sauvegardes + immunité Peur/Étourdissement (L2) et Paralysie (L3).
     - **Assassin Sith — *Spectre de la Force I–III*** *(ex Camouflage par la Force, `Armure intermédiaire`, passif, exclusif Assassin)* : furtivité sans ceinture + course furtive, embuscade `+2d6`/Stun 1t, L3 kill → crit confirmé + `+25 %` esquive 2t.
     - **Jedi protecteur — *Affranchi de la Force I–III*** (`Armure lourde`, passif, nouveau) : `+1` tous les 8 rangs combinés sur 4 paires (`Informatique+Sécurité` → Atq, `Démolition+Réparation` → Dég, `Vigilance+Discrétion` → CA, `Persuasion+Premiers soins` → Saves ; plafond `+3/+5/+7`) + L2 `+25 %` efficacité consommables + L3 Résistance à la Force passive (`15 + Niv`).
     - **Seigneur Sith — *Déchirure de la Force I–III*** *(ex Annihilation de l'opposition, `Armure lourde`, 45 s)* : `-2/-4/-6` Atq, Sauvegardes et CA en zone 15 m (`Volonté` annule).
     - **Maître Jedi — *Écho des Liens I–III*** *(ex Inspiration des disciples, `Armure lourde`)* : L1 (30 s) partage buffs personnels avec l'allié le plus proche ; L2 (45 s) tout le groupe ; L3 (60 s) buffs personnels + soins partagés avec tout le groupe (sans restriction d'armure sur les alliés, comme Kreia).
     - **Alignement** : *Grâce du côté Lumineux* (`Armure intermédiaire`, lancer instantané 50 PF, *Vitesse* plafonnée à `+1 atq/rd` si armure portée) ; *Écrasement de Force* (`Armure légère`, `1d8/Niv` dégâts purs sans cap + immo 6 s, Vig ½ et annule).
   - **Coûts en PF évolutifs par rang (`Spé Pouvoirs.csv`, acté le 21/11)** : grille complète `L1 / L2 / L3` calibrée sur les réserves réelles Niv. 25 (`Gardien ~200 / Sentinelle ~300 / Consulaire ~500 PF`) — L1 `10–20 PF`, L2 `20–35 PF`, L3 `35–65 PF` (ex. *Tempête* `15/30/50`, *Champ de stase* `15/30/50`, *Insanité* `15/25/45`, *Soins* `20/35/50`, *Grâce* `50`, *Écrasement* `60`), réglant aussi la pénalité d'alignement opposé (`~85–90 PF` en Lumineux pour *Tempête L3*).
   - **Pouvoirs de débuff & sauvegardes (clos le 21/11)** : *Méditation de combat* indexée sur `mod. CHA` non plafonné (L1 groupe, L2 ajoute malus ennemis 10 m Vol annule, L3 `+2` et 15 m), *Subterfuge / Confusion* conservés en vanilla, *Déchirure* conservée en Volonté annule, *Cri de Force* confirmé sur **Volonté** (plus rare que Vigueur : 5 vs 8 lignées ; `½` dégâts et annule le malus), *Blessure L1* harmonisée sur Vigueur `½` dégâts.
10. **[Utilitaire externe — Cahier des charges acté (24/11)]** : **Convertisseur de sauvegarde (D20-Overhaul ↔ Vanilla) + Assistant de Respec autonome (`.exe`)** — cahier des charges complet dans [`specs_utilitaire_respec.md`](specs_utilitaire_respec.md) (sélection sauvegarde, détection auto Overhaul/Vanilla, respec complet stats/classe/leveling avec pré-sélection des choix existants et bouton *Multiclassage* libre).
11. **[Respec in-game — Clos / Limitation moteur (24/11)]** : un respec en jeu (dialogue T3-M4 / script NWScript / console) est **techniquement impossible** dans l'Odyssey Engine (aucune API `RemoveFeat`, `RemoveSpell`, baisse de niveau ou reset de compétences/caractéristiques, cf. [`README.md`](README.md) §3.D). Remplacé par l'utilitaire externe ci-dessus ([`specs_utilitaire_respec.md`](specs_utilitaire_respec.md)).
