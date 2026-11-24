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

- **RD native & arbres** : hook fin de round de `k_ai_master.nss` lisant `GetBaseItemType()` de l'armure (lignes baseitems 38–43), parcours anti-cumul d'effets (README §3.A).
- **Effets validés par arbre d'armure** (`nwscript.nss`) :
  - **Lourde (*Juggernaut*)** : `EffectDamageReduction` (RD 4 native + `3/4/5` du don) + `EffectDamageImmunityIncrease(nDamageType, 10/20/30)` sur les types de dégâts (cap d'immunité global à surveiller avec les pièces d'équipement).
  - **Moyenne (*Blindage de Combat*)** :
    - *Furtivité sans ceinture (Rang I, armure moyenne portée)* : octroi/retrait conditionnel via `GrantFeat` / `PERSONAL_CLOAKING_SHIELD` (`feat.2da` ligne `201`, seul don de camouflage actif sous armure, contrairement aux rangs II/III de `XXXFORCE_CAMOFLAGE` `97/141/142`) ; *Course furtive* au Rang II via `STEALTH_RUN` (ligne `197`). *(À tester : retrait propre quand l'armure est retirée ou changement de comportement si l'armure moyenne est déséquipée — si `RemoveFeat` n'existe pas dans `nwscript.nss`, privilégier un garde-fou ou une vérification sur les scripts/dons).*
    - *Boucliers (`+100 %` durée au Rang I, efficacité `×2 / ×3` aux Rangs II–III)* : tous les boucliers d'avant-bras passent par `k_sup_bands.nss` → `EffectForceShield(nShield)` indexé sur `forceshields.2da`. Rang I double `fDuration` (`200.0 + 2.0 * nRepairSkill`) ; Rangs II et III sélectionnent des lignes dupliquées dans `forceshields.2da` avec `amount × 2` et `amount × 3`.
  - **Légère (*Seconde Peau*)** : `EffectMissChance(10/20/30)` (signature K2 à 1 paramètre `int nPercentage`, `nwscript.nss` l. 4324) + `EffectACIncrease(1/2/3)` (aucune hausse du plafond de DEX).
- **Établi dans `swkotor2.exe` — limite des slots & contournement par `UpgradeLevel` (vérifiés le 17/11)** :
  - Contrairement aux `.uti` ou à `baseitems.2da`, le nombre de slots d'établi est codé en dur par onglet (`0x4ca630` + table `4 × 6` à `0x5a70e8`) : Sabres = 6 slots (`BTN_UPGRADE31..36_LS` dans `upgrade_p.gui`, dont Slots 0 et 2 sur `upgradetype 0`), Distance/Mêlée = 3 slots, Armures = **2 slots maximum** (`Slot 0 = upgradetype 10` *Sur-couche*, `Slot 1 = upgradetype 11` *Sous-couche* ; le 3e bouton `BTN_UPGRADE33` est explicitement masqué à `0x4cb070`). Impossible donc d'équiper 2 sur-couches + 2 sous-couches séparées sans patch binaire.
  - **Gating natif via `UpgradeLevel` (`0x4cbcd0`)** : pour chaque slot, le moteur vérifie `upgrade.UpgradeLevel <= item.UpgradeLevel`.
    - **Armures** : en attribuant le **`UpgradeLevel` maximal** (ex. `4`, ou `3` avec Bure = `0`, Lourde = `1`, Légère = `2`, Intermédiaire = `3`/`4`) **uniquement aux `.uti` d'armures intermédiaires** et en créant lors de la refonte des **sur-couches et sous-couches combinées** (fusionnant deux upgrades communes en une pièce) calées sur ce palier, les armures intermédiaires obtiennent nativement l'exclusivité de ces upgrades doubles sur simple critère de type d'armure (aucun don requis). Les armures **légères** (Sur-couche uniquement) et **lourdes** (Sous-couche uniquement) sont quant à elles limitées à **1 seul emplacement d'upgrade** chacune (décision confirmée le 18/11).
    - **Armes (hiérarchie des slots par famille, 18/11)** : le même mécanisme `UpgradeLevel` gâte les emplacements progressifs sur les `.uti` d'armes :
      - *Mêlée* (`Poignée = 1 < Lame = 2 < Cellule = 3`) : *Impact* (`UpgradeLevel = 1`, Poignée seule) · *Traditionnelle* (`UpgradeLevel = 2`, Poignée + Lame) · *Résonance* (`UpgradeLevel = 3`, Poignée + Lame + Cellule).
      - *Distance* (`Viseur = 1 < Cellule = 2 < Chambrage = 3`) : *Tir Tactique* (`UpgradeLevel = 1`, Viseur seul) · *Tir Assassin* (`UpgradeLevel = 2`, Viseur + Cellule) · *Tir d'Assaut & Tir Pénétrant* (`UpgradeLevel = 3`, Viseur + Cellule + Chambrage).
      *(Vérifier lors de l'implémentation que chaque `.uti` d'arme porte uniquement les propriétés `Upgrade` correspondant à ses slots autorisés, ou le palier `UpgradeLevel` adéquat).*
  - *Piste archivée (non retenue pour les armures intermédiaires)* : `ShowUpgradeScreen(..., sOverride2DA)` dans `k_workbench.nss` (précédent `k_workbench_bdm.nss` → `"itemcreatemira"`) et les lignes inutilisées `CRAFT` / `MASTERCRAFT_WEAPONS_I..III` / `MASTERCRAFT_ARMOR_I..III` (`175–181` de `feat.2da`) permettent de conditionner des recettes `itemcreate*.2da` à un don, mais exigent un don plutôt que le type d'armure.
- **`forbiditemmask` — mapping confirmé (09/11)** : `0x01` = AC4 (38, légère) · `0x02` = AC5 (39) · `0x04` = AC6 (40, interm.) · `0x08` = AC7 (41) · `0x10` = AC8 (42, lourde) · `0x20` = AC9 (43). Un pouvoir est bloqué si `(masque ET bits de l'armure portée) ≠ 0`.
- **Les bits viennent de l'identité de ligne, pas des stats** (constaté 14/11) : les lignes 98 (*Combinaison ubese*, `baseac 5`) et 102 (*Zeison Sha*) échappent à **tous** les masques alors que la ligne 39 a le même `baseac` — preuve que les bits dérivent de l'appartenance au bloc 38–43.
- **Aucune exception « Force-friendly » (décision 23/11)** : les lignes 98 (*Combinaison ubese*) et 102 (*Zeison Sha / Jal Shey*) ne bénéficient d'aucune exception — elles suivent les mêmes restrictions de pouvoirs que les armures légères standard (à aligner côté `baseitems.2da` / `.uti` lors de l'implémentation). Seules les robes 35–37 autorisent tous les pouvoirs.
- **`requireitemmask`** (inverse) : permet des pouvoirs exclusifs aux armures — piste de compensation Juggernaut.
- **`feat.2da`** : *Condition physique* = lignes 13/21/22 (*conservées vanilla, 23/11*) ; *Esquive* = ligne 125 ; *Course furtive* = ligne 197 ; *Bouclier de camouflage personnel* = ligne 201 ; *Création / Maître armes & armures* (inutilisés) = lignes 175–181.

