"""Chemins centralisés du dépôt KotOR 2 D20-Overhaul.

Évite la duplication de chemins relatifs en dur dans les scripts de `tools/`.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Couche utilisateur : tables CSV FR et traductions EN
CSV_DIR = ROOT / "csv"
CSV_FR_DIR = CSV_DIR / "fr"
CSV_EN_DIR = CSV_DIR / "en"

CSV_FEATS = CSV_FR_DIR / "Kotor 2 - rééquilibrage - WIP Feats.csv"
CSV_WEAPONS = CSV_FR_DIR / "Kotor 2 - rééquilibrage - armes.csv"
CSV_ARMORS = CSV_FR_DIR / "Kotor 2 - rééquilibrage - Armures.csv"
CSV_POWERS = CSV_FR_DIR / "Kotor 2 - rééquilibrage - Spé Pouvoirs.csv"
CSV_CRAFT = CSV_FR_DIR / "Kotor 2 - rééquilibrage - Craft.csv"
CSV_UPGRADES = CSV_FR_DIR / "Kotor 2 - rééquilibrage - Améliorations.csv"

GEAR_CSV_NAMES = [
    "Kotor 2 - rééquilibrage - Casques.csv",
    "Kotor 2 - rééquilibrage - Implants.csv",
    "Kotor 2 - rééquilibrage - Gants.csv",
    "Kotor 2 - rééquilibrage - Ceintures.csv",
    "Kotor 2 - rééquilibrage - Brassards.csv",
    "Kotor 2 - rééquilibrage - Armures items.csv",
]
GEAR_CSVS = [CSV_FR_DIR / name for name in GEAR_CSV_NAMES]

# Ressources de référence et analyses extraites
REF_DIR = ROOT / "_reference"
REF_2DA = REF_DIR / "2da"
REF_SCRIPTS = REF_DIR / "scripts"
REF_TLK_DIR = REF_DIR / "tlk"
BASE_TLK = REF_TLK_DIR / "dialog.tlk.bak"
REF_ANALYSES_KOTOR = REF_DIR / "analyses_kotor"
REF_JDR = REF_DIR / "jdr"

# Sorties de build, documentation et distribution
OUT_MOD = ROOT / "mods" / "overhaul"
OVR_DIR = OUT_MOD / "Override"
DOCS_DIR = ROOT / "docs"
INSTALLER_DIR = ROOT / "installer"
DIST_DIR = ROOT / "dist"

# Nids Trieste et documents de conception
NESTS_DIR = ROOT / "nests"
TABLEAU_ENNEMIS_MD = REF_ANALYSES_KOTOR / "tableau_ennemis.md"
