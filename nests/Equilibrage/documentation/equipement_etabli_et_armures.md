# Équipement, Établi, Cristal Personnel & Armures

> Sources opérationnelles : `csv/fr/` (*armes*, *Améliorations*, *Craft*, *Armures* et les 6 CSV d'équipement). En cas de divergence, les CSV font foi.

## 1. Armes, Établi & Cloisonnement des améliorations

- **Plafonds de dégâts moyens des upgrades d'armes** (226 pièces dans *Améliorations.csv*) : Early (`Niv. 1–10`, Mk I) **`+2`** · Mid (`Niv. 11–18`, Mk II) **`+5`** · Late (`Niv. 19+`, Mk III) **`+10`** *(pour une arme disposant de tous ses slots)*.
- **Verrou de niveau du Craft (`itemcreate.2da`)** : **`Mk I = Niv. 1 / Mk II = Niv. 10 / Mk III = Niv. 15 / Mk IV-T5 = Niv. 20`** (`1 / 10 / 18` sur lignées 3 tiers). Toutes les armes de base non-laser sont craftables dès le Niv. 1. *Bâton Gaffi* retiré.
- **Hiérarchie des slots par famille (`UpgradeLevel`) & cloisonnement strict** *(1 seul slot à dégâts bruts réguliers par catégorie)* :
  - **Mêlée (`Poignée 1 < Lame 2 < Cellule 3`)** : *Mains nues* (0) · *Impact* (1 : Poignée) · *Traditionnelle* (2 : Poignée, Lame) · *Résonance* (3 : Poignée, Lame, Cellule).
    - *Poignée* : `+Atq` / `+CA` (`0` dégât) · *Lame* : `Acéré`, `Critiques massifs`, *On-Hit* scalés, `vs Droïdes` (`0` dégât brut) · ***Cellule*** *(Résonance seule)* : **seul slot à dégâts réguliers**.
  - **Distance (`Lunette 1 < Pack 2 < Chambrage 3`)** : *Tir Tactique* (1 : Lunette) · ***Tir d'Assaut* & *Tir Assassin*** (2 : Lunette, Pack) · *Tir Pénétrant* (3 : Lunette, Pack, Chambrage).
    - *Lunette* : `+Atq`, `Acéré`, ***On-Hit* scalés** (`0` dégât) · *Pack* : `Critiques massifs`, `Ion / vs Droïdes & Boucliers`, ou léger bonus constant (`+1..+3` max) · ***Chambrage*** *(Tir Pénétrant seul)* : **seul slot à gros dégâts bruts**.
  - **Sabre Laser** : *Émetteur* (`+CA`, Parade, ***On-Hit* scalés**, `0` dégât) · *Lentille* (`+Atq`, `Acéré`, `Critiques massifs`, `0` dégât) · ***Cellule*** (**seul slot à dégâts réguliers**) · *Cristaux ×2* (`+Caracs`, Régén PV/PF, `+Atq`, Parade, `vs Alignement/Droïdes`, `0` dégât brut générique).
- **Compensation des familles à 1–2 slots** : dés de base plus élevés, plage de critique élargie ou multiplicateur supérieur (ex. `Heavy_Blaster` `1d12`, `Hold_Out_Blaster` `1d6`, `Double sabre` `2d8`, `Lame wookiee` `1d10 20/×3`).
- **Armes nommées, loot & 6 reliques endgame** : retrait des dégâts gratuits sur les armes craftables Niv. 1 (`w_melee_03`, `w_melee_09`) ; plafond des bonus `.uti` de série par palier (**T1–14 : `+2`** · **T15–22 : `+1d4`/`+3`** · **T23–30 : `+1d6`/`+4`**) ; **6 reliques** (*Arg'garok*, *Épée de Freyyr*, *Bâton électrique géonosien*, *Blaster de Freedon Nadd*, *Fusil auto zabrak*, *Fusil à répétition d'Ondéron*) à `ulvl = 0` (non modifiables) avec bonus unique plafonné à `+1d8` / `+1d10`.
- **Équipement (6 CSV : Casques, Implants, Gants, Ceintures, Brassards, Armures items)** : plafond strict **`+1 / +2`** par carac (max **`+3`** légendaire sur une stat unique), couverture des 6 caracs sur les 5 slots majeurs, RD exactes via `iprp_resistcost.2da` (`2/3/4/6/12/-`).

## 2. Cristal personnel de l'Exilé

- **Stats (3 paliers, `0` dégât brut / `0` On-Hit / `0` save)** : **`+2/+1/0`** (`Niv. 1–14`), **`+4/+2/+1`** (`Niv. 15–21`), **`+6/+4/+2`** (`Niv. 22+`) sur `1re / 2e / 4 autres stats` (attribué auto sur les 2 meilleures stats de base, personnalisable via Kreia : `30 paires × 3 paliers = 90 .uti`).
- **Effets de multiclassage (2 cumulables max : Base + Prestige, quand monté dans le sabre tenu)** :
  - *Base* : **Gardien** (`+1 PV/niv` & `+1 Atq`) · **Sentinelle** (`+1 Atq/CA/Saves`) · **Consulaire** (`coût PF -10 %`).
  - *Prestige* : **Maître d'Armes** (`On-Hit +1 Atq & +1 CA` 2 rds, cap `+5`) · **Maraudeur** (`On-Hit` soin `+1 % PV max`) · **Jedi protecteur** (`+3` toutes compétences) · **Assassin** (`Critiques massifs +2d6` & `+1` plage) · **Maître Jedi** (`+2 DD` & durée buffs `+25 %`) · **Seigneur Sith** (`+2 DD` & `Régén PF +3`).

## 3. Armures, Défenses & Dégradé de Pouvoirs

| Catégorie | CA base | Plafond DEX | RD native (Phys & Én.) | Accès Établi (`UpgradeLevel`) |
| :--- | :---: | :---: | :---: | :--- |
| **Bure / Sans armure** | `0–1` | Illimité | `0` | `ulvl 0` (0 slot) |
| **Légère** *(dont Ubese & Zeison Sha)* | **`4–5`** | **`+14` à `+16`** | `0` | **`ulvl 1`** (1 slot : 15 Sous-couches légères) |
| **Intermédiaire** | **`6–7`** | **`+3` à `+4`** | **`RD 2/-`** | **`ulvl 6`** (2 slots : 30 Sous-couches + **30 Sur-couches exclusives renforcées**) |
| **Lourde** | **`10–11`** | **`+0` à `+1`** | **`RD 4/-`** | **`ulvl 2`** (1 slot : 30 Sous-couches complètes) |

- **Hiérarchie CA** : *Nue* = Légère (`19–20`) > Lourde (`11`) > Intermédiaire (`10`) · *En jeu* = Légère (`+Esq. Bal.`) ≈ Bure *full buff* > Intermédiaire upgradée > Lourde (`RD 11/- + 30 % imm.`).
- **Exception *Tenue de danse* (`Slave_Outfit` / `g_danceroutfit`, ID `100`)** : classée Sans armure (`0` CA, `0` RD, `0` slot, tous pouvoirs), utilise **`max(CHA, DEX)`** pour son bonus de carac à la CA.
- **Trois arbres d'armures (3 rangs)** :
  - **Juggernaut** *(lourde)* : `RD 3/4/5/-` + immunité tous dégâts `10/20/30 %` *(cumul max avec native + Robustesse II = `RD 11/- + 30 %`, pas de cap global d'immunité)*.
  - **Armure Tactique** *(interm.)* : `RD 3/4/5/-`, `+1/+2/+3 CA` ; R1 durée boucliers `+100 %` & furtivité sans ceinture ; R2 absorption boucliers `×2` & Course furtive ; R3 absorption boucliers `×3`.
  - **Esquive Balistique** *(légère)* : Esquive `10/20/30 %` + `+1/+2/+3 CA base` (ne relève pas le plafond DEX).
- **Dégradé de pouvoirs (`forbiditemmask`)** : **Bure** = tous · **Légère** = autorise *Talent*, *Suppression/Destruction*, *Terreur/Horreur/Insanité*, *Cri*, *Écrasement* + interm./lourde (bloque *Vitesse*, *Armure de Force*, *Stase*, *Tempête*, *Mise à mort*, *Absorption de vie* ; **aucune exception Force-friendly** sur Ubese / Zeison Sha) · **Interm.** = *Guérison/Soins*, *Revitalisation*, *Barrière*, *Résist. Énergie*, *Peste*, *Poussée/Tourbillon/Vague*, *Méditation*, *Destruction droïde*, *Subterfuge/Confusion*, *Spectre*, *Grâce LS* + lourde · **Lourde** = *Corps de Force*, *Lancer de sabre*, *Résist./Imm. Force*, *Absorption*, *Parade/Renvoi*, *Contrôle respiration* et 5 ultimes de prestige.
- ***Condition physique I–III*** : conservé vanilla (`+1/+2/+3` sauvegardes).
