# Star Wars: KotOR II — D20 Overhaul

Refonte complète d20 de **Star Wars: Knights of the Old Republic II — The Sith Lords** (compatible TSLRCM), disponible en **français** et en **anglais** via installateur multilingue TSLPatcher.

![D20 Overhaul](docs/assets/D20%20Overhaul%20Thumbnail.jpg)

## Pour les joueurs

- **Installer le mod** : récupérer l'archive dans [`dist/`](dist/) ou lancer `installer/INSTALL.exe` (choisir Français ou English).
- **Guides du joueur** :
  - 🇫🇷 [Guide du Joueur (FR)](docs/README.md) · [Version PDF FR](docs/KotOR2_D20_Overhaul_Guide_Joueur_FR.pdf)
  - 🇬🇧 [Player Guide (EN)](docs/en/README.md) · [PDF Version EN](docs/KotOR2_D20_Overhaul_Player_Guide_EN.pdf)
- **Contribuer à une traduction** : voir [`docs/HOW_TO_TRANSLATE.md`](docs/HOW_TO_TRANSLATE.md).

## Architecture du dépôt

| Dossier | Rôle |
| :--- | :--- |
| [`csv/fr/`](csv/fr/) & [`csv/en/`](csv/en/) | Tables CSV de référence (couche utilisateur FR et localisation EN) |
| [`tools/`](tools/) | Pipeline Python de build, simulation DPR (`dpr_check.py`), génération PDF, vérification (`verify_passes123.py`) et chemins centralisés (`paths.py`) |
| [`docs/`](docs/) | Guides du joueur FR/EN (Markdown + PDF) et ressources visuelles (`docs/assets/`) |
| [`installer/`](installer/) & [`dist/`](dist/) | Installateur multilingue TSLPatcher (`namespaces.ini`) et archives de distribution |
| [`mods/`](mods/) | Sorties de build locales (`mods/overhaul/`) et tables d'IDs générées |
| [`_reference/`](_reference/) | Ressources vanilla extraites (`2da/`, `scripts/`), analyses KotOR 2 (`analyses_kotor/`), références Star Wars d20 (`jdr/`) et outils tiers |
| [`nests/`](nests/) | Organisation interne par domaines (design, moteur, utilitaire, lore/distribution, retours joueurs) |

## Chaîne de build & vérification (développeurs)

Toutes les commandes utilisent l'environnement virtuel local `.venv` (Python 3.14 + `pykotor` patché — voir les notes techniques dans [`nests/Mod-Moteur/documentation/pieges_pykotor_et_odyssey.md`](nests/Mod-Moteur/documentation/pieges_pykotor_et_odyssey.md)) :

```powershell
.\.venv\Scripts\python.exe tools\build_overhaul.py    # Génère les .2da et dialog.tlk -> mods/overhaul/
.\.venv\Scripts\python.exe tools\build_items.py       # Génère les .uti / .dlg -> mods/overhaul/Override/
.\.venv\Scripts\python.exe tools\build_scripts.py     # Compile les .nss -> .ncs (nwnnsscomp C++)
.\.venv\Scripts\python.exe tools\build_enemies.py     # Applique les profils ennemis (.utc)
.\.venv\Scripts\python.exe tools\build_installer.py   # Assemble l'installateur TSLPatcher + archive dist/
.\.venv\Scripts\python.exe tools\verify_passes123.py  # Suite de vérification complète (177 tests)
```

Simulateur d'équilibrage DPR :

```powershell
.\.venv\Scripts\python.exe tools\dpr_check.py --selftest
.\.venv\Scripts\python.exe tools\dpr_check.py --feats "Duel 3,Spécialisation Arme Laser 3,Coup critique 3"
```
