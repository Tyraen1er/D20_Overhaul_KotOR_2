#!/usr/bin/env python3
"""KotOR 2 Overhaul — Jalon 4 : Générateur des ennemis (.utc + peaux ov_hide_*.uti).

Applique les décisions actées dans `equilibrage_ennemis.md` (22–23/11/2026) :
  - D1 : résistances partielles (25/30 %) ; 100 % réservé aux droïdes.
  - D2 : boucliers d'énergie équipés (`LEFT_ARM`) sur ~1 élite soldat/droïde sur 3 et élites mandaloriens (lootables).
  - D3 : statu quo sur les soins (aucun ajout de Guérison) + régén lente HORS COMBAT sur grosses bêtes apex (gérée en runtime).
  - D4 : aucune phase de boss scriptée supplémentaire (compatibilité TSLRCM intacte).
  - Boss Set_4 / Set_5 : marqueur `MOD_BOSS_RD` sur tous les templates sûrs + détection runtime pour multi-modules (RD 2/5/8).
  - Sécurité TSLRCM : n'émet dans Override/ que les `.utc` de `chitin.key` et les `.utc` de `Modules/*.mod`
    uniques ou à signature identique (faction, dialogue, scripts, tag) — jamais les resrefs à scripts divergents entre modules !
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

from pykotor.common.misc import EquipmentSlot, InventoryItem, ResRef
from pykotor.extract.installation import Installation
from pykotor.resource.formats.erf import read_erf
from pykotor.resource.formats.gff import read_gff
from pykotor.resource.generics.utc import read_utc, write_utc
from pykotor.resource.generics.uti import UTIProperty, read_uti, write_uti
from pykotor.resource.type import ResourceType

ROOT = Path(__file__).resolve().parent.parent
GAME_PATH = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Knights of the Old Republic II")
OUT_DIR = ROOT / "mods" / "overhaul"
OVR_DIR = OUT_DIR / "Override"
FEAT_IDS_FILE = OUT_DIR / "feat_ids.json"

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
    """Crée les 8 peaux de créature familiales (`ov_hide_*.uti`) à partir de `g_i_crhide001`.
    IDs itempropdef.2da vérifiés :
      - prop 27 = SavingThrowSpecific (sub 2=Reflex, 3=Will ; cost_tbl 2)
      - prop 25 = ImprovedMagicResist (cost_tbl 11 : 4=18, 7=24) — complété en runtime par 15+Niv / 20+Niv
      - prop 14 = DamageImmunity (sub: 8=Fire, 12=Energy ; cost_tbl 5 : 3=25%, 10=30%)
      - prop 17 = DamageResist (cost_tbl 7 : 1=5/-)
      - prop 24 = Immunity (sub 5 = Fear)
    """
    res = inst.resource("g_i_crhide001", ResourceType.UTI)
    assert res, "g_i_crhide001 introuvable"

    hides: dict[str, list[UTIProperty]] = {
        "ov_hide_sith_l1": [
            make_prop(27, 3, 2, 2),   # Volonté +2
        ],
        "ov_hide_sith_l2": [
            make_prop(27, 3, 2, 4),   # Volonté +4
            make_prop(25, 0, 11, 4),  # ImprovedMagicResist (SR 18 base ; runtime 15+Niv)
        ],
        "ov_hide_sith_l3": [
            make_prop(27, 3, 2, 6),   # Volonté +6
            make_prop(25, 0, 11, 7),  # ImprovedMagicResist (SR 24 base ; runtime 20+Niv)
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
            make_prop(24, 5, 0, 0),   # Immunité Peur (subtype 5 = Fear)
        ],
        "ov_hide_beast_l": [
            make_prop(17, 0, 7, 1),
            make_prop(17, 1, 7, 1),
            make_prop(17, 2, 7, 1),
            make_prop(17, 12, 7, 1),  # RD Énergie 5/- (apex)
            make_prop(24, 5, 0, 0),   # Immunité Peur (subtype 5 = Fear ; régén hors combat gérée en runtime)
        ],
        "ov_hide_assn": [
            make_prop(27, 2, 2, 2),   # Réflexes +2 (esquive 20/25% gérée en runtime)
        ],
    }

    for rr, props in hides.items():
        u = read_uti(res.data)
        u.resref.set_data(rr)
        u.tag = rr
        u.properties = props
        write_uti(u, OVR_DIR / f"{rr}.uti")
    return len(hides)


EXCLUDED_UTC_SUBSTRINGS = (
    "cut", "dead", "holo", "corpse", "ghost", "body", "dummy", "fakpc",
    "wind", "mand_train", "command_", "zuka", "selkath",
)
EXCLUDED_UTC_EXACT = {
    "g_mandalore", "mand", "npc_bralor", "npc_berun", "npc_nallek", "npc_taepalae",
    "z2_atris", "z2_brianna", "n_azanti001", "g_gate_guard001", "vaklu_door",
}


def _is_excluded_utc(rr: str) -> bool:
    return (
        rr.startswith("p_")
        or rr.startswith("n_dodonna")
        or rr.startswith("n_yoda")
        or rr in EXCLUDED_UTC_EXACT
        or any(k in rr for k in EXCLUDED_UTC_SUBSTRINGS)
    )


def _classify_enemy(rr: str, tag: str = "") -> str | None:
    """Classe un template UTC hostile (jamais compagnons p_* ni PNJ neutres/cutscenes)."""
    if _is_excluded_utc(rr):
        return None
    s = f"{rr} {tag.lower()}"
    if "mandalor" in s or rr.startswith("mando"):
        return "mando"
    if "sithass" in s or "sith_ass" in s or "sithassassin" in s:
        return "assassin"
    if any(
        k in s
        for k in (
            "darkjedi", "dark_jed", "dark_app", "dark_mas", "sithappren",
            "sith_warrior", "sith_mar", "sith_lord", "sith_mas", "sithmaster",
            "darthsion", "darthtraya", "darthrevan", "darthnihil", "sith_acolyte",
            "sith_student", "sith_teacher", "twinsun",
        )
    ):
        return "sith"
    if any(k in rr for k in ("droid", "drd", "turret", "trt", "hk50", "hk51")):
        return "droid"
    if any(
        k in s
        for k in (
            "boma", "zakkeg", "drexl", "tukata", "rancor", "stormbeast",
            "krayt", "kataarn", "hssiss", "kinrath", "wraid", "laigrek",
            "cannok", "maalraas", "kath", "shyrack",
        )
    ):
        return "beast"
    if any(
        k in rr
        for k in (
            "sithtroop", "sithcmndo", "sithcomm", "sith_soldier", "sith_elite", "sith_troop",
            "merc", "vaklu", "vak_soldier", "roy_soldier", "ro_sold", "va_sold",
            "ro_officer", "va_officer", "zhug", "brakatan", "rakatan", "gammorean",
            "exch", "redeclip", "bounty", "ubh", "thug", "slaver", "serroco",
        )
    ):
        return "soldier"
    return None


def _collect_safe_module_utcs(core_resrefs: set[str]) -> list[tuple[str, bytes, int, str]]:
    """Collecte les .utc de `Modules/*.mod` sûrs à placer dans Override/ :
      - absents de chitin.key (ou déjà gérés)
      - présents dans un seul `.mod` OU avec une signature identique (faction, dialogue, scripts, tag)
        dans tous les `.mod` où ils apparaissent (évite toute régression de quête TSLRCM)."""
    grouped: dict[str, list[tuple[bytes, int, int, str, tuple]]] = defaultdict(list)
    mod_dir = GAME_PATH / "Modules"
    if not mod_dir.exists():
        return []
    for mod_path in sorted(mod_dir.glob("*.mod")):
        try:
            erf = read_erf(mod_path)
        except Exception:
            continue
        for res in erf:
            if res.restype != ResourceType.UTC:
                continue
            rr = str(res.resref).lower()
            if rr in core_resrefs or rr.startswith("p_"):
                continue
            try:
                g = read_gff(res.data)
                ms = g.root.get_uint8("MultiplierSet") if g.root.exists("MultiplierSet") else 0
                fac = g.root.get_uint32("FactionID") if g.root.exists("FactionID") else 0
                tag = g.root.get_string("Tag") if g.root.exists("Tag") else ""
                sig = (
                    fac,
                    str(g.root.get_resref("Conversation")).lower() if g.root.exists("Conversation") else "",
                    str(g.root.get_resref("ScriptSpawn")).lower() if g.root.exists("ScriptSpawn") else "",
                    str(g.root.get_resref("ScriptDeath")).lower() if g.root.exists("ScriptDeath") else "",
                    str(g.root.get_resref("ScriptUserDefine")).lower() if g.root.exists("ScriptUserDefine") else "",
                    str(g.root.get_resref("ScriptHeartbeat")).lower() if g.root.exists("ScriptHeartbeat") else "",
                    tag.lower(),
                )
            except Exception:
                continue
            grouped[rr].append((res.data, ms, fac, tag, sig))

    safe: list[tuple[str, bytes, int, str]] = []
    for rr, entries in sorted(grouped.items()):
        # Si présent dans plusieurs modules avec des signatures différentes -> NE PAS toucher en Override
        if len(entries) > 1 and len({e[4] for e in entries}) > 1:
            continue
        data, ms, fac, tag, _ = entries[0]
        # Ne jamais toucher les membres du groupe (faction 2)
        if fac == 2:
            continue
        safe.append((rr, data, ms, tag))
    return safe


def build_enemy_utcs(inst: Installation) -> dict[str, int]:
    fids: dict[str, int] = json.loads(FEAT_IDS_FILE.read_text(encoding="utf-8")) if FEAT_IDS_FILE.exists() else {}
    feat_boss_rd = fids.get("MOD_BOSS_RD")

    stats = {
        "sith": 0, "soldier": 0, "mando": 0, "beast": 0, "droid": 0, "assassin": 0,
        "boss_only": 0, "boss_rd_marked": 0, "shields_added": 0,
    }
    soldier_elite_idx = 0
    droid_elite_idx = 0
    mando_elite_idx = 0

    candidates: list[tuple[str, bytes, int, str]] = []
    core_seen: set[str] = set()

    for res in inst.core_resources():
        if res.restype() != ResourceType.UTC:
            continue
        rr = res.resname().lower()
        if rr in core_seen:
            continue
        core_seen.add(rr)
        data = res.data()
        try:
            g = read_gff(data)
            ms = g.root.get_uint8("MultiplierSet") if g.root.exists("MultiplierSet") else 0
            tag = g.root.get_string("Tag") if g.root.exists("Tag") else ""
        except Exception:
            continue
        candidates.append((rr, data, ms, tag))

    candidates.extend(_collect_safe_module_utcs(core_seen))

    for rr, data, mult_set, tag in candidates:
        if _is_excluded_utc(rr):
            continue
        fam = _classify_enemy(rr, tag)
        is_boss = mult_set in (4, 5)
        if not fam and not is_boss:
            continue
        try:
            u = read_utc(data)
        except Exception:
            continue

        cr = float(u.challenge_rating)
        dirty = False

        # Marqueur Boss RD (Set_4 / Set_5 -> RD passive 2/5/8 appliquée en runtime)
        if is_boss and feat_boss_rd is not None and feat_boss_rd not in u.feats:
            u.feats.append(feat_boss_rd)
            stats["boss_rd_marked"] += 1
            dirty = True

        if fam == "sith":
            if EquipmentSlot.ARMOR not in u.equipment:
                robe = "a_robe_18" if cr >= 14 else "a_robe_09"
                u.equipment[EquipmentSlot.ARMOR] = InventoryItem(ResRef(robe), droppable=False)
                dirty = True
            if EquipmentSlot.HIDE not in u.equipment:
                hide = "ov_hide_sith_l3" if cr >= 14 else ("ov_hide_sith_l2" if cr >= 8 else "ov_hide_sith_l1")
                u.equipment[EquipmentSlot.HIDE] = InventoryItem(ResRef(hide), droppable=False)
                dirty = True
            if cr >= 15 and FEAT_EVASION not in u.feats:
                u.feats.append(FEAT_EVASION)
                dirty = True

        elif fam == "soldier":
            if EquipmentSlot.ARMOR not in u.equipment:
                if FEAT_ARMOR_MED in u.feats and cr >= 7:
                    arm = "a_medium_06" if cr >= 12 else "a_medium_01"
                    u.equipment[EquipmentSlot.ARMOR] = InventoryItem(ResRef(arm), droppable=False)
                    dirty = True
                elif FEAT_ARMOR_LIGHT in u.feats:
                    u.equipment[EquipmentSlot.ARMOR] = InventoryItem(ResRef("a_light_02"), droppable=False)
                    dirty = True
            if cr >= 7 and EquipmentSlot.LEFT_ARM not in u.equipment:
                soldier_elite_idx += 1
                if soldier_elite_idx % 3 == 0:
                    sh = "a_shield_04" if cr >= 12 else "a_shield_01"
                    u.equipment[EquipmentSlot.LEFT_ARM] = InventoryItem(ResRef(sh), droppable=True)
                    stats["shields_added"] += 1
                    dirty = True

        elif fam == "mando":
            if EquipmentSlot.ARMOR not in u.equipment:
                u.equipment[EquipmentSlot.ARMOR] = InventoryItem(ResRef("a_heavy_07"), droppable=False)
                dirty = True
            if EquipmentSlot.HIDE not in u.equipment:
                hide = "ov_hide_mando_l" if cr >= 12 else "ov_hide_mando_m"
                u.equipment[EquipmentSlot.HIDE] = InventoryItem(ResRef(hide), droppable=False)
                dirty = True
            # Boucliers mandaloriens sur les élites (~1 sur 2, CR >= 8, lootables)
            if cr >= 8 and EquipmentSlot.LEFT_ARM not in u.equipment:
                mando_elite_idx += 1
                if mando_elite_idx % 2 == 0:
                    sh = "a_shield_05" if cr >= 13 else "a_shield_02"
                    u.equipment[EquipmentSlot.LEFT_ARM] = InventoryItem(ResRef(sh), droppable=True)
                    stats["shields_added"] += 1
                    dirty = True

        elif fam == "beast":
            if cr >= 8 and EquipmentSlot.HIDE not in u.equipment:
                hide = "ov_hide_beast_l" if cr >= 12 else "ov_hide_beast_m"
                u.equipment[EquipmentSlot.HIDE] = InventoryItem(ResRef(hide), droppable=False)
                dirty = True

        elif fam == "droid":
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
            if fam:
                stats[fam] += 1
            else:
                stats["boss_only"] += 1

    return stats


def main() -> None:
    OVR_DIR.mkdir(parents=True, exist_ok=True)
    # Nettoyer les anciens .utc générés avant reconstruction (évite tout fichier fantôme)
    for old_utc in OVR_DIR.glob("*.utc"):
        old_utc.unlink()
    inst = Installation(GAME_PATH)
    print(f"=== Build Jalon 4 (Ennemis .utc + peaux ov_hide_*.uti) -> {OVR_DIR} ===")
    n_hides = build_creature_hides(inst)
    print(f"[OK] {n_hides} peaux de créatures créées (ov_hide_*.uti)")
    stats = build_enemy_utcs(inst)
    total_utc = sum(v for k, v in stats.items() if k not in ("shields_added", "boss_rd_marked"))
    print(
        f"[OK] {total_utc} templates .utc ennemis générés : "
        f"Sith={stats['sith']}, Soldats={stats['soldier']}, Mandaloriens={stats['mando']}, "
        f"Bêtes={stats['beast']}, Droïdes={stats['droid']}, Assassins={stats['assassin']}, "
        f"BossAutres={stats['boss_only']} "
        f"(dont {stats['boss_rd_marked']} boss marqués MOD_BOSS_RD, {stats['shields_added']} boucliers ajoutés)"
    )
    print("=== Jalon 4 BUILD OK ===")


if __name__ == "__main__":
    main()
