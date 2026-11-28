#!/usr/bin/env python3
"""KotOR 2 Overhaul — Générateur de l'installateur TSLPatcher multilingue (EN par défaut / FR).

Crée une distribution complète de l'installateur dans `installer/` :
  - `INSTALL.exe` (exécutable TSLPatcher de stoffe / K2CP)
  - `Readme.rtf` & `HOW_TO_TRANSLATE.md` (documentation utilisateur & tuto moddeurs)
  - `tslpatchdata/namespaces.ini` (menu de choix de langue : English par défaut, Français)
  - `tslpatchdata/changes_en.ini` & `changes_fr.ini`
  - `tslpatchdata/info_en.rtf` & `info_fr.rtf`
  - `tslpatchdata/append_en.tlk` & `append_fr.tlk` (232 chaînes TLK)
  - `tslpatchdata/kreia_en.dlg` / `kreia_fr.dlg` & `ov_gam_conv_en.dlg` / `ov_gam_conv_fr.dlg`
  - `tslpatchdata/*.2da` (les 10 tables TSLRCM de base requises par TSLPatcher)
  - `tslpatchdata/*.uti`, `*.utc`, `*.ncs`, `*.utp` (fichiers communs ; `.uti` bilingues EN+FR natifs)

Garanties de compatibilité TSLPatcher classique (`INSTALL.exe`) & HoloPatcher :
  - Utilise uniquement des directives nativement supportées par `INSTALL.exe` (`namespaces.ini`, `!SourceFile`, `!SaveAs`, `Replace`).
  - Nettoyage complet de `tslpatchdata/` à chaque build (aucun fichier fantôme).
  - Les 10 `.2da` de référence sont incluses dans `tslpatchdata/` (indispensable sur jeu propre).
  - Cellules effacées dans `ChangeRow` écrites en `****`.
  - `ExclusiveColumn=label` sur tous les ajouts de lignes 2DA (idempotent & compatible K2CP).
  - `Replace0..N` dans `[install_folder0]` et `[GFFList]` (permet les mises à jour propres).
  - Résolution dynamique des `StrRef` (`[TLKList]`) et des `BaseItem` / `MOD_GAMORREAN_2` (`2DAMEMORY`).
"""

from __future__ import annotations

import csv
import shutil
from pathlib import Path

from pykotor.common.language import Gender, Language
from pykotor.resource.formats.tlk import TLK, read_tlk, write_tlk
from pykotor.resource.formats.twoda import read_2da
from pykotor.resource.generics.dlg import read_dlg, write_dlg
from pykotor.resource.generics.uti import read_uti, write_uti

from build_overhaul import sanitize_tlk  # repli CP1252 (→, ↔, ≤, ≥, −) : le TLK EN est encode en Windows-1252
from paths import (
    BASE_TLK,
    CSV_EN_DIR as EN_CSV_DIR,
    CSV_POWERS,
    DIST_DIR,
    INSTALLER_DIR,
    OUT_MOD,
    OVR_DIR,
    REF_2DA,
    ROOT,
)

MOD_TLK = OUT_MOD / "dialog.tlk"

TSL_DATA_DIR = INSTALLER_DIR / "tslpatchdata"
RELEASE_ZIP_NAME = "KotOR2_D20_Overhaul_v1.0.zip"
PDF_GUIDES = [
    ROOT / "docs" / "KotOR2_D20_Overhaul_Guide_Joueur_FR.pdf",
    ROOT / "docs" / "KotOR2_D20_Overhaul_Player_Guide_EN.pdf",
]
HOW_TO_TRANSLATE_MD = ROOT / "docs" / "HOW_TO_TRANSLATE.md"

SOURCE_INSTALL_EXE = Path(r"C:\Users\emman\Desktop\kotor 2 updates\K2CP_v1.6.3\INSTALL.exe")
if not SOURCE_INSTALL_EXE.exists():
    SOURCE_INSTALL_EXE = ROOT / "_reference" / "autres_mods" / "Content Pack-57-1-67-1616632489" / "TSLPatcher.exe"

# Ordre important : feat.2da AVANT baseitems.2da afin que les 2DAMEMORY de dons soient résolus avant baseitems
TABLE_NAMES = [
    "feat.2da",
    "featgain.2da",
    "classpowergain.2da",
    "baseitems.2da",
    "spells.2da",
    "itemcreate.2da",
    "itemcreatemira.2da",
    "forceshields.2da",
    "iprp_resistcost.2da",
    "autobalance.2da",
]

# Traductions EN exactes des 33 chaînes internes/renommées absentes des colonnes CSV directes
EN_TLK_FALLBACK_MAP: dict[str, str] = {
    "Voie des Arcanes": "Path of the Arcane",
    "[Mod D20-Overhaul]\nMaîtrise avancée de la Force ouvrant l'accès au Rang III d'Éveil de Force (Maître Jedi, Seigneur Sith et Kreia Niv. 15+).": (
        "[Mod D20-Overhaul]\nAdvanced Force mastery unlocking Rank III Force Awakening (Jedi Master, Sith Lord, and Kreia Lv. 15+)."
    ),
    "Voie de l'Ombre": "Path of the Shadow",
    "[Mod D20-Overhaul]\nMaîtrise tactique et furtive ouvrant l'accès aux dons de prestige hybrides (Protecteur, Assassin, Visas Niv. 15+ et spécialistes).": (
        "[Mod D20-Overhaul]\nTactical and stealth mastery unlocking hybrid prestige feats (Watchman, Assassin, Visas Lv. 15+, and specialists)."
    ),
    "Voie Martiale": "Martial Path",
    "[Mod D20-Overhaul]\nMaîtrise martiale avancée ouvrant l'accès aux spécialisations d'armure de Rang III (Maître d'Armes, Maraudeur et Soldat).": (
        "[Mod D20-Overhaul]\nAdvanced martial mastery unlocking Rank III armor specializations (Weapon Master, Marauder, and Soldier)."
    ),
    "Endurance d'Élite": "Elite Endurance",
    "[Mod D20-Overhaul]\nRésistance aux dégâts passive de sous-boss et de boss (RD 2 / 5 / 8 selon le palier de niveau).": (
        "[Mod D20-Overhaul]\nPassive damage reduction for sub-bosses and bosses (DR 2 / 5 / 8 depending on level tier)."
    ),
    "Prémonition du combat (Echani)": "Battle Precognition (Echani)",
    "[Mod D20-Overhaul]\nEnseignement de la Servante : accorde passivement +10 % d'esquive au corps à corps (remplace le bonus SAG à la CA).": (
        "[Mod D20-Overhaul]\nHandmaiden's teaching: passively grants +10% melee dodge (replaces the WIS bonus to Defense)."
    ),
    "Adaptation Gamorréenne (2M / 1M)": "Gamorrean Adaptation (2H / 1H)",
    "[Mod D20-Overhaul]\nPermet à un personnage possédant Raffinement Gamorréen II d'ouvrir en posture hors combat l'établi d'amélioration portatif à tout moment (indépendamment de l'arme équipée) ou de convertir l'arme 2M / Double tenue en main droite vers son équivalent à une main (1M), et inversement.": (
        "[Mod D20-Overhaul]\nAllows a character with Gamorrean Refinement II to open the portable upgrade workbench at any time out of combat (regardless of equipped weapon), or to convert the 2H / Double weapon held in the main hand to its 1H equivalent and vice versa."
    ),
    "Écho des Liens I": "Echo of Bonds I",
    "Écho des Liens II": "Echo of Bonds II",
    "Écho des Liens III": "Echo of Bonds III",
    "Déchirure de la Force I": "Force Rift I",
    "Déchirure de la Force II": "Force Rift II",
    "Déchirure de la Force III": "Force Rift III",
    "Stigmate de Force I": "Force Stigma I",
    "Stigmate de Force II": "Force Stigma II",
    "Stigmate de Force III": "Force Stigma III",
    "Spectre de la Force I": "Force Specter I",
    "Spectre de la Force II": "Force Specter II",
    "Spectre de la Force III": "Force Specter III",
    "Cicatrice de Force I": "Force Scar I",
    "Cicatrice de Force II": "Force Scar II",
    "Cicatrice de Force III": "Force Scar III",
    "Festin de mort": "Death Feast",
    "Résistance 2/-": "Resistance 2/-",
    "Résistance 3/-": "Resistance 3/-",
    "Résistance 4/-": "Resistance 4/-",
    "Résistance 6/-": "Resistance 6/-",
    "Résistance 12/-": "Resistance 12/-",
}

