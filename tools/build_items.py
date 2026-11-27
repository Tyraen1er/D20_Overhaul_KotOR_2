#!/usr/bin/env python3
"""KotOR 2 Overhaul — Jalon 2 : Générateur des items .uti.

Lit directement nos CSV utilisateur + les ressources TSLRCM/vanilla du jeu et génère
dans `mods/overhaul/Override/*.uti` :
  1. Tous les équipements modifiés des 6 CSV (Casques, Implants, Gants, Ceintures,
     Brassards, Armures items) : plafonds stats primaires (+1/+2/+3), ajouts lore 6 stats,
     et plafonds secondaires (RD, Immunités %, Dégâts gants, Saves, CA, Atq).
  2. Verrouillage `upgrade_level` des armures intermédiaires (= 6) pour réserver
     les 24 upgrades combinées intermédiaires (`u_a_over_19..30`, `u_a_unde_19..30`).
  3. Génération des 24 `.uti` d'upgrades combinées intermédiaires (depuis `Améliorations.csv`).
  4. Génération des variantes `.uti` 1M Gamoréen II pour les armes 2M/Doubles de base
     (utilisant `mods/overhaul/baseitem_1m_map.json` issu du Jalon 1).
"""

from __future__ import annotations

import csv
import json
import re
import unicodedata
from pathlib import Path

from pykotor.common.language import Gender, Language, LocalizedString
from pykotor.common.misc import ResRef
from pykotor.extract.installation import Installation, SearchLocation
from pykotor.resource.formats.erf import read_erf
from pykotor.resource.formats.gff import GFFList, read_gff, write_gff
from pykotor.resource.formats.key import read_key
from pykotor.resource.formats.tlk import read_tlk
from pykotor.resource.formats.twoda import read_2da
from pykotor.resource.generics.uti import UTIProperty, read_uti, write_uti
from pykotor.resource.generics.utp import read_utp, write_utp
from pykotor.resource.type import ResourceType
import copy

ROOT = Path(__file__).resolve().parent.parent
GAME_PATH = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Knights of the Old Republic II")
OVR_DIR = ROOT / "mods" / "overhaul" / "Override"
OUT_DIR = ROOT / "mods" / "overhaul"
MIRROR_MAP_FILE = OUT_DIR / "baseitem_1m_map.json"
FEAT_IDS_FILE = OUT_DIR / "feat_ids.json"
SPELL_IDS_FILE = OUT_DIR / "spell_ids.json"
GAM_SWAP_MAP_FILE = OUT_DIR / "gamorrean_swap_map.json"

GEAR_CSVS = [
    "Kotor 2 - rééquilibrage - Casques.csv",
    "Kotor 2 - rééquilibrage - Implants.csv",
    "Kotor 2 - rééquilibrage - Gants.csv",
    "Kotor 2 - rééquilibrage - Ceintures.csv",
    "Kotor 2 - rééquilibrage - Brassards.csv",
    "Kotor 2 - rééquilibrage - Armures items.csv",
]
CSV_UPGRADES = ROOT / "Kotor 2 - rééquilibrage - Améliorations.csv"

STAT_TO_SUB = {"FOR": 0, "DEX": 1, "CON": 2, "INT": 3, "SAG": 4, "CHA": 5}
DMG_COST_MAP = {
    "1": 1, "2": 2, "3": 3, "4": 4, "5": 5,
    "1d2": 14, "1d3": 14, "1d4": 6, "1d6": 7, "1d8": 8, "1d10": 9,
    "2d6": 10, "1d12": 11, "2d8": 12, "2d10": 13,
}
DMG_TYPE_SUB = {
    "slashing": 2, "cold": 5, "electrical": 7, "fire": 8,
    "sonic": 10, "ion": 11, "energy": 12,
}
ABILITY_EN_SUB = {
    "strength": 0, "dexterity": 1, "constitution": 2,
    "intelligence": 3, "wisdom": 4, "charisma": 5,
}
ONHIT_FR_SUB = {
    "etourdissement": 1, "paralysie": 2, "horreur": 4, "lenteur": 5,
}
IMM_COST_MAP = {5: 1, 10: 2, 15: 8, 20: 9, 25: 3, 30: 10}
# iprp_resistcost.2da (étendu par build_overhaul.py : 1=5/-, 2=10/-, 3=15/-, 7=2/-, 8=3/-, 9=4/-, 10=6/-, 11=12/-)
RD_TO_COST = {2: 7, 3: 8, 4: 9, 5: 1, 6: 10, 10: 2, 12: 11, 15: 3}
COST_TO_RD = {1: 5, 2: 10, 3: 15, 4: 20, 5: 25, 6: 30, 7: 2, 8: 3, 9: 4, 10: 6, 11: 12}

# Variantes 1M Gamoréen II : resref vanilla (du bon type d'arme !) -> (baseitem_label_2m, resref_1m)
GAMORREAN_WEAPONS = [
    ("w_melee_04",    "Quarter_Staff",            "m_w_qtrstf_1m"),
    ("w_melee_07",    "Double_Bladed_Sword",      "m_w_dblswd_1m"),
    ("w_melee_12",    "Vibro_Double_Blade",       "m_w_vbrdbl_1m"),
    ("g_w_dblsbr001", "Double_Bladed_Lightsaber", "m_w_dblsbr_1m"),
    ("w_melee_06",    "Vibro_Sword",              "m_w_vbrswd_1m"),
    ("w_melee_09",    "Gammorean_Battleaxe",      "m_w_gamaxe_1m"),
    ("w_melee_14",    "Force_Pike",               "m_w_frcpik_1m"),
    ("w_melee_30",    "Wookie_Warblade",          "m_w_wookwb_1m"),
    ("w_brifle_04",   "Blaster_Rifle",            "m_w_blsrfl_1m"),
    ("w_brifle_01",   "Blaster_Carbine",          "m_w_blscrb_1m"),
    ("w_brifle_06",   "Repeating_Blaster",        "m_w_rptbls_1m"),
    ("w_brifle_17",   "Heavy_Repeating_Blaster",  "m_w_hvyrpt_1m"),
    ("w_brifle_08",   "Disrupter_Rifle",          "m_w_dsrrfl_1m"),
    ("w_brifle_03",   "Sonic_Rifle",              "m_w_sncrfl_1m"),
    ("w_brifle_02",   "Ion_Rifle",                "m_w_ionrfl_1m"),
    ("w_brifle_05",   "Bowcaster",                "m_w_bowcst_1m"),
]

# Cloisonnement strict des emplacements d'améliorations d'armes (decisions_finales.md §3.A) :
#   Mêlée    : Poignée (1) < Lame (2) < Cellule (3)
#   Distance : Lunette (1) < Pack d'énergie (2) < Chambrage (3)
WEAPON_UPGRADE_LEVEL_BY_PREFIX: dict[str, int] = {
    "u_m_grip_": 1,  # Poignée (mêlée)
    "u_m_edge_": 2,  # Lame (mêlée)
    "u_m_cell_": 3,  # Cellule d'énergie (mêlée)
    "u_r_targ_": 1,  # Lunette (distance)
    "u_r_powe_": 2,  # Pack d'énergie (distance)
    "u_r_firi_": 3,  # Chambrage (distance)
}

# Anciens templates KotOR 1 encore référencés dans upgrade.2da (sécurité anti-contournement)
LEGACY_WEAPON_UPGRADE_ULVL: dict[str, int] = {
    "g_i_upgrade007": 1,  # Poignée (upgradetype 7)
    "g_i_upgrade008": 2,  # Lame (upgradetype 8)
    "g_i_upgrade009": 3,  # Cellule (upgradetype 9)
    "g_i_upgrade001": 1,  # Lunette (upgradetype 4)
    "g_i_upgrade002": 2,  # Pack d'énergie (upgradetype 5)
    "g_i_upgrade003": 3,  # Chambrage (upgradetype 6)
    "g_i_upgrade004": 3,  # Chambrage (upgradetype 6)
}

# Plafond UpgradeLevel par baseitem d'arme (Armes.csv / decisions_finales.md §3.A)
WEAPON_BASEITEM_ULVL: dict[int, int] = {
    # Mêlée — Impact (1 : Poignée)
    0:  1,  # Quarter_Staff
    1:  1,  # Stun_Baton
    93: 1,  # Force_Pike
    # Mêlée — Traditionnelle (2 : Poignée + Lame)
    2:  2,  # Long_Sword
    4:  2,  # Short_Sword
    6:  2,  # Double_Bladed_Sword
    79: 2,  # Wookie_Warblade
    80: 2,  # Gammorean_Battleaxe
    # Mêlée — Résonance (3 : Poignée + Lame + Cellule)
    3:  3,  # Vibro_Sword
    5:  3,  # Vibro_Blade
    7:  3,  # Vibro_Double_Blade
    # Distance — Tir Tactique (1 : Lunette)
    15: 1,  # Ion_Blaster
    17: 1,  # Sonic_Pistol
    18: 1,  # Ion_Rifle
    22: 1,  # Sonic_Rifle
    # Distance — Tir d'Assaut (2 : Lunette + Pack)
    12: 2,  # Blaster_Pistol
    20: 2,  # Blaster_Carbine
    23: 2,  # Repeating_Blaster
    # Distance — Tir Assassin (2 : Lunette + Pack)
    14: 2,  # Hold_Out_Blaster
    16: 2,  # Disrupter_Pistol
    21: 2,  # Disrupter_Rifle
    # Distance — Tir Pénétrant (3 : Lunette + Pack + Chambrage)
    13: 3,  # Heavy_Blaster
    19: 3,  # Bowcaster
    24: 3,  # Heavy_Repeating_Blaster
    77: 3,  # Blaster_Rifle
}

WEAPON_LABEL_ULVL: dict[str, int] = {
    "Quarter_Staff":            1,
    "Stun_Baton":               1,
    "Force_Pike":               1,
    "Long_Sword":               2,
    "Short_Sword":              2,
    "Double_Bladed_Sword":      2,
    "Wookie_Warblade":          2,
    "Gammorean_Battleaxe":      2,
    "Vibro_Sword":              3,
    "Vibro_Blade":              3,
    "Vibro_Double_Blade":       3,
    "Double_Bladed_Lightsaber": 3,
    "Ion_Blaster":              1,
    "Sonic_Pistol":             1,
    "Ion_Rifle":                1,
    "Sonic_Rifle":              1,
    "Blaster_Pistol":           2,
    "Blaster_Carbine":          2,
    "Repeating_Blaster":        2,
    "Hold_Out_Blaster":         2,
    "Disrupter_Pistol":         2,
    "Disrupter_Rifle":          2,
    "Heavy_Blaster":            3,
    "Bowcaster":                3,
    "Heavy_Repeating_Blaster":  3,
    "Blaster_Rifle":            3,
}