### D. Budget détaillé par build (§6/§8) — *ancienne structure, à réarbitrer (voir §9-J)*

Gardé pour mémoire : Gardien Juggernaut / robe, Sentinelle, Consulaire — 15 dons socle + bonus. La refonte postures/familles/carac (13–15/11) rend cette récomposition obsolète sans en changer les totaux (21/16/13).

---

## 2. Options techniques validées (à activer lors des chantiers)

- **Coût de PF dynamique à l'impact** : `GetCurrentForcePoints`, `EffectDamageForcePoints`/`EffectHealForcePoints`, `GetSpellBaseForcePointCost` (précédent vanilla : remboursement Consulaire, `k_inc_force.nss` ~5950). Contraintes : l'UI n'affiche que le coût 2DA (documenter dans `dialog.tlk`) ; garder un coût de base non nul pour l'IA.
- **Réserve de PF — formule moteur (extraite de `classes.2da` le 14/11)** : `PF max = Σ par niveau (forcedie + mod. SAG + mod. CHA)` avec forcedie : Gardien 4 · Sentinelle 6 · Consulaire 8 · Maître d'Armes/Maraudeur 6 · Jedi protecteur/Assassin 8 · Maître Jedi/Seigneur Sith 10 (0 pour classes non-Jedi). Niveau 30 : Consulaire ~540–900 PF selon SAG/CHA ; Gardien ~180–270 PF.
- **Régénération / jauges** : `IsStealthed` (nwscript l. 5808), `GetMaxForcePoints`, `EffectRegenerate`, `EffectMissChance` (l. 4324), `GetTotalDamageDealt`, `GiveXPToCreature`/`SetXP`, `EffectSkillIncrease`, `EffectDamageShield` — tous vérifiés dans `nwscript.nss`.
- **`requireitemmask`** : pouvoirs exclusifs à un type d'armure (§1.C).

