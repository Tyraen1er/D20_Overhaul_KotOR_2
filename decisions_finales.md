# Décisions Finales d'Équilibrage — Synthèse (*KotOR 2 Overhaul*)

Ce document est le **contrat de game design** : chaque décision actée y figure sous forme condensée.
Les justifications, la recherche (JdR papier, D&D, consensus communauté) et les notes d'implémentation sont dans **[`decisions_annexes.md`](decisions_annexes.md)**.

> **Hiérarchie des sources (README §0)** : les CSV `Kotor 2 - rééquilibrage - *.csv` sont la référence opérationnelle côté utilisateur — ce contrat en est la **consolidation**. En cas de divergence, les CSV font foi ; ce document doit alors être resynchronisé.
> **Dernière grosse consolidation : 15/11/2026** (refonte postures/spé d'arme/spé carac). Journal des arbitrages : annexes §9.

| Domaine | Décision (résumé) | Détail |
| :--- | :--- | :---: |
| Progression des classes | Symétrie inverse Combattants ↔ Mages (dons ↔ pouvoirs) | §1 |
| Pouvoirs de la Force | Aucun ajout ; nerf du haut du panier, buff des alternatives, restauration via Métamagie | §2 |
| Établi & Boss | Plafonds d'amélioration `+2/+5/+10`, RD des boss `3/7/12`, combats de 5–10 rounds | §3 |
| Postures & spécialisations d'armes | 4 postures (Duel, Ambidextrie, Arme Lourde, Arme haute cadence) × 8 familles (4 mêlée + 4 tir) ; dons vanilla Duel/TWF/Finesse/Focus/Spec **supprimés** | §4 |
| Spécialisations de caractéristique | 6 arbres exclusifs (FOR, DEX, CON, INT, SAG, CHA) — un par caractéristique, ordre canonique | §5 |
| Architecture de dons | Posture (3) + famille (3) + spé carac (3) + défenses ; budgets 21/16/13 (socle à réarbitrer) | §6 |
| Dons transversaux | 7 dons de Métamagie + *Esquive Totale* (anti-AoE) | §7 |
| Armures | RD native (Interm. 2 / Lourde 4), 3 arbres de dons par type, dégradé de pouvoirs, *Condition physique* révisé | §8 |
| Contrat mathématique | DPR nets et durées de boss cibles par phase de jeu (colonnes à remapper sur la nouvelle architecture) | §9 |
| Furtivité | Embuscade : première attaque depuis la furtivité = critique confirmé (simulation scriptée) | §10 |
| Conventions & principes | DD (`10+Niv+carac directrice` ; base 10 si proc lié à la plage, 5 sinon), procs `plage/20`, ordre canonique des caracs, « les synergies se trouvent, ne se décrivent pas » | §11 |

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
- Early (Niv. 1–10, Mk I) : max **`+2` dégâts moyens/coup** • Mid (Niv. 11–18, Mk II) : max **`+5`** • Late (Niv. 19+, Mk III) : max **`+10`**

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
| **Duel** | Dégâts mêlée 150 % FOR (règle moteur 1M, main gauche vide) | `+2/+4/+6 Atq` et **plage de critique +1/+2/+3** | Prérequis : arme à une main **ou mains nues** ; la plage élargie augmente la fréquence des procs des Spé d'arme (proc = plage/20 par coup) |
| **Ambidextrie** | Malus 2 armes `-6/-10` (`+2/0` si arme équilibrée en main gauche) | `-6/-6 & +1 CA` → `-4/-4 & +2 CA` → `-2/-2 & +3 CA` | Identité parade/CA ; malus de main gauche remonte mais l'attaque s'achète de la Défense |
| **Arme Lourde (2M)** | Mêlée 200 % FOR / distance 150 % DEX | `+1/+2/+3 Atq` ; mêlée **250→300 % FOR** ; distance **200→250 % DEX** | Prérequis : arme à deux mains non double — mêlée **et** distance |
| **Arme haute cadence** (ex « Arme Double & Repeating ») | Dégâts 150 %/50 % FOR (droite/gauche), malus moddé **`-5 CA`** (au lieu de `-6/-10 Atq`) | `+1/+1` & CA `-3` → `+2/+2` & `-2` → `+3/+3` & `-1` | Repeating et lourds à répétition partagent cette posture ; moteur : les repeating **ne sont pas** des armes doubles (`weaponwield 6 ≠ 3`) |

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

**D. L'axe distance/mêlée** : parité de viabilité, asymétrie de coûts — chaque posture/famille distance atteint les cibles DPR du §9 par son propre chemin (DEX % via Arme Lourde, utilitaires via les familles de tir) ; la mêlée paie en défense et approche, la distance paie en contreurs (boucliers d'énergie, déflexion). Équilibrage fin par le chantier ennemis.

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