WEAPON_ULVL_EXCLUDED_PREFIXES = (
    "prop",
    "g_w_null",
    "g_i_bithitem",
    "w_drink_",
    "w_emptyhnd_",
    "w_pazaak_",
)

WEAPON_ULVL_EXCLUDED_RESREFS = {
    "killblaster",       # objet debug développeur
    "killstick",         # objet debug développeur
    "plasmatorch",       # outil utilitaire Péragus (baseitem dédié Plasma_Torch)
    "mininglaser",       # outil de forage Péragus (baseitem dédié Mining_Laser)
    "advancedminingla",  # outil de forage Péragus (baseitem dédié Adv_Mining_Laser)
    "heavymininglaser",  # outil de forage droïde Péragus
    "vibrocutter",       # outil de découpe Péragus
    "guidonbeacon",      # balise de quête Péragus
    "w_blaste_x20",      # arme interne du droïde téléguidé (Remote)
    "w_brifle_25",       # Fusil d'esclavagiste (No_Damage, utilitaire pur contrôle)
}

# Armes jouables présentes uniquement dans les .mod (absentes de chitin.key)
MODULE_PLAYABLE_WEAPONS = [
    ("208tel.mod", "benoksblaster"),
    ("411dxn.mod", "g_w_fnaddblade"),
    ("201tel.mod", "g_w_hldoblstr002"),
    ("101per.mod", "g_w_qtrstaff002"),
    ("403dxn.mod", "g_w_vbroswrd002"),
]

# B2-1a — Calibrage des armes de série/nommées & 6 reliques légendaires endgame :
#   1. Armes craftables Niv. 1 (w_melee_03, w_melee_09) : retrait des bonus de dégâts gratuits.
#   2. 6 reliques légendaires endgame : ulvl=0 (non modifiables à l'établi) + bonus dégâts unique plafonné à 1d8/1d10.
#   3. Autres armes de série/loot : bonus dégâts .uti (prop 11) dédoublonné et plafonné par palier
#      (T1-14: +2 max ; T15-22: +1d4 / +3 max ; T23-30: +1d6 / +4 max), identité conservée intacte.
WEAPON_STRIP_DMG_RESREFS = {
    "w_melee_03",  # Matraque à énergie (craftable Niv. 1) : retire +1d3 gratuit
    "w_melee_09",  # Hache de guerre gamorréenne (craftable Niv. 1) : retire +1d8 gratuit
}

WEAPON_RELIC_OVERRIDES: dict[str, tuple[int, int]] = {
    # resref -> (upgrade_level=0, capped iprp_damagecost: 8=1d8, 9=1d10)
    "w_melee_25":  (0, 9),  # Arg'garok (2x 1d12 -> 1d10 Tranchant, ulvl 0)
    "w_melee_30":  (0, 9),  # Épée de guerre de Freyyr (2 + 2d10 -> 1d10 Tranchant, ulvl 0)
    "w_melee_26":  (0, 8),  # Bâton électrique géonosien (1d6 + 2d6 -> 1d8 Électrique, ulvl 0)
    "w_blaste_30": (0, 9),  # Blaster de Freedon Nadd (2d10 -> 1d10 Côté Obscur, ulvl 0)
    "w_brifle_24": (0, 9),  # Fusil blaster automatique zabrak (1d12 + 3 -> 1d10 Énergie, ulvl 0)
    "w_brifle_26": (0, 8),  # Fusil à répétition d'Ondéron (2d6 -> 1d8 Énergie, ulvl 0)
}

WEAPON_NAMED_TIERS: dict[str, int] = {
    "benoksblaster": 10,   # Télos (T1-14)
    "w_melee_x01":   16,   # Bâton de la Servante (T15-22)
    "w_melee_x03":   16,   # Lame Twi'lek (T15-22)
    "w_melee_x12":   20,   # Épée de guerre de Ludo Kressh (T15-22)
    "g_w_fnaddblade": 25,  # Épée de Freedon Nadd (T23-30)
}

# Moyenne des dégâts par cost_value dans iprp_damagecost.2da
DMG_CV_AVG: dict[int, float] = {
    1: 1.0, 2: 2.0, 3: 3.0, 4: 4.0, 5: 5.0,
    14: 2.0, 6: 2.5, 7: 3.5, 8: 4.5, 9: 5.5, 10: 7.0, 11: 6.5, 12: 9.0, 13: 11.0,
}
DMG_FLAT_CVS = {1, 2, 3, 4, 5}


def _weapon_tier_from_resref(rr: str) -> int:
    if rr in WEAPON_NAMED_TIERS:
        return WEAPON_NAMED_TIERS[rr]
    m = re.search(r"_(\d{2})$", rr)
    return int(m.group(1)) if m else 15


def _apply_weapon_b2_balance(rr: str, uti, default_ulvl: int) -> tuple[int, bool]:
    """Applique B2-1a sur une arme jouable (upgrade_level + plafonnement prop 11 Damage Bonus).
    Retourne `(final_ulvl, dmg_modified)`."""
    if rr in WEAPON_STRIP_DMG_RESREFS:
        before = len(uti.properties)
        uti.properties = [p for p in uti.properties if p.property_name != 11]
        uti.upgrade_level = default_ulvl
        return default_ulvl, len(uti.properties) != before

    if rr in WEAPON_RELIC_OVERRIDES:
        relic_ulvl, cap_cv = WEAPON_RELIC_OVERRIDES[rr]
        uti.upgrade_level = relic_ulvl
        dmg_props = [p for p in uti.properties if p.property_name == 11]
        if dmg_props:
            best = max(dmg_props, key=lambda p: DMG_CV_AVG.get(p.cost_value, 0.0))
            best.cost_value = cap_cv
            kept = False
            new_props: list[UTIProperty] = []
            for p in uti.properties:
                if p.property_name == 11:
                    if not kept:
                        new_props.append(best)
                        kept = True
                else:
                    new_props.append(p)
            uti.properties = new_props
        return relic_ulvl, True

    uti.upgrade_level = default_ulvl
    modified = False

    # Uniformisation Hold_Out_Blaster (baseitem 14) : Massive Criticals >= +1d8 (cost_value 8 ; préserve 2d6=10 sur w_blaste_27)
    if uti.base_item == 14:
        mc_props = [p for p in uti.properties if p.property_name == 49]
        if not mc_props:
            uti.properties.append(make_prop(49, 0, 4, 8))
            modified = True
        else:
            for p in mc_props:
                if DMG_CV_AVG.get(p.cost_value, 0.0) < DMG_CV_AVG[8]:
                    p.cost_value = 8
                    modified = True

    dmg_props = [p for p in uti.properties if p.property_name == 11]
    if not dmg_props:
        return default_ulvl, modified

    tier = _weapon_tier_from_resref(rr)
    best = max(dmg_props, key=lambda p: DMG_CV_AVG.get(p.cost_value, 0.0))
    orig_cv = best.cost_value
    orig_avg = DMG_CV_AVG.get(orig_cv, 0.0)
    is_flat = orig_cv in DMG_FLAT_CVS

    if tier <= 14:
        new_cv = 2 if orig_avg > 2.0 else orig_cv
    elif tier <= 22:
        if orig_avg > 3.0:
            new_cv = 3 if is_flat else 6  # +3 fixe ou +1d4 dé
        else:
            new_cv = orig_cv
    else:
        if orig_avg > 4.0:
            new_cv = 4 if is_flat else 7  # +4 fixe ou +1d6 dé
        else:
            new_cv = orig_cv

    dmg_changed = (len(dmg_props) > 1) or (new_cv != orig_cv)
    if dmg_changed:
        best.cost_value = new_cv
        kept = False
        new_props = []
        for p in uti.properties:
            if p.property_name == 11:
                if not kept:
                    new_props.append(best)
                    kept = True
            else:
                new_props.append(p)
        uti.properties = new_props
    return default_ulvl, (modified or dmg_changed)


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.replace("'", " ").replace("\u2019", " ")
    return re.sub(r"\s+", " ", s.lower()).strip()


def set_uti_desc(uti, desc_txt: str, desc_en: str | None = None) -> None:
    """Injecte une description VF (et EN si fournie) dans un UTI."""
    if not desc_txt:
        return
    ls = LocalizedString.from_invalid()
    ls.set_data(Language.FRENCH, Gender.MALE, desc_txt)
    ls.set_data(Language.ENGLISH, Gender.MALE, desc_en if desc_en is not None else desc_txt)
    uti.description = ls


def make_prop(prop_id: int, subtype: int, cost_table: int, cost_value: int) -> UTIProperty:
    p = UTIProperty()
    p.property_name = prop_id
    p.subtype = subtype
    p.cost_table = cost_table
    p.cost_value = cost_value
    p.param1 = 255
    p.param1_value = 0
    p.chance_appear = 100
    return p


def _parse_stat_pairs(txt: str) -> dict[str, int]:
    out: dict[str, int] = {}
    for k, v in re.findall(r"\b(FOR|DEX|CON|INT|SAG|CHA)\s*([+-]\d+)", txt):
        out[k] = int(v)
    return out