---

## 3. Contrat mathématique détaillé (décisions §9)

Détail des mesures simulées dans [`tools/dpr_check.py`](tools/dpr_check.py) (mode `cap` & `vanilla` resynchronisé sur *WIP Améliorations.csv*, avec `bab_progression = 1.0` selon `CLS_ATK_1`, rangs I/II/III progressifs par phase) :

| Phase & Boss | Posture | **DPR net boss** | **Durée (TTK)** |
| :--- | :--- | :---: | :---: |
| **EARLY (Niv. 8)** 120 PV, CA 20, RD 3 | Duel (`1M`) · Ambidextrie (`2A`) · Lourde (`2M`) · Haute Cadence (`D`) | 14–24 · 13–17 · 18–24 · 23–30 | 5–9 · 7–9 · 5–7 · 4–5 |
| **MID (Niv. 16)** 280 PV, CA 29, RD 7 | idem | 30–62 · 31–46 · 49–65 · 45–64 | 4–9 · 6–9 · 4–6 · 4–6 |
| **LATE (Niv. 26)** 650 PV, CA 44, RD 12 | idem | 61–128 · 74–132 · 116–161 · 104–154 | 5–11 · 5–9 · 4–6 · 4–6 |

*Survie de référence (Boss `Set_5` à 16 / 28 / 45 dégâts/coup) :* Bure Jedi (`CA 18/28/39`, `TTD 4,1/3,7/4,3 rds`) · Légère + Seconde Peau (`CA 21/26/34` + `10/20/30 %` esquive, `TTD 4,2–10,3 rds`) · Moyenne + Blindage + Illumination (`CA 21/29/36`, `RD 6/8/9`, bouclier `20/70/180`, `TTD 6,6–8,1 rds`) · Lourde + Juggernaut (`CA 20/28/36`, `RD 8/12/14`, `Imm 15/30/44 %`, `TTD 11,7–17,2 rds`).

---

## 4. Références de données

- **CSV de référence (couche utilisateur)** : *Style de combat*, *Spécialisation d'arme*, *spé carac*, *WIP Feats* (agrégateur), *WIP armes*, *WIP Améliorations* (226 pièces), *WIP Spé Pouvoirs*, *spé Armure*.
- **Données extraites** : `datas_kotor/` (`equipement_*.md`, `loot_*.md`, `dons_kotor2.md`, `pouvoirs_kotor2.md`, `ennemis_*.md`, `modeles_mathematiques_equilibrage.md`, `armes_kotor2.md`) ; cache `itemdb/` (items.json, loot.json) via `tools/extract_items.py`.
- **JdR Star Wars d20** : `datas_jdr_SW/`. **Idées brutes** : `idée mods.md`.

