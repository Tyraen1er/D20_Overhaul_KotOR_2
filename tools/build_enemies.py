#!/usr/bin/env python3
"""KotOR 2 Overhaul — Jalon 4 : Générateur des ennemis (.utc + peaux ov_hide_*.uti).

Applique les décisions actées dans `equilibrage_ennemis.md` (22–23/11/2026) :
  - D1 : résistances partielles (25/30 %) ; 100 % réservé aux droïdes.
  - D2 : boucliers d'énergie équipés (`LEFT_ARM`) sur ~1 élite soldat/droïde sur 3 (CR >= 7/8, lootables).
  - D3 : statu quo sur les soins (aucun ajout de Guérison) + régén lente sur grosses bêtes apex.
  - D4 : aucune phase de boss scriptée supplémentaire (compatibilité TSLRCM intacte).
  - Familles :
      * Sith / Jedi obscurs : robes réelles (au lieu de nus) + peau Volonté (+2/+4/+6) & Rés. Force + Esquive Totale (CR >= 15).
      * Soldats / Mercenaires : armures légères/moyennes réelles + boucliers (~1/3 élites).
      * Mandaloriens : armure lourde (6/8+) + peau résistance Laser (Énergie) & Feu 25%/30% (Réflexes moyens conservés !).
      * Bêtes : peau RD Physique+Énergie 5/- + immunité Peur (+ régén sur apex).
      * Droïdes : statu quo sur les 82 peaux + déflecteur sur ~1/3 droïdes élites (CR >= 8).
      * Assassins Sith : peau +2 Réflexes + 15 % immunité physique.
"""

from __future__ import annotations

from pathlib import Path

from pykotor.common.misc import EquipmentSlot, InventoryItem, ResRef
from pykotor.extract.installation import Installation
from pykotor.resource.generics.utc import read_utc, write_utc
from pykotor.resource.generics.uti import UTIProperty, read_uti, write_uti
from pykotor.resource.type import ResourceType

ROOT = Path(__file__).resolve().parent.parent
GAME_PATH = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Knights of the Old Republic II")
OVR_DIR = ROOT / "mods" / "overhaul" / "Override"

FEAT_EVASION = 125
FEAT_ARMOR_LIGHT = 5
FEAT_ARMOR_MED = 6
FEAT_ARMOR_HEAVY = 4


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


def build_creature_hides(inst: Installation) -> int:
    """Crée les 8 peaux de créature familiales (`ov_hide_*.uti`) à partir de `g_i_crhide001`."""
    res = inst.resource("g_i_crhide001", ResourceType.UTI)
    assert res, "g_i_crhide001 introuvable"

    # prop 27=SavingThrowSpecific (sub 3=Will, 2=Reflex), prop 39=SpellResistance (cost_tbl 11: val=N),
    # prop 14=DamageImmunity (sub: 0=Bludg, 1=Pierc, 2=Slash, 8=Fire, 12=Energy; cost_tbl 5: 8=15%, 3=25%, 10=30%),
    # prop 17=DamageResistance (cost_tbl 7: 1=5/-), prop 24=ImmunityMisc (sub 1=Fear), prop 35=Regeneration (cost_tbl 2: val)
    hides: dict[str, list[UTIProperty]] = {
        "ov_hide_sith_l1": [
            make_prop(27, 3, 2, 2),   # Volonté +2
        ],
        "ov_hide_sith_l2": [
            make_prop(27, 3, 2, 4),   # Volonté +4
            make_prop(39, 0, 11, 4),  # Résistance à la Force (~18)
        ],
        "ov_hide_sith_l3": [
            make_prop(27, 3, 2, 6),   # Volonté +6
            make_prop(39, 0, 11, 7),  # Résistance à la Force (~24)
        ],
        "ov_hide_mando_m": [
            make_prop(14, 12, 5, 3),  # Immunité Énergie (Laser) 25%
            make_prop(14, 8, 5, 3),   # Immunité Feu 25%
        ],
        "ov_hide_mando_l": [
            make_prop(14, 12, 5, 10), # Immunité Énergie (Laser) 30%
            make_prop(14, 8, 5, 10),  # Immunité Feu 30%
        ],
        "ov_hide_beast_m": [
            make_prop(17, 0, 7, 1),   # RD Contondant 5/-
            make_prop(17, 1, 7, 1),   # RD Perforant 5/-
            make_prop(17, 2, 7, 1),   # RD Tranchant 5/-
            make_prop(24, 1, 0, 0),   # Immunité Peur
        ],
        "ov_hide_beast_l": [
            make_prop(17, 0, 7, 1),
            make_prop(17, 1, 7, 1),
            make_prop(17, 2, 7, 1),
            make_prop(17, 12, 7, 1),  # RD Énergie 5/- (apex)
            make_prop(24, 1, 0, 0),   # Immunité Peur
            make_prop(35, 0, 2, 2),   # Régénération +2
        ],
        "ov_hide_assn": [
            make_prop(27, 2, 2, 2),   # Réflexes +2
            make_prop(14, 0, 5, 8),   # Immunité Contondant 15%
            make_prop(14, 1, 5, 8),   # Immunité Perforant 15%
            make_prop(14, 2, 5, 8),   # Immunité Tranchant 15%
        ],
    }

    for rr, props in hides.items():
        u = read_uti(res.data)
        u.resref.set_data(rr)
        u.tag = rr
        u.properties = props
        write_uti(u, OVR_DIR / f"{rr}.uti")
    return len(hides)