def apply_mod_to_uti(uti, mod_txt: str) -> bool:
    """Applique les directives de `Changement (mod)` sur un objet UTI. Retourne True si modifié."""
    changed = False
    if not mod_txt:
        return False

    # Découper les directives multiples séparées par ';'
    segments = [seg.strip() for seg in mod_txt.split(";") if seg.strip()]
    for seg in segments:
        seg_n = norm(seg)

        # 1. Stats primaires : remplacement "→ ..." ou "Ajout : ..."
        if "→" in seg and (any(k in seg for k in STAT_TO_SUB) or "+1 aux 6 caracs" in seg_n):
            rhs = seg.split("→", 1)[1]
            if "+1 aux 6 caracs" in norm(rhs):
                new_stats = {k: 1 for k in STAT_TO_SUB}
            else:
                new_stats = _parse_stat_pairs(rhs)
            if new_stats:
                uti.properties = [p for p in uti.properties if p.property_name != 0]
                for k, v in new_stats.items():
                    uti.properties.append(make_prop(0, STAT_TO_SUB[k], 1, v))
                changed = True
                continue
        elif seg_n.startswith("ajout") and any(k in seg for k in STAT_TO_SUB):
            add_stats = _parse_stat_pairs(seg)
            for k, v in add_stats.items():
                sub = STAT_TO_SUB[k]
                uti.properties = [p for p in uti.properties if not (p.property_name == 0 and p.subtype == sub)]
                uti.properties.append(make_prop(0, sub, 1, v))
                changed = True
            continue

        # 2. CA : "CA +X → CA +Y"
        m_ac = re.search(r"ca \+\d+ → ca \+(\d+)", seg_n)
        if m_ac:
            new_ac = int(m_ac.group(1))
            for p in uti.properties:
                if p.property_name == 1:
                    p.cost_value = new_ac
                    changed = True

        # 3. Attaque : "Atq +X → Atq +Y"
        m_atk = re.search(r"atq \+\d+ → atq \+(\d+)", seg_n)
        if m_atk:
            new_atk = int(m_atk.group(1))
            for p in uti.properties:
                if p.property_name == 38:
                    p.cost_value = new_atk
                    changed = True

        # 4. Saves : "Saves +X → Saves +Y"
        m_sv = re.search(r"saves \+\d+ → saves \+(\d+)", seg_n)
        if m_sv:
            new_sv = int(m_sv.group(1))
            for p in uti.properties:
                if p.property_name in (26, 27):
                    p.cost_value = new_sv
                    changed = True

        # 5. Dégâts sur Gants : "Dégâts +X → +Y"
        m_dmg = re.search(r"degats \+(?:\d+d\d+|\d+) → \+(\d+d\d+|\d+)", seg_n)
        if m_dmg:
            new_cv = DMG_COST_MAP.get(m_dmg.group(1))
            if new_cv is not None:
                for p in uti.properties:
                    if p.property_name == 11:
                        p.cost_value = new_cv
                        changed = True

        # 6. Immunités % : "Immunité +75% → +30%" ou "+50%/+50% → +25%/+25%"
        m_imm = re.search(r"immunite .*?→ \+(\d+)%", seg_n)
        if m_imm:
            cap_pct = int(m_imm.group(1))
            cap_cv = IMM_COST_MAP.get(cap_pct, 10)
            for p in uti.properties:
                if p.property_name == 14 and p.cost_value in (4, 5, 6, 7):  # >= 50%
                    p.cost_value = cap_cv
                    changed = True

        # 7. RD : "RD ... → RD +Y/-" ou "→ +Y/-" (comparaison par valeur réelle amount, pas par index!)
        m_rd = re.search(r"rd .*?→ (?:rd )?\+(\d+)/-", seg_n)
        if m_rd:
            target_rd = int(m_rd.group(1))
            target_cv = RD_TO_COST.get(target_rd, 1)
            for p in uti.properties:
                if p.property_name == 17 and COST_TO_RD.get(p.cost_value, 999) > target_rd:
                    p.cost_value = target_cv
                    changed = True

    return changed


def build_gear_utis(inst: Installation) -> tuple[int, int]:
    modified_items = 0
    tiered_armors = 0
    for fname in GEAR_CSVS:
        path = ROOT / fname
        with open(path, encoding="utf-8-sig", newline="") as fh:
            rows = list(csv.reader(fh))
        h = {c.strip(): i for i, c in enumerate(rows[0])}
        is_armor_csv = "Armures items" in fname

        for r in rows[1:]:
            if not r or not r[0].strip():
                continue
            resref = r[h["ResRef"]].strip().lower()
            mod_txt = r[h["Changement (mod)"]].strip() if "Changement (mod)" in h and len(r) > h["Changement (mod)"] else ""
            desc_txt = r[h["Description (mod)"]].strip() if "Description (mod)" in h and len(r) > h["Description (mod)"] else ""
            target_ulvl: int | None = None
            if is_armor_csv:
                tcol = r[h["Type (2DA)"]].strip()
                if tcol in ("Armor Class 4", "Armor Class 5", "Armor Armd Flight Suit", "Armor Zeison Sha"):
                    target_ulvl = 1  # Légère : 1 slot (sous-couches Légère level=1 uniquement)
                elif tcol in ("Armor Class 8", "Armor Class 9"):
                    target_ulvl = 2  # Lourde : 1 slot (sous-couches Lourde level=2 + Légère level=1)
                elif tcol in ("Armor Class 6", "Armor Class 7"):
                    target_ulvl = 6  # Intermédiaire : 2 slots + 24 combinées (level=6)
                elif any(k in tcol for k in ("Robe", "Clothing", "Revan")):
                    target_ulvl = 0  # Robes : 0 slot

            if not mod_txt and not desc_txt and target_ulvl is None:
                continue

            res = inst.resource(resref, ResourceType.UTI, order=[SearchLocation.CHITIN]) or inst.resource(resref, ResourceType.UTI)
            if not res:
                continue
            uti = read_uti(res.data)
            dirty = apply_mod_to_uti(uti, mod_txt)
            if desc_txt:
                set_uti_desc(uti, desc_txt)
                dirty = True
            if target_ulvl is not None:
                uti.upgrade_level = target_ulvl
                dirty = True
                tiered_armors += 1
            if dirty:
                write_uti(uti, OVR_DIR / f"{resref}.uti")
                modified_items += 1
    return modified_items, tiered_armors


# Sous-couches réservées aux Armures Lourdes & Intermédiaires (ulvl=2 ; bloquées sur Légère ulvl=1) :
#   Renforçante (04/10/16/22/28), Flexible (05/11/17/23/29), Duracier (06/12/18/24/30)
HEAVY_ONLY_UNDERLAYS = {4, 5, 6, 10, 11, 12, 16, 17, 18, 22, 23, 24, 28, 29, 30}

ARMOR_IMM_MISC_SUB = {
    "drain": 1,
    "effets mentaux": 2,
    "poison": 3,
    "peur": 5,
    "paralysie": 7,
    "critiques": 8,
}

ARMOR_DMG_GROUP_SUBS: dict[str, list[int]] = {
    "bludgeoning": [0],
    "piercing": [1],
    "slashing": [2],
    "physique": [0, 1, 2],
    "cold": [5],
    "froid": [5],
    "electrical": [7],
    "electrique": [7],
    "fire": [8],
    "feu": [8],
    "sonic": [10],
    "sonique": [10],
    "ion": [11],
    "energy": [12],
    "energie": [12],
}

ARMOR_SKILL_SUB = {
    "discretion": 2,
}


def _expand_armor_dmg_types(group_str: str) -> list[int]:
    subs: list[int] = []
    for tok in re.split(r"[/,]", group_str):
        k = norm(tok)
        if k in ARMOR_DMG_GROUP_SUBS:
            for s in ARMOR_DMG_GROUP_SUBS[k]:
                if s not in subs:
                    subs.append(s)
    return subs


def _parse_armor_upgrade_props(rr: str, mod_txt: str) -> list[UTIProperty]:
    """Convertit la colonne `Changement (mod)` d'une upgrade d'armure (`Améliorations.csv`)
    en liste exhaustive de `UTIProperty` natifs KotOR 2 (erreur explicite si un token n'est pas reconnu)."""
    out: list[UTIProperty] = []
    for raw in [s.strip() for s in mod_txt.split(",") if s.strip()]:
        s = norm(raw)
        m = re.match(r"bonus defense \+(\d+)$", s)
        if m:
            out.append(make_prop(1, 0, 2, int(m.group(1))))
            continue
        m = re.match(r"defense vs physique \+(\d+)$", s)
        if m:
            val = int(m.group(1))
            for sub in (0, 1, 2):  # Bludgeoning, Piercing, Slashing
                out.append(make_prop(3, sub, 2, val))
            continue
        m = re.match(r"bonus dex max \+(\d+)$", s)
        if m:
            out.append(make_prop(68, 0, 2, int(m.group(1))))
            continue
        m = re.match(r"bonus de caracteristique \((\w+)\) \+(\d+)$", s)
        if m:
            out.append(make_prop(0, ABILITY_EN_SUB[m.group(1)], 1, int(m.group(2))))
            continue
        m = re.match(r"regeneration \+(\d+)$", s)
        if m:
            out.append(make_prop(35, 0, 2, int(m.group(1))))
            continue
        m = re.match(r"jets de sauvegarde ameliores \+(\d+)$", s)
        if m:
            out.append(make_prop(27, 0, 2, int(m.group(1))))  # subtype 0 = All saves
            continue
        m = re.match(r"bonus de competence \((\w+)\) \+(\d+)$", s)
        if m:
            out.append(make_prop(36, ARMOR_SKILL_SUB[m.group(1)], 1, int(m.group(2))))
            continue
        m = re.match(r"immunite contre degats \(([^)]+)\) \+(\d+)%$", s)
        if m:
            subs = _expand_armor_dmg_types(m.group(1))
            cv = IMM_COST_MAP[int(m.group(2))]
            if not subs:
                raise ValueError(f"Type de dégâts inconnu dans {rr}: {raw!r}")
            for sub in subs:
                out.append(make_prop(14, sub, 5, cv))
            continue
        m = re.match(r"resistance aux degats \(([^)]+)\) \+(\d+)/-$", s)
        if m:
            subs = _expand_armor_dmg_types(m.group(1))
            cv = RD_TO_COST[int(m.group(2))]
            if not subs:
                raise ValueError(f"Type de dégâts inconnu dans {rr}: {raw!r}")
            for sub in subs:
                out.append(make_prop(17, sub, 7, cv))
            continue
        m = re.match(r"immunite \(([^)]+)\)$", s)
        if m:
            key = m.group(1).strip()
            if key not in ARMOR_IMM_MISC_SUB:
                raise ValueError(f"Immunité inconnue dans {rr}: {raw!r}")
            out.append(make_prop(24, ARMOR_IMM_MISC_SUB[key], 0, 0))
            continue
        raise ValueError(f"Propriété d'amélioration d'armure non reconnue dans {rr}: {raw!r}")
    return out