**Nouvelle structure (post-15/11)** : chaque personnage combine **une posture** (3 rangs) + **une famille de Spé d'arme par catégorie d'armes utilisées** (3 rangs chacune) + **un arbre de Spé carac** (3 rangs, exclusif) + **défenses** (Robustesse 3, Condition physique 3 ou arbre d'armure 3) + **Métamagie** (7, profil caster) + dons actifs vanilla conservés (Déluge, Attaque en puissance, Coup critique, Décharge, Tir rapide, Sniper).

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

### 8. Armures : RD Native, 3 Arbres de Dons, Dégradé de Pouvoirs, *Condition physique* révisé

Décisions actées (08/11/2026) — justifications dans [`decisions_annexes.md`](decisions_annexes.md#1-armures--recherche-et-justifications) :

**A. RD native des armures (passive, sans don)** — CA et plafonds DEX vanilla inchangés *sauf Techniques Echanis III (§5)* :

| Type | CA base | Plafond DEX | **RD Physique & Énergie native** |
| :--- | :---: | :---: | :---: |
| Légère | 4–5 | +4/+5 | **0** |
| Intermédiaire | 6–7 | +2/+3 | **RD 2** |
| Lourde | 8–9 | +0/+1 | **RD 4** |

**B. Trois arbres de dons** (3 dons chacun) : *Seconde Peau* (légère : CA + Réflexes), *Blindage de Combat* (interm. : RD + Vigueur), *Juggernaut* (lourde : RD + immunisés) — détail §8.B d'origine ; *les cellules du WIP Feats.csv sont en TODO en attente de revalidation*. RD cumulée max : **RD 13**.

**C. Dégradé des pouvoirs sous armure** (`forbiditemmask`) : robe = tous ; légère = vanilla + Vaillance I + Résistance ; interm. = vanilla + Résistance ; lourde = vanilla strict.

**D. *Condition physique* révisé** : rang III `+3` toutes sauvegardes **+2 contre les pouvoirs de Force**.

### 9. Contrat Mathématique (DPR nets & durées de boss cibles)

Avec établi plafonné (`+2/+5/+10`) et RD des boss (`3/7/12`) :

| Phase (Boss étalon) | Gatling / Lame Double | 2 Pistolets / 2 Armes | Fusil / Duel 1M |
| :--- | :--- | :--- | :--- |
| **EARLY** — Niv. 8 (120 PV, CA 20, RD 3) | 16,5 DPR — 7,2 rounds | 11,7 DPR — 6–10 rounds | 19,5 DPR — 6,1 rounds |
| **MID** — Niv. 16 (280 PV, CA 29, RD 7) | 39,0 DPR — 7,2 rounds | 25,2 DPR — 6–11 rounds | 58,6 DPR — 4,8 rounds |
| **LATE** — Niv. 26 (650 PV, CA 44, RD 12) | 57,6 DPR — 11,2 rounds | 45,5 DPR — 7–14 rounds | 122–128 DPR — 5,1 rounds |

**[À remapper]** : les colonnes « triangle Pistolet/Fusil/Gatling » (§4 d'origine, abrogé le 15/11) doivent être réexprimées en **postures × familles** lors du chantier équilibrage (`tools/k2balance.py`) ; les cibles de DPR/TTK restent la référence.

### 10. Furtivité : l'attaque en embuscade est un critique confirmé

**Décision actée (13/11/2026)** :

- La **première attaque** portée depuis la furtivité est un **critique confirmé** (multiplicateur de l'arme, sans jet de confirmation). L'attaque brise la furtivité.
- Les dés d'**Attaque sournoise** s'appliquent par-dessus (comportement vanilla) ; les effets sur critique maison (Spé d'arme) se déclenchent.
- **Implémentation** : simulation scriptée (le pipeline d'attaque est fermé) — drapeau « embuscade armée » posé par heartbeat tant que `IsStealthed()`, consommé par le hook 1006 de la victime, dégâts `GetTotalDamageDealt() × (multiplicateur − 1)`. Limites documentées en annexes §5.

### 11. Conventions & principes transverses

1. **DD des effets sur coup** : `DD = 10 + Niveau attaquant + mod. de la caractéristique directrice de l'arme` — **base 10 si le proc dépend de la plage de menace, base 5 s'il en est indépendant** (règle générale posée le 15/11).
2. **Procs sur coup** : `chance = plage de menace de l'arme / 20 par coup` (évolue avec la posture Duel) ; ou sauvegarde par coup touché selon la famille.
3. **Ordre canonique des caractéristiques** : FOR, DEX, CON, INT, SAG, CHA — dans l'ordre des dons comme dans les descriptions.
4. **« Les synergies doivent être trouvées, pas décrites »** (14/11) : un don dont le texte doit citer les rangs d'un autre don est défectueux par construction ; les descriptions joueurs ne référencent jamais un autre don.
5. **CSV = couche utilisateur** (parcimonie obligatoire), `decisions_*.md` = couche agents (README §0).

---

## Partie 2 : TODOs & Chantiers Ouverts

1. **[TODO Tests moteur]** (tracés dans la colonne *Détail technique* du WIP Feats.csv) : **T-exclusion** (colonne `exclusion` de feat.2da, mutualité des 6 arbres carac), **T1** (arme double en main gauche — Colosse), **T2** (`reqfeat0` sur baseitem d'arme), **T3** (détection des ratés — événement 1005), **plafond CA** (cumul Nomi/Matukai + Précognition), **grenades** (scripts moddables — Gand III).
2. **[TODO Budgets §6]** : recomposer le socle de dons avec les nouveaux axes (posture/famille/carac) suite aux suppressions vanilla.
3. **[TODO Contrat §9]** : remapper les colonnes DPR sur l'architecture postures × familles dans `k2balance.py`.
4. **[TODO Arbres d'armures §8.B]** : cellules en TODO dans le WIP Feats.csv — revalider les 9 dons.
5. **[TODO Servante]** : seul son don « CA via la Sagesse » reste concerné par un éventuel remplacement (les `ECHANI_STRIKE` sont confirmés inchangés).
6. **[TODO Équipement & Loot]** : revoir statistiques et distribution (viabilité des familles d'armes Niv. 1 à 30) — référence : *WIP armes.csv* et *WIP Améliorations.csv*.
7. **[TODO Craft & Établi]** : recettes viables par famille, cohérentes avec les plafonds §3 ; types d'améliorations par famille (TODO historique : Lame+Garde primitives / +Cellule vibrantes / cristaux lasers).
8. **[TODO Amélioration de la Furtivité]** : ~~une attaque furtive est-elle un critique ?~~ **ACTÉ (13/11) → §10.**