def _classify_enemy(rr: str) -> str | None:
    """Classe un template UTC hostile (jamais compagnons p_* ni PNJ neutres)."""
    if rr.startswith("p_") or rr.startswith("n_dodonna") or rr.startswith("n_yoda") or "cut" in rr or "dead" in rr:
        return None
    if "mandalor" in rr:
        return "mando"
    if "sithass" in rr or "sith_ass" in rr:
        return "assassin"
    if any(k in rr for k in ("darkjedi", "dark_jed", "dark_app", "dark_mas", "sithappren", "sith_warrior", "darthsion", "darthtraya", "darthrevan")):
        return "sith"
    if any(k in rr for k in ("droid", "drd", "turret", "trt")):
        return "droid"
    if any(k in rr for k in ("boma", "zakkeg", "drexl", "tukata", "rancor", "stormbeast", "krayt", "kataarn", "hssiss", "kinrath", "wraid", "laigrek")):
        return "beast"
    if any(k in rr for k in ("sithtroop", "sithcmndo", "sith_soldier", "sith_elite", "merc", "vaklu", "vak_soldier", "roy_soldier", "ro_sold", "va_sold", "ro_officer", "zhug", "brakatan", "rakatan", "gammorean")):
        return "soldier"
    return None


def build_enemy_utcs(inst: Installation) -> dict[str, int]:
    stats = {"sith": 0, "soldier": 0, "mando": 0, "beast": 0, "droid": 0, "assassin": 0, "shields_added": 0}
    soldier_elite_idx = 0
    droid_elite_idx = 0

    seen: set[str] = set()
    for res in inst.core_resources():
        if res.restype() != ResourceType.UTC:
            continue
        rr = res.resname().lower()
        if rr in seen:
            continue
        seen.add(rr)
        fam = _classify_enemy(rr)
        if not fam:
            continue
        try:
            u = read_utc(res.data())
        except Exception:
            continue

        cr = float(u.challenge_rating)
        dirty = False

        if fam == "sith":
            # Habillage robe si nu
            if EquipmentSlot.ARMOR not in u.equipment:
                robe = "a_robe_18" if cr >= 14 else "a_robe_09"
                u.equipment[EquipmentSlot.ARMOR] = InventoryItem(ResRef(robe), droppable=False)
                dirty = True
            # Peau Volonté + Rés. Force selon palier
            if EquipmentSlot.HIDE not in u.equipment:
                hide = "ov_hide_sith_l3" if cr >= 14 else ("ov_hide_sith_l2" if cr >= 8 else "ov_hide_sith_l1")
                u.equipment[EquipmentSlot.HIDE] = InventoryItem(ResRef(hide), droppable=False)
                dirty = True
            # Esquive Totale dès CR >= 15 (acté §7.B)
            if cr >= 15 and FEAT_EVASION not in u.feats:
                u.feats.append(FEAT_EVASION)
                dirty = True

        elif fam == "soldier":
            # Habillage armure si nu et possède un don de port d'armure
            if EquipmentSlot.ARMOR not in u.equipment:
                if FEAT_ARMOR_MED in u.feats and cr >= 7:
                    arm = "a_medium_06" if cr >= 12 else "a_medium_01"
                    u.equipment[EquipmentSlot.ARMOR] = InventoryItem(ResRef(arm), droppable=False)
                    dirty = True
                elif FEAT_ARMOR_LIGHT in u.feats:
                    u.equipment[EquipmentSlot.ARMOR] = InventoryItem(ResRef("a_light_02"), droppable=False)
                    dirty = True
            # Bouclier énergie sur ~1 élite sur 3 (CR >= 7, lootable)
            if cr >= 7 and EquipmentSlot.LEFT_ARM not in u.equipment:
                soldier_elite_idx += 1
                if soldier_elite_idx % 3 == 0:
                    sh = "a_shield_04" if cr >= 12 else "a_shield_01"
                    u.equipment[EquipmentSlot.LEFT_ARM] = InventoryItem(ResRef(sh), droppable=True)
                    stats["shields_added"] += 1
                    dirty = True

        elif fam == "mando":
            # Armure lourde si nu + peau résistance Laser (Énergie) & Feu (Réflexes moyens conservés!)
            if EquipmentSlot.ARMOR not in u.equipment:
                u.equipment[EquipmentSlot.ARMOR] = InventoryItem(ResRef("a_heavy_07"), droppable=False)
                dirty = True
            if EquipmentSlot.HIDE not in u.equipment:
                hide = "ov_hide_mando_l" if cr >= 12 else "ov_hide_mando_m"
                u.equipment[EquipmentSlot.HIDE] = InventoryItem(ResRef(hide), droppable=False)
                dirty = True

        elif fam == "beast":
            # Peau RD + immunité Peur sur grosses bêtes (CR >= 8)
            if cr >= 8 and EquipmentSlot.HIDE not in u.equipment:
                hide = "ov_hide_beast_l" if cr >= 12 else "ov_hide_beast_m"
                u.equipment[EquipmentSlot.HIDE] = InventoryItem(ResRef(hide), droppable=False)
                dirty = True

        elif fam == "droid":
            # Statu quo peaux + déflecteur sur ~1/3 droïdes élites (CR >= 8)
            if cr >= 8 and EquipmentSlot.LEFT_ARM not in u.equipment:
                droid_elite_idx += 1
                if droid_elite_idx % 3 == 0:
                    sh = "d_shield_04" if cr >= 12 else "d_shield_02"
                    u.equipment[EquipmentSlot.LEFT_ARM] = InventoryItem(ResRef(sh), droppable=True)
                    stats["shields_added"] += 1
                    dirty = True

        elif fam == "assassin":
            if EquipmentSlot.HIDE not in u.equipment:
                u.equipment[EquipmentSlot.HIDE] = InventoryItem(ResRef("ov_hide_assn"), droppable=False)
                dirty = True

        if dirty:
            write_utc(u, OVR_DIR / f"{rr}.utc")
            stats[fam] += 1

    return stats


def main() -> None:
    OVR_DIR.mkdir(parents=True, exist_ok=True)
    inst = Installation(GAME_PATH)
    print(f"=== Build Jalon 4 (Ennemis .utc + peaux ov_hide_*.uti) -> {OVR_DIR} ===")
    n_hides = build_creature_hides(inst)
    print(f"[OK] {n_hides} peaux de créatures créées (ov_hide_*.uti)")
    stats = build_enemy_utcs(inst)
    total_utc = sum(v for k, v in stats.items() if k != "shields_added")
    print(f"[OK] {total_utc} templates .utc ennemis générés : "
          f"Sith={stats['sith']}, Soldats={stats['soldier']}, Mandaloriens={stats['mando']}, "
          f"Bêtes={stats['beast']}, Droïdes={stats['droid']}, Assassins={stats['assassin']} "
          f"(dont {stats['shields_added']} boucliers/déflecteurs ajoutés)")
    print("=== Jalon 4 BUILD OK ===")


if __name__ == "__main__":
    main()
