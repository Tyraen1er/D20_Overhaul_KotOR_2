# Documentation — Utilitaires Externes

## Périmètre du nid

Ce nid couvre tous les outils compagnons hors-jeu destinés aux joueurs ou au modding autour de **KotOR 2 D20-Overhaul**.

## Chantier initial : Utilitaire de Conversion & Respec

- **Cahier des charges complet** : [`documentation/specs_utilitaire_respec.md`](documentation/specs_utilitaire_respec.md) (acté le 24/11/2026, motivé par l'impossibilité moteur d'un respec in-game en NWScript — absence de `RemoveFeat`, `RemoveSpell` et de baisse de niveau dans `swkotor2.exe`).

### Briques disponibles dans le dépôt

- **Emplacement acté (`Organisateur`, 28/11/2026)** : le code source de l'utilitaire vit dans `tools/utilitaire/` (paquet Python avec son propre fichier de dépendances), utilise le `.venv` commun du dépôt (pour embarquer automatiquement le `pykotor` corrigé sans dupliquer les 5 patchs) et transmet l'exécutable final à `Distribution` pour livraison dans `dist/`.

- **`.venv`** : Python 3.14.7, `pykotor 2.3.12` corrigé de 5 bugs dans `.venv/Lib/site-packages/pykotor/` (cf. `nests/Mod-Moteur/documentation/pieges_pykotor_et_odyssey.md` §2 ; le correctif n° 4, lecture binaire des `.2da`, sert à l'outil pour lire les tables de l'installation du joueur). Ni framework graphique ni `PyInstaller` n'y sont installés ; Tk 9.0 y est disponible. Les correctifs n'existent que dans ce `.venv` : un `.venv` recréé ou un `pykotor` réinstallé les perd.
- **Tables** : l'Overhaul remplace 10 tables, générées dans `mods/overhaul/Override/` (`feat`, `featgain`, `classpowergain`, `spells`, `baseitems`, `itemcreate`, `itemcreatemira`, `forceshields`, `iprp_resistcost`, `autobalance`). Il ne fournit ni `classes.2da` ni `skills.2da` : celles-ci viennent des BIF du jeu. La copie installée dans le jeu peut différer de la sortie de build du dépôt (constaté sur `feat.2da` le 28/11/2026) : l'outil lit donc toujours les tables de l'installation du joueur.
- **IDs custom** : `mods/overhaul/feat_ids.json` (dons 245 à 322), `spell_ids.json` (pouvoirs 282 à 286) et `baseitem_1m_map.json` (types d'objet 104 à 123). Repères vanilla TSLRCM dans `_reference/2da/*_tslrcm.2da` : `feat.2da` 245 lignes, `spells.2da` 282, `baseitems.2da` 104.
- **Objets custom** : 170 `.uti` à ResRef inconnu du vanilla, en 4 familles : `ov1m_001` à `ov1m_069` (variantes à une main ; correspondance vers l'arme à deux mains d'origine dans `mods/overhaul/gamorrean_swap_map.json`), `ov_crys_*` (90), `ov_hide_*` (10) et `ov_gam_adapt`. Seuls 72 `.uti` utilisent un type d'objet custom : les 69 `ov1m_*` plus `mininglaser`, `advancedminingla` et `plasmatorch`.
- **KSE** (`tools/KSE_353/`) est présent localement (non versionné) comme référence de structure des sauvegardes K2 (`SAVEGAME.sav`, `PARTYTABLE.res`, `AVAILNPC*.utc`).

### Ce que `pykotor` 2.3.12 apporte, et n'apporte pas

- **Aucun support dédié des sauvegardes** : le paquet ne contient aucune occurrence de `SAVEGAME`, `PARTYTABLE` ou `GLOBALVARS`, et ses formats sont bif, bwm, erf, gff, key, lip, ltr, lyt, mdl, ncs, rim, ssf, tlk, tpc, twoda, txi, vis, wav.
- Les `.utc` passent par `pykotor.resource.generics.utc` (`read_utc`/`write_utc`, en usage dans `tools/build_enemies.py`) et les `.uti` par `pykotor.resource.generics.uti`. Le reste (`.res`, contenu de `.sav`) passe par les formats génériques GFF, ERF et RIM (`read_gff`/`write_gff`, `read_erf`, en usage dans `tools/build_items.py`).
- La recherche de ressources du jeu (BIF via `chitin.key`, puis `Override`) passe par `pykotor.extract.installation.Installation` (en usage dans `tools/build_craft_csv.py`).
- **API de cette version** : `GFFStruct` se manipule comme un dictionnaire de champs typés (`root.acquire("Label", défaut)` renvoie la valeur ; sinon `get_uint8`, `get_int32`, `get_string`, `get_resref`, `get_list`, `get_struct`… et leurs `set_*`). `TwoDA` expose `get_height()`, `get_labels()`, `get_row(i)` et `get_cell` ; une ligne expose `get_integer`, `get_float`, `get_string` et `.label`.

### Environnement de test local

- Jeu installé (Steam, build « Remaster ») dans `C:\Program Files (x86)\Steam\steamapps\common\Knights of the Old Republic II` — chemin déjà utilisé par `tools/install_to_game.py`. Son `Override/` contient l'Overhaul (les 993 fichiers de `mods/overhaul/Override/` y sont, parmi 3615).
- Les sauvegardes sont dans `<jeu>\cloudsaves\<identifiant Steam>\` (un dossier par sauvegarde, du type `000000 - QUICKSAVE`) ; `<jeu>\saves\` existe mais est vide. La détection doit donc couvrir `saves/` et `cloudsaves/*/`, plus le parcours manuel.
- Ces sauvegardes appartiennent à l'utilisateur : les lire va de soi, les modifier non. Tout test d'écriture se fait sur une copie, avec son accord.
- Aucune sauvegarde vanilla (TSLRCM) n'est disponible : le jeu d'essai de l'étape 8 du plan est à constituer avec l'utilisateur.

### Points d'attention techniques

- **Structure exacte d'une sauvegarde K2** (conteneurs ERF et RIM, GFF embarqués) à établir sur une vraie sauvegarde, KSE comme référence. L'aller-retour lecture/écriture à l'identique via `pykotor` est le premier test à faire passer.
- **Le `.utc` ne garde pas l'historique niveau par niveau** des dons et pouvoirs : l'outil doit reconstruire une affectation déterministe et légale (`Niv. 1 -> Niv. N`) respectant `mincharlevel`, `prereqfeat1/2`, `orreqfeat0..4`, `minattackbonus` et les quotas par classe afin de pré-cocher tous les choix existants.
- **Retour en Vanilla** : retirer aussi les pouvoirs custom (282 à 286), pas seulement les dons ; les objets `ov*` n'ont plus de définition dans le jeu (traitement à trancher dans `choices.md`).
- **Portée d'une conversion** à définir : seuls les personnages choisis, ou toutes les créatures enregistrées dans la sauvegarde (compagnons hors groupe, PNJ des `.rim` et `.git` du module).
