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

**Conclusion design :** KotOR 2 a hérité de la CA de D&D 3.0 *sans* les dons de spécialisation de D&D 5e *ni* la RD du JdR SW. L'overhaul restaure les deux leviers.

### B. Diagnostic de *Condition physique* (consensus communauté)

*Filler feat* typique en vanilla ; sa valeur remonte dans l'overhaul (DD des pouvoirs de boss renforcés, *Esquive Totale* qui rend chaque point de Réflexes rentable) → rang III révisé (§8.D).

### C. Notes d'implémentation (§8)

- **RD native & arbres** : hook fin de round de `k_ai_master.nss` lisant `GetBaseItemType()` de l'armure (lignes baseitems 38–43), parcours anti-cumul d'effets (README §3.A).
- **Effets validés** : `EffectDamageReduction`, `EffectACIncrease`, `EffectSavingThrowIncrease`, `EffectImmunity` (`KNOCKDOWN = 28`, `STUN = 12`).
- **`forbiditemmask` — mapping confirmé (09/11)** : `0x01` = AC4 (38, légère) · `0x02` = AC5 (39) · `0x04` = AC6 (40, interm.) · `0x08` = AC7 (41) · `0x10` = AC8 (42, lourde) · `0x20` = AC9 (43). Un pouvoir est bloqué si `(masque ET bits de l'armure portée) ≠ 0`.
- **Les bits viennent de l'identité de ligne, pas des stats** (constaté 14/11) : les lignes 98 (*Combinaison ubese*, `baseac 5`) et 102 (*Zeison Sha*) échappent à **tous** les masques alors que la ligne 39 a le même `baseac` — preuve que les bits dérivent de l'appartenance au bloc 38–43.
- **Exception « Force-friendly »** : lignes 98/102 + robes 35-37 échappent à tous les masques — assumées rares et universelles (le prix Matukai, abandonné, aurait été des lignes lourdes sans bits ; design rejeté 14/11).
- **`requireitemmask`** (inverse) : permet des pouvoirs exclusifs aux armures — piste de compensation Juggernaut.
- **`feat.2da`** : *Condition physique* = lignes 13/21/22 ; *Esquive* = ligne 125.

### D. Budget détaillé par build (§6/§8) — *ancienne structure, à réarbitrer (voir §9-J)*

Gardé pour mémoire : Gardien Juggernaut / robe, Sentinelle, Consulaire — 15 dons socle + bonus. La refonte postures/familles/carac (13–15/11) rend cette récomposition obsolète sans en changer les totaux (21/16/13).

---

## 2. Options techniques validées (à activer lors des chantiers)

- **Coût de PF dynamique à l'impact** : `GetCurrentForcePoints`, `EffectDamageForcePoints`/`EffectHealForcePoints`, `GetSpellBaseForcePointCost` (précédent vanilla : remboursement Consulaire, `k_inc_force.nss` ~5950). Contraintes : l'UI n'affiche que le coût 2DA (documenter dans `dialog.tlk`) ; garder un coût de base non nul pour l'IA.
- **Réserve de PF — formule moteur (extraite de `classes.2da` le 14/11)** : `PF max = Σ par niveau (forcedie + mod. SAG + mod. CHA)` avec forcedie : Gardien 4 · Sentinelle 6 · Consulaire 8 · Maître d'Armes/Maraudeur 6 · Veilleur/Assassin 8 · Maître Jedi/Seigneur Sith 10 (0 pour classes non-Jedi). Niveau 30 : Consulaire ~540–900 PF selon SAG/CHA ; Gardien ~180–270 PF.
- **Régénération / jauges** : `IsStealthed` (nwscript l. 5808), `GetMaxForcePoints`, `EffectRegenerate`, `EffectMissChance` (l. 4324), `GetTotalDamageDealt`, `GiveXPToCreature`/`SetXP`, `EffectSkillIncrease`, `EffectDamageShield` — tous vérifiés dans `nwscript.nss`.
- **`requireitemmask`** : pouvoirs exclusifs à un type d'armure (§1.C).

---

## 3. Contrat mathématique détaillé (décisions §9)

Détail des hypothèses (attaques/round, dégâts bruts et nets après RD, précision, DPR sbires) :

| Phase & Boss | Archétype | Atq/round | Bruts/coup | Nets après RD | Précision | **DPR net boss** | **Durée** |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **EARLY (Niv. 8)** 120 PV, CA 20, RD 3 | Gatling/Lame Double · 2 Pistolets/2 Armes · Fusil/1M | 3 · 3 · 2 | 13 · 9,5 · 13 | 10 · 6,5 · 13 | 55 % · 60 % · 75 % | 16,5 · 11,7 · 19,5 | 7,2 · 6–10 · 6,1 |
| **MID (Niv. 16)** 280 PV, CA 29, RD 7 | idem | 5/4 · 4 · 3 | 20 · 16 · 23 | 13 · 9 · 23 | 60 % · 70 % · 85 % | 39,0 · 25,2 · 58,6 | 7,2 · 6–11 · 4,8 |
| **LATE (Niv. 26)** 650 PV, CA 44, RD 12 | idem | 6/5 · 5 · 3–4 | 28 · 25 · 40–48 | 16 · 13 · 40–48 | 60 % · 70 % · 85 % | 57,6 · 45,5 · 122–128 | 11,2 · 7–14 · 5,1 |

