# Décisions Finales d'Équilibrage — Synthèse (*KotOR 2 Overhaul*)

Ce document est le **contrat de game design** : chaque décision actée y figure sous forme condensée.
Les justifications, la recherche (JdR papier, D&D, consensus communauté) et les notes d'implémentation sont dans **[`decisions_annexes.md`](decisions_annexes.md)**.

> **Hiérarchie des sources (README §0)** : les CSV `Kotor 2 - rééquilibrage - *.csv` sont la référence opérationnelle côté utilisateur — ce contrat en est la **consolidation**. En cas de divergence, les CSV font foi ; ce document doit alors être resynchronisé.
> **Dernière grosse consolidation : 18/11/2026** (scaling DEX `100 % / 50 %` à distance 1M/D, hiérarchie des slots d'upgrades par famille d'arme, slot unique sur armures légères/lourdes ; arbres d'armures le 17/11 ; refonte postures/spé d'arme/spé carac le 15/11/2026). Journal des arbitrages : annexes §9.

| Domaine | Décision (résumé) | Détail |
| :--- | :--- | :---: |
| Progression des classes | Symétrie inverse Combattants ↔ Mages (dons ↔ pouvoirs) | §1 |
| Pouvoirs de la Force | Aucun ajout ; nerf du haut du panier, buff des alternatives, restauration via Métamagie | §2 |
| Établi & Boss | Plafonds d'amélioration `+2/+5/+10`, RD des boss `3/7/12`, combats de 5–10 rounds | §3 |
| Postures & spécialisations d'armes | 4 postures (Duel, Ambidextrie, Arme Lourde, Arme haute cadence) × 8 familles (4 mêlée + 4 tir) ; dons vanilla Duel/TWF/Finesse/Focus/Spec **supprimés** | §4 |
| Spécialisations de caractéristique | 6 arbres exclusifs (FOR, DEX, CON, INT, SAG, CHA) — un par caractéristique, ordre canonique | §5 |
| Architecture de dons | Posture (3) + famille (3) + spé carac (3) + défenses ; budgets 21/16/13 (socle à réarbitrer) | §6 |
| Dons transversaux | 7 dons de Métamagie + *Esquive Totale* (anti-AoE) | §7 |
| Armures & Défenses | RD native (Interm. 2 / Lourde 4), upgrades combinées exclusives aux intermédiaires (`UpgradeLevel`), 3 arbres de dons par type, dégradé de pouvoirs, *Condition physique III* supprimé | §8 |
| Contrat mathématique | DPR nets et durées de boss cibles par phase de jeu (colonnes à remapper sur la nouvelle architecture) | §9 |
| Furtivité | Embuscade : première attaque depuis la furtivité = critique confirmé (simulation scriptée) | §10 |
| Conventions & principes | DD Spé d'arme (`10`/`5` + Niv + carac), grenades (`10` + Niv + INT), fléchettes/roquettes (`12` + Niv + INT), *On-Hit* armes (`3/5/7/9` + Niv + carac à définir), procs `plage/20`, ordre canonique, « les synergies se trouvent » | §11 |

---

## Partie 1 : Décisions Actées

### 1. Progression des Classes (`spellgain.2da` & `featgain.2da`)

Symétrie inverse stricte entre Combattants et Mages :

| Famille de Classes | Gain de Pouvoirs | Total Pouvoirs (Niv. 30) | Gain de Dons | Total Dons (Niv. 30) | Identité |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Gardien / Maître d'Armes / Maraudeur Sith** | `1/3` niveaux | ~12 | `2/3` niveaux + 1 don Niv. 1 | **21** | Maître Martial |
| **Sentinelle / Veilleur / Assassin Sith** | `1/2` niveaux | ~16 | `1/2` niveaux + 1 don Niv. 1 | **16** | Hybride Tactique |
| **Consulaire / Maître Jedi / Seigneur Sith** | `1/1` niveau | ~31 | `1/2,5` niveaux + 1 don Niv. 1 | **13** | Archimage |

### 2. Philosophie des Pouvoirs de la Force