def build_armor_upgrades(inst: Installation) -> tuple[int, int]:
    """Compile les 60 améliorations d'armure (`u_a_unde_01..30`, `u_a_over_01..30`) directement
    depuis `Améliorations.csv` (effets réels, descriptions VF et cloisonnement `upgrade_level`) :
      - `u_a_unde_01..30` : 15 communes (`ulvl = 1`, Légère/Lourde/Interm.) + 15 blindées (`ulvl = 2`, Lourde/Interm.)
      - `u_a_over_01..30` : 30 sur-couches renforcées (`ulvl = 6`, 100 % exclusives Armure Intermédiaire)
      - Legacy `g_i_upgrade005` (over=6) & `g_i_upgrade006` (unde=1)."""
    if not CSV_UPGRADES.exists():
        return 0, 0
    with open(CSV_UPGRADES, encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.reader(fh))
    d_idx = rows[0].index("Description (mod)") if rows and "Description (mod)" in rows[0] else -1

    n_over = 0
    n_unde = 0
    for r in rows[1:]:
        if len(r) < 7:
            continue
        rr = r[0].strip().lower()
        if not (rr.startswith("u_a_over_") or rr.startswith("u_a_unde_")):
            continue
        if "_c" in rr:
            continue
        mod_txt = r[6].strip()
        if not mod_txt:
            continue
        # Charger depuis CHITIN pour préserver le nom StrRef et l'icône vanilla d'origine
        res = inst.resource(rr, ResourceType.UTI, order=[SearchLocation.CHITIN])
        if not res:
            res = inst.resource(rr, ResourceType.UTI, order=[SearchLocation.CHITIN]) or inst.resource(rr, ResourceType.UTI)
        if not res:
            continue
        uti = read_uti(res.data)
        uti.properties = _parse_armor_upgrade_props(rr, mod_txt)
        num = int(rr.rsplit("_", 1)[1])
        if rr.startswith("u_a_over_"):
            uti.upgrade_level = 6
            n_over += 1
        else:
            uti.upgrade_level = 2 if num in HEAVY_ONLY_UNDERLAYS else 1
            n_unde += 1
        if d_idx >= 0 and len(r) > d_idx and r[d_idx].strip():
            set_uti_desc(uti, r[d_idx].strip())
        write_uti(uti, OVR_DIR / f"{rr}.uti")

    # Sécurité anti-contournement sur les 2 anciens templates KotOR 1 présents dans upgrade.2da
    for legacy_rr, legacy_lvl in (("g_i_upgrade005", 6), ("g_i_upgrade006", 1)):
        res = inst.resource(legacy_rr, ResourceType.UTI, order=[SearchLocation.CHITIN])
        if res:
            u = read_uti(res.data)
            u.upgrade_level = legacy_lvl
            write_uti(u, OVR_DIR / f"{legacy_rr}.uti")

    return n_unde, n_over


