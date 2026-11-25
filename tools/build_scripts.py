#!/usr/bin/env python3
"""KotOR 2 Overhaul — Jalon 3 : Générateur & Compilateur des scripts NWScript (.nss -> .ncs).

Respecte strictement les règles moteur validées (README.md §2–§3) :
  - Bug #7 : NE JAMAIS recompiler `k_ai_master.ncs` — tous les hooks passent par les
    petits wrappers `k_hen_*` / `k_def_*` qui appellent ensuite le vrai `k_ai_master` vanilla.
  - T4 : tous les bonus de CA custom sont additionnés dans un seul `nTotalAC` avant
    un unique `EffectACIncrease(nTotalAC, AC_DODGE_BONUS)`.
  - T-excl : mutualité des 6 Spé Carac assurée par garde-fou `LocalNumber(oTarget, 22)`.
  - Prologue safety : `GetIsPlayerMadeCharacter` vérifié avant tout effet sur le PJ.
  - LocalNumber strictement dans la plage 12–28 (JAMAIS 29).
  - Garde-fou 1×/6s sur le groupe (`LocalNumber 16`) pour éliminer le bug heartbeat ×N.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

from pykotor.resource.formats.twoda import read_2da

ROOT = Path(__file__).resolve().parent.parent
REF_SCRIPTS = ROOT / "_reference" / "scripts"
NWNNSSCOMP = ROOT / "_reference" / "autres_mods" / "Content Pack-57-1-67-1616632489" / "tslpatchdata" / "nwnnsscomp.exe"
OUT_DIR = ROOT / "mods" / "overhaul"
SRC_DIR = OUT_DIR / "src"
STAGE_DIR = OUT_DIR / "_compile_stage"
OVR_DIR = OUT_DIR / "Override"
FEAT_IDS_FILE = OUT_DIR / "feat_ids.json"
SPELL_IDS_FILE = OUT_DIR / "spell_ids.json"
MIRROR_MAP_FILE = OUT_DIR / "baseitem_1m_map.json"


def _prepare_stage() -> None:
    """Prépare un répertoire de compilation contenant nwnnsscomp.exe, nwscript.nss et tous les includes."""
    STAGE_DIR.mkdir(parents=True, exist_ok=True)
    if not (STAGE_DIR / "nwnnsscomp.exe").exists():
        shutil.copy2(NWNNSSCOMP, STAGE_DIR / "nwnnsscomp.exe")
    for inc in REF_SCRIPTS.glob("*.nss"):
        dst = STAGE_DIR / inc.name
        if not dst.exists():
            shutil.copy2(inc, dst)
    for src in SRC_DIR.glob("*.nss"):
        shutil.copy2(src, STAGE_DIR / src.name)


def compile_script(name: str, code: str) -> int:
    src_path = SRC_DIR / f"{name}.nss"
    stage_src = STAGE_DIR / f"{name}.nss"
    out_path = OVR_DIR / f"{name}.ncs"
    src_path.write_text(code, encoding="latin1")
    _prepare_stage()
    stage_src.write_text(code, encoding="latin1")
    if out_path.exists():
        out_path.unlink()
    res = subprocess.run(
        [str(STAGE_DIR / "nwnnsscomp.exe"), "-c", f"{name}.nss", "-o", str(out_path)],
        cwd=str(STAGE_DIR),
        capture_output=True,
        text=True,
    )
    out_txt = (res.stdout or "") + "\n" + (res.stderr or "")
    if res.returncode != 0 or "Error:" in out_txt or "aborted" in out_txt.lower() or not out_path.exists():
        raise RuntimeError(f"nwnnsscomp failed on {name}.nss:\n{out_txt}")
    size = out_path.stat().st_size
    print(f"[OK] {name}.ncs ({size} octets, compilé via nwnnsscomp.exe C++)")
    return size


def _build_dynamic_baseitem_helpers() -> tuple[str, str, str, str, str, str]:
    """Construit dynamiquement depuis `baseitems.2da` et `baseitem_1m_map.json` :
      1. `Ov_GetArmorDexCap`
      2. `Ov_GetWeaponFamily`
      3. `Ov_IsHeavy2HBaseItem`
      4. `Ov_IsMirror1MBaseItem`
      5. `Ov_GetWeaponBaseThreat`
      6. `Ov_IsSonicBaseItem`"""
    bi_path = OVR_DIR / "baseitems.2da"
    bi = read_2da(bi_path) if bi_path.exists() else None
    mirror_map: dict[str, int] = (
        json.loads(MIRROR_MAP_FILE.read_text(encoding="utf-8"))
        if MIRROR_MAP_FILE.exists()
        else {}
    )

    # 1. Plafonds DEX exacts par baseitem d'armure/bure restrictive
    dex_cap_lines: list[str] = []
    for bi_idx in (38, 39, 40, 41, 42, 43, 98, 99, 102):
        if bi is not None and bi_idx < len(bi):
            row = bi.get_row(bi_idx)
            val = row.get_string("dexbonus").strip()
            lbl = row.get_string("label").strip()
            if val.isdigit():
                dex_cap_lines.append(f"    if (nBase == {bi_idx}) return {int(val)}; // {lbl}")
    dex_cap_body = "\n".join(dex_cap_lines)

    # 2. Familles d'armes (1..8)
    fam_ids: dict[int, list[int]] = {
        1: [-1, 0, 1, 78, 93],         # Impact (mains nues, bâton, matraque, gaffi, pique)
        2: [2, 4, 6, 79, 80],          # Traditionnelle (épées, hache gamorréenne, lame wookie)
        3: [3, 5, 7],                  # Résonance (vibrolame, vibro-épée, vibro-double)
        4: [8, 9, 10],                 # Laser (sabres)
        5: [12, 20, 23],               # Tir d'Assaut (pistolet, carabine, répétition)
        6: [13, 19, 24, 77],           # Tir Pénétrant (lourd, arbalète, lourd répét., fusil)
        7: [15, 17, 18, 22],           # Tir Tactique (ions, soniques)
        8: [14, 16, 21],               # Tir Assassin (poche, disrupteurs)
    }
    mirror_to_fam = {
        "Plasma_Torch": 1,
        "Quarter_Staff": 1,
        "Force_Pike": 1,
        "Double_Bladed_Sword": 2,
        "Wookie_Warblade": 2,
        "Gammorean_Battleaxe": 2,
        "Vibro_Sword": 3,
        "Vibro_Double_Blade": 3,
        "Double_Bladed_Lightsaber": 4,
        "Mining_Laser": 5,
        "Blaster_Carbine": 5,
        "Repeating_Blaster": 5,
        "Adv_Mining_Laser": 6,
        "Blaster_Rifle": 6,
        "Heavy_Repeating_Blaster": 6,
        "Bowcaster": 6,
        "Sonic_Rifle": 7,
        "Ion_Rifle": 7,
        "Disrupter_Rifle": 8,
    }
    for lbl, bi_idx in sorted(mirror_map.items(), key=lambda kv: kv[1]):
        fam = mirror_to_fam.get(lbl)
        if fam is not None and bi_idx not in fam_ids[fam]:
            fam_ids[fam].append(bi_idx)

    fam_lines: list[str] = []
    for fam in range(1, 9):
        cond = " || ".join(f"nBI == {i}" for i in fam_ids[fam])
        fam_lines.append(f"    if ({cond}) return {fam};")
    fam_body = "\n".join(fam_lines)

    # 3. Armes 2M non-doubles (Maniement d'Arme Lourde)
    heavy_2h_ids = [3, 80, 93, 18, 19, 20, 21, 22, 77]
    if "Adv_Mining_Laser" in mirror_map:
        heavy_2h_ids.append(mirror_map["Adv_Mining_Laser"])
    heavy_2h_cond = " || ".join(f"nBI == {i}" for i in heavy_2h_ids)

    # 4. Variantes miroirs 1M Gamoréen II (ne doivent pas déclencher les branches 2M/Double)
    non_mirror_keys = {"Mining_Laser", "Adv_Mining_Laser", "Plasma_Torch"}
    mirror_1m_ids = [idx for lbl, idx in sorted(mirror_map.items(), key=lambda kv: kv[1]) if lbl not in non_mirror_keys]
    mirror_1m_cond = " || ".join(f"nBI == {i}" for i in mirror_1m_ids) if mirror_1m_ids else "FALSE"

    # 5. Plages de menace critiques exactes lues depuis baseitems.2da (+ Mains nues -1 -> 2 = 19-20)
    threat_lines = ["    if (nBI == -1) return 2; // Unarmed 19-20 x2"]
    all_weap_ids = sorted({i for ids in fam_ids.values() for i in ids if i >= 0})
    if bi is not None:
        for wid in all_weap_ids:
            if wid < len(bi):
                thr = bi.get_row(wid).get_string("critthreat").strip()
                if thr.isdigit() and int(thr) > 1:
                    threat_lines.append(f"    if (nBI == {wid}) return {int(thr)};")
    threat_body = "\n".join(threat_lines)

    # 6. Armes soniques (baseitems 17, 22 + Sonic_Rifle_1M)
    sonic_ids = [17, 22]
    if "Sonic_Rifle" in mirror_map:
        sonic_ids.append(mirror_map["Sonic_Rifle"])
    sonic_cond = " || ".join(f"nBI == {i}" for i in sonic_ids)

    return dex_cap_body, fam_body, heavy_2h_cond, mirror_1m_cond, threat_body, sonic_cond


def build_ov_inc_core(fids: dict[str, int], sids: dict[str, int]) -> str:
    dex_cap_body, fam_body, heavy_2h_cond, mirror_1m_cond, threat_body, sonic_cond = _build_dynamic_baseitem_helpers()
    code = f'''//:: ov_inc_core - KotOR 2 Overhaul Core Library (Passes 1, 2 & 3)

int OV_GAM_1 = {fids["MOD_GAMORREAN_1"]};
int OV_GAM_2 = {fids["MOD_GAMORREAN_2"]};
int OV_GAM_3 = {fids["MOD_GAMORREAN_3"]};
int OV_ECH_1 = {fids["MOD_ECHANI_1"]};
int OV_ECH_2 = {fids["MOD_ECHANI_2"]};
int OV_ECH_3 = {fids["MOD_ECHANI_3"]};
int OV_KRA_1 = {fids["MOD_KRAITH_CON_1"]};
int OV_KRA_2 = {fids["MOD_KRAITH_CON_2"]};
int OV_KRA_3 = {fids["MOD_KRAITH_CON_3"]};
int OV_GAN_1 = {fids["MOD_GAND_1"]};
int OV_GAN_2 = {fids["MOD_GAND_2"]};
int OV_GAN_3 = {fids["MOD_GAND_3"]};
int OV_MAT_1 = {fids["MOD_MATUKAI_SAG_1"]};
int OV_MAT_2 = {fids["MOD_MATUKAI_SAG_2"]};
int OV_MAT_3 = {fids["MOD_MATUKAI_SAG_3"]};
int OV_NOM_1 = {fids["MOD_NOMI_1"]};
int OV_NOM_2 = {fids["MOD_NOMI_2"]};
int OV_NOM_3 = {fids["MOD_NOMI_3"]};

int OV_ARM_L1 = {fids["MOD_ARMOR_LIGHT_1"]};
int OV_ARM_L2 = {fids["MOD_ARMOR_LIGHT_2"]};
int OV_ARM_L3 = {fids["MOD_ARMOR_LIGHT_3"]};
int OV_ARM_M1 = {fids["MOD_ARMOR_MED_1"]};
int OV_ARM_M2 = {fids["MOD_ARMOR_MED_2"]};
int OV_ARM_M3 = {fids["MOD_ARMOR_MED_3"]};
int OV_ARM_H1 = {fids["MOD_ARMOR_HEAVY_1"]};
int OV_ARM_H2 = {fids["MOD_ARMOR_HEAVY_2"]};
int OV_ARM_H3 = {fids["MOD_ARMOR_HEAVY_3"]};

int OV_AMB_1 = {fids["MOD_AMBIDEXTRY_1"]};
int OV_AMB_2 = {fids["MOD_AMBIDEXTRY_2"]};
int OV_AMB_3 = {fids["MOD_AMBIDEXTRY_3"]};
int OV_HVY_1 = {fids["MOD_HEAVY_WEAPON_1"]};
int OV_HVY_2 = {fids["MOD_HEAVY_WEAPON_2"]};
int OV_HVY_3 = {fids["MOD_HEAVY_WEAPON_3"]};
int OV_DUE_1 = {fids["MOD_DUEL_1"]};
int OV_DUE_2 = {fids["MOD_DUEL_2"]};
int OV_DUE_3 = {fids["MOD_DUEL_3"]};
int OV_DBL_1 = {fids["MOD_DOUBLE_WEAPON_1"]};
int OV_DBL_2 = {fids["MOD_DOUBLE_WEAPON_2"]};
int OV_DBL_3 = {fids["MOD_DOUBLE_WEAPON_3"]};

int OV_SP_BLUNT_1 = {fids["MOD_SPEC_BLUNT_1"]};
int OV_SP_BLUNT_2 = {fids["MOD_SPEC_BLUNT_2"]};
int OV_SP_BLUNT_3 = {fids["MOD_SPEC_BLUNT_3"]};
int OV_SP_PRIM_1  = {fids["MOD_SPEC_PRIM_1"]};
int OV_SP_PRIM_2  = {fids["MOD_SPEC_PRIM_2"]};
int OV_SP_PRIM_3  = {fids["MOD_SPEC_PRIM_3"]};
int OV_SP_VIBRO_1 = {fids["MOD_SPEC_VIBRO_1"]};
int OV_SP_VIBRO_2 = {fids["MOD_SPEC_VIBRO_2"]};
int OV_SP_VIBRO_3 = {fids["MOD_SPEC_VIBRO_3"]};
int OV_SP_LASER_1 = {fids["MOD_SPEC_LASER_1"]};
int OV_SP_LASER_2 = {fids["MOD_SPEC_LASER_2"]};
int OV_SP_LASER_3 = {fids["MOD_SPEC_LASER_3"]};
int OV_SP_ASSAULT_1 = {fids["MOD_SPEC_ASSAULT_1"]};
int OV_SP_ASSAULT_2 = {fids["MOD_SPEC_ASSAULT_2"]};
int OV_SP_ASSAULT_3 = {fids["MOD_SPEC_ASSAULT_3"]};
int OV_SP_HEAVY_1   = {fids["MOD_SPEC_HEAVY_1"]};
int OV_SP_HEAVY_2   = {fids["MOD_SPEC_HEAVY_2"]};
int OV_SP_HEAVY_3   = {fids["MOD_SPEC_HEAVY_3"]};
int OV_SP_TAC_1     = {fids["MOD_SPEC_TAC_1"]};
int OV_SP_TAC_2     = {fids["MOD_SPEC_TAC_2"]};
int OV_SP_TAC_3     = {fids["MOD_SPEC_TAC_3"]};
int OV_SP_ASSASSIN_1 = {fids["MOD_SPEC_ASSASSIN_1"]};
int OV_SP_ASSASSIN_2 = {fids["MOD_SPEC_ASSASSIN_2"]};
int OV_SP_ASSASSIN_3 = {fids["MOD_SPEC_ASSASSIN_3"]};

int OV_UNB_1 = {fids["MOD_UNBOUND_FORCE_1"]};
int OV_UNB_2 = {fids["MOD_UNBOUND_FORCE_2"]};
int OV_UNB_3 = {fids["MOD_UNBOUND_FORCE_3"]};

int OV_PREST_MAGE   = {fids["MOD_PRESTIGE_MAGE"]};
int OV_PREST_HYB    = {fids["MOD_PRESTIGE_HYBRID"]};
int OV_PREST_MART   = {fids["MOD_PRESTIGE_MARTIAL"]};
int OV_BOSS_RD      = {fids["MOD_BOSS_RD"]};
int OV_BATTLE_PRECOG = {fids["MOD_BATTLE_PRECOG"]};

int OV_SP_DEATH_FEAST = {sids["FORCE_POWER_DEATH_FEAST"]};
int OV_SP_SCAR_1      = {sids["FORCE_POWER_FORCE_SCAR_I"]};
int OV_SP_SCAR_2      = {sids["FORCE_POWER_FORCE_SCAR_II"]};
int OV_SP_SCAR_3      = {sids["FORCE_POWER_FORCE_SCAR_III"]};

// 0=sans/robe, 1=legere, 2=moyenne, 3=lourde
int Ov_GetArmorTier(object oTarget)
{{
    object oArmor = GetItemInSlot(INVENTORY_SLOT_BODY, oTarget);
    if (!GetIsObjectValid(oArmor)) return 0;
    int nBase = GetBaseItemType(oArmor);
    if (nBase == 38 || nBase == 39 || nBase == 98 || nBase == 102) return 1;
    if (nBase == 40 || nBase == 41) return 2;
    if (nBase == 42 || nBase == 43) return 3;
    return 0;
}}

int Ov_GetArmorDexCap(object oTarget)
{{
    object oArmor = GetItemInSlot(INVENTORY_SLOT_BODY, oTarget);
    if (!GetIsObjectValid(oArmor)) return -1;
    int nBase = GetBaseItemType(oArmor);
{dex_cap_body}
    return -1;
}}

int Ov_GetWeaponFamily(int nBI)
{{
{fam_body}
    return 0;
}}

int Ov_IsRangedBaseItem(int nBI)
{{
    int nFam = Ov_GetWeaponFamily(nBI);
    return (nFam >= 5 && nFam <= 8);
}}

int Ov_IsDoubleBaseItem(int nBI)
{{
    return (nBI == 0 || nBI == 6 || nBI == 7 || nBI == 9 || nBI == 23 || nBI == 24 || nBI == 78 || nBI == 79);
}}

int Ov_IsHeavy2HBaseItem(int nBI)
{{
    return ({heavy_2h_cond});
}}

int Ov_IsMirror1MBaseItem(int nBI)
{{
    return ({mirror_1m_cond});
}}

int Ov_IsSonicBaseItem(int nBI)
{{
    return ({sonic_cond});
}}

int Ov_GetWeaponBaseThreat(int nBI)
{{
{threat_body}
    return 1;
}}

int Ov_IsPartyMember(object oTarget)
{{
    if (!GetIsObjectValid(oTarget)) return FALSE;
    if (oTarget == GetFirstPC()) return TRUE;
    if (oTarget == GetPartyMemberByIndex(0) || oTarget == GetPartyMemberByIndex(1) || oTarget == GetPartyMemberByIndex(2)) return TRUE;
    return FALSE;
}}

// Verifie si le Cristal personnel (prop 62) est effectivement monte dans un sabre tenu en main
int Ov_HasPersonalCrystal(object oPC)
{{
    if (!GetIsObjectValid(oPC) || oPC != GetFirstPC()) return FALSE;
    object oR = GetItemInSlot(INVENTORY_SLOT_RIGHTWEAPON, oPC);
    if (GetIsObjectValid(oR) && GetItemHasItemProperty(oR, 62)) return TRUE;
    object oL = GetItemInSlot(INVENTORY_SLOT_LEFTWEAPON, oPC);
    if (GetIsObjectValid(oL) && GetItemHasItemProperty(oL, 62)) return TRUE;
    return FALSE;
}}

// Detection Boss Set_4 / Set_5 (marqueur MOD_BOSS_RD ou tag des boss multi-modules)
int Ov_IsBoss(object oTarget)
{{
    if (!GetIsObjectValid(oTarget) || Ov_IsPartyMember(oTarget)) return FALSE;
    if (GetHasFeat(OV_BOSS_RD, oTarget)) return TRUE;
    string sTag = GetStringLowerCase(GetTag(oTarget));
    if (sTag == "darthsion" || sTag == "darthnihilus" || sTag == "nihilus" || sTag == "atris" || sTag == "kreia") return TRUE;
    if (sTag == "vaklu" || sTag == "kavar" || sTag == "vrook" || sTag == "npc_vrook" || sTag == "zezkaiel") return TRUE;
    if (sTag == "jedimaster1" || sTag == "jedimaster2" || sTag == "jedimaster3" || sTag == "jedimaster4") return TRUE;
    if (sTag == "npc_azkul" || sTag == "hk50" || sTag == "hk501" || sTag == "hk502" || sTag == "hk503" || sTag == "hk51_1") return TRUE;
    if (sTag == "sister" || sTag == "tobin" || sTag == "talia" || sTag == "kadron" || sTag == "xarga") return TRUE;
    if (sTag == "npc_dopak" || sTag == "npc_gerevick" || sTag == "npc_saedhe" || sTag == "npc_zherron") return TRUE;
    if (sTag == "overseer" || sTag == "thugboss" || sTag == "ritual_leader" || sTag == "recapt" || sTag == "samhan") return TRUE;
    if (sTag == "va_officer" || sTag == "g_darkjedi03" || sTag == "g_darkjedi04" || sTag == "g_sithcomm02") return TRUE;
    if (sTag == "fuel_sith" || sTag == "g0t0droid" || sTag == "tdroid" || sTag == "boma_young") return TRUE;
    return FALSE;
}}

// Garde-fou de mutualite des 6 Spe Carac (LocalNumber 22 : 1=GAM, 2=ECH, 3=KRA, 4=GAN, 5=MAT, 6=NOM)
int Ov_GetActiveCaracTree(object oTarget)
{{
    int nTree = GetLocalNumber(oTarget, 22);
    if (nTree > 0) return nTree;
    if (GetHasFeat(OV_GAM_1, oTarget) || GetHasFeat(OV_GAM_2, oTarget) || GetHasFeat(OV_GAM_3, oTarget)) nTree = 1;
    else if (GetHasFeat(OV_ECH_1, oTarget) || GetHasFeat(OV_ECH_2, oTarget) || GetHasFeat(OV_ECH_3, oTarget)) nTree = 2;
    else if (GetHasFeat(OV_KRA_1, oTarget) || GetHasFeat(OV_KRA_2, oTarget) || GetHasFeat(OV_KRA_3, oTarget)) nTree = 3;
    else if (GetHasFeat(OV_GAN_1, oTarget) || GetHasFeat(OV_GAN_2, oTarget) || GetHasFeat(OV_GAN_3, oTarget)) nTree = 4;
    else if (GetHasFeat(OV_MAT_1, oTarget) || GetHasFeat(OV_MAT_2, oTarget) || GetHasFeat(OV_MAT_3, oTarget)) nTree = 5;
    else if (GetHasFeat(OV_NOM_1, oTarget) || GetHasFeat(OV_NOM_2, oTarget) || GetHasFeat(OV_NOM_3, oTarget)) nTree = 6;
    if (nTree > 0) SetLocalNumber(oTarget, 22, nTree);
    return nTree;
}}

// Matukai II : punition mod. SAG en degats directs quand la cible reussit une sauvegarde
void Ov_CheckMatukaiPunish(object oDefender, object oAttacker)
{{
    if (!GetIsObjectValid(oDefender) || !GetIsObjectValid(oAttacker)) return;
    if (oDefender == oAttacker || GetIsDead(oDefender) || GetIsDead(oAttacker)) return;
    if (!GetIsEnemy(oDefender, oAttacker)) return;
    if (Ov_GetActiveCaracTree(oDefender) == 5 && GetHasFeat(OV_MAT_2, oDefender))
    {{
        int nWis = GetAbilityModifier(ABILITY_WISDOM, oDefender);
        if (nWis > 0)
        {{
            AssignCommand(oDefender, ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectDamage(nWis, DAMAGE_TYPE_BLUDGEONING), oAttacker));
        }}
    }}
}}

void Ov_RemoveOldPassives(object oTarget)
{{
    effect e = GetFirstEffect(oTarget);
    while (GetIsEffectValid(e))
    {{
        if (GetEffectSubType(e) == SUBTYPE_EXTRAORDINARY && GetEffectDurationType(e) == DURATION_TYPE_PERMANENT)
        {{
            RemoveEffect(oTarget, e);
        }}
        e = GetNextEffect(oTarget);
    }}
}}

int Ov_ConsumeStealthAmbush(object oTarget)
{{
    int bFound = FALSE;
    effect e = GetFirstEffect(oTarget);
    while (GetIsEffectValid(e))
    {{
        if (GetEffectSubType(e) == SUBTYPE_SUPERNATURAL && GetEffectType(e) == EFFECT_TYPE_ATTACK_INCREASE)
        {{
            RemoveEffect(oTarget, e);
            bFound = TRUE;
        }}
        e = GetNextEffect(oTarget);
    }}
    return bFound;
}}

void Ov_ApplyStealthAmbush(object oTarget)
{{
    Ov_ConsumeStealthAmbush(oTarget);
    ApplyEffectToObject(DURATION_TYPE_TEMPORARY, SupernaturalEffect(EffectAttackIncrease(50)), oTarget, 6.0);
}}

void Ov_PollStealth()
{{
    int i = 0;
    while (i < 3)
    {{
        object oPM = GetPartyMemberByIndex(i);
        if (GetIsObjectValid(oPM) && IsStealthed(oPM))
        {{
            Ov_ApplyStealthAmbush(oPM);
        }}
        i += 1;
    }}
}}

void Ov_EnsureAutoGrants(object oTarget)
{{
    if (!Ov_IsPartyMember(oTarget)) return;
    int nHD = GetHitDice(oTarget);
    object oPC = GetFirstPC();

    // 1. Exceptions compagnons Kreia / Visas Niv. 15+
    if (oTarget != oPC && nHD >= 15)
    {{
        string sTag = GetStringLowerCase(GetTag(oTarget));
        if (sTag == "kreia" && !GetHasFeat(OV_PREST_MAGE, oTarget))
        {{
            GrantFeat(OV_PREST_MAGE, oTarget);
        }}
        else if ((sTag == "visasmarr" || sTag == "visas") && !GetHasFeat(OV_PREST_HYB, oTarget))
        {{
            GrantFeat(OV_PREST_HYB, oTarget);
        }}
    }}

    // 2. Octroi automatique 1/5/9 des pouvoirs de prestige (fiable meme sur sauvegardes existantes)
    int nJWM = GetLevelByClass(CLASS_TYPE_JEDIWEAPONMASTER, oTarget);
    if (nJWM >= 1 && !GetHasSpell(OV_SP_SCAR_1, oTarget)) GrantSpell(OV_SP_SCAR_1, oTarget);
    if (nJWM >= 5 && !GetHasSpell(OV_SP_SCAR_2, oTarget)) GrantSpell(OV_SP_SCAR_2, oTarget);
    if (nJWM >= 9 && !GetHasSpell(OV_SP_SCAR_3, oTarget)) GrantSpell(OV_SP_SCAR_3, oTarget);

    int nSMA = GetLevelByClass(CLASS_TYPE_SITHMARAUDER, oTarget);
    if (nSMA >= 1 && !GetHasSpell(164, oTarget)) GrantSpell(164, oTarget);
    if (nSMA >= 5 && !GetHasSpell(165, oTarget)) GrantSpell(165, oTarget);
    if (nSMA >= 9 && !GetHasSpell(166, oTarget)) GrantSpell(166, oTarget);

    int nJMA = GetLevelByClass(CLASS_TYPE_JEDIMASTER, oTarget);
    if (nJMA >= 1 && !GetHasSpell(167, oTarget)) GrantSpell(167, oTarget);
    if (nJMA >= 5 && !GetHasSpell(168, oTarget)) GrantSpell(168, oTarget);
    if (nJMA >= 9 && !GetHasSpell(169, oTarget)) GrantSpell(169, oTarget);

    int nSLD = GetLevelByClass(CLASS_TYPE_SITHLORD, oTarget);
    if (nSLD >= 1 && !GetHasSpell(144, oTarget)) GrantSpell(144, oTarget);
    if (nSLD >= 5 && !GetHasSpell(145, oTarget)) GrantSpell(145, oTarget);
    if (nSLD >= 9 && !GetHasSpell(146, oTarget)) GrantSpell(146, oTarget);

    int nSAS = GetLevelByClass(CLASS_TYPE_SITHASSASSIN, oTarget);
    if (nSAS >= 1 && !GetHasSpell(156, oTarget)) GrantSpell(156, oTarget);
    if (nSAS >= 5 && !GetHasSpell(157, oTarget)) GrantSpell(157, oTarget);
    if (nSAS >= 9 && !GetHasSpell(158, oTarget)) GrantSpell(158, oTarget);

    int nJWA = GetLevelByClass(CLASS_TYPE_JEDIWATCHMAN, oTarget);
    if (nJWA >= 1 && !GetHasFeat(OV_UNB_1, oTarget)) GrantFeat(OV_UNB_1, oTarget);
    if (nJWA >= 5 && !GetHasFeat(OV_UNB_2, oTarget)) GrantFeat(OV_UNB_2, oTarget);
    if (nJWA >= 9 && !GetHasFeat(OV_UNB_3, oTarget)) GrantFeat(OV_UNB_3, oTarget);

    // 3. Furtivite sans ceinture & Course furtive (Armure Tactique I-II et Spectre de la Force I)
    if (GetHasFeat(OV_ARM_M1, oTarget) || GetHasSpell(156, oTarget))
    {{
        if (!GetHasFeat(FEAT_PERSONAL_CLOAKING_SHIELD, oTarget)) GrantFeat(FEAT_PERSONAL_CLOAKING_SHIELD, oTarget);
    }}
    if (GetHasFeat(OV_ARM_M2, oTarget) || GetHasSpell(156, oTarget))
    {{
        if (!GetHasFeat(FEAT_STEALTH_RUN, oTarget)) GrantFeat(FEAT_STEALTH_RUN, oTarget);
    }}

    // 4. Tir d'Assaut II (Combat rapproche) & Tir Assassin II (Attaque sournoise native flanquement)
    if (GetHasFeat(OV_SP_ASSAULT_2, oTarget))
    {{
        if (!GetHasFeat(FEAT_CLOSE_COMBAT, oTarget)) GrantFeat(FEAT_CLOSE_COMBAT, oTarget);
        if (!GetHasFeat(140, oTarget)) GrantFeat(140, oTarget); // FEAT_IMPROVED_CLOSE_COMBAT
    }}
    if (GetHasFeat(OV_SP_ASSASSIN_2, oTarget))
    {{
        if (!GetHasFeat(FEAT_SNEAK_ATTACK_1D6, oTarget)) GrantFeat(FEAT_SNEAK_ATTACK_1D6, oTarget);
    }}
}}

void Ov_RefreshPassives(object oTarget)
{{
    if (!GetIsObjectValid(oTarget) || GetIsDead(oTarget)) return;
    object oPC = GetFirstPC();
    if (oTarget == oPC && !GetIsPlayerMadeCharacter(oTarget)) return;

    Ov_EnsureAutoGrants(oTarget);

    if (IsStealthed(oTarget))
    {{
        Ov_ApplyStealthAmbush(oTarget);
    }}

    int nTier = Ov_GetArmorTier(oTarget);
    int nTree = Ov_GetActiveCaracTree(oTarget);

    int nTotalAC = 0;
    int nTotalRD = 0;
    int nTotalImm = 0;
    int nTotalDodge = 0;
    int nTotalSaves = 0;
    int nTotalAtk = 0;
    int nTotalDmg = 0;
    int nExtraAttacks = 0;
    int nForceRes = 0;
    int nSkillAll = 0;
    int nStealthBon = 0;
    int bMindImm = FALSE;
    int bBreathPass = FALSE;

    // 1. RD native d'armure (Moyenne = 2/-, Lourde = 4/-)
    if (nTier == 2) nTotalRD += 2;
    else if (nTier == 3) nTotalRD += 4;

    // 2. Arbres d'armures
    if (nTier == 1)
    {{
        if (GetHasFeat(OV_ARM_L3, oTarget)) {{ nTotalAC += 3; nTotalDodge += 30; }}
        else if (GetHasFeat(OV_ARM_L2, oTarget)) {{ nTotalAC += 2; nTotalDodge += 20; }}
        else if (GetHasFeat(OV_ARM_L1, oTarget)) {{ nTotalAC += 1; nTotalDodge += 10; }}
    }}
    else if (nTier == 2)
    {{
        if (GetHasFeat(OV_ARM_M3, oTarget)) {{ nTotalAC += 3; nTotalRD += 5; }}
        else if (GetHasFeat(OV_ARM_M2, oTarget)) {{ nTotalAC += 2; nTotalRD += 4; }}
        else if (GetHasFeat(OV_ARM_M1, oTarget)) {{ nTotalAC += 1; nTotalRD += 3; }}
    }}
    else if (nTier == 3)
    {{
        if (GetHasFeat(OV_ARM_H3, oTarget)) {{ nTotalRD += 5; nTotalImm += 30; }}
        else if (GetHasFeat(OV_ARM_H2, oTarget)) {{ nTotalRD += 4; nTotalImm += 20; }}
        else if (GetHasFeat(OV_ARM_H1, oTarget)) {{ nTotalRD += 3; nTotalImm += 10; }}
    }}

    // 3. Armes equipees -> Postures, Scaling Distance/2M & Specialisations d'arme
    object oRight = GetItemInSlot(INVENTORY_SLOT_RIGHTWEAPON, oTarget);
    object oLeft  = GetItemInSlot(INVENTORY_SLOT_LEFTWEAPON, oTarget);
    int nBI = GetIsObjectValid(oRight) ? GetBaseItemType(oRight) : -1;
    int nFam = Ov_GetWeaponFamily(nBI);
    int bRanged = (nBI >= 0) ? Ov_IsRangedBaseItem(nBI) : FALSE;
    int bIsMirror1M = (nBI >= 0) ? Ov_IsMirror1MBaseItem(nBI) : FALSE;

    int nStr = GetAbilityModifier(ABILITY_STRENGTH, oTarget);
    int nDex = GetAbilityModifier(ABILITY_DEXTERITY, oTarget);
    int nCon = GetAbilityModifier(ABILITY_CONSTITUTION, oTarget);
    int nInt = GetAbilityModifier(ABILITY_INTELLIGENCE, oTarget);
    int nWis = GetAbilityModifier(ABILITY_WISDOM, oTarget);
    int nCha = GetAbilityModifier(ABILITY_CHARISMA, oTarget);

    // Modificateur de degats effectif a distance (DEX ou INT via Gand II) et melee (FOR ou DEX via Echani II)
    int nRngStat = nDex;
    if (nTree == 4 && GetHasFeat(OV_GAN_2, oTarget) && nInt > nDex) nRngStat = nInt;
    if (nRngStat < 0) nRngStat = 0;

    int nMelStat = nStr;
    if (nTree == 2 && GetHasFeat(OV_ECH_2, oTarget) && nDex > nStr) nMelStat = nDex;
    if (nMelStat < 0) nMelStat = 0;

    // Mains nues : compense 1d4 vanilla (moy. 2.5) -> 1d6 Armes.csv (moy. 3.5)
    if (nBI == -1)
    {{
        nTotalDmg += 1;
    }}

    // 3a. 4 Postures de combat + Scaling Distance DEX (0% natif moteur) & 2M
    if (GetIsObjectValid(oRight) && GetIsObjectValid(oLeft))
    {{
        // Ambidextrie (2 armes)
        if (GetHasFeat(OV_AMB_3, oTarget)) {{ nTotalAC += 3; nTotalAtk += 6; }}
        else if (GetHasFeat(OV_AMB_2, oTarget)) {{ nTotalAC += 2; nTotalAtk += 4; }}
        else if (GetHasFeat(OV_AMB_1, oTarget)) {{ nTotalAC += 1; nTotalAtk += 2; }}
        if (bRanged && nRngStat > 0) nTotalDmg += nRngStat; // +100% DEX/INT distance
    }}
    else if (GetIsObjectValid(oRight) && Ov_IsDoubleBaseItem(nBI) && !bIsMirror1M)
    {{
        // Arme haute cadence (double melee ou blaster a repetition) : malus -5/-3/-2/-1 CA, +0/+1/+2/+3 Dmg
        if (GetHasFeat(OV_DBL_3, oTarget)) {{ nTotalDmg += 3; nTotalAC -= 1; }}
        else if (GetHasFeat(OV_DBL_2, oTarget)) {{ nTotalDmg += 2; nTotalAC -= 2; }}
        else if (GetHasFeat(OV_DBL_1, oTarget)) {{ nTotalDmg += 1; nTotalAC -= 3; }}
        else {{ nTotalAC -= 5; }}

        if (bRanged)
        {{
            // Blasters a repetition : +1 attaque/round + 150% DEX/INT
            nExtraAttacks += 1;
            if (nRngStat > 0) nTotalDmg += (nRngStat * 150) / 100;
        }}
        else
        {{
            // Armes doubles de melee : compense le malus d'attaque TWF vanilla (-6)
            nTotalAtk += 6;
        }}
    }}
    else if (GetIsObjectValid(oRight) && Ov_IsHeavy2HBaseItem(nBI) && !bIsMirror1M)
    {{
        // Maniement d'arme lourde (2M non double) :
        // Base 2M sans don = 200% FOR melee (+100% au-dessus du 100% moteur) / 150% DEX distance
        // R1/R2/R3 ajoutent +1/+2/+3 Atq et +15%/+35%/+50% supplementaires
        int nPct2H = bRanged ? 150 : 100;
        if (GetHasFeat(OV_HVY_3, oTarget)) {{ nTotalAtk += 3; nPct2H += 50; }}
        else if (GetHasFeat(OV_HVY_2, oTarget)) {{ nTotalAtk += 2; nPct2H += 35; }}
        else if (GetHasFeat(OV_HVY_1, oTarget)) {{ nTotalAtk += 1; nPct2H += 15; }}
        int nStat2H = bRanged ? nRngStat : nMelStat;
        if (nStat2H > 0) nTotalDmg += (nStat2H * nPct2H) / 100;
    }}
    else if (!GetIsObjectValid(oLeft))
    {{
        // Duel (1M ou mains nues) : +2/+4/+6 Atq (et +1/+2/+3 critique gere dans Ov_OnDamageHook)
        if (GetHasFeat(OV_DUE_3, oTarget)) {{ nTotalAtk += 6; }}
        else if (GetHasFeat(OV_DUE_2, oTarget)) {{ nTotalAtk += 4; }}
        else if (GetHasFeat(OV_DUE_1, oTarget)) {{ nTotalAtk += 2; }}
        if (bRanged && nRngStat > 0) nTotalDmg += (nRngStat * 150) / 100; // +150% DEX/INT 1M Duel
    }}

    // 3b. 8 Specialisations d'arme
    if (nFam == 1 && GetHasFeat(OV_SP_BLUNT_1, oTarget)) {{ nTotalAtk += 2; nTotalDmg += 2; }}
    else if (nFam == 2 && GetHasFeat(OV_SP_PRIM_1, oTarget)) {{ nTotalAtk += 2; nTotalDmg += 2; }}
    else if (nFam == 3 && GetHasFeat(OV_SP_VIBRO_1, oTarget)) {{ nTotalAtk += 2; nTotalDmg += 2; }}
    else if (nFam == 4 && GetHasFeat(OV_SP_LASER_1, oTarget)) {{ nTotalAtk += 2; nTotalDmg += 2; }}
    else if (nFam == 5 && GetHasFeat(OV_SP_ASSAULT_1, oTarget))
    {{
        nTotalAtk += 2; nTotalDmg += 2;
        if (GetHasFeat(OV_SP_ASSAULT_2, oTarget))
        {{
            // Neutralise le malus de defense en melee (-10) quand un ennemi est au contact (<= 3.5m)
            object oNearE = GetNearestCreature(CREATURE_TYPE_REPUTATION, REPUTATION_TYPE_ENEMY, oTarget, 1);
            if (GetIsObjectValid(oNearE) && !GetIsDead(oNearE) && GetDistanceBetween(oTarget, oNearE) <= 3.5)
            {{
                nTotalAC += 6;
            }}
        }}
        if (GetHasFeat(OV_SP_ASSAULT_3, oTarget)) nExtraAttacks += 1;
    }}
    else if (nFam == 6 && GetHasFeat(OV_SP_HEAVY_1, oTarget))
    {{
        nTotalAtk += 2; nTotalDmg += 2;
        if (GetHasFeat(OV_SP_HEAVY_3, oTarget)) nTotalDmg += 5;
    }}
    else if (nFam == 7 && GetHasFeat(OV_SP_TAC_1, oTarget)) {{ nTotalAtk += 2; nTotalDmg += 2; }}
    else if (nFam == 8 && GetHasFeat(OV_SP_ASSASSIN_1, oTarget)) {{ nTotalAtk += 2; nTotalDmg += 2; }}

    // 4. Specialisations de Caracteristique (mutuellement exclusives via nTree)
    int nTreeAbil = -1;
    int nTreeBonus = 0;
    if (nTree == 1) // Gamoreen (FOR : +1/+2/+3 ; I: +1/2 FOR toutes comp. ; II: 1M ; III: imm. mental)
    {{
        nTreeAbil = ABILITY_STRENGTH;
        nTreeBonus = GetHasFeat(OV_GAM_3, oTarget) ? 3 : (GetHasFeat(OV_GAM_2, oTarget) ? 2 : 1);
        if (nStr > 0) nSkillAll += (nStr / 2);
        if (GetHasFeat(OV_GAM_3, oTarget)) bMindImm = TRUE;
    }}
    else if (nTree == 2) // Echani (DEX : +1/+2/+3 ; I: DEX Atq melee ; II: DEX Dmg melee ; III: leve plafond DEX)
    {{
        nTreeAbil = ABILITY_DEXTERITY;
        nTreeBonus = GetHasFeat(OV_ECH_3, oTarget) ? 3 : (GetHasFeat(OV_ECH_2, oTarget) ? 2 : 1);
        if (!bRanged && nDex > nStr)
        {{
            nTotalAtk += (nDex - nStr);
            if (GetHasFeat(OV_ECH_2, oTarget)) nTotalDmg += (nDex - nStr);
        }}
        if (GetHasFeat(OV_ECH_3, oTarget))
        {{
            int nCap = Ov_GetArmorDexCap(oTarget);
            if (nCap >= 0 && nDex > nCap) nTotalAC += (nDex - nCap);
        }}
    }}
    else if (nTree == 3) // Kraith (CON : +1/+2/+3 ; I: +1/2 CON arrondi sup. RD ; II: transfusion 1x/6s ; III: +CON saves)
    {{
        nTreeAbil = ABILITY_CONSTITUTION;
        nTreeBonus = GetHasFeat(OV_KRA_3, oTarget) ? 3 : (GetHasFeat(OV_KRA_2, oTarget) ? 2 : 1);
        if (nCon > 0) nTotalRD += (nCon + 1) / 2;
        if (GetHasFeat(OV_KRA_3, oTarget) && nCon > 0) nTotalSaves += nCon;
    }}
    else if (nTree == 4) // Gand (INT : +1/+2/+3 ; I: grenades/mines ; II: INT Atq/Dmg distance ; III: grenades)
    {{
        nTreeAbil = ABILITY_INTELLIGENCE;
        nTreeBonus = GetHasFeat(OV_GAN_3, oTarget) ? 3 : (GetHasFeat(OV_GAN_2, oTarget) ? 2 : 1);
        if (bRanged && GetHasFeat(OV_GAN_2, oTarget) && nInt > nDex)
        {{
            nTotalAtk += (nInt - nDex); // Degats deja calcules via nRngStat ci-dessus !
        }}
    }}
    else if (nTree == 5) // Matukai (SAG : +1/+2/+3 ; I: +SAG Atq ; II: +1/2 SAG saves + punition ; III: SAG->CA + riposte)
    {{
        nTreeAbil = ABILITY_WISDOM;
        nTreeBonus = GetHasFeat(OV_MAT_3, oTarget) ? 3 : (GetHasFeat(OV_MAT_2, oTarget) ? 2 : 1);
        if (nWis > 0) nTotalAtk += nWis;
        if (GetHasFeat(OV_MAT_2, oTarget) && nWis > 0) nTotalSaves += (nWis / 2);
        if (GetHasFeat(OV_MAT_3, oTarget) && nWis > nDex) nTotalAC += (nWis - nDex);
    }}
    else if (nTree == 6) // Nomi (CHA : +1/+2/+3 ; I: XP 100% ; II: +CHA saves groupe ; III: +CHA CA)
    {{
        nTreeAbil = ABILITY_CHARISMA;
        nTreeBonus = GetHasFeat(OV_NOM_3, oTarget) ? 3 : (GetHasFeat(OV_NOM_2, oTarget) ? 2 : 1);
        if (GetHasFeat(OV_NOM_2, oTarget) && nCha > 0) nTotalSaves += nCha;
        if (GetHasFeat(OV_NOM_3, oTarget) && nCha > 0) nTotalAC += nCha;
    }}

    // Aura Nomi II du PJ sur les compagnons
    if (oTarget != oPC && GetIsObjectValid(oPC) && (GetPartyMemberByIndex(1) == oTarget || GetPartyMemberByIndex(2) == oTarget))
    {{
        if (Ov_GetActiveCaracTree(oPC) == 6 && GetHasFeat(OV_NOM_2, oPC))
        {{
            int nChaPC = GetAbilityModifier(ABILITY_CHARISMA, oPC);
            if (nChaPC > 0) nTotalSaves += nChaPC;
        }}
    }}

    // 5. Affranchi de la Force I-III (4 paires / 8, cap +3/+5/+7 + RF 15+Niv au rang III)
    if (GetHasFeat(OV_UNB_1, oTarget))
    {{
        int nCap = GetHasFeat(OV_UNB_3, oTarget) ? 7 : (GetHasFeat(OV_UNB_2, oTarget) ? 5 : 3);
        int bAtk = (GetSkillRank(SKILL_COMPUTER_USE, oTarget) + GetSkillRank(SKILL_SECURITY, oTarget)) / 8;
        int bDmg = (GetSkillRank(SKILL_DEMOLITIONS, oTarget) + GetSkillRank(SKILL_REPAIR, oTarget)) / 8;
        int bAC  = (GetSkillRank(SKILL_AWARENESS, oTarget) + GetSkillRank(SKILL_STEALTH, oTarget)) / 8;
        int bSav = (GetSkillRank(SKILL_PERSUADE, oTarget) + GetSkillRank(SKILL_TREAT_INJURY, oTarget)) / 8;
        if (bAtk > nCap) bAtk = nCap;
        if (bDmg > nCap) bDmg = nCap;
        if (bAC  > nCap) bAC  = nCap;
        if (bSav > nCap) bSav = nCap;
        nTotalAtk += bAtk;
        nTotalDmg += bDmg;
        nTotalAC  += bAC;
        nTotalSaves += bSav;
        if (GetHasFeat(OV_UNB_3, oTarget) && (15 + GetHitDice(oTarget)) > nForceRes)
        {{
            nForceRes = 15 + GetHitDice(oTarget);
        }}
    }}

    // 6. Pouvoirs passifs refondus :
    //    - Spectre de la Force I-III (+4/+8/+12 Discretion jusqu'en Armure Moyenne + +25% esquive kill L3)
    if (nTier <= 2)
    {{
        if (GetHasSpell(158, oTarget)) nStealthBon += 12;
        else if (GetHasSpell(157, oTarget)) nStealthBon += 8;
        else if (GetHasSpell(156, oTarget)) nStealthBon += 4;
    }}
    if (GetLocalNumber(oTarget, 18) > 0) nTotalDodge += 25;

    //    - Premonition du combat (Echani : +10% esquive)
    if (GetHasFeat(OV_BATTLE_PRECOG, oTarget)) nTotalDodge += 10;

    //    - Parade / Renvoi grace a la Force (+2 / +4 Defense)
    if (GetHasSpell(163, oTarget)) nTotalAC += 4;
    else if (GetHasSpell(162, oTarget)) nTotalAC += 2;

    //    - Controle de la respiration (+4 Fortitude vs Poison permanent)
    if (GetHasSpell(270, oTarget)) bBreathPass = TRUE;

    // 7. Cristal personnel de l'Exile (uniquement si monte dans le sabre tenu en main -> prop 62)
    if (oTarget == oPC && nFam == 4 && Ov_HasPersonalCrystal(oPC))
    {{
        if (GetLevelByClass(CLASS_TYPE_JEDIGUARDIAN, oPC) > 0)
        {{
            nTotalAtk += 1;
        }}
        else if (GetLevelByClass(CLASS_TYPE_JEDISENTINEL, oPC) > 0)
        {{
            nTotalAtk += 1; nTotalAC += 1; nTotalSaves += 1;
        }}
        if (GetLevelByClass(CLASS_TYPE_JEDIWATCHMAN, oPC) > 0)
        {{
            nSkillAll += 3;
        }}
        // Maitre d'Armes : cumuls On-Hit (+1/+1 jusqu'a +5/+5) integres dans nTotalAC (regle T4!)
        if (GetLevelByClass(CLASS_TYPE_JEDIWEAPONMASTER, oPC) > 0)
        {{
            int nWM = GetLocalNumber(oPC, 24);
            if (nWM > 5) nWM = 5;
            if (nWM > 0) {{ nTotalAtk += nWM; nTotalAC += nWM; }}
        }}
    }}

    // 8. Traits runtime du Bestiaire & RD Boss Set_4/Set_5 (uniquement PNJ hostiles hors groupe)
    if (!Ov_IsPartyMember(oTarget) && GetIsObjectValid(oPC) && GetIsEnemy(oTarget, oPC))
    {{
        int nHD = GetHitDice(oTarget);
        string sLowTag = GetStringLowerCase(GetTag(oTarget));

        // 8a. Boss / Sous-boss : RD passive 2 (<=10) / 5 (11..18) / 8 (19+)
        if (Ov_IsBoss(oTarget))
        {{
            int nPcLvl = GetHitDice(oPC);
            int nBossRD = (nPcLvl <= 10) ? 2 : ((nPcLvl <= 18) ? 5 : 8);
            nTotalRD += nBossRD;
        }}

        // 8b. Sith / Jedi Obscurs : Resistance a la Force dynamique 15+Niv (Mid) / 20+Niv (Late) + Esquive Totale 20+
        if (GetMaxForcePoints(oTarget) > 0)
        {{
            int nSithSR = 0;
            if (nHD >= 14) nSithSR = 20 + nHD;
            else if (nHD >= 8) nSithSR = 15 + nHD;
            if (nSithSR > nForceRes) nForceRes = nSithSR;
            if (nHD >= 20 && !GetHasFeat(FEAT_EVASION, oTarget)) GrantFeat(FEAT_EVASION, oTarget);
        }}

        // 8c. Mandaloriens : Stim de combat (+2 FOR / +2 CON, 60s) declenche une fois a l'engagement
        if (GetIsInCombat(oTarget) && GetLocalNumber(oTarget, 15) == 0 && FindSubString(sLowTag, "mando") >= 0)
        {{
            SetLocalNumber(oTarget, 15, 1);
            effect eStim = EffectLinkEffects(EffectAbilityIncrease(ABILITY_STRENGTH, 2), EffectAbilityIncrease(ABILITY_CONSTITUTION, 2));
            ApplyEffectToObject(DURATION_TYPE_TEMPORARY, eStim, oTarget, 60.0);
        }}

        // 8d. Assassins Sith : Esquive 20% (Mid) / 25% (Late)
        if (FindSubString(sLowTag, "sithass") >= 0 || FindSubString(sLowTag, "assassin") >= 0)
        {{
            nTotalDodge += (nHD >= 14) ? 25 : 20;
        }}

        // 8e. Betes apex : regeneration lente HORS COMBAT uniquement
        if (!GetIsInCombat(oTarget) && nHD >= 12 && GetCurrentHitPoints(oTarget) < GetMaxHitPoints(oTarget))
        {{
            if (FindSubString(sLowTag, "boma") >= 0 || FindSubString(sLowTag, "zakkeg") >= 0 ||
                FindSubString(sLowTag, "drexl") >= 0 || FindSubString(sLowTag, "tukata") >= 0 ||
                FindSubString(sLowTag, "rancor") >= 0 || FindSubString(sLowTag, "stormbeast") >= 0 ||
                FindSubString(sLowTag, "hssiss") >= 0 || FindSubString(sLowTag, "kinrath") >= 0)
            {{
                int nReg = GetMaxHitPoints(oTarget) / 40;
                if (nReg < 2) nReg = 2;
                ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectHeal(nReg), oTarget);
            }}
        }}
    }}

    if (nTotalDodge > 75) nTotalDodge = 75;

    // Reconstruire proprement le bundle permanent (regle T4 : UN SEUL EffectACIncrease!)
    Ov_RemoveOldPassives(oTarget);
    int bHasAny = FALSE;
    effect eBundle;

    if (nTotalAC > 0)
    {{
        eBundle = EffectACIncrease(nTotalAC, AC_DODGE_BONUS);
        bHasAny = TRUE;
    }}
    else if (nTotalAC < 0)
    {{
        eBundle = EffectACDecrease(-nTotalAC);
        bHasAny = TRUE;
    }}
    if (nTotalRD > 0)
    {{
        effect eR1 = EffectDamageResistance(DAMAGE_TYPE_BLUDGEONING, nTotalRD);
        effect eR2 = EffectDamageResistance(DAMAGE_TYPE_PIERCING, nTotalRD);
        effect eR3 = EffectDamageResistance(DAMAGE_TYPE_SLASHING, nTotalRD);
        effect eR4 = EffectDamageResistance(DAMAGE_TYPE_BLASTER, nTotalRD);
        effect eRAll = EffectLinkEffects(EffectLinkEffects(eR1, eR2), EffectLinkEffects(eR3, eR4));
        if (bHasAny) eBundle = EffectLinkEffects(eBundle, eRAll); else eBundle = eRAll;
        bHasAny = TRUE;
    }}
    if (nTotalImm > 0)
    {{
        // Juggernaut : immunite % contre TOUS les types de degats (physiques + elementaires + Force)
        effect eI1 = EffectLinkEffects(EffectDamageImmunityIncrease(DAMAGE_TYPE_BLUDGEONING, nTotalImm), EffectDamageImmunityIncrease(DAMAGE_TYPE_PIERCING, nTotalImm));
        effect eI2 = EffectLinkEffects(EffectDamageImmunityIncrease(DAMAGE_TYPE_SLASHING, nTotalImm), EffectDamageImmunityIncrease(DAMAGE_TYPE_BLASTER, nTotalImm));
        effect eI3 = EffectLinkEffects(EffectDamageImmunityIncrease(DAMAGE_TYPE_FIRE, nTotalImm), EffectDamageImmunityIncrease(DAMAGE_TYPE_COLD, nTotalImm));
        effect eI4 = EffectLinkEffects(EffectDamageImmunityIncrease(DAMAGE_TYPE_ELECTRICAL, nTotalImm), EffectDamageImmunityIncrease(DAMAGE_TYPE_SONIC, nTotalImm));
        effect eI5 = EffectLinkEffects(EffectDamageImmunityIncrease(DAMAGE_TYPE_ION, nTotalImm), EffectDamageImmunityIncrease(DAMAGE_TYPE_ACID, nTotalImm));
        effect eI6 = EffectLinkEffects(EffectDamageImmunityIncrease(DAMAGE_TYPE_DARK_SIDE, nTotalImm), EffectDamageImmunityIncrease(DAMAGE_TYPE_LIGHT_SIDE, nTotalImm));
        effect eIAll = EffectLinkEffects(EffectLinkEffects(eI1, eI2), EffectLinkEffects(EffectLinkEffects(eI3, eI4), EffectLinkEffects(eI5, eI6)));
        if (bHasAny) eBundle = EffectLinkEffects(eBundle, eIAll); else eBundle = eIAll;
        bHasAny = TRUE;
    }}
    if (nTotalDodge > 0)
    {{
        effect eDg = EffectMissChance(nTotalDodge);
        if (bHasAny) eBundle = EffectLinkEffects(eBundle, eDg); else eBundle = eDg;
        bHasAny = TRUE;
    }}
    if (nTotalSaves > 0)
    {{
        effect eSv = EffectSavingThrowIncrease(SAVING_THROW_ALL, nTotalSaves);
        if (bHasAny) eBundle = EffectLinkEffects(eBundle, eSv); else eBundle = eSv;
        bHasAny = TRUE;
    }}
    if (bBreathPass)
    {{
        effect eBp = EffectSavingThrowIncrease(SAVING_THROW_FORT, 4, SAVING_THROW_TYPE_POISON);
        if (bHasAny) eBundle = EffectLinkEffects(eBundle, eBp); else eBundle = eBp;
        bHasAny = TRUE;
    }}
    if (nTotalAtk > 0)
    {{
        effect eAt = EffectAttackIncrease(nTotalAtk);
        if (bHasAny) eBundle = EffectLinkEffects(eBundle, eAt); else eBundle = eAt;
        bHasAny = TRUE;
    }}
    if (nTotalDmg > 0)
    {{
        effect eDm = EffectDamageIncrease(nTotalDmg, DAMAGE_TYPE_UNIVERSAL);
        if (bHasAny) eBundle = EffectLinkEffects(eBundle, eDm); else eBundle = eDm;
        bHasAny = TRUE;
    }}
    if (nExtraAttacks > 0)
    {{
        effect eEx = EffectModifyAttacks(nExtraAttacks);
        if (bHasAny) eBundle = EffectLinkEffects(eBundle, eEx); else eBundle = eEx;
        bHasAny = TRUE;
    }}
    if (nForceRes > 0)
    {{
        effect eFr = EffectForceResistanceIncrease(nForceRes);
        if (bHasAny) eBundle = EffectLinkEffects(eBundle, eFr); else eBundle = eFr;
        bHasAny = TRUE;
    }}
    if (nSkillAll > 0)
    {{
        int nSk = 0;
        while (nSk < 8)
        {{
            effect eSk = EffectSkillIncrease(nSk, nSkillAll);
            if (bHasAny) eBundle = EffectLinkEffects(eBundle, eSk); else eBundle = eSk;
            bHasAny = TRUE;
            nSk += 1;
        }}
    }}
    if (nStealthBon > 0)
    {{
        effect eStl = EffectSkillIncrease(SKILL_STEALTH, nStealthBon);
        if (bHasAny) eBundle = EffectLinkEffects(eBundle, eStl); else eBundle = eStl;
        bHasAny = TRUE;
    }}
    if (bMindImm)
    {{
        effect eMi = EffectImmunity(IMMUNITY_TYPE_MIND_SPELLS);
        if (bHasAny) eBundle = EffectLinkEffects(eBundle, eMi); else eBundle = eMi;
        bHasAny = TRUE;
    }}
    if (nTreeAbil >= 0 && nTreeBonus > 0)
    {{
        effect eAb = EffectAbilityIncrease(nTreeAbil, nTreeBonus);
        if (bHasAny) eBundle = EffectLinkEffects(eBundle, eAb); else eBundle = eAb;
        bHasAny = TRUE;
    }}

    if (bHasAny)
    {{
        ApplyEffectToObject(DURATION_TYPE_PERMANENT, ExtraordinaryEffect(eBundle), oTarget);
    }}
}}

// Garde-fou 1x / 6 secondes pour le PJ et son groupe (elimine le bug heartbeat xN PNJ!)
void Ov_UnlockPartyTick(object oPC)
{{
    if (GetIsObjectValid(oPC)) SetLocalNumber(oPC, 16, 0);
}}

void Ov_PartyTick6s()
{{
    object oPC = GetFirstPC();
    if (!GetIsObjectValid(oPC) || !GetIsPlayerMadeCharacter(oPC)) return;
    if (GetLocalNumber(oPC, 16) != 0) return;
    SetLocalNumber(oPC, 16, 1);
    DelayCommand(5.8, Ov_UnlockPartyTick(oPC));

    // Sondage furtivite groupe (une seule chaine par round, jamais xN!)
    Ov_PollStealth();
    DelayCommand(1.0, Ov_PollStealth());
    DelayCommand(2.0, Ov_PollStealth());
    DelayCommand(3.0, Ov_PollStealth());
    DelayCommand(4.0, Ov_PollStealth());
    DelayCommand(5.0, Ov_PollStealth());

    // Nomi I : compagnons a 100% de l'XP du PJ
    int bNomiXP = (Ov_GetActiveCaracTree(oPC) == 6 && GetHasFeat(OV_NOM_1, oPC));
    int nPcXP = GetXP(oPC);

    int i = 0;
    while (i < 3)
    {{
        object oPM = GetPartyMemberByIndex(i);
        if (GetIsObjectValid(oPM) && !GetIsDead(oPM))
        {{
            Ov_RefreshPassives(oPM);

            // Sync XP Nomi I
            if (bNomiXP && oPM != oPC && nPcXP > GetXP(oPM))
            {{
                SetXP(oPM, nPcXP);
            }}

            // Krayt II : Transfusion vitale (strictement 1x / 6 secondes!)
            if (Ov_GetActiveCaracTree(oPM) == 3 && GetHasFeat(OV_KRA_2, oPM))
            {{
                int nMaxHP = GetMaxHitPoints(oPM);
                int nCurHP = GetCurrentHitPoints(oPM);
                int nMaxFP = GetMaxForcePoints(oPM);
                int nCurFP = GetCurrentForcePoints(oPM);
                if (nMaxFP > 0 && nCurFP < (nMaxFP / 2) && nCurHP > ((nMaxHP * 3) / 4))
                {{
                    int nHpCost = nMaxHP / 20;
                    int nFpGain = nMaxFP / 20;
                    if (nHpCost < 1) nHpCost = 1;
                    if (nFpGain < 1) nFpGain = 1;
                    ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectDamage(nHpCost, DAMAGE_TYPE_DARK_SIDE), oPM);
                    ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectHealForcePoints(nFpGain), oPM);
                }}
            }}
        }}
        i += 1;
    }}

    // Cristal personnel de l'Exile (ticks 1x/6s : Seigneur Sith +3 PF, Gardien +1 PV/niv hors combat)
    if (!GetIsDead(oPC) && Ov_HasPersonalCrystal(oPC))
    {{
        if (GetLevelByClass(CLASS_TYPE_SITHLORD, oPC) > 0)
        {{
            ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectHealForcePoints(3), oPC);
        }}
        if (GetLevelByClass(CLASS_TYPE_JEDIGUARDIAN, oPC) > 0)
        {{
            if (GetIsInCombat(oPC))
            {{
                SetLocalNumber(oPC, 14, 2);
            }}
            else
            {{
                int nGState = GetLocalNumber(oPC, 14);
                if (nGState == 2) SetLocalNumber(oPC, 14, 0);
                if (GetLocalNumber(oPC, 14) == 0 && !GetHasSpellEffect(OV_SP_DEATH_FEAST, oPC))
                {{
                    int nBonusHP = GetHitDice(oPC);
                    if (nBonusHP > 0)
                    {{
                        SetLocalNumber(oPC, 14, 1);
                        ApplyEffectToObject(DURATION_TYPE_TEMPORARY, EffectTemporaryHitpoints(nBonusHP), oPC, 300.0);
                    }}
                }}
            }}
        }}
    }}
}}

int Ov_IsIncapacitated(object oTarget)
{{
    effect e = GetFirstEffect(oTarget);
    while (GetIsEffectValid(e))
    {{
        int nT = GetEffectType(e);
        if (nT == EFFECT_TYPE_STUNNED || nT == EFFECT_TYPE_PARALYZE || nT == EFFECT_TYPE_FRIGHTENED)
        {{
            return TRUE;
        }}
        e = GetNextEffect(oTarget);
    }}
    return FALSE;
}}

void Ov_ResetPushLock(object oVictim)
{{
    if (GetIsObjectValid(oVictim)) SetLocalNumber(oVictim, 28, 0);
}}

void Ov_ResetMutilate(object oVictim, int nTok)
{{
    if (GetIsObjectValid(oVictim) && GetLocalNumber(oVictim, 19) == nTok)
    {{
        SetLocalNumber(oVictim, 27, 0);
    }}
}}

void Ov_ResetArmorBreak(object oVictim, int nTok)
{{
    if (GetIsObjectValid(oVictim) && GetLocalNumber(oVictim, 20) == nTok)
    {{
        SetLocalNumber(oVictim, 25, 0);
    }}
}}

void Ov_ResetWMStack(object oPC, int nTok)
{{
    if (GetIsObjectValid(oPC) && GetLocalNumber(oPC, 21) == nTok)
    {{
        SetLocalNumber(oPC, 24, 0);
        Ov_RefreshPassives(oPC);
    }}
}}

void Ov_ResetSpectreKill(object oKiller, int nTok)
{{
    if (GetIsObjectValid(oKiller) && GetLocalNumber(oKiller, 17) == nTok)
    {{
        SetLocalNumber(oKiller, 18, 0);
        Ov_RefreshPassives(oKiller);
    }}
}}

void Ov_RemoveSupernaturalACDec(object oVictim)
{{
    effect e = GetFirstEffect(oVictim);
    while (GetIsEffectValid(e))
    {{
        if (GetEffectSubType(e) == SUBTYPE_SUPERNATURAL && GetEffectType(e) == EFFECT_TYPE_AC_DECREASE)
        {{
            RemoveEffect(oVictim, e);
        }}
        e = GetNextEffect(oVictim);
    }}
}}

void Ov_OnDamageHook(object oVictim)
{{
    object oAtk = GetLastDamager();
    if (!GetIsObjectValid(oAtk)) return;

    int nDealt = GetTotalDamageDealt();
    object oW = GetItemInSlot(INVENTORY_SLOT_RIGHTWEAPON, oAtk);
    object oL = GetItemInSlot(INVENTORY_SLOT_LEFTWEAPON, oAtk);
    int nBI = GetIsObjectValid(oW) ? GetBaseItemType(oW) : -1;
    int nFam = Ov_GetWeaponFamily(nBI);
    int bIsRanged = (nBI >= 0) ? Ov_IsRangedBaseItem(nBI) : FALSE;
    int bIsMirror1M = (nBI >= 0) ? Ov_IsMirror1MBaseItem(nBI) : FALSE;
    int nLvl = GetHitDice(oAtk);
    if (nLvl < 1) nLvl = 1;

    int nStat = bIsRanged
        ? GetAbilityModifier(ABILITY_DEXTERITY, oAtk)
        : GetAbilityModifier(ABILITY_STRENGTH, oAtk);
    int nTree = Ov_GetActiveCaracTree(oAtk);
    if (nTree == 2 && !bIsRanged)
    {{
        int nD = GetAbilityModifier(ABILITY_DEXTERITY, oAtk);
        if (nD > nStat) nStat = nD;
    }}
    else if (nTree == 4 && bIsRanged && GetHasFeat(OV_GAN_2, oAtk))
    {{
        int nI = GetAbilityModifier(ABILITY_INTELLIGENCE, oAtk);
        if (nI > nStat) nStat = nI;
    }}

    // 1. Embuscade furtive & Spectre de la Force II / III
    int bAmbush = (Ov_ConsumeStealthAmbush(oAtk) || IsStealthed(oAtk));
    int bSpectreKillCrit = (GetLocalNumber(oAtk, 18) >= 2);
    int bGuaranteedCrit = (bAmbush || bSpectreKillCrit);

    if (bGuaranteedCrit && nDealt > 0 && !GetIsDead(oVictim))
    {{
        if (bSpectreKillCrit) SetLocalNumber(oAtk, 18, 1); // Critique consomme, esquive +25% conservee
        ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectVisualEffect(VFX_IMP_FORCE_PUSH), oVictim);
        AssignCommand(oAtk, ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectDamage(nDealt, DAMAGE_TYPE_PIERCING), oVictim));
        // Spectre de la Force II : embuscade +2d6 degats + Etourdissement 1t (Vig annule)
        if (bAmbush && GetHasSpell(157, oAtk))
        {{
            AssignCommand(oAtk, ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectDamage(d6(2), DAMAGE_TYPE_PIERCING), oVictim));
            if (!FortitudeSave(oVictim, 10 + nLvl + nStat, SAVING_THROW_TYPE_NONE, oAtk))
            {{
                ApplyEffectToObject(DURATION_TYPE_TEMPORARY, EffectStunned(), oVictim, 6.0);
            }}
            else
            {{
                Ov_CheckMatukaiPunish(oVictim, oAtk);
            }}
        }}
    }}

    if (GetIsDead(oVictim) || nFam == 0) return;

    // 2. Plage de critique dynamique (baseitems.2da + Acere + Duel I-III + Cristal Assassin Sith)
    int nBaseThreat = Ov_GetWeaponBaseThreat(nBI);
    if (GetIsObjectValid(oW) && GetItemHasItemProperty(oW, 28)) nBaseThreat = nBaseThreat * 2;

    int nExtraThreat = 0;
    int bDuelPosture = (!GetIsObjectValid(oL) && !(GetIsObjectValid(oW) && (Ov_IsDoubleBaseItem(nBI) || Ov_IsHeavy2HBaseItem(nBI)) && !bIsMirror1M));
    if (bDuelPosture)
    {{
        if (GetHasFeat(OV_DUE_3, oAtk)) nExtraThreat += 3;
        else if (GetHasFeat(OV_DUE_2, oAtk)) nExtraThreat += 2;
        else if (GetHasFeat(OV_DUE_1, oAtk)) nExtraThreat += 1;
    }}
    int bSithAssnCrystal = (oAtk == GetFirstPC() && nFam == 4 && Ov_HasPersonalCrystal(oAtk) && GetLevelByClass(CLASS_TYPE_SITHASSASSIN, oAtk) > 0);
    if (bSithAssnCrystal) nExtraThreat += 1;

    int nTotalThreat = nBaseThreat + nExtraThreat;
    if (nTotalThreat > 19) nTotalThreat = 19;

    // Simulation critique etendu (Duel +1/+2/+3 & Cristal Assassin +1) et Critiques Massifs +2d6 / Tir Assassin III (+1 mult)
    int bSimulatedCrit = FALSE;
    if (!bGuaranteedCrit && nDealt > 0 && nExtraThreat > 0 && d20() <= nExtraThreat)
    {{
        bSimulatedCrit = TRUE;
        AssignCommand(oAtk, ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectDamage(nDealt, DAMAGE_TYPE_PIERCING), oVictim));
    }}
    if (bSithAssnCrystal && (bGuaranteedCrit || bSimulatedCrit || d20() <= nBaseThreat))
    {{
        AssignCommand(oAtk, ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectDamage(d6(2), DAMAGE_TYPE_PIERCING), oVictim));
    }}
    if (nFam == 8 && GetHasFeat(OV_SP_ASSASSIN_3, oAtk) && nDealt > 0)
    {{
        if (bGuaranteedCrit || bSimulatedCrit || d20() <= nTotalThreat)
        {{
            AssignCommand(oAtk, ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectDamage(nDealt, DAMAGE_TYPE_PIERCING), oVictim));
        }}
    }}

    if (GetIsDead(oVictim)) return;

    // 3. Procs des 8 Specialisations d'arme (Rangs II & III)
    if (nFam == 1 && GetHasFeat(OV_SP_BLUNT_2, oAtk)) // Impact II-III : Renversement sur plage critique
    {{
        if (d20() <= nTotalThreat)
        {{
            if (!FortitudeSave(oVictim, 10 + nLvl + nStat, SAVING_THROW_TYPE_NONE, oAtk))
            {{
                float fKD = GetHasFeat(OV_SP_BLUNT_3, oAtk) ? 12.0 : 6.0;
                ApplyEffectToObject(DURATION_TYPE_TEMPORARY, EffectKnockdown(), oVictim, fKD);
            }}
            else Ov_CheckMatukaiPunish(oVictim, oAtk);
        }}
    }}
    else if (nFam == 2 && GetHasFeat(OV_SP_PRIM_2, oAtk)) // Trad II-III : Bris d'armure -3 CA (cumulable en R3!)
    {{
        if (!FortitudeSave(oVictim, 5 + nLvl + nStat, SAVING_THROW_TYPE_NONE, oAtk))
        {{
            if (GetHasFeat(OV_SP_PRIM_3, oAtk))
            {{
                int nBr = GetLocalNumber(oVictim, 25) + 3;
                if (nBr > 12) nBr = 12;
                int nTokB = GetLocalNumber(oVictim, 20) + 1;
                if (nTokB > 200) nTokB = 1;
                SetLocalNumber(oVictim, 25, nBr);
                SetLocalNumber(oVictim, 20, nTokB);
                Ov_RemoveSupernaturalACDec(oVictim);
                ApplyEffectToObject(DURATION_TYPE_TEMPORARY, SupernaturalEffect(EffectACDecrease(nBr)), oVictim, 18.0);
                DelayCommand(18.0, Ov_ResetArmorBreak(oVictim, nTokB));
            }}
            else
            {{
                Ov_RemoveSupernaturalACDec(oVictim);
                ApplyEffectToObject(DURATION_TYPE_TEMPORARY, SupernaturalEffect(EffectACDecrease(3)), oVictim, 12.0);
            }}
        }}
        else Ov_CheckMatukaiPunish(oVictim, oAtk);
    }}
    else if (nFam == 3 && GetHasFeat(OV_SP_VIBRO_2, oAtk)) // Resonance II-III : Mutilation -4 (-8 empilable III)
    {{
        if (!ReflexSave(oVictim, 5 + nLvl + nStat, SAVING_THROW_TYPE_NONE, oAtk))
        {{
            int nPen = 4;
            if (GetHasFeat(OV_SP_VIBRO_3, oAtk))
            {{
                int nCur = GetLocalNumber(oVictim, 27);
                nPen = (nCur >= 4) ? (nCur + 2) : 4;
                if (nPen > 8) nPen = 8;
                int nTokM = GetLocalNumber(oVictim, 19) + 1;
                if (nTokM > 200) nTokM = 1;
                SetLocalNumber(oVictim, 27, nPen);
                SetLocalNumber(oVictim, 19, nTokM);
                DelayCommand(6.5, Ov_ResetMutilate(oVictim, nTokM));
            }}
            effect eMut = EffectLinkEffects(EffectAttackDecrease(nPen), EffectDamageDecrease(nPen, DAMAGE_TYPE_UNIVERSAL));
            ApplyEffectToObject(DURATION_TYPE_TEMPORARY, eMut, oVictim, 6.0);
        }}
        else Ov_CheckMatukaiPunish(oVictim, oAtk);
    }}
    else if (nFam == 4 && GetHasFeat(OV_SP_LASER_2, oAtk)) // Laser II-III : Bris de volonte -4 saves (sans jet III)
    {{
        if (GetHasFeat(OV_SP_LASER_3, oAtk))
        {{
            ApplyEffectToObject(DURATION_TYPE_TEMPORARY, EffectSavingThrowDecrease(SAVING_THROW_ALL, 4), oVictim, 12.0);
        }}
        else if (!WillSave(oVictim, 5 + nLvl + nStat, SAVING_THROW_TYPE_MIND_AFFECTING, oAtk))
        {{
            ApplyEffectToObject(DURATION_TYPE_TEMPORARY, EffectSavingThrowDecrease(SAVING_THROW_ALL, 4), oVictim, 12.0);
        }}
        else Ov_CheckMatukaiPunish(oVictim, oAtk);
    }}
    else if (nFam == 6 && GetHasFeat(OV_SP_HEAVY_2, oAtk)) // Penetrant II : Repousse 3m (1x/round)
    {{
        if (GetLocalNumber(oVictim, 28) == 0)
        {{
            if (!FortitudeSave(oVictim, 5 + nLvl + nStat, SAVING_THROW_TYPE_NONE, oAtk))
            {{
                SetLocalNumber(oVictim, 28, 1);
                ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectForcePushTargeted(GetLocation(oAtk)), oVictim);
                DelayCommand(6.0, Ov_ResetPushLock(oVictim));
            }}
            else Ov_CheckMatukaiPunish(oVictim, oAtk);
        }}
    }}
    else if (nFam == 7 && GetHasFeat(OV_SP_TAC_2, oAtk)) // Tactique II-III : Stun 1-2 tours sur plage critique
    {{
        if (d20() <= nTotalThreat)
        {{
            if (!FortitudeSave(oVictim, 10 + nLvl + nStat, SAVING_THROW_TYPE_NONE, oAtk))
            {{
                float fSt = GetHasFeat(OV_SP_TAC_3, oAtk) ? 12.0 : 6.0;
                effect eSt = (GetRacialType(oVictim) == RACIAL_TYPE_DROID) ? EffectDroidStun() : EffectStunned();
                ApplyEffectToObject(DURATION_TYPE_TEMPORARY, eSt, oVictim, fSt);
            }}
            else Ov_CheckMatukaiPunish(oVictim, oAtk);
        }}
    }}
    else if (nFam == 8 && GetHasFeat(OV_SP_ASSASSIN_2, oAtk)) // Assassin II : +2d6 degats sur cible incapacitee/embusquee
    {{
        if (bAmbush || Ov_IsIncapacitated(oVictim))
        {{
            AssignCommand(oAtk, ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectDamage(d6(2), DAMAGE_TYPE_PIERCING), oVictim));
        }}
    }}

    // 3b. Armes soniques : On-Hit -2 DEX (DD scale 5 + Niv + Carac)
    if (nBI >= 0 && Ov_IsSonicBaseItem(nBI))
    {{
        if (!FortitudeSave(oVictim, 5 + nLvl + nStat, SAVING_THROW_TYPE_SONIC, oAtk))
        {{
            ApplyEffectToObject(DURATION_TYPE_TEMPORARY, EffectAbilityDecrease(ABILITY_DEXTERITY, 2), oVictim, 12.0);
        }}
        else Ov_CheckMatukaiPunish(oVictim, oAtk);
    }}

    // 4. Cristal personnel de l'Exile : procs On-Hit de prestige (monte dans le sabre!)
    if (oAtk == GetFirstPC() && nFam == 4 && Ov_HasPersonalCrystal(oAtk))
    {{
        if (GetLevelByClass(CLASS_TYPE_JEDIWEAPONMASTER, oAtk) > 0)
        {{
            int nSt = GetLocalNumber(oAtk, 24) + 1;
            if (nSt > 5) nSt = 5;
            int nTokW = GetLocalNumber(oAtk, 21) + 1;
            if (nTokW > 200) nTokW = 1;
            SetLocalNumber(oAtk, 24, nSt);
            SetLocalNumber(oAtk, 21, nTokW);
            Ov_RefreshPassives(oAtk); // Regle T4 : AC integre dans l'unique EffectACIncrease!
            DelayCommand(12.0, Ov_ResetWMStack(oAtk, nTokW));
        }}
        if (GetLevelByClass(CLASS_TYPE_SITHMARAUDER, oAtk) > 0)
        {{
            int nH = GetMaxHitPoints(oAtk) / 100;
            if (nH < 1) nH = 1;
            ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectHeal(nH), oAtk);
        }}
    }}
}}

void Ov_OnDeathHook(object oDead)
{{
    object oKiller = GetLastKiller();
    if (!GetIsObjectValid(oKiller) || GetIsDead(oKiller)) return;
    // Spectre de la Force III : chaque kill donne prochaine attaque = critique confirme + +25% esquive 12s
    if (GetHasSpell(158, oKiller))
    {{
        int nTok = GetLocalNumber(oKiller, 17) + 1;
        if (nTok > 200) nTok = 1;
        SetLocalNumber(oKiller, 17, nTok);
        SetLocalNumber(oKiller, 18, 2);
        Ov_RefreshPassives(oKiller);
        DelayCommand(12.0, Ov_ResetSpectreKill(oKiller, nTok));
    }}
}}

void Ov_OnAttackedHook(object oDefender)
{{
    if (!GetIsObjectValid(oDefender) || GetIsDead(oDefender)) return;
    // Matukai III : riposte mod. SAG en degats directs si l'attaquant rate son coup
    if (Ov_GetActiveCaracTree(oDefender) == 5 && GetHasFeat(OV_MAT_3, oDefender))
    {{
        object oAttacker = GetLastAttacker(oDefender);
        if (GetIsObjectValid(oAttacker) && !GetIsDead(oAttacker) && GetTotalDamageDealt() == 0)
        {{
            int nWis = GetAbilityModifier(ABILITY_WISDOM, oDefender);
            if (nWis > 0)
            {{
                AssignCommand(oDefender, ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectDamage(nWis, DAMAGE_TYPE_BLUDGEONING), oAttacker));
            }}
        }}
    }}
}}
'''
    (SRC_DIR / "ov_inc_core.nss").write_text(code, encoding="latin1")
    return code


def build_wrappers() -> None:
    drain_hook = '''
void Ov_SithDrainForceCheck()
{
    if (!GetIsInCombat(OBJECT_SELF) || GetIsPC(OBJECT_SELF)) return;
    int nMaxFP = GetMaxForcePoints(OBJECT_SELF);
    if (nMaxFP <= 0) return;
    if (GetCurrentForcePoints(OBJECT_SELF) < ((nMaxFP * 30) / 100))
    {
        object oTarget = GetNearestCreature(CREATURE_TYPE_REPUTATION, REPUTATION_TYPE_ENEMY, OBJECT_SELF, 1, CREATURE_TYPE_PERCEPTION, PERCEPTION_SEEN);
        if (GetIsObjectValid(oTarget))
        {
            if (GetHasSpell(FORCE_POWER_MASTER_DRAIN_FORCE)) ActionCastSpellAtObject(FORCE_POWER_MASTER_DRAIN_FORCE, oTarget);
            else if (GetHasSpell(FORCE_POWER_IMPROVED_DRAIN_FORCE)) ActionCastSpellAtObject(FORCE_POWER_IMPROVED_DRAIN_FORCE, oTarget);
            else if (GetHasSpell(FORCE_POWER_DRAIN_FORCE)) ActionCastSpellAtObject(FORCE_POWER_DRAIN_FORCE, oTarget);
        }
    }
}
'''
    wrappers = {
        "k_hen_heartbt01": '#include "k_inc_switch"\n#include "ov_inc_core"\nvoid main() {\n    Ov_PartyTick6s();\n    Ov_RefreshPassives(OBJECT_SELF);\n    ExecuteScript("k_ai_master", OBJECT_SELF, KOTOR_HENCH_EVENT_ON_HEARTBEAT);\n}\n',
        "k_def_heartbt01": '#include "k_inc_switch"\n#include "ov_inc_core"\n' + drain_hook + '\nvoid main() {\n    Ov_PartyTick6s();\n    Ov_RefreshPassives(OBJECT_SELF);\n    Ov_SithDrainForceCheck();\n    ExecuteScript("k_ai_master", OBJECT_SELF, KOTOR_DEFAULT_EVENT_ON_HEARTBEAT);\n}\n',
        "k_hen_damage01":  '#include "k_inc_switch"\n#include "ov_inc_core"\nvoid main() {\n    Ov_OnDamageHook(OBJECT_SELF);\n    ExecuteScript("k_ai_master", OBJECT_SELF, KOTOR_HENCH_EVENT_ON_DAMAGE);\n}\n',
        "k_def_damage01":  '#include "k_inc_switch"\n#include "ov_inc_core"\nvoid main() {\n    Ov_OnDamageHook(OBJECT_SELF);\n    ExecuteScript("k_ai_master", OBJECT_SELF, KOTOR_DEFAULT_EVENT_ON_DAMAGE);\n}\n',
        "k_hen_attacked01": '#include "k_inc_switch"\n#include "ov_inc_core"\nvoid main() {\n    Ov_OnAttackedHook(OBJECT_SELF);\n    ExecuteScript("k_ai_master", OBJECT_SELF, KOTOR_HENCH_EVENT_ON_ATTACKED);\n}\n',
        "k_def_attacked01": '#include "k_inc_switch"\n#include "ov_inc_core"\nvoid main() {\n    Ov_PollStealth();\n    Ov_OnAttackedHook(OBJECT_SELF);\n    ExecuteScript("k_ai_master", OBJECT_SELF, KOTOR_DEFAULT_EVENT_ON_ATTACKED);\n}\n',
        "k_def_death01":    '#include "k_inc_switch"\n#include "ov_inc_core"\nvoid main() {\n    Ov_OnDeathHook(OBJECT_SELF);\n    ExecuteScript("k_ai_master", OBJECT_SELF, KOTOR_DEFAULT_EVENT_ON_DEATH);\n}\n',
    }
    for name, code in wrappers.items():
        compile_script(name, code)


def build_support_scripts() -> None:
    """Compile k_sup_bands, k_sup_healing, k_trp_generic, k_sup_grenade et a_addcombatpre."""
    # 1. k_sup_bands.nss : Armure Tactique I (+100% duree), II/III (x2/x3 absorption) + Affranchi II (+25%)
    bands = (REF_SCRIPTS / "k_sup_bands.nss").read_text(encoding="latin1")
    bands = bands.replace('#include "k_inc_debug"', '#include "k_inc_debug"\n#include "ov_inc_core"', 1)
    bands_hook = '''    // Overhaul : Armure Tactique I-III (duree x2, absorption x2/x3) + Affranchi II (+25%)
    int nOvArmTier = Ov_GetArmorTier(OBJECT_SELF);
    if (nOvArmTier == 2 && GetHasFeat(OV_ARM_M1, OBJECT_SELF))
    {
        fDuration = fDuration * 2.0;
    }
    int nOvTactTier = 0;
    if (nOvArmTier == 2)
    {
        if (GetHasFeat(OV_ARM_M3, OBJECT_SELF)) nOvTactTier = 2;
        else if (GetHasFeat(OV_ARM_M2, OBJECT_SELF)) nOvTactTier = 1;
    }
    int nOvUnb2 = GetHasFeat(OV_UNB_2, OBJECT_SELF) ? 21 : 0;
    nShield = nShield + (nOvTactTier * 42) + nOvUnb2;

    effect eShield = EffectForceShield(nShield);'''
    assert "effect eShield = EffectForceShield(nShield);" in bands
    bands = bands.replace("effect eShield = EffectForceShield(nShield);", bands_hook, 1)
    compile_script("k_sup_bands", bands)

    # 2. k_sup_healing.nss : Affranchi II (+25% medpacs/kits) + Echo des Liens L3 (partage groupe)
    heal = (REF_SCRIPTS / "k_sup_healing.nss").read_text(encoding="latin1")
    heal = heal.replace('#include "k_inc_force"', '#include "k_inc_force"\n#include "ov_inc_core"', 1)
    heal = heal.replace(
        "int nHeal = 10;",
        "int nHeal = 10;\n        if (GetHasFeat(OV_UNB_2, OBJECT_SELF)) nHeal = (nHeal * 125) / 100;",
        1,
    )
    heal_old = "eHeal = EffectHeal(nSkill);\n        ApplyEffectToObject(DURATION_TYPE_INSTANT, eHeal, GetSpellTarget());"
    heal_old_crlf = heal_old.replace("\n", "\r\n")
    heal_new = '''if (GetHasFeat(OV_UNB_2, OBJECT_SELF))
        {
            nSkill = (nSkill * 125) / 100;
        }
        eHeal = EffectHeal(nSkill);
        object oHealTarget = GetSpellTarget();
        ApplyEffectToObject(DURATION_TYPE_INSTANT, eHeal, oHealTarget);
        // Echo des Liens L3 : partage des soins medpacs/kits avec tout le groupe
        if (GetLocalNumber(OBJECT_SELF, 23) >= 3)
        {
            int nEi = 0;
            while (nEi < 3)
            {
                object oEPM = GetPartyMemberByIndex(nEi);
                if (GetIsObjectValid(oEPM) && !GetIsDead(oEPM) && oEPM != oHealTarget)
                {
                    ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectHeal(nSkill), oEPM);
                }
                nEi += 1;
            }
        }'''
    if heal_old_crlf in heal:
        heal = heal.replace(heal_old_crlf, heal_new, 1)
    elif heal_old in heal:
        heal = heal.replace(heal_old, heal_new, 1)
    else:
        raise RuntimeError("Anchor not found in k_sup_healing.nss")
    compile_script("k_sup_healing", heal)

    # 3. k_trp_generic.nss : Gand I (+5%/rang Demolition) + Affranchi II (+25%) + Esquive Totale 1/2 sur echec
    trp = (REF_SCRIPTS / "k_trp_generic.nss").read_text(encoding="latin1")
    trp_helpers = '''#include "k_inc_debug"
#include "ov_inc_core"

int Ov_ScaleMineDamage(int nBaseDmg, int nDemoSkill)
{
    if (nDemoSkill <= 0) return nBaseDmg;
    int bHasGand1 = FALSE;
    int bHasUnb2 = FALSE;
    int i = 0;
    while (i < 3)
    {
        object oPM = GetPartyMemberByIndex(i);
        if (GetIsObjectValid(oPM))
        {
            if (Ov_GetActiveCaracTree(oPM) == 4 && GetHasFeat(OV_GAN_1, oPM)) bHasGand1 = TRUE;
            if (GetHasFeat(OV_UNB_2, oPM)) bHasUnb2 = TRUE;
        }
        i += 1;
    }
    int nOut = nBaseDmg;
    if (bHasGand1) nOut = nOut + (nOut * nDemoSkill * 5) / 100;
    if (bHasUnb2) nOut = (nOut * 125) / 100;
    return nOut;
}

int Ov_MineReflexDmg(int nDamage, object oTarget, int nDC)
{
    int bSaved = ReflexSave(oTarget, nDC, SAVING_THROW_TYPE_NONE);
    if (bSaved)
    {
        if (GetHasFeat(FEAT_EVASION, oTarget)) return 0;
        return nDamage / 2;
    }
    if (GetHasFeat(FEAT_EVASION, oTarget)) return nDamage / 2;
    return nDamage;
}
'''
    trp = trp.replace("\r\n", "\n")
    trp = trp.replace('#include "k_inc_debug"', trp_helpers, 1)
    trp = trp.replace(
        "nDamage += nDemoSkill;//RWT-OEI 05/24/04 - Took out the /5 per Fergus",
        "nDamage += nDemoSkill; nDamage = Ov_ScaleMineDamage(nDamage, nDemoSkill);",
    )
    trp = trp.replace(
        "nDamage += 3 * nDemoSkill / 2;//RWT-OEI 05/24/04 - Changed to (3*skill)/2 per Fergus",
        "nDamage += (3 * nDemoSkill) / 2; nDamage = Ov_ScaleMineDamage(nDamage, nDemoSkill);",
    )
    # Sonic mine only (avoid double-matching the already patched frag line!)
    trp = re.sub(
        r"nDamage \+= nDemoSkill;(?!\s*nDamage = Ov_ScaleMineDamage)",
        "nDamage += nDemoSkill; nDamage = Ov_ScaleMineDamage(nDamage, nDemoSkill);",
        trp,
    )
    trp = trp.replace("GetReflexAdjustedDamage(nDamage, oTarget, nDC)", "Ov_MineReflexDmg(nDamage, oTarget, nDC)")
    # Eviter de muter nDamage dans la boucle Frag/Plasma entre cibles (bug vanilla corrige aussi!)
    trp = trp.replace(
        "nDamage = Ov_MineReflexDmg(nDamage, oTarget, nDC);\n                eDamage = EffectDamage(nDamage, DAMAGE_TYPE_PIERCING);",
        "int nDmgApp = Ov_MineReflexDmg(nDamage, oTarget, nDC);\n                eDamage = EffectDamage(nDmgApp, DAMAGE_TYPE_PIERCING);",
    )
    trp = trp.replace(
        "nDamage = Ov_MineReflexDmg(nDamage, oTarget, nDC);\n                eDamage = EffectDamage(nDamage, DAMAGE_TYPE_BLASTER);",
        "int nDmgApp = Ov_MineReflexDmg(nDamage, oTarget, nDC);\n                eDamage = EffectDamage(nDmgApp, DAMAGE_TYPE_BLASTER);",
    )
    compile_script("k_trp_generic", trp)

    # 4. a_addcombatpre.nss : Premonition du combat -> +10% esquive (don OV_BATTLE_PRECOG)
    combatpre = '''//:: a_addcombatpre - Premonition du combat Echani (+10% esquive melee)
#include "ov_inc_core"
void main()
{
    object oPC = GetFirstPC();
    if (!GetIsObjectValid(oPC)) return;
    if (!GetHasFeat(OV_BATTLE_PRECOG, oPC))
    {
        GrantFeat(OV_BATTLE_PRECOG, oPC);
    }
    Ov_RefreshPassives(oPC);
}
'''
    compile_script("a_addcombatpre", combatpre)

    # 5. k_sup_grenade.nss : refonte propre (DD 10+Niv+INT, +2 roquettes/flechettes, Poison scale,
    #    Gand I +5%/Demo sur TOUTES grenades/roquettes, Affranchi II +25%,
    #    Gand III rayon 6m + percage Esquive Totale + 50% remboursement, Esquive Totale 1/2 sur echec, Matukai II)
    grenade_code = '''//:: k_sup_grenade - Grenades, Roquettes & Flechettes (KotOR 2 Overhaul)
#include "k_inc_debug"
#include "k_inc_force"
#include "ov_inc_core"

int GR_GetGrenadeDC(object oTarget)
{
    int nDC = 0;
    if (GetHasFeat(FEAT_UNCANNY_DODGE_1, oTarget))
    {
        nDC += 2;
        if (GetHasFeat(FEAT_UNCANNY_DODGE_2, oTarget)) nDC += 2;
    }
    return nDC;
}

int Ov_IsRocketOrDart(int nSpell)
{
    return (nSpell == 185 || (nSpell >= 190 && nSpell <= 199));
}

int Ov_HasGand3(object oCaster)
{
    return (Ov_GetActiveCaracTree(oCaster) == 4 && GetHasFeat(OV_GAN_3, oCaster));
}

int Ov_GrBaseDC(int nSpell)
{
    int nDC = 10 + GetHitDice(OBJECT_SELF) + GetAbilityModifier(ABILITY_INTELLIGENCE, OBJECT_SELF);
    if (Ov_IsRocketOrDart(nSpell)) nDC += 2;
    return nDC;
}

int Ov_GrScaleDmg(int nDamage)
{
    if (Ov_GetActiveCaracTree(OBJECT_SELF) == 4 && GetHasFeat(OV_GAN_1, OBJECT_SELF))
    {
        nDamage = nDamage + (nDamage * GetSkillRank(SKILL_DEMOLITIONS, OBJECT_SELF) * 5) / 100;
    }
    if (GetHasFeat(OV_UNB_2, OBJECT_SELF))
    {
        nDamage = (nDamage * 125) / 100;
    }
    return nDamage;
}

int Ov_GrReflexRoll(object oTarget, int nDamage, int nDC, int nDmgType, int nSaveType, float fDelay = 0.0)
{
    int bGand3 = Ov_HasGand3(OBJECT_SELF);
    int bEvasion = GetHasFeat(FEAT_EVASION, oTarget);
    int bSaved = ReflexSave(oTarget, nDC, nSaveType, OBJECT_SELF);
    int nApply = nDamage;
    if (bSaved)
    {
        Ov_CheckMatukaiPunish(oTarget, OBJECT_SELF);
        if (bEvasion && !bGand3) nApply = 0;
        else nApply = nDamage / 2;
    }
    else
    {
        if (bEvasion && !bGand3) nApply = nDamage / 2;
    }
    if (nApply > 0)
    {
        if (fDelay > 0.0) DelayCommand(fDelay, ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectDamage(nApply, nDmgType), oTarget));
        else ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectDamage(nApply, nDmgType), oTarget);
    }
    return bSaved;
}

string Ov_GetGrenadeResRef(int nSpell)
{
    if (nSpell == 87 || nSpell == 246) return "g_w_fraggren01";
    if (nSpell == 88 || nSpell == 247) return "g_w_stungren01";
    if (nSpell == 89 || nSpell == 248) return "g_w_thermldet01";
    if (nSpell == 90 || nSpell == 249) return "g_w_poisngren01";
    if (nSpell == 91 || nSpell == 250) return "g_w_sonicgren01";
    if (nSpell == 186 || nSpell == 255) return "g_w_sonicdet01";
    if (nSpell == 187 || nSpell == 256) return "g_w_sonicdet02";
    if (nSpell == 92 || nSpell == 251) return "g_w_adhsvgren001";
    if (nSpell == 93 || nSpell == 252) return "g_w_cryobgren001";
    if (nSpell == 94 || nSpell == 253) return "g_w_firegren001";
    if (nSpell == 95 || nSpell == 254) return "g_w_iongren01";
    return "";
}

void main()
{
    int nSpell = GetSpellId();
    int nDamage = 0;
    int nDC = Ov_GrBaseDC(nSpell);
    int nDCCheck = nDC;
    int nVFX = 0;
    int nFeat = GetHasFeat(FEAT_WEAPON_SPECIALIZATION_GRENADE) ? 6 : 0;
    float fRad = Ov_HasGand3(OBJECT_SELF) ? 6.0 : 4.0;
    location lLoc = GetSpellTargetLocation();
    object oTarget;

    if (nSpell == 87 || nSpell == 246) // Fragmentation
    {
        ApplyEffectAtLocation(DURATION_TYPE_INSTANT, EffectVisualEffect(1044), lLoc);
        nVFX = 3003;
        nDamage = Ov_GrScaleDmg(20 + nFeat);
        oTarget = GetFirstObjectInShape(SHAPE_SPHERE, fRad, lLoc, FALSE);
        while (GetIsObjectValid(oTarget))
        {
            if (!GetIsNeutral(oTarget))
            {
                SignalEvent(oTarget, EventSpellCastAt(OBJECT_SELF, nSpell, SWFP_HARMFUL));
                Ov_GrReflexRoll(oTarget, nDamage, nDC - GR_GetGrenadeDC(oTarget), DAMAGE_TYPE_PIERCING, SAVING_THROW_TYPE_NONE);
            }
            oTarget = GetNextObjectInShape(SHAPE_SPHERE, fRad, lLoc, FALSE);
        }
    }
    else if (nSpell == 88 || nSpell == 247) // Stun Grenade
    {
        nVFX = 3004;
        effect eStun = EffectLinkEffects(SetEffectIcon(EffectStunned(), 41), EffectVisualEffect(VFX_IMP_STUN));
        effect eDroidStun = EffectDroidStun();
        oTarget = GetFirstObjectInShape(SHAPE_SPHERE, fRad, lLoc, FALSE);
        while (GetIsObjectValid(oTarget))
        {
            if (!GetIsNeutral(oTarget))
            {
                SignalEvent(oTarget, EventSpellCastAt(OBJECT_SELF, nSpell, SWFP_HARMFUL));
                if (!WillSave(oTarget, nDC - GR_GetGrenadeDC(oTarget), SAVING_THROW_TYPE_SONIC, OBJECT_SELF))
                {
                    if (GetRacialType(oTarget) == RACIAL_TYPE_DROID) ApplyEffectToObject(DURATION_TYPE_TEMPORARY, eDroidStun, oTarget, 9.0);
                    else if (!GetIsLinkImmune(oTarget, eStun)) ApplyEffectToObject(DURATION_TYPE_TEMPORARY, eStun, oTarget, 9.0);
                }
                else Ov_CheckMatukaiPunish(oTarget, OBJECT_SELF);
            }
            oTarget = GetNextObjectInShape(SHAPE_SPHERE, fRad, lLoc, FALSE);
        }
    }
    else if (nSpell == 89 || nSpell == 248) // Thermal Detonator
    {
        ApplyEffectAtLocation(DURATION_TYPE_INSTANT, EffectVisualEffect(1044), lLoc);
        nVFX = 3005;
        nDamage = Ov_GrScaleDmg(60 + nFeat);
        effect ePush = EffectForcePushTargeted(lLoc);
        oTarget = GetFirstObjectInShape(SHAPE_SPHERE, fRad, lLoc, FALSE);
        while (GetIsObjectValid(oTarget))
        {
            if (!GetIsNeutral(oTarget))
            {
                SignalEvent(oTarget, EventSpellCastAt(OBJECT_SELF, nSpell, SWFP_HARMFUL));
                Ov_GrReflexRoll(oTarget, nDamage, nDC - GR_GetGrenadeDC(oTarget), DAMAGE_TYPE_BLASTER, SAVING_THROW_TYPE_BLASTER, 0.5);
                ApplyEffectToObject(DURATION_TYPE_TEMPORARY, ePush, oTarget, 0.1);
            }
            oTarget = GetNextObjectInShape(SHAPE_SPHERE, fRad, lLoc, FALSE);
        }
    }
    else if (nSpell == 90 || nSpell == 249) // Poison Grenade (DD scale scripte!)
    {
        nVFX = 3006;
        effect ePoison = EffectPoison(POISON_DAMAGE_AVERAGE);
        oTarget = GetFirstObjectInShape(SHAPE_SPHERE, fRad, lLoc, FALSE);
        while (GetIsObjectValid(oTarget))
        {
            if (!GetIsNeutral(oTarget) && GetRacialType(oTarget) != RACIAL_TYPE_DROID)
            {
                SignalEvent(oTarget, EventSpellCastAt(OBJECT_SELF, nSpell, SWFP_HARMFUL));
                if (!FortitudeSave(oTarget, nDC - GR_GetGrenadeDC(oTarget), SAVING_THROW_TYPE_POISON, OBJECT_SELF))
                {
                    if (!GetIsPoisoned(oTarget)) ApplyEffectToObject(DURATION_TYPE_PERMANENT, ePoison, oTarget);
                }
                else Ov_CheckMatukaiPunish(oTarget, OBJECT_SELF);
            }
            oTarget = GetNextObjectInShape(SHAPE_SPHERE, fRad, lLoc, FALSE);
        }
    }
    else if (nSpell == 91 || nSpell == 250 || nSpell == 186 || nSpell == 187 || nSpell == 255 || nSpell == 256) // Sonic 1 / 2 / 3
    {
        nVFX = 3007;
        int nDexPen = 6;
        int nBase = 20;
        if (nSpell == 187 || nSpell == 256) { nBase = 12; nDexPen = 4; }
        else if (nSpell == 186 || nSpell == 255) { nBase = 6; nDexPen = 2; }
        nDamage = Ov_GrScaleDmg(nBase + nFeat);
        effect eDex = SetEffectIcon(EffectAbilityDecrease(ABILITY_DEXTERITY, nDexPen), 41);
        int bGand3 = Ov_HasGand3(OBJECT_SELF);
        oTarget = GetFirstObjectInShape(SHAPE_SPHERE, fRad, lLoc, FALSE);
        while (GetIsObjectValid(oTarget))
        {
            if (!GetIsNeutral(oTarget))
            {
                SignalEvent(oTarget, EventSpellCastAt(OBJECT_SELF, nSpell, SWFP_HARMFUL));
                int bEvasion = GetHasFeat(FEAT_EVASION, oTarget);
                if (!WillSave(oTarget, nDC - GR_GetGrenadeDC(oTarget), SAVING_THROW_TYPE_SONIC, OBJECT_SELF))
                {
                    int nApp = (bEvasion && !bGand3) ? (nDamage / 2) : nDamage;
                    ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectDamage(nApp, DAMAGE_TYPE_SONIC), oTarget);
                    ApplyEffectToObject(DURATION_TYPE_TEMPORARY, eDex, oTarget, 30.0);
                }
                else
                {
                    Ov_CheckMatukaiPunish(oTarget, OBJECT_SELF);
                    int nApp = (bEvasion && !bGand3) ? 0 : (nDamage / 2);
                    if (nApp > 0) ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectDamage(nApp, DAMAGE_TYPE_SONIC), oTarget);
                }
            }
            oTarget = GetNextObjectInShape(SHAPE_SPHERE, fRad, lLoc, FALSE);
        }
    }
    else if (nSpell == 92 || nSpell == 251) // Adhesive Grenade
    {
        nVFX = 3008;
        effect eEnt = SetEffectIcon(EffectEntangle(), 43);
        effect eGoo = EffectVisualEffect(1038);
        oTarget = GetFirstObjectInShape(SHAPE_SPHERE, fRad, lLoc, FALSE);
        while (GetIsObjectValid(oTarget))
        {
            if (!GetIsNeutral(oTarget))
            {
                SignalEvent(oTarget, EventSpellCastAt(OBJECT_SELF, nSpell, SWFP_HARMFUL));
                if (!GetIsLinkImmune(oTarget, eEnt) || GetRacialType(oTarget) == RACIAL_TYPE_DROID)
                {
                    ApplyEffectToObject(DURATION_TYPE_TEMPORARY, eEnt, oTarget, 15.0);
                    DelayCommand(0.8, ApplyEffectAtLocation(DURATION_TYPE_INSTANT, eGoo, GetLocation(oTarget)));
                }
            }
            oTarget = GetNextObjectInShape(SHAPE_SPHERE, fRad, lLoc, FALSE);
        }
    }
    else if (nSpell == 93 || nSpell == 252) // Cryoban Grenade
    {
        nVFX = 3009;
        nDamage = Ov_GrScaleDmg(20 + nFeat);
        effect ePara = SetEffectIcon(EffectParalyze(), 44);
        oTarget = GetFirstObjectInShape(SHAPE_SPHERE, fRad, lLoc, FALSE);
        while (GetIsObjectValid(oTarget))
        {
            if (!GetIsNeutral(oTarget))
            {
                SignalEvent(oTarget, EventSpellCastAt(OBJECT_SELF, nSpell, SWFP_HARMFUL));
                int bSaved = Ov_GrReflexRoll(oTarget, nDamage, nDC - GR_GetGrenadeDC(oTarget), DAMAGE_TYPE_COLD, SAVING_THROW_TYPE_COLD);
                if (!bSaved && (!GetIsLinkImmune(oTarget, ePara) || GetRacialType(oTarget) == RACIAL_TYPE_DROID))
                {
                    ApplyEffectToObject(DURATION_TYPE_TEMPORARY, ePara, oTarget, 6.0);
                }
            }
            oTarget = GetNextObjectInShape(SHAPE_SPHERE, fRad, lLoc, FALSE);
        }
    }
    else if (nSpell == 94 || nSpell == 253) // Plasma Grenade
    {
        ApplyEffectAtLocation(DURATION_TYPE_INSTANT, EffectVisualEffect(1044), lLoc);
        nVFX = 3010;
        nDamage = Ov_GrScaleDmg(36 + nFeat);
        effect eHorror = EffectHorrified();
        effect eFlame = EffectVisualEffect(VFX_IMP_FLAME);
        oTarget = GetFirstObjectInShape(SHAPE_SPHERE, fRad, lLoc, FALSE);
        while (GetIsObjectValid(oTarget))
        {
            if (!GetIsNeutral(oTarget))
            {
                SignalEvent(oTarget, EventSpellCastAt(OBJECT_SELF, nSpell, SWFP_HARMFUL));
                int bSaved = Ov_GrReflexRoll(oTarget, nDamage, nDC - GR_GetGrenadeDC(oTarget), DAMAGE_TYPE_FIRE, SAVING_THROW_TYPE_FIRE);
                if (!bSaved)
                {
                    ApplyEffectToObject(DURATION_TYPE_INSTANT, eFlame, oTarget);
                    ApplyEffectToObject(DURATION_TYPE_TEMPORARY, eHorror, oTarget, 2.0);
                }
            }
            oTarget = GetNextObjectInShape(SHAPE_SPHERE, fRad, lLoc, FALSE);
        }
    }
    else if (nSpell == 95 || nSpell == 254) // Ion Grenade
    {
        nVFX = 3011;
        oTarget = GetFirstObjectInShape(SHAPE_SPHERE, fRad, lLoc, FALSE);
        while (GetIsObjectValid(oTarget))
        {
            if (!GetIsNeutral(oTarget))
            {
                SignalEvent(oTarget, EventSpellCastAt(OBJECT_SELF, nSpell, SWFP_HARMFUL));
                int nIonBase = 15 + nFeat + ((GetRacialType(oTarget) == RACIAL_TYPE_DROID) ? 30 : 0);
                Ov_GrReflexRoll(oTarget, Ov_GrScaleDmg(nIonBase), nDC - GR_GetGrenadeDC(oTarget), DAMAGE_TYPE_ION, SAVING_THROW_TYPE_ION);
            }
            oTarget = GetNextObjectInShape(SHAPE_SPHERE, fRad, lLoc, FALSE);
        }
    }
    else if (nSpell == 185) // Explosive Rocket
    {
        oTarget = GetSpellTargetObject();
        ApplyEffectAtLocation(DURATION_TYPE_INSTANT, EffectVisualEffect(1044), lLoc);
        nVFX = 3005;
        if (!GetIsNeutral(oTarget))
        {
            SignalEvent(oTarget, EventSpellCastAt(OBJECT_SELF, nSpell, SWFP_HARMFUL));
            if (!ReflexSave(oTarget, nDC, SAVING_THROW_TYPE_NONE, OBJECT_SELF))
                ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectDamage(Ov_GrScaleDmg(10), DAMAGE_TYPE_PIERCING), oTarget);
            else Ov_CheckMatukaiPunish(oTarget, OBJECT_SELF);
        }
        nDamage = Ov_GrScaleDmg(24);
        oTarget = GetFirstObjectInShape(SHAPE_SPHERE, fRad, lLoc, FALSE);
        while (GetIsObjectValid(oTarget))
        {
            if (!GetIsNeutral(oTarget))
            {
                SignalEvent(oTarget, EventSpellCastAt(OBJECT_SELF, nSpell, SWFP_HARMFUL));
                Ov_GrReflexRoll(oTarget, nDamage, nDC, DAMAGE_TYPE_PIERCING, SAVING_THROW_TYPE_NONE);
            }
            oTarget = GetNextObjectInShape(SHAPE_SPHERE, fRad, lLoc, FALSE);
        }
    }
    else if (nSpell == 190) // Buster Rocket
    {
        oTarget = GetSpellTargetObject();
        nVFX = 3005;
        if (!GetIsNeutral(oTarget))
        {
            SignalEvent(oTarget, EventSpellCastAt(OBJECT_SELF, nSpell, SWFP_HARMFUL));
            Ov_GrReflexRoll(oTarget, Ov_GrScaleDmg(50), nDC, DAMAGE_TYPE_PIERCING, SAVING_THROW_TYPE_NONE);
        }
    }
    else if (nSpell == 191) // Poison Rocket (DD scale scripte!)
    {
        oTarget = GetSpellTargetObject();
        nVFX = 3006;
        if (!GetIsNeutral(oTarget))
        {
            SignalEvent(oTarget, EventSpellCastAt(OBJECT_SELF, nSpell, SWFP_HARMFUL));
            if (!ReflexSave(oTarget, nDC, SAVING_THROW_TYPE_NONE, OBJECT_SELF))
                ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectDamage(Ov_GrScaleDmg(10), DAMAGE_TYPE_PIERCING), oTarget);
            else Ov_CheckMatukaiPunish(oTarget, OBJECT_SELF);
        }
        effect ePoison = EffectPoison(POISON_DAMAGE_ROCKET);
        oTarget = GetFirstObjectInShape(SHAPE_SPHERE, fRad, lLoc, FALSE);
        while (GetIsObjectValid(oTarget))
        {
            if (!GetIsNeutral(oTarget) && GetRacialType(oTarget) != RACIAL_TYPE_DROID)
            {
                SignalEvent(oTarget, EventSpellCastAt(OBJECT_SELF, nSpell, SWFP_HARMFUL));
                if (!FortitudeSave(oTarget, nDC, SAVING_THROW_TYPE_POISON, OBJECT_SELF))
                {
                    if (!GetIsPoisoned(oTarget)) ApplyEffectToObject(DURATION_TYPE_PERMANENT, ePoison, oTarget);
                }
                else Ov_CheckMatukaiPunish(oTarget, OBJECT_SELF);
            }
            oTarget = GetNextObjectInShape(SHAPE_SPHERE, fRad, lLoc, FALSE);
        }
    }
    else if (nSpell == 192) // Ion Rocket
    {
        oTarget = GetSpellTargetObject();
        nVFX = 3011;
        if (!GetIsNeutral(oTarget))
        {
            SignalEvent(oTarget, EventSpellCastAt(OBJECT_SELF, nSpell, SWFP_HARMFUL));
            if (!ReflexSave(oTarget, nDC, SAVING_THROW_TYPE_NONE, OBJECT_SELF))
                ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectDamage(Ov_GrScaleDmg(10), DAMAGE_TYPE_PIERCING), oTarget);
            else Ov_CheckMatukaiPunish(oTarget, OBJECT_SELF);
        }
        nDamage = Ov_GrScaleDmg(48);
        oTarget = GetFirstObjectInShape(SHAPE_SPHERE, fRad, lLoc, FALSE);
        while (GetIsObjectValid(oTarget))
        {
            if (!GetIsNeutral(oTarget))
            {
                SignalEvent(oTarget, EventSpellCastAt(OBJECT_SELF, nSpell, SWFP_HARMFUL));
                Ov_GrReflexRoll(oTarget, nDamage, nDC, DAMAGE_TYPE_ION, SAVING_THROW_TYPE_ION);
            }
            oTarget = GetNextObjectInShape(SHAPE_SPHERE, fRad, lLoc, FALSE);
        }
    }
    else if (nSpell == 193) // Plasma Rocket
    {
        oTarget = GetSpellTargetObject();
        ApplyEffectAtLocation(DURATION_TYPE_INSTANT, EffectVisualEffect(1044), lLoc);
        nVFX = 3010;
        if (!GetIsNeutral(oTarget))
        {
            SignalEvent(oTarget, EventSpellCastAt(OBJECT_SELF, nSpell, SWFP_HARMFUL));
            if (!ReflexSave(oTarget, nDC, SAVING_THROW_TYPE_NONE, OBJECT_SELF))
                ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectDamage(Ov_GrScaleDmg(10), DAMAGE_TYPE_PIERCING), oTarget);
            else Ov_CheckMatukaiPunish(oTarget, OBJECT_SELF);
        }
        nDamage = Ov_GrScaleDmg(36);
        oTarget = GetFirstObjectInShape(SHAPE_SPHERE, fRad, lLoc, FALSE);
        while (GetIsObjectValid(oTarget))
        {
            if (!GetIsNeutral(oTarget))
            {
                SignalEvent(oTarget, EventSpellCastAt(OBJECT_SELF, nSpell, SWFP_HARMFUL));
                Ov_GrReflexRoll(oTarget, nDamage, nDC, DAMAGE_TYPE_FIRE, SAVING_THROW_TYPE_FIRE);
            }
            oTarget = GetNextObjectInShape(SHAPE_SPHERE, fRad, lLoc, FALSE);
        }
    }
    else if (nSpell == 194) // Concussion Rocket
    {
        oTarget = GetSpellTargetObject();
        if (!GetIsNeutral(oTarget))
        {
            SignalEvent(oTarget, EventSpellCastAt(OBJECT_SELF, nSpell, SWFP_HARMFUL));
            if (!ReflexSave(oTarget, nDC, SAVING_THROW_TYPE_NONE, OBJECT_SELF))
            {
                ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectDamage(1, DAMAGE_TYPE_BLUDGEONING), oTarget);
                ApplyEffectToObject(DURATION_TYPE_TEMPORARY, EffectForcePushed(), oTarget, 0.1);
                DelayCommand(2.55, ApplyEffectToObject(DURATION_TYPE_TEMPORARY, EffectStunned(), oTarget, 9.0));
            }
            else Ov_CheckMatukaiPunish(oTarget, OBJECT_SELF);
        }
    }
    else if (nSpell == 195) // Poison Dart (DD scale scripte!)
    {
        oTarget = GetSpellTargetObject();
        if (!GetIsNeutral(oTarget))
        {
            SignalEvent(oTarget, EventSpellCastAt(OBJECT_SELF, nSpell, SWFP_HARMFUL));
            ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectDamage(1, DAMAGE_TYPE_PIERCING), oTarget);
            if (GetRacialType(oTarget) != RACIAL_TYPE_DROID)
            {
                if (!FortitudeSave(oTarget, nDC, SAVING_THROW_TYPE_POISON, OBJECT_SELF))
                {
                    if (!GetIsPoisoned(oTarget)) ApplyEffectToObject(DURATION_TYPE_PERMANENT, EffectPoison(POISON_DAMAGE_NORMAL_DART), oTarget);
                }
                else Ov_CheckMatukaiPunish(oTarget, OBJECT_SELF);
            }
        }
    }
    else if (nSpell == 196) // Kyber Dart
    {
        oTarget = GetSpellTargetObject();
        if (!GetIsNeutral(oTarget))
        {
            SignalEvent(oTarget, EventSpellCastAt(OBJECT_SELF, nSpell, SWFP_HARMFUL));
            ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectDamage(1, DAMAGE_TYPE_PIERCING), oTarget);
            if (!GetIsPoisoned(oTarget) && GetRacialType(oTarget) != RACIAL_TYPE_DROID)
            {
                if (!FortitudeSave(oTarget, nDC, SAVING_THROW_TYPE_POISON, OBJECT_SELF))
                    ApplyEffectToObject(DURATION_TYPE_PERMANENT, EffectPoison(POISON_DAMAGE_KYBER_DART), oTarget);
                else
                {
                    Ov_CheckMatukaiPunish(oTarget, OBJECT_SELF);
                    ApplyEffectToObject(DURATION_TYPE_PERMANENT, EffectPoison(POISON_DAMAGE_KYBER_DART_HALF), oTarget);
                }
            }
        }
    }
    else if (nSpell == 197) // Paralysis Dart
    {
        oTarget = GetSpellTargetObject();
        if (!GetIsNeutral(oTarget))
        {
            SignalEvent(oTarget, EventSpellCastAt(OBJECT_SELF, nSpell, SWFP_HARMFUL));
            ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectDamage(1, DAMAGE_TYPE_PIERCING), oTarget);
            if (GetRacialType(oTarget) != RACIAL_TYPE_DROID)
            {
                if (!FortitudeSave(oTarget, nDC, SAVING_THROW_TYPE_PARALYSIS, OBJECT_SELF))
                {
                    ApplyEffectToObject(DURATION_TYPE_TEMPORARY, SetEffectIcon(EffectParalyze(), 44), oTarget, 9.0);
                }
                else
                {
                    Ov_CheckMatukaiPunish(oTarget, OBJECT_SELF);
                    effect eSlow = EffectLinkEffects(EffectMovementSpeedDecrease(50), EffectACDecrease(2));
                    eSlow = EffectLinkEffects(eSlow, EffectAttackDecrease(2));
                    eSlow = EffectLinkEffects(eSlow, EffectSavingThrowDecrease(SAVING_THROW_REFLEX, 2));
                    ApplyEffectToObject(DURATION_TYPE_TEMPORARY, eSlow, oTarget, 3.0);
                }
            }
        }
    }
    else if (nSpell == 198) // Tranquilizer Dart
    {
        oTarget = GetSpellTargetObject();
        if (!GetIsNeutral(oTarget))
        {
            SignalEvent(oTarget, EventSpellCastAt(OBJECT_SELF, nSpell, SWFP_HARMFUL));
            ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectDamage(1, DAMAGE_TYPE_PIERCING), oTarget);
            if (GetRacialType(oTarget) != RACIAL_TYPE_DROID)
            {
                if (!FortitudeSave(oTarget, nDC, SAVING_THROW_TYPE_PARALYSIS, OBJECT_SELF))
                {
                    effect eSt = EffectLinkEffects(SetEffectIcon(EffectStunned(), 41), EffectVisualEffect(VFX_IMP_STUN));
                    ApplyEffectToObject(DURATION_TYPE_TEMPORARY, eSt, oTarget, 9.0);
                }
                else Ov_CheckMatukaiPunish(oTarget, OBJECT_SELF);
            }
        }
    }
    else if (nSpell == 199) // Lawn Dart
    {
        oTarget = GetSpellTargetObject();
        if (!GetIsNeutral(oTarget))
        {
            SignalEvent(oTarget, EventSpellCastAt(OBJECT_SELF, nSpell, SWFP_HARMFUL));
            if (!ReflexSave(oTarget, nDC, SAVING_THROW_TYPE_NONE, OBJECT_SELF))
                ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectDamage(Ov_GrScaleDmg(50), DAMAGE_TYPE_PIERCING), oTarget);
            else Ov_CheckMatukaiPunish(oTarget, OBJECT_SELF);
        }
    }

    if (nVFX > 0) ApplyEffectAtLocation(DURATION_TYPE_INSTANT, EffectVisualEffect(nVFX), lLoc);

    // Gand III : 50% de chance de ne pas consommer la grenade
    if (Ov_HasGand3(OBJECT_SELF) && d2() == 1)
    {
        string sRefund = Ov_GetGrenadeResRef(nSpell);
        if (sRefund != "")
        {
            CreateItemOnObject(sRefund, OBJECT_SELF, 1);
        }
    }
}
'''
    compile_script("k_sup_grenade", grenade_code)


def build_ov_inc_powers(fids: dict[str, int], sids: dict[str, int]) -> str:
    """Genere ov_inc_powers.nss : refontes mecaniques completes des pouvoirs (Passes 1, 2 & 3)."""
    pen1, pen2, pen3 = fids["MOD_META_PENETRATE_1"], fids["MOD_META_PENETRATE_2"], fids["MOD_META_PENETRATE_3"]
    emp1, emp2, emp3 = fids["MOD_META_EMPOWER_1"], fids["MOD_META_EMPOWER_2"], fids["MOD_META_EMPOWER_3"]
    code = f'''//:: ov_inc_powers - Refontes completes des pouvoirs de la Force (KotOR 2 Overhaul)
#include "ov_inc_core"

int Ov_IsArmorAllowedOffensive(int nSpell)
{{
    if (nSpell == FORCE_POWER_FEAR || nSpell == FORCE_POWER_HORROR || nSpell == FORCE_POWER_INSANITY) return TRUE;
    if (nSpell == 159 || nSpell == 160 || nSpell == 161) return TRUE;
    if (nSpell == FORCE_POWER_SLOW || nSpell == FORCE_POWER_AFFLICTION || nSpell == FORCE_POWER_PLAGUE) return TRUE;
    if (nSpell == FORCE_POWER_FORCE_PUSH || nSpell == FORCE_POWER_FORCE_WHIRLWIND || nSpell == FORCE_POWER_FORCE_WAVE) return TRUE;
    if (nSpell == 153 || nSpell == 154 || nSpell == 155) return TRUE;
    if (nSpell == FORCE_POWER_LIGHT_SABER_THROW || nSpell == FORCE_POWER_LIGHT_SABER_THROW_ADVANCED) return TRUE;
    if (nSpell == 47 || nSpell == 12 || nSpell == 13) return TRUE; // Droid Stun/Disable/Destroy
    if (nSpell == 144 || nSpell == 145 || nSpell == 146) return TRUE;
    if (nSpell == FORCE_POWER_FORCE_CRUSH) return TRUE;
    return FALSE;
}}

int Ov_IsOffensiveDamagePower(int nSpell)
{{
    if (nSpell == FORCE_POWER_SHOCK || nSpell == FORCE_POWER_LIGHTNING || nSpell == FORCE_POWER_FORCE_STORM) return TRUE;
    if (nSpell == FORCE_POWER_FEAR || nSpell == FORCE_POWER_HORROR || nSpell == FORCE_POWER_INSANITY) return TRUE;
    if (nSpell == FORCE_POWER_WOUND || nSpell == FORCE_POWER_CHOKE || nSpell == FORCE_POWER_KILL) return TRUE;
    if (nSpell == FORCE_POWER_DRAIN_LIFE || nSpell == FORCE_POWER_DEATH_FIELD || nSpell == OV_SP_DEATH_FEAST) return TRUE;
    if (nSpell == FORCE_POWER_SLOW || nSpell == FORCE_POWER_AFFLICTION || nSpell == FORCE_POWER_PLAGUE) return TRUE;
    if (nSpell == FORCE_POWER_FORCE_PUSH || nSpell == FORCE_POWER_FORCE_WHIRLWIND || nSpell == FORCE_POWER_FORCE_WAVE) return TRUE;
    if (nSpell == 159 || nSpell == 160 || nSpell == 161) return TRUE;
    if (nSpell == FORCE_POWER_LIGHT_SABER_THROW || nSpell == FORCE_POWER_LIGHT_SABER_THROW_ADVANCED) return TRUE;
    if (nSpell == 47 || nSpell == 12 || nSpell == 13) return TRUE;
    if (nSpell == 153 || nSpell == 154 || nSpell == 155) return TRUE;
    if (nSpell == FORCE_POWER_FORCE_CRUSH) return TRUE;
    return FALSE;
}}

void Ov_ApplyCastFPCostMods(object oCaster, int nSpell)
{{
    // Consulaire Cristal personnel : -10% cout PF (monte dans le sabre)
    if (oCaster == GetFirstPC() && Ov_HasPersonalCrystal(oCaster) && GetLevelByClass(CLASS_TYPE_JEDICONSULAR, oCaster) > 0)
    {{
        int nBaseFP = GetSpellBaseForcePointCost(nSpell);
        int nRefund = (nBaseFP * 10) / 100;
        if (nRefund > 0) ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectHealForcePoints(nRefund), oCaster);
    }}
    // Pouvoir Amplifie I-III : surcout +2 / +4 / +6 PF sur les pouvoirs offensifs
    if (Ov_IsOffensiveDamagePower(nSpell))
    {{
        int nExtraFP = 0;
        if (GetHasFeat({emp3}, oCaster)) nExtraFP = 6;
        else if (GetHasFeat({emp2}, oCaster)) nExtraFP = 4;
        else if (GetHasFeat({emp1}, oCaster)) nExtraFP = 2;
        if (nExtraFP > 0) ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectDamageForcePoints(nExtraFP), oCaster);
    }}
}}

int Ov_GetSpellDC(object oCaster, int nSpell = 0)
{{
    int nDC = Sp_GetJediDCSave();
    if (GetHasFeat({pen3}, oCaster)) nDC += 6;
    else if (GetHasFeat({pen2}, oCaster)) nDC += 4;
    else if (GetHasFeat({pen1}, oCaster)) nDC += 2;
    if (oCaster == GetFirstPC() && Ov_HasPersonalCrystal(oCaster))
    {{
        if (GetLevelByClass(CLASS_TYPE_JEDIMASTER, oCaster) > 0 || GetLevelByClass(CLASS_TYPE_SITHLORD, oCaster) > 0)
        {{
            nDC += 2;
        }}
    }}
    // Corps de Force I-III : +2/+4/+6 DD des pouvoirs utilisables sous armure
    if (nSpell == 0 || Ov_IsArmorAllowedOffensive(nSpell))
    {{
        if (GetHasSpellEffect(152, oCaster)) nDC += 6;
        else if (GetHasSpellEffect(151, oCaster)) nDC += 4;
        else if (GetHasSpellEffect(150, oCaster)) nDC += 2;
    }}
    return nDC;
}}

void Ov_RemoveTempHP(object oTarget)
{{
    effect e = GetFirstEffect(oTarget);
    while (GetIsEffectValid(e))
    {{
        if (GetEffectType(e) == EFFECT_TYPE_TEMPORARY_HITPOINTS) RemoveEffect(oTarget, e);
        e = GetNextEffect(oTarget);
    }}
}}

void Ov_MirrorBuffViaEcho(object oCaster, effect eBuff, float fDur)
{{
    int nEcho = GetLocalNumber(oCaster, 23);
    if (nEcho <= 0) return;
    if (nEcho == 1)
    {{
        object oBest = OBJECT_INVALID;
        float fMinD = 999.0;
        int i = 0;
        while (i < 3)
        {{
            object oPM = GetPartyMemberByIndex(i);
            if (GetIsObjectValid(oPM) && !GetIsDead(oPM) && oPM != oCaster)
            {{
                float d = GetDistanceBetween(oCaster, oPM);
                if (d < fMinD) {{ fMinD = d; oBest = oPM; }}
            }}
            i += 1;
        }}
        if (GetIsObjectValid(oBest)) ApplyEffectToObject(DURATION_TYPE_TEMPORARY, eBuff, oBest, fDur);
    }}
    else
    {{
        int i = 0;
        while (i < 3)
        {{
            object oPM = GetPartyMemberByIndex(i);
            if (GetIsObjectValid(oPM) && !GetIsDead(oPM) && oPM != oCaster)
            {{
                ApplyEffectToObject(DURATION_TYPE_TEMPORARY, eBuff, oPM, fDur);
            }}
            i += 1;
        }}
    }}
}}

void Ov_ResetEchoLinks(object oCaster)
{{
    if (GetIsObjectValid(oCaster)) SetLocalNumber(oCaster, 23, 0);
}}

void Ov_MentalDotTick(object oTarget, int nDmg, int nTicksLeft)
{{
    if (!GetIsObjectValid(oTarget) || GetIsDead(oTarget) || nTicksLeft <= 0) return;
    ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectDamage(nDmg, DAMAGE_TYPE_DARK_SIDE), oTarget);
    if (nTicksLeft > 1) DelayCommand(6.0, Ov_MentalDotTick(oTarget, nDmg, nTicksLeft - 1));
}}

void Ov_PlagueTick(object oCaster, object oTarget, int nTier, int nTicksLeft)
{{
    if (!GetIsObjectValid(oTarget) || nTicksLeft <= 0) return;
    if (GetIsDead(oTarget))
    {{
        object oNear = GetFirstObjectInShape(SHAPE_SPHERE, 5.0, GetLocation(oTarget), FALSE, OBJECT_TYPE_CREATURE);
        while (GetIsObjectValid(oNear))
        {{
            if (GetIsEnemy(oNear, oCaster) && !GetIsDead(oNear) && GetLocalNumber(oNear, 26) == 0)
            {{
                SetLocalNumber(oNear, 26, 1);
                DelayCommand(0.5, Ov_PlagueTick(oCaster, oNear, nTier, nTicksLeft));
            }}
            oNear = GetNextObjectInShape(SHAPE_SPHERE, 5.0, GetLocation(oTarget), FALSE, OBJECT_TYPE_CREATURE);
        }}
        return;
    }}
    int nLevel = GetHitDice(oCaster);
    int nDC = Ov_GetSpellDC(oCaster, FORCE_POWER_PLAGUE) + ((nTier - 1) * 4);
    if (FortitudeSave(oTarget, nDC, SAVING_THROW_TYPE_POISON, oCaster))
    {{
        Ov_CheckMatukaiPunish(oTarget, oCaster);
        SetLocalNumber(oTarget, 26, 0);
        return;
    }}
    int nTickDmg = nLevel / 2;
    if (nTickDmg < 1) nTickDmg = 1;
    ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectDamage(nTickDmg, DAMAGE_TYPE_DARK_SIDE), oTarget);
    int nPen = nTier * 3;
    effect eDeb = EffectLinkEffects(EffectAbilityDecrease(ABILITY_STRENGTH, nPen), EffectAbilityDecrease(ABILITY_DEXTERITY, nPen));
    eDeb = EffectLinkEffects(eDeb, EffectAbilityDecrease(ABILITY_CONSTITUTION, nPen));
    eDeb = EffectLinkEffects(eDeb, EffectAbilityDecrease(ABILITY_INTELLIGENCE, nPen));
    eDeb = EffectLinkEffects(eDeb, EffectAbilityDecrease(ABILITY_WISDOM, nPen));
    eDeb = EffectLinkEffects(eDeb, EffectAbilityDecrease(ABILITY_CHARISMA, nPen));
    eDeb = EffectLinkEffects(eDeb, EffectMovementSpeedDecrease(50));
    ApplyEffectToObject(DURATION_TYPE_TEMPORARY, eDeb, oTarget, 6.0);
    if (nTicksLeft > 1) DelayCommand(6.0, Ov_PlagueTick(oCaster, oTarget, nTier, nTicksLeft - 1));
    else SetLocalNumber(oTarget, 26, 0);
}}

void Ov_WhirlwindTick(object oTarget, int nTickDmg, int nTicksLeft)
{{
    if (!GetIsObjectValid(oTarget) || GetIsDead(oTarget) || nTicksLeft <= 0) return;
    ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectDamage(nTickDmg, DAMAGE_TYPE_BLUDGEONING), oTarget);
    if (nTicksLeft > 1) DelayCommand(2.0, Ov_WhirlwindTick(oTarget, nTickDmg, nTicksLeft - 1));
}}

void Ov_StasisCheckNext(object oCaster, object oTarget, int nDC, int nRoundsLeft);

void Ov_StasisTick(object oCaster, object oTarget, int nDC, int nRoundsLeft)
{{
    if (!GetIsObjectValid(oTarget) || GetIsDead(oTarget) || nRoundsLeft <= 0) return;
    ApplyEffectToObject(DURATION_TYPE_TEMPORARY, EffectParalyze(), oTarget, 6.0);
    if (nRoundsLeft > 1)
    {{
        int nNextDC = nDC - 3;
        if (nNextDC < 5) nNextDC = 5;
        DelayCommand(6.0, Ov_StasisCheckNext(oCaster, oTarget, nNextDC, nRoundsLeft - 1));
    }}
}}

void Ov_StasisCheckNext(object oCaster, object oTarget, int nDC, int nRoundsLeft)
{{
    if (!GetIsObjectValid(oTarget) || GetIsDead(oTarget) || nRoundsLeft <= 0) return;
    if (FortitudeSave(oTarget, nDC, SAVING_THROW_TYPE_PARALYSIS, oCaster))
    {{
        Ov_CheckMatukaiPunish(oTarget, oCaster);
        return; // Echappe a la stase!
    }}
    Ov_StasisTick(oCaster, oTarget, nDC, nRoundsLeft);
}}

void Ov_StigmateTick(object oCaster, int nTicksLeft)
{{
    if (!GetIsObjectValid(oCaster) || GetIsDead(oCaster) || nTicksLeft <= 0) return;
    int nMaxHP = GetMaxHitPoints(oCaster);
    int nCurHP = GetCurrentHitPoints(oCaster);
    if (nCurHP <= (nMaxHP / 4)) return;
    int nDrain = nMaxHP / 20;
    if (nDrain < 1) nDrain = 1;
    ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectDamage(nDrain, DAMAGE_TYPE_DARK_SIDE), oCaster);
    if (nTicksLeft > 1) DelayCommand(6.0, Ov_StigmateTick(oCaster, nTicksLeft - 1));
}}

void Ov_CicatriceTick(object oCaster, int nPct, int nTicksLeft)
{{
    if (!GetIsObjectValid(oCaster) || GetIsDead(oCaster) || nTicksLeft <= 0) return;
    int nHeal = (GetMaxHitPoints(oCaster) * nPct) / 100;
    if (nHeal < 1) nHeal = 1;
    ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectHeal(nHeal), oCaster);
    if (GetLocalNumber(oCaster, 23) >= 3)
    {{
        int i = 0;
        while (i < 3)
        {{
            object oPM = GetPartyMemberByIndex(i);
            if (GetIsObjectValid(oPM) && !GetIsDead(oPM) && oPM != oCaster)
            {{
                int nHPM = (GetMaxHitPoints(oPM) * nPct) / 100;
                if (nHPM < 1) nHPM = 1;
                ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectHeal(nHPM), oPM);
            }}
            i += 1;
        }}
    }}
    if (nTicksLeft > 1) DelayCommand(6.0, Ov_CicatriceTick(oCaster, nPct, nTicksLeft - 1));
}}

int Ov_HandleCustomPower(int nSpell)
{{
    object oCaster = OBJECT_SELF;
    object oTarget = GetSpellTargetObject();
    int nLevel = GetHitDice(oCaster);
    if (nLevel < 1) nLevel = 1;
    int nDC = Ov_GetSpellDC(oCaster, nSpell);

    // 1. CHOC / FOUDRE (cone 16m!) / TEMPETE DE FORCE (sphere 10m) : 1d6/Niv, Reflexes 1/2, Esquive Totale 0/1/2
    if (nSpell == FORCE_POWER_SHOCK || nSpell == FORCE_POWER_LIGHTNING || nSpell == FORCE_POWER_FORCE_STORM)
    {{
        int nShape = (nSpell == FORCE_POWER_LIGHTNING) ? SHAPE_SPELLCONE : SHAPE_SPHERE;
        float fSize = (nSpell == FORCE_POWER_LIGHTNING) ? 16.0 : ((nSpell == FORCE_POWER_FORCE_STORM) ? 10.0 : 0.0);
        location lLoc = GetSpellTargetLocation();

        object oCur = (fSize > 0.0)
            ? GetFirstObjectInShape(nShape, fSize, lLoc, FALSE, OBJECT_TYPE_CREATURE)
            : oTarget;
        while (GetIsObjectValid(oCur))
        {{
            if (GetIsEnemy(oCur, oCaster) && !GetIsDead(oCur))
            {{
                SignalEvent(oCur, EventSpellCastAt(oCaster, nSpell, TRUE));
                int nDmg = Sp_CalcDamage(oCur, nLevel, 6);
                int bEvasion = GetHasFeat(FEAT_EVASION, oCur);
                int bSaved = ReflexSave(oCur, nDC, SAVING_THROW_TYPE_ELECTRICAL, oCaster);
                if (bSaved)
                {{
                    Ov_CheckMatukaiPunish(oCur, oCaster);
                    if (bEvasion) nDmg = 0;
                    else nDmg = nDmg / 2;
                }}
                else if (bEvasion && fSize > 0.0)
                {{
                    nDmg = nDmg / 2;
                }}
                ApplyEffectToObject(DURATION_TYPE_TEMPORARY, EffectBeam(VFX_BEAM_LIGHTNING_DARK_L, oCaster, BODY_NODE_HAND), oCur, 1.0);
                ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectVisualEffect(VFX_PRO_LIGHTNING_L), oCur);
                if (nDmg > 0) ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectDamage(nDmg, DAMAGE_TYPE_ELECTRICAL), oCur);
            }}
            if (fSize <= 0.0) break;
            oCur = GetNextObjectInShape(nShape, fSize, lLoc, FALSE, OBJECT_TYPE_CREATURE);
        }}
        return TRUE;
    }}

    // 2. TERREUR / HORREUR / INSANITE (DoT mental Niv/rd + -4/-6/-8 Atq, sans stun)
    if (nSpell == FORCE_POWER_FEAR || nSpell == FORCE_POWER_HORROR || nSpell == FORCE_POWER_INSANITY)
    {{
        int nPen = 4;
        float fRad = 0.0;
        if (nSpell == FORCE_POWER_HORROR) {{ nPen = 6; fRad = 5.0; }}
        else if (nSpell == FORCE_POWER_INSANITY) {{ nPen = 8; fRad = 10.0; }}

        object oCur = (fRad > 0.0)
            ? GetFirstObjectInShape(SHAPE_SPHERE, fRad, GetSpellTargetLocation(), FALSE, OBJECT_TYPE_CREATURE)
            : oTarget;
        while (GetIsObjectValid(oCur))
        {{
            if (GetIsEnemy(oCur, oCaster) && !GetIsDead(oCur))
            {{
                SignalEvent(oCur, EventSpellCastAt(oCaster, nSpell, TRUE));
                int bSaved = WillSave(oCur, nDC, SAVING_THROW_TYPE_MIND_AFFECTING, oCaster);
                if (bSaved) Ov_CheckMatukaiPunish(oCur, oCaster);
                int nTicks = bSaved ? 1 : 4;
                float fDur = Sp_CalcDuration(IntToFloat(nTicks * 6));
                ApplyEffectToObject(DURATION_TYPE_TEMPORARY, EffectAttackDecrease(nPen), oCur, fDur);
                Ov_MentalDotTick(oCur, Sp_CalcDamage(oCur, 0, 0, nLevel), nTicks);
            }}
            if (fRad <= 0.0) break;
            oCur = GetNextObjectInShape(SHAPE_SPHERE, fRad, GetSpellTargetLocation(), FALSE, OBJECT_TYPE_CREATURE);
        }}
        return TRUE;
    }}

    // 3. BLESSURE / ETOUFFEMENT / MISE A MORT (1d4 / 1d6+stun / 1d8+stun, Vig 1/2 & annule stun)
    if (nSpell == FORCE_POWER_WOUND || nSpell == FORCE_POWER_CHOKE || nSpell == FORCE_POWER_KILL)
    {{
        if (GetIsObjectValid(oTarget) && !GetIsDead(oTarget))
        {{
            SignalEvent(oTarget, EventSpellCastAt(oCaster, nSpell, TRUE));
            int nDie = (nSpell == FORCE_POWER_WOUND) ? 4 : ((nSpell == FORCE_POWER_CHOKE) ? 6 : 8);
            int nDmg = Sp_CalcDamage(oTarget, nLevel, nDie);
            int bSaved = FortitudeSave(oTarget, nDC, SAVING_THROW_TYPE_NONE, oCaster);
            if (bSaved)
            {{
                Ov_CheckMatukaiPunish(oTarget, oCaster);
                nDmg = nDmg / 2;
            }}
            ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectVisualEffect(VFX_IMP_CHOKE), oTarget);
            ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectDamage(nDmg, DAMAGE_TYPE_DARK_SIDE), oTarget);
            if (!bSaved && (nSpell == FORCE_POWER_CHOKE || nSpell == FORCE_POWER_KILL))
            {{
                ApplyEffectToObject(DURATION_TYPE_TEMPORARY, EffectStunned(), oTarget, 6.0);
            }}
        }}
        return TRUE;
    }}

    // 4. ABSORPTION DE VIE / CHAMP DE MORT / FESTIN DE MORT (L3 dedie!)
    if (nSpell == FORCE_POWER_DRAIN_LIFE || nSpell == FORCE_POWER_DEATH_FIELD || nSpell == OV_SP_DEATH_FEAST)
    {{
        float fRad = (nSpell == FORCE_POWER_DRAIN_LIFE) ? 0.0 : 10.0;
        int nTotalHeal = 0;
        object oCur = (fRad > 0.0)
            ? GetFirstObjectInShape(SHAPE_SPHERE, fRad, GetSpellTargetLocation(), FALSE, OBJECT_TYPE_CREATURE)
            : oTarget;
        while (GetIsObjectValid(oCur))
        {{
            if (GetIsEnemy(oCur, oCaster) && !GetIsDead(oCur) && GetRacialType(oCur) != RACIAL_TYPE_DROID)
            {{
                SignalEvent(oCur, EventSpellCastAt(oCaster, nSpell, TRUE));
                int nDmg = Sp_CalcDamage(oCur, nLevel, 3);
                if (FortitudeSave(oCur, nDC, SAVING_THROW_TYPE_NONE, oCaster))
                {{
                    Ov_CheckMatukaiPunish(oCur, oCaster);
                    nDmg = nDmg / 2;
                }}
                ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectDamage(nDmg, DAMAGE_TYPE_DARK_SIDE), oCur);
                nTotalHeal += nDmg;
            }}
            if (fRad <= 0.0) break;
            oCur = GetNextObjectInShape(SHAPE_SPHERE, fRad, GetSpellTargetLocation(), FALSE, OBJECT_TYPE_CREATURE);
        }}
        if (nTotalHeal > 0)
        {{
            int nMissing = GetMaxHitPoints(oCaster) - GetCurrentHitPoints(oCaster);
            ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectHeal(nTotalHeal), oCaster);
            if (nSpell == OV_SP_DEATH_FEAST && nTotalHeal > nMissing)
            {{
                int nOver = nTotalHeal - nMissing;
                Ov_RemoveTempHP(oCaster);
                ApplyEffectToObject(DURATION_TYPE_TEMPORARY, EffectTemporaryHitpoints(nOver), oCaster, Sp_CalcDuration(24.0));
            }}
        }}
        return TRUE;
    }}

    // 5. LENTEUR / AFFLICTION / PESTE (Maladie contagieuse 42s, tick 6s, -3/-6/-9 caracs, propagation 5m)
    if (nSpell == FORCE_POWER_SLOW || nSpell == FORCE_POWER_AFFLICTION || nSpell == FORCE_POWER_PLAGUE)
    {{
        int nTier = (nSpell == FORCE_POWER_SLOW) ? 1 : ((nSpell == FORCE_POWER_AFFLICTION) ? 2 : 3);
        if (GetIsObjectValid(oTarget) && !GetIsDead(oTarget))
        {{
            SignalEvent(oTarget, EventSpellCastAt(oCaster, nSpell, TRUE));
            SetLocalNumber(oTarget, 26, 1);
            Ov_PlagueTick(oCaster, oTarget, nTier, 7);
        }}
        return TRUE;
    }}

    // 6. TOURBILLON L2 & VAGUE DE FORCE L3 (6 ticks de 1/3 Niv / 2s sur 12s = 2xNiv ; Reflexes reussie = 1xNiv immediat!)
    if (nSpell == FORCE_POWER_FORCE_WHIRLWIND || nSpell == FORCE_POWER_FORCE_WAVE)
    {{
        int bAoE = (nSpell == FORCE_POWER_FORCE_WAVE);
        object oCur = bAoE
            ? GetFirstObjectInShape(SHAPE_SPHERE, 6.0, GetSpellTargetLocation(), FALSE, OBJECT_TYPE_CREATURE)
            : oTarget;
        while (GetIsObjectValid(oCur))
        {{
            if (GetIsEnemy(oCur, oCaster) && !GetIsDead(oCur))
            {{
                SignalEvent(oCur, EventSpellCastAt(oCaster, nSpell, TRUE));
                int nHalfDmg = Sp_CalcDamage(oCur, 0, 0, nLevel);
                int nTickDmg = Sp_CalcDamage(oCur, 0, 0, nLevel) / 3;
                if (nTickDmg < 1) nTickDmg = 1;
                int bEvasion = GetHasFeat(FEAT_EVASION, oCur);
                if (ReflexSave(oCur, nDC, SAVING_THROW_TYPE_NONE, oCaster))
                {{
                    Ov_CheckMatukaiPunish(oCur, oCaster);
                    if (!(bAoE && bEvasion))
                    {{
                        ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectDamage(nHalfDmg, DAMAGE_TYPE_BLUDGEONING), oCur);
                    }}
                }}
                else
                {{
                    if (bAoE && bEvasion) nTickDmg = (nTickDmg + 1) / 2;
                    float fDur = Sp_CalcDuration(12.0);
                    int nTicks = FloatToInt(fDur / 2.0);
                    if (nTicks < 1) nTicks = 6;
                    effect eWhirl = EffectLinkEffects(EffectWhirlWind(), EffectVisualEffect(VFX_IMP_FORCE_WHIRLWIND));
                    ApplyEffectToObject(DURATION_TYPE_TEMPORARY, eWhirl, oCur, fDur);
                    Ov_WhirlwindTick(oCur, nTickDmg, nTicks);
                }}
            }}
            if (!bAoE) break;
            oCur = GetNextObjectInShape(SHAPE_SPHERE, 6.0, GetSpellTargetLocation(), FALSE, OBJECT_TYPE_CREATURE);
        }}
        return TRUE;
    }}

    // 7. BARRIERE DE FORCE & RESISTANCE A L'ENERGIE (CORRIGE : 42 = L1 RD 4, 40 = L2 RD 8, 133 = L3 RD 12!)
    if (nSpell == FORCE_POWER_FORCE_BARRIER || nSpell == FORCE_POWER_IMPROVED_FORCE_BARRIER || nSpell == FORCE_POWER_MASTER_FORCE_BARRIER)
    {{
        int nRD = (nSpell == FORCE_POWER_FORCE_BARRIER) ? 4 : ((nSpell == FORCE_POWER_IMPROVED_FORCE_BARRIER) ? 8 : 12);
        effect eB = EffectLinkEffects(EffectDamageResistance(DAMAGE_TYPE_BLUDGEONING, nRD), EffectDamageResistance(DAMAGE_TYPE_PIERCING, nRD));
        eB = EffectLinkEffects(eB, EffectDamageResistance(DAMAGE_TYPE_SLASHING, nRD));
        float fDur = Sp_CalcDuration(60.0);
        ApplyEffectToObject(DURATION_TYPE_TEMPORARY, eB, oCaster, fDur);
        Ov_MirrorBuffViaEcho(oCaster, eB, fDur);
        return TRUE;
    }}
    if (nSpell == FORCE_POWER_RESIST_POISON_DISEASE_SONIC || nSpell == FORCE_POWER_RESIST_COLD_HEAT_ENERGY || nSpell == FORCE_POWER_MASTER_ENERGY_RESISTANCE)
    {{
        // nwscript.nss : 42 (RESIST_POISON_DISEASE_SONIC) = RESIST_ENERGY_1 (L1) ; 40 (RESIST_COLD_HEAT_ENERGY) = RESIST_ENERGY_2 (L2)
        int nRD = (nSpell == FORCE_POWER_RESIST_POISON_DISEASE_SONIC) ? 4 : ((nSpell == FORCE_POWER_RESIST_COLD_HEAT_ENERGY) ? 8 : 12);
        effect eE = EffectLinkEffects(EffectDamageResistance(DAMAGE_TYPE_BLASTER, nRD), EffectDamageResistance(DAMAGE_TYPE_FIRE, nRD));
        eE = EffectLinkEffects(eE, EffectDamageResistance(DAMAGE_TYPE_COLD, nRD));
        eE = EffectLinkEffects(eE, EffectDamageResistance(DAMAGE_TYPE_ELECTRICAL, nRD));
        eE = EffectLinkEffects(eE, EffectDamageResistance(DAMAGE_TYPE_SONIC, nRD));
        float fDur = Sp_CalcDuration(60.0);
        ApplyEffectToObject(DURATION_TYPE_TEMPORARY, eE, oCaster, fDur);
        Ov_MirrorBuffViaEcho(oCaster, eE, fDur);
        return TRUE;
    }}

    // 8. TALENT DE FORCE (+2/+3/+4 aux 6 caracs groupe + immunite Poison L2/L3)
    if (nSpell == FORCE_POWER_FORCE_MIND || nSpell == FORCE_POWER_KNIGHT_MIND || nSpell == FORCE_POWER_MIND_MASTERY)
    {{
        int nBon = (nSpell == FORCE_POWER_FORCE_MIND) ? 2 : ((nSpell == FORCE_POWER_KNIGHT_MIND) ? 3 : 4);
        effect eV = EffectLinkEffects(EffectAbilityIncrease(ABILITY_STRENGTH, nBon), EffectAbilityIncrease(ABILITY_DEXTERITY, nBon));
        eV = EffectLinkEffects(eV, EffectAbilityIncrease(ABILITY_CONSTITUTION, nBon));
        eV = EffectLinkEffects(eV, EffectAbilityIncrease(ABILITY_INTELLIGENCE, nBon));
        eV = EffectLinkEffects(eV, EffectAbilityIncrease(ABILITY_WISDOM, nBon));
        eV = EffectLinkEffects(eV, EffectAbilityIncrease(ABILITY_CHARISMA, nBon));
        if (nBon >= 3) eV = EffectLinkEffects(eV, EffectImmunity(IMMUNITY_TYPE_POISON));
        float fDur = Sp_CalcDuration(20.0);
        int i = 0;
        while (i < 3)
        {{
            object oPM = GetPartyMemberByIndex(i);
            if (GetIsObjectValid(oPM) && !GetIsDead(oPM)) ApplyEffectToObject(DURATION_TYPE_TEMPORARY, eV, oPM, fDur);
            i += 1;
        }}
        return TRUE;
    }}

    // 9. REVITALISATION I-III (10% 1 allie / 20% 2 allies / 30% tout le groupe)
    if (nSpell == 173 || nSpell == 174 || nSpell == 175)
    {{
        int nPct = (nSpell == 173) ? 10 : ((nSpell == 174) ? 20 : 30);
        int nMaxRev = (nSpell == 173) ? 1 : ((nSpell == 174) ? 2 : 3);
        int nRevived = 0;
        int i = 0;
        while (i < 3 && nRevived < nMaxRev)
        {{
            object oPM = GetPartyMemberByIndex(i);
            if (GetIsObjectValid(oPM) && GetIsDead(oPM))
            {{
                ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectResurrection(), oPM);
                int nH = (GetMaxHitPoints(oPM) * nPct) / 100;
                if (nH < 1) nH = 1;
                ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectHeal(nH), oPM);
                ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectVisualEffect(VFX_IMP_CURE), oPM);
                nRevived += 1;
            }}
            i += 1;
        }}
        if (nSpell == 175)
        {{
            i = 0;
            while (i < 3)
            {{
                object oPM = GetPartyMemberByIndex(i);
                if (GetIsObjectValid(oPM) && !GetIsDead(oPM))
                {{
                    int nH = (GetMaxHitPoints(oPM) * 30) / 100;
                    if (nH > 0) ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectHeal(nH), oPM);
                }}
                i += 1;
            }}
        }}
        return TRUE;
    }}

    // 10. CHAMP DE STASE L3 (zone 10m, max 36s / 6 rounds avec jet de Vigueur chaque round a DD -3/rd)
    if (nSpell == FORCE_POWER_SLEEP)
    {{
        object oCur = GetFirstObjectInShape(SHAPE_SPHERE, 10.0, GetSpellTargetLocation(), FALSE, OBJECT_TYPE_CREATURE);
        while (GetIsObjectValid(oCur))
        {{
            if (GetIsEnemy(oCur, oCaster) && !GetIsDead(oCur) && GetRacialType(oCur) != RACIAL_TYPE_DROID)
            {{
                SignalEvent(oCur, EventSpellCastAt(oCaster, nSpell, TRUE));
                if (FortitudeSave(oCur, nDC, SAVING_THROW_TYPE_PARALYSIS, oCaster))
                {{
                    Ov_CheckMatukaiPunish(oCur, oCaster);
                    effect eSl = EffectLinkEffects(EffectMovementSpeedDecrease(50), EffectACDecrease(2));
                    eSl = EffectLinkEffects(eSl, EffectAttackDecrease(2));
                    eSl = EffectLinkEffects(eSl, EffectSavingThrowDecrease(SAVING_THROW_REFLEX, 2));
                    ApplyEffectToObject(DURATION_TYPE_TEMPORARY, eSl, oCur, Sp_CalcDuration(12.0));
                }}
                else
                {{
                    Ov_StasisTick(oCaster, oCur, nDC, 6);
                }}
            }}
            oCur = GetNextObjectInShape(SHAPE_SPHERE, 10.0, GetSpellTargetLocation(), FALSE, OBJECT_TYPE_CREATURE);
        }}
        return TRUE;
    }}

    // 11. MEDITATION DE COMBAT I-III (+mod. CHA groupe, -mod. CHA ennemis 10m L2, +/- (mod. CHA + 2) 15m L3)
    if (nSpell == 138 || nSpell == 139 || nSpell == 140)
    {{
        int nCha = GetAbilityModifier(ABILITY_CHARISMA, oCaster);
        if (nCha < 1) nCha = 1;
        int nBon = (nSpell == 140) ? (nCha + 2) : nCha;
        float fDur = Sp_CalcDuration(20.0);
        effect eB = EffectLinkEffects(EffectAttackIncrease(nBon), EffectDamageIncrease(nBon, DAMAGE_TYPE_UNIVERSAL));
        eB = EffectLinkEffects(eB, EffectSavingThrowIncrease(SAVING_THROW_WILL, nBon));
        eB = EffectLinkEffects(eB, EffectRegenerate(2, 6.0));
        int i = 0;
        while (i < 3)
        {{
            object oPM = GetPartyMemberByIndex(i);
            if (GetIsObjectValid(oPM) && !GetIsDead(oPM)) ApplyEffectToObject(DURATION_TYPE_TEMPORARY, eB, oPM, fDur);
            i += 1;
        }}
        if (nSpell == 139 || nSpell == 140)
        {{
            float fRad = (nSpell == 140) ? 15.0 : 10.0;
            effect eD = EffectLinkEffects(EffectAttackDecrease(nBon), EffectDamageDecrease(nBon, DAMAGE_TYPE_UNIVERSAL));
            eD = EffectLinkEffects(eD, EffectSavingThrowDecrease(SAVING_THROW_WILL, nBon));
            object oCur = GetFirstObjectInShape(SHAPE_SPHERE, fRad, GetLocation(oCaster), FALSE, OBJECT_TYPE_CREATURE);
            while (GetIsObjectValid(oCur))
            {{
                if (GetIsEnemy(oCur, oCaster) && !GetIsDead(oCur))
                {{
                    SignalEvent(oCur, EventSpellCastAt(oCaster, nSpell, TRUE));
                    if (!WillSave(oCur, nDC, SAVING_THROW_TYPE_MIND_AFFECTING, oCaster))
                    {{
                        ApplyEffectToObject(DURATION_TYPE_TEMPORARY, eD, oCur, fDur);
                    }}
                    else Ov_CheckMatukaiPunish(oCur, oCaster);
                }}
                oCur = GetNextObjectInShape(SHAPE_SPHERE, fRad, GetLocation(oCaster), FALSE, OBJECT_TYPE_CREATURE);
            }}
        }}
        return TRUE;
    }}

    // 12. LANCER DE SABRE LASER L1/L2 (1d4/Niv ; L1 Renversement Vig ; L2 3 cibles + ignore RD via ACID/Unstoppable)
    if (nSpell == FORCE_POWER_LIGHT_SABER_THROW || nSpell == FORCE_POWER_LIGHT_SABER_THROW_ADVANCED)
    {{
        if (GetIsObjectValid(oTarget) && !GetIsDead(oTarget))
        {{
            int bAdv = (nSpell == FORCE_POWER_LIGHT_SABER_THROW_ADVANCED);
            int nDmgType = bAdv ? DAMAGE_TYPE_ACID : DAMAGE_TYPE_BLASTER;
            object oT2 = OBJECT_INVALID;
            object oT3 = OBJECT_INVALID;
            if (bAdv)
            {{
                object oN = GetFirstObjectInShape(SHAPE_SPHERE, 5.0, GetLocation(oTarget), FALSE, OBJECT_TYPE_CREATURE);
                while (GetIsObjectValid(oN))
                {{
                    if (oN != oTarget && GetIsEnemy(oN, oCaster) && !GetIsDead(oN))
                    {{
                        if (!GetIsObjectValid(oT2)) oT2 = oN;
                        else if (!GetIsObjectValid(oT3)) {{ oT3 = oN; break; }}
                    }}
                    oN = GetNextObjectInShape(SHAPE_SPHERE, 5.0, GetLocation(oTarget), FALSE, OBJECT_TYPE_CREATURE);
                }}
            }}
            ApplyEffectToObject(DURATION_TYPE_TEMPORARY, EffectLightsaberThrow(oTarget, oT2, oT3, 0), oCaster, 1.5);

            SignalEvent(oTarget, EventSpellCastAt(oCaster, nSpell, TRUE));
            ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectDamage(Sp_CalcDamage(oTarget, nLevel, 4), nDmgType), oTarget);
            if (!bAdv)
            {{
                if (!FortitudeSave(oTarget, nDC, SAVING_THROW_TYPE_NONE, oCaster))
                    ApplyEffectToObject(DURATION_TYPE_TEMPORARY, EffectKnockdown(), oTarget, 6.0);
                else Ov_CheckMatukaiPunish(oTarget, oCaster);
            }}
            if (GetIsObjectValid(oT2))
            {{
                SignalEvent(oT2, EventSpellCastAt(oCaster, nSpell, TRUE));
                ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectDamage(Sp_CalcDamage(oT2, nLevel, 4), nDmgType), oT2);
            }}
            if (GetIsObjectValid(oT3))
            {{
                SignalEvent(oT3, EventSpellCastAt(oCaster, nSpell, TRUE));
                ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectDamage(Sp_CalcDamage(oT3, nLevel, 4), nDmgType), oT3);
            }}
        }}
        return TRUE;
    }}

    // 13. ABSORPTION DE FORCE I-III (15/30/45 + Niv PF + moitie en degats directs aux utilisateurs de Force)
    if (nSpell == 153 || nSpell == 154 || nSpell == 155)
    {{
        int nBaseDrain = (nSpell == 153) ? 15 : ((nSpell == 154) ? 30 : 45);
        float fRad = (nSpell == 155) ? 10.0 : 0.0;
        int nTotalGain = 0;
        object oCur = (fRad > 0.0)
            ? GetFirstObjectInShape(SHAPE_SPHERE, fRad, GetSpellTargetLocation(), FALSE, OBJECT_TYPE_CREATURE)
            : oTarget;
        while (GetIsObjectValid(oCur))
        {{
            if (GetIsEnemy(oCur, oCaster) && !GetIsDead(oCur))
            {{
                SignalEvent(oCur, EventSpellCastAt(oCaster, nSpell, TRUE));
                int nDr = nBaseDrain + nLevel;
                if (WillSave(oCur, nDC, SAVING_THROW_TYPE_MIND_AFFECTING, oCaster))
                {{
                    Ov_CheckMatukaiPunish(oCur, oCaster);
                    nDr = nDr / 2;
                }}
                if (nDr > 0)
                {{
                    ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectDamageForcePoints(nDr), oCur);
                    nTotalGain += nDr;
                    if (GetMaxForcePoints(oCur) > 0)
                    {{
                        int nHPDirect = Sp_CalcDamage(oCur, 0, 0, nDr / 2);
                        if (nHPDirect > 0) ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectDamage(nHPDirect, DAMAGE_TYPE_DARK_SIDE), oCur);
                    }}
                }}
            }}
            if (fRad <= 0.0) break;
            oCur = GetNextObjectInShape(SHAPE_SPHERE, fRad, GetSpellTargetLocation(), FALSE, OBJECT_TYPE_CREATURE);
        }}
        if (nTotalGain > 0) ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectHealForcePoints(nTotalGain), oCaster);
        return TRUE;
    }}

    // 14. CRI DE FORCE I-III (1d3/Niv -2 ; 1d4/Niv -4 ; 1d4/Niv sans cap -6 ; Volonte 1/2 & annule malus)
    if (nSpell == 159 || nSpell == 160 || nSpell == 161)
    {{
        int nDie = (nSpell == 159) ? 3 : 4;
        int nPen = (nSpell == 159) ? 2 : ((nSpell == 160) ? 4 : 6);
        int nShape = (nSpell == 161) ? SHAPE_SPHERE : SHAPE_SPELLCONE;
        float fSize = (nSpell == 161) ? 12.0 : 10.0;
        location lLoc = GetSpellTargetLocation();
        float fDur = Sp_CalcDuration(30.0);
        effect ePen = EffectLinkEffects(EffectAbilityDecrease(ABILITY_STRENGTH, nPen), EffectAbilityDecrease(ABILITY_DEXTERITY, nPen));
        ePen = EffectLinkEffects(ePen, EffectAbilityDecrease(ABILITY_CONSTITUTION, nPen));
        ePen = EffectLinkEffects(ePen, EffectAbilityDecrease(ABILITY_INTELLIGENCE, nPen));
        ePen = EffectLinkEffects(ePen, EffectAbilityDecrease(ABILITY_WISDOM, nPen));
        ePen = EffectLinkEffects(ePen, EffectAbilityDecrease(ABILITY_CHARISMA, nPen));

        object oCur = GetFirstObjectInShape(nShape, fSize, lLoc, FALSE, OBJECT_TYPE_CREATURE);
        while (GetIsObjectValid(oCur))
        {{
            if (GetIsEnemy(oCur, oCaster) && !GetIsDead(oCur))
            {{
                SignalEvent(oCur, EventSpellCastAt(oCaster, nSpell, TRUE));
                int nDmg = Sp_CalcDamage(oCur, nLevel, nDie);
                int bEvasion = GetHasFeat(FEAT_EVASION, oCur);
                if (WillSave(oCur, nDC, SAVING_THROW_TYPE_SONIC, oCaster))
                {{
                    Ov_CheckMatukaiPunish(oCur, oCaster);
                    nDmg = bEvasion ? 0 : (nDmg / 2);
                }}
                else
                {{
                    if (bEvasion) nDmg = nDmg / 2;
                    ApplyEffectToObject(DURATION_TYPE_TEMPORARY, ePen, oCur, fDur);
                }}
                if (nDmg > 0) ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectDamage(nDmg, DAMAGE_TYPE_SONIC), oCur);
            }}
            oCur = GetNextObjectInShape(nShape, fSize, lLoc, FALSE, OBJECT_TYPE_CREATURE);
        }}
        return TRUE;
    }}

    // 15. GRACE DU COTE LUMINEUX (lancer instantane + Vitesse plafonnee +1 atq/rd sous armure)
    if (nSpell == FORCE_POWER_FORCE_ENLIGHTENMENT)
    {{
        int nArmTier = Ov_GetArmorTier(oCaster);
        // Vitesse (plafonnee a +1 atq/rd si une armure est portee ; +2 uniquement en Robe)
        if (GetHasSpell(FORCE_POWER_SPEED_MASTERY, oCaster) || GetHasSpell(FORCE_POWER_KNIGHT_SPEED, oCaster) || GetHasSpell(FORCE_POWER_SPEED_BURST, oCaster))
        {{
            int nSpAC = GetHasSpell(FORCE_POWER_KNIGHT_SPEED, oCaster) ? 4 : 2;
            int nSpAtq = 0;
            if (GetHasSpell(FORCE_POWER_SPEED_MASTERY, oCaster)) nSpAtq = (nArmTier == 0) ? 2 : 1;
            else if (GetHasSpell(FORCE_POWER_KNIGHT_SPEED, oCaster)) nSpAtq = 1;
            effect eSp = EffectLinkEffects(EffectMovementSpeedIncrease(99), EffectACIncrease(nSpAC, AC_DODGE_BONUS));
            if (nSpAtq > 0) eSp = EffectLinkEffects(eSp, EffectModifyAttacks(nSpAtq));
            float fSpDur = Sp_CalcDuration(36.0);
            ApplyEffectToObject(DURATION_TYPE_TEMPORARY, eSp, oCaster, fSpDur);
            Ov_MirrorBuffViaEcho(oCaster, eSp, fSpDur);
        }}
        // Armure de Force
        if (GetHasSpell(FORCE_POWER_FORCE_ARMOR, oCaster) || GetHasSpell(FORCE_POWER_FORCE_SHIELD, oCaster) || GetHasSpell(FORCE_POWER_FORCE_AURA, oCaster))
        {{
            int nAr = GetHasSpell(FORCE_POWER_FORCE_ARMOR, oCaster) ? 6 : (GetHasSpell(FORCE_POWER_FORCE_SHIELD, oCaster) ? 4 : 2);
            effect eAr = EffectLinkEffects(EffectACIncrease(nAr, AC_DODGE_BONUS), EffectSavingThrowIncrease(SAVING_THROW_ALL, nAr));
            float fArDur = Sp_CalcDuration(20.0);
            ApplyEffectToObject(DURATION_TYPE_TEMPORARY, eAr, oCaster, fArDur);
            Ov_MirrorBuffViaEcho(oCaster, eAr, fArDur);
        }}
        // Talent de Force (+2/+3/+4)
        if (GetHasSpell(FORCE_POWER_MIND_MASTERY, oCaster) || GetHasSpell(FORCE_POWER_KNIGHT_MIND, oCaster) || GetHasSpell(FORCE_POWER_FORCE_MIND, oCaster))
        {{
            int nVal = GetHasSpell(FORCE_POWER_MIND_MASTERY, oCaster) ? 4 : (GetHasSpell(FORCE_POWER_KNIGHT_MIND, oCaster) ? 3 : 2);
            effect eV = EffectLinkEffects(EffectAbilityIncrease(ABILITY_STRENGTH, nVal), EffectAbilityIncrease(ABILITY_DEXTERITY, nVal));
            eV = EffectLinkEffects(eV, EffectAbilityIncrease(ABILITY_CONSTITUTION, nVal));
            eV = EffectLinkEffects(eV, EffectAbilityIncrease(ABILITY_INTELLIGENCE, nVal));
            eV = EffectLinkEffects(eV, EffectAbilityIncrease(ABILITY_WISDOM, nVal));
            eV = EffectLinkEffects(eV, EffectAbilityIncrease(ABILITY_CHARISMA, nVal));
            if (nVal >= 3) eV = EffectLinkEffects(eV, EffectImmunity(IMMUNITY_TYPE_POISON));
            float fValDur = Sp_CalcDuration(20.0);
            int i = 0;
            while (i < 3)
            {{
                object oPM = GetPartyMemberByIndex(i);
                if (GetIsObjectValid(oPM) && !GetIsDead(oPM)) ApplyEffectToObject(DURATION_TYPE_TEMPORARY, eV, oPM, fValDur);
                i += 1;
            }}
        }}
        return TRUE;
    }}

    // 16. ECHO DES LIENS I-III (partage buffs personnels + soins L3, sans restriction d'armure sur allies)
    if (nSpell == FORCE_POWER_INSPIRE_FOLLOWERS_I || nSpell == FORCE_POWER_INSPIRE_FOLLOWERS_II || nSpell == FORCE_POWER_INSPIRE_FOLLOWERS_III)
    {{
        int nTier = (nSpell == FORCE_POWER_INSPIRE_FOLLOWERS_I) ? 1 : ((nSpell == FORCE_POWER_INSPIRE_FOLLOWERS_II) ? 2 : 3);
        float fBase = (nTier == 1) ? 30.0 : ((nTier == 2) ? 45.0 : 60.0);
        float fDur = Sp_CalcDuration(fBase);
        SetLocalNumber(oCaster, 23, nTier);
        DelayCommand(fDur, Ov_ResetEchoLinks(oCaster));

        // Recopier immediatement les buffs personnels deja actifs sur le lanceur vers l'allie/le groupe
        if (GetHasSpellEffect(FORCE_POWER_SPEED_MASTERY, oCaster))
            Ov_MirrorBuffViaEcho(oCaster, EffectLinkEffects(EffectMovementSpeedIncrease(99), EffectModifyAttacks(2)), fDur);
        else if (GetHasSpellEffect(FORCE_POWER_KNIGHT_SPEED, oCaster))
            Ov_MirrorBuffViaEcho(oCaster, EffectLinkEffects(EffectMovementSpeedIncrease(99), EffectModifyAttacks(1)), fDur);
        else if (GetHasSpellEffect(FORCE_POWER_SPEED_BURST, oCaster))
            Ov_MirrorBuffViaEcho(oCaster, EffectMovementSpeedIncrease(99), fDur);

        if (GetHasSpellEffect(FORCE_POWER_FORCE_ARMOR, oCaster))
            Ov_MirrorBuffViaEcho(oCaster, EffectLinkEffects(EffectACIncrease(6, AC_DODGE_BONUS), EffectSavingThrowIncrease(SAVING_THROW_ALL, 6)), fDur);
        else if (GetHasSpellEffect(FORCE_POWER_FORCE_SHIELD, oCaster))
            Ov_MirrorBuffViaEcho(oCaster, EffectLinkEffects(EffectACIncrease(4, AC_DODGE_BONUS), EffectSavingThrowIncrease(SAVING_THROW_ALL, 4)), fDur);
        else if (GetHasSpellEffect(FORCE_POWER_FORCE_AURA, oCaster))
            Ov_MirrorBuffViaEcho(oCaster, EffectLinkEffects(EffectACIncrease(2, AC_DODGE_BONUS), EffectSavingThrowIncrease(SAVING_THROW_ALL, 2)), fDur);

        if (GetHasSpellEffect(FORCE_POWER_MASTER_FORCE_BARRIER, oCaster) || GetHasSpellEffect(FORCE_POWER_IMPROVED_FORCE_BARRIER, oCaster) || GetHasSpellEffect(FORCE_POWER_FORCE_BARRIER, oCaster))
        {{
            int nRD = GetHasSpellEffect(FORCE_POWER_MASTER_FORCE_BARRIER, oCaster) ? 12 : (GetHasSpellEffect(FORCE_POWER_IMPROVED_FORCE_BARRIER, oCaster) ? 8 : 4);
            effect eB = EffectLinkEffects(EffectDamageResistance(DAMAGE_TYPE_BLUDGEONING, nRD), EffectDamageResistance(DAMAGE_TYPE_PIERCING, nRD));
            eB = EffectLinkEffects(eB, EffectDamageResistance(DAMAGE_TYPE_SLASHING, nRD));
            Ov_MirrorBuffViaEcho(oCaster, eB, fDur);
        }}
        if (GetHasSpellEffect(FORCE_POWER_MASTER_ENERGY_RESISTANCE, oCaster) || GetHasSpellEffect(FORCE_POWER_RESIST_COLD_HEAT_ENERGY, oCaster) || GetHasSpellEffect(FORCE_POWER_RESIST_POISON_DISEASE_SONIC, oCaster))
        {{
            int nRD = GetHasSpellEffect(FORCE_POWER_MASTER_ENERGY_RESISTANCE, oCaster) ? 12 : (GetHasSpellEffect(FORCE_POWER_RESIST_COLD_HEAT_ENERGY, oCaster) ? 8 : 4);
            effect eE = EffectLinkEffects(EffectDamageResistance(DAMAGE_TYPE_BLASTER, nRD), EffectDamageResistance(DAMAGE_TYPE_FIRE, nRD));
            eE = EffectLinkEffects(eE, EffectDamageResistance(DAMAGE_TYPE_COLD, nRD));
            eE = EffectLinkEffects(eE, EffectDamageResistance(DAMAGE_TYPE_ELECTRICAL, nRD));
            eE = EffectLinkEffects(eE, EffectDamageResistance(DAMAGE_TYPE_SONIC, nRD));
            Ov_MirrorBuffViaEcho(oCaster, eE, fDur);
        }}
        ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectVisualEffect(VFX_IMP_CURE), oCaster);
        return TRUE;
    }}

    // 17. CICATRICE DE FORCE I-III (Maitre d'Armes : soin 2/4/6% PV max/rd + +1/+2/+3 saves + imm. Peur/Stun L2, Paralysie L3)
    if (nSpell == OV_SP_SCAR_1 || nSpell == OV_SP_SCAR_2 || nSpell == OV_SP_SCAR_3)
    {{
        int nTier = (nSpell == OV_SP_SCAR_1) ? 1 : ((nSpell == OV_SP_SCAR_2) ? 2 : 3);
        int nPct = nTier * 2;
        effect eSc = EffectSavingThrowIncrease(SAVING_THROW_ALL, nTier);
        if (nTier >= 2)
        {{
            eSc = EffectLinkEffects(eSc, EffectImmunity(IMMUNITY_TYPE_FEAR));
            eSc = EffectLinkEffects(eSc, EffectImmunity(IMMUNITY_TYPE_STUN));
        }}
        if (nTier >= 3)
        {{
            eSc = EffectLinkEffects(eSc, EffectImmunity(IMMUNITY_TYPE_PARALYSIS));
        }}
        float fDur = Sp_CalcDuration(30.0);
        int nTicks = FloatToInt(fDur / 6.0);
        if (nTicks < 1) nTicks = 5;
        ApplyEffectToObject(DURATION_TYPE_TEMPORARY, eSc, oCaster, fDur);
        Ov_MirrorBuffViaEcho(oCaster, eSc, fDur);
        Ov_CicatriceTick(oCaster, nPct, nTicks);
        return TRUE;
    }}

    // 18. STIGMATE DE FORCE I-III (anti-cumul Vitesse + ticks dynamiques sur duree prolongee!)
    if (nSpell == FORCE_POWER_FURY || nSpell == FORCE_POWER_IMPROVED_FURY || nSpell == FORCE_POWER_MASTER_FURY)
    {{
        int nBon = (nSpell == FORCE_POWER_FURY) ? 2 : ((nSpell == FORCE_POWER_IMPROVED_FURY) ? 4 : 6);
        effect eF = EffectLinkEffects(EffectAbilityIncrease(ABILITY_STRENGTH, nBon), EffectAbilityIncrease(ABILITY_DEXTERITY, nBon));
        if (!GetHasSpellEffect(FORCE_POWER_KNIGHT_SPEED, oCaster) && !GetHasSpellEffect(FORCE_POWER_SPEED_MASTERY, oCaster))
        {{
            eF = EffectLinkEffects(eF, EffectModifyAttacks(1));
        }}
        eF = EffectLinkEffects(eF, EffectImmunity(IMMUNITY_TYPE_PARALYSIS));
        float fDur = Sp_CalcDuration(30.0);
        int nTicks = FloatToInt(fDur / 6.0);
        if (nTicks < 1) nTicks = 5;
        ApplyEffectToObject(DURATION_TYPE_TEMPORARY, eF, oCaster, fDur);
        Ov_MirrorBuffViaEcho(oCaster, eF, fDur);
        DelayCommand(6.0, Ov_StigmateTick(oCaster, nTicks));
        return TRUE;
    }}

    // 19. ECRASEMENT DE FORCE (1d8/Niv degats purs ACID/Unstoppable ignorent RD & elem + Paralysie 6s)
    if (nSpell == FORCE_POWER_FORCE_CRUSH)
    {{
        if (GetIsObjectValid(oTarget) && !GetIsDead(oTarget))
        {{
            SignalEvent(oTarget, EventSpellCastAt(oCaster, nSpell, TRUE));
            int nDmg = Sp_CalcDamage(oTarget, nLevel, 8);
            int bSaved = FortitudeSave(oTarget, nDC, SAVING_THROW_TYPE_NONE, oCaster);
            if (bSaved)
            {{
                Ov_CheckMatukaiPunish(oTarget, oCaster);
                nDmg = nDmg / 2;
            }}
            ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectDamage(nDmg, DAMAGE_TYPE_ACID), oTarget);
            if (!bSaved) ApplyEffectToObject(DURATION_TYPE_TEMPORARY, EffectParalyze(), oTarget, 6.0);
        }}
        return TRUE;
    }}

    // 20. DECHIRURE DE LA FORCE I-III (-2/-4/-6 Atq, CA, Saves, 15m, 45s, Volonte annule)
    if (nSpell == FORCE_POWER_CRUSH_OPPOSITION_I || nSpell == FORCE_POWER_CRUSH_OPPOSITION_II || nSpell == FORCE_POWER_CRUSH_OPPOSITION_III)
    {{
        int nPen = (nSpell == FORCE_POWER_CRUSH_OPPOSITION_I) ? 2 : ((nSpell == FORCE_POWER_CRUSH_OPPOSITION_II) ? 4 : 6);
        effect eD = EffectLinkEffects(EffectAttackDecrease(nPen), EffectACDecrease(nPen));
        eD = EffectLinkEffects(eD, EffectSavingThrowDecrease(SAVING_THROW_ALL, nPen));
        float fDur = Sp_CalcDuration(45.0);
        object oCur = GetFirstObjectInShape(SHAPE_SPHERE, 15.0, GetLocation(oCaster), FALSE, OBJECT_TYPE_CREATURE);
        while (GetIsObjectValid(oCur))
        {{
            if (GetIsEnemy(oCur, oCaster) && !GetIsDead(oCur))
            {{
                SignalEvent(oCur, EventSpellCastAt(oCaster, nSpell, TRUE));
                if (!WillSave(oCur, nDC, SAVING_THROW_TYPE_MIND_AFFECTING, oCaster))
                {{
                    ApplyEffectToObject(DURATION_TYPE_TEMPORARY, eD, oCur, fDur);
                }}
                else Ov_CheckMatukaiPunish(oCur, oCaster);
            }}
            oCur = GetNextObjectInShape(SHAPE_SPHERE, 15.0, GetLocation(oCaster), FALSE, OBJECT_TYPE_CREATURE);
        }}
        return TRUE;
    }}

    // 21. Echo des Liens actif : miroir automatique des buffs personnels vanilla (Vitesse, Aura/Bouclier/Armure)
    if (GetLocalNumber(oCaster, 23) > 0)
    {{
        if (nSpell == FORCE_POWER_SPEED_MASTERY)
            Ov_MirrorBuffViaEcho(oCaster, EffectLinkEffects(EffectMovementSpeedIncrease(99), EffectModifyAttacks(2)), Sp_CalcDuration(36.0));
        else if (nSpell == FORCE_POWER_KNIGHT_SPEED)
            Ov_MirrorBuffViaEcho(oCaster, EffectLinkEffects(EffectMovementSpeedIncrease(99), EffectModifyAttacks(1)), Sp_CalcDuration(36.0));
        else if (nSpell == FORCE_POWER_SPEED_BURST)
            Ov_MirrorBuffViaEcho(oCaster, EffectMovementSpeedIncrease(99), Sp_CalcDuration(36.0));
        else if (nSpell == FORCE_POWER_FORCE_ARMOR)
            Ov_MirrorBuffViaEcho(oCaster, EffectLinkEffects(EffectACIncrease(6, AC_DODGE_BONUS), EffectSavingThrowIncrease(SAVING_THROW_ALL, 6)), Sp_CalcDuration(20.0));
        else if (nSpell == FORCE_POWER_FORCE_SHIELD)
            Ov_MirrorBuffViaEcho(oCaster, EffectLinkEffects(EffectACIncrease(4, AC_DODGE_BONUS), EffectSavingThrowIncrease(SAVING_THROW_ALL, 4)), Sp_CalcDuration(20.0));
        else if (nSpell == FORCE_POWER_FORCE_AURA)
            Ov_MirrorBuffViaEcho(oCaster, EffectLinkEffects(EffectACIncrease(2, AC_DODGE_BONUS), EffectSavingThrowIncrease(SAVING_THROW_ALL, 2)), Sp_CalcDuration(20.0));
    }}

    return FALSE;
}}
'''
    (SRC_DIR / "ov_inc_powers.nss").write_text(code, encoding="latin1")
    return code


def build_force_powers(fids: dict[str, int], sids: dict[str, int]) -> None:
    """Patch k_inc_force.nss (Metamagie, Cristal Maitre Jedi/Seigneur Sith, Corps de Force DD,
    Matukai II punition, Esquive Totale 1/2 sur echec) et compile k_sp1_generic.ncs."""
    inc = (REF_SCRIPTS / "k_inc_force.nss").read_text(encoding="latin1")

    emp1, emp2, emp3 = fids["MOD_META_EMPOWER_1"], fids["MOD_META_EMPOWER_2"], fids["MOD_META_EMPOWER_3"]
    pen1, pen2, pen3 = fids["MOD_META_PENETRATE_1"], fids["MOD_META_PENETRATE_2"], fids["MOD_META_PENETRATE_3"]
    ext1 = fids["MOD_META_EXTEND"]
    mat2 = fids["MOD_MATUKAI_SAG_2"]

    # 1. Sp_CalcDamage : Pouvoir Amplifie I-III (+15% / +30% / +50%)
    dmg_anchor = "if( IsFormActive( OBJECT_SELF, FORM_FORCE_I_FOCUS ) )"
    assert dmg_anchor in inc, "Sp_CalcDamage anchor not found"
    emp_code = f'''// Overhaul Metamagie : Pouvoir Amplifie I-III (+15% / +30% / +50%)
    if (GetHasFeat({emp3}, OBJECT_SELF)) {{ nDamage = (nDamage * 150) / 100; }}
    else if (GetHasFeat({emp2}, OBJECT_SELF)) {{ nDamage = (nDamage * 130) / 100; }}
    else if (GetHasFeat({emp1}, OBJECT_SELF)) {{ nDamage = (nDamage * 115) / 100; }}
    ''' + dmg_anchor
    inc = inc.replace(dmg_anchor, emp_code, 1)

    # 2. Sp_CalcDuration : Pouvoir Prolonge (x2) + Cristal Maitre Jedi (+25% duree)
    dur_anchor = "if( IsFormActive( OBJECT_SELF, FORM_FORCE_IV_MASTERY ) )"
    assert dur_anchor in inc, "Sp_CalcDuration anchor not found"
    ext_code = f'''// Overhaul Metamagie : Pouvoir Prolonge (x2) + Cristal Maitre Jedi (+25% duree buffs)
    if (GetHasFeat({ext1}, OBJECT_SELF)) {{ fFinalDuration = fFinalDuration * 2.0f; }}
    if (OBJECT_SELF == GetFirstPC() && GetLevelByClass(CLASS_TYPE_JEDIMASTER, OBJECT_SELF) > 0) {{
        object oOvR = GetItemInSlot(INVENTORY_SLOT_RIGHTWEAPON, OBJECT_SELF);
        object oOvL = GetItemInSlot(INVENTORY_SLOT_LEFTWEAPON, OBJECT_SELF);
        if ((GetIsObjectValid(oOvR) && GetItemHasItemProperty(oOvR, 62)) || (GetIsObjectValid(oOvL) && GetItemHasItemProperty(oOvL, 62))) {{
            fFinalDuration = fFinalDuration * 1.25f;
        }}
    }}
    ''' + dur_anchor
    inc = inc.replace(dur_anchor, ext_code, 1)

    # 3. Sp_MySavingThrows : Pouvoir Penetrant I-III (+2/4/6 DD) + Cristal JMA/SLD (+2 DD) + Corps de Force (+2/4/6 DD)
    dc_anchor = "if( IsFormActive( OBJECT_SELF, FORM_FORCE_IV_MASTERY ) ) {\n        // +2 bonus to DC."
    if dc_anchor not in inc:
        dc_anchor = "if( IsFormActive( OBJECT_SELF, FORM_FORCE_IV_MASTERY ) ) {\r\n        // +2 bonus to DC."
    assert dc_anchor in inc, "Sp_MySavingThrows anchor not found"
    pen_code = f'''// Overhaul : Pouvoir Penetrant I-III (+2/4/6) + Cristal JMA/SLD (+2) + Corps de Force (+2/4/6)
    if (GetHasFeat({pen3}, OBJECT_SELF)) {{ nMod += 6; }}
    else if (GetHasFeat({pen2}, OBJECT_SELF)) {{ nMod += 4; }}
    else if (GetHasFeat({pen1}, OBJECT_SELF)) {{ nMod += 2; }}
    if (OBJECT_SELF == GetFirstPC() && (GetLevelByClass(CLASS_TYPE_JEDIMASTER, OBJECT_SELF) > 0 || GetLevelByClass(CLASS_TYPE_SITHLORD, OBJECT_SELF) > 0)) {{
        object oOvR2 = GetItemInSlot(INVENTORY_SLOT_RIGHTWEAPON, OBJECT_SELF);
        object oOvL2 = GetItemInSlot(INVENTORY_SLOT_LEFTWEAPON, OBJECT_SELF);
        if ((GetIsObjectValid(oOvR2) && GetItemHasItemProperty(oOvR2, 62)) || (GetIsObjectValid(oOvL2) && GetItemHasItemProperty(oOvL2, 62))) {{
            nMod += 2;
        }}
    }}
    if (GetHasSpellEffect(152, OBJECT_SELF)) {{ nMod += 6; }}
    else if (GetHasSpellEffect(151, OBJECT_SELF)) {{ nMod += 4; }}
    else if (GetHasSpellEffect(150, OBJECT_SELF)) {{ nMod += 2; }}
    ''' + dc_anchor
    inc = inc.replace(dc_anchor, pen_code, 1)

    # 4. Sp_MySavingThrows : Matukai II punition mod. SAG en cas de sauvegarde reussie (sur tous les sorts vanilla)
    mat_anchor = "DisplayFeedBackText(oTarget, 2);"
    assert mat_anchor in inc, "Sp_MySavingThrows Matukai anchor not found"
    mat_code = f'''DisplayFeedBackText(oTarget, 2);
        if (GetLocalNumber(oTarget, 22) == 5 && GetHasFeat({mat2}, oTarget) && GetIsEnemy(oTarget, OBJECT_SELF) && !GetIsDead(oTarget))
        {{
            int nOvWis = GetAbilityModifier(ABILITY_WISDOM, oTarget);
            if (nOvWis > 0)
            {{
                AssignCommand(oTarget, ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectDamage(nOvWis, DAMAGE_TYPE_BLUDGEONING), OBJECT_SELF));
            }}
        }}'''
    inc = inc.replace(mat_anchor, mat_code, 1)

    # 5. Esquive Totale (FEAT_EVASION) sur pouvoirs AoE vanilla restants (Droid Disable/Destroy, etc.) : 1/2 degats sur echec
    ev_pat = "effect eDamage = EffectDamage(nDamage, DAMAGE_TYPE_ELECTRICAL);;"
    if ev_pat in inc:
        inc = inc.replace(
            ev_pat,
            "int nFailDmg = GetHasFeat(FEAT_EVASION, oTarget) ? (nDamage / 2) : nDamage;\n            effect eDamage = EffectDamage(nFailDmg, DAMAGE_TYPE_ELECTRICAL);",
        )

    (SRC_DIR / "k_inc_force.nss").write_text(inc, encoding="latin1")
    build_ov_inc_powers(fids, sids)

    sp1 = (REF_SCRIPTS / "k_sp1_generic.nss").read_text(encoding="latin1")
    sp1 = sp1.replace('#include "k_inc_force"', '#include "k_inc_force"\n#include "ov_inc_powers"', 1)

    m_main = re.search(r"void\s+main\s*\(\s*\)\s*\{", sp1)
    assert m_main, "main() not found in k_sp1_generic.nss"
    dispatch_call = '''
    {
        int nOvSp = GetSpellId();
        Ov_ApplyCastFPCostMods(OBJECT_SELF, nOvSp);
        if (Ov_HandleCustomPower(nOvSp))
        {
            return;
        }
    }
'''
    sp1 = sp1[:m_main.end()] + dispatch_call + sp1[m_main.end():]
    compile_script("k_sp1_generic", sp1)


def build_personal_crystal_script() -> None:
    """Compile a_q_cryst_change.ncs : attribue le Cristal personnel 3 paliers (ov_crys_<tier>_<s1><s2>)
    soit selon le choix manuel du joueur dans kreia.dlg (ActionParam1=s1+1, ActionParam2=s2+1),
    soit automatiquement selon les 2 meilleures caracteristiques de base si ActionParam1/2 = 0."""
    code = '''//:: a_q_cryst_change - Cristal personnel de l'Exile 3 paliers (Auto ou Choix manuel Kreia)
void main()
{
    object oPC = GetFirstPC();
    if (!GetIsObjectValid(oPC)) return;

    int nLvl = GetHitDice(oPC);
    int nTier = 1;
    if (nLvl >= 22) nTier = 3;
    else if (nLvl >= 15) nTier = 2;

    int nBest1 = -1;
    int nBest2 = -1;
    int p1 = GetScriptParameter(1);
    int p2 = GetScriptParameter(2);
    if (p1 >= 1 && p1 <= 6 && p2 >= 1 && p2 <= 6 && p1 != p2)
    {
        nBest1 = p1 - 1;
        nBest2 = p2 - 1;
    }
    else
    {
        nBest1 = 0;
        int nVal1 = -1;
        int i = 0;
        while (i < 6)
        {
            int v = GetAbilityScore(oPC, i);
            if (v > nVal1) { nVal1 = v; nBest1 = i; }
            i += 1;
        }
        nBest2 = (nBest1 == 0) ? 1 : 0;
        int nVal2 = -1;
        i = 0;
        while (i < 6)
        {
            if (i != nBest1)
            {
                int v2 = GetAbilityScore(oPC, i);
                if (v2 > nVal2) { nVal2 = v2; nBest2 = i; }
            }
            i += 1;
        }
    }

    // Retirer l'ancien cristal personnel (vanilla ou overhaul)
    int nOld = GetGlobalNumber("000_Quest_Crystal");
    if (nOld > 0)
    {
        string sOld = IntToString(nOld);
        object oOld1 = GetItemPossessedBy(oPC, "qcrystal_" + GetStringLeft(sOld, 1) + "_" + GetStringRight(sOld, 1));
        if (GetIsObjectValid(oOld1)) DestroyObject(oOld1);
        int t = nOld / 100;
        int rem = nOld - (t * 100);
        int a1 = rem / 10;
        int a2 = rem - (a1 * 10);
        object oOld2 = GetItemPossessedBy(oPC, "ov_crys_" + IntToString(t) + "_" + IntToString(a1) + IntToString(a2));
        if (GetIsObjectValid(oOld2)) DestroyObject(oOld2);
    }

    string sRes = "ov_crys_" + IntToString(nTier) + "_" + IntToString(nBest1) + IntToString(nBest2);
    SetGlobalNumber("000_Quest_Crystal", (nTier * 100) + (nBest1 * 10) + nBest2);
    CreateItemOnObject(sRes, oPC, 1);
}
'''
    compile_script("a_q_cryst_change", code)


def main() -> None:
    SRC_DIR.mkdir(parents=True, exist_ok=True)
    OVR_DIR.mkdir(parents=True, exist_ok=True)
    fids: dict[str, int] = json.loads(FEAT_IDS_FILE.read_text(encoding="utf-8"))
    sids: dict[str, int] = json.loads(SPELL_IDS_FILE.read_text(encoding="utf-8"))
    print(f"=== Build Jalon 3 (NWScript .nss -> .ncs) -> {OVR_DIR} ===")
    build_ov_inc_core(fids, sids)
    build_force_powers(fids, sids)
    build_wrappers()
    build_support_scripts()
    build_personal_crystal_script()
    print("=== Jalon 3 BUILD OK (tous les scripts compiles sans erreur) ===")


if __name__ == "__main__":
    main()
