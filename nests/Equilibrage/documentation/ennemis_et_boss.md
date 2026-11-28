# Équilibrage Ennemis & Boss

> Inventaire brut complet des 367 templates ennemis : [`_reference/analyses_kotor/tableau_ennemis.md`](../../../_reference/analyses_kotor/tableau_ennemis.md) (généré par `tools/extract_enemies.py --phase 3`).
> Constats d'extraction : `_reference/analyses_kotor/ennemis_defenses_etat_des_lieux.md` et `ennemis_reference_kotor2.md`.

## 1. Principes directeurs (P1–P5)

- **P1 — Une famille = une réponse forcée** : chaque grande famille dispose d'une résistance signature et d'une faiblesse assumée (évite la monotonie de Péragus à Malachor sans rendre tout le monde résistant à tout).
- **P2 — Résistances partielles par défaut** : pénalise sans verrouiller un build ; immunités 100 % réservées aux droïdes et cas raciaux.
- **P3 — Variété qualitative plutôt que sacs à PV** : PV/CA/Atq restent pilotés par `autobalance.2da` (avec `Set_5 vpmult = 0,95` et `damagemult` boss réduit pour des combats de **5–10 rounds**).
- **P4 — Zéro phase de boss scriptée supplémentaire & soins statu quo** : compatibilité totale TSLRCM ; les Maîtres Jedi/Sith conservent leurs sorts vanilla (*Guérison*, *Drain de vie*).
- **P5 — Lisibilité immédiate** : équipement visible (armures, bures, boucliers lootables), VFX et mentions « Résisté » du journal de combat.

## 2. Matrice des profils défensifs par famille (scaling continu sur `Niv. PJ`)

Formules continues alignées sur `autobalance.2da` (sans cassure de paliers Early/Mid/Late) :

| Famille | Profil défensif (scaling continu sur `Niv. PJ`) | Faiblesse assumée | Réponse joueur |
| :--- | :--- | :--- | :--- |
| **Sith / Jedi obscurs** | **Bures réelles** + Résist. Force **`10 + 1,40 × Niv`** + Volonté **`1 + 0,20 × Niv`** *(max `+6`)* + ***Esquive Totale*** *(Niv. ≥ 20)* + **Absorption de Force** si `PF < 30 %` | RD nulle, Vigueur moyenne | Dégâts bruts / sabre, *Peste* (Vig), *Destruction de Force* / *Pouvoir Pénétrant* |
| **Soldats / Mercenaires** | **Armures légères/interm.** portées (`RD 2/-` Interm.) + **résist. Énergie & Feu `5 % + 1,0 % × Niv`** *(max **`35 %`**)* + **boucliers d'énergie** (`50/100 PV`) sur ~1/3 élites (lootables) | Volonté basse, vulnérables physique/ion/sonique | Mêlée physique, *Disrupteur*, *Insanité* / *Tourbillon* |
| **Mandaloriens** | **Armure lourde** (`RD 4/-` native) + **résist. Énergie & Feu `30 % + 1,5 % × Niv`** *(max **`75 %`**)* + boucliers élites + stim (`+2 FOR/CON`) | **Aucune résist. Force**, Volonté basse, vulnérables physique/ion/sonique | Force (*Tempête*, *Insanité*, *Stase*), armes physiques + bris d'armure (*Traditionnelle*), ion/sonique |
| **Bêtes** | **RD Physique pure `1 + 0,50 × Niv`** *(max **`15/-`**, 0 RD Énergie)* + haute Vigueur + imm. *Peur* (`CR ≥ 8`) + régén lente hors combat (apex) | Volonté très basse, **aucune résist./RD Énergie, Électricité ou Feu** | **Sabres laser, blasters**, *Éclairs*, grenades incendiaires/plasma, contrôles mentaux |
| **Droïdes** | **Statu quo binaire** (esprit/poison/drain) + **déflecteurs droïdes** (`50–60 PV`) sur ~1/3 élites | Ion, *Destruction de droïde*, Électrique | Armes/grenades ioniques, pouvoirs anti-droïdes |
| **Assassins Sith** | Furtivité + *Esquive instinctive* + **esquive `10 % + 0,5 % × Niv`** *(max **`25 %`**)* + **Réflexes `1 + 0,15 × Niv`** *(max **`+5`**)* | PV faibles, RD nulle, Vigueur basse | *Peste* / *Stase* (Vig), dégâts garantis |
| **Boss (`Set_4`/`Set_5`)** | Profil familial + **RD passive `1 + 0,25 × Niv`** *(max **`RD 8/-`**, Phys & Énergie)* + `Set_5 vpmult = 0,95` | Selon famille | S'appuie sur l'existant TSLRCM sans conflit |

## 3. Boucliers ennemis (repères chiffrés)

L'IA ennemie (`GN_ActivateForceField`) active automatiquement tout brassard porté au round 1 (`1×/spawn`, durée `200 s + 2 s/Réparation`). Valeurs vanilla cohérentes avec nos plafonds d'établi : `RD 5–10`, pool `50–100 PV` (`a_shield_01..07` et `d_shield_01..06`, soit ~2–4 coups de blaster absorbés). Contre-mesures : mêlée, sabres, *Disrupteur de bouclier*.
