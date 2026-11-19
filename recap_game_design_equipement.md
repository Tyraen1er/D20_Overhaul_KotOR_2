# Récapitulatif Game Design — Équipement, Upgrades, Armes & Armures

> Synthèse comparant les choix d'origine d'Obsidian / BioWare (et du JdR *Star Wars d20*) avec l'architecture de notre mod de rééquilibrage.  
> Sources de référence : [`armes_kotor2.md`](datas_kotor/armes_kotor2.md), [`equipement_ameliorations.md`](datas_kotor/equipement_ameliorations.md), [`equipement_armes_melee.md`](datas_kotor/equipement_armes_melee.md), [`equipement_armes_distance.md`](datas_kotor/equipement_armes_distance.md), [`WIP armes.csv`](Kotor%202%20-%20rééquilibrage%20-%20WIP%20armes.csv), [`WIP Améliorations.csv`](Kotor%202%20-%20rééquilibrage%20-%20WIP%20Améliorations.csv), [`Spécialisation d'arme.csv`](Kotor%202%20-%20rééquilibrage%20-%20Spécialisation%20d'arme.csv), [`Style de combat.csv`](Kotor%202%20-%20rééquilibrage%20-%20Style%20de%20combat.csv), [`spé Armure.csv`](Kotor%202%20-%20rééquilibrage%20-%20spé%20Armure.csv), [`spé carac.csv`](Kotor%202%20-%20rééquilibrage%20-%20spé%20carac.csv).

---

## 1. Utilité et Identité des Upgrades d'Équipement

> **Note technique importante sur les fichiers vanilla (`En cas de coup au but +10..+22`)** :  
> Dans [`equipement_ameliorations.md`](datas_kotor/equipement_ameliorations.md) et [`WIP Améliorations.csv`](Kotor%202%20-%20rééquilibrage%20-%20WIP%20Améliorations.csv), les propriétés traduites par `En cas de coup au but +10 / +14 / +18 / +22` sur les **Lunettes** et les **Émetteurs** ne sont pas des bonus de dégâts ou d'attaque : dans le moteur KotOR 2 (`iprp_onhit.2da`), ce sont des **effets de statut à l'impact (*On-Hit*) dont le chiffre indique le DD de sauvegarde (DD 10, 14, 18, 22)** — typiquement *Étourdissement (Stun)*, *Paralysie*, *Lenteur/Blessure (Slow/Wound)* ou *Horreur*.

### A. Upgrades d'Armes de Mêlée (`Poignée < Lame < Cellule`)

Dans notre mod, le budget offensif d'une arme de mêlée à 3 slots est réparti en **15 % Poignée / 35 % Lame / 50 % Cellule**, ce qui crée un déverrouillage progressif par famille :
- **Armes d'Impact (1 slot)** : *Poignée* uniquement (`15 %` du plafond d'établi).
- **Armes Traditionnelles (2 slots)** : *Poignée + Lame* (`50 %` du plafond d'établi).
- **Armes à Résonance (3 slots)** : *Poignée + Lame + Cellule* (`100 %` du plafond d'établi).

| Emplacement | Rôle & Identité Globale | Sous-familles (Lignées d'établi Obsidian) | Effets principaux (Vanilla & Mod) |
| :--- | :--- | :--- | :--- |
| **Poignée / Garde**<br>*(Grip — Slot 1)*<br>**Poids : 15 %** | **Maniement, Précision & Parade**<br>Ajuste l'équilibre de l'arme : toucher, défense (CA) ou léger appoint de tranchant. | • **Galbée** (*Contoured*)<br>• **À garde** (*Basket Hilt*)<br>• **Nagai**<br>• **Zabrak**<br>• **Agrinium** | • **Précision pure** : `+1 à +3 Attaque` (léger malus dégâts en vanilla)<br>• **Parade défensive** : `+1 à +3 CA` (léger malus Atq en vanilla)<br>• **Duel équilibré** : `+Attaque` + `+CA` (sans malus)<br>• **Agressif** : `+Attaque` + petits dégâts Tranchants contre `-CA`<br>• **Lestée** : Dégâts Tranchants légers (`+1d4` à `+2d6`) |
| **Lame**<br>*(Edge — Slot 2)*<br>**Poids : 35 %** | **Critique & Tranchant physique**<br>Définit le profil de létalité physique : plage critique (*Acéré*), puissance des critiques (*Critiques massifs*) ou tranchant brut. | • **Mullinine**<br>• **Dévaronien**<br>• **Neutronium / Quadranium**<br>• **Ostrine**<br>• **Ionite** | • **Acéré (*Keen*)** + Dégâts Tranchants (double la plage de critique)<br>• **Critiques massifs** (`+1d4` à `+3d8` sur crit) + léger Tranchant<br>• **Tranchant pur** : gros dés physiques réguliers (`+1d4` à `+3d6`)<br>• **Cryo-lame** : Dégâts de **Froid** + **Acéré**<br>• **Conductrice** : Dégâts **Ioniques** + bonus **vs Droïdes** |
| **Cellule d'énergie**<br>*(Energy Cell — Slot 3)*<br>**Poids : 50 %** | **Dégâts élémentaires lourds & Surcharge**<br>Cœur offensif des armes technologiques (Résonance) : gros dés d'énergie/élémentaires et effets secondaires violents. | • **Vibrations**<br>• **Alcaline**<br>• **Décharge sonique**<br>• **Ions** | • **Surcharge haute fréquence** : très gros dés Tranchants (`+1d6` à `+4d6`) contre `-1/-2 Attaque`<br>• **Énergie pure** : gros dés d'Énergie fiables sans malus (`+1d4` à `+3d6`)<br>• **Sonique & Choc** : dégâts **Soniques** + **Critiques massifs** (contre `-Attaque`)<br>• **Anti-Droïde / Bouclier** : dégâts **Ioniques** + **vs Droïdes** + **Critiques massifs** |

---

### B. Upgrades d'Armes à Distance (`Lunette < Cellule < Chambrage`)

À distance, la hiérarchie est inversée entre la cellule et le mécanisme interne : **15 % Lunette / 35 % Cellule / 50 % Chambrage** :
- **Tir Tactique (1 slot)** : *Lunette / Viseur* uniquement (`15 %` du plafond d'établi).
- **Tir d'Assaut & Tir Assassin (2 slots)** : *Lunette + Cellule d'énergie* (`50 %` du plafond d'établi).
- **Tir Pénétrant (3 slots)** : *Lunette + Cellule d'énergie + Chambrage* (`100 %` du plafond d'établi).

| Emplacement | Rôle & Identité Globale | Sous-familles (Lignées d'établi Obsidian) | Effets principaux (Vanilla & Mod) |
| :--- | :--- | :--- | :--- |
| **Lunette / Viseur**<br>*(Targeting — Slot 1)*<br>**Poids : 15 %** | **Visée, Critique & Effets ciblés (*On-Hit*)**<br>Permet de toucher les points vitaux : précision, *Acéré*, et effets de statut à l'impact (DD 10 à 22). | • **Précision** (*Pinpoint*)<br>• **Sniper** (*Crippling*)<br>• **Visée** (*Targeting*)<br>• **Mutilation** (*Maiming*) | • **Acquisition pure** : `+1 à +5 Attaque`<br>• **Tir chirurgical** : **Acéré (*Keen*)** + Effet *On-Hit* (Stun/Paralysie DD 10–22)<br>• **Télémétrie** : petits dégâts d'Énergie + Effet *On-Hit*<br>• **Tir incapacitant** : dégâts d'Énergie + Effet *On-Hit* (Blessure/Lenteur) |
| **Cellule / Pack d'énergie**<br>*(Power Pack — Slot 2)*<br>**Poids : 35 %** | **Munition énergétique & Critiques massifs**<br>Détermine la nature du plasma tiré : énergie pure, impulsion critique ou charge ionique. | • **Rylith**<br>• **Impulsions** (*Pulse*)<br>• **Ions** (*Ion Charger*) | • **Plasma dense** : dégâts d'**Énergie** réguliers élevés (`+1d4` à `+3d8`)<br>• **Surcharge critique** : **Critiques massifs** (`+1d6` à `+3d8`) + Énergie<br>• **Surcharge ionique** : dégâts **Ioniques** + **vs Droïdes** + **Critiques massifs** |
| **Chambrage**<br>*(Firing Chamber — Slot 3)*<br>**Poids : 50 %** | **Puissance de feu brute & Canon lourd**<br>Modifie la culasse et le canon (exclusif aux armes *Pénétrantes*) pour démultiplier les dégâts par tir. | • **Amplification / Séparateur**<br>• **Élargissement** (*Broadening*)<br>• **Mandalorien** | • **Surpuissance brute** : très gros dés d'**Énergie** (`+1d6` à `+4d6`)<br>• **Canon rayé** : `+1 à +4 Attaque` + **Critiques massifs** (`+1d6` à `+3d6`)<br>• **Culasse lourde** : très gros dégâts d'**Énergie** + `+Attaque` contre `-1/-2 CA` |

---

### C. Upgrades de Sabres Laser (`4 emplacements : Émetteur + Lentille + Cellule + 2 Cristaux`)

Les sabres laser ont accès à **tous leurs emplacements**, mais démarrent sans bonus de caractéristique inné particulier hors de leur arbre de dons (*Laser*) et de l'alchimie de leurs cristaux :

| Emplacement | Rôle & Identité Globale | Sous-familles / Archétypes | Effets principaux (Vanilla & Mod) |
| :--- | :--- | :--- | :--- |
| **Émetteur**<br>*(Emitter — 15 %)* | **Garde de parade vs Effet de contact**<br>Choisit entre la maîtrise défensive Jedi et l'effet de choc au contact de la lame. | • **Déflection / Clôture**<br>• **Expert**<br>• **Phobium / Désordre** | • **Parade Jedi** : `+1 à +3 CA` (et Déflection blaster)<br>• **Équilibre offensif** : `+CA` + petits dégâts d'Énergie<br>• **Onde de choc** : Effet *On-Hit* (Étourdissement/Horreur DD 14–22) + Énergie contre `-CA` |
| **Lentille**<br>*(Lens — 35 %)* | **Focalisation du faisceau (Critique & Toucher)**<br>Concentre le rayon pour gagner en précision, en plage critique (*Acéré*) ou en tranchant énergétique. | • **Synthétiseur / Kunda**<br>• **Gemme à rayon** (*Byrothsis*)<br>• **Adegan / Pontite / Vibratoire** | • **Focalisation** : `+1 à +4 Attaque` (+ `+CA` sur Kunda)<br>• **Faisceau chirurgical** : **Acéré (*Keen*)** + `+Attaque` ou `+Énergie`<br>• **Amplification optique** : gros dés d'**Énergie** (`+1d6` à `+3d6`) + **Critiques massifs** |
| **Cellule d'énergie**<br>*(Energy Cell — 50 %)* | **Générateur de puissance brute**<br>Fournit le gros des dégâts du sabre (Énergie pure, Électrique, Ionique ou Critique). | • **Diatium**<br>• **Telgorn Jolt**<br>• **Décharge** (*Discharge*)<br>• **Ions** | • **Flux Diatium** : très gros dégâts d'**Énergie** purs (`+1d6` à `+4d6`)<br>• **Surtension** : dégâts **Électriques**<br>• **Instabilité critique** : **Critiques massifs** + Énergie<br>• **Court-circuit** : dégâts **Ioniques** + **vs Droïdes** |
| **Cristaux de puissance**<br>*(2 slots)* | **Identité Force, Caractéristiques & Synergies**<br>Personnalise le sabre selon le build du Jedi (stats mentales/physiques, alignement, régénération, *Acéré*). | • **Cristal personnel (Nom)**<br>• **Stats / Force** (*Kaiburr, Ruusan, Kasha*)<br>• **Critique** (*Nextor, Velmorite, Opila*)<br>• **Survie / Alignement** (*Ankarès, Solari, Qixoni*) | • **Évolution liée au joueur** : `+Attaque`, `+FOR/DEX/CON/SAG/CHA`, `+Dégâts`, *Acéré*<br>• **Catalyseur de Force** : `+SAG`, `+CHA`, Régénération de PF<br>• **Létalité** : **Acéré**, **Critiques massifs** (`+2d6` à `+3d8`), `+Attaque`<br>• **Vitalité** : Régénération PV, Bonus de Défense, Dégâts élémentaires (Feu/Froid/Acide) |

---

### D. Upgrades d'Armures (`Sur-couche`, `Sous-couche`, et `Upgrades Combinées`)

Notre règle de mod associe chaque catégorie d'armure à une signature d'amélioration unique :
- **Bure Jedi (0 slot)** : aucun accès à l'établi d'armure.
- **Armure Légère (1 slot : Sur-couche standard)** : traitement externe uniquement.
- **Armure Lourde (1 slot : Sous-couche standard)** : doublure interne uniquement.
- **Armure Intermédiaire (2 slots : 1 Sur-couche combinée + 1 Sous-couche combinée)** : accès exclusif aux versions hybrides (`UpgradeLevel = 3`).

| Emplacement | Rôle & Identité Globale | Sous-familles | Effets principaux (Vanilla & Mod) |
| :--- | :--- | :--- | :--- |
| **Sur-couche standard**<br>*(Overlay — Armure Légère)* | **Bouclier externe & Revêtement tactique**<br>Protège contre les éléments, les tirs d'énergie, le balistique ou augmente la CA et les compétences. | • **Ablatif / Dissimulation énergétique**<br>• **Thermique / Sonique**<br>• **Balistique**<br>• **Plaques de Défense**<br>• **Camouflage / Sauvegardes** | • **Immunité Énergie** : `15 % à 40 %` vs Énergie<br>• **Immunité Élémentaire** : `25 % à 75 %` vs Feu / Froid / Sonique<br>• **Blindage balistique** : `10 % à 30 %` vs Tranchant / Perforant / Contondant<br>• **Défense active** : `+1 à +5 CA`<br>• **Spécialiste** : bonus Compétences / Jets de sauvegarde |
| **Sous-couche standard**<br>*(Underlay — Armure Lourde)* | **Exosquelette interne & Métabolisme**<br>Renforce le corps du porteur : caractéristiques physiques, régénération, souplesse DEX ou immunité aux coups critiques. | • **Renforcement** (*Strengthening*)<br>• **Biorestauratrice**<br>• **Assouplissement** (*Flex*)<br>• **Duracier**<br>• **Environnementale** | • **Servomoteurs** : `+1 à +5 FOR` et `+1 à +5 CON`<br>• **Survie** : **Régénération PV** (`+1 à +6`) + `+CON`<br>• **Articulations souples** : `+1 à +5 DEX` et hausse du **Bonus DEX max**<br>• **Plaques internes** : `+CA vs Physique` ou **Immunité aux Critiques / Drain** |
| **Sur-couche & Sous-couche Combinées**<br>*(Exclusif Armure Intermédiaire)* | **Polyvalence modulaire du Soldat**<br>Fusionne deux propriétés de tiers intermédiaires sur chaque slot, permettant à l'armure moyenne de cumuler 4 axes de bonus. | • **Sur-couche Combinée** (`u_a_over_16..30`)<br>• **Sous-couche Combinée** (`u_a_unde_16..30`) | • **Sur-couche Combinée** : cumule *Immunité Énergie/Élémentaire* **+** *Immunité Balistique* ou *+CA / Sauvegardes*<br>• **Sous-couche Combinée** : cumule *+FOR / +CON / +DEX* **+** *Régénération PV* ou *Immunité Critiques / Éléments* |

---

## 2. Identité des 8 Catégories (Familles) d'Armes

Le principe directeur de notre rééquilibrage est une **compensation croisée entre le potentiel d'établi (nombre de slots), les statistiques de base de l'arme, et la puissance des effets de Spécialisation Rang II/III** ([`Spécialisation d'arme.csv`](Kotor%202%20-%20rééquilibrage%20-%20Spécialisation%20d'arme.csv)) :

| Catégorie (Famille) | Slots d'Établi | Identité en 1–2 lignes | Mécanique de Spécialisation (Rangs I → II → III) |
| :--- | :---: | :--- | :--- |
| **1. Armes d'Impact**<br>*(Mêlée — Contondant)* | **1 slot**<br>*(Poignée — 15 %)* | **Contrôle de foule et anti-armure brute** : peu améliorables à l'établi, elles compensent par des dégâts de base solides, une multitude d'effets *On-Hit* natifs (étourdissement, choc) et une capacité unique à étourdir en chaîne tout en ignorant la défense et la RD des cibles sonnées. | • **I** : `+1d4` Contondant (`+1d8` à 2M)<br>• **II** : Coup critique → **Étourdissement 1 tour** (Vigueur `DD 10 + ½ niv + FOR/DEX/INT`)<br>• **III** : **Ignore 25 % CA et 50 % RD** sur cible étourdie ; tuer une cible étourdie → **Attaque d'opportunité gratuite** |
| **2. Armes Traditionnelles**<br>*(Mêlée — Tranchant)* | **2 slots**<br>*(Poignée + Lame — 50 %)* | **Létalité martiale pure et hémorragie** : privées de cellule d'énergie mais dotées des meilleures lames, elles misent sur d'excellentes statistiques de base (dés élevés ou critique `18-20` / `×3`) et un *Saignement* cumulable qui s'emballe dès que l'ennemi saigne. | • **I** : `+1d4` Tranchant (`+1d8` à 2M)<br>• **II** : **Saignement** pendant 2 tours (`Mod FOR` à 1M/D, `1,5× FOR` à 2M)<br>• **III** : **`+2 Attaque` et `+1d6` dégâts** contre toute cible qui saigne ; le saignement monte à **3 tours** |
| **3. Armes à Résonance**<br>*(Mêlée — Haute Fréquence)* | **3 slots**<br>*(Poignée + Lame + Cellule — 100 %)* | **Plafond technologique et duel d'attrition** : statistiques de base modestes mais **100 % personnalisables à l'établi** (3 slots complets) ; leurs vibrations affaiblissent l'attaque et les dégâts de l'ennemi (*Mutilation*) et déclenchent des ripostes gratuites. | • **I** : `+1d4` Tranchant (`+1d8` à 2M)<br>• **II** : Coup critique → **Mutilation 2 tours** (`-2 Attaque` et `-2 Dégâts` infligés par la cible)<br>• **III** : Sur cible mutilée, la mutilation passe à **`-4 Attaque / -4 Dégâts`** ; si la cible vous rate en mêlée → **Riposte gratuite** (1/tour) |
| **4. Armes Laser**<br>*(Mêlée — Énergie / Force)* | **4 slots**<br>*(Émetteur + Lentille + Cellule + 2 Cristaux)* | **Arme mystique évolutive à pénétration absolue** : réservée aux initiés de la Force, elle évolue via ses cristaux, dévie les tirs de blaster et finit par **ignorer 100 % des réductions de dégâts (RD)** tout en frappant un second ennemi à chaque critique. | • **I** : `+2 Attaque`, `+1d6` Énergie<br>• **II** : **Ignore 50 % des RD** ; coup critique → **+50 % de dégâts bonus** sur la cible<br>• **III** : **Ignore 100 % des RD** ; coup critique → **Enchaînement (*Cleave*) gratuit** sur un ennemi proche |
| **5. Tir d'Assaut**<br>*(Distance — Cadence & Saturation)* | **2 slots**<br>*(Lunette + Cellule — 50 %)* | **Déluge de feu à courte/moyenne portée** : conçu pour le double pistolet ou la répétition (`D`), il transforme le volume d'attaques en valeur sûre grâce à une chance de **tir supplémentaire gratuit** et un bonus de dégâts croissant sur la même cible. | • **I** : `+1d4` Énergie (`+1d8` à 2M)<br>• **II** : **15 % de chance par attaque** de déclencher un **tir supplémentaire immédiat** (`25 %` avec Tir Rapide)<br>• **III** : Chaque tir touchant la même cible dans le tour ajoute **`+2 dégâts` cumulables** ; la chance de tir bonus passe à **25 %** (`35 %` avec Tir Rapide) |
| **6. Tir Pénétrant**<br>*(Distance — Perforation lourde)* | **3 slots**<br>*(Lunette + Cellule + Chambrage — 100 %)* | **Artillerie anti-blindage hautement modulaire** : seule famille à distance dotée du **Chambrage (3 slots)**, elle compense sa lenteur par des dégâts massifs par tir qui **percent la RD, traversent les boucliers** et fracassent l'armure adverse (`-CA`). | • **I** : `+1d4` Énergie (`+1d8` à 2M)<br>• **II** : **Ignore 5 points de RD** et traverse **25 % des boucliers** ; coup critique → **`-2 CA`** à la cible pendant 2 tours<br>• **III** : **Ignore 10 points de RD** et traverse **50 % des boucliers** ; sur cible à armure brisée, **`+1d8` dégâts** et malus porté à **`-4 CA`** |
| **7. Tir Tactique**<br>*(Distance — Contrôle & Choc)* | **1 slot**<br>*(Lunette — 15 %)* | **Disruption et neutralisation de zone** : très peu d'établi (1 seul slot de lunette), mais des armes exotiques à forts dés de base ou effets natifs qui **renversent, ralentissent et achèvent** les ennemis contrôlés tout en brisant leurs boucliers. | • **I** : `+1d4` Sonique/Énergie (`+1d8` à 2M)<br>• **II** : Coup critique (ou Tir Déstabilisant) → **Renversement 1 tour** ou **Lenteur + `-2 Attaque` (2 tours)** (Réflexes `DD 10 + ½ niv + DEX/INT`)<br>• **III** : **`+1d6` dégâts** et **`+2` à la plage critique** contre toute cible ralentie/étourdie/renversée ; **dégâts doublés contre les boucliers** |
| **8. Tir Assassin**<br>*(Distance — Précision chirurgicale)* | **2 slots**<br>*(Lunette + Cellule — 50 %)* | **Chasseur de primes et tireur d'élite critique** : armes à large plage critique (`18-20`) ou multiplicateur violent (`×3`) qui appliquent une **Marque du chasseur** sur critique, garantissant l'escalade des critiques suivants et remboursant le coût en attaque des dons actifs. | • **I** : `+1 Attaque`, `+1d4` Énergie (`+1d8` à 2M)<br>• **II** : **`+1` au multiplicateur de critique** ; un critique applique **Marque du chasseur (2 tours)** (`+2` à la plage critique contre cette cible)<br>• **III** : Contre une cible marquée, **ignore le malus d'attaque** de Tir Précis / Tir Déstabilisant ; tout critique inflige un **Saignement / Brûlure interne (`2d6`/tour, 2 tours)** |

---

## 3. Rappel express : les 4 Postures & les 4 Catégories d'Armures

### Les 4 Postures de Combat ([`Style de combat.csv`](Kotor%202%20-%20rééquilibrage%20-%20Style%20de%20combat.csv))
- **Combat à une main (*Duel* — `1M`)** : **Précision, Défense et Critique** (`+1/+2/+3 Attaque et Défense`, puis au Rang III **`+1` à la plage critique** et `+50 %` FOR ou DEX aux dégâts). Idéal pour les builds critiques, tanks ou lanceurs de pouvoirs.
- **Combat à deux armes (*Ambidextrie* — `1M + 1M`)** : **Volume d'attaques et Dégâts par coup** (réduit les malus à `-4/-4`, `-2/-2`, puis `0/0` avec une **arme équilibrée** en main gauche, qui reçoit `+50 %` FOR ou DEX). Idéal pour multiplier les effets à l'impact (*Saignement*, *Stun*, *Tir d'Assaut*) et rentabiliser les gros upgrades d'établi.
- **Maniement d'Arme Lourde (`2M`)** : **Démultiplicateur de Caractéristique et Punition** (`150 %` FOR ou DEX de base, porté à **`200 % / 225 % / 250 %`** aux Rangs I–III + Attaque Puissante doublée en mêlée + **AoO gratuite** sur tout critique au Rang III). Idéal pour les armes à `1` ou `2` slots aux gros dés de base.
- **Arme à haute cadence (`D` — Double lame & Répétition)** : **Hybride 2-en-1** offrant **2 attaques à `0/0` de malus dès le départ** sans payer la ligne de dons *Ambidextrie* (`100 %` FOR/DEX sur le 1er coup, `50 %` sur le 2nd). Libère 3 dons pour investir dans l'armure, les compétences ou la Force.

### Les 4 Catégories d'Armures ([`spé Armure.csv`](Kotor%202%20-%20rééquilibrage%20-%20spé%20Armure.csv))
- **Bure Jedi (0 slot)** : **Mobilité, Force et Esquive pure** (`CA 3–5`, DEX illimitée, régénération PF, aucune restriction de pouvoirs, synergie *Art du Mouvement / Matukai / Nomi*).
- **Armure Légère — *Seconde Peau* (1 slot : Sur-couche)** : **Agilité, Esquive d'attaque et Critique** (`CA 5–7`, DEX max `5–8` étendu à `+2/+4/+6`, **10 % à 20 % d'esquive directe** au Rang II–III et `+1/+2` Attaque & Dégâts). Permet les pouvoirs de Force.
- **Armure Intermédiaire — *Blindage de Combat* (2 slots : Sur-couche + Sous-couche combinées)** : **Soldat modulaire et Maître des Boucliers** (`CA 7–9`, DEX max `3–4`, capacité des **boucliers d'énergie +25 % / +50 % / +100 %** et explosion Sonique à la rupture). Bloque les pouvoirs offensifs/buffs d'armure.
- **Armure Lourde — *Juggernaut* (1 slot : Sous-couche)** : **Forteresse inébranlable à RD massive** (`CA 10–13`, DEX max `1–2`, **`+5 / +10 / +15 RD` universelle**, `25 % à 100 %` d'immunité aux critiques/renversements et revanche `+1d6` quand touché).

---

## 4. Identité des 29 Armes (Tableau & Définition en 1–2 lignes)

> *Note : Le **Bâton Gaffi** est retiré du jeu. L'attribut **Équilibrée** annule le malus résiduel de `-2/-2` au Rang III d'Ambidextrie lorsqu'elle est équipée en main gauche (ou sur une arme `D`).*

### A. Armes de Mêlée (16 armes)

| Arme (et famille) | Posture & Équilibre | Stats Base (Mod) | Slots | Identité en 1–2 lignes & Build Idéal |
| :--- | :---: | :---: | :---: | :--- |
| **Matraque électrique**<br>*(Impact)* | `1M`<br>Équilibrée | `1d6` (`3,5`)<br>`20 / ×2` | **1**<br>*(Poignée)* | **Arme de contrôle rapide en main gauche** : dégâts de base légers mais équilibrée et dotée en vanilla d'effets d'étourdissement natifs ; idéale en **main gauche d'un build Impact Ambidextre** pour multiplier les chances de *Stun* sans malus de toucher. |
| **Gantelet énergétique**<br>*(Impact)* | `1M`<br>Standard | `1d10` (`5,5`)<br>`20 / ×3` | **1**<br>*(Poignée)* | **Uppercut lourd à une main** : le plus gros dé de base (`1d10`) et multiplicateur (`×3`) des armes 1M d'impact ; idéal en **Duel 1M ou main droite** pour assommer une cible et lui infliger un critique dévastateur pendant qu'elle est étourdie. |
| **Bâton de combat**<br>*(Impact)* | `2M`<br>Lourde | `2d6` (`7,0`)<br>`19-20 / ×2` | **1**<br>*(Poignée)* | **Bâton de maîtrise martiale à deux mains** : troque le multiplicateur brutal contre une **plage critique doublée (`19-20`)** qui déclenche l'étourdissement de *Spé Impact II* deux fois plus souvent ; idéal pour un **build 2M Contrôle / Enchaînement d'AoO** (et électro-bâton géonosien en vanilla). |
| **Masse énergétique**<br>*(Impact)* | `2M`<br>Lourde | `2d10` (`11,0`)<br>`20 / ×3` | **1**<br>*(Poignée)* | **Démolisseur pur à deux mains** : possède les dégâts de base les plus élevés de toutes les armes de mêlée non-laser (`2d10`, moy. `11`) et un critique `×3` ; idéale pour un **build Gamoréen / Arme Lourde 2M (`250 % FOR`)** qui écrase les cibles en un seul coup puissant. |
| **Épée courte**<br>*(Traditionnelle)* | `1M`<br>Équilibrée | `1d8` (`4,5`)<br>`19-20 / ×2` | **2**<br>*(Poig.+Lame)* | **Lame d'appoint agile et polyvalente** : équilibrée, dotée d'un bon critique (`19-20`) et de l'accès aux *Lames* d'établi ; idéale en **main gauche d'un duelliste Ambidextre** pour appliquer le *Saignement* dès l'ouverture et activer le bonus de `+2 Atq / +1d6` du Rang III. |
| **Épée longue**<br>*(Traditionnelle)* | `1M`<br>Standard | `1d12` (`6,5`)<br>`19-20 / ×2` | **2**<br>*(Poig.+Lame)* | **Épée de chevalier fiable et constante** : gros dé de base à une main (`1d12`) combiné à `19-20 / ×2` et 2 slots d'établi ; idéale en **Duel 1M ou main droite Ambidextre** pour un guerrier cherchant des dégâts réguliers élevés sans dépendre d'une cellule d'énergie. |
| **Sabre / Lame de guerre**<br>*(Traditionnelle)* | `1M`<br>Standard | `1d10` (`5,5`)<br>`18-20 / ×2` | **2**<br>*(Poig.+Lame)* | **Reine du critique physique à une main** : plage critique exceptionnelle de **`18-20` (15 % de base, 30 % avec une lame Acérée, 40 % en Duel III)** ; idéale pour un **build Critique Echani / Duel 1M** qui maximise les critiques massifs des lames Dévaroniennes. |
| **Hache gamoréenne**<br>*(Traditionnelle)* | `1M`<br>Standard | `1d12` (`6,5`)<br>`20 / ×3` | **2**<br>*(Poig.+Lame)* | **Hachoir brutal à une main** : même dé massif que l'épée longue (`1d12`), mais orienté vers des critiques explosifs **`×3`** plutôt que fréquents ; idéale pour un **build Force pure (Gamoréen)** en double hache ou bouclier énergétique qui mise sur les gros chiffres bruts. |
| **Épée à deux mains**<br>*(Traditionnelle)* | `2M`<br>Lourde | `2d10` (`11,0`)<br>`19-20 / ×2` | **2**<br>*(Poig.+Lame)* | **Claymore de guerre lourde** : combine le dé massif de `2d10`, une plage critique `19-20` et l'accès aux *Lames* d'établi ; idéale pour un **build Arme Lourde 2M Saignement** (`1,5× FOR` de saignement par tour + AoO sur critique). |
| **Pique de Force**<br>*(Traditionnelle)* | `2M`<br>Lourde | `2d8` (`9,0`)<br>`18-20 / ×3` | **2**<br>*(Poig.+Lame)* | **Arme d'hast d'élite au profil critique hors norme** : seule arme de mêlée combinant **`18-20` ET `×3`** avec le multiplicateur `250 % FOR` des armes `2M` ; idéale pour un **build Maître d'Arme Lourde Critique** qui déclenche une AoO gratuite (`Arme Lourde III`) sur 30 % de ses coups. |
| **Vibrolame**<br>*(Résonance)* | `1M`<br>Équilibrée | `1d8` (`4,5`)<br>`19-20 / ×2` | **3**<br>*(Complet)* | **Couteau suisse technologique équilibré** : dégâts de base modestes, mais **très améliorable (3 slots complets)** et sans malus en main gauche ; idéale comme **arme de main gauche universelle (Ambidextrie)** ou pour un **build critique/élémentaire** exploitant les cellules d'énergie. |
| **Vibro-épée**<br>*(Résonance)* | `1M`<br>Standard | `1d10` (`5,5`)<br>`19-20 / ×2` | **3**<br>*(Complet)* | **Épée haute fréquence de référence** : version plus lourde de la vibrolame (`1d10`) disposant des **3 emplacements d'établi** ; idéale en **main droite d'un build Ambidextre Résonance** ou en **Duel Riposte** (mutilation `-4 Atq/-4 Dég` + riposte gratuite quand l'ennemi rate). |
| **Vibro-double lame**<br>*(Résonance)* | `D`<br>Équilibrée | `1d10` (`5,5`)<br>`20 / ×2` | **3**<br>*(Complet)* | **Moulinet haute cadence économique en dons** : 2 attaques par round à `0/0` de malus sans prendre *Ambidextrie*, tout en appliquant les **3 slots d'établi** (notamment la Cellule d'énergie à 50 %) sur les deux extrémités ; idéale pour un **Sentinelle / Tech hybride**. |
| **Sabre laser court**<br>*(Laser)* | `1M`<br>Équilibrée | `2d6` (`7,0`)<br>`19-20 / ×2` | **4**<br>*(Sabre)* | **Shoto Jedi de main gauche** : équilibré, `19-20 / ×2` et doté des 4 emplacements de sabre ; idéal en **main gauche d'un Jedi Ambidextre (Kraith / Maraudeur / Maître d'Armes)** pour un toucher parfait (`0/0`) et 4 cristaux équipés au total sur les deux sabres. |
| **Sabre laser**<br>*(Laser)* | `1M`<br>Standard | `2d8` (`9,0`)<br>`19-20 / ×2` | **4**<br>*(Sabre)* | **L'arme emblématique du Chevalier Jedi** : excellente base (`2d8`, `19-20 / ×2`), ignore 100 % des RD au Rang III et profite pleinement du style **Duel 1M** (`+3 Atq/CA`, plage critique `18-20` de base, `15-20` avec cristal/lentille *Acéré*) ou de la main droite en Ambidextrie. |
| **Double sabre laser**<br>*(Laser)* | `D`<br>Équilibrée | `2d10` (`11,0`)<br>`20 / ×2` | **4**<br>*(Sabre)* | **Sabre de puissance pure à haute cadence** : plage critique réduite (`20 / ×2`), mais plus gros dé de base du jeu (`2d10`) appliqué deux fois par tour à `0/0` de malus avec les mêmes cristaux/cellule ; idéal pour un **build Attaque Puissante / Vitesse de Force** qui ne cherche pas le critique. |

---

### B. Armes à Distance (13 armes)

| Arme (et famille) | Posture & Équilibre | Stats Base (Mod) | Slots | Identité en 1–2 lignes & Build Idéal |
| :--- | :---: | :---: | :---: | :--- |
| **Pistolet de maintien**<br>*(Tir d'Assaut)* | `1M`<br>Équilibrée | `1d4` (`2,5`)<br>`19-20 / ×2` | **2**<br>*(Lun.+Cell.)* | **Pistolet léger de main gauche pour déluge de tirs** : faible dé de base (`1d4`) mais équilibré et `19-20` ; idéal en **main gauche d'un Pistolero Ambidextre** pour atteindre `0/0` de malus, empiler les `+2 dégâts/tir` de *Tir d'Assaut III* et déclencher des tirs gratuits. |
| **Pistolet blaster**<br>*(Tir d'Assaut)* | `1M`<br>Standard | `1d6` (`3,5`)<br>`19-20 / ×2` | **2**<br>*(Lun.+Cell.)* | **Arme de poing standard polyvalente** : équilibrée entre dégâts (`1d6`), critique (`19-20`) et améliorations (Lunette + Cellule) ; idéale en **main droite d'un build Double Pistolet Tir Rapide** (jusqu'à 35 % de chance de tir supplémentaire par attaque). |
| **Carabine blaster**<br>*(Tir d'Assaut)* | `2M`<br>Lourde | `1d10` (`5,5`)<br>`19-20 / ×2` | **2**<br>*(Lun.+Cell.)* | **Fusil d'assaut compact pour soldat mobile** : combine la mécanique de tirs supplémentaires de *Tir d'Assaut* avec le scaling **`250 % DEX` (ou `INT` Gand)** du *Maniement d'Arme Lourde (`2M`)* ; idéale pour un **commando à deux mains** qui veut la cadence sans jouer aux pistolets. |
| **Blaster à répétition léger**<br>*(Tir d'Assaut)* | `D`<br>Équilibrée | `1d8` (`4,5`)<br>`20 / ×2` | **2**<br>*(Lun.+Cell.)* | **Mitrailleuse légère autonome** : 2 tirs de base à `0/0` de malus (`100 % DEX` + `50 % DEX`) sans investir dans *Ambidextrie* ; avec *Tir Rapide* et *Tir d'Assaut III*, elle sature une cible de tirs tout en laissant le personnage libre de ses dons techniques ou de Force. |
| **Blaster lourd**<br>*(Tir Pénétrant)* | `1M`<br>Standard | `1d8` (`4,5`)<br>`19-20 / ×2` | **3**<br>*(Complet)* | **Canon de poing lourd ultra-améliorable** : seul pistolet standard disposant des **3 emplacements d'établi (dont le Chambrage à 50 %)** ; idéal en **Duel Pistolet 1M ou Double Blaster Lourd** pour percer les boucliers et la RD tout en profitant du plafond maximal d'upgrades. |
| **Fusil blaster**<br>*(Tir Pénétrant)* | `2M`<br>Lourde | `1d12` (`6,5`)<br>`19-20 / ×2` | **3**<br>*(Complet)* | **Fusil d'infanterie lourd de référence** : gros dé de base (`1d12`), **3 slots complets (Lunette + Cellule + Chambrage)** et scaling `250 % DEX/INT` ; l'arme à deux mains la plus fiable et complète du jeu pour **briser l'armure (`-4 CA`) et traverser 50 % des boucliers**. |
| **Blaster à répétition lourd**<br>*(Tir Pénétrant)* | `D`<br>Standard | `2d6` (`7,0`)<br>`19-20 / ×2` | **3**<br>*(Complet)* | **Sulfateuse lourde d'appui-feu** : combine **2 tirs natifs (`D`)**, un gros dé de base (`2d6`), une plage `19-20` et les **3 slots d'établi complets** ; l'arme de saturation lourde ultime en fin de jeu pour faire fondre les boss blindés et les droïdes. |
| **Pistolet sonique**<br>*(Tir Tactique)* | `1M`<br>Équilibrée | `1d6` (`3,5`)<br>`20 / ×2` | **1**<br>*(Lunette)* | **Disrupteur acoustique de main gauche** : un seul slot de lunette, mais équilibré et infligeant des **dégâts Soniques** (rarement résistés, dévastateurs contre les boucliers et les Jedi) ; idéal en **main gauche d'un build Tactique** pour appliquer *Lenteur / Renversement*. |
| **Pistolet ionique**<br>*(Tir Tactique)* | `1M`<br>Équilibrée | `1d6` (`3,5`)<br>`20 / ×2` | **1**<br>*(Lunette)* | **Neutralisateur anti-droïdes et anti-boucliers** : arme équilibrée à 1 slot spécialisée dans l'annihilation des droïdes, tourelles et barrières énergétiques (**dégâts doublés contre les boucliers** au Rang III de *Tir Tactique*). |
| **Fusil sonique**<br>*(Tir Tactique)* | `2M`<br>Lourde | `2d6` (`7,0`)<br>`20 / ×2` | **1**<br>*(Lunette)* | **Canon à ondes de choc à deux mains** : compense son unique slot d'établi par un dé massif (`2d6` Sonique) et le scaling `250 % DEX/INT` ; idéal avec **Tir Déstabilisant** pour renverser/ralentir les groupes d'élite et les achever avec `+1d6` et une plage critique élargie (`18-20` sur cible contrôlée). |
| **Fusil ionique**<br>*(Tir Tactique)* | `2M`<br>Lourde | `2d6` (`7,0`)<br>`20 / ×2` | **1**<br>*(Lunette)* | **Canon EMP lourd** : équivalent ionique du fusil sonique (`2d6`, `2M`, 1 slot), conçu pour pulvériser instantanément les boucliers ennemis et paralyser/détruire les boss mécaniques (Telos, Goto, Malachor). |
| **Pistolet désintégrateur**<br>*(Tir Assassin)* | `1M`<br>Standard | `1d6` (`3,5`)<br>`18-20 / ×2` | **2**<br>*(Lun.+Cell.)* | **Arme d'exécution chirurgicale à une main** : plage critique naturelle de **`18-20`** (qui monte à `16-20` sur cible marquée, voire `11-20` avec Lunette Sniper *Acérée* + Duel III) et multiplicateur porté à `×3` via *Tir Assassin II* ; idéal pour un **build Critique / Tir Précis**. |
| **Fusil désintégrateur / Arbalète Wookie**<br>*(Tir Assassin)* | `2M`<br>Lourde | `1d12` (`6,5`)<br>`18-20 / ×3` | **2**<br>*(Lun.+Cell.)* | **Le Sniper ultime de KotOR 2** : combine un dé de `1d12`, une plage critique **`18-20`**, un multiplicateur natif **`×3` (porté à `×4` avec *Tir Assassin II*)** et `250 % DEX/INT` à deux mains ; chaque critique pose la *Marque du chasseur*, inflige `2d6` de brûlure interne et donne une **AoO gratuite** (*Arme Lourde III*). |

---

## 5. Synthèse Visuelle : La Matrice de Game Design

```text
                       POTENTIEL D'ÉTABLI (MODULARITÉ)
             Faible (1 slot : 15%)      Moyen (2 slots : 50%)     Maximal (3-4 slots : 100%)
          ┌──────────────────────────┬──────────────────────────┬──────────────────────────┐
MÊLÉE     │ 1. IMPACT (Poignée)      │ 2. TRADITIONNELLE        │ 3. RÉSONANCE (3 slots)   │
          │ • Gros dés (jusqu'à 2d10)│    (Poignée + Lame)      │ • Base modeste (1d8-1d10)│
          │ • Stun 1t sur critique   │ • Critiques 18-20 ou ×3  │ • 100% des upgrades      │
          │ • Ignore 25% CA / 50% RD │ • Saignement (1.5× FOR)  │ • Mutilation (-4 Atq/Dég)│
          │ • AoO au kill d'étourdi  │ • +2 Atq / +1d6 si saigne│ • Riposte gratuite 1/t   │
          │                          │                          ├──────────────────────────┤
          │                          │                          │ 4. LASER (4 slots)       │
          │                          │                          │ • Évolue via Cristaux    │
          │                          │                          │ • Ignore 50% -> 100% RD  │
          │                          │                          │ • Cleave sur critique    │
──────────┼──────────────────────────┼──────────────────────────┼──────────────────────────┤
DISTANCE  │ 7. TIR TACTIQUE (Lunette)│ 5. TIR D'ASSAUT          │ 6. TIR PÉNÉTRANT         │
          │ • Sonique / Ionique natif│    (Lunette + Cellule)   │    (Lun.+Cell.+Chambrage)│
          │ • Renversement / Lenteur │ • 15% -> 35% tir gratuit │ • 100% des upgrades      │
          │ • +1d6 & +2 Crit sur CC  │ • +2 dégâts cumulés/tir  │ • Ignore 10 RD / 50% Bcl │
          │ • ×2 dégâts vs Boucliers │                          │ • Brise-armure (-4 CA)   │
          │                          ├──────────────────────────┤                          │
          │                          │ 8. TIR ASSASSIN          │                          │
          │                          │    (Lunette + Cellule)   │                          │
          │                          │ • Critique 18-20 / ×3->×4│                          │
          │                          │ • Marque (+2 plage crit) │                          │
          │                          │ • Ignore malus Tir Précis│                          │
          └──────────────────────────┴──────────────────────────┴──────────────────────────┘
```

---

## 6. Trois pistes de réflexion pour la suite

1. **Valoriser les effets *On-Hit* (`En cas de coup au but DD 10..22`) sur les Lunettes et Émetteurs** :  
   Les armes de **Tir Tactique** n'ont accès qu'à un seul emplacement : la **Lunette / Viseur**. Or, dans le jeu de base, Obsidian avait placé des effets *On-Hit* (Stun, Paralysie, Lenteur/Mutilation) sur 3 des 4 lignées de lunettes (*Sniper*, *Visée*, *Mutilation*). Conserver et bien calibrer ces effets de statut sur les lunettes permet au joueur *Tir Tactique* d'utiliser son unique slot pour déclencher encore plus facilement les conditions (*ralenti / étourdi*) qui activent son Rang III (`+1d6` dégâts et `+2` plage critique).
2. **L'identité des armes uniques `.uti` trouvées en jeu (Drop / Quêtes)** :  
   Dans [`equipement_armes_melee.md`](datas_kotor/equipement_armes_melee.md), Obsidian compensait le manque d'établi des armes d'Impact (*Matraques*, *Bâtons*, *Gantelets*) et Traditionnelles (*Lame mortelle rodienne*, *Fendoir gamoréen*, *Pique de Force*) en donnant à leurs versions Tier 2/3/Uniques des **effets natifs pré-intégrés** (ex. *Électro-bâton géonosien* avec dégâts électriques + poison ; *Pique de Force* avec étourdissement 25 % DD 14). C'est un excellent levier pour que le loot des armes à 1 ou 2 slots reste excitant tout au long du jeu.
3. **La distinction Pistolet Sonique vs Pistolet Ionique (et Fusil Sonique vs Ionique)** :  
   Actuellement dans [`WIP armes.csv`](Kotor%202%20-%20rééquilibrage%20-%20WIP%20armes.csv), le couple *Sonique* et le couple *Ionique* ont exactement les mêmes dés (`1d6` en pistolet, `2d6` en fusil) et le même critique (`20 / ×2`). Pour leur donner une personnalité encore plus marquée au sein du *Tir Tactique*, on pourrait par exemple donner au **Sonique** une plage critique de `19-20 / ×2` (plus de chances de déclencher le *Renversement/Lenteur* sur critique du Rang II contre les organiques/Jedi), et laisser l'**Ionique** en `20 / ×2` (ou `20 / ×3`) avec son bonus natif anti-droïdes/boucliers.
