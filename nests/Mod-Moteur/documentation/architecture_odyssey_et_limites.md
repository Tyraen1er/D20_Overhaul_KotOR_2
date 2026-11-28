# Architecture Moteur Odyssey — Moddable vs Hardcodé & Notes d'Implémentation

> Complète [`pieges_pykotor_et_odyssey.md`](pieges_pykotor_et_odyssey.md) (qui couvre les 5 patchs `.venv` de `pykotor` et les pièges d'exécution en jeu).

## 1. Codé en dur dans `swkotor2.exe` (invariants & contournements)

1. **Effets des dons passifs vanilla** (Duel, TWF, Weapon Focus/Spec, Finesse, Robustesse…) : contournés en masquant les dons vanilla (`allclassescanuse = "0"`, `*_list = "4"`) et en recréant les dons custom (`ID 245+`) avec effets scriptés.
2. **Formules des attaques actives** (Déluge, Attaque en puissance, Coup critique, Décharge, Tir rapide, Sniper) : non modifiables.
3. **Multiplicateur de caractéristique par configuration** : en mêlée `1,0× / 0,5× / 1,5× FOR` ; à distance **`0×` en vanilla**. Tout écart (`150 % DEX` en `1M`/`2M`, `100 %/50 % DEX` en Ambidextrie, `150 %/50 % DEX` en `HC`, `165/185/200 % DEX` ou `215/235/250 % FOR` via *Arme Lourde*, `INT` via *Gand II*) s'injecte en différentiel dans `Ov_RefreshPassives()` via `k_def_*` / `k_hen_*`.
4. **Pipeline d'attaque & absence d'indicateur de critique** : aucune API pour forcer un critique ni détecter dans `OnDamage` (`1006`) si un coup était critique → procs des Spé d'arme simulés à `plage/20`, embuscade furtive simulée par `SupernaturalEffect(EffectAttackIncrease(50))` (`6,0 s`) + `EffectDamage(GetTotalDamageDealt(), DAMAGE_TYPE_PIERCING)` dans `Ov_OnDamageHook`.
5. **Aucun événement « attaque manquée »** (`hooks 1001–1012`) : la punition *Matukai III* repose sur le différentiel `Σ1005 (OnAttacked) − Σ1006 (OnDamage)` (test **T3** à confirmer en jeu par VFX/log).
6. **Sauvegardes internes au moteur** (`iprp_onhit` natifs) : aucun hook — les punitions sur sauvegarde réussie (*Matukai II*) ne couvrent que les sauvegardes scriptées (pouvoirs dans `k_inc_force.nss`, grenades dans `k_sup_grenade.nss`).
7. **Effets NWScript inexistants** : pas de `EffectDamageReductionDecrease` ; pas d'interception du lancement d'un pouvoir faute de PF (→ *Krayt II* implémenté par conversion périodique en heartbeat) ; pas de `RemoveFeat` / `RemoveSpell` / baisse de niveau (→ respec externalisé dans le nid `Utilitaire`).
8. **Limite d'emplacements à l'établi (`swkotor2.exe`)** : table `4 × 6` codée en dur (`0x4ca630`, `0x5a70e8`) — Sabres = 6 slots (`BTN_UPGRADE31..36_LS`), Distance/Mêlée = 3 slots, Armures = **2 slots max** (`Slot 0 = upgradetype 10` Sur-couche, `Slot 1 = upgradetype 11` Sous-couche ; `BTN_UPGRADE33` masqué à `0x4cb070`).

## 2. Leviers `.2da` validés

- **`UpgradeLevel` (`0x4cbcd0`)** : le moteur vérifie `upgrade.UpgradeLevel <= item.UpgradeLevel`.
  - *Armures* : Bure `0` · Légère `1` (15 sous-couches) · Lourde `2` (30 sous-couches) · Intermédiaire `6` (30 sous-couches + 30 sur-couches exclusives calées à `ulvl 6`).
  - *Armes* : Mêlée (`Poignée 1 < Lame 2 < Cellule 3`) · Distance (`Lunette 1 < Pack 2 < Chambrage 3`).
- **`forbiditemmask` & `itemtype`** : `0x01` = AC4 (38), `0x02` = AC5 (39), `0x04` = AC6 (40), `0x08` = AC7 (41), `0x10` = AC8 (42), `0x20` = AC9 (43). C'est `itemtype` (`31`/`32` = légère, `38` = bure) qui pilote le grisé natif des pouvoirs indépendamment de `bodyvar` (d'où `Armor_Zeison_Sha` ligne `102` à `itemtype = 31`). `requireitemmask` existe pour des pouvoirs exclusifs aux armures.
- **`feat.2da` & `classes.2da`** :
  - `exclusion` ne bloque **pas** la sélection au level-up → mutualité des 6 Spé Carac gérée par garde-fou scripté `LocalNumber 22`.
  - Lignes utiles : *Condition physique* `13/21/22` · *Esquive Totale* `125` · *Course furtive* `197` · *Camouflage personnel* `201` (seul don de furtivité actif sous armure, contrairement à `97/141/142`).
  - Formule PF max (`classes.2da`) : `Σ (forcedie + mod. SAG + mod. CHA)` avec `forcedie` = Gardien `4`, Sentinelle/Maître d'Armes/Maraudeur `6`, Consulaire/Protecteur/Assassin `8`, Maître Jedi/Seigneur Sith `10`.
- **`baseitems.2da` (`104..123`, Gamorréen II)** : `equipableslots = 0x00030` + `weaponwield = 2` (mêlée) ou `4` (distance, jamais `5`) + `weaponsize = 3` + `reqfeat0 = MOD_GAMORREAN_2` (complété par `Use_Limitation_Feat` prop `57` sur les 69 jumeaux `ov1m_*.uti`). Les repeating ont `weaponwield = 6 ≠ 3`.
- **`forceshields.2da` & `iprp_resistcost.2da`** : lignes dupliquées `amount ×2 / ×3` dans `forceshields.2da` pour *Armure Tactique II–III* (`k_sup_bands.nss`) ; lignes `7..11` ajoutées à `iprp_resistcost.2da` pour les RD exactes `2/3/4/6/12/-`.

## 3. Leviers scripts & ennemis

- **Wrappers passifs/dégâts** : `k_def_heartbt01`, `k_hen_heartbt01`, `k_def_attacked01`, `k_hen_attacked01`, `k_def_damage01`, `k_hen_damage01` (jamais de recompilation de `k_ai_master.ncs`). Tous les bonus de CA custom additionnés dans **un seul `EffectACIncrease(nTotalAC, AC_DODGE_BONUS)`**.
- **Fonctions NWScript vérifiées** : `GetCurrentForcePoints`, `EffectDamageForcePoints`/`EffectHealForcePoints`, `GetSpellBaseForcePointCost`, `IsStealthed`, `GetMaxForcePoints`, `EffectRegenerate`, `EffectMissChance(int)` (1 seul paramètre en K2), `EffectDamageImmunityIncrease`, `GetTotalDamageDealt`, `GiveXPToCreature`, `EffectSkillIncrease`, `EffectDamageShield`.
- **Ennemis (`build_enemies.py` & `ov_inc_core.nss`)** : peaux marqueurs (`ov_hide_soldier`, `ov_hide_mando_*`, `ov_hide_beast_*`, `ov_hide_assn`, Sith) + scaling continu en script sur `Niv. PJ` + équipement réel (armures/bures/boucliers) dans les `.utc` + `autobalance.2da`.