# Traductions EN exactes des dialogues ajoutés (kreia.dlg & ov_gam_conv.dlg)
EN_DLG_MAP: dict[str, str] = {
    # kreia.dlg
    "[Vous ne pouvez pas parler à Kreia maintenant.]": "[You cannot speak with Kreia right now.]",
    "Très bien. Quelle caractéristique principale souhaitez-vous ancrer dans votre cristal ?": (
        "Very well. Which primary attribute do you wish to anchor into your crystal?"
    ),
    "Caractéristique principale : Force. Quelle caractéristique secondaire souhaitez-vous y associer ?": (
        "Primary attribute: Strength. Which secondary attribute do you wish to pair with it?"
    ),
    "Caractéristique principale : Dextérité. Quelle caractéristique secondaire souhaitez-vous y associer ?": (
        "Primary attribute: Dexterity. Which secondary attribute do you wish to pair with it?"
    ),
    "Caractéristique principale : Constitution. Quelle caractéristique secondaire souhaitez-vous y associer ?": (
        "Primary attribute: Constitution. Which secondary attribute do you wish to pair with it?"
    ),
    "Caractéristique principale : Intelligence. Quelle caractéristique secondaire souhaitez-vous y associer ?": (
        "Primary attribute: Intelligence. Which secondary attribute do you wish to pair with it?"
    ),
    "Caractéristique principale : Sagesse. Quelle caractéristique secondaire souhaitez-vous y associer ?": (
        "Primary attribute: Wisdom. Which secondary attribute do you wish to pair with it?"
    ),
    "Caractéristique principale : Charisme. Quelle caractéristique secondaire souhaitez-vous y associer ?": (
        "Primary attribute: Charisma. Which secondary attribute do you wish to pair with it?"
    ),
    "[Kreia est inconscient, vous ne pouvez pas lui parler pour le moment.]": (
        "[Kreia is unconscious, you cannot speak with her right now.]"
    ),
    "Nous n'interviendrons pas tant que nous ne posséderons pas un sabre laser.": (
        "We shall not intervene until we possess a lightsaber."
    ),
    "[Visas doit avoir un sabre laser équipé.]": "[Visas must have a lightsaber equipped.]",
    "[Vous devez posséder 2 sabres laser à une lame, un pour vous-même et un pour Visas.]": (
        "[You must possess 2 single-bladed lightsabers, one for yourself and one for Visas.]"
    ),
    "Laissez la Force guider l'accord automatiquement (2 meilleures caractéristiques).": (
        "Let the Force guide the attunement automatically (2 highest attributes)."
    ),
    "Je souhaite choisir moi-même les deux caractéristiques de mon cristal.": (
        "I wish to choose the two attributes of my crystal myself."
    ),
    "Force (caractéristique principale)": "Strength (primary attribute)",
    "Dextérité (caractéristique principale)": "Dexterity (primary attribute)",
    "Constitution (caractéristique principale)": "Constitution (primary attribute)",
    "Intelligence (caractéristique principale)": "Intelligence (primary attribute)",
    "Sagesse (caractéristique principale)": "Wisdom (primary attribute)",
    "Charisme (caractéristique principale)": "Charisma (primary attribute)",
    "Force (caractéristique secondaire)": "Strength (secondary attribute)",
    "Dextérité (caractéristique secondaire)": "Dexterity (secondary attribute)",
    "Constitution (caractéristique secondaire)": "Constitution (secondary attribute)",
    "Intelligence (caractéristique secondaire)": "Intelligence (secondary attribute)",
    "Sagesse (caractéristique secondaire)": "Wisdom (secondary attribute)",
    "Charisme (caractéristique secondaire)": "Charisma (secondary attribute)",
    # ov_gam_conv.dlg
    (
        "[ÉTABLI PORTATIF GAMORRÉEN — ADAPTATION 2M/D ET 1M]\n\n"
        "Permet d'ouvrir l'établi d'amélioration en tout lieu, ou de convertir votre arme à deux mains (2M) "
        "ou haute cadence / double (D) tenue en main droite (mêlée et distance) vers son équivalent à une main (1M), "
        "et inversement.\n\n"
        "ATTENTION — AMÉLIORATIONS :\n"
        "Les améliorations montées sur l'arme ne peuvent pas être transférées automatiquement lors de la conversion.\n"
        "• Utilisez d'abord « Ouvrir l'établi d'amélioration » pour RETIRER toutes les pièces de votre arme "
        "(sinon elles seront DÉFINITIVEMENT PERDUES) ;\n"
        "• Utilisez ensuite « Convertir l'arme équipée » ;\n"
        "• Rouvrez enfin l'établi pour remonter vos pièces sur l'arme convertie."
    ): (
        "[GAMORREAN PORTABLE WORKBENCH — 2H/D & 1H ADAPTATION]\n\n"
        "Allows you to open the upgrade workbench anywhere, or to convert the two-handed (2H) or "
        "high-rate / double-bladed (D) weapon held in your main hand (melee or ranged) into its "
        "one-handed (1H) equivalent, and vice versa.\n\n"
        "WARNING — UPGRADES:\n"
        "Upgrades installed on the weapon cannot be transferred automatically during conversion.\n"
        "• First select 'Open Upgrade Workbench' to REMOVE all upgrades from your weapon "
        "(otherwise they will be PERMANENTLY LOST);\n"
        "• Then select 'Convert Equipped Main-Hand Weapon';\n"
        "• Finally reopen the workbench to reinstall your upgrades on the converted weapon."
    ),
    (
        "[ÉTABLI PORTATIF GAMORRÉEN]\n\n"
        "L'établi d'amélioration portatif est prêt à être utilisé.\n\n"
        "(Conversion 2M/D - 1M indisponible : aucune arme à deux mains, double, haute cadence ou déjà adaptée "
        "en 1M n'est actuellement équipée en main droite.)"
    ): (
        "[GAMORREAN PORTABLE WORKBENCH]\n\n"
        "The portable upgrade workbench is ready to use.\n\n"
        "(2H/D - 1H conversion unavailable: no two-handed, double-bladed, heavy-rate, or 1H-adapted "
        "weapon is currently equipped in your main hand.)"
    ),
    (
        "[ÉTABLI PORTATIF GAMORRÉEN]\n\n"
        "Utilisation impossible pour le moment.\n"
        "Vérifiez que :\n"
        "- Ce personnage possède le don Raffinement Gamorréen II ;\n"
        "- Vous êtes en posture hors combat."
    ): (
        "[GAMORREAN PORTABLE WORKBENCH]\n\n"
        "Cannot be used right now.\n"
        "Please make sure that:\n"
        "- This character has the Gamorrean Refinement II feat;\n"
        "- You are currently out of combat."
    ),
    "1. Ouvrir l'établi d'amélioration (retirer ou remonter mes pièces)": (
        "1. Open Upgrade Workbench (remove or reinstall upgrades)"
    ),
    "2. Convertir l'arme équipée en main droite (2M/D - 1M)": (
        "2. Convert Equipped Main-Hand Weapon (2H/D <-> 1H)"
    ),
    "3. Annuler": "3. Cancel",
    "1. Ouvrir l'établi d'amélioration": "1. Open Upgrade Workbench",
    "2. Fermer": "2. Close",
    "Fermer": "Close",
}


