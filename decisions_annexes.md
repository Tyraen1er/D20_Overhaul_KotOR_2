# Annexes des Décisions — Justifications, Recherche & Notes d'Implémentation

> Compagnon de [`decisions_finales.md`](decisions_finales.md) (le contrat de game design).
> Tout ce qui **explique ou prépare** les décisions sans en faire partie y est rassemblé :
> recherche sur les systèmes papier, diagnostics, mécanismes moteur vérifiés, options techniques validées, journal des arbitrages.

---

## 1. Armures — Recherche et Justifications (décisions §8)

### A. Comparaison des systèmes papier (pourquoi « RD native + arbres par type »)

| Système | Légère | Intermédiaire | Lourde | Levier de différenciation |
| :--- | :--- | :--- | :--- | :--- |
| **D&D 3.5** | CA `+1` à `+4`, DEX pleine, malus `0` à `-2` | CA `+4/+5`, DEX max `+3`, malus `-4/-6` | CA `+6` à `+8`, DEX max `+0/+1`, malus `-6/-8` | La **CA** contre DEX/vitesse/compétences ; 3 dons de *Proficiency* |
| **D&D 5e** | DEX entière | DEX max `+2` ; don *Medium Armor Master* | ***Heavy Armor Master* = RD 3 physique** | **Dons de spécialisation par type d'armure** |
| **SW d20 RCR** *(source de KotOR)* | **RD 2–3**, DEX max `+4/+5` | **RD 4–5**, DEX max `+3` | **RD 7–9**, DEX max `+1` | **L'armure donne de la RD, pas de la Défense** ; les sabres ignorent la RD des armures |
| **SW Saga (SWSE)** | Remplace le niveau dans la Défense Réflexe | Talents *Armored Defense* | *Juggernaut*, *Armor Mastery* | Talents d'arbre *Armor Specialist* |
| **KotOR 2 Vanilla** | CA `4-5`, DEX max `+5/+4` | CA `6-7`, DEX max `+3/+2` | CA `8-9`, DEX max `+1/+0` | Aucune identité : blocage uniforme des pouvoirs → Tier F Jedi |

**Conclusion design :** KotOR 2 a hérité de la CA de D&D 3.0 *sans* les dons de spécialisation de D&D 5e *ni* la RD du JdR SW. **D20 Overhaul** restaure les deux leviers.

### B. Diagnostic de *Condition physique* (consensus communauté)

*Filler feat* typique en vanilla ; le rang III (*Condition physique III* / `MASTER_CONDITIONING`) avait d'abord été envisagé avec un bonus contre la Force, puis supprimé (17/11), et finalement **rétabli en vanilla** (décision 23/11, §8.D : les 3 rangs `+1/+2/+3` sont conservés tels quels).

### C. Notes d'implémentation (§8)

