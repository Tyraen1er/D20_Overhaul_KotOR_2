# 7. Combat & Guide tactique des Ennemis

[← Page précédente : Armes, Établi & Cristal](06_armes_ameliorations_et_cristal.md) | [Introduction](README.md) | [Page suivante : Annexe Équipements →](08_annexe_equipements_reequilibres.md)

---

> **Rappel (Furtivité) :** votre **première attaque** dans les **6 secondes** suivant la sortie du mode furtif reçoit **`+50` en Attaque** (touche garantie) et **duplique la totalité de ses dégâts (Attaque sournoise comprise)** sur une **seconde ligne** du journal de combat pour simuler un coup critique garanti.

## Rythme des combats & Boss

L'équilibrage global des combats a été pensé autour d'une règle simple : **un combat contre un boss doit être un vrai duel, pas une formalité de 2 rounds.**
- **Durée cible des boss :** **5 à 10 rounds** (et **10 à 15 rounds** pour les grands affrontements finaux comme Dark Sion ou Dark Traya).
- **Réduction de Dégâts (RD) passive des sous-boss et boss :** évolue en continu avec votre niveau selon **`1 + 0,25 × Niveau`** *(plafonné à **`RD 8`** — ex. `RD 2` au Niv. 5, `RD 5` au Niv. 16, `RD 8` au Niv. 28+)*.
- **PV des boss** légèrement rehaussés pour accompagner votre montée en puissance.
- **Dégâts des boss modérés** afin qu'un personnage bien préparé (en bure, légère, intermédiaire ou lourde) puisse lui aussi tenir 5 à 10 rounds sans se faire éliminer en un coup.
- **Compatibilité garantie :** aucune mécanique de phase artificielle n'a été rajoutée aux boss pour rester 100 % fidèle aux événements du jeu et de TSLRCM.

---

## Guide tactique des 6 Familles d'ennemis

Dans le jeu de base, presque tous les ennemis organiques combattaient « nus » (sans véritable armure ni résistance), ce qui rendait les combats uniformes. Le mod donne à **chaque grande famille d'ennemis** un profil défensif lisible qui **évolue en continu avec votre niveau** (comme l'autobalance du jeu, quel que soit l'ordre des planètes) et une **faiblesse claire** pour récompenser l'adaptation tactique.

> **Règle d'or :** les résistances des ennemis organiques sont **partielles et progressives** (jusqu'à `35 %` ou `75 %` selon la famille) afin de pousser à changer d'arme ou de tactique sans jamais bloquer totalement un build. Les immunités `100 %` restent réservées aux droïdes.

| Famille d'ennemis | Forces & Défenses *(évolutives selon votre Niveau)* | Faiblesses | Comment les contrer ? |
| :--- | :--- | :--- | :--- |
| **Sith & Jedi Obscurs** | • Portent de **vraies bures défensives**<br>• **Résistance à la Force :** **`10 + 1,40 × Niv`** *(ex. `24` Niv. 10, `38` Niv. 20, `52` Niv. 30)*<br>• **Bonus en Volonté :** **`1 + 0,20 × Niv`** *(max **`+6`**)*<br>• Obtiennent **Esquive Totale** dès que vous atteignez le **niveau 20+**<br>• Utilisent **Absorption de Force** en priorité si leurs PF tombent sous 30 % | • Aucune Réduction de Dégâts<br>• Vigueur moyenne | • Dégâts bruts au sabre ou au blaster<br>• Pouvoirs ciblant la **Vigueur** (*Peste*, *Stase*)<br>• *Destruction de Force* et don *Pouvoir Pénétrant* pour percer leurs défenses |
| **Soldats & Mercenaires** | • Portent de **vraies armures légères et intermédiaires** (`RD 2/-` sur les intermédiaires)<br>• **Résistance Énergie & Feu :** **`5 % + 1 % × Niv`** *(max **`35 %`**)*<br>• Environ **1 élite sur 3** active un **bouclier d'énergie** (`50` à `100` PV, récupérable sur son corps !)<br>• Utilisent toujours leurs grenades | • Volonté basse<br>• Vulnérables aux dégâts **physiques, ioniques et soniques** *(les boucliers d'énergie n'arrêtent pas la mêlée physique)* | • Armes physiques (épées, vibrolames) / corps-à-corps<br>• Grenades *Disrupteur de bouclier*<br>• Pouvoirs mentaux (*Insanité*) et *Tourbillon* |
| **Mandaloriens** | • Portent de **vraies armures lourdes** (`RD 4/-` native)<br>• **Résistance Énergie (blasters/sabres) & Feu :** **`30 % + 1,5 % × Niv`** *(max **`75 %`** — ex. `45 %` Niv. 10, `60 %` Niv. 20, `75 %` Niv. 30)*<br>• Boucliers sur les élites et **stimulants** activés au début du combat (`+2 FOR/CON`) | • **Aucune résistance à la Force**<br>• Volonté basse<br>• Vulnérables aux dégâts **physiques, ioniques et soniques** | • Pouvoirs de la Force (*Tempête*, *Insanité*, *Stase*)<br>• Armes physiques (épées, vibrolames) et **Bris d'armure** (*Arme Traditionnelle*)<br>• Armes ioniques / soniques |
| **Bêtes & Créatures** | • **RD Physique uniquement :** **`1 + 0,50 × Niv`** *(max **`RD 15/-`** — ex. `6` Niv. 10, `11` Niv. 20, `15` Niv. 30 ; aucune RD contre l'Énergie)*<br>• Haute **Vigueur**<br>• Immunité à la **Peur** sur les prédateurs majeurs<br>• Régénération lente hors combat (apex) | • **Volonté très basse**<br>• **Aucune RD ni résistance contre l'Énergie, l'Électricité ou le Feu** | • **Sabres laser, blasters**, *Foudre / Tempête*<br>• Grenades incendiaires / plasma<br>• Contrôles mentaux et *Confusion des bêtes* |
| **Droïdes** | • Conservent leurs **immunités mécaniques** (esprit, poison, drain)<br>• Environ **1 droïde d'assaut/guerre élite sur 3** active un **déflecteur d'énergie** (`50–60` PV) | • **Ions**, **Électricité** et pouvoirs anti-droïdes | • Armes et grenades **ioniques**<br>• *Désactivation / Destruction de droïde*, *Foudre* |
| **Assassins Sith & Traqueurs** | • **Furtivité** + *Esquive instinctive*<br>• **Esquive :** **`10 % + 0,5 % × Niv`** *(max **`25 %`**)*<br>• **Bonus en Réflexes :** **`1 + 0,15 × Niv`** *(max **`+5`**)* | • PV faibles, aucune RD<br>• **Vigueur basse** | • Pouvoirs sur la **Vigueur** (*Peste*, *Stase*)<br>• Contrôles et dégâts directs |

---

[← Page précédente : Armes, Établi & Cristal](06_armes_ameliorations_et_cristal.md) | [Introduction](README.md) | [Page suivante : Annexe Équipements →](08_annexe_equipements_reequilibres.md)