def rtf_escape(text: str) -> str:
    """Échappe le texte pour le format RTF (caractères accentués et spéciaux)."""
    out = []
    for char in text:
        code = ord(char)
        if char == "\\":
            out.append("\\\\")
        elif char == "{":
            out.append("\\{")
        elif char == "}":
            out.append("\\}")
        elif char == "\n":
            out.append("\\par\n")
        elif code > 127:
            out.append(f"\\u{code}?")
        else:
            out.append(char)
    return "".join(out)


def generate_info_rtf(lang: str = "fr") -> str:
    """Génère le texte RTF affiché dans la fenêtre de TSLPatcher (EN ou FR)."""
    if lang == "en":
        title = "Star Wars: Knights of the Old Republic II - The Sith Lords"
        subtitle = "D20 Overhaul Mod - Version 1.0 (English)"
        content = (
            "Welcome to the KotOR 2 D20 Overhaul installer!\n\n"
            "MOD OVERVIEW:\n"
            "This mod overhauls KotOR 2's combat, progression, and equipment systems to restore "
            "rigorous d20 Star Wars Roleplaying Game (WotC) mathematical balance:\n\n"
            "1. FEATS & FORCE POWERS:\n"
            "  - 78 new d20 feats (Weapon family specializations, combat styles, attribute feats)\n"
            "    and the 6 Prestige Class powers completely overhauled (including 2 brand-new powers).\n"
            "  - 33 redundant or unbalanced vanilla feats cleanly hidden.\n"
            "  - Rebalanced feat & power progression budgets (22/18/15 feats over 30 levels).\n\n"
            "2. WEAPONS, ARMOR & SHIELDS:\n"
            "  - Full d20 weapon profile overhaul (damage dice, critical ranges, 1H/2H wielding).\n"
            "  - Light, medium, and heavy armors rebalanced with d20 AC and Max DEX caps.\n"
            "  - Energy shield overhaul and Force power armor restrictions revised.\n\n"
            "3. WORKBENCH & EQUIPMENT:\n"
            "  - Expanded workbench (and Mira's rocket launcher) with base weapons, level locks,\n"
            "    and 60 armor upgrades (30 underlays + 30 overlays exclusive to Medium Armor).\n"
            "  - Lore-accurate stat caps across helmets, gloves, implants, belts, and armbands.\n"
            "  - Exile's personal crystal customizable via Kreia (automatic or manual choice).\n\n"
            "4. ENEMY BALANCING:\n"
            "  - 316 creatures & enemies rebalanced + calibrated boss autobalance.\n\n"
            "COMPATIBILITY:\n"
            "  - Compatible with TSLRCM (The Sith Lords Restored Content Mod) 1.8.6 / 2022.\n"
            "  - Compatible with K2CP (KotOR 2 Community Patch) v1.6.3 (install K2CP first).\n"
            "  - Dynamic merging with automatic backup in 'backup/'.\n\n"
            "INSTRUCTIONS:\n"
            "Click 'Install Mod' below and select your KotOR 2 ROOT directory "
            "(the folder containing swkotor2.exe, NOT the Override subfolder).\n"
        )
        deflang = "1033"
    else:
        title = "Star Wars: Knights of the Old Republic II - The Sith Lords"
        subtitle = "D20 Overhaul Mod - Version 1.0 (Français)"
        content = (
            "Bienvenue dans l'installateur du mod D20 Overhaul pour KotOR 2 !\n\n"
            "DESCRIPTION DU MOD :\n"
            "Ce mod transforme le système de combat et d'équipement de KotOR 2 pour rétablir "
            "une fidélité mathématique rigoureuse aux règles d20 Star Wars Roleplaying Game (WotC) :\n\n"
            "1. DONS & POUVOIRS :\n"
            "  - 78 nouveaux dons d20 (Familles d'armes Laser, Assaut, Lourdes, etc., Styles de combat,\n"
            "    Dons de Caractéristiques rééquilibrés) et les 6 pouvoirs de classe de prestige entièrement\n"
            "    refondus (avec 2 pouvoirs inédits).\n"
            "  - 33 dons redondants ou déséquilibrés masqués proprement.\n"
            "  - Progression des dons et pouvoirs réétalonnée (budgets 22/18/15 dons sur 30 niveaux).\n\n"
            "2. ARMES, ARMURES & BOUCLIERS :\n"
            "  - Refonte d20 des profils d'armes (dégâts, plages de coups critiques, maniement 1M/2M).\n"
            "  - Armures légères, moyennes et lourdes rééquilibrées avec bonus de DEX max et CA d20.\n"
            "  - Refonte des boucliers d'énergie et levée des restrictions de Force sous armure légère.\n\n"
            "3. FABRICATION & ÉQUIPEMENT :\n"
            "  - Établi d'artisanat (et lance-roquettes de Mira) enrichi avec armes de base, verrous de\n"
            "    niveau et 60 améliorations d'armures (30 sous-couches + 30 sur-couches exclusives Armure intermédiaire).\n"
            "  - Plafonds de stats lore pour tous les casques, gants, implants et ceintures.\n"
            "  - Cristal personnel de l'Exilé personnalisable auprès de Kreia (auto ou choix manuel).\n\n"
            "4. ÉQUILIBRAGE DU BESTIAIRE :\n"
            "  - 316 créatures et ennemis rééquilibrés + autobalance calibrée pour des combats tactiques.\n\n"
            "COMPATIBILITÉ :\n"
            "  - Compatible avec TSLRCM (The Sith Lords Restored Content Mod) 1.8.6 / 2022.\n"
            "  - Compatible avec K2CP (KotOR 2 Community Patch) v1.6.3 (installez K2CP avant ce mod).\n"
            "  - Le patcher effectue une fusion dynamique et crée une sauvegarde automatique dans 'backup/'.\n\n"
            "INSTRUCTIONS :\n"
            "Cliquez sur le bouton 'Install Mod' ci-dessous, puis sélectionnez le répertoire racine "
            "de votre jeu KotOR 2 (le dossier contenant swkotor2.exe, PAS le sous-dossier Override).\n"
        )
        deflang = "1036"

    return (
        f"{{\\rtf1\\ansi\\ansicpg1252\\deff0\\deflang{deflang}\n"
        "{\\fonttbl{\\f0\\fnil\\fcharset0 Segoe UI;}{\\f1\\fnil\\fcharset0 Calibri;}}\n"
        "{\\colortbl ;\\red0\\green51\\blue102;\\red180\\green0\\blue0;\\red60\\green60\\blue60;}\n"
        "\\viewkind4\\uc1\\pard\\cf1\\b\\f0\\fs28 " + rtf_escape(title) + "\\par\n"
        "\\fs22\\cf2 " + rtf_escape(subtitle) + "\\b0\\par\\par\n"
        "\\cf3\\f1\\fs20 " + rtf_escape(content) + "\n"
        "}"
    )