---

## 5. Architecture Moteur — Moddable vs Hardcodé (Odyssey Engine)

### ❌ A. Codé en dur dans `swkotor2.exe`
1. **Effets des dons passifs vanilla** (Duel `+Atq/CA`, TWF `-6/-10`, Spé `+2`, Robustesse…) — contournables par dons neufs + effets scriptés (solution actée 15/11 : les dons Duel/Ambidextrie sont **recréés from scratch**, les vanilla sont supprimés de la sélection).
2. **Formules des attaques actives** (Déluge, Attaque en puissance, Critique, Décharge, Sniper).
3. **Multiplicateur de caractéristique par configuration** (en mêlée : 1,0×/0,5×/1,5× FOR par slot et armes doubles ; à distance : **0× en vanilla** sur toutes les configurations) — tout écart ou ajout à distance (`100 % / 50 % DEX` en `1M`/`D`, `150 % → 250 % DEX` en `2M`, ou `INT` via *Gand II*) s'injecte en différentiel via `k_ai_master.nss`.
4. **Pipeline de résolution d'attaque : jet → menace → confirmation → multiplicateur.** Aucune fonction pour forcer un critique, **aucun indicateur « ce coup fut un critique »** dans l'événement OnDamage (1006). Conséquences actées : procs des Spé d'arme = probabilité `plage/20` par coup ; critique furtif §10 = simulation.
5. **Aucun événement « attaque manquée »** (hooks 1001–1012). La punition du Matukai III dépend du **test T3** : reconstruction `Σ1005 (OnAttacked) − Σ1006 (OnDamage)` par attaquant, régularisée au 1003 — suppose que 1005 se déclenche à *chaque* attaque subie (non vérifié) et un ordre d'événements non garanti.
6. **Sauvegardes internes au moteur** (ex. propriétés d'objet `iprp_onhit`, DD 14 sonique) : aucun hook. Les punitions/effets « sur sauvegarde réussie » ne fonctionnent que pour les sauvegardes **scriptées** (pouvoirs via `k_inc_force.nss`, grenades si scriptées) — limite documentée pour Matukai II.
7. **Blocage d'équipage par `reqfeat`** : certain pour les **armures** (prérequis de port), **inconnu pour les armes** (test T2 — la colonne semble y piloter le malus -4 de non-maniement).
8. **Ciblage des attaques multiples** : si la 1re attaque du round tue, les suivantes sont perdues.

### ✅ B. Moddable en `.2da` pur
1. Prérequis et accès des dons (`feat.2da` : `prereqfeat`, `orreqfeat`, colonnes `*_list`/`*_granted`, `featgain.2da`).
2. **Colonne `exclusion` de feat.2da** (découverte 14/11) : bitfield probable de mutualité — **seul usage vanilla : `DROID_TRICK` (234) et `DROID_CONFUSION` (235) = `0x01`** (paradoxe : le second exige le premier en prérequis → à tester, test T-exclusion). Piste retenue pour l'exclusivité des 6 arbres carac + garde-fou script (n'appliquer que la première origine prise).
3. Statistiques de base des armes/armures (`baseitems.2da` : dés, plage/multiplicateur critique, `equipableslots`, `reqfeat0-4`, CA, plafond DEX).
4. Coûts PF et restrictions d'armure des pouvoirs (`spells.2da`, `forbiditemmask`/`requireitemmask`).
5. Scaling ennemis (`autobalance.2da`), recettes (`itemcreate.2da` + `.uti`), progression de classes (`classes.2da` : `forcedie`, etc.).