1. **Aucun nouveau pouvoir** : rééquilibrage à 100 % dans `k_inc_force.nss` et `spells.csv`.
2. **Hiérarchie :** *Éclair/Tempête* (zone) et *Blessure/Étranglement/Mise à mort* (monocible) restent les meilleurs DPS de Force — **nerfés à la base**, restaurables via **Métamagie**. Les alternatives sont boostées sans jamais dépasser ce plafond.
3. **Alignement :** *Champ de Stase* reste un pouvoir du Côté Lumineux.

### 3. Établi & Boss (Rythme des Combats)

**A. Plafond des améliorations d'armes** (pièces `u_r_*`, `u_m_*`, `u_l_*` retravaillées — inventaire de référence : CSV *WIP Améliorations*, 226 pièces) :
- Early (Niv. 1–10, Mk I) : max **`+2` dégâts moyens/coup** • Mid (Niv. 11–18, Mk II) : max **`+5`** • Late (Niv. 19+, Mk III) : max **`+10`** *(valeurs max pour une arme disposant de tous ses emplacements d'amélioration).*
- **Slots autorisés par famille d'arme** (*WIP armes.csv*, via hiérarchie `UpgradeLevel`) :
  - **Mêlée (`Poignée < Lame < Cellule`)** : *Mains nues* (0 slot) · *Impact* (1 : Poignée) · *Traditionnelle* (2 : Poignée, Lame) · *Résonance* (3 : Poignée, Lame, Cellule) · *Laser* (Cristal de couleur + Cristal d'amélioration + Émetteur + Lentille + Cellule). *Bâton Gaffi* retiré du jeu (héritage KotOR 1).
  - **Distance (`Viseur < Cellule < Chambrage`)** : *Tir Tactique* (1 : Viseur) · *Tir Assassin* (2 : Viseur, Cellule) · *Tir d'Assaut & Tir Pénétrant* (3 : Viseur, Cellule, Chambrage).
- **Principe de compensation** : l'absence de `Cellule` / `Chambrage` sur les familles à 1 ou 2 slots plafonne leurs upgrades plus bas à l'établi, en échange de **dégâts de base plus élevés, d'une plage de critique élargie ou d'un multiplicateur de critique supérieur**.

**B. Boss** :
- **Règle d'or :** aucun boss tué en moins de 4 rounds ; cible **5–10 rounds** (10–15 pour Sion/Traya).
- **RD passive** des Sous-Boss/Boss (`Set_4`/`Set_5`) : `RD 3` (Early) / `RD 7` (Mid) / `RD 12` (Late).
- **`damagemult` des boss réduit** (`autobalance.2da`) pour que le joueur tienne aussi 5–10 rounds.

### 4. Postures & Spécialisations d'armes (refonte 13–15/11)

**Dons vanilla supprimés** (remplacés par les dons custom ci-dessous, cf. *WIP Feats.csv*) :
`DUELING` I-III, `TWO_WEAPON_FIGHTING` I-III, `FINESSE_MELEE_WEAPONS`, `FINESSE_LIGHTSABERS`, `WEAPON_FOCUS/SPEC` (pistolets, fusils, mêlée, sabres).

**A. Les 4 postures** (*Style de combat.csv* — chacune 3 rangs, recréés **from scratch**) :

| Posture | Base moddée | Rang I → III | Notes |
| :--- | :--- | :--- | :--- |
| **Duel** | Dégâts mêlée `150 % FOR` (règle moteur 1M, main gauche vide) ; **distance 1M `100 % DEX`** | `+2/+4/+6 Atq` et **plage de critique +1/+2/+3** | Prérequis : arme à une main **ou mains nues** ; la plage élargie augmente la fréquence des procs des Spé d'arme (proc = plage/20 par coup) |
| **Ambidextrie** | Dégâts `100 % / 50 % FOR` (mêlée) ou **`100 % / 50 % DEX` (distance)** ; malus 2 armes `-6/-10` (`+2/0` si arme équilibrée en main gauche) | `-6/-6 & +1 CA` → `-4/-4 & +2 CA` → `-2/-2 & +3 CA` | Identité parade/CA ; malus de main gauche remonte mais l'attaque s'achète de la Défense |
| **Arme Lourde (2M)** | Mêlée `200 % FOR` / distance `150 % DEX` | `+1/+2/+3 Atq` ; mêlée **250→300 % FOR** ; distance **200→250 % DEX** | Prérequis : arme à deux mains non double — mêlée **et** distance |
| **Arme haute cadence** (ex « Arme Double & Repeating ») | Dégâts `150 % / 50 % FOR` (arme double mêlée) ou **`100 % / 50 % DEX` (répétition distance)**, malus moddé **`-5 CA`** (au lieu de `-6/-10 Atq`) | `+1/+1` & CA `-3` → `+2/+2` & `-2` → `+3/+3` & `-1` | Repeating et lourds à répétition partagent cette posture ; moteur : les repeating **ne sont pas** des armes doubles (`weaponwield 6 ≠ 3`) |

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
| **Chasseur de prime Gand** (INT) | +1 INT ; attaque distance : DEX/INT (si INT > DEX) | +2 INT ; dégâts distance : DEX/INT | +3 INT ; **grenades ×2** |
| **Maîtrise Matukai** (SAG) | +1 SAG ; **ajoute** le mod. de SAG à l'attaque (par-dessus la carac directrice) | +2 SAG ; sauvegardes + ½ SAG ; **réussir une sauvegarde inflige SAG dégâts à l'attaquant** | +3 SAG ; **SAG remplace DEX pour la CA** ; tout ennemi vous ratant subit SAG dégâts par attaque échouée |
| **Héritage de Nomi** (CHA) | +1 CHA ; compagnons 100 % de l'XP | +2 CHA ; groupe : sauvegardes + mod. CHA | +3 CHA ; **Défense + mod. CHA** (cumulable avec Précognition guerrière) |

Notes d'équilibrage : la transfusion Kraith échange invariablement **25 % PV ↔ 25 % PF** (rituel complet) ; les dégâts de punition Matukai contournent la RD (scriptés) et ne peuvent pas critiquer ; le cumul Nomi/Matukai + Précognition suppose des types de bonus distincts (plafond moteur à vérifier).

### 6. Architecture de Dons & Budgets

**Nouvelle structure (post-15/11)** : chaque personnage combine **une posture** (3 rangs) + **une famille de Spé d'arme par catégorie d'armes utilisées** (3 rangs chacune) + **un arbre de Spé carac** (3 rangs, exclusif) + **défenses** (Robustesse 3, Condition physique 2 ou arbre d'armure 3) + **Métamagie** (7, profil caster) + dons actifs vanilla conservés (Déluge, Attaque en puissance, Coup critique, Décharge, Tir rapide, Sniper).

**Budgets Niv. 30 (maintenus)** : 21 (Gardien) / 16 (Sentinelle) / 13 (Consulaire).
**[À réarbitrer]** : la composition du socle 15 dons (ancienne structure 3+3+3+6) doit être revécue avec les nouveaux axes (la Spé carac s'ajoute sans remplacer) — les dons supprimés (Duel/TWF/Finesse/Focus/Spec vanilla) libèrent par ailleurs des emplacements.

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

**B. Trois arbres de dons** (3 dons chacun, arbitrage du 17/11 — source : *WIP spé Armure.csv*) :

| Arbre | Rang I | Rang II | Rang III | Identité |
| :--- | :--- | :--- | :--- | :--- |
| **Juggernaut** (lourde) | RD 3/-, immunité tous dégâts 10 % | RD 4/-, immunité 20 % | RD 5/-, immunité 30 % | Encaisser les dégâts |
| **Blindage de Combat** (intermédiaire) | RD 3/-, +1 CA, durée des boucliers +100 %, furtivité sans ceinture (armure moyenne portée) | RD 4/-, +2 CA, efficacité boucliers ×2, accès à Course furtive (armure moyenne portée) | RD 5/-, +3 CA, efficacité boucliers ×3 | Spé ingénieur et craft — boucliers & furtivité |
| **Seconde Peau** (légère) | Esquive +10 %, +1 CA base | Esquive +20 %, +2 CA base | Esquive +30 %, +3 CA base | Esquiver toutes les attaques *(pas d'augmentation de la CA gagnée via caractéristiques)* |

**RD cumulée max** (Juggernaut III + native lourde 4 + Robustesse II 2) : **RD 11 + 30 % d'immunité** (≈ −53 % sur un coup de 23, ≈ −40 % sur un coup de 68). Cap d'immunité tous dégâts à définir avec les pièces typées (proposition : 40-50 % global).

**C. Dégradé des pouvoirs sous armure** (`forbiditemmask`) : robe = tous ; légère = vanilla + Vaillance I + Résistance ; interm. = vanilla + Résistance ; lourde = vanilla strict.

**D. *Condition physique III* (`MASTER_CONDITIONING`)** : **supprimé** (décision 17/11). Seuls les rangs I (+1) et II (+2) sont conservés en vanilla ; le rang III est supprimé.

### 9. Contrat Mathématique (DPR nets & durées de boss cibles)

Avec établi plafonné (`+2/+5/+10` pondéré par slots de famille), scaling distance `100 % / 50 % DEX` et RD des boss (`3/7/12`) — remappage postures × familles vérifié sous `tools/dpr_check.py` (rangs de dons I/II/III par phase) :

| Phase (Boss étalon) | Duel (`1M`) | Ambidextrie (`2 armes`) | Arme Lourde (`2M`) | Haute Cadence (`D`) |
| :--- | :---: | :---: | :---: | :---: |
| **EARLY** — Niv. 8 (120 PV, CA 20, RD 3) | 14–24 DPR (5–9 rds) | 13–17 DPR (7–9 rds) | 18–24 DPR (5–7 rds) | 23–30 DPR (4–5 rds) |
| **MID** — Niv. 16 (280 PV, CA 29, RD 7) | 30–62 DPR (4–9 rds) | 31–46 DPR (6–9 rds) | 49–65 DPR (4–6 rds) | 45–64 DPR (4–6 rds) |
| **LATE** — Niv. 26 (650 PV, CA 44, RD 12) | 61–128 DPR (5–11 rds) | 74–132 DPR (5–9 rds) | 116–161 DPR (4–6 rds) | 104–154 DPR (4–6 rds) |

*(Note : en `Tactique` 1M, le DPR pur plus bas `61–82` est compensé par les procs de Stun 1–2 tours sur `plage/20`. Côté survie, la cible TTD `5–10+ rounds` est vérifiée de Légère à Lourde, la Bure restant fragile en solo pur à `~4 rounds` sans Nomi/Matukai/contrôle.)*

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

---

## Partie 2 : TODOs & Chantiers Ouverts

1. **[TODO Tests moteur]** (tracés dans la colonne *Détail technique* du WIP Feats.csv) : **T-exclusion** (colonne `exclusion` de feat.2da, mutualité des 6 arbres carac), **T1** (arme double en main gauche — Colosse), **T2** (`reqfeat0` sur baseitem d'arme), **T3** (détection des ratés — événement 1005), **plafond CA** (cumul Nomi/Matukai + Précognition), **grenades** (scripts moddables — Gand III).
2. **[TODO Budgets §6]** : recomposer le socle de dons avec les nouveaux axes (posture/famille/carac) suite aux suppressions vanilla.
3. **[TODO Contrat §9]** : ~~remapper les colonnes DPR sur l'architecture postures × familles.~~ **ACTÉ (18/11) dans `dpr_check.py` / `dpr_data.json` (remappage à répercuter si besoin dans `k2balance.py`).**
4. **[TODO Arbres d'armures §8.B]** : ~~cellules en TODO dans le WIP Feats.csv — revalider les 9 dons.~~ **ACTÉ (17/11) : 9 dons d'armure intégrés dans WIP Feats.csv.**
5. **[TODO Servante]** : seul son don « CA via la Sagesse » reste concerné par un éventuel remplacement (les `ECHANI_STRIKE` sont confirmés inchangés).
6. **[TODO Équipement & Loot]** : revoir statistiques et distribution (viabilité des familles d'armes Niv. 1 à 30) — référence : *WIP armes.csv* et *WIP Améliorations.csv*.
7. **[TODO Craft & Établi]** : refonte totale de toutes les améliorations d'équipement (recettes viables par famille, cohérentes avec les plafonds §3 ; types d'améliorations par famille : Lame+Garde primitives / +Cellule vibrantes / cristaux lasers ; création des sur-couches et sous-couches combinées exclusives aux armures intermédiaires via `UpgradeLevel`).
8. **[TODO Amélioration de la Furtivité]** : ~~une attaque furtive est-elle un critique ?~~ **ACTÉ (13/11) → §10.**