def _load_english_uti_descriptions() -> dict[str, str]:
    """Charge les descriptions anglaises des items/upgrades depuis english_csv/."""
    en_desc: dict[str, str] = {}
    csv_names = [
        "Kotor 2 - Rebalancing - Armbands.csv",
        "Kotor 2 - Rebalancing - Armor Items.csv",
        "Kotor 2 - Rebalancing - Belts.csv",
        "Kotor 2 - Rebalancing - Gloves.csv",
        "Kotor 2 - Rebalancing - Headgear.csv",
        "Kotor 2 - Rebalancing - Implants.csv",
        "Kotor 2 - Rebalancing - Upgrades.csv",
    ]
    for name in csv_names:
        p = EN_CSV_DIR / name
        if not p.exists():
            continue
        with open(p, encoding="utf-8-sig", newline="") as fh:
            rows = list(csv.reader(fh))
        if not rows or "Description (Mod)" not in rows[0]:
            continue
        d_idx = rows[0].index("Description (Mod)")
        for r in rows[1:]:
            if len(r) > d_idx and r[0].strip() and r[d_idx].strip():
                en_desc[r[0].strip().lower()] = r[d_idx].strip()
    return en_desc


def build_append_tlks_and_map() -> tuple[TLK, TLK, dict[int, str], int]:
    """Construit append_fr.tlk (FR) et append_en.tlk (EN) + la table StrRef."""
    base_tlk = read_tlk(BASE_TLK)
    mod_tlk = read_tlk(MOD_TLK)
    base_len = len(base_tlk)
    mod_len = len(mod_tlk)

    # Charger les correspondances EN depuis english_csv/
    en_feat_by_label: dict[str, tuple[str, str]] = {}
    en_feat_by_id: dict[int, tuple[str, str]] = {}
    en_feats_csv = EN_CSV_DIR / "Kotor 2 - Rebalancing - Feats.csv"
    if en_feats_csv.exists():
        with open(en_feats_csv, encoding="utf-8-sig", newline="") as fh:
            for r in list(csv.reader(fh))[1:]:
                if len(r) >= 9:
                    fid_s, lbl, name_en, desc_en = r[0].strip(), r[1].strip(), r[2].strip(), r[8].strip()
                    if lbl:
                        en_feat_by_label[lbl] = (name_en, desc_en)
                    if fid_s.isdigit():
                        en_feat_by_id[int(fid_s)] = (name_en, desc_en)

    fr_to_en_spell_desc: dict[str, str] = {}
    fr_pow_csv = CSV_POWERS
    en_pow_csv = EN_CSV_DIR / "Kotor 2 - Rebalancing - Force Powers.csv"
    if fr_pow_csv.exists() and en_pow_csv.exists():
        with open(fr_pow_csv, encoding="utf-8-sig", newline="") as f1, open(en_pow_csv, encoding="utf-8-sig", newline="") as f2:
            for fr_r, en_r in zip(list(csv.reader(f1))[1:], list(csv.reader(f2))[1:]):
                if len(fr_r) >= 8 and len(en_r) >= 8 and fr_r[7].strip() and en_r[7].strip():
                    fr_to_en_spell_desc[fr_r[7].strip()] = en_r[7].strip()

    feat_2da = read_2da(OVR_DIR / "feat.2da")
    feat_strref_to_en: dict[int, str] = {}
    for r_i in range(len(feat_2da)):
        row = feat_2da.get_row(r_i)
        lbl = row.get_string("label")
        pair = en_feat_by_label.get(lbl) or en_feat_by_id.get(r_i)
        if not pair:
            continue
        name_en, desc_en = pair
        nv = row.get_string("name")
        dv = row.get_string("description")
        if nv.isdigit() and int(nv) >= base_len and name_en:
            feat_strref_to_en[int(nv)] = name_en
        if dv.isdigit() and int(dv) >= base_len and desc_en:
            feat_strref_to_en[int(dv)] = desc_en

    append_fr = TLK(Language.FRENCH)
    append_en = TLK(Language.ENGLISH)
    strref_map: dict[int, str] = {}
    en_fallback_count = 0

    for i in range(base_len, mod_len):
        entry = mod_tlk.get(i)
        idx_append = len(append_fr)
        voice = str(entry.voiceover) if entry.voiceover else ""
        fr_text = entry.text
        append_fr.add(fr_text, voice)

        # Résolution du texte anglais correspondant
        en_text = (
            feat_strref_to_en.get(i)
            or fr_to_en_spell_desc.get(fr_text.strip())
            or EN_TLK_FALLBACK_MAP.get(fr_text.strip())
        )
        if not en_text:
            en_text = fr_text
            en_fallback_count += 1
        # TLK EN encode en Windows-1252 : un symbole hors CP1252 (≤, ≥, →…) y deviendrait un « ? » en jeu.
        append_en.add(sanitize_tlk(en_text), voice)
        strref_map[i] = f"StrRef{idx_append}"

    if en_fallback_count:
        print(f"[WARN] {en_fallback_count} chaîne(s) TLK sans traduction EN trouvée(s) (fallback FR)")
    return append_fr, append_en, strref_map, base_len


def _build_english_dlg(src_dlg: Path, dst_dlg: Path) -> int:
    """Crée une version anglaise d'un fichier .dlg en traduisant les nœuds custom (stringref == -1)."""
    dlg = read_dlg(src_dlg)
    translated = 0

    def _translate_ls(ls) -> None:
        nonlocal translated
        if ls.stringref != -1:
            return
        fr_txt = ls.get(Language.FRENCH, Gender.MALE) or ls.get(Language.ENGLISH, Gender.MALE)
        if fr_txt and fr_txt in EN_DLG_MAP:
            en_txt = EN_DLG_MAP[fr_txt]
            ls.set_data(Language.ENGLISH, Gender.MALE, en_txt)
            ls.set_data(Language.FRENCH, Gender.MALE, en_txt)
            translated += 1

    for e in dlg.all_entries():
        _translate_ls(e.text)
    for r in dlg.all_replies():
        _translate_ls(r.text)

    write_dlg(dlg, dst_dlg)
    return translated