- **RD native & arbres** : wrappers heartbeat (`k_def_heartbt01` / `k_hen_heartbt01`, sans jamais recompiler `k_ai_master.ncs`) lisant `GetBaseItemType()` de l'armure (lignes baseitems 38–43, 98, 102), parcours anti-cumul d'effets (README §3.A).
- **Effets validés par arbre d'armure** (`nwscript.nss`) :
  - **Lourde (*Juggernaut*)** : `EffectDamageReduction` (RD 4 native + `3/4/5` du don) + `EffectDamageImmunityIncrease(nDamageType, 10/20/30)` sur les types de dégâts (pas de cap global d'immunité).
  - **Intermédiaire (*Armure Tactique*, ex *Blindage de Combat*)** :
    - *Furtivité sans ceinture (Rang I, armure intermédiaire portée)* : octroi conditionnel via `GrantFeat` / `PERSONAL_CLOAKING_SHIELD` (`feat.2da` ligne `201`, seul don de camouflage actif sous armure, contrairement aux rangs II/III de `XXXFORCE_CAMOFLAGE` `97/141/142`) ; *Course furtive* au Rang II via `STEALTH_RUN` (ligne `197`).
    - *Boucliers (`+100 %` durée au Rang I, efficacité `×2 / ×3` aux Rangs II–III)* : tous les boucliers d'avant-bras passent par `k_sup_bands.nss` → `EffectForceShield(nShield)` indexé sur `forceshields.2da`. Rang I double `fDuration` (`200.0 + 2.0 * nRepairSkill`) ; Rangs II et III sélectionnent des lignes dupliquées dans `forceshields.2da` avec `amount × 2` et `amount × 3`.
  - **Légère (*Esquive Balistique*, ex *Seconde Peau*)** : `EffectMissChance(10/20/30)` (signature K2 à 1 paramètre `int nPercentage`, `nwscript.nss` l. 4324) + `EffectACIncrease(1/2/3)` (sommé dans `nTotalAC`, aucune hausse du plafond de DEX).
- **Établi dans `swkotor2.exe` — limite des slots & contournement par `UpgradeLevel` (vérifiés le 17–24/11)** :
  - Contrairement aux `.uti` ou à `baseitems.2da`, le nombre de slots d'établi est codé en dur par onglet (`0x4ca630` + table `4 × 6` à `0x5a70e8`) : Sabres = 6 slots (`BTN_UPGRADE31..36_LS` dans `upgrade_p.gui`, dont Slots 0 et 2 sur `upgradetype 0`), Distance/Mêlée = 3 slots, Armures = **2 slots maximum** (`Slot 0 = upgradetype 10` *Sur-couche*, `Slot 1 = upgradetype 11` *Sous-couche* ; le 3e bouton `BTN_UPGRADE33` est explicitement masqué à `0x4cb070`). Impossible donc d'équiper 2 sur-couches + 2 sous-couches séparées sans patch binaire.
  - **Gating natif via `UpgradeLevel` (`0x4cbcd0`)** : pour chaque slot, le moteur vérifie `upgrade.UpgradeLevel <= item.UpgradeLevel`.
    - **Armures (acté le 24/11)** : Bures = `ulvl 0` (0 slot) ; **Légères = `ulvl 1`** (**1 slot** : 15 Sous-couches légères) ; **Lourdes = `ulvl 2`** (**1 slot** : 30 Sous-couches complètes) ; **Intermédiaires = `ulvl 6`** (**2 slots** : 30 Sous-couches complètes + **30 Sur-couches exclusives renforcées** calées à `ulvl 6`, aucun don requis).
    - **Armes (hiérarchie des slots par famille, révisée le 19/11)** : le même mécanisme `UpgradeLevel` gâte les emplacements progressifs sur les `.uti` d'armes :
      - *Mêlée* (`Poignée = 1 < Lame = 2 < Cellule = 3`) : *Impact* (`UpgradeLevel = 1`, Poignée seule) · *Traditionnelle* (`UpgradeLevel = 2`, Poignée + Lame) · *Résonance* (`UpgradeLevel = 3`, Poignée + Lame + Cellule).
      - *Distance* (`Lunette = 1 < Pack = 2 < Chambrage = 3`) : *Tir Tactique* (`UpgradeLevel = 1`, Lunette seule) · ***Tir d'Assaut* & *Tir Assassin*** (`UpgradeLevel = 2`, Lunette + Pack) · *Tir Pénétrant* (`UpgradeLevel = 3`, Lunette + Pack + Chambrage).
  - *Piste archivée (non retenue pour les armures intermédiaires)* : `ShowUpgradeScreen(..., sOverride2DA)` dans `k_workbench.nss` (précédent `k_workbench_bdm.nss` → `"itemcreatemira"`) et les lignes inutilisées `CRAFT` / `MASTERCRAFT_WEAPONS_I..III` / `MASTERCRAFT_ARMOR_I..III` (`175–181` de `feat.2da`) permettent de conditionner des recettes `itemcreate*.2da` à un don, mais exigent un don plutôt que le type d'armure.
- **`forbiditemmask` — mapping confirmé (09/11 & 24/11)** : `0x01` = AC4 (38, légère) · `0x02` = AC5 (39) · `0x04` = AC6 (40, interm.) · `0x08` = AC7 (41) · `0x10` = AC8 (42, lourde) · `0x20` = AC9 (43). Un pouvoir est bloqué si `(masque ET bits de l'armure portée) ≠ 0`.
- **Règle moteur confirmée (24/11, cf. README §3.D)** : c'est la colonne **`itemtype`** (`31`/`32` = armure légère, `38` = bure) qui pilote le grisé natif des pouvoirs (`forbiditemmask`), indépendamment de `bodyvar`. Passer `Armor_Zeison_Sha` (ligne 102) à `itemtype = 31` aligne nativement Zeison Sha / Jal Shey / Malak (et Ubese ligne 98, déjà `itemtype = 32`) sur les armures légères tout en conservant 100 % des modèles 3D.
- **Aucune exception « Force-friendly » (décision 23/11)** : les lignes 98 (*Combinaison ubese*) et 102 (*Zeison Sha / Jal Shey*) suivent les mêmes restrictions de pouvoirs que les armures légères standard. Seules les bures 35–37 autorisent tous les pouvoirs.
- **`requireitemmask`** (inverse) : permet des pouvoirs exclusifs aux armures — piste de compensation Juggernaut.
- **`feat.2da`** : *Condition physique* = lignes 13/21/22 (*conservées vanilla, 23/11*) ; *Esquive* = ligne 125 ; *Course furtive* = ligne 197 ; *Bouclier de camouflage personnel* = ligne 201 ; *Création / Maître armes & armures* (inutilisés) = lignes 175–181.

### D. Budget détaillé par build (§6/§8) — *archive historique*

Gardé pour mémoire : la récomposition initiale (21/16/13) a été remplacée le 19/11 par les budgets définitifs **22 / 18 / 15 dons** (pour **12 / 16 / 24 pouvoirs**) avec gating par classe/prestige (cf. `decisions_finales.md` §1 & §6).

---

## 2. Options techniques validées (à activer lors des chantiers)

- **Coût de PF dynamique à l'impact** : `GetCurrentForcePoints`, `EffectDamageForcePoints`/`EffectHealForcePoints`, `GetSpellBaseForcePointCost` (précédent vanilla : remboursement Consulaire, `k_inc_force.nss` ~5950). Contraintes : l'UI n'affiche que le coût 2DA (documenter dans `dialog.tlk`) ; garder un coût de base non nul pour l'IA.
- **Réserve de PF — formule moteur (extraite de `classes.2da` le 14/11)** : `PF max = Σ par niveau (forcedie + mod. SAG + mod. CHA)` avec forcedie : Gardien 4 · Sentinelle 6 · Consulaire 8 · Maître d'Armes/Maraudeur 6 · Jedi protecteur/Assassin 8 · Maître Jedi/Seigneur Sith 10 (0 pour classes non-Jedi). Niveau 30 : Consulaire ~540–900 PF selon SAG/CHA ; Gardien ~180–270 PF.
- **Régénération / jauges** : `IsStealthed` (nwscript l. 5808), `GetMaxForcePoints`, `EffectRegenerate`, `EffectMissChance` (l. 4324), `GetTotalDamageDealt`, `GiveXPToCreature`/`SetXP`, `EffectSkillIncrease`, `EffectDamageShield` — tous vérifiés dans `nwscript.nss`.
- **`requireitemmask`** : pouvoirs exclusifs à un type d'armure (§1.C).

---

## 3. Contrat mathématique détaillé (décisions §9)

Détail des mesures simulées dans [`tools/dpr_check.py`](tools/dpr_check.py) (calibrage du 19/11 avec `Améliorations.csv` cloisonné, `bab_progression = 1.0` selon `CLS_ATK_1`, rangs I/II/III progressifs par phase et RD boss **`2/5/8`**) :

| Phase & Boss | Posture | **DPR net boss** | **Durée (TTK)** |
| :--- | :--- | :---: | :---: |
| **EARLY (Niv. 8)** 120 PV, CA 20, **RD 2** | Duel (`1M`) · Ambidextrie (`2A`) · Lourde (`2M`) · Haute Cadence (`HC`) | 11–23 · 9–18 · 14–26 · 17–30 | 5–11 · 7–14 · 5–8 · 4–7 |
| **MID (Niv. 16)** 280 PV étalon DPR *(rehaussé à `~380–420 PV` en Jalon 4)*, CA 29, **RD 5** | idem | 26–67 · 23–65 · 36–66 · 36–81 | 4–11 · 4–12 · 4–8 · 3,5–8 |
| **LATE (Niv. 26)** 650 PV, CA 44, **RD 8** | idem | 55–140 · 49–150 · 86–186 · 61–170 | 5–12 · 4–13 · 3,5–8 · 4–11 |

*Survie Late de référence (`Déluge 3` + `Robustesse 3`) :* Bure (`TTD/TTK = 1,51×` [8,0r / 5,3r]) · Légère + *Esquive Balistique* (`1,51×` [14,3r / 9,5r]) · Intermédiaire + *Armure Tactique* (`1,17×` sur 1 bouclier 100×3 [`1,55×` sur 2 boucliers]) · Lourde + *Juggernaut* (`1,54×` [17,2r / 11,2r]).

---

## 4. Références de données

- **12 CSV de référence (couche utilisateur)** : *Armes*, *Armures*, *Améliorations* (226 pièces), *Craft*, *Spé Pouvoirs*, *WIP Feats* (agrégateur), et les 6 CSV d'équipement (*Armures items*, *Brassards*, *Casques*, *Ceintures*, *Gants*, *Implants*).
- **Données extraites** : `datas_kotor/` (`equipement_*.md`, `loot_*.md`, `dons_kotor2.md`, `pouvoirs_kotor2.md`, `ennemis_*.md`, `modeles_mathematiques_equilibrage.md`, `armes_kotor2.md`) ; cache `itemdb/` (items.json, loot.json) via `tools/extract_items.py`.
- **JdR Star Wars d20** : `datas_jdr_SW/`.

---

## 5. Architecture Moteur — Moddable vs Hardcodé (Odyssey Engine)

### ❌ A. Codé en dur dans `swkotor2.exe`
1. **Effets des dons passifs vanilla** (Duel `+Atq/CA`, TWF `-6/-10`, Spé `+2`, Robustesse…) — contournables par dons neufs + effets scriptés (solution actée 15/11 : les dons Duel/Ambidextrie sont **recréés from scratch**, les vanilla sont supprimés de la sélection).
2. **Formules des attaques actives** (Déluge, Attaque en puissance, Critique, Décharge, Sniper).
3. **Multiplicateur de caractéristique par configuration** (en mêlée : 1,0×/0,5×/1,5× FOR par slot et armes doubles ; à distance : **0× en vanilla** sur toutes les configurations) — tout écart ou ajout à distance (`150 % DEX` en `1M` seul / `2M` base, `100 % / 50 % DEX` en Ambidextrie, `150 % / 50 % DEX` en `HC`, `165/185/200 % DEX` via *Arme Lourde*, ou `INT` via *Gand II*) s'injecte en différentiel via les wrappers `k_def_*` / `k_hen_*`.
4. **Pipeline de résolution d'attaque : jet → menace → confirmation → multiplicateur.** Aucune fonction pour forcer un critique, **aucun indicateur « ce coup fut un critique »** dans l'événement OnDamage (1006). Conséquences actées : procs des Spé d'arme = probabilité `plage/20` par coup ; critique furtif §10 = simulation.
5. **Aucun événement « attaque manquée »** (hooks 1001–1012). La punition du Matukai III dépend du **test T3** : reconstruction `Σ1005 (OnAttacked) − Σ1006 (OnDamage)` par attaquant, régularisée au 1003 — suppose que 1005 se déclenche à *chaque* attaque subie (non vérifié) et un ordre d'événements non garanti.
6. **Sauvegardes internes au moteur** (ex. propriétés d'objet `iprp_onhit`, DD 14 sonique) : aucun hook. Les punitions/effets « sur sauvegarde réussie » ne fonctionnent que pour les sauvegardes **scriptées** (pouvoirs via `k_inc_force.nss`, grenades si scriptées) — limite documentée pour Matukai II.
7. **Blocage d'équipage par `reqfeat0` (validé OK le 23/11 — test T2)** : bloque réellement l'équipement des armures **et** des armes (utilisé pour réserver les 69 variantes 1M `ov1m_*.uti` à *Raffinement Gamorréen II*).
8. **Ciblage des attaques multiples** : si la 1re attaque du round tue, les suivantes sont perdues.

### ✅ B. Moddable en `.2da` pur
1. Prérequis et accès des dons (`feat.2da` : `prereqfeat`, `orreqfeat`, colonnes `*_list`/`*_granted`, `featgain.2da`).
2. **Colonne `exclusion` de `feat.2da` (testée KO le 23/11)** : ne bloque pas la sélection au level-up → la mutualité des 6 arbres de Spé Carac repose sur le **garde-fou scripté** (premier arbre pris prioritaire, enregistré en `LocalNumber`).
3. Statistiques de base des armes/armures (`baseitems.2da` : dés, plage/multiplicateur critique, `equipableslots`, `reqfeat0-4`, CA, plafond DEX).
4. Coûts PF et restrictions d'armure des pouvoirs (`spells.2da`, `forbiditemmask`/`requireitemmask`).
5. Scaling ennemis (`autobalance.2da`), recettes (`itemcreate.2da` + `.uti`), progression de classes (`classes.2da` : `forcedie`, etc.).

### ⚡ C. Moddable par script (`.nss` → `.ncs`)
1. **Pouvoirs** (`k_inc_force.nss`) : dégâts, plafonds, attaques bonus, durées, DD — 100 % de contrôle.
2. **Passifs via wrappers heartbeat (`k_def_heartbt01` / `k_hen_heartbt01`)** : lecture des dons/caracs/équipement, bonus différentiels (attaque, dégâts dont `+150 % DEX` en `1M`/`2M`, `+100 % / +50 % DEX` en Ambidextrie, `+150 % / +50 % DEX` en `HC`, `165/185/200 % DEX` en `2M` *Arme Lourde* ou `INT` via *Gand II*, CA, RD, attaques bonus via `EffectModifyAttacks`).
3. **On-hit au hook 1006** (côté victime) : `GetLastDamager()`, arme via `GetItemInSlot`, procs maison (Spé d'arme), critique furtif §10, transfusion Krayt (heartbeat), punitions Matukai.
4. **Cumul `EffectACIncrease` (vérifié le 23/11 — T4)** : non cumulable entre effets séparés (seul le max s'applique) → tous les bonus de CA custom sont additionnés dans un unique `EffectACIncrease(nTotalAC, AC_DODGE_BONUS)`.
5. **Armes 2M/HC en main gauche (Gamorréen II — VALIDÉ EN JEU 25/11)** : T1/T2 confirmés (`baseitems.2da` 104–123 avec `equipableslots=0x00030`, `weaponwield=2/4`, `weaponsize=3`, `reqfeat0=MOD_GAMORREAN_2`, + `Use_Limitation_Feat` prop 57 sur chaque `.uti`). Plutôt que d'encombrer l'établi de recettes 1M figées, le don octroie l'**Adaptateur Gamorréen** (`ov_gam_adapt.uti`, `BaseItem=54` Stimulant `Unlimited_Use`) ouvrant un menu terminal (`ov_gam_conv.dlg` via placeable invisible `ov_gam_term.utp`) proposant 2 actions (« Ouvrir l'établi » et « Convertir l'arme équipée » + avertissement sur les améliorations) pour basculer à volonté toute arme 2M/HC tenue en main droite (mêlée et distance, **69** jumeaux exacts `ov1m_001..069.uti` dont les 3 armes de Péragus). Conséquence actée : Gamorréen II **n'interdit plus** les postures Arme Lourde (2M) ni Arme haute cadence (HC). Fait établi : les repeating ne sont pas des armes doubles (`weaponwield 6 ≠ 3`).
6. **Effets inexistants** : pas de `EffectDamageReductionDecrease` (→ variante « RD -3 » de la Spé Primitive écartée) ; pas de détection de critique ; pas d'interception du refus de lancement faute de PF (→ Krayt L2 en conversion heartbeat, pas en « puiser dans les PV »).

---

## 6. Diagnostic des Archétypes Vanilla (Niv. 28–30)

Analyse comparative historique (pré-D20 Overhaul) :

| Archétype / Classe | Total Dons | Budget Vanilla | Total Pouvoirs | Budget Pouvoirs |
| :--- | :---: | :---: | :---: | :---: |
| **Gunslinger 2 Blasters** (Voyou 15) | 17–18 | Équilibré | 0 (ou 15) | 0 (ou 5 arbres) |
| **Maraudeur Sith (2 Sabres)** | 17–18 | Équilibré | 29–31 | +16 en trop |
| **Jedi / Sith Mage** (Consulaire 15) | 12–13 | +4 à +6 inutiles | 38–40 | +18 à +24 en trop |
| **Sentinelle / Jedi protecteur** | 15–16 | +6 sans option martiale | 29–31 | +14 en trop |

**Constats** : le Consulaire croule sous ~40 pouvoirs sans dons pour les payer ; le Gardien perd son identité martiale sous ~30 pouvoirs ; la Sentinelle n'a pas accès aux dons Supérieurs.

---

## 7. Historique : la branche Mains nues (supprimée le 14/11)

L'arbre *Arts Martiaux / Arts Matukai / Arts Martiaux Supérieurs* (spécification initiale : Atq & Dégâts = jet + (DEX ou FOR) + SAG, plage 19-20 → 17-20, Tourbillon de Force sur critique — acté §6/§7 d'origine) a été **supprimé** : une seule série de dons par caractéristique étant retenue (§5), et l'identité mains nues étant désormais portée par la famille **Armes d'Impact** (décision révisée 24/11) + la posture Duel + la chaîne vanilla + la Spé carac Matukai. Le rang III Matukai a connu trois itérations (Vague de Force sur critique → Tourbillon à synergie Impact explicite, rejetée car « les synergies doivent être trouvées, pas décrites » → punitions sur sauvegarde ratée/attaque manquée, actée 15/11).

---

## 8. Spé caractéristique — Recherches & justifications (§5 du contrat)

- **Une carac = un arbre** : contrainte posée 13/11 pour forcer des builds atypiques (le CON du caster, la SAG du moine-soldat).
- **Exclusivité** : mutualité des 6 rangs I — le premier rang I choisi fixe l'arbre actif, les 5 autres arbres restent sélectionnables au level-up mais sans effet (garde-fou scripté `LocalNumber 22` ; la colonne `exclusion` de `feat.2da` a été testée KO le 23/11).
- **Transfusion Krayt** : l'indexation croisée (coût 5 % PV max, gain 5 % PF max) rend le rituel complet **invariable : 25 % PV ↔ 25 % PF** pour toutes les classes — le caster CON-investi est la cible (marge de PV + RD L1 pour rester > 75 %), le Gardien n'en a pas besoin. Combo assumé avec le pouvoir *Corps de Force*. Contre-jeu : faire pression sur les PV du Krayt.
- **Matukai (moine-ronce)** : boucle interne implicite — la CA-SAG du rang III augmente les ratés, donc la punition du rang III. Dégâts scriptés : contournent la RD, ne critent pas. À SAG +12 : +6 saves, ~12 dmg par punition.
- **Gamorréen (Colosse — révisé et validé en jeu le 25/11)** : octroie l'**Adaptateur Gamorréen** (bascule libre hors combat `2M/HC ↔ 1M` sur les **69** armes 2M/HC jouables, avec accès intégré à `ShowUpgradeScreen`) ; comme le personnage peut basculer de mode à volonté, **Gamorréen II n'interdit plus les postures Arme Lourde (2M) ni Arme haute cadence (HC)**. La FOR n'additionnant rien aux dégâts à distance, la version « 2 fusils » reste contenue naturellement.
- **Echani III** : suppression du plafond DEX des armures — perce volontairement le pilier §8.A (la duelliste cuirassée, Brianna) ; implémentation par différentiel (mod − plafond).
- **Suppression des dons Finesse vanilla** : les remaps d'attaque (DEX/FOR, DEX/INT, SAG) passent par les Spé carac ; FINESSE_MELEE et FINESSE_LIGHTSABERS retirés de la sélection.

---

## 9. Journal des arbitrages

| Date | Arbitre | Décision |
| :--- | :--- | :--- |
| 08/11 | — | Armures actées (§8) : RD native, 3 arbres, dégradé de pouvoirs, Condition physique III |
| 13/11 | utilisateur | Rangs III des Spé d'arme : abandon du « durée +1 tour / crit +1 » (marche sur les platebandes de Duel) → effets par famille |
| 13/11 | utilisateur | Proc sur coup = plage de menace / 20 ; DD = 10 + Niv + carac directrice |
| 13/11 | utilisateur | Une seule série de dons par caractéristique (6 arbres exclusifs) ; validation Gand + Echanis I-II + Nomi |
| 13/11 | utilisateur | Mains nues via Spé Contondante + Duel ; branche dédiée supprimée |
| 13/11 | utilisateur | Krayt L2 : 5 % PV max → 5 % PF max (jamais sous 75 % PV) |
| 13/11 | utilisateur | Matukai L1 : la SAG **s'ajoute** à l'attaque ; L2/L3 SAG→CA |
| 13/11 | utilisateur | Embuscade furtive = critique confirmé (§10) |
| 14/11 | utilisateur | Refonte des Spé d'arme : renommages (Impact/Traditionnelle/Résonance) + **4 familles de tir** ; Feats.csv restructuré à la main (colonne Source supprimée, colonne « Détail technique » ajoutée) |
| 14/11 | utilisateur | L'ordre canonique des caracs est FOR, DEX, CON, INT, SAG, CHA (dons et descriptions) |
| 14/11 | utilisateur | « Les synergies doivent être trouvées, pas décrites » — principe de conception |
| 15/11 | utilisateur | Style renommé « Arme haute cadence » ; règle balanced conservée (formulation vanilla) |
| 15/11 | utilisateur | Duel & TWF vanilla **supprimés**, dons recréés from scratch ; Finesse supprimés |
| 15/11 | utilisateur | Règle DD : base 10 si proc lié à la plage, 5 sinon ; Tir Lourd → **Tir Pénétrant** (ambiguïté mêlée/distance) |
| 15/11 | utilisateur | Résonance III : empilable, plafond -8, durée rafraîchie ; Résonance II : DD 5 |
| 15/11 | utilisateur | Matukai L2/L3 : punitions sur sauvegarde réussie et attaque ratée (moine-ronce) |
| 15/11 | utilisateur | Tests moteur tracés en TODO (colonne Détail technique du WIP Feats.csv) |
| 16/11 | utilisateur | Armures : RD native lourde portée à `4/-` ; refonte des 3 arbres (*Juggernaut*, *Blindage de Combat*, *Seconde Peau*) |
| 17/11 | utilisateur | *Seconde Peau* recalibré (`+1/+2/+3 CA base` + `10/20/30 %` esquive, sans hausse du plafond DEX) ; *Blindage de Combat* recentré sur boucliers (`+100 %` durée, efficacité `×2/×3`), furtivité sans ceinture et Course furtive |
| 17/11 | utilisateur | Upgrades armures intermédiaires : `swkotor2.exe` étant limité à 2 slots (`Sur-couche` + `Sous-couche`), décision de préparer lors de la refonte globale des upgrades des pièces combinant deux upgrades communes, réservées aux armures intermédiaires via `UpgradeLevel` (prérequis = type d'armure, sans don requis) |
| 17/11 | utilisateur | MASTER_CONDITIONING (Condition physique III) : supprimé au lieu d'être modifié (§8.D) |
| 18/11 | utilisateur | Armes à distance `1M` et `HC` : ajout de **`+100 % DEX`** en main directrice et **`+50 % DEX`** en main gauche / 2e tir (ou `INT` via *Gand II*) ; `2M` conservées à `150 % → 250 % DEX` |
| 18/11 | utilisateur | Armures légères et lourdes : confirmées à **1 seul emplacement d'upgrade** chacune (Sur-couche seule pour Légère, Sous-couche seule pour Lourde) ; Intermédiaires = 2 emplacements combinés |
| 18/11 | utilisateur | Slots d'upgrades par famille d'arme (`Poignée < Lame < Cellule` en mêlée ; `Viseur < Cellule < Chambrage` à distance) + retrait du bâton Gaffi ; les familles à 1–2 slots plafonnent plus bas à l'établi en échange de dégâts de base / plages / multiplicateurs de critique plus élevés |
| 18/11 | — | Calibrage complet validé sous `dpr_check.py` : `CLS_ATK_1` (`BAB 1.0`) toutes classes ; suppression du malus `-6/-10 Atq` sur `double` ; `Armure lourde` portée à `CA base 10` ; 29 armes calibrées (`WIP armes.csv`) ; 216 améliorations moddées (`WIP Améliorations.csv`, `18` standards + `12` combinées sur-couches/sous-couches) |
| 19/11 | utilisateur | Scaling des DD fixes : **Grenades** = `10 + Niv + Mod INT` (seuil ≥ 40 % sur Vigueur élite à INT 14), **Fléchettes/Roquettes** = `12 + Niv + Mod INT`, ***On-Hit* d'armes** (ex DD 10/14/18/22) = `3 / 5 / 7 / 9 + Niv + Mod Carac` (caractéristique à définir au cas par cas lors du rééquilibrage des armes) |
| 19/11 | utilisateur | **Cloisonnement strict des rôles par slot d'amélioration d'arme** (§3.A) : 1 seul slot de dégâts bruts par catégorie (`Cellule` en mêlée/sabre, `Chambrage` à distance), 0 dégât plat sur Poignée/Lame/Lunette/Émetteur/Lentille/Cristaux ; **Tir d'Assaut verrouillé à 2 slots** (`Lunette + Pack`, pas de Chambrage) ; **effets *On-Hit* scalés réintroduits sur les Lunettes et Émetteurs** (synergie *Tir Tactique* et *Laser*) |
| 19/11 | utilisateur | **Refonte identités & dés des armes (`WIP armes.csv`)** : retour aux dés natifs d20 (`1d6` à `2d8`), correction de l'inversion 1M/2M à distance, **toutes les armes doubles (`HC`) sont `balanced`**, *Lame de guerre wookiee* confirmée en épée double *Traditionnelle* (`HC balanced`, `1d10`, `20/×3`), *Vibro-épée* confirmée en `2M` (`1d10`, `19-20/×2`), *Double sabre laser* à `2d8` (`20/×2`) |
| 19/11 | utilisateur | **Budgets Dons / Pouvoirs Niv. 30 (§1 & §6)** : recalibrés à **22 / 18 / 15 dons** pour **12 / 16 / 24 pouvoirs** (Consulaire ramené de 31 à 24 pouvoirs pour supprimer les fillers de fin de jeu) ; arbres conservés en 3 rangs marquants (pas de découpage massif), identités protégées par le gating Classe / Prestige sur les Rangs II–III |
| 19/11 | utilisateur | **Gating Classe / Prestige & renommage armures (§6 & §8.B)** : *Blindage de Combat* → **Armure Tactique**, *Seconde Peau* → **Esquive Balistique** ; matrice de prérequis actée sur Spé d'arme, Postures, Armures, Éveil de Force et Spé Carac (paliers Niv. 1/8/15+, libres de classe) ; **Compagnons** reportés à un arbitrage par classe dans un second temps |
| 19/11 | utilisateur | **Compagnons (§6)** : gating réglé par classe (non-Jedi `SOL/SCT/SCD/TEC/DRC` accèdent aux Rangs III pertinents au Niv. 15+ via `minattackbonus = 15`) + **2 exceptions level-up uniquement** : **Kreia Niv. 15+** = Maître Jedi (tout Éveil de Force), **Visas Niv. 15+** = Assassin Sith (dons sélectionnables d'Assassin). Implémentation propre via don prérequis caché (`MOD_PRESTIGE_MAGE` / `MOD_PRESTIGE_HYBRID`) accordé auto aux prestiges et scripté sur Kreia/Visas au Niv. 15 |
| 19/11 | utilisateur | **Validation simulation DPR/TTK/Survie (§3.B, §4.A, §9)** : *Vitesse de Force* (`+2` atq en Bure) confirmée équilibrée (ratios TTD/TTK identiques ~`1,5×` sur Bure/Légère/Intermédiaire/Lourde) ; **RD boss** ramenée de `3/7/12` à **`2/5/8`** (PV inchangés) ; **Arme Lourde (`2M`)** plafonnée à **`215/235/250 % FOR` / `165/185/200 % DEX`** ; parité distance **`150 % DEX`** en Duel 1M et **`150 %/50 %`** en `HC` ; Pistolets `1M` portés à `1d10` (`1d8` poche) et Blasters à répétition `HC` à `2d6` ; *Armure Tactique* validée sans buff d'arbre (bouclier `100×3` + 2 slots combinés suffisent) |
| 19/11 | utilisateur | **Refonte Chasseur de prime Gand (§5)** : **Gand I** = `+1 INT` + grenades **`+5 %` dégâts / rang total de Démolition** (viables dès Péragus) ; **Gand II** = `+2 INT` + attaque & dégâts distance DEX/INT ; **Gand III** = `+3 INT` + rayon grenades `4 m → 6 m`, perce *Esquive Totale* et `50 %` de non-consommation (100 % scripté dans `k_sup_grenade.nss`) |
| 19/11 | utilisateur | **Servante, Immunité & Craft** : *Prémonition du combat* (récompense Echani) remplacé par **`+10 %` d'esquive en mêlée** ; **aucun cap global d'immunité** (révisable selon retours joueurs) ; **toutes les armes de base non-laser craftables** à l'établi |
| 19/11 | utilisateur | **Paliers de niveau du Craft (`Craft.csv` / `itemcreate.2da`)** : verrou par niveau joueur acté à **`Mk I = Niv. 1 / Mk II = Niv. 10 / Mk III = Niv. 15 / Mk IV-T5 = Niv. 20`** (`1 / 10 / 18` sur lignées 3 tiers) ; 18 armes de base non-laser manquantes + 24 upgrades doubles d'armures intermédiaires ajoutées dans `Craft.csv` |
| 19/11 | utilisateur | **Refonte *Camouflage par la Force* (`Spé Pouvoirs.csv`)** : autorisé jusqu'à Armure intermédiaire · **L1** : furtivité sans ceinture + Course furtive auto + `+4` Discrétion · **L2** : `+8` Discrétion + embuscade `+2d6` et Stun 1t (`DD 10 + Niv + Carac`) · **L3** : `+12` Discrétion + chaque kill donne prochain coup critique confirmé (dans les 2 rounds) et `+25 %` esquive pendant 2 rounds (non cumulable, réinitialisable) |
| 20/11 | utilisateur | **Passe complète Pouvoirs (`Spé Pouvoirs.csv`)** : aucun cap de dés en L3 ; *Tempête* `1d6/Niv` sans drain PF passée en jet de **Réflexes** (cohérence d20 + Esquive Totale native) ; *Mise à mort* `1d8/Niv` + stun (suppression du 50 % PV max) ; *Lancer de sabre* `1d4/Niv` + Renversement **Vigueur** en L1 / 3 cibles + ignore RD en L2 ; *Peste* sans DD 100 (`-6` / `-3` si Vig) ; *Écrasement* `1d6/Niv` (Vig ½ + annule) ; *Barrière* `3/6/10` *(aligné ensuite à `4/8/12`)*, *Résist. Énergie* `4/8/12` + Poison *(aligné ensuite sans Poison)*, *Talent* `+2/+3/+4` ; buffs de *Cri, Absorption de Force, Corps de Force, Parade/Renvoi, Confusion* et validation des 4 `(WIP)` |
| 21/11 | utilisateur | **Refonte des Ultimes de Prestige & Alignement (`Spé Pouvoirs.csv`, adossée à la philosophie de Kreia)** : uniformisation de tous les pouvoirs de prestige en **L3 max (niv. 1/5/9 de prestige)** · *Stigmate de Force* (ex *Fureur Sith*, Maraudeur, Lourde, 30 s) = `+2/+4/+6` FOR & DEX, immunité Stase/Paralysie, **`+1 atq/rd` dès L1**, `-5 %` PV max/rd (arrêt ≤ 25 % PV) · *Cicatrice de Force* (nouveau, Maître d'armes, Lourde, 30 s) = `+2/+4/+6 %` PV max/rd + `+1/+2/+3` saves + immunités mentales · *Spectre de la Force* (ex *Camouflage par la Force*, exclusif Assassin Sith) · *Affranchi de la Force* (nouveau passif, Jedi protecteur, Lourde) = `+1` / 8 rangs combinés sur 4 paires de compétences (plafond `+3/+5/+7`) + L2 `+25 %` objets profanes + L3 SR passive `15 + Niv` · *Déchirure de la Force* (ex *Annihilation de l'opposition*, Seigneur Sith, Lourde, 45 s) = `-2/-4/-6` Atq/Saves/CA en zone 15 m (Vol annule) · *Écho des Liens* (ex *Inspiration des disciples*, Maître Jedi, Lourde) = partage des buffs personnels 30/45/60 s (1 allié → groupe → groupe + soins, exploit Kreia conservé) · *Grâce du côté Lumineux* (`Armure intermédiaire`, *Vitesse* plafonnée `+1 atq/rd` en armure) & *Écrasement de Force* (`Armure légère`, `1d8/Niv` dégâts purs + immo 6 s) |
| 21/11 | utilisateur | **Grille des coûts en PF évolutifs par rang (`Spé Pouvoirs.csv`, colonne `Coût PF (L1/L2/L3)`)** : suppression des coûts plats/dégressifs vanilla (`Tempête` `15/30/50`, `Insanité` `15/25/45`, `Stase` `15/30/50`, `Soins` `20/35/50`, `Barrière` & `Résist. Énergie` `15/25/35`, `Vitesse`/`Talent` `15/30/45`, `Grâce` `50`, `Écrasement` `60`, ultimes prestige `20/30/40` martiaux & `25/35/45` mages) ; calibrée sur les réserves L25 (`200 / 300 / 500 PF`) et rend la pénalité d'alignement opposé réellement dissuasive |
| 21/11 | utilisateur | **Alignement final *Barrière de Force* & *Résistance à l'énergie* (`Spé Pouvoirs.csv`)** : les deux pouvoirs sont alignés en **Armure intermédiaire**, **`RD 4 / 8 / 12`**, personnel uniquement, durée **`60 s`** à tous les rangs, coût **`15 / 25 / 35 PF`** (suppression de l'effet de groupe et de l'immunité Poison sur *Résistance à l'énergie*). |
| 21/11 | utilisateur | **Rééquilibrage DS/LS & sauvegardes de 4 pouvoirs classiques (`Spé Pouvoirs.csv`)** : *Terreur/Horreur/Insanité* (`Légère`, `15/25/45 PF`) devient DoT mental (`Niv` dég/rd) + `-4/-6/-8 Atq` sans perte d'action (`24 s` échec / `6 s` réussite Vol) · *Champ de stase* (`Bure`, `10 m`) porté à `36 s` max avec jet de Vigueur chaque round à DD `-3/rd` · *Vague de Force* (`Intermédiaire`) transformé en Tourbillon AoE `6 m / 12 s` (`1/3 Niv / 2 s`, Réf réussie = ½ dégâts immédiats) · *Absorption de vie / Champ de mort / Festin de mort* (`Bure`, `20/40/55 PF`) passé à `1d3/Niv` (100 % dégâts = soin) avec nouveau L3 **Festin de mort** (excédent de soin → `EffectTemporaryHitpoints` pendant `24 s`, non cumulable, zéro conflit bouclier) |
| 25/11 | utilisateur | **RD exactes équipement & bêtes (`iprp_resistcost.2da`)** : option 1 validée — extension de `iprp_resistcost.2da` avec les lignes `7..11` (`2/-`, `3/-`, `4/-`, `6/-`, `12/-`) appliquées aux 13 `.uti` d'équipement plafonnés (Casques/Implants/Gants/Ceintures/Brassards/Armures) et aux peaux de bêtes (`4/-`, `6/-`), sans arrondi aux paliers vanilla `5/10/15`. |
| 25/11 | utilisateur | **Gamorréen II — Adaptateur `2M/HC ↔ 1M` validé en jeu & levée de l'interdiction des postures 2M/HC** : abandon de l'établi de recettes 1M figées au profit de l'**Adaptateur Gamorréen** (`ov_gam_adapt.uti` + `ov_gam_conv.dlg` + `ShowUpgradeScreen` intégré toujours disponible quelle que soit l'arme équipée, **69** jumeaux exacts `ov1m_*.uti` dont Péragus, doublement verrouillés via `reqfeat0` + `Use_Limitation_Feat = MOD_GAMORREAN_2`). Comme le joueur peut basculer librement en posture hors combat entre mode 2M/HC et mode 1M, **la sélection de Raffinement Gamorréen II n'interdit plus l'usage des postures Arme Lourde (2M) et Arme haute cadence (HC)**. |
| 25/11 | utilisateur | **Gamorréen II — Option B validée après simulation DPR/TTK/Survie** : toute arme haute cadence (double-lame ou blaster à répétition) adaptée en **1M** et équipée en **main principale (main droite)** conserve **`+1` attaque/round** (`EffectModifyAttacks(1)`, plafond moteur `+2` partagé avec Vitesse de Force / Tir d'Assaut III, **`0` malus de CA**) ; **aucun bonus d'attaque en main gauche** (limitation moteur `OffHandAttacks ≤ 1` + équilibre DPR, mentionné explicitement sur la fiche de chaque arme HC 1M). Cumul de deux postures (*Amb + HC* ou *Amb + Arme Lourde*) écarté (TTK `< 4` rounds). |
