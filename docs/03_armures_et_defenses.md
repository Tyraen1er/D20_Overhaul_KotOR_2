# 3. Armures, Boucliers & Défenses

[← Page précédente : Dons & Spécialisations](02_dons_postures_et_specialisations.md) | [Introduction](README.md) | [Page suivante : Pouvoirs de la Force →](04_pouvoirs_de_la_force.md)

---

## Une vraie identité pour chaque catégorie d'armure

Dans le jeu de base, porter une armure en tant que Jedi était presque toujours un piège : elles bloquaient la majorité des pouvoirs de Force et offraient moins de Défense qu'une simple bure avec une bonne Dextérité.

Le mod redéfinit **chaque type d'armure** autour d'un rôle précis, avec une **Réduction de Dégâts (RD) native**, de nouveaux plafonds de Dextérité, un accès différent à l'établi et **trois arbres de dons dédiés**.

| Catégorie | CA de base *(avant → après)* | Plafond DEX *(avant → après)* | RD native *(Physique & Énergie)* | Emplacements à l'établi | Pouvoirs de Force autorisés |
| :--- | :---: | :---: | :---: | :--- | :--- |
| **Bures & Tenues** *(sans armure)* | `0` *(inchangé)* | Illimité *(sauf bures restrictives +5)* | **0** | Aucun *(0 emplacement)* | **Tous les pouvoirs** *(défense dépendant des buffs temporaires : Armure de Force, Vitesse, Talent)* |
| **Armure Légère** | `4–5` → **`4–5`** | `+4/+5` → **`+14 à +16`** | **0** | **1 emplacement** : Sous-couche légère uniquement *(15 pièces)* | Pouvoirs autorisés en légère *(bloque Vitesse, Armure de Force, Stase, Tempête, Mise à mort, Absorption de vie)* |
| **Armure Intermédiaire** | `6–7` → **`6–7`** | `+2/+3` → **`+3 à +4`** | **RD `2/-`** | **2 emplacements** : Sous-couche complète *(identique Lourde)* + **Sur-couche exclusive renforcée** *(30 pièces)* | Pouvoirs autorisés en intermédiaire *(Soins, Revitalisation, Barrière, Résistance Énergie, Peste, Poussée/Vague, Méditation, Grâce LS…)* |
| **Armure Lourde** | `8–9` → **`10–11`** | `0/+1` → **`+0 à +1`** | **RD `4/-`** | **1 emplacement** : Sous-couche complète *(30 pièces)* | Pouvoirs autorisés en lourde *(Corps de Force, Lancer de sabre, Résistance Force, Absorption Force, Parade/Renvoi, Ultimes de prestige)* |

> **Ports d'armure gratuits dès le niveau 1 :** pour éviter de dépenser des dons dès Péragus, les classes Jedi débutent désormais avec le **Gardien** équipé de tous les ports d'armure (*Légère, Intermédiaire et Lourde*), la **Sentinelle** avec *Légère et Intermédiaire*, et le **Consulaire** avec *Légère*.

> **Fin des passe-droits sur les armures légères :** les **Combinaisons Ubese / de vol blindées** et les **Armures Zeison Sha / Jal Shey** ne bénéficient plus de leur passe-droit du jeu de base — elles suivent désormais exactement les mêmes restrictions de pouvoirs de la Force que toutes les autres armures légères.

> **Tenue de danse (`Slave_Outfit`) :** cette tenue sans armure bénéficie d'une exception unique — elle applique le **modificateur de Charisme (CHA)** à la CA plutôt que la Dextérité *(si CHA > DEX)*, tout en autorisant tous les pouvoirs de la Force.

> **Blindages Droïdes** (T3-M4, HK-47, G0-T0) : inchangés dans leur fonctionnement de base.

---

## Pourquoi les armures intermédiaires ont-elles des améliorations exclusives ?

Les armures intermédiaires incarnent l'**armure technologique et tactique** par excellence : là où les armures légères privilégient la souplesse et les armures lourdes le blindage brut, leur châssis modulaire accueille deux composants complémentaires. Concrètement, chaque catégorie s'améliore différemment à l'établi :
- **Armures Légères (1 emplacement — Sous-couche légère)** : accès aux **15 sous-couches légères** (*Anti-environnement*, *Bio-restaurative*, *Fortificatrice*).
- **Armures Lourdes (1 emplacement — Sous-couche complète)** : accès aux **30 sous-couches** (*communes* + *Renforçante FOR/CON*, *Flexible DEX max*, *Duracier Physique*).
- **Armures Intermédiaires (2 emplacements — Sous-couche complète + Sur-couche exclusive renforcée)** : sans aucun don requis, l'armure intermédiaire partage **les mêmes 30 sous-couches que l'armure lourde** et dispose en plus de l'exclusivité des **30 sur-couches renforcées** (*8 lignées* combinant résistances/immunités croisées, sauvegardes, discrétion, immunités aux effets de contrôle et renforts défensifs). C'est l'armure polyvalente et modulable par excellence !