def _generate_changes_ini(
    *,
    lang_code: str,
    window_caption: str,
    append_tlk_filename: str,
    tlk_count: int,
    loose_files: list[str],
    localized_dlgs: list[tuple[str, str]],  # [(src_name_in_tslpatchdata, save_as_name)]
    gff_baseitem_patches: list[tuple[str, list[tuple[str, str]]]],
    strref_map: dict[int, str],
    baseitem_row_to_mem: dict[int, int],
    feat_row_to_mem: dict[int, int],
    gam2_feat_idx: int | None,
) -> list[str]:
    """Construit les lignes d'un fichier changes_<lang>.ini complet pour TSLPatcher."""
    ini_lines: list[str] = [
        "; //////////////////////////////////////////////////////////////////////////////",
        f"; KOTOR 2: THE SITH LORDS - D20 OVERHAUL MOD ({lang_code.upper()})",
        "; TSLPatcher configuration file",
        "; //////////////////////////////////////////////////////////////////////////////",
        "",
        "[Settings]",
        "FileExists=1",
        "ConfirmMessage=N/A",
        "LogLevel=3",
        "InstallerMode=1",
        "BackupFiles=1",
        "PlaintextLog=1",
        "LookupGameFolder=0",
        "LookupGameNumber=2",
        "SaveProcessedScripts=0",
        f"WindowCaption={window_caption}",
        "",
        "[TLKList]",
        f"!SourceFile={append_tlk_filename}",
    ]

    for i in range(tlk_count):
        ini_lines.append(f"StrRef{i}={i}")

    ini_lines.extend([
        "",
        "[InstallList]",
        "install_folder0=Override",
        "",
        "[2DAList]",
    ])

    for idx, tname in enumerate(TABLE_NAMES):
        ini_lines.append(f"Table{idx}={tname}")

    ini_lines.extend(["", "[GFFList]"])
    for idx, (fname, _) in enumerate(gff_baseitem_patches):
        ini_lines.append(f"Replace{idx}={fname}")

    ini_lines.extend([
        "",
        "[CompileList]",
        "",
        "[SSFList]",
        "",
        "; ===================================================================",
        "[install_folder0]",
    ])

    rep_idx = 0
    for fname in loose_files:
        ini_lines.append(f"Replace{rep_idx}={fname}")
        rep_idx += 1
    for src_dlg_name, _ in localized_dlgs:
        ini_lines.append(f"Replace{rep_idx}={src_dlg_name}")
        rep_idx += 1

    # Redirection !SaveAs pour les dialogues localisés
    for src_dlg_name, save_as_name in localized_dlgs:
        ini_lines.extend([
            "",
            f"[{src_dlg_name}]",
            f"!SaveAs={save_as_name}",
        ])

    # Sections [2da] avec ChangeRow et AddRow
    for tname in TABLE_NAMES:
        ref_file = REF_2DA / tname.replace(".2da", "_tslrcm.2da")
        ovr_file = OVR_DIR / tname
        if not ref_file.exists() or not ovr_file.exists():
            continue

        ref_2da = read_2da(ref_file)
        ovr_2da = read_2da(ovr_file)
        headers = ovr_2da.get_headers()
        has_label = "label" in headers

        change_rows: list[tuple[int, str, dict[str, str]]] = []
        add_rows: list[tuple[int, str, dict[str, str], int | None]] = []

        common_len = min(len(ref_2da), len(ovr_2da))
        for r_idx in range(common_len):
            r_row = ref_2da.get_row(r_idx)
            o_row = ovr_2da.get_row(r_idx)
            diff_cols: dict[str, str] = {}
            for h in headers:
                rv = r_row.get_string(h)
                ov = o_row.get_string(h)
                if rv != ov:
                    if ov == "":
                        diff_cols[h] = "****"
                    elif ov.isdigit() and int(ov) in strref_map:
                        diff_cols[h] = strref_map[int(ov)]
                    else:
                        diff_cols[h] = ov
            if diff_cols:
                lbl = o_row.get_string("label") if has_label else str(r_idx)
                safe_lbl = "".join(c if c.isalnum() else "_" for c in lbl.lower()).strip("_")
                sec_name = f"{tname.replace('.2da', '')}_mod_{safe_lbl}_{r_idx}"
                change_rows.append((r_idx, sec_name, diff_cols))

        for r_idx in range(len(ref_2da), len(ovr_2da)):
            o_row = ovr_2da.get_row(r_idx)
            row_cols: dict[str, str] = {}
            for h in headers:
                ov = o_row.get_string(h)
                if ov.isdigit() and int(ov) in strref_map:
                    row_cols[h] = strref_map[int(ov)]
                elif (
                    tname == "baseitems.2da"
                    and h == "reqfeat0"
                    and gam2_feat_idx is not None
                    and ov == str(gam2_feat_idx)
                ):
                    row_cols[h] = f"2DAMEMORY{feat_row_to_mem[gam2_feat_idx]}"
                else:
                    row_cols[h] = ov
            lbl = o_row.get_string("label") if has_label else str(r_idx)
            safe_lbl = "".join(c if c.isalnum() else "_" for c in lbl.lower()).strip("_")
            sec_name = f"{tname.replace('.2da', '')}_row_{safe_lbl}_{r_idx}"

            mem_id: int | None = None
            if tname == "baseitems.2da" and r_idx in baseitem_row_to_mem:
                mem_id = baseitem_row_to_mem[r_idx]
            elif tname == "feat.2da" and r_idx in feat_row_to_mem:
                mem_id = feat_row_to_mem[r_idx]

            add_rows.append((r_idx, sec_name, row_cols, mem_id))

        ini_lines.extend(["", f"; {'=' * 67}", f"[{tname}]"])
        for c_i, (_, sec_name, _) in enumerate(change_rows):
            ini_lines.append(f"ChangeRow{c_i}={sec_name}")
        for a_i, (_, sec_name, _, _) in enumerate(add_rows):
            ini_lines.append(f"AddRow{a_i}={sec_name}")

        for r_idx, sec_name, cols in change_rows:
            ini_lines.extend(["", f"[{sec_name}]", f"RowIndex={r_idx}"])
            for ch, cv in cols.items():
                ini_lines.append(f"{ch}={cv}")

        for _, sec_name, cols, mem_id in add_rows:
            ini_lines.extend(["", f"[{sec_name}]"])
            if has_label and "label" in cols and cols["label"]:
                ini_lines.append("ExclusiveColumn=label")
            for ch, cv in cols.items():
                if cv != "":
                    ini_lines.append(f"{ch}={cv}")
            if mem_id is not None:
                ini_lines.append(f"2DAMEMORY{mem_id}=RowIndex")

    # Sections [GFFList] pour les .uti à BaseItem / Use_Limitation_Feat dynamiques
    if gff_baseitem_patches:
        ini_lines.extend(["", f"; {'=' * 67}", "; GFF Patches (BaseItem & Use_Limitation_Feat dynamiques via 2DAMEMORY)"])
        for fname, fields in gff_baseitem_patches:
            ini_lines.extend(["", f"[{fname}]"])
            for fk, fv in fields:
                ini_lines.append(f"{fk}={fv}")

    return ini_lines