### ⚡ C. Moddable par script (`.nss` → `.ncs`)
1. **Pouvoirs** (`k_inc_force.nss`) : dégâts, plafonds, attaques bonus, durées, DD — 100 % de contrôle.
2. **Passifs au hook 1003** (fin de round, `k_ai_master.nss`) : lecture des dons/caracs/équipement, bonus différentiels (attaque, dégâts dont `+100 % / +50 % DEX` à distance `1M`/`D` et `150 % → 250 % DEX` en `2M` ou `INT` via *Gand II*, CA, RD, attaques bonus via `EffectModifyAttacks`).
3. **On-hit au hook 1006** (côté victime) : `GetLastDamager()`, arme via `GetItemInSlot`, procs maison (Spé d'arme), critique furtif §10, transfusion Kraith (heartbeat), punitions Matukai.
4. **Effets vérifiés mais sémantique inconnue** : plafond éventuel des bonus de CA de même type (esquive +20 héritée NWN ?) — impacte le cumul Nomi/Matukai × Précognition guerrière (test « plafond CA »).
5. **Armes doubles en main gauche** : jamais possible en vanilla (`equipableslots 0x10`) — comportement (nombre d'attaques, multiplicateurs) totalement inconnu → **test T1** (Gamoréen II) ; gating des éventuelles variantes 1M → **test T2**. Fait établi : les repeating ne sont pas des armes doubles (`weaponwield 6 ≠ 3`).
6. **Effets inexistants** : pas de `EffectDamageReductionDecrease` (→ variante « RD -3 » de la Spé Primitive écartée) ; pas de détection de critique ; pas d'interception du refus de lancement faute de PF (→ Kraith L2 en conversion heartbeat, pas en « puiser dans les PV »).

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

L'arbre *Arts Martiaux / Arts Mutaki / Arts Martiaux Supérieurs* (spécification initiale : Atq & Dégâts = jet + (DEX ou FOR) + SAG, plage 19-20 → 17-20, Tourbillon de Force sur critique — acté §6/§7 d'origine) a été **supprimé** : une seule série de dons par caractéristique étant retenue (§5), et l'identité mains nues étant désormais portée par la famille **Armes d'Impact** (décision révisée 24/11) + la posture Duel + la chaîne vanilla + la Spé carac Matukai. Le rang III Matukai a connu trois itérations (Vague de Force sur critique → Tourbillon à synergie Impact explicite, rejetée car « les synergies doivent être trouvées, pas décrites » → punitions sur sauvegarde ratée/attaque manquée, actée 15/11).

---

## 8. Spé caractéristique — Recherches & justifications (§5 du contrat)

- **Une carac = un arbre** : contrainte posée 13/11 pour forcer des builds atypiques (le CON du caster, la SAG du moine-soldat).
- **Exclusivité** : interdiction mutuelle des 6 rangs I. Mécanisme : bit `exclusion` partagé (T-exclusion) + garde-fou script (heartbeat : seule la première origine prise s'applique).
- **Transfusion Kraith** : l'indexation croisée (coût 5 % PV max, gain 5 % PF max) rend le rituel complet **invariable : 25 % PV ↔ 25 % PF** pour toutes les classes — le caster CON-investi est la cible (marge de PV + RD L1 pour rester > 75 %), le Gardien n'en a pas besoin. Combo assumé avec le pouvoir *Corps de Force*. Contre-jeu : faire pression sur les PV du Kraith.
- **Matukai (moine-ronce)** : boucle interne implicite — la CA-SAG du rang III augmente les ratés, donc la punition du rang III. Dégâts scriptés : contournent la RD, ne critent pas. À SAG +12 : +6 saves, ~12 dmg par punition.
- **Gamoréen (Colosse)** : toutes armes à 1M contre la perte des postures Double/2M ; la FOR n'additionnant rien aux dégâts à distance, la version « 2 fusils » est contenue naturellement. Dépend des tests T1/T2.
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
| 13/11 | utilisateur | Kraith L2 : 5 % PV max → 5 % PF max (jamais sous 75 % PV) |
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
| 18/11 | utilisateur | Armes à distance `1M` et `D` : ajout de **`+100 % DEX`** en main directrice et **`+50 % DEX`** en main gauche / 2e tir (ou `INT` via *Gand II*) ; `2M` conservées à `150 % → 250 % DEX` |
| 18/11 | utilisateur | Armures légères et lourdes : confirmées à **1 seul emplacement d'upgrade** chacune (Sur-couche seule pour Légère, Sous-couche seule pour Lourde) ; Intermédiaires = 2 emplacements combinés |
| 18/11 | utilisateur | Slots d'upgrades par famille d'arme (`Poignée < Lame < Cellule` en mêlée ; `Viseur < Cellule < Chambrage` à distance) + retrait du bâton Gaffi ; les familles à 1–2 slots plafonnent plus bas à l'établi en échange de dégâts de base / plages / multiplicateurs de critique plus élevés |
| 18/11 | — | Calibrage complet validé sous `dpr_check.py` : `CLS_ATK_1` (`BAB 1.0`) toutes classes ; suppression du malus `-6/-10 Atq` sur `double` ; `Armure lourde` portée à `CA base 10` ; 29 armes calibrées (`WIP armes.csv`) ; 216 améliorations moddées (`WIP Améliorations.csv`, `18` standards + `12` combinées sur-couches/sous-couches) |
| 19/11 | utilisateur | Scaling des DD fixes : **Grenades** = `10 + Niv + Mod INT` (seuil ≥ 40 % sur Vigueur élite à INT 14), **Fléchettes/Roquettes** = `12 + Niv + Mod INT`, ***On-Hit* d'armes** (ex DD 10/14/18/22) = `3 / 5 / 7 / 9 + Niv + Mod Carac` (caractéristique à définir au cas par cas lors du rééquilibrage des armes) |
| 19/11 | utilisateur | **Cloisonnement strict des rôles par slot d'amélioration d'arme** (§3.A) : 1 seul slot de dégâts bruts par catégorie (`Cellule` en mêlée/sabre, `Chambrage` à distance), 0 dégât plat sur Poignée/Lame/Lunette/Émetteur/Lentille/Cristaux ; **Tir d'Assaut verrouillé à 2 slots** (`Lunette + Pack`, pas de Chambrage) ; **effets *On-Hit* scalés réintroduits sur les Lunettes et Émetteurs** (synergie *Tir Tactique* et *Laser*) |
| 19/11 | utilisateur | **Refonte identités & dés des armes (`WIP armes.csv`)** : retour aux dés natifs d20 (`1d6` à `2d8`), correction de l'inversion 1M/2M à distance, **toutes les armes doubles (`D`) sont `balanced`**, *Lame de guerre wookie* confirmée en épée double *Traditionnelle* (`D balanced`, `1d10`, `20/×3`), *Vibro-épée* confirmée en `2M` (`1d10`, `19-20/×2`), *Double sabre laser* à `2d8` (`20/×2`) |
| 19/11 | utilisateur | **Budgets Dons / Pouvoirs Niv. 30 (§1 & §6)** : recalibrés à **22 / 18 / 15 dons** pour **12 / 16 / 24 pouvoirs** (Consulaire ramené de 31 à 24 pouvoirs pour supprimer les fillers de fin de jeu) ; arbres conservés en 3 rangs marquants (pas de découpage massif), identités protégées par le gating Classe / Prestige sur les Rangs II–III |
| 19/11 | utilisateur | **Gating Classe / Prestige & renommage armures (§6 & §8.B)** : *Blindage de Combat* → **Armure Tactique**, *Seconde Peau* → **Esquive Ballistique** ; matrice de prérequis actée sur Spé d'arme, Postures, Armures, Métamagie et Spé Carac (paliers Niv. 1/8/15+, libres de classe) ; **Compagnons** reportés à un arbitrage par classe dans un second temps |
| 19/11 | utilisateur | **Compagnons (§6)** : gating réglé par classe (non-Jedi `SOL/SCT/SCD/TEC/DRC` accèdent aux Rangs III pertinents au Niv. 15+ via `minattackbonus = 15`) + **2 exceptions level-up uniquement** : **Kreia Niv. 15+** = Maître Jedi (toute la Métamagie), **Visas Niv. 15+** = Assassin Sith (dons sélectionnables d'Assassin). Implémentation propre via don prérequis caché (`MOD_PRESTIGE_MAGE` / `MOD_PRESTIGE_HYBRID`) accordé auto aux prestiges et scripté sur Kreia/Visas au Niv. 15 |
| 19/11 | utilisateur | **Validation simulation DPR/TTK/Survie (§3.B, §4.A, §9)** : *Vitesse de Force* (`+2` atq en Bure) confirmée équilibrée (ratios TTD/TTK identiques ~`1,5×` sur Bure/Légère/Moyenne/Lourde) ; **RD boss** ramenée de `3/7/12` à **`2/5/8`** (PV inchangés) ; **Arme Lourde (`2M`)** plafonnée à **`215/235/250 % FOR` / `165/185/200 % DEX`** ; parité distance **`150 % DEX`** en Duel 1M et **`150 %/50 %`** en `D` ; Pistolets `1M` portés à `1d10` (`1d8` poche) et Blasters à répétition `D` à `2d6` ; *Armure Tactique* validée sans buff d'arbre (bouclier `100×3` + 2 slots combinés suffisent) |
| 19/11 | utilisateur | **Refonte Chasseur de prime Gand (§5)** : **Gand I** = `+1 INT` + grenades **`+5 %` dégâts / rang total de Démolition** (viables dès Péragus) ; **Gand II** = `+2 INT` + attaque & dégâts distance DEX/INT ; **Gand III** = `+3 INT` + rayon grenades `4 m → 6 m`, perce *Esquive Totale* et `50 %` de non-consommation (100 % scripté dans `k_sup_grenade.nss`) |
| 19/11 | utilisateur | **Servante, Immunité & Craft** : *Prémonition du combat* (récompense Echani) remplacé par **`+10 %` d'esquive en mêlée** ; **aucun cap global d'immunité** (révisable selon retours joueurs) ; **toutes les armes de base non-laser craftables** à l'établi |
| 19/11 | utilisateur | **Paliers de niveau du Craft (`Craft.csv` / `itemcreate.2da`)** : verrou par niveau joueur acté à **`Mk I = Niv. 1 / Mk II = Niv. 10 / Mk III = Niv. 15 / Mk IV-T5 = Niv. 20`** (`1 / 10 / 18` sur lignées 3 tiers) ; 18 armes de base non-laser manquantes + 24 upgrades doubles d'armures intermédiaires ajoutées dans `Craft.csv` |
| 19/11 | utilisateur | **Refonte *Camouflage par la Force* (`Spé Pouvoirs.csv`)** : autorisé jusqu'à Armure moyenne · **L1** : furtivité sans ceinture + Course furtive auto + `+4` Discrétion · **L2** : `+8` Discrétion + embuscade `+2d6` et Stun 1t (`DD 10 + Niv + Carac`) · **L3** : `+12` Discrétion + chaque kill donne prochain coup critique confirmé (dans les 2 rounds) et `+25 %` esquive pendant 2 rounds (non cumulable, réinitialisable) |
| 20/11 | utilisateur | **Passe complète Pouvoirs (`Spé Pouvoirs.csv`)** : aucun cap de dés en L3 ; *Tempête* `1d6/Niv` sans drain PF passée en jet de **Réflexes** (cohérence d20 + Esquive Totale native) ; *Mise à mort* `1d8/Niv` + stun (suppression du 50 % PV max) ; *Lancer de sabre* `1d4/Niv` + Renversement **Vigueur** en L1 / 3 cibles + ignore RD en L2 ; *Peste* sans DD 100 (`-6` / `-3` si Vig) ; *Écrasement* `1d6/Niv` (Vig ½ + annule) ; *Barrière* `3/6/10`, *Résist. Énergie* `4/8/12` + Poison, *Talent* `+2/+3/+4` ; buffs de *Cri, Absorption de Force, Corps de Force, Parade/Renvoi, Confusion* et validation des 4 `(WIP)` |
| 21/11 | utilisateur | **Refonte des Ultimes de Prestige & Alignement (`Spé Pouvoirs.csv`, adossée à la philosophie de Kreia)** : uniformisation de tous les pouvoirs de prestige en **L3 max (niv. 1/5/9 de prestige)** · *Stigmate de Force* (ex *Fureur Sith*, Maraudeur, Lourde, 30 s) = `+2/+4/+6` FOR & DEX, immunité Stase/Paralysie, **`+1 atq/rd` dès L1**, `-5 %` PV max/rd (arrêt ≤ 25 % PV) · *Cicatrice de Force* (nouveau, Maître d'armes, Lourde, 30 s) = `+2/+4/+6 %` PV max/rd + `+1/+2/+3` saves + immunités mentales · *Spectre de la Force* (ex *Camouflage par la Force*, exclusif Assassin Sith) · *Affranchi de la Force* (nouveau passif, Jedi protecteur, Lourde) = `+1` / 8 rangs combinés sur 4 paires de compétences (plafond `+3/+5/+7`) + L2 `+25 %` objets profanes + L3 SR passive `15 + Niv` · *Déchirure de la Force* (ex *Annihilation de l'opposition*, Seigneur Sith, Lourde, 45 s) = `-2/-4/-6` Atq/Saves/CA en zone 15 m (Vol annule) · *Écho des Liens* (ex *Inspiration des disciples*, Maître Jedi, Lourde) = partage des buffs personnels 30/45/60 s (1 allié → groupe → groupe + soins, exploit Kreia conservé) · *Grâce du côté Lumineux* (`Armure moyenne`, *Vitesse* plafonnée `+1 atq/rd` en armure) & *Écrasement de Force* (`Armure légère`, `1d8/Niv` dégâts purs + immo 6 s) |
| 21/11 | utilisateur | **Grille des coûts en PF évolutifs par rang (`Spé Pouvoirs.csv`, colonne `Coût PF (L1/L2/L3)`)** : suppression des coûts plats/dégressifs vanilla (`Tempête` `15/30/50`, `Insanité` `15/25/45`, `Stase` `15/30/50`, `Soins` `20/35/50`, `Résist. Énergie` `15/25/40`, `Vitesse`/`Talent` `15/30/45`, `Grâce` `50`, `Écrasement` `60`, ultimes prestige `20/30/40` martiaux & `25/35/45` mages) ; calibrée sur les réserves L25 (`200 / 300 / 500 PF`) et rend la pénalité d'alignement opposé réellement dissuasive |
| 21/11 | utilisateur | **Rééquilibrage DS/LS & sauvegardes de 4 pouvoirs classiques (`Spé Pouvoirs.csv`)** : *Terreur/Horreur/Insanité* (`Légère`, `15/25/45 PF`) devient DoT mental (`Niv` dég/rd) + `-4/-6/-8 Atq` sans perte d'action (`24 s` échec / `6 s` réussite Vol) · *Champ de stase* (`Robe`, `10 m`) porté à `36 s` max avec jet de Vigueur chaque round à DD `-3/rd` · *Vague de Force* (`Moyenne`) transformé en Tourbillon AoE `6 m / 12 s` (`1/3 Niv / 2 s`, Réf réussie = ½ dégâts immédiats) · *Absorption de vie / Champ de mort / Festin de mort* (`Robe`, `20/40/55 PF`) passé à `1d3/Niv` (100 % dégâts = soin) avec nouveau L3 **Festin de mort** (excédent de soin → `EffectTemporaryHitpoints` pendant `24 s`, non cumulable, zéro conflit bouclier) |
