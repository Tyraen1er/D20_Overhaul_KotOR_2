# KotOR 2 Modding Workspace — Guide & Pièges Techniques (Pour Agents IA & Développeurs)

Ce dépôt contient l'environnement de développement CLI/Python pour créer des mods **Star Wars: Knights of the Old Republic II (TSL)**.
Ce document répertorie l'architecture de l'espace de travail ainsi que les **découvertes critiques et correctifs appliqués à `pykotor`** afin qu'aucun agent ne reproduise les bugs rencontrés lors de la mise en place.

---

## 0. Hiérarchie des Fichiers & Politique de Modification

> **Règle de conduite pour tous les agents** — qui possède quoi, et dans quel ordre toucher les fichiers.

### A. Les CSV = la couche utilisateur (parcimonie obligatoire)
* Les fichiers `Kotor 2 - rééquilibrage - *.csv` sont **ce qui est le plus proche de l'utilisateur** : ils constituent la référence de ses décisions de game design (armes, styles de combat, spécialisations, dons de caractéristique, pouvoirs...).
* **N'y toucher qu'avec parcimonie, et uniquement en rapport direct avec l'utilisateur** (report d'une décision qu'il vient de valider ou de prendre dans la conversation). Ne jamais y reporter un changement de sa propre initiative.
* Le fichier **`Kotor 2 - rééquilibrage - WIP Feats.csv`** est un fichier d'**agrégation** : il regroupe, pour les dons vanilla et moddés, les informations des autres CSV. **Depuis le 15/11/2026, il est maintenu à la main** (structure restructurée par l'utilisateur : colonne Source supprimée, colonne « Détail technique » ajoutée) — [`tools/build_feats_csv.py`](tools/build_feats_csv.py) n'est plus la source de vérité (bootstrap historique).

### B. Les fichiers des agents : `decisions_finales.md` & `decisions_annexes.md`
* Ces deux fichiers appartiennent aux agents :
  * **`decisions_finales.md`** = le contrat de game design (synthèse condensée des décisions actées) ;
  * **`decisions_annexes.md`** = justifications, recherche, diagnostics et **détails techniques**.
* On peut y consigner librement les détails d'implémentation et la faisabilité vérifiée, ainsi que toute décision actée **dans les CSV ou à travers la discussion avec l'utilisateur**.

### C. Ordre de propagation d'une décision
1. Décision prise dans la conversation ou inscrite dans un CSV (référence utilisateur) ;
2. Report dans `decisions_finales.md` (synthèse) et/ou `decisions_annexes.md` (détails techniques) ;
3. Si elle concerne les dons : édition directe du CSV d'agrégation `WIP Feats.csv` (maintenu à la main depuis le 15/11/2026).

---

## 1. Environnement & Chemins Clés