def build_installer() -> None:
    print(f"=== Création de l'installateur TSLPatcher multilingue dans {INSTALLER_DIR} ===")
    INSTALLER_DIR.mkdir(parents=True, exist_ok=True)

    # 0. Nettoyer tslpatchdata/ pour éviter tout fichier fantôme d'un ancien build
    if TSL_DATA_DIR.exists():
        shutil.rmtree(TSL_DATA_DIR)
    TSL_DATA_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Copier l'exécutable INSTALL.exe & HOW_TO_TRANSLATE.md
    if SOURCE_INSTALL_EXE.exists():
        dst_exe = INSTALLER_DIR / "INSTALL.exe"
        shutil.copy2(SOURCE_INSTALL_EXE, dst_exe)
        print(f"[OK] INSTALL.exe copié depuis {SOURCE_INSTALL_EXE.name} ({dst_exe.stat().st_size} octets)")
    else:
        print(f"[WARN] INSTALL.exe non trouvé dans {SOURCE_INSTALL_EXE}")

    if HOW_TO_TRANSLATE_MD.exists():
        shutil.copy2(HOW_TO_TRANSLATE_MD, INSTALLER_DIR / "HOW_TO_TRANSLATE.md")

    # 2. Générer info_en.rtf, info_fr.rtf et Readme.rtf
    (TSL_DATA_DIR / "info_en.rtf").write_text(generate_info_rtf("en"), encoding="ascii")
    (TSL_DATA_DIR / "info_fr.rtf").write_text(generate_info_rtf("fr"), encoding="ascii")
    (INSTALLER_DIR / "Readme.rtf").write_text(generate_info_rtf("en"), encoding="ascii")
    print("[OK] info_en.rtf, info_fr.rtf & Readme.rtf générés")

    # 3. Générer namespaces.ini (English par défaut en Namespace1, Français en Namespace2)
    # Encodage ASCII pur pour compatibilité universelle TSLPatcher (CP1252) & HoloPatcher (UTF-8)
    namespaces_ini = (
        "; KotOR 2 D20 Overhaul - Language Selection\r\n"
        "; See HOW_TO_TRANSLATE.md to add a new language.\r\n"
        "\r\n"
        "[Namespaces]\r\n"
        "Namespace1=english\r\n"
        "Namespace2=francais\r\n"
        "\r\n"
        "; ===================================================================\r\n"
        "\r\n"
        "[english]\r\n"
        "IniName=changes_en.ini\r\n"
        "InfoName=info_en.rtf\r\n"
        "DataPath=\r\n"
        "Name=English (Default)\r\n"
        "Description=Install KotOR 2 D20 Overhaul in English (feats, powers, items, dialogues).\r\n"
        "\r\n"
        "[francais]\r\n"
        "IniName=changes_fr.ini\r\n"
        "InfoName=info_fr.rtf\r\n"
        "DataPath=\r\n"
        "Name=Francais\r\n"
        "Description=Installer KotOR 2 D20 Overhaul en francais (dons, pouvoirs, objets, dialogues).\r\n"
    )
    with open(TSL_DATA_DIR / "namespaces.ini", "w", encoding="ascii", newline="") as fh:
        fh.write(namespaces_ini)
    print("[OK] namespaces.ini généré (Défaut : English, Option 2 : Français)")

    # 4. Extraire append_fr.tlk & append_en.tlk
    append_fr, append_en, strref_map, _ = build_append_tlks_and_map()
    write_tlk(append_fr, TSL_DATA_DIR / "append_fr.tlk")
    write_tlk(append_en, TSL_DATA_DIR / "append_en.tlk")
    print(f"[OK] append_en.tlk & append_fr.tlk générés ({len(append_en)} chaînes chacun)")

    # 5. Copier les 10 tables .2da de référence (TSLRCM) dans tslpatchdata/
    copied_2das = 0
    for tname in TABLE_NAMES:
        ref_file = REF_2DA / tname.replace(".2da", "_tslrcm.2da")
        if not ref_file.exists():
            raise FileNotFoundError(f"Table de référence manquante : {ref_file}")
        shutil.copy2(ref_file, TSL_DATA_DIR / tname)
        copied_2das += 1
    print(f"[OK] {copied_2das} tables .2da de base (TSLRCM) copiées dans tslpatchdata/")

    # 6. Allouer les jetons 2DAMEMORY (baseitems >= 104 + MOD_GAMORREAN_2)
    ref_bi = read_2da(REF_2DA / "baseitems_tslrcm.2da")
    mod_bi = read_2da(OVR_DIR / "baseitems.2da")
    next_mem_id = 1
    baseitem_row_to_mem: dict[int, int] = {}
    for bi_idx in range(len(ref_bi), len(mod_bi)):
        baseitem_row_to_mem[bi_idx] = next_mem_id
        next_mem_id += 1

    ref_feat = read_2da(REF_2DA / "feat_tslrcm.2da")
    mod_feat = read_2da(OVR_DIR / "feat.2da")
    feat_row_to_mem: dict[int, int] = {}
    gam2_feat_idx: int | None = None
    for f_idx in range(len(ref_feat), len(mod_feat)):
        if mod_feat.get_row(f_idx).get_string("label") in ("MOD_GAMORREAN_2", "MOD_GAMORRAN_2"):
            gam2_feat_idx = f_idx
            feat_row_to_mem[f_idx] = next_mem_id
            next_mem_id += 1
            break

    # 7. Copier les fichiers Override dans tslpatchdata/
    #    - Les .dlg sont dupliqués en *_fr.dlg et *_en.dlg (traduits) avec !SaveAs
    #    - Les .uti reçoivent leur description EN dans Language.ENGLISH (tout en gardant FR dans Language.FRENCH)
    en_uti_descs = _load_english_uti_descriptions()
    bilingual_utis = 0
    loose_files: list[str] = []
    localized_dlgs_en: list[tuple[str, str]] = []
    localized_dlgs_fr: list[tuple[str, str]] = []
    gff_baseitem_patches: list[tuple[str, list[tuple[str, str]]]] = []

    for f in sorted(OVR_DIR.iterdir()):
        if not f.is_file() or f.suffix.lower() not in {".uti", ".utc", ".ncs", ".dlg", ".utp"}:
            continue
        ext = f.suffix.lower()
        if ext == ".dlg":
            fr_name = f"{f.stem}_fr.dlg"
            en_name = f"{f.stem}_en.dlg"
            shutil.copy2(f, TSL_DATA_DIR / fr_name)
            n_tr = _build_english_dlg(f, TSL_DATA_DIR / en_name)
            localized_dlgs_fr.append((fr_name, f.name))
            localized_dlgs_en.append((en_name, f.name))
            print(f"[OK] Dialogue localisé {f.name} -> {fr_name} / {en_name} ({n_tr} nœuds traduits EN)")
            continue

        dst_path = TSL_DATA_DIR / f.name
        if ext == ".uti":
            uti = read_uti(f)
            # Enrichir le slot Language.ENGLISH si une description EN existe dans english_csv/
            en_d = en_uti_descs.get(f.stem.lower())
            if en_d and uti.description.stringref == -1:
                uti.description.set_data(Language.ENGLISH, Gender.MALE, en_d)
                write_uti(uti, dst_path)
                bilingual_utis += 1
            else:
                shutil.copy2(f, dst_path)

            fields: list[tuple[str, str]] = []
            if uti.base_item in baseitem_row_to_mem:
                fields.append(("BaseItem", f"2DAMEMORY{baseitem_row_to_mem[uti.base_item]}"))
            if gam2_feat_idx is not None and gam2_feat_idx in feat_row_to_mem:
                gam2_mem = feat_row_to_mem[gam2_feat_idx]
                for p_idx, prop in enumerate(uti.properties):
                    if prop.property_name == 57 and prop.subtype == gam2_feat_idx:
                        fields.append((f"PropertiesList\\{p_idx}\\Subtype", f"2DAMEMORY{gam2_mem}"))
            if fields:
                gff_baseitem_patches.append((f.name, fields))
                continue
        else:
            shutil.copy2(f, dst_path)

        loose_files.append(f.name)

    print(
        f"[OK] {len(loose_files)} fichiers communs + {len(localized_dlgs_en)} dialogues localisés "
        f"+ {len(gff_baseitem_patches)} .uti [GFFList] copiés ({bilingual_utis} .uti bilingues EN+FR)"
    )

    # 8. Générer changes_en.ini et changes_fr.ini
    common_kwargs = dict(
        tlk_count=len(append_en),
        loose_files=loose_files,
        gff_baseitem_patches=gff_baseitem_patches,
        strref_map=strref_map,
        baseitem_row_to_mem=baseitem_row_to_mem,
        feat_row_to_mem=feat_row_to_mem,
        gam2_feat_idx=gam2_feat_idx,
    )

    ini_en = _generate_changes_ini(
        lang_code="en",
        window_caption="KotOR 2: The Sith Lords - D20 Overhaul Mod (English)",
        append_tlk_filename="append_en.tlk",
        localized_dlgs=localized_dlgs_en,
        **common_kwargs,
    )
    ini_fr = _generate_changes_ini(
        lang_code="fr",
        window_caption="KotOR 2: The Sith Lords - D20 Overhaul Mod (FR)",
        append_tlk_filename="append_fr.tlk",
        localized_dlgs=localized_dlgs_fr,
        **common_kwargs,
    )

    for fname, lines in [("changes_en.ini", ini_en), ("changes_fr.ini", ini_fr)]:
        out_p = TSL_DATA_DIR / fname
        with open(out_p, "w", encoding="windows-1252", errors="replace", newline="") as fh:
            fh.write("\r\n".join(lines) + "\r\n")
        print(f"[OK] {fname} généré ({out_p.stat().st_size} octets, {len(lines)} lignes)")

    # 9. Validation automatique des deux configurations
    _validate_installer("changes_en.ini", len(loose_files) + len(localized_dlgs_en), [f for f, _ in gff_baseitem_patches], len(append_en))
    _validate_installer("changes_fr.ini", len(loose_files) + len(localized_dlgs_fr), [f for f, _ in gff_baseitem_patches], len(append_fr))
    print(f"=== INSTALLATEUR MULTILINGUE PRÊT DANS {INSTALLER_DIR} ===")


def _validate_installer(
    ini_filename: str,
    expected_install_count: int,
    expected_gff_files: list[str],
    expected_tlk_count: int,
) -> None:
    """Valide l'intégrité structurelle d'un fichier changes_*.ini."""
    import configparser

    ini_path = TSL_DATA_DIR / ini_filename
    cfg = configparser.RawConfigParser(strict=False)
    cfg.read(ini_path, encoding="windows-1252")

    tlk_list = cfg["TLKList"]
    tlk_entries = {k: v for k, v in tlk_list.items() if not k.startswith("!")}
    assert len(tlk_entries) == expected_tlk_count, f"{ini_filename}: TLKList ({len(tlk_entries)}) != {expected_tlk_count}"
    src_tlk = tlk_list.get("!sourcefile", "append.tlk")
    assert (TSL_DATA_DIR / src_tlk).exists(), f"{ini_filename}: {src_tlk} manquant"

    inst_folder = cfg["install_folder0"]
    assert len(inst_folder) == expected_install_count, (
        f"{ini_filename}: install_folder0 ({len(inst_folder)}) != {expected_install_count}"
    )
    for _, fname in inst_folder.items():
        assert (TSL_DATA_DIR / fname).exists(), f"{ini_filename}: fichier manquant : {fname}"

    gff_list = cfg["GFFList"]
    assert len(gff_list) == len(expected_gff_files), (
        f"{ini_filename}: GFFList ({len(gff_list)}) != {len(expected_gff_files)}"
    )
    for _, fname in gff_list.items():
        assert (TSL_DATA_DIR / fname).exists(), f"{ini_filename}: fichier GFF manquant : {fname}"
        assert fname in cfg, f"{ini_filename}: section GFF [{fname}] manquante"

    tables = [v for _, v in cfg["2DAList"].items()]
    total_changes, total_adds = 0, 0
    for t in tables:
        assert (TSL_DATA_DIR / t).exists(), f"{ini_filename}: table de base {t} manquante"
        assert t in cfg, f"{ini_filename}: section [{t}] manquante"
        for k, target_sec in cfg[t].items():
            assert target_sec in cfg, f"{ini_filename}: sous-section [{target_sec}] manquante pour {t}"
            if k.startswith("changerow"):
                total_changes += 1
            elif k.startswith("addrow"):
                total_adds += 1

    print(
        f"[OK] Validation {ini_filename} : {len(tables)} tables "
        f"({total_changes} ChangeRows, {total_adds} AddRows), "
        f"{len(inst_folder)} fichiers Override + {len(gff_list)} patchs GFF, "
        f"{expected_tlk_count} chaînes TLK ({src_tlk})."
    )


