idées mods Kotor 2

Règles de base :

- Créer la catégorie d'arme à 2M. Prend les 2 emplacements mais ne donne pas d'extra attaque.
- Attaquer en furtif assure un critique (ou simule l'effet d'un critique si limitation technique.

Equipement :
- [TODO] Revoir les statistiques des équipements et leur distribution en loot et chez les marchands (soutenir la viabilité de toutes les familles d'armes : Laser, Arme à résonance, Arme traditionnelle, Arme d'impact du Niv. 1 à 30).
- [TODO] Revoir les équipements craftables à l'établi (recettes, équilibrage des composants et cohérence avec les plafonds fixés).
- [TODO] Refonte totale de toutes les améliorations (upgrades) d'équipement, incluant :
  - Modifier les aspects améliorables selon la famille d'arme (ex: pas de cellule énergétique pour les armes Traditionnelles, 3 slots complets pour les armes à Résonance).
  - Armures intermédiaires : créer des upgrades propres aux armures intermédiaires qui combinent deux upgrades communes (sur-couches combinées et sous-couches combinées). Le moteur étant limité à 1 slot sur-couche + 1 slot sous-couche à l'établi, ces upgrades combinées sont réservées aux armures intermédiaires via un `UpgradeLevel` dédié sur les `.uti` (prérequis = type d'armure, aucun don requis).

Armure : 

- légère = esquive et mobilité (`+1/+2/+3` CA base et `10/20/30 %` esquive via dons, sans augmentation de CA via les stats du perso) — upgrade overlay.

- intermédiaire = armure technologique permettant furtivité sans ceinture + Course furtive + amplification des boucliers (durée `+100 %`, efficacité `×2/×3` via dons) + concept de défense spécialisée (meilleure RD sur un type par armure) + upgrades propres combinant deux upgrades communes (simulant 2 sur-couches + 2 sous-couches via `UpgradeLevel`).
 
- lourde = tank pur / encaisser les dégâts (`RD 4/-` native + dons `RD 3/4/5/-` et immunité tous dégâts `10/20/30 %`) et CA fixe sans dépendre de stats — upgrade underlay.