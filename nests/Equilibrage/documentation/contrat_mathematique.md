# Contrat Mathématique, Formules & Invariants de Design

> Outils associés : `tools/dpr_check.py`, `tools/dpr_data.json`, `tools/dpr_review.py` (dernier rapport : [`../content/dpr_review_2026-11-26.md`](../content/dpr_review_2026-11-26.md)).

## 1. Cibles DPR nets & durées de boss (TTK)

**Règle d'or** : aucun boss tué en moins de **4 rounds** ; cible **5–10 rounds** (`10–15` pour Sion/Traya).

| Phase (Boss étalon) | Duel (`1M`) | Ambidextrie (`2A`) | Arme Lourde (`2M`) | Haute Cadence (`HC`) |
| :--- | :---: | :---: | :---: | :---: |
| **EARLY** — Niv. 8 (120 PV, CA 20, **RD 2**) | 11–23 DPR (5–11 rds) | 9–18 DPR (7–14 rds) | 14–26 DPR (5–8 rds) | 17–30 DPR (4–7 rds) |
| **MID** — Niv. 16 (280 PV étalon DPR / ~380–420 PV réels, CA 29, **RD 5**) | 26–67 DPR (4–11 rds) | 23–65 DPR (4–12 rds) | 36–66 DPR (4–8 rds) | 36–81 DPR (3,5–8 rds) |
| **LATE** — Niv. 26 (650 PV, CA 44, **RD 8**) | 55–140 DPR (5–12 rds) | 49–150 DPR (4–13 rds) | 86–186 DPR (3,5–8 rds) | 61–170 DPR (4–11 rds) |

**Survie Late de référence** (`Déluge 3` + `Robustesse 3`) : Bure `TTD/TTK = 1,51×` (`8,0r / 5,3r`) · Légère + *Esquive Balistique* `1,51×` (`14,3r / 9,5r`) · Intermédiaire + *Armure Tactique* `1,17×` sur 1 bouclier `100×3` (`1,55×` sur 2) · Lourde + *Juggernaut* `1,54×` (`17,2r / 11,2r`).

## 2. Formules de DD, procs & embuscade furtive

- **Spécialisations d'arme** : `DD = 10 + Niv + Mod Carac directrice` si le proc dépend de la plage de critique (`plage/20`), **`5 + Niv + Mod Carac directrice`** s'il s'applique à chaque coup.
- **Grenades** : `DD = 10 + Niv + Mod INT` (cible ≥ `40 %` sur Vigueur élite `Set_3` à INT 14).
- **Fléchettes & Roquettes spécialisées** : `DD = 12 + Niv + Mod INT`.
- **Effets *On-Hit* d'armes** : table graduée `3 / 5 / 7 / 9 + Niv + Mod Carac directrice de l'arme` (`FOR/DEX` mêlée, `DEX/INT` distance).
- **Embuscade furtive** : la première attaque portée depuis la furtivité (fenêtre `6,0 s` après sortie) touche quasi automatiquement (`+50 Atq`) et double la totalité des dégâts (Attaque sournoise incluse) pour simuler un critique confirmé.
- **Axe distance / mêlée** : parité de viabilité par chemins asymétriques (`DEX` à distance, `INT` via Gand II ; la mêlée paie l'approche/défense, la distance paie boucliers et déflexion).

## 3. Garde-fous de conception (décisions écartées à ne pas rouvrir sans raison forte)

- **Pas de branche Mains nues dédiée** (*Arts Martiaux* supprimé) : une seule série par caractéristique, et l'identité mains nues est déjà portée par Impact + Duel + Spécialiste mains nues R1–R3 + Matukai.
- **Pas de Chambrage sur *Tir d'Assaut*** : combiné au `+1 atq/rd` de Spé III, le Chambrage écraserait *Tir Pénétrant*.
- **Pas de cumul de deux postures via *Gamorréen II*** (*Amb + HC* ou *Amb + Arme Lourde* fait chuter le TTK sous 4 rounds) ; l'arme `HC 1M` en main droite garde `+1 atq/rd` (`0` CA) mais rien en main gauche.
- **Pas d'exception d'armures « Force-friendly »** : *Ubese* et *Zeison Sha / Jal Shey* suivent les restrictions des armures légères standard ; seules les bures autorisent tous les pouvoirs.
- **Pas de cap global d'immunité aux dégâts** à ce stade (révisable uniquement sur retours joueurs concrets).
- **Principes transverses** : ordre canonique `FOR, DEX, CON, INT, SAG, CHA` ; notation en dés d20 (`1d6`, `2d8`) ; *« les synergies doivent être trouvées, pas décrites »*.