def generate_usage_readme_txt() -> str:
    """Génère un README.txt d'usage clair (EN + FR) pour l'archive de distribution."""
    return (
        "================================================================================\r\n"
        "  STAR WARS: KNIGHTS OF THE OLD REPUBLIC II - THE SITH LORDS\r\n"
        "  D20 OVERHAUL MOD - Version 1.0 (English / Français)\r\n"
        "================================================================================\r\n"
        "\r\n"
        "[ENGLISH]\r\n"
        "---------\r\n"
        "\r\n"
        "ARCHIVE CONTENTS:\r\n"
        "  - INSTALL.exe                               : TSLPatcher installer (language selector)\r\n"
        "  - tslpatchdata/                             : Mod data folder (keep next to INSTALL.exe)\r\n"
        "  - KotOR2_D20_Overhaul_Player_Guide_EN.pdf   : Complete Player Guide (EN)\r\n"
        "  - KotOR2_D20_Overhaul_Guide_Joueur_FR.pdf   : Guide complet du joueur (FR)\r\n"
        "  - HOW_TO_TRANSLATE.md                       : Guide for modders to add a new language\r\n"
        "  - Readme.rtf                                : Mod overview\r\n"
        "\r\n"
        "REQUIREMENTS & RECOMMENDED INSTALL ORDER:\r\n"
        "  1. Star Wars: KotOR II (Steam, GOG, or Disc — standalone TSLRCM recommended\r\n"
        "     over Steam Workshop for TSLPatcher compatibility).\r\n"
        "  2. TSLRCM (The Sith Lords Restored Content Mod 1.8.6 / 2022) — strongly recommended.\r\n"
        "  3. K2CP (KotOR 2 Community Patch v1.6.3) — optional, install BEFORE this mod.\r\n"
        "  4. D20 Overhaul (this mod) — install AFTER TSLRCM and K2CP.\r\n"
        "\r\n"
        "INSTALLATION:\r\n"
        "  1. Extract the ENTIRE archive to a temporary folder (keep INSTALL.exe and\r\n"
        "     tslpatchdata/ together).\r\n"
        "  2. Run INSTALL.exe (as Administrator if the game is under Program Files).\r\n"
        "  3. Choose your language in the dropdown menu (English is selected by default;\r\n"
        "     Français is also available) and click 'Install Mod'.\r\n"
        "  4. Select your KotOR 2 ROOT directory (the folder containing swkotor2.exe,\r\n"
        "     NOT the Override subfolder).\r\n"
        "  5. Wait for completion. Starting a new game is strongly recommended.\r\n"
        "\r\n"
        "UPDATING:\r\n"
        "  Simply run the updated INSTALL.exe pointing to your KotOR 2 folder; existing\r\n"
        "  mod files are backed up and cleanly replaced.\r\n"
        "\r\n"
        "UNINSTALLATION:\r\n"
        "  TSLPatcher automatically creates a backup/ folder next to INSTALL.exe.\r\n"
        "  Restore dialog.tlk and Override files from backup/ to revert.\r\n"
        "\r\n"
        "WANT TO TRANSLATE THIS MOD INTO YOUR LANGUAGE?\r\n"
        "  See HOW_TO_TRANSLATE.md included in this archive!\r\n"
        "\r\n"
        "================================================================================\r\n"
        "\r\n"
        "[FRANÇAIS]\r\n"
        "----------\r\n"
        "\r\n"
        "CONTENU DE L'ARCHIVE :\r\n"
        "  - INSTALL.exe                               : Installateur TSLPatcher (choix de langue)\r\n"
        "  - tslpatchdata/                             : Données du mod (NE PAS déplacer)\r\n"
        "  - KotOR2_D20_Overhaul_Guide_Joueur_FR.pdf   : Guide complet du joueur (FR)\r\n"
        "  - KotOR2_D20_Overhaul_Player_Guide_EN.pdf   : Complete Player Guide (EN)\r\n"
        "  - HOW_TO_TRANSLATE.md                       : Tutoriel pour ajouter une nouvelle langue\r\n"
        "  - Readme.rtf                                : Résumé rapide du mod\r\n"
        "\r\n"
        "PRÉREQUIS & ORDRE D'INSTALLATION RECOMMANDÉ :\r\n"
        "  1. Star Wars: KotOR II (Steam, GOG ou CD) — version autonome recommandée\r\n"
        "     (évitez TSLRCM via le Steam Workshop pour les mods TSLPatcher).\r\n"
        "  2. TSLRCM (The Sith Lords Restored Content Mod 1.8.6 / 2022) — fortement recommandé.\r\n"
        "  3. K2CP (KotOR 2 Community Patch v1.6.3) — optionnel, à installer AVANT ce mod.\r\n"
        "  4. D20 Overhaul (ce mod) — à installer EN DERNIER parmi les mods de gameplay.\r\n"
        "\r\n"
        "INSTALLATION :\r\n"
        "  1. Extrayez TOUT le contenu de ce .zip dans un dossier temporaire\r\n"
        "     (gardez bien INSTALL.exe et le dossier tslpatchdata/ côte à côte).\r\n"
        "  2. Lancez INSTALL.exe (en administrateur si le jeu est dans Program Files).\r\n"
        "  3. Sélectionnez votre langue dans le menu déroulant (English par défaut,\r\n"
        "     ou Français) puis cliquez sur « Install Mod ».\r\n"
        "  4. Sélectionnez le dossier RACINE du jeu (celui qui contient swkotor2.exe,\r\n"
        "     ATTENTION : NE sélectionnez PAS le sous-dossier Override !).\r\n"
        "  5. Attendez le message de confirmation. Une nouvelle partie est fortement recommandée.\r\n"
        "\r\n"
        "MISE À JOUR :\r\n"
        "  Relancez simplement le nouvel INSTALL.exe sur votre dossier de jeu : les fichiers\r\n"
        "  du mod seront automatiquement sauvegardés puis remplacés par la nouvelle version.\r\n"
        "\r\n"
        "DÉSINSTALLATION :\r\n"
        "  TSLPatcher crée automatiquement un dossier backup/ à côté de INSTALL.exe avant\r\n"
        "  toute modification. Restaurez dialog.tlk et Override depuis backup/ pour revenir en arrière.\r\n"
        "================================================================================\r\n"
    )


def build_release_zip(zip_path: Path | None = None) -> Path:
    """Construit une archive .zip propre prête au partage (installateur multilingue + README + tuto + PDFs)."""
    import zipfile

    DIST_DIR.mkdir(parents=True, exist_ok=True)
    out_zip = zip_path or (DIST_DIR / RELEASE_ZIP_NAME)
    top_dir = "KotOR2_D20_Overhaul"

    assert (INSTALLER_DIR / "INSTALL.exe").exists(), "INSTALL.exe manquant dans installer/"
    assert (TSL_DATA_DIR / "namespaces.ini").exists(), "namespaces.ini manquant dans installer/tslpatchdata/"

    readme_txt = generate_usage_readme_txt()

    file_count = 0
    with zipfile.ZipFile(out_zip, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        zf.write(INSTALLER_DIR / "INSTALL.exe", f"{top_dir}/INSTALL.exe")
        file_count += 1
        if (INSTALLER_DIR / "Readme.rtf").exists():
            zf.write(INSTALLER_DIR / "Readme.rtf", f"{top_dir}/Readme.rtf")
            file_count += 1
        zf.writestr(f"{top_dir}/README.txt", readme_txt.encode("utf-8"))
        file_count += 1
        if HOW_TO_TRANSLATE_MD.exists():
            zf.write(HOW_TO_TRANSLATE_MD, f"{top_dir}/HOW_TO_TRANSLATE.md")
            file_count += 1

        for pdf in PDF_GUIDES:
            if pdf.exists():
                zf.write(pdf, f"{top_dir}/{pdf.name}")
                file_count += 1
            else:
                print(f"[WARN] PDF absent : {pdf}")

        for p in sorted(TSL_DATA_DIR.rglob("*")):
            if p.is_file():
                rel = p.relative_to(TSL_DATA_DIR).as_posix()
                zf.write(p, f"{top_dir}/tslpatchdata/{rel}")
                file_count += 1

    size_mb = out_zip.stat().st_size / (1024 * 1024)
    print(f"[OK] Archive de partage créée : {out_zip} ({size_mb:.2f} Mo, {file_count} fichiers)")
    return out_zip


if __name__ == "__main__":
    import argparse
    import subprocess
    import sys

    parser = argparse.ArgumentParser(description="Générateur de l'installateur TSLPatcher multilingue")
    parser.add_argument(
        "-f", "--full",
        action="store_true",
        help="Reconstruit d'abord tout le mod (build_overhaul, build_items, build_scripts, build_enemies) avant de packager l'installateur.",
    )
    parser.add_argument(
        "-z", "--zip",
        action="store_true",
        help="Crée aussi l'archive .zip prête au partage dans dist/ (installateur + README.txt + tuto traduction + guides PDF).",
    )
    args = parser.parse_args()

    if args.full:
        print("=== RECONSTRUCTION COMPLÈTE DU MOD (--full) ===")
        scripts = [
            ("Jalon 1 (2DA & TLK)", ROOT / "tools" / "build_overhaul.py"),
            ("Jalon 2 (Items UTI)", ROOT / "tools" / "build_items.py"),
            ("Jalon 3 (Scripts NCS)", ROOT / "tools" / "build_scripts.py"),
            ("Bestiaire (Créatures UTC)", ROOT / "tools" / "build_enemies.py"),
        ]
        for name, script_path in scripts:
            print(f"\n--- Exécution : {name} ---")
            res = subprocess.run([sys.executable, str(script_path)], check=False)
            if res.returncode != 0:
                print(f"[ERREUR] Échec de {script_path.name} (code {res.returncode})")
                sys.exit(res.returncode)
        print("\n=== RECONSTRUCTION DES FICHIERS SOURCE TERMINÉE ===\n")

    build_installer()
    if args.zip:
        build_release_zip()
