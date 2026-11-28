## Open decisions

### D1 — Quel framework pour l'interface graphique de l'outil ?

#### Faits

- Le `.venv` du dépôt tourne sous Python 3.14.7 ; ni `PySide6`, ni `CustomTkinter`, ni `PyInstaller` n'y sont installés aujourd'hui.
- Les deux candidats prennent en charge Python 3.14.
- `PySide6` (Qt Widgets) fournit nativement un conteneur d'assistant, des arborescences à cases à cocher, des infobulles et du tri et du filtrage ; sa licence LGPLv3 convient à un outil gratuit moyennant une mention de licence.
- `CustomTkinter` est écrite en Python pur au-dessus de `tkinter` (dernière publication le 24/06/2026) ; arborescence à cases, infobulles et navigation d'assistant sont à écrire à la main. L'interpréteur local embarque Tk 9.0 : le comportement de la bibliothèque avec cette version n'est pas vérifié.
- Taille du `.exe` et durée de lancement non mesurées : Qt devrait donner un fichier de plusieurs dizaines de Mo, plus lent à démarrer en `--onefile` ; Tk un fichier d'une dizaine de Mo.

#### Options

- A. `PySide6`, en n'embarquant que Qt Widgets.
- B. `CustomTkinter`.

#### Conséquences

- A : moins de code d'interface à écrire et à corriger pour les longues listes de dons et de pouvoirs avec prérequis ; `.exe` plus lourd et dépendance au rythme de publication de Qt.
- B : `.exe` léger et rapide à démarrer ; développement d'interface plus long (listes défilantes à cases, infobulles, pages de l'assistant) et rendu dépendant de la version de Tk empaquetée.

#### Suggestion

A : l'assistant de respec est surtout fait de longues listes à cases à cocher avec prérequis et recherche, ce que Qt Widgets fournit tout fait. B reste une option valable si la taille du `.exe` prime.

### D2 — Dans quelle(s) langue(s) est l'interface de l'outil ?

#### Faits

- Le mod est distribué en français et en anglais (installateur et guides joueur dans les deux langues).
- Les noms de dons, pouvoirs, classes et objets sont lus dans le `dialog.tlk` de l'installation du joueur : ils suivent déjà la langue de son jeu, quel que soit ce choix.
- Seuls les textes propres à l'outil (boutons, titres, messages, règles affichées) sont concernés : de l'ordre de 150 à 250 chaînes courtes.

#### Options

- A. Français et anglais, au choix de l'utilisateur (français par défaut).
- B. Français seulement pour la v1.0.
- C. Anglais seulement pour la v1.0.

#### Conséquences

- A : environ 10 à 15 % de travail d'interface en plus, et des textes anglais à faire relire par `Rédacteur-en-chef`.
- B ou C : v1.0 plus rapide, mais les joueurs de l'autre langue n'ont pas d'outil dans leur langue ; ajouter la langue plus tard suppose de reprendre toute l'interface.

#### Suggestion

A, le mod étant bilingue. Dans tous les cas, les textes seront regroupés dans un seul fichier dès le départ : coût nul, et B ou C restent possibles sans refonte.

### D3 — Que devient un objet exclusif à l'Overhaul lors d'une conversion vers Vanilla ?

#### Faits

- L'Overhaul ajoute 170 objets inconnus du jeu vanilla, en 4 familles : `ov1m_001` à `ov1m_069` (variantes à une main d'armes à deux mains), `ov_crys_*` (90 cristaux), `ov_hide_*` (10 armures de peaux de bêtes) et `ov_gam_adapt`.
- Une fois le mod désinstallé, ces objets n'ont plus de définition dans le jeu ; la réaction du jeu face à un objet introuvable n'est pas établie.
- Une table de correspondance vers l'arme à deux mains d'origine existe déjà pour `ov1m_*` (`mods/overhaul/gamorrean_swap_map.json`) ; il n'y en a aucune pour les trois autres familles.
- Les 473 autres objets du mod portent le nom d'un objet vanilla et devraient retrouver leur définition d'origine après désinstallation (à confirmer).

#### Options

- A. Remplacer par l'équivalent vanilla quand une correspondance existe, supprimer les autres, après affichage de la liste des changements.
- B. Tout supprimer, après affichage de la même liste.
- C. Les conserver tels quels.

#### Conséquences

- A : le joueur garde ses armes, en version à deux mains ; il faut établir les correspondances des cristaux et vérifier les peaux avec `Mod-Moteur`, donc plus de travail.
- B : le plus simple et le plus sûr ; le joueur perd ses cristaux et ses armures de peaux.
- C : aucun travail, mais des objets orphelins au comportement inconnu dans le jeu vanilla.

#### Suggestion

A, en deux temps : la v1.0 applique la correspondance `ov1m_*` (déjà existante) et supprime les trois autres familles, listées avant écriture ; les correspondances `ov_crys_*` et `ov_hide_*` sont vérifiées ensuite avec `Mod-Moteur`.

## Projects on hold