* **Installation du jeu (Steam) :** `C:\Program Files (x86)\Steam\steamapps\common\Knights of the Old Republic II`
  * Contient déjà un dossier `Override/` peuplé (TSLRCM / mods graphiques). **Toujours vérifier si un fichier `.2da` ou `.ncs` existe déjà dans `Override/` avant d'extraire la version vanilla de `chitin.key`.**
  * Utiliser `Installation.resource(resname, restype)` de `pykotor` (qui respecte l'ordre de priorité `Override` > `Modules` > `chitin.key`).
* **Environnement Python local :** `.venv\Scripts\python.exe` (Python 3.14 + `pykotor 2.3.12` patché).
* **Outil CLI maison :** [`tools/k2mod.py`](tools/k2mod.py)
  * Compiler un script `.nss` en `.ncs` :
    ```powershell
    .\.venv\Scripts\python.exe tools\k2mod.py compile chemin\vers\script.nss -o chemin\vers\script.ncs
    ```
  * Extraire une ressource du jeu (en respectant la priorité `Override`) :
    ```powershell
    .\.venv\Scripts\python.exe tools\k2mod.py extract <resname> <ext> -o <output_path>
    ```
* **Checker de DPR (équilibrage) :** [`tools/dpr_check.py`](tools/dpr_check.py) + données [`tools/dpr_data.json`](tools/dpr_data.json)
  * Simule le DPR d'un **build défini par ses dons** contre les boss étalons du contrat mathématique (§9), en **choisissant automatiquement la meilleure arme / mode de port (1M, 2M, 2 armes, double) / arme de main gauche / attaque active / améliorations** — la meilleure arme change donc selon les dons pris (spé de famille, style, crit…).
    ```powershell
    .\.venv\Scripts\python.exe tools\dpr_check.py --feats "Duel 3,Spécialisation Arme Laser 3,Coup critique 3"
    .\.venv\Scripts\python.exe tools\dpr_check.py --feats "Ambidextrie 3,Tir d'Assaut 3,Tir rapide 3" --char sentinelle
    ```
  * Utile : `--armor sans|legere|moyenne|lourde` + `--buffs "Vitesse 3,Talent de Force 3"` — l'armure portée ne donne **aucun bonus simulé** mais **gâte les pouvoirs de Force** (Vitesse interdite sous armure, Talent ≤ légère, Illumination ≤ moyenne qui relance Vitesse+Talent au rang max, Fureur = fallback vanilla toute armure) ; `--upgrades cap|vanilla|none` (plafonds actés +2/+5/+10 ou meilleurs items actuels), `--speed` (override manuel), `--sneak-dice/--sneak-uptime`, `--enemy PV,CA,RD`, `--weapon <filtre>`, `--top N`, `--list-feats`, `--list-weapons`, `--md`.
  * **Toutes les valeurs d'équilibrage vivent dans `tools/dpr_data.json`** (armes, dons, boss, plafonds) : c'est ce fichier qu'on édite pour tester des ajustements — jamais le moteur. Les pools d'améliorations se régénèrent depuis le CSV utilisateur via `--reingest-upgrades`.
  * Conventions : toucher `(21-(CA-Atq))/20` borné 5-95 %, critique confirmé (≈ proba de toucher), RD du boss soustraite par coup après multiplication critique, Vitesse = +1/+2 attaques main directrice (auto par phase).
* **Ressources de référence extraites (`_reference/`) :**
  * `_reference/scripts/` : Contient les 638 scripts `.nss` du jeu (`nwscript.nss`, `k_inc_force.nss`, `k_ai_master.nss`, `k_sp1_generic.nss`, etc.).
  * `_reference/2da/` : Contient les fichiers `.2da` et `.csv` de référence (`feat.2da`, `spells.2da`, `baseitems.2da`, `iprp_damagecost.2da`, `iprp_onhit.2da`).

---

## 2. Bugs Critiques de `pykotor` (v2.3.12) Identifiés et Corrigés dans `.venv`

> **⚠️ ATTENTION :** Si l'environnement virtuel `.venv` est recréé ou si `pykotor` est réinstallé via `pip`, **ces 4 bugs réapparaîtront** et casseront silencieusement les fichiers `.2da` ou les scripts `.ncs` en jeu. Vérifiez toujours qu'ils sont bien patchés dans `.venv\Lib\site-packages\pykotor\`.

### Bug #1 : Ordre des arguments inversé dans les appels moteur (`ACTION`) du compilateur NCS
* **Fichier :** `.venv\Lib\site-packages\pykotor\resource\formats\ncs\compiler\classes.py` (`EngineCallExpression.compile`, ~ligne 1341)
* **Symptôme en jeu :** Les scripts compilés cassent complètement le jeu (impossible d'interagir avec le loot au sol, IA figée, fonctions comme `GetHasFeat(245, oTarget)` ou `ExecuteScript("k_ai_master", OBJECT_SELF, 2001)` qui reçoivent leurs paramètres à l'envers).
* **Cause :** Dans le bytecode NWScript de l'Odyssey Engine, les arguments d'une instruction `ACTION` doivent être empilés **de droite à gauche** (du dernier paramètre au premier : `range(len(self._args) - 1, -1, -1)`). `pykotor` les empilait de gauche à droite (`range(len(self._args))`).
* **Correctif appliqué :** Boucle remplacée par `for i in range(len(self._args) - 1, -1, -1):`.

### Bug #2 : Prologue `JSR` manquant à l'octet 0 quand un script contient des variables globales
* **Fichier :** `.venv\Lib\site-packages\pykotor\resource\formats\ncs\compiler\classes.py` (`CodeRoot.compile`, ~ligne 393)
* **Symptôme en jeu :** Tout script ayant des variables globales (ou incluant `k_inc_switch.nss`, `k_inc_generic.nss`, `k_inc_force.nss`, comme `k_ai_master.ncs` ou `k_sp1_generic.ncs`) est silencieusement ignoré ou rejeté par la VM de KotOR 2.
* **Cause :** La VM de KotOR exige que l'instruction `0` d'un fichier `.ncs` soit **toujours** un `JSR` suivi à l'instruction `1` d'un `RETN`. Lorsqu'il y a des variables globales, l'instruction `0` doit faire `JSR` vers la routine d'initialisation des globales (instruction `2`), qui se termine par :
  ```text
  SAVEBP
  JSR -> main
  RESTOREBP
  MOVSP [-taille_globales]
  RETN
  ```
  Par défaut, `pykotor` plaçait directement `RSADDI` à l'instruction `0` sans `JSR` initial et oubliait `RESTOREBP` / `MOVSP`.
* **Correctif appliqué :** `CodeRoot.compile` génère désormais le prologue/épilogue complet exact attendu par l'Odyssey Engine.

### Bug #3 : Erreur de syntaxe sur les boucles `for ( ; condition; inc )` d'Obsidian
* **Fichier :** `.venv\Lib\site-packages\pykotor\resource\formats\ncs\compiler\parser.py` (`p_for_loop`, ~ligne 310)
* **Symptôme :** Échec de compilation (`Syntax error at line 1626, token=';'`) lorsqu'on compile un script qui inclut `k_inc_force.nss`.
* **Cause :** Les développeurs d'Obsidian ont écrit `int index = 0; for ( ; index < 3; ++index )` dans `k_inc_force.nss`. La grammaire Yacc/PLY de `pykotor` n'acceptait pas d'expression d'initialisation vide dans `for (...)`.
* **Correctif appliqué :** Ajout de la règle `| FOR_CONTROL '(' ';' expression ';' expression ')' '{' code_block '}'` dans `parser.py`.

### Bug #4 : Cellules vides lors de la lecture des fichiers binaires `.2da` (`V2.b`)
* **Fichier :** `.venv\Lib\site-packages\pykotor\resource\formats\twoda\io_twoda.py` (`TwoDABinaryReader.load`, ~ligne 165)
* **Symptôme :** `read_2da()` ou `pykotorcli 2da2csv` renvoie un tableau avec le bon nombre de lignes et de colonnes, mais **toutes les cellules sont vides (`""`)**.
* **Cause :** Le lecteur Kaitai (`_load_twoda_from_kaitai`) échoue silencieusement à lire les chaînes de caractères des offsets sans lever d'exception, empêchant le fallback vers `_load_twoda_legacy`.
* **Correctif appliqué :** `TwoDABinaryReader.load` utilise désormais directement `_load_twoda_legacy(BinaryReader.from_bytes(data, 0))`, qui lit parfaitement 100 % des `.2da` de KotOR 2.

### Bug #5 : Paramètre manquant `nOpponentPazaakDeck` dans la signature de `PlayPazaak`
* **Fichier :** `.venv\Lib\site-packages\pykotor\common\scriptdefs.py` (~lignes 6321 et 12669)
* **Symptôme :** `CompileError: Type mismatch for parameter 'oOpponent' in call to 'PlayPazaak'` lors de la compilation de tout script appelant `PlayPazaak(...)`.
* **Cause :** La liste `ScriptParam` de `PlayPazaak` omettait le premier paramètre `int nOpponentPazaakDeck`, décalant tous les arguments suivants.
* **Correctif appliqué :** Ajout de `ScriptParam(DataType.INT, "nOpponentPazaakDeck", None)` en tête de liste des paramètres pour K1 et K2.

### Bug #6 : Cellules vides dans `pykotor.TwoDA` (`""` obligatoire, JAMAIS `"****"`)
* **Symptôme en jeu :** Un don ajouté dans `feat.2da` n'apparaît pas du tout dans la liste au passage de niveau (ou un prérequis est rejeté).
* **Cause :** Dans `pykotor`, une cellule vide d'un `.2da` doit être la chaîne vide **`""`** (que `write_2da` sérialise correctement en `****` au format binaire). Écrire la chaîne littérale **`"****"`** stocke les 4 caractères `"****"`, que le moteur lit comme un entier/prérequis invalide et masque la ligne.
* **Règle stricte :** Toujours initialiser les cellules vides avec **`""`** (ou cloner une ligne fonctionnelle existante) — jamais `"****"`.

### Bug #7 : Corruption des gros scripts vanilla par le compilateur NCS de `pykotor` (`k_ai_master.ncs`, `k_sp1_generic.ncs`, `k_sup_grenade.ncs`)
* **Symptôme en jeu :** Recompiler un gros script (> 15k instructions) avec le compilateur Python de `pykotor` corrompt le bytecode (`k_ai_master.ncs` gèle toute l'IA ; `k_sp1_generic.ncs` fait que les pouvoirs ne lancent plus que l'animation ; `k_sup_grenade.ncs` empêche les grenades d'exploser).
* **Solution définitive validée (23/11/2026) :** Utiliser le **vrai compilateur C++ `nwnnsscomp.exe`** présent dans `_reference/autres_mods/Content Pack-57-1-67-1616632489/tslpatchdata/nwnnsscomp.exe` (déjà intégré automatiquement dans [`tools/build_scripts.py`](tools/build_scripts.py) via dossier staging). Continuer par ailleurs à ne jamais recompiler `k_ai_master.ncs` et à passer par les petits wrappers `k_def_*` / `k_hen_*`.

### Bug #8 : `feat.2da` — Masquage (`*_list = "4"`) et Icônes réelles (crash KSE `Bioware/TPC.pm`)
* **Masquer un don (supprimé ou interdit à une classe) :** mettre **`allclassescanuse = "0"`** ET **`*_list = "4"`** (et **NON** `""`, qui laisse le don visible au level-up !). Seules les classes autorisées reçoivent `"1"`.
* **Icônes obligatoires :** toute icône inexistante (ex. `"ifeat_dueling"`) affiche un **carré gris** en jeu ET fait **crasher KSE** (`Can't use an undefined value as an ARRAY reference at Bioware/TPC.pm line 190`). Toujours utiliser un vrai nom d'icône vanilla de `feat.2da` (`if_duel01..03`, `if_2weap01..03`, `if_armprof01..03`, `if_pattack01..03`, `if_preshot01..03`, `if_jedidef01..03`, `if_finesse01/02`, `if_focalter`, `if_focmaster`, `if_foccontr`, `if_focboost`, `if_focdemo`, `if_focsense`, `if_battlemed`, `if_focaware`).

---

## 3. Règles et Pièges Spécifiques au Moteur de KotOR 2 (Odyssey Engine)

### A. Création de Dons (`feat.2da`) et Effets Passifs
1. **`feat.2da` ne gère que l'interface et la sélection :**
   * Ajouter une ligne dans `feat.2da` (et ses StrRefs de nom/description dans `dialog.tlk`) permet d'afficher le don, ses prérequis et sa disponibilité au passage de niveau (`*_list = 1`, `*_granted = -1`, `pips = 1`).
   * **Important pour la fiche de personnage :** Dans KotOR 2, la liste des dons acquis d'un personnage est filtrée par `masterfeat` et `pips`, mais aussi par les colonnes de classe (`scd_list`, `sol_list`, etc.). Copiez toujours les colonnes de base d'un don fonctionnel (ex: ligne `194` `FINESSE_MELEE_WEAPONS`) avant de modifier les champs souhaités.
2. **Où coder l'effet d'un nouveau don passif ?**
   * Les dons vanilla ont leurs effets codés en dur dans `swkotor2.exe`.
   * Pour un nouveau don (ex: ID `245`), il faut vérifier `GetHasFeat(245, oTarget)` dans un script exécuté régulièrement.
   * **Point d'entrée universel (validé 23/11 — voir Bug #7) :** Le joueur (`pc.utc`), les compagnons (`p_*.utc`) et les PNJ ont tous des petits scripts wrappers (`k_hen_heartbt01`, `k_def_heartbt01`, `k_hen_attacked01`, `k_hen_damage01`, `k_def_attacked01`, `k_def_damage01`) qui appellent `ExecuteScript("k_ai_master", OBJECT_SELF, ...)`.
   * **Toujours placer les hooks custom dans ces petits wrappers** (jamais en recompilant `k_ai_master.nss`), en laissant l'appel `ExecuteScript("k_ai_master", ...)` intact juste après.
3. **Éviter le cumul infini des bonus passifs :**
   * Avant d'appliquer un effet `DURATION_TYPE_PERMANENT` + `ExtraordinaryEffect(eLink)` dans le wrapper heartbeat, **toujours parcourir `GetFirstEffect(oTarget)` / `GetNextEffect(oTarget)`** pour vérifier si l'effet (`EFFECT_TYPE_*` avec `SUBTYPE_EXTRAORDINARY` et `DURATION_TYPE_PERMANENT`) n'est pas déjà présent sur la créature.
4. **Ne jamais supprimer de lignes vanilla dans `feat.2da` :**
   * Supprimer ou décaler des index vanilla dans `feat.2da` rend les sauvegardes existantes incompatibles. Toujours **ajouter** les nouveaux dons à la fin (`245+`) et masquer les dons retirés en mettant leurs colonnes `*_list` à `""` (vide) plutôt qu'en supprimant la ligne.

### B. Fonctionnement de `EffectDamageIncrease` vs `DAMAGE_BONUS_*`
* **Piège classique :** Dans `nwscript.nss`, le commentaire au-dessus de `EffectDamageIncrease(int nBonus, ...)` mentionne `DAMAGE_BONUS_*` (qui sont les constantes de la table `iprp_damagecost.2da` où `1..5` = `+1..+5`, `6` = `1d4`, `10` = `2d6`).
* **Réalité dans KotOR 2 :**
  * Pour `EffectDamageIncrease(nBonus, DAMAGE_TYPE_*)` (comme utilisé par Obsidian dans `k_inc_force.nss` pour *Inspire Followers*), passer un entier direct comme `10` donne directement **+10 de dégâts fixes** sur la feuille de personnage !
  * De plus, deux effets `EffectDamageIncrease` du même type de dégâts ne se cumulent pas entre eux s'ils sont appliqués séparément (seul le plus élevé est retenu sur la feuille de personnage). Pour donner `+10`, il faut donc passer directement `EffectDamageIncrease(10, DAMAGE_TYPE_UNIVERSAL)`.

### C. Scripts `.nss` vs `.ncs` et Fichiers `#include`
* Le jeu n'exécute **que** les fichiers compilés `.ncs` présents dans `Override/` (ou dans les modules `.mod`/`.rim`).
* Les fichiers `k_inc_*.nss` (comme `k_inc_force.nss` ou `k_inc_combat.nss`) sont des bibliothèques (`#include`) sans fonction `main()`. Si vous modifiez `k_inc_force.nss` (par exemple pour rééquilibrer le pouvoir de Vitesse), vous devez compiler **`k_sp1_generic.nss` ➔ `k_sp1_generic.ncs`** et placer `k_sp1_generic.ncs` dans `Override/`.
* ⚠️ Pièges NWScript K2 (constatés le 13/11/2026) : **`GetLocalInt`/`SetLocalInt` n'existent pas** — utiliser `Get/SetLocalNumber(oObject, nIndex)` (index 12 à 28, valeur 0-255 ; idem `Get/SetLocalBoolean`). **Pendant le prologue, `GetFirstPC()` = T3-M4, pas l'Exilé** — distinguer avec `GetIsPlayerMadeCharacter()` (commande 876) ; un script qui déclenche une action intrusive sur `GetFirstPC()` pendant la cinématique du prologue fige le module (écran noir, audio en fond). `GrantFeat(nFeat, oCreature)` (commande 786, ajout K2) octroie un don par script sans tenir compte des prérequis ; pas d'événement `OnLevelUp` (polling heartbeat). La séquence d'écrans de la création de perso et ses validations sont codées en dur dans l'exe (non moddables ; pas de mécanisme de « liste de dons bonus » en K2 — colonnes `*_bon` de `featgain.2da` inutilisées).

### D. Vérifications Moteur Actées en Jeu (Jalon 0 — 23/11/2026)
* **`feat.2da` colonne `exclusion` = KO pour les dons sélectionnables :** mettre le même bit `exclusion` (ex. `0x02`) sur deux dons **n'empêche pas** de prendre les deux au level-up. La mutualité des 6 arbres de Spé Carac doit donc passer par un **garde-fou scripté** (premier arbre acquis enregistré en `LocalNumber`, les autres ignorés).
* **`EffectACIncrease` ne se cumule PAS entre effets séparés :** même en utilisant des types différents (`AC_DODGE_BONUS`, `AC_DEFLECTION_BONUS`, `AC_NATURAL_BONUS`), KotOR 2 ne conserve que la valeur la plus élevée (`+5`, pas `+15`). **Règle obligatoire :** additionner tous les bonus de CA custom (Nomi III, Matukai III, Esquive Ballistique, Armure Tactique) en **une seule variable `nTotalAC`** et appliquer **un seul `EffectACIncrease(nTotalAC, AC_DODGE_BONUS)`** (en retirant/remplaçant l'ancien effet si `nTotalAC` change).
* **`baseitems.2da` pour armes 2M/Doubles tenues à 1M (Gamoréen II) :** il faut modifier **les 3 colonnes ensemble** : `equipableslots = 0x00030` + `weaponwield = 2` + **`weaponsize = 3`** (si `weaponsize` reste à `4`, l'emplacement main gauche reste grisé même avec `weaponwield = 2`).
* **`baseitems.2da` colonne `reqfeat0` = OK :** bloque réellement l'équipement d'une arme tant que le personnage ne possède pas le don indiqué (permet de réserver les variantes `.uti` 1M à Gamoréen II).
* **`itemcreate.2da` colonne `level` = OK :** masque et verrouille nativement les recettes à l'établi tant que le niveau du personnage est inférieur à `level`.
* **`AurPostString` en jeu :** n'affiche rien si le mode debug n'est pas activé dans `swkotor2.ini` ; privilégier un VFX ou un effet visible sur la fiche de perso pour les tests rapides.
* **Compatibilité TSLRCM :** `Override/` contient déjà des fichiers `feat.2da` et `itemcreate.2da` modifiés (TSLRCM). Tout générateur doit partir de ces fichiers (ou de leur backup propre) plutôt que d'écraser avec du vanilla pur.
* **Embuscade furtive (pattern moteur validé en jeu — 23/11/2026) :**
  * **Piège #1 (race condition `LocalNumber` multi-PNJ) :** ne **jamais** décrémenter un compteur `LocalNumber` sur le PJ depuis `k_def_heartbt01` : dans une zone contenant *N* ennemis (ex. 25 droïdes sur Péragus `105PER`), chaque ennemi exécute son heartbeat en parallèle et vide le compteur en `< 0,2 s` dès la sortie de furtivité, avant même que l'animation d'attaque ne touche.
  * **Piège #2 (`EffectDamage` + `DAMAGE_TYPE_UNIVERSAL`) :** `DAMAGE_TYPE_UNIVERSAL` n'est utilisé **nulle part** avec `EffectDamage(...)` dans les 4 000+ scripts vanilla de KotOR 2 (uniquement avec `EffectDamageIncrease`). Toujours utiliser un type concret (`DAMAGE_TYPE_PIERCING`, `DAMAGE_TYPE_BLUDGEONING`, `DAMAGE_TYPE_DARK_SIDE`, etc.) dans `EffectDamage(...)`, et appeler `AssignCommand(oAtk, ApplyEffectToObject(...))` depuis le hook `OnDamaged` de la victime pour que le journal de combat attribue la 2e ligne de dégâts à l'attaquant.
  * **Méthode retenue & validée (`ov_inc_core.nss` dans [`tools/build_scripts.py`](tools/build_scripts.py)) :**
    1. **Armement & chrono moteur exact (`6,0 s`) :** dans `Ov_PollStealth()` (`k_def_heartbt01`, polling toutes les `1 s`) et `Ov_RefreshPassives()`, tant que `IsStealthed(oPM)` est vrai, `Ov_ApplyStealthAmbush(oPM)` retire l'ancien buff puis pose **`ApplyEffectToObject(DURATION_TYPE_TEMPORARY, SupernaturalEffect(EffectAttackIncrease(50)), oPM, 6.0)`**. Le `+50 Atq` garantit la touche sur la 1re attaque et c'est le **moteur lui-même** qui expire le buff exactement `6,0 s` après la sortie de furtivité (aucune race condition quel que soit le nombre de PNJ dans la zone).
    2. **Consommation & dégâts `×2` à l'impact :** dans `Ov_OnDamageHook(oVictim)` (`k_def_damage01` / `k_hen_damage01`), `Ov_ConsumeStealthAmbush(oAtk)` parcourt `GetFirstEffect(oAtk)` / `GetNextEffect(oAtk)` à la recherche d'un effet `GetEffectSubType(e) == SUBTYPE_SUPERNATURAL && GetEffectType(e) == EFFECT_TYPE_ATTACK_INCREASE`, le supprime immédiatement (`RemoveEffect`, même si la cible meurt en un coup), puis si `!GetIsDead(oVictim)` applique **`VFX_IMP_FORCE_PUSH`** et **`AssignCommand(oAtk, ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectDamage(GetTotalDamageDealt(), DAMAGE_TYPE_PIERCING), oVictim))`**.


