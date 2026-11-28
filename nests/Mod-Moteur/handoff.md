# Handoff — Session du 28/11/2026

## Ce qui a été fait

- Initialisation du nid (six fichiers canoniques lus, deux guides repérés), puis passe de correction demandée par l'utilisateur via `Organisateur`.
- Contrôle de conformité du `feat.2da` généré avant toute correction des tests : prérequis R1 (armures `4/5/6`, armes `43/44`) et `EVASION` (ligne `125`) conformes au CSV `WIP Feats.csv` ; `changes_fr.ini` de l'installateur déjà synchronisé sur `prereqfeat2` (commit `40416c6`). Aucun `.2da` ni artefact du mod régénéré.
- `tools/verify_passes123.py` : les 6 assertions en échec resynchronisées sur `prereqfeat2` (tableau des 7 rangs I + `EVASION`), avec garde « `prereqfeat1` vide » ; résultat `187 PASSED, 0 FAILED`.
- `documentation/pieges_pykotor_et_odyssey.md` : §0.B–C redirigé vers `nests/Equilibrage/documentation/`, « 4 bugs » → « 5 bugs », règle `prereqfeat1`/`prereqfeat2` ajoutée en §3.A.5, liens relatifs vers `tools/` réparés après la migration et mentions des deux scripts retirés (`build_feats_csv.py`, `verify_mod.py`) corrigées.
- `documentation.md` : 187 tests, `itemcreatemira.2da` ajouté à la liste des `.2da` générés. `inbox.md` vidé (2 messages traités). `choices.md` : 2 projets en réserve (code de sortie, renommage éventuel de la suite).
- `nests/Lore-et-Distribution/inbox.md` : prévenu que la suite repasse à 100 %.

## État pour la suite

- `plan.md` inchangé : restent la *Tenue de danse* (`max(CHA, DEX)` sur la CA dans `Ov_RefreshPassives()`) et le test moteur T3 (Matukai III). `intent.md` n'a pas été touché.
- `Lore-et-Distribution` a reconstruit `installer/` et `dist/` pendant la session (28/11, 02 h 21) : ne rien y toucher depuis ce nid.