**[À remapper 15/11]** : colonnes issues de l'ancien « triangle » (abrogé) — à réexprimer en postures × familles dans `k2balance.py` ; cibles DPR/TTK inchangées. *Ambidextrie : l'Attaque Sournoise sur cible contrôlée double le DPR net (devient +2d6 pour tous via Tir Assassin II — arbitrage éventuel).*

---

## 4. Références de données

- **CSV de référence (couche utilisateur)** : *Style de combat*, *Spécialisation d'arme*, *spé carac*, *WIP Feats* (agrégateur), *WIP armes*, *WIP Améliorations* (226 pièces), *WIP Spé Pouvoirs*, *WIP spé Armure*.
- **Données extraites** : `datas_kotor/` (`equipement_*.md`, `loot_*.md`, `dons_kotor2.md`, `pouvoirs_kotor2.md`, `ennemis_*.md`, `modeles_mathematiques_equilibrage.md`, `armes_kotor2.md`) ; cache `itemdb/` (items.json, loot.json) via `tools/extract_items.py`.
- **JdR Star Wars d20** : `datas_jdr_SW/`. **Idées brutes** : `idée mods.md`.

---

## 5. Architecture Moteur — Moddable vs Hardcodé (Odyssey Engine)

### ❌ A. Codé en dur dans `swkotor2.exe`
1. **Effets des dons passifs vanilla** (Duel `+Atq/CA`, TWF `-6/-10`, Spé `+2`, Robustesse…) — contournables par dons neufs + effets scriptés (solution actée 15/11 : les dons Duel/Ambidextrie sont **recréés from scratch**, les vanilla sont supprimés de la sélection).
2. **Formules des attaques actives** (Déluge, Attaque en puissance, Critique, Décharge, Sniper).
3. **Multiplicateur de Force par configuration** (1,0×/0,5×/1,5× par slot ; armes doubles) — tout écart s'injecte en différentiel via `k_ai_master.nss`.
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
2. **Passifs au hook 1003** (fin de round, `k_ai_master.nss`) : lecture des dons/caracs/équipement, bonus différenciels (attaque, dégâts, CA, RD, attaques bonus via `EffectModifyAttacks`).
3. **On-hit au hook 1006** (côté victime) : `GetLastDamager()`, arme via `GetItemInSlot`, procs maison (Spé d'arme), critique furtif §10, transfusion Kraith (heartbeat), punitions Matukai.
4. **Effets vérifiés mais sémantique inconnue** : plafond éventuel des bonus de CA de même type (esquive +20 héritée NWN ?) — impacte le cumul Nomi/Matukai × Précognition guerrière (test « plafond CA »).
5. **Armes doubles en main gauche** : jamais possible en vanilla (`equipableslots 0x10`) — comportement (nombre d'attaques, multiplicateurs) totalement inconnu → **test T1** (Gamoréen II) ; gating des éventuelles variantes 1M → **test T2**. Fait établi : les repeating ne sont pas des armes doubles (`weaponwield 6 ≠ 3`).
6. **Effets inexistants** : pas de `EffectDamageReductionDecrease` (→ variante « RD -3 » de la Spé Primitive écartée) ; pas de détection de critique ; pas d'interception du refus de lancement faute de PF (→ Kraith L2 en conversion heartbeat, pas en « puiser dans les PV »).

---

## 6. Diagnostic des Archétypes Vanilla (Niv. 28–30)

Analyse comparative historique (pré-overhaul) :

| Archétype / Classe | Total Dons | Budget Vanilla | Total Pouvoirs | Budget Pouvoirs |
| :--- | :---: | :---: | :---: | :---: |
| **Gunslinger 2 Blasters** (Voyou 15) | 17–18 | Équilibré | 0 (ou 15) | 0 (ou 5 arbres) |
| **Maraudeur Sith (2 Sabres)** | 17–18 | Équilibré | 29–31 | +16 en trop |
| **Jedi / Sith Mage** (Consulaire 15) | 12–13 | +4 à +6 inutiles | 38–40 | +18 à +24 en trop |
| **Sentinelle / Veilleur** | 15–16 | +6 sans option martiale | 29–31 | +14 en trop |

**Constats** : le Consulaire croule sous ~40 pouvoirs sans dons pour les payer ; le Gardien perd son identité martiale sous ~30 pouvoirs ; la Sentinelle n'a pas accès aux dons Supérieurs.

---

## 7. Historique : la branche Mains nues (supprimée le 14/11)

L'arbre *Arts Martiaux / Arts Mutaki / Arts Martiaux Supérieurs* (spécification initiale : Atq & Dégâts = jet + (DEX ou FOR) + SAG, plage 19-20 → 17-20, Tourbillon de Force sur critique — acté §6/§7 d'origine) a été **supprimé** : une seule série de dons par caractéristique étant retenue (§5), et l'identité mains nues étant désormais portée par la posture Duel + la chaîne vanilla + la Spé carac Matukai. Le rang III Matukai a connu trois itérations (Vague de Force sur critique → Tourbillon à synergie Impact explicite, rejetée car « les synergies doivent être trouvées, pas décrites » → punitions sur sauvegarde ratée/attaque manquée, actée 15/11).

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
| 13/11 | utilisateur | Matukai L1 : la SAG **s'ajoute** à l'attaque ; L2/L3 SAG→CA cumulable avec Précognition |
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