---

## Les 3 Arbres de dons d'armure

Chaque type d'armure dispose désormais de son propre arbre de **3 dons** (Niv. 1 / 8 / 15). Les bonus s'appliquent dès que vous portez une armure de la catégorie correspondante.

### 1. Esquive Balistique *(Armure Légère — Mobilité & Esquive)*
*Idéal pour les duellistes, éclaireurs et combattants agiles qui misent sur la chance d'esquiver complètement les coups.*

| Rang | Prérequis | Effet |
| :---: | :--- | :--- |
| **Esquive Balistique I** | Niv. 1+, Port d'armure légère | **`+10 %` d'esquive**, **`+1 CA`** |
| **Esquive Balistique II** | Niv. 8+, Rang I, Gardien / Sentinelle / prestiges *(ou Soldat/Éclaireur/Voyou)* | **`+20 %` d'esquive**, **`+2 CA`** |
| **Esquive Balistique III** | Niv. 15+, Rang II, Maître d'Armes / Maraudeur / Jedi Protecteur / Assassin *(ou Soldat/Éclaireur/Voyou Niv. 15+ ; Visas Niv. 15+)* | **`+30 %` d'esquive**, **`+3 CA`** |

### 2. Armure Tactique *(Armure Intermédiaire — Boucliers & Furtivité)*
*Idéal pour les profils ingénieurs, hybrides et furtifs : transforme les boucliers d'avant-bras en véritables murs d'énergie et autorise la discrétion en armure intermédiaire.*

| Rang | Prérequis | Effet |
| :---: | :--- | :--- |
| **Armure Tactique I** | Niv. 1+, Port d'armure intermédiaire | **`RD 3/-`**, **`+1 CA`**, **durée des boucliers `+100 %`**, **furtivité sans ceinture** *(en armure intermédiaire)* |
| **Armure Tactique II** | Niv. 8+, Rang I, Sentinelle / Jedi Protecteur / Assassin *(ou Éclaireur/Voyou/Technicien)* | **`RD 4/-`**, **`+2 CA`**, **absorption des boucliers doublée (`×2`)**, accès à **Course furtive** *(en armure intermédiaire)* |
| **Armure Tactique III** | Niv. 15+, Rang II, Jedi Protecteur / Assassin *(ou Éclaireur/Voyou/Technicien Niv. 15+ ; Visas Niv. 15+)* | **`RD 5/-`**, **`+3 CA`**, **absorption des boucliers triplée (`×3`)** |

### 3. Juggernaut *(Armure Lourde — Tank pur)*
*Idéal pour les combattants en première ligne qui veulent encaisser les coups sans broncher.*

| Rang | Prérequis | Effet |
| :---: | :--- | :--- |
| **Juggernaut I** | Niv. 1+, Port d'armure lourde | **`RD 3/-`**, **immunité à tous les dégâts `+10 %`** |
| **Juggernaut II** | Niv. 8+, Rang I, Gardien / Maître d'Armes / Maraudeur *(ou Soldat)* | **`RD 4/-`**, **immunité à tous les dégâts `+20 %`** |
| **Juggernaut III** | Niv. 15+, Rang II, Maître d'Armes / Maraudeur *(ou Soldat Niv. 15+)* | **`RD 5/-`**, **immunité à tous les dégâts `+30 %`** |

> **Combien un Juggernaut peut-il encaisser ?**
> En cumulant la RD native de l'armure lourde (`4/-`), *Juggernaut III* (`5/-`) et *Robustesse II* (`2/-`), vous atteignez **`RD 11/-` + `30 %` d'immunité à tous les dégâts** (sans plafond artificiel si vous ajoutez des résistances via votre équipement). Vous devenez pratiquement indestructible face aux escouades d'ennemis !

---

[← Page précédente : Dons & Spécialisations](02_dons_postures_et_specialisations.md) | [Introduction](README.md) | [Page suivante : Pouvoirs de la Force →](04_pouvoirs_de_la_force.md)