def build_gamorrean_1m_utis(inst: Installation) -> int:
    """Génère un jumeau exact 1M (`ov1m_001.uti..ov1m_NNN.uti`, reqfeat0=MOD_GAMORREAN_2) pour
    TOUTES les armes 2M / Doubles jouables du jeu (base, loot, uniques, reliques et doubles sabres laser).
    Conserve 100 % des stats natives, noms (+ ' (1M)'), icônes, modèles 3D et UpgradeLevel, et produit
    `mods/overhaul/gamorrean_swap_map.json` pour la bascule bidirectionnelle 2M <-> 1M en script."""
    if not MIRROR_MAP_FILE.exists():
        return 0
    mirror_map: dict[str, int] = json.loads(MIRROR_MAP_FILE.read_text(encoding="utf-8"))

    # Nettoyer les anciennes variantes 1M (m_w_*_1m.uti ou ov1m_*.uti) pour éviter tout fichier fantôme
    for old_f in list(OVR_DIR.glob("m_w_*_1m.uti")) + list(OVR_DIR.glob("ov1m_*.uti")):
        old_f.unlink()

    bi_table = read_2da(OVR_DIR / "baseitems.2da")
    tlk = read_tlk(OUT_DIR / "dialog.tlk")
    en_tlk_path = ROOT / "_reference" / "autres_mods" / "Ultimate Balancing Mod" / "dialog.tlk"
    en_tlk = read_tlk(en_tlk_path) if en_tlk_path.exists() else None
    fids: dict[str, int] = json.loads(FEAT_IDS_FILE.read_text(encoding="utf-8")) if FEAT_IDS_FILE.exists() else {}
    gam2_id = fids.get("MOD_GAMORREAN_2") or fids.get("MOD_GAMORRAN_2")
    assert gam2_id is not None, "MOD_GAMORREAN_2 absent de feat_ids.json"

    # Mapping baseitem source -> baseitem 1M (inclut Adv_Mining_Laser -> Adv_Mining_Laser_1M)
    non_mirror_keys = {"Mining_Laser", "Adv_Mining_Laser", "Adv_Mining_Laser_1M", "Plasma_Torch"}
    src_to_1m_bi: dict[str, int] = {lbl: idx for lbl, idx in mirror_map.items() if lbl not in non_mirror_keys}
    if "Adv_Mining_Laser_1M" in mirror_map:
        src_to_1m_bi["Adv_Mining_Laser"] = mirror_map["Adv_Mining_Laser_1M"]

    bi_to_label = {
        i: bi_table.get_row(i).get_string("label")
        for i in range(len(bi_table))
        if bi_table.get_row(i).get_string("label") in src_to_1m_bi
    }

    # Collecter tous les candidats UTI (Override fraîchement généré + chitin.key)
    key = read_key(GAME_PATH / "chitin.key")
    candidates: set[str] = {str(e.resref).lower() for e in key.key_entries if e.restype == ResourceType.UTI}
    for f in OVR_DIR.glob("*.uti"):
        candidates.add(f.stem.lower())

    # Exclusions strictes pour Gamorréen II (uniquement debug / arme droïde Remote / No_Damage ;
    # autorise les 3 armes 2M/D propres à 101per.mod : heavymininglaser, advancedminingla, guidonbeacon)
    gam_excluded_resrefs = {
        "killblaster",
        "killstick",
        "w_blaste_x20",
        "w_brifle_25",
    }

    swap_map: list[dict[str, str]] = []
    idx = 0
    for rr in sorted(candidates):
        if rr.startswith(WEAPON_ULVL_EXCLUDED_PREFIXES) or rr in gam_excluded_resrefs:
            continue
        if rr.startswith(("m_w_", "ov1m_", "ov_")):
            continue
        ovr_path = OVR_DIR / f"{rr}.uti"
        if ovr_path.exists():
            uti = read_uti(ovr_path)
        else:
            res = inst.resource(rr, ResourceType.UTI, order=[SearchLocation.CHITIN])
            if not res:
                continue
            try:
                uti = read_uti(res.data)
            except Exception:
                continue

        bi_lbl = bi_to_label.get(uti.base_item)
        if not bi_lbl or bi_lbl not in src_to_1m_bi:
            continue
        if any(p.property_name == 31 for p in uti.properties):  # Exclure No_Damage
            continue

        orig_tag = (uti.tag or rr).strip().lower()
        idx += 1
        dst_rr = f"ov1m_{idx:03d}"

        # Résoudre le nom VF et EN d'origine pour ajouter " (1M)" / " (1H)" lisiblement dans l'inventaire
        orig_name_fr = uti.name.get(Language.FRENCH, Gender.MALE) or uti.name.get(Language.ENGLISH, Gender.MALE)
        if not orig_name_fr and uti.name.stringref is not None and 0 <= uti.name.stringref < len(tlk):
            orig_name_fr = tlk.get(uti.name.stringref).text
        orig_name_en = uti.name.get(Language.ENGLISH, Gender.MALE)
        if not orig_name_en and en_tlk is not None and uti.name.stringref is not None and 0 <= uti.name.stringref < len(en_tlk):
            orig_name_en = re.sub(r"\{[^}]*\}", "", en_tlk.get(uti.name.stringref).text).strip()
        if not orig_name_en:
            orig_name_en = orig_name_fr
        if orig_name_fr:
            ls_nm = LocalizedString.from_invalid()
            ls_nm.set_data(Language.FRENCH, Gender.MALE, f"{orig_name_fr} (1M)")
            ls_nm.set_data(Language.ENGLISH, Gender.MALE, f"{orig_name_en} (1H)")
            uti.name = ls_nm

        uti.base_item = src_to_1m_bi[bi_lbl]
        # Double verrou : baseitems.2da reqfeat0=MOD_GAMORREAN_2 + Use_Limitation_Feat (prop 57) visible en fiche objet !
        if not any(p.property_name == 57 and p.subtype == gam2_id for p in uti.properties):
            uti.properties.append(make_prop(57, gam2_id, 0, 0))

        # Option B (Gamorréen II) : indiquer sur toutes les armes haute cadence (1M) que l'attaque bonus
        # n'est valide qu'en main principale (aucun bonus d'attaque en main gauche, sans malus de CA)
        if bi_lbl in {
            "Quarter_Staff", "Double_Bladed_Sword", "Vibro_Double_Blade",
            "Double_Bladed_Lightsaber", "Wookie_Warblade",
            "Repeating_Blaster", "Heavy_Repeating_Blaster",
        }:
            orig_desc_fr = uti.description.get(Language.FRENCH, Gender.MALE) or uti.description.get(Language.ENGLISH, Gender.MALE)
            if not orig_desc_fr and uti.description.stringref is not None and 0 <= uti.description.stringref < len(tlk):
                orig_desc_fr = tlk.get(uti.description.stringref).text
            orig_desc_en = uti.description.get(Language.ENGLISH, Gender.MALE)
            if not orig_desc_en and en_tlk is not None and uti.description.stringref is not None and 0 <= uti.description.stringref < len(en_tlk):
                orig_desc_en = re.sub(r"\{[^}]*\}", "", en_tlk.get(uti.description.stringref).text).strip()
            hc_note_fr = (
                "[Mod D20-Overhaul — Arme haute cadence (1M)]\n"
                "En main principale (main droite), cette arme conserve +1 attaque supplémentaire par round "
                "(plafond moteur +2 avec Vitesse de Force ou Tir d'Assaut III, sans malus de CA). "
                "Équipée en main gauche, elle n'octroie pas d'attaque supplémentaire."
            )
            hc_note_en = (
                "[Mod D20-Overhaul — High-Rate Weapon (1H)]\n"
                "When equipped in your main hand (right hand), this weapon retains +1 extra attack per round "
                "(engine cap +2 with Force Speed or Assault Fire III, with no AC penalty). "
                "When equipped in your off-hand, it grants no extra attack."
            )
            full_desc_fr = f"{orig_desc_fr.rstrip()}\n\n{hc_note_fr}" if orig_desc_fr and orig_desc_fr.strip() else hc_note_fr
            full_desc_en = f"{orig_desc_en.rstrip()}\n\n{hc_note_en}" if orig_desc_en and orig_desc_en.strip() else hc_note_en
            set_uti_desc(uti, full_desc_fr, full_desc_en)

        uti.resref.set_data(dst_rr)
        uti.tag = dst_rr
        write_uti(uti, OVR_DIR / f"{dst_rr}.uti")

        swap_map.append({
            "tag_2m": orig_tag,
            "res_2m": rr,
            "tag_1m": dst_rr,
            "res_1m": dst_rr,
            "baseitem_label": bi_lbl,
        })

    GAM_SWAP_MAP_FILE.write_text(json.dumps(swap_map, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return len(swap_map)


def build_gamorrean_adapter_item_and_dlg(inst: Installation) -> tuple[int, int, int]:
    """Génère :
      1. `ov_gam_adapt.uti` : objet réutilisable (Adaptateur Gamorréen, BaseItem=54 Combat_Shots utilisable
         même à 100% PV depuis le HUD Stimulants ET l'Inventaire, auto-réapprovisionné dans `ov_gam_use`).
      2. `ov_gam_term.utp` : terminal invisible temporaire (cloné de `plc_invis`) permettant d'ouvrir
         proprement le dialogue COMPUTER (le moteur interdit l'auto-dialogue créature -> soi-même).
      3. `ov_gam_conv.dlg` : menu terminal (ConversationType=1) permettant de :
         - Ouvrir l'écran d'amélioration (ShowUpgradeScreen) pour retirer ses pièces avant conversion
         - Convertir l'arme en main droite (2M <-> 1M)
         - Rouvrir immédiatement l'écran d'amélioration après conversion pour remonter ses pièces."""
    sids: dict[str, int] = json.loads(SPELL_IDS_FILE.read_text(encoding="utf-8")) if SPELL_IDS_FILE.exists() else {}
    gam_spell_id = sids.get("ITEM_ABILITY_GAMORREAN_ADAPT")
    assert gam_spell_id is not None, "ITEM_ABILITY_GAMORREAN_ADAPT absent de spell_ids.json"

    # 1. Objet utilitaire réutilisable ov_gam_adapt.uti (cloné de g_i_cmbtshot001, bi=54 Combat_Shots)
    res_it = inst.resource("g_i_cmbtshot001", ResourceType.UTI, order=[SearchLocation.CHITIN])
    assert res_it, "g_i_cmbtshot001 introuvable"
    uti = read_uti(res_it.data)
    uti.resref.set_data("ov_gam_adapt")
    uti.tag = "ov_gam_adapt"
    uti.cost = 0
    uti.additional_cost = 0
    uti.stack_size = 1
    uti.charges = 1
    uti.plot = False  # plot=False indispensable pour apparaitre en barre d'action HUD & onglet Consommables !
    uti.properties = [make_prop(10, gam_spell_id, 3, 13)]  # CastSpell, Unlimited_Use (cost_value=13, evite la perte d'item)
    ls_name = LocalizedString.from_invalid()
    ls_name.set_data(Language.FRENCH, Gender.MALE, "Adaptateur Gamorréen (2M / 1M)")
    ls_name.set_data(Language.ENGLISH, Gender.MALE, "Gamorrean Adapter (2H / 1H)")
    uti.name = ls_name
    set_uti_desc(
        uti,
        "[Mod D20-Overhaul]\n"
        "Le goût insatiable des Gamorréens pour la guerre les a poussés à bricoler cet établi de campagne "
        "sommaire mais indestructible, pensé pour ajuster, démonter et rééquilibrer n'importe quel armement "
        "lourd sur le terrain, en tout lieu.\n\n"
        "---\n"
        "Mode d'emploi (Raffinement Gamorréen II) :\n"
        "Objet réutilisable à l'infini, utilisable en posture hors combat (depuis le slot Stimulants du HUD "
        "ou l'Inventaire) :\n"
        "- Ouvre l'établi d'amélioration portatif à tout moment, quelle que soit l'arme équipée ;\n"
        "- Convertit l'arme à deux mains (2M) ou haute cadence / double (D) tenue en main droite (mêlée et "
        "distance) vers sa version à une main (1M), ou inversement.\n\n"
        "ATTENTION : retirez toujours les améliorations de votre arme à l'établi AVANT de la convertir "
        "(sinon elles seront définitivement perdues), puis remontez-les après conversion. "
        "Les armes converties en 1M requièrent le don Raffinement Gamorréen II pour être équipées.",
        "[Mod D20-Overhaul]\n"
        "The Gamorreans' insatiable appetite for warfare led them to cobble together this crude yet "
        "indestructible field workbench, built to tune, strip down, and rebalance any heavy armament "
        "in the field, anywhere.\n\n"
        "---\n"
        "Instructions (Gamorrean Refinement II):\n"
        "Infinitely reusable item, usable out of combat (from the HUD Stims slot or Inventory):\n"
        "- Opens the portable upgrade workbench at any time, regardless of equipped weapon;\n"
        "- Converts the two-handed (2H) or high-rate / double-bladed (D) weapon held in your main hand "
        "(melee or ranged) into its one-handed (1H) version, and vice versa.\n\n"
        "WARNING: Always remove all upgrades from your weapon at the workbench BEFORE converting it "
        "(otherwise they will be permanently lost), then reinstall them afterward. "
        "Weapons converted to 1H require the Gamorrean Refinement II feat to equip.",
    )
    write_uti(uti, OVR_DIR / "ov_gam_adapt.uti")

    # 2. Placeable invisible temporaire ov_gam_term.utp (cloné de plc_invis) pour supporter le dialogue COMPUTER
    res_utp = inst.resource("plc_invis", ResourceType.UTP, order=[SearchLocation.CHITIN])
    assert res_utp, "plc_invis.utp introuvable"
    utp = read_utp(res_utp.data)
    utp.resref.set_data("ov_gam_term")
    utp.tag = "ov_gam_term"
    utp.conversation.set_data("ov_gam_conv")
    utp.useable = False
    utp.static = False
    utp.plot = True
    utp.min1_hp = True
    utp.has_inventory = False
    utp.not_blastable = True
    ls_term = LocalizedString.from_invalid()
    ls_term.set_data(Language.FRENCH, Gender.MALE, "Adaptateur Gamorréen")
    ls_term.set_data(Language.ENGLISH, Gender.MALE, "Gamorrean Adapter")
    utp.name = ls_term
    write_utp(utp, OVR_DIR / "ov_gam_term.utp")

    # 2. Dialogue terminal ov_gam_conv.dlg (cloné du schéma exact de 000_medstation.dlg)
    res_dlg = inst.resource("000_medstation", ResourceType.DLG, order=[SearchLocation.CHITIN])
    assert res_dlg, "000_medstation.dlg introuvable"
    gff = read_gff(res_dlg.data)

    orig_entries = gff.root.get_list("EntryList")
    orig_replies = gff.root.get_list("ReplyList")
    orig_starters = gff.root.get_list("StartingList")
    tmpl_entry = copy.deepcopy(orig_entries.at(0))
    tmpl_reply = copy.deepcopy(orig_replies.at(0))
    tmpl_starter = copy.deepcopy(orig_starters.at(0))
    tmpl_rep_link = next(
        copy.deepcopy(orig_entries.at(i).get_list("RepliesList").at(0))
        for i in range(len(orig_entries))
        if len(orig_entries.at(i).get_list("RepliesList")) > 0
    )
    tmpl_ent_link = next(
        copy.deepcopy(orig_replies.at(i).get_list("EntriesList").at(0))
        for i in range(len(orig_replies))
        if len(orig_replies.at(i).get_list("EntriesList")) > 0
    )

    def _loc(txt: str) -> LocalizedString:
        ls = LocalizedString.from_invalid()
        ls.set_data(Language.FRENCH, Gender.MALE, txt)
        ls.set_data(Language.ENGLISH, Gender.MALE, txt)
        return ls

    def _link(tmpl, target_idx: int, pos_idx: int, active: str = ""):
        lk = copy.deepcopy(tmpl)
        lk.struct_id = pos_idx
        lk.set_uint32("Index", target_idx)
        lk.set_resref("Active", ResRef(active))
        if lk.exists("Active2"):
            lk.set_resref("Active2", ResRef(""))
        if lk.exists("Param1"):
            lk.set_int32("Param1", 0)
        if lk.exists("Not"):
            lk.set_uint8("Not", 0)
        if lk.exists("Not2"):
            lk.set_uint8("Not2", 0)
        return lk

    new_entries = GFFList()
    new_replies = GFFList()
    new_starters = GFFList()

    def _add_entry(txt: str, reply_indices: list[int]) -> int:
        ent = copy.deepcopy(tmpl_entry)
        idx = len(new_entries)
        ent.struct_id = idx
        ent.set_string("Speaker", "")
        ent.set_locstring("Text", _loc(txt))
        ent.set_resref("VO_ResRef", ResRef(""))
        ent.set_resref("Sound", ResRef(""))
        if ent.exists("SoundExists"):
            ent.set_uint8("SoundExists", 0)
        if ent.exists("Delay"):
            ent.set_uint32("Delay", 4294967295)
        if ent.exists("NodeID"):
            ent.set_int32("NodeID", idx + 1)
        ent.set_resref("Script", ResRef(""))
        ent.set_resref("Script2", ResRef(""))
        ent.set_int32("ActionParam1", 0)
        ent.set_int32("ActionParam2", 0)
        if ent.exists("ActionParamStrA"):
            ent.set_string("ActionParamStrA", "")
        if ent.exists("ActionParamStrB"):
            ent.set_string("ActionParamStrB", "")
        rl = GFFList()
        for pos_i, ri in enumerate(reply_indices):
            rl._structs.append(_link(tmpl_rep_link, ri, pos_i))
        ent.set_list("RepliesList", rl)
        new_entries._structs.append(ent)
        return idx

    def _add_reply(txt: str, script: str = "", next_entries: list[int] | None = None) -> int:
        rep = copy.deepcopy(tmpl_reply)
        idx = len(new_replies)
        rep.struct_id = idx
        rep.set_locstring("Text", _loc(txt))
        rep.set_resref("VO_ResRef", ResRef(""))
        rep.set_resref("Sound", ResRef(""))
        rep.set_resref("Script", ResRef(script))
        rep.set_resref("Script2", ResRef(""))
        rep.set_int32("ActionParam1", 0)
        rep.set_int32("ActionParam2", 0)
        if rep.exists("ActionParamStrA"):
            rep.set_string("ActionParamStrA", "")
        if rep.exists("ActionParamStrB"):
            rep.set_string("ActionParamStrB", "")
        el = GFFList()
        for pos_i, ei in enumerate(next_entries or []):
            el._structs.append(_link(tmpl_ent_link, ei, pos_i))
        rep.set_list("EntriesList", el)
        new_replies._structs.append(rep)
        return idx

    # Replies : établi toujours disponible (quelle que soit l'arme équipée) + conversion si arme 2M/D/1M en main droite
    r_upgr = _add_reply(
        "1. Ouvrir l'établi d'amélioration (retirer ou remonter mes pièces)",
        script="ov_gam_a_upgr",
    )
    r_swap = _add_reply(
        "2. Convertir l'arme équipée en main droite (2M/D - 1M)",
        script="ov_gam_a_swap",
    )
    r_cancel = _add_reply("3. Annuler")
    r_upgr_only = _add_reply(
        "1. Ouvrir l'établi d'amélioration",
        script="ov_gam_a_upgr",
    )
    r_close_2 = _add_reply("2. Fermer")
    r_close = _add_reply("Fermer")

    # Entries :
    #   0: Menu complet (établi + conversion 2M/D - 1M) avec avertissement explicite sur les améliorations
    #   1: Menu établi seul (établi portatif toujours accessible, même sans arme 2M/D équipée en main droite)
    #   2: Fallback (pas le don Raffinement Gamorréen II ou en combat)
    e_main = _add_entry(
        "[ÉTABLI PORTATIF GAMORRÉEN — ADAPTATION 2M/D ET 1M]\n\n"
        "Permet d'ouvrir l'établi d'amélioration en tout lieu, ou de convertir votre arme à deux mains (2M) "
        "ou haute cadence / double (D) tenue en main droite (mêlée et distance) vers son équivalent à une main (1M), "
        "et inversement.\n\n"
        "ATTENTION — AMÉLIORATIONS :\n"
        "Les améliorations montées sur l'arme ne peuvent pas être transférées automatiquement lors de la conversion.\n"
        "• Utilisez d'abord « Ouvrir l'établi d'amélioration » pour RETIRER toutes les pièces de votre arme "
        "(sinon elles seront DÉFINITIVEMENT PERDUES) ;\n"
        "• Utilisez ensuite « Convertir l'arme équipée » ;\n"
        "• Rouvrez enfin l'établi pour remonter vos pièces sur l'arme convertie.",
        [r_upgr, r_swap, r_cancel],
    )
    e_wb_only = _add_entry(
        "[ÉTABLI PORTATIF GAMORRÉEN]\n\n"
        "L'établi d'amélioration portatif est prêt à être utilisé.\n\n"
        "(Conversion 2M/D - 1M indisponible : aucune arme à deux mains, double, haute cadence ou déjà adaptée en 1M "
        "n'est actuellement équipée en main droite.)",
        [r_upgr_only, r_close_2],
    )
    e_fallback = _add_entry(
        "[ÉTABLI PORTATIF GAMORRÉEN]\n\n"
        "Utilisation impossible pour le moment.\n"
        "Vérifiez que :\n"
        "- Ce personnage possède le don Raffinement Gamorréen II ;\n"
        "- Vous êtes en posture hors combat.",
        [r_close],
    )

    # StartingList : Entry 0 si ov_gam_c_can == TRUE, Entry 1 si ov_gam_c_wb == TRUE, sinon Entry 2
    new_starters._structs.append(_link(tmpl_starter, e_main, 0, active="ov_gam_c_can"))
    new_starters._structs.append(_link(tmpl_starter, e_wb_only, 1, active="ov_gam_c_wb"))
    new_starters._structs.append(_link(tmpl_starter, e_fallback, 2, active=""))

    gff.root.set_int32("ConversationType", 1)  # CONVERSATION_TYPE_COMPUTER
    gff.root.set_uint8("UnequipItems", 0)
    gff.root.set_uint8("UnequipHItem", 0)
    gff.root.set_resref("EndConversation", ResRef("ov_gam_end"))
    gff.root.set_resref("EndConverAbort", ResRef("ov_gam_end"))
    gff.root.set_string("VO_ID", "")
    gff.root.set_list("EntryList", new_entries)
    gff.root.set_list("ReplyList", new_replies)
    gff.root.set_list("StartingList", new_starters)
    write_gff(gff, OVR_DIR / "ov_gam_conv.dlg")
    return 1, 1, 1


def _parse_upgrade_props(mod_txt: str, old_props: list[UTIProperty]) -> list[UTIProperty]:
    """Convertit la colonne `Changement (mod)` de `Améliorations.csv` en liste UTIProperty."""
    old_skill_sub = next((p.subtype for p in old_props if p.property_name == 36), 0)
    out: list[UTIProperty] = []
    for raw in [s.strip() for s in mod_txt.split(",") if s.strip()]:
        s = norm(raw)
        if s == "acere":
            out.append(make_prop(28, 0, 0, 0))
            continue
        m = re.match(r"bonus aux degats \((\w+)\) \+(\d+d\d+|\d+)", s)
        if m:
            sub = DMG_TYPE_SUB.get(m.group(1), 12)
            cv = DMG_COST_MAP.get(m.group(2), 1)
            out.append(make_prop(11, sub, 4, cv))
            continue
        m = re.match(r"bonus aux degats contre (?:droides|race) \+(\d+d\d+|\d+)", s)
        if m:
            p = make_prop(13, 5, 4, DMG_COST_MAP.get(m.group(1), 6))
            p.param1, p.param1_value = 0, 11
            out.append(p)
            continue
        m = re.match(r"bonus aux degats contre cote obscur \+(\d+d\d+|\d+)", s)
        if m:
            p = make_prop(12, 3, 4, DMG_COST_MAP.get(m.group(1), 8))
            p.param1, p.param1_value = 0, 0
            out.append(p)
            continue
        m = re.match(r"coups critiques plus importants \+(\d+d\d+|\d+)", s)
        if m:
            out.append(make_prop(49, 0, 4, DMG_COST_MAP.get(m.group(1), 6)))
            continue
        m = re.match(r"bonus d attaque \+(\d+)", s)
        if m:
            out.append(make_prop(38, 0, 2, int(m.group(1))))
            continue
        m = re.match(r"malus a l attaque -(\d+)", s)
        if m:
            out.append(make_prop(8, 0, 20, int(m.group(1))))
            continue
        m = re.match(r"bonus defense \+(\d+)", s)
        if m:
            out.append(make_prop(1, 0, 2, int(m.group(1))))
            continue
        m = re.match(r"malus de defense -(\d+)", s)
        if m:
            out.append(make_prop(20, 0, 20, int(m.group(1))))
            continue
        m = re.match(r"jets de sauvegarde ameliores \+(\d+)", s)
        if m:
            out.append(make_prop(27, 0, 2, int(m.group(1))))
            continue
        m = re.match(r"parade tirs de blaster \+(\d+)", s)
        if m:
            out.append(make_prop(55, 0, 1, int(m.group(1))))
            continue
        m = re.match(r"parade tirs de blaster -(\d+)", s)
        if m:
            out.append(make_prop(56, 0, 21, int(m.group(1))))
            continue
        m = re.match(r"bonus de caracteristique \((\w+)\) \+(\d+)", s)
        if m:
            out.append(make_prop(0, ABILITY_EN_SUB.get(m.group(1), 0), 1, int(m.group(2))))
            continue
        m = re.match(r"bonus de competence \+(\d+)", s)
        if m:
            out.append(make_prop(36, old_skill_sub, 1, int(m.group(1))))
            continue
        m = re.match(r"regeneration de points de force \+(\d+)", s)
        if m:
            out.append(make_prop(54, 0, 2, int(m.group(1))))
            continue
        m = re.match(r"regeneration \+(\d+)", s)
        if m:
            out.append(make_prop(35, 0, 2, int(m.group(1))))
            continue
        m = re.match(r"resistance aux degats \((\w+)\) \+(\d+)/-", s)
        if m:
            out.append(make_prop(17, DMG_TYPE_SUB.get(m.group(1), 8), 7, RD_TO_COST.get(int(m.group(2)), 1)))
            continue
        if "restriction d alignement (lumineux)" in s:
            out.append(make_prop(43, 2, 0, 0))
            continue
        if "restriction d alignement (obscur)" in s:
            out.append(make_prop(43, 3, 0, 0))
            continue
        m = re.match(r"en cas de coup au but \((\w+)\s*:\s*dd\s*(\d+)", s)
        if m:
            sub = ONHIT_FR_SUB.get(m.group(1), 1)
            base_dc = int(m.group(2))
            cv = 1 if base_dc <= 4 else (2 if base_dc <= 6 else 4)
            p = make_prop(32, sub, 25, cv)
            p.param1, p.param1_value = 1, 0
            out.append(p)
            continue
    return out


def build_weapon_upgrades(inst: Installation) -> int:
    """Applique le cloisonnement (`upgrade_level` 1/2/3) et le calibrage des 156 améliorations
    d'armes/sabres (`Améliorations.csv`), plus les 7 templates legacy `g_i_upgrade00*`."""
    if not CSV_UPGRADES.exists():
        return 0
    with open(CSV_UPGRADES, encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.reader(fh))
    d_idx = rows[0].index("Description (mod)") if rows and "Description (mod)" in rows[0] else -1
    count = 0
    for r in rows[1:]:
        if len(r) < 7:
            continue
        rr = r[0].strip().lower()
        if not rr.startswith(("u_m_", "u_r_", "u_l_")):
            continue
        mod_txt = r[6].strip()
        has_mod_props = bool(mod_txt) and norm(mod_txt) != "inchange"
        target_ulvl = next((lvl for pref, lvl in WEAPON_UPGRADE_LEVEL_BY_PREFIX.items() if rr.startswith(pref)), None)
        if not has_mod_props and target_ulvl is None:
            continue
        res = inst.resource(rr, ResourceType.UTI, order=[SearchLocation.CHITIN]) or inst.resource(rr, ResourceType.UTI)
        if not res:
            continue
        uti = read_uti(res.data)
        dirty = False
        if has_mod_props:
            new_props = _parse_upgrade_props(mod_txt, uti.properties)
            if new_props:
                uti.properties = new_props
                if d_idx >= 0 and len(r) > d_idx and r[d_idx].strip():
                    set_uti_desc(uti, r[d_idx].strip())
                dirty = True
        if target_ulvl is not None:
            uti.upgrade_level = target_ulvl
            dirty = True
        if dirty:
            write_uti(uti, OVR_DIR / f"{rr}.uti")
            count += 1

    # Cloisonner aussi les 7 templates legacy KotOR 1 encore présents dans upgrade.2da
    for rr, lvl in LEGACY_WEAPON_UPGRADE_ULVL.items():
        res = inst.resource(rr, ResourceType.UTI, order=[SearchLocation.CHITIN]) or inst.resource(rr, ResourceType.UTI)
        if not res:
            continue
        uti = read_uti(res.data)
        uti.upgrade_level = lvl
        write_uti(uti, OVR_DIR / f"{rr}.uti")
        count += 1
    return count


def build_weapon_slots_partition(inst: Installation) -> tuple[int, dict[int, int], int]:
    """Aligne `upgrade_level` (0 pour les 6 reliques, 1 / 2 / 3 par famille) et applique le
    calibrage B2-1a des bonus de dégâts `.uti` sur toutes les armes jouables (mêlée & distance).

    Exclut automatiquement les props/décor, objets debug, outils utilitaires Péragus
    (plasmatorch, lasers miniers, vibrocutter, guidonbeacon) et armes No_Damage (w_brifle_25)."""
    candidates: set[str] = set()
    key = read_key(GAME_PATH / "chitin.key")
    for entry in key.key_entries:
        if entry.restype == ResourceType.UTI:
            candidates.add(str(entry.resref).lower())
    game_ovr = GAME_PATH / "Override"
    if game_ovr.exists():
        for f in game_ovr.glob("*.uti"):
            candidates.add(f.stem.lower())

    counts_by_lvl: dict[int, int] = {0: 0, 1: 0, 2: 0, 3: 0}
    written = 0
    b2_modified = 0

    for rr in sorted(candidates):
        if rr.startswith(WEAPON_ULVL_EXCLUDED_PREFIXES) or rr in WEAPON_ULVL_EXCLUDED_RESREFS:
            continue
        res = inst.resource(rr, ResourceType.UTI, order=[SearchLocation.CHITIN]) or inst.resource(rr, ResourceType.UTI)
        if not res:
            continue
        try:
            uti = read_uti(res.data)
        except Exception:
            continue
        target_ulvl = WEAPON_BASEITEM_ULVL.get(uti.base_item)
        if target_ulvl is None:
            continue
        # Exclure les armes utilitaires No_Damage (property_name == 31)
        if any(p.property_name == 31 for p in uti.properties):
            continue
        final_ulvl, was_mod = _apply_weapon_b2_balance(rr, uti, target_ulvl)
        write_uti(uti, OVR_DIR / f"{rr}.uti")
        counts_by_lvl[final_ulvl] = counts_by_lvl.get(final_ulvl, 0) + 1
        written += 1
        if was_mod:
            b2_modified += 1

    # Armes jouables uniquement présentes dans les modules (.mod)
    for mod_name, target_rr in MODULE_PLAYABLE_WEAPONS:
        if target_rr in candidates:
            continue
        mod_path = GAME_PATH / "Modules" / mod_name
        if not mod_path.exists():
            continue
        erf = read_erf(mod_path)
        for res in erf:
            if res.restype == ResourceType.UTI and str(res.resref).lower() == target_rr:
                uti = read_uti(res.data)
                target_ulvl = WEAPON_BASEITEM_ULVL.get(uti.base_item)
                if target_ulvl is not None and not any(p.property_name == 31 for p in uti.properties):
                    final_ulvl, was_mod = _apply_weapon_b2_balance(target_rr, uti, target_ulvl)
                    write_uti(uti, OVR_DIR / f"{target_rr}.uti")
                    counts_by_lvl[final_ulvl] = counts_by_lvl.get(final_ulvl, 0) + 1
                    written += 1
                    if was_mod:
                        b2_modified += 1
                break

    return written, counts_by_lvl, b2_modified


def build_personal_crystals(inst: Installation) -> int:
    """Génère les 90 variantes .uti du Cristal personnel de l'Exilé (3 paliers × 30 paires de stats) :
    ov_crys_<tier>_<s1><s2>.uti (tier 1: +2/+1/0 ; tier 2: +4/+2/+1 ; tier 3: +6/+4/+2)."""
    res_base = inst.resource("qcrystal_1_2", ResourceType.UTI)
    if not res_base:
        return 0
    tier_bonuses = {1: (2, 1, 0), 2: (4, 2, 1), 3: (6, 4, 2)}
    count = 0
    for tier, (b1, b2, b_other) in tier_bonuses.items():
        for s1 in range(6):
            for s2 in range(6):
                if s1 == s2:
                    continue
                rr = f"ov_crys_{tier}_{s1}{s2}"
                uti = read_uti(res_base.data)
                uti.resref.set_data(rr)
                uti.tag = rr
                props = [make_prop(62, 0, 0, 0)]  # Personal Crystal flag
                for st in range(6):
                    val = b1 if st == s1 else (b2 if st == s2 else b_other)
                    if val > 0:
                        props.append(make_prop(0, st, 1, val))
                uti.properties = props
                write_uti(uti, OVR_DIR / f"{rr}.uti")
                count += 1
    return count


def build_plasma_torch_vanilla() -> int:
    """Restaure les dégâts vanilla (1d1 + 1d6 Feu) de la Torche à plasma (plasmatorch.uti)
    via le baseitem dédié Plasma_Torch (sans affecter les Matraques 1d8)."""
    if not MIRROR_MAP_FILE.exists():
        return 0
    mirror_map: dict[str, int] = json.loads(MIRROR_MAP_FILE.read_text(encoding="utf-8"))
    pt_bi = mirror_map.get("Plasma_Torch")
    if pt_bi is None:
        return 0
    from pykotor.resource.formats.erf import read_erf
    mod_path = GAME_PATH / "Modules" / "101per.mod"
    if not mod_path.exists():
        return 0
    erf = read_erf(mod_path)
    for res in erf:
        if res.restype == ResourceType.UTI and str(res.resref).lower() == "plasmatorch":
            uti = read_uti(res.data)
            uti.base_item = pt_bi
            write_uti(uti, OVR_DIR / "plasmatorch.uti")
            return 1
    return 0


def build_mining_lasers_k2cp(inst: Installation) -> int:
    """Aligne mininglaser.uti (1d7) et advancedminingla.uti (1d11) sur les baseitems dédiés
    Mining_Laser (104) et Adv_Mining_Laser (105), 100 % compatibles avec K2CP v1.6.3,
    et extrait aussi heavymininglaser.uti + guidonbeacon.uti depuis 101per.mod dans Override/
    pour que leur bascule 2M/D <-> 1M fonctionne dans tous les modules du jeu."""
    if not MIRROR_MAP_FILE.exists():
        return 0
    mirror_map: dict[str, int] = json.loads(MIRROR_MAP_FILE.read_text(encoding="utf-8"))
    targets = [
        ("mininglaser", mirror_map.get("Mining_Laser")),
        ("advancedminingla", mirror_map.get("Adv_Mining_Laser")),
    ]
    count = 0
    for rr, bi_idx in targets:
        if bi_idx is None:
            continue
        res = inst.resource(rr, ResourceType.UTI, order=[SearchLocation.CHITIN]) or inst.resource(rr, ResourceType.UTI)
        if res is None:
            continue
        uti = read_uti(res.data)
        uti.base_item = bi_idx
        write_uti(uti, OVR_DIR / f"{rr}.uti")
        count += 1

    # Extraire les 2 autres armes 2M/D propres à 101per.mod (Laser de forage lourd & Balise de guidage)
    mod_path = GAME_PATH / "Modules" / "101per.mod"
    if mod_path.exists():
        erf = read_erf(mod_path)
        for res in erf:
            if res.restype == ResourceType.UTI and str(res.resref).lower() in ("heavymininglaser", "guidonbeacon"):
                rr = str(res.resref).lower()
                uti = read_uti(res.data)
                write_uti(uti, OVR_DIR / f"{rr}.uti")
                count += 1
    return count


def build_craftable_base_weapons(inst: Installation) -> int:
    """Génère les 2 armes de base craftables ajoutées dans Craft.csv / itemcreate.2da
    qui n'ont pas de modèle de base propre dans vanilla :
      - w_melee_ww_base.uti (Lame de guerre wookie, baseitem 79, ulvl 2, sans bonus de relique)
      - w_brifle_hr_base.uti (Blaster lourd à répétition, baseitem 24, ulvl 3, sans bonus gratuit)"""
    specs = [
        (
            "w_melee_30",
            "w_melee_ww_base",
            79,
            2,
            "Lame de guerre wookie",
            "Wookiee Warblade",
            "[Mod D20-Overhaul]\nLame de guerre wookie de facture standard (arme double, 2 slots : Poignée + Lame).",
            "[Mod D20-Overhaul]\nStandard-issue Wookiee warblade (double-bladed weapon, 2 slots: Grip + Edge).",
        ),
        (
            "w_brifle_17",
            "w_brifle_hr_base",
            24,
            3,
            "Blaster lourd à répétition",
            "Heavy Repeating Blaster",
            "[Mod D20-Overhaul]\nBlaster lourd à répétition de série (arme à répétition, 3 slots : Lunette + Pack + Chambrage).",
            "[Mod D20-Overhaul]\nStandard-issue heavy repeating blaster (repeating weapon, 3 slots: Scope + Power Pack + Firing Chamber).",
        ),
    ]
    count = 0
    for src_rr, dst_rr, bi_id, ulvl, name_fr, name_en, desc_fr, desc_en in specs:
        res = inst.resource(src_rr, ResourceType.UTI, order=[SearchLocation.CHITIN]) or inst.resource(src_rr, ResourceType.UTI)
        if not res:
            continue
        uti = read_uti(res.data)
        uti.base_item = bi_id
        uti.upgrade_level = ulvl
        uti.properties = []
        uti.cost = 100
        uti.additional_cost = 0
        uti.resref.set_data(dst_rr)
        uti.tag = dst_rr
        ls_name = LocalizedString.from_invalid()
        ls_name.set_data(Language.FRENCH, Gender.MALE, name_fr)
        ls_name.set_data(Language.ENGLISH, Gender.MALE, name_en)
        uti.name = ls_name
        set_uti_desc(uti, desc_fr, desc_en)
        write_uti(uti, OVR_DIR / f"{dst_rr}.uti")
        count += 1
    return count


def build_kreia_crystal_dlg(inst: Installation) -> int:
    """Patch kreia.dlg autour d'EntryList[288] pour offrir un choix au joueur lors de
    l'accordage du Cristal personnel avec Kreia :
      - Automatique (2 meilleures caractéristiques de base, ActionParam1=0, ActionParam2=0)
      - Manuel (choix de la caractéristique principale + secondaire -> ActionParam1=s1+1, ActionParam2=s2+1)
    Préserve la voix VO (gblkreia054) et tout le reste du dialogue TSLRCM intact."""
    res = inst.resource("kreia", ResourceType.DLG, order=[SearchLocation.OVERRIDE, SearchLocation.CHITIN])
    if not res:
        return 0
    gff = read_gff(res.data)
    entries = gff.root.get_list("EntryList")
    replies = gff.root.get_list("ReplyList")
    if len(entries) <= 289 or len(replies) <= 309:
        return 0

    e288 = entries.at(288)
    if str(e288.get_resref("Script")).lower() != "a_q_cryst_change":
        # Sécurité : chercher l'entrée portant a_q_cryst_change si l'index différait
        found_idx = None
        for idx in range(len(entries)):
            if str(entries.at(idx).get_resref("Script")).lower() == "a_q_cryst_change":
                found_idx = idx
                break
        if found_idx is None:
            return 0
        e288 = entries.at(found_idx)

    orig_replies = e288.get_list("RepliesList")
    if len(orig_replies) == 0:
        return 0
    tmpl_rep_link = copy.deepcopy(orig_replies.at(0))
    orig_ridx = tmpl_rep_link.get_uint32("Index")
    tmpl_reply = copy.deepcopy(replies.at(orig_ridx))
    orig_entries = tmpl_reply.get_list("EntriesList")
    if len(orig_entries) == 0:
        return 0
    tmpl_ent_link = copy.deepcopy(orig_entries.at(0))
    next_entry_idx = tmpl_ent_link.get_uint32("Index")  # EntryList[289]

    def _make_loc(txt: str) -> LocalizedString:
        ls = LocalizedString.from_invalid()
        ls.set_data(Language.FRENCH, Gender.MALE, txt)
        ls.set_data(Language.ENGLISH, Gender.MALE, txt)
        return ls

    def _make_link(tmpl, target_idx: int, pos_idx: int):
        lk = copy.deepcopy(tmpl)
        lk.struct_id = pos_idx
        lk.set_uint32("Index", target_idx)
        lk.set_resref("Active", ResRef(""))
        if lk.exists("Active2"):
            lk.set_resref("Active2", ResRef(""))
        return lk

    def _make_entry(txt: str, reply_indices: list[int]) -> int:
        ent = copy.deepcopy(e288)
        new_idx = len(entries)
        ent.struct_id = new_idx
        ent.set_locstring("Text", _make_loc(txt))
        ent.set_resref("VO_ResRef", ResRef(""))
        ent.set_resref("Sound", ResRef(""))
        if ent.exists("SoundExists"):
            ent.set_uint8("SoundExists", 0)
        ent.set_resref("Script", ResRef(""))
        ent.set_int32("ActionParam1", 0)
        ent.set_int32("ActionParam2", 0)
        rl = GFFList()
        for pos_i, r_i in enumerate(reply_indices):
            rl._structs.append(_make_link(tmpl_rep_link, r_i, pos_i))
        ent.set_list("RepliesList", rl)
        entries._structs.append(ent)
        return new_idx

    def _make_reply(txt: str, entry_idx: int, script_name: str = "", p1: int = 0, p2: int = 0) -> int:
        rep = copy.deepcopy(tmpl_reply)
        new_idx = len(replies)
        rep.struct_id = new_idx
        rep.set_locstring("Text", _make_loc(txt))
        rep.set_resref("Script", ResRef(script_name))
        if rep.exists("ActionParam1"):
            rep.set_int32("ActionParam1", p1)
        if rep.exists("ActionParam2"):
            rep.set_int32("ActionParam2", p2)
        el = GFFList()
        el._structs.append(_make_link(tmpl_ent_link, entry_idx, 0))
        rep.set_list("EntriesList", el)
        replies._structs.append(rep)
        return new_idx

    stat_names = ["Force", "Dextérité", "Constitution", "Intelligence", "Sagesse", "Charisme"]

    # Option 1 : Automatique (2 meilleures caractéristiques)
    r_auto = _make_reply(
        "Laissez la Force guider l'accord automatiquement (2 meilleures caractéristiques).",
        next_entry_idx,
        script_name="a_q_cryst_change",
        p1=0,
        p2=0,
    )

    # Option 2 : Choix manuel (6 primaires × 5 secondaires)
    r_prim_list: list[int] = []
    for s1 in range(6):
        r_sec_list: list[int] = []
        for s2 in range(6):
            if s2 == s1:
                continue
            r_s2 = _make_reply(
                f"{stat_names[s2]} (caractéristique secondaire)",
                next_entry_idx,
                script_name="a_q_cryst_change",
                p1=s1 + 1,
                p2=s2 + 1,
            )
            r_sec_list.append(r_s2)
        e_ask2 = _make_entry(
            f"Caractéristique principale : {stat_names[s1]}. Quelle caractéristique secondaire souhaitez-vous y associer ?",
            r_sec_list,
        )
        r_s1 = _make_reply(f"{stat_names[s1]} (caractéristique principale)", e_ask2)
        r_prim_list.append(r_s1)

    r_prim_list.append(r_auto)
    e_ask1 = _make_entry(
        "Très bien. Quelle caractéristique principale souhaitez-vous ancrer dans votre cristal ?",
        r_prim_list,
    )
    r_manual = _make_reply(
        "Je souhaite choisir moi-même les deux caractéristiques de mon cristal.",
        e_ask1,
    )

    # Remplacer le script immédiat sur EntryList[288] par le menu de choix
    e288.set_resref("Script", ResRef(""))
    new_rl = GFFList()
    new_rl._structs.append(_make_link(tmpl_rep_link, r_auto, 0))
    new_rl._structs.append(_make_link(tmpl_rep_link, r_manual, 1))
    e288.set_list("RepliesList", new_rl)

    gff.root.set_list("EntryList", entries)
    gff.root.set_list("ReplyList", replies)
    write_gff(gff, OVR_DIR / "kreia.dlg")
    return 1


def main() -> None:
    OVR_DIR.mkdir(parents=True, exist_ok=True)
    inst = Installation(GAME_PATH)
    print(f"=== Build Jalon 2 (items .uti + kreia.dlg) -> {OVR_DIR} ===")
    n_gear, n_arm = build_gear_utis(inst)
    print(f"[OK] Équipement (6 CSV) : {n_gear} fichiers .uti générés (dont {n_arm} armures cloisonnées level 0/1/2/6)")
    n_unde, n_over = build_armor_upgrades(inst)
    print(
        f"[OK] Améliorations d'armures (Améliorations.csv) : {n_unde} sous-couches (ulvl 1/2) "
        f"+ {n_over} sur-couches exclusives Intermédiaire (ulvl 6) + 2 legacy"
    )
    n_wup = build_weapon_upgrades(inst)
    print(f"[OK] Améliorations d'armes & sabres (Améliorations.csv + ulvl 1/2/3) : {n_wup} fichiers .uti générés")
    n_wslots, w_by_lvl, n_b2 = build_weapon_slots_partition(inst)
    print(
        f"[OK] Cloisonnement slots armes + B2-1a : {n_wslots} fichiers .uti "
        f"(reliques ulvl 0={w_by_lvl[0]}, ulvl 1={w_by_lvl[1]}, ulvl 2={w_by_lvl[2]}, ulvl 3={w_by_lvl[3]} ; "
        f"{n_b2} armes calibrées B2-1a)"
    )
    n_basew = build_craftable_base_weapons(inst)
    print(f"[OK] Armes de base craftables ajoutées : {n_basew} fichiers .uti (w_melee_ww_base, w_brifle_hr_base)")
    n_ml = build_mining_lasers_k2cp(inst)
    print(f"[OK] Lasers miniers & Péragus 2M/D : {n_ml} fichiers .uti (mininglaser, advancedminingla, heavymininglaser, guidonbeacon)")
    n_gam = build_gamorrean_1m_utis(inst)
    print(f"[OK] Variantes 1M Gamorréen II (toutes armes 2M/Doubles) : {n_gam} fichiers .uti (ov1m_*.uti)")
    n_gam_it, n_gam_dlg, n_gam_utp = build_gamorrean_adapter_item_and_dlg(inst)
    print(f"[OK] Adaptateur Gamorréen II : {n_gam_it} .uti (ov_gam_adapt.uti) + {n_gam_utp} .utp (ov_gam_term.utp) + {n_gam_dlg} .dlg (ov_gam_conv.dlg)")
    n_crys = build_personal_crystals(inst)
    print(f"[OK] Cristal personnel de l'Exilé (3 paliers × 30 paires) : {n_crys} fichiers .uti (ov_crys_*.uti)")
    n_dlg = build_kreia_crystal_dlg(inst)
    print(f"[OK] Dialogue Cristal personnel Kreia (auto / choix manuel 6×5) : {n_dlg} fichier .dlg (kreia.dlg)")
    n_pt = build_plasma_torch_vanilla()
    print(f"[OK] Torche à plasma vanilla (1d1 + 1d6 Feu) : {n_pt} fichier .uti (plasmatorch.uti)")
    total = n_gear + n_unde + n_over + 2 + n_gam + n_gam_it + n_wup + n_wslots + n_basew + n_crys + n_pt + n_ml
    print(f"=== Jalon 2 BUILD OK ({total} .uti + {n_dlg + n_gam_dlg} .dlg générés) ===")


if __name__ == "__main__":
    main()
