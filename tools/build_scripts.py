#!/usr/bin/env python3
"""KotOR 2 Overhaul — Jalon 3 : Générateur & Compilateur des scripts NWScript (.nss -> .ncs).

Respecte strictement les règles moteur validées (README.md §2–§3) :
  - Bug #7 : NE JAMAIS recompiler `k_ai_master.ncs` — tous les hooks passent par les
    petits wrappers `k_hen_*` / `k_def_*` qui appellent ensuite le vrai `k_ai_master` vanilla.
  - T4 : tous les bonus de CA custom sont additionnés dans un seul `nTotalAC` avant
    un unique `EffectACIncrease(nTotalAC, AC_DODGE_BONUS)`.
  - T-excl : mutualité des 6 Spé Carac assurée par garde-fou `LocalNumber(oTarget, 22)`.
  - Prologue safety : `GetIsPlayerMadeCharacter` vérifié avant tout effet sur le PJ.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REF_SCRIPTS = ROOT / "_reference" / "scripts"
NWNNSSCOMP = ROOT / "_reference" / "autres_mods" / "Content Pack-57-1-67-1616632489" / "tslpatchdata" / "nwnnsscomp.exe"
OUT_DIR = ROOT / "mods" / "overhaul"
SRC_DIR = OUT_DIR / "src"
STAGE_DIR = OUT_DIR / "_compile_stage"
OVR_DIR = OUT_DIR / "Override"
FEAT_IDS_FILE = OUT_DIR / "feat_ids.json"


def _prepare_stage() -> None:
    """Prépare un répertoire de compilation contenant nwnnsscomp.exe, nwscript.nss et tous les includes."""
    STAGE_DIR.mkdir(parents=True, exist_ok=True)
    if not (STAGE_DIR / "nwnnsscomp.exe").exists():
        shutil.copy2(NWNNSSCOMP, STAGE_DIR / "nwnnsscomp.exe")
    # Copier tous les includes de _reference/scripts/ une seule fois
    for inc in REF_SCRIPTS.glob("*.nss"):
        dst = STAGE_DIR / inc.name
        if not dst.exists():
            shutil.copy2(inc, dst)
    # Écraser avec nos propres sources modifiées (ov_inc_core.nss, k_inc_force.nss, etc.)
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


def build_ov_inc_core(fids: dict[str, int]) -> str:
    code = f'''//:: ov_inc_core - KotOR 2 Overhaul Core Library (Passe 2 : Passifs + Postures + Spe Armes + Ripostes)

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

// Famille d'arme : 1=Impact, 2=Trad, 3=Resonance, 4=Laser, 5=Assaut, 6=Penetrant, 7=Tactique, 8=Assassin
int Ov_GetWeaponFamily(int nBI)
{{
    if (nBI == 0 || nBI == 1 || nBI == 78 || nBI == 93 || nBI == 104) return 1;
    if (nBI == 2 || nBI == 4 || nBI == 6 || nBI == 79 || nBI == 80 || nBI == 105) return 2;
    if (nBI == 3 || nBI == 5 || nBI == 7 || nBI == 106) return 3;
    if (nBI == 8 || nBI == 9 || nBI == 10 || nBI == 107) return 4;
    if (nBI == 12 || nBI == 20 || nBI == 23 || nBI == 109 || nBI == 110) return 5;
    if (nBI == 13 || nBI == 19 || nBI == 24 || nBI == 77 || nBI == 108 || nBI == 111 || nBI == 114) return 6;
    if (nBI == 15 || nBI == 17 || nBI == 18 || nBI == 22 || nBI == 112 || nBI == 113) return 7;
    if (nBI == 14 || nBI == 16 || nBI == 21) return 8;
    return 0;
}}

int Ov_IsRangedBaseItem(int nBI)
{{
    int nFam = Ov_GetWeaponFamily(nBI);
    return (nFam >= 5 && nFam <= 8);
}}

int Ov_IsDoubleBaseItem(int nBI)
{{
    return (nBI == 0 || nBI == 6 || nBI == 7 || nBI == 9 || nBI == 23 || nBI == 24 || nBI == 78 || nBI == 93);
}}

int Ov_IsHeavy2HBaseItem(int nBI)
{{
    return (nBI == 18 || nBI == 19 || nBI == 20 || nBI == 21 || nBI == 22 || nBI == 77 || nBI == 79);
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

void Ov_RefreshPassives(object oTarget);

void Ov_PollStealth()
{{
    int i = 0;
    while (i < 3)
    {{
        object oPM = GetPartyMemberByIndex(i);
        if (GetIsObjectValid(oPM))
        {{
            object oArea = GetArea(oPM);
            if (IsStealthed(oPM))
            {{
                int nPrev = GetLocalNumber(oPM, 25);
                SetLocalNumber(oPM, 25, 6);
                if (GetIsObjectValid(oArea)) SetLocalNumber(oArea, 25, 6);
                if (nPrev == 0) Ov_RefreshPassives(oPM);
            }}
            else
            {{
                int nCur = GetLocalNumber(oPM, 25);
                if (nCur > 0)
                {{
                    nCur -= 1;
                    SetLocalNumber(oPM, 25, nCur);
                    if (nCur == 0)
                    {{
                        if (GetIsObjectValid(oArea)) SetLocalNumber(oArea, 25, 0);
                        Ov_RefreshPassives(oPM);
                    }}
                }}
            }}
        }}
        i += 1;
    }}
}}

void Ov_RefreshPassives(object oTarget)
{{
    if (!GetIsObjectValid(oTarget) || GetIsDead(oTarget)) return;
    if (oTarget == GetFirstPC() && !GetIsPlayerMadeCharacter(oTarget)) return;

    if (IsStealthed(oTarget))
    {{
        SetLocalNumber(oTarget, 25, 6);
        object oArea = GetArea(oTarget);
        if (GetIsObjectValid(oArea)) SetLocalNumber(oArea, 25, 6);
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
    int bMindImm = FALSE;

    // Bonus Embuscade furtive : +50 Atq garanti tant que furtif ou 6s max apres sortie (consomme au 1er coup)
    if (IsStealthed(oTarget) || GetLocalNumber(oTarget, 25) > 0)
    {{
        nTotalAtk += 50;
    }}

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

    // 3. Armes equipees -> Postures & Specialisations d'arme
    object oRight = GetItemInSlot(INVENTORY_SLOT_RIGHTWEAPON, oTarget);
    object oLeft  = GetItemInSlot(INVENTORY_SLOT_LEFTWEAPON, oTarget);
    int nBI = GetIsObjectValid(oRight) ? GetBaseItemType(oRight) : -1;
    int nFam = (nBI >= 0) ? Ov_GetWeaponFamily(nBI) : 0;
    int bRanged = (nBI >= 0) ? Ov_IsRangedBaseItem(nBI) : FALSE;

    int nStr = GetAbilityModifier(ABILITY_STRENGTH, oTarget);
    int nDex = GetAbilityModifier(ABILITY_DEXTERITY, oTarget);
    int nCon = GetAbilityModifier(ABILITY_CONSTITUTION, oTarget);
    int nInt = GetAbilityModifier(ABILITY_INTELLIGENCE, oTarget);
    int nWis = GetAbilityModifier(ABILITY_WISDOM, oTarget);
    int nCha = GetAbilityModifier(ABILITY_CHARISMA, oTarget);

    // 3a. 4 Postures de combat
    int bGam2 = (nTree == 1 && GetHasFeat(OV_GAM_2, oTarget));
    if (GetIsObjectValid(oRight) && GetIsObjectValid(oLeft))
    {{
        // Ambidextrie
        if (GetHasFeat(OV_AMB_3, oTarget)) {{ nTotalAC += 3; nTotalAtk += 6; }}
        else if (GetHasFeat(OV_AMB_2, oTarget)) {{ nTotalAC += 2; nTotalAtk += 4; }}
        else if (GetHasFeat(OV_AMB_1, oTarget)) {{ nTotalAC += 1; nTotalAtk += 2; }}
    }}
    else if (GetIsObjectValid(oRight) && Ov_IsDoubleBaseItem(nBI) && !bGam2)
    {{
        // Arme haute cadence (double) : malus base -5 CA -> -3/-2/-1, degats +1/+2/+3
        if (GetHasFeat(OV_DBL_3, oTarget)) {{ nTotalDmg += 3; nTotalAC -= 1; }}
        else if (GetHasFeat(OV_DBL_2, oTarget)) {{ nTotalDmg += 2; nTotalAC -= 2; }}
        else if (GetHasFeat(OV_DBL_1, oTarget)) {{ nTotalDmg += 1; nTotalAC -= 3; }}
        else {{ nTotalAC -= 5; }}
    }}
    else if (GetIsObjectValid(oRight) && Ov_IsHeavy2HBaseItem(nBI) && !bGam2)
    {{
        // Maniement d'arme lourde (2M non double)
        int nStat2H = bRanged ? nDex : nStr;
        if (nStat2H < 0) nStat2H = 0;
        if (GetHasFeat(OV_HVY_3, oTarget)) {{ nTotalAtk += 3; nTotalDmg += (nStat2H * 50) / 100; }}
        else if (GetHasFeat(OV_HVY_2, oTarget)) {{ nTotalAtk += 2; nTotalDmg += (nStat2H * 35) / 100; }}
        else if (GetHasFeat(OV_HVY_1, oTarget)) {{ nTotalAtk += 1; nTotalDmg += (nStat2H * 15) / 100; }}
    }}
    else if (!GetIsObjectValid(oLeft))
    {{
        // Duel (1M ou mains nues)
        if (GetHasFeat(OV_DUE_3, oTarget)) {{ nTotalAtk += 6; }}
        else if (GetHasFeat(OV_DUE_2, oTarget)) {{ nTotalAtk += 4; }}
        else if (GetHasFeat(OV_DUE_1, oTarget)) {{ nTotalAtk += 2; }}
    }}

    // 3b. 8 Specialisations d'arme (Rang I : +2 Atq/+2 Dmg ; Assaut III : +1 Atq/rd ; Penetrant III : +5 Dmg)
    if (nFam == 1 && GetHasFeat(OV_SP_BLUNT_1, oTarget)) {{ nTotalAtk += 2; nTotalDmg += 2; }}
    else if (nFam == 2 && GetHasFeat(OV_SP_PRIM_1, oTarget)) {{ nTotalAtk += 2; nTotalDmg += 2; }}
    else if (nFam == 3 && GetHasFeat(OV_SP_VIBRO_1, oTarget)) {{ nTotalAtk += 2; nTotalDmg += 2; }}
    else if (nFam == 4 && GetHasFeat(OV_SP_LASER_1, oTarget)) {{ nTotalAtk += 2; nTotalDmg += 2; }}
    else if (nFam == 5 && GetHasFeat(OV_SP_ASSAULT_1, oTarget))
    {{
        nTotalAtk += 2; nTotalDmg += 2;
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
    if (nTree == 1) // Gamoreen
    {{
        if (GetHasFeat(OV_GAM_3, oTarget)) bMindImm = TRUE;
    }}
    else if (nTree == 2) // Echani (I: DEX Atq melee, II: DEX Dmg melee, III: leve plafond DEX armure)
    {{
        if (!bRanged && nDex > nStr)
        {{
            nTotalAtk += (nDex - nStr);
            if (GetHasFeat(OV_ECH_2, oTarget)) nTotalDmg += (nDex - nStr);
        }}
        if (GetHasFeat(OV_ECH_3, oTarget) && nTier > 0)
        {{
            int nCap = (nTier == 1) ? 5 : ((nTier == 2) ? 3 : 1);
            if (nDex > nCap) nTotalAC += (nDex - nCap);
        }}
    }}
    else if (nTree == 3) // Kraith (I: +1/2 CON arrondi sup., II: transfusion, III: +CON saves)
    {{
        if (nCon > 0) nTotalRD += (nCon + 1) / 2;
        if (GetHasFeat(OV_KRA_3, oTarget) && nCon > 0) nTotalSaves += nCon;
        if (GetHasFeat(OV_KRA_2, oTarget))
        {{
            int nMaxHP = GetMaxHitPoints(oTarget);
            int nCurHP = GetCurrentHitPoints(oTarget);
            int nMaxFP = GetMaxForcePoints(oTarget);
            int nCurFP = GetCurrentForcePoints(oTarget);
            if (nMaxFP > 0 && nCurFP < (nMaxFP / 2) && nCurHP > ((nMaxHP * 3) / 4))
            {{
                int nHpCost = nMaxHP / 20;
                int nFpGain = nMaxFP / 20;
                if (nHpCost < 1) nHpCost = 1;
                if (nFpGain < 1) nFpGain = 1;
                ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectDamage(nHpCost, DAMAGE_TYPE_DARK_SIDE), oTarget);
                ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectHealForcePoints(nFpGain), oTarget);
            }}
        }}
    }}
    else if (nTree == 4) // Gand (II: INT Atq/Dmg distance si INT > DEX)
    {{
        if (bRanged && GetHasFeat(OV_GAN_2, oTarget) && nInt > nDex)
        {{
            nTotalAtk += (nInt - nDex);
            nTotalDmg += (nInt - nDex);
        }}
    }}
    else if (nTree == 5) // Matukai (I: +SAG Atq, II: +1/2 SAG saves, III: SAG remplace DEX pour CA)
    {{
        if (nWis > 0) nTotalAtk += nWis;
        if (GetHasFeat(OV_MAT_2, oTarget) && nWis > 0) nTotalSaves += (nWis / 2);
        if (GetHasFeat(OV_MAT_3, oTarget) && nWis > nDex) nTotalAC += (nWis - nDex);
    }}
    else if (nTree == 6) // Nomi (II: +CHA saves, III: +CHA CA)
    {{
        if (GetHasFeat(OV_NOM_2, oTarget) && nCha > 0) nTotalSaves += nCha;
        if (GetHasFeat(OV_NOM_3, oTarget) && nCha > 0) nTotalAC += nCha;
    }}

    // Aura Nomi II du PJ sur les compagnons
    object oPC = GetFirstPC();
    if (oTarget != oPC && GetIsObjectValid(oPC) && GetPartyMemberByIndex(1) == oTarget || GetPartyMemberByIndex(2) == oTarget)
    {{
        if (Ov_GetActiveCaracTree(oPC) == 6 && GetHasFeat(OV_NOM_2, oPC))
        {{
            int nChaPC = GetAbilityModifier(ABILITY_CHARISMA, oPC);
            if (nChaPC > 0) nTotalSaves += nChaPC;
        }}
    }}

    // 5. Affranchi de la Force I-III (4 paires de competences / 8, cap +3/+5/+7 + RF 15+Niv au rang III)
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
        if (GetHasFeat(OV_UNB_3, oTarget)) nForceRes = 15 + GetHitDice(oTarget);
    }}

    // 6. Cristal personnel de l'Exile : effets de classe de base + prestige quand sabre equipe
    int nSkillAll = 0;
    if (oTarget == oPC && nFam == 4 && GetGlobalNumber("000_Quest_Crystal") > 0)
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
        if (GetLevelByClass(CLASS_TYPE_SITHLORD, oPC) > 0)
        {{
            ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectHealForcePoints(3), oPC);
        }}
    }}

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
        effect eI1 = EffectDamageImmunityIncrease(DAMAGE_TYPE_BLUDGEONING, nTotalImm);
        effect eI2 = EffectDamageImmunityIncrease(DAMAGE_TYPE_PIERCING, nTotalImm);
        effect eI3 = EffectDamageImmunityIncrease(DAMAGE_TYPE_SLASHING, nTotalImm);
        effect eI4 = EffectDamageImmunityIncrease(DAMAGE_TYPE_BLASTER, nTotalImm);
        effect eIAll = EffectLinkEffects(EffectLinkEffects(eI1, eI2), EffectLinkEffects(eI3, eI4));
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
    if (bMindImm)
    {{
        effect eMi = EffectImmunity(IMMUNITY_TYPE_MIND_SPELLS);
        if (bHasAny) eBundle = EffectLinkEffects(eBundle, eMi); else eBundle = eMi;
        bHasAny = TRUE;
    }}

    if (bHasAny)
    {{
        ApplyEffectToObject(DURATION_TYPE_PERMANENT, ExtraordinaryEffect(eBundle), oTarget);
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

void Ov_ResetMutilate(object oVictim)
{{
    if (GetIsObjectValid(oVictim)) SetLocalNumber(oVictim, 27, 0);
}}

void Ov_OnDamageHook(object oVictim)
{{
    object oAtk = GetLastDamager();
    if (!GetIsObjectValid(oAtk)) return;

    // 1. Embuscade furtive : premiere attaque depuis la furtivite = critique confirme (x2)
    object oArea = GetArea(oAtk);
    int bAmbush = (GetLocalNumber(oAtk, 25) > 0 || IsStealthed(oAtk) || (GetIsObjectValid(oArea) && GetLocalNumber(oArea, 25) > 0 && (oAtk == GetFirstPC() || GetPartyMemberByIndex(1) == oAtk || GetPartyMemberByIndex(2) == oAtk)));
    if (bAmbush)
    {{
        SetLocalNumber(oAtk, 25, 0);
        if (GetIsObjectValid(oArea)) SetLocalNumber(oArea, 25, 0);
        Ov_RefreshPassives(oAtk);
        int nDealt = GetTotalDamageDealt();
        if (nDealt > 0 && !GetIsDead(oVictim))
        {{
            ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectVisualEffect(VFX_IMP_FORCE_PUSH), oVictim);
            AssignCommand(oAtk, ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectDamage(nDealt, DAMAGE_TYPE_PIERCING), oVictim));
        }}
    }}

    if (GetIsDead(oVictim)) return;

    // 2. Procs des 8 Specialisations d'arme (Rangs II & III)
    object oW = GetItemInSlot(INVENTORY_SLOT_RIGHTWEAPON, oAtk);
    if (!GetIsObjectValid(oW)) return;
    int nBI = GetBaseItemType(oW);
    int nFam = Ov_GetWeaponFamily(nBI);
    if (nFam == 0) return;

    int nLvl = GetHitDice(oAtk);
    int nStat = Ov_IsRangedBaseItem(nBI)
        ? GetAbilityModifier(ABILITY_DEXTERITY, oAtk)
        : GetAbilityModifier(ABILITY_STRENGTH, oAtk);
    int nTree = Ov_GetActiveCaracTree(oAtk);
    if (nTree == 2 && !Ov_IsRangedBaseItem(nBI))
    {{
        int nD = GetAbilityModifier(ABILITY_DEXTERITY, oAtk);
        if (nD > nStat) nStat = nD;
    }}
    else if (nTree == 4 && Ov_IsRangedBaseItem(nBI) && GetHasFeat(OV_GAN_2, oAtk))
    {{
        int nI = GetAbilityModifier(ABILITY_INTELLIGENCE, oAtk);
        if (nI > nStat) nStat = nI;
    }}

    if (nFam == 1 && GetHasFeat(OV_SP_BLUNT_2, oAtk)) // Impact II-III : Renversement 1-2 tours
    {{
        if (d20() <= 2 && !FortitudeSave(oVictim, 10 + nLvl + nStat, SAVING_THROW_TYPE_NONE, oAtk))
        {{
            float fKD = GetHasFeat(OV_SP_BLUNT_3, oAtk) ? 12.0 : 6.0;
            ApplyEffectToObject(DURATION_TYPE_TEMPORARY, EffectKnockdown(), oVictim, fKD);
        }}
    }}
    else if (nFam == 2 && GetHasFeat(OV_SP_PRIM_2, oAtk)) // Trad II-III : Bris d'armure -3 CA (12s/18s)
    {{
        if (!FortitudeSave(oVictim, 5 + nLvl + nStat, SAVING_THROW_TYPE_NONE, oAtk))
        {{
            float fBr = GetHasFeat(OV_SP_PRIM_3, oAtk) ? 18.0 : 12.0;
            ApplyEffectToObject(DURATION_TYPE_TEMPORARY, EffectACDecrease(3), oVictim, fBr);
        }}
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
                SetLocalNumber(oVictim, 27, nPen);
                DelayCommand(6.5, Ov_ResetMutilate(oVictim));
            }}
            effect eMut = EffectLinkEffects(EffectAttackDecrease(nPen), EffectDamageDecrease(nPen, DAMAGE_TYPE_UNIVERSAL));
            ApplyEffectToObject(DURATION_TYPE_TEMPORARY, eMut, oVictim, 6.0);
        }}
    }}
    else if (nFam == 4 && GetHasFeat(OV_SP_LASER_2, oAtk)) // Laser II-III : Bris de volonte -4 saves (sans jet III)
    {{
        if (GetHasFeat(OV_SP_LASER_3, oAtk) || !WillSave(oVictim, 5 + nLvl + nStat, SAVING_THROW_TYPE_MIND_AFFECTING, oAtk))
        {{
            ApplyEffectToObject(DURATION_TYPE_TEMPORARY, EffectSavingThrowDecrease(SAVING_THROW_ALL, 4), oVictim, 12.0);
        }}
    }}
    else if (nFam == 6 && GetHasFeat(OV_SP_HEAVY_2, oAtk)) // Penetrant II : Repousse 3m (1x/round)
    {{
        if (GetLocalNumber(oVictim, 28) == 0 && !FortitudeSave(oVictim, 5 + nLvl + nStat, SAVING_THROW_TYPE_NONE, oAtk))
        {{
            SetLocalNumber(oVictim, 28, 1);
            ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectForcePushTargeted(GetLocation(oAtk)), oVictim);
            DelayCommand(6.0, Ov_ResetPushLock(oVictim));
        }}
    }}
    else if (nFam == 7 && GetHasFeat(OV_SP_TAC_2, oAtk)) // Tactique II-III : Stun 1-2 tours (droide ou organique)
    {{
        if (d20() <= 2 && !FortitudeSave(oVictim, 10 + nLvl + nStat, SAVING_THROW_TYPE_NONE, oAtk))
        {{
            float fSt = GetHasFeat(OV_SP_TAC_3, oAtk) ? 12.0 : 6.0;
            effect eSt = (GetRacialType(oVictim) == RACIAL_TYPE_DROID) ? EffectDroidStun() : EffectStunned();
            ApplyEffectToObject(DURATION_TYPE_TEMPORARY, eSt, oVictim, fSt);
        }}
    }}
    else if (nFam == 8 && GetHasFeat(OV_SP_ASSASSIN_2, oAtk)) // Assassin II : +2d6 degats sur cible incapacitee/embusquee
    {{
        if (bAmbush || Ov_IsIncapacitated(oVictim))
        {{
            AssignCommand(oAtk, ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectDamage(d6(2), DAMAGE_TYPE_PIERCING), oVictim));
        }}
    }}

    // 3. Cristal personnel de l'Exile : procs On-Hit de prestige (sabre equipe)
    if (oAtk == GetFirstPC() && nFam == 4 && GetGlobalNumber("000_Quest_Crystal") > 0)
    {{
        if (GetLevelByClass(CLASS_TYPE_JEDIWEAPONMASTER, oAtk) > 0)
        {{
            int nSt = GetLocalNumber(oAtk, 29) + 1;
            if (nSt > 5) nSt = 5;
            SetLocalNumber(oAtk, 29, nSt);
            effect eWM = EffectLinkEffects(EffectAttackIncrease(nSt), EffectACIncrease(nSt, AC_DODGE_BONUS));
            ApplyEffectToObject(DURATION_TYPE_TEMPORARY, eWM, oAtk, 12.0);
        }}
        if (GetLevelByClass(CLASS_TYPE_SITHMARAUDER, oAtk) > 0)
        {{
            int nH = GetMaxHitPoints(oAtk) / 100;
            if (nH < 1) nH = 1;
            ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectHeal(nH), oAtk);
        }}
        if (GetLevelByClass(CLASS_TYPE_SITHASSASSIN, oAtk) > 0 && (bAmbush || Ov_IsIncapacitated(oVictim)))
        {{
            AssignCommand(oAtk, ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectDamage(d6(2), DAMAGE_TYPE_PIERCING), oVictim));
        }}
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
        "k_hen_heartbt01": '#include "k_inc_switch"\n#include "ov_inc_core"\nvoid main() {\n    Ov_RefreshPassives(OBJECT_SELF);\n    Ov_RefreshPassives(GetFirstPC());\n    ExecuteScript("k_ai_master", OBJECT_SELF, KOTOR_HENCH_EVENT_ON_HEARTBEAT);\n}\n',
        "k_def_heartbt01": '#include "k_inc_switch"\n#include "ov_inc_core"\n' + drain_hook + '\nvoid main() {\n    Ov_RefreshPassives(OBJECT_SELF);\n    Ov_RefreshPassives(GetFirstPC());\n    Ov_PollStealth();\n    DelayCommand(1.0, Ov_PollStealth());\n    DelayCommand(2.0, Ov_PollStealth());\n    DelayCommand(3.0, Ov_PollStealth());\n    DelayCommand(4.0, Ov_PollStealth());\n    DelayCommand(5.0, Ov_PollStealth());\n    Ov_SithDrainForceCheck();\n    ExecuteScript("k_ai_master", OBJECT_SELF, KOTOR_DEFAULT_EVENT_ON_HEARTBEAT);\n}\n',
        "k_hen_damage01":  '#include "k_inc_switch"\n#include "ov_inc_core"\nvoid main() {\n    Ov_OnDamageHook(OBJECT_SELF);\n    ExecuteScript("k_ai_master", OBJECT_SELF, KOTOR_HENCH_EVENT_ON_DAMAGE);\n}\n',
        "k_def_damage01":  '#include "k_inc_switch"\n#include "ov_inc_core"\nvoid main() {\n    Ov_OnDamageHook(OBJECT_SELF);\n    ExecuteScript("k_ai_master", OBJECT_SELF, KOTOR_DEFAULT_EVENT_ON_DAMAGE);\n}\n',
        "k_hen_attacked01": '#include "k_inc_switch"\n#include "ov_inc_core"\nvoid main() {\n    Ov_OnAttackedHook(OBJECT_SELF);\n    ExecuteScript("k_ai_master", OBJECT_SELF, KOTOR_HENCH_EVENT_ON_ATTACKED);\n}\n',
        "k_def_attacked01": '#include "k_inc_switch"\n#include "ov_inc_core"\nvoid main() {\n    Ov_PollStealth();\n    Ov_OnAttackedHook(OBJECT_SELF);\n    ExecuteScript("k_ai_master", OBJECT_SELF, KOTOR_DEFAULT_EVENT_ON_ATTACKED);\n}\n',
    }
    for name, code in wrappers.items():
        compile_script(name, code)


def build_grenades(fids: dict[str, int]) -> None:
    """Patch k_sup_grenade.nss : DD = 10 + Niv + Mod INT (12 + Niv + INT pour roquettes/flechettes)
    + Gand I (+5% degats / rang de Demolition)."""
    src = (REF_SCRIPTS / "k_sup_grenade.nss").read_text(encoding="latin1")
    # Ne remplacer que les assignations `nDC = 15;` (etc.), JAMAIS `int nDC = 0;` dans GR_GetGrenadeDC()!
    scaled_dc_nw = "nDC = 10 + GetHitDice(OBJECT_SELF) + GetAbilityModifier(ABILITY_INTELLIGENCE, OBJECT_SELF); if (GetSpellId() >= 246) { nDC += 2; }"
    src_patched = re.sub(r"(?<!int\s)\bnDC\s*=\s*[1-9]\d*\s*;", scaled_dc_nw, src)
    # Bonus Gand I (+5% degats / rang total de Demolition)
    gand1 = fids["MOD_GAND_1"]
    gand_snippet = f"if (GetHasFeat({gand1}, OBJECT_SELF)) {{ nDamage = nDamage + (nDamage * GetSkillRank(SKILL_DEMOLITIONS, OBJECT_SELF) * 5) / 100; }}"
    src_patched = src_patched.replace("nDamage = 20 + nFeat;", f"nDamage = 20 + nFeat; {gand_snippet}")
    src_patched = src_patched.replace("nDamage = 40 + nFeat;", f"nDamage = 40 + nFeat; {gand_snippet}")
    src_patched = src_patched.replace("nDamage = 60 + nFeat;", f"nDamage = 60 + nFeat; {gand_snippet}")
    compile_script("k_sup_grenade", src_patched)


def build_ov_inc_powers(fids: dict[str, int]) -> str:
    """Genere ov_inc_powers.nss : refontes mecaniques des pouvoirs actees dans Spe Pouvoirs.csv.
    Appele au debut de k_sp1_generic.nss ; herite automatiquement de Sp_CalcDamage/Sp_CalcDuration/Ov_GetSpellDC (Metamagie)."""
    pen1, pen2, pen3 = fids["MOD_META_PENETRATE_1"], fids["MOD_META_PENETRATE_2"], fids["MOD_META_PENETRATE_3"]
    code = f'''//:: ov_inc_powers - Refontes des pouvoirs de la Force (KotOR 2 Overhaul)

int Ov_GetSpellDC(object oCaster)
{{
    int nDC = Sp_GetJediDCSave();
    if (GetHasFeat({pen3}, oCaster)) nDC += 6;
    else if (GetHasFeat({pen2}, oCaster)) nDC += 4;
    else if (GetHasFeat({pen1}, oCaster)) nDC += 2;
    if (oCaster == GetFirstPC() && GetGlobalNumber("000_Quest_Crystal") > 0)
    {{
        if (GetLevelByClass(CLASS_TYPE_JEDIMASTER, oCaster) > 0 || GetLevelByClass(CLASS_TYPE_SITHLORD, oCaster) > 0)
        {{
            nDC += 2;
        }}
    }}
    return nDC;
}}

void Ov_MentalDotTick(object oTarget, int nDmg, int nTicksLeft)
{{
    if (!GetIsObjectValid(oTarget) || GetIsDead(oTarget) || nTicksLeft <= 0) return;
    ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectDamage(nDmg, DAMAGE_TYPE_DARK_SIDE), oTarget);
    if (nTicksLeft > 1)
    {{
        DelayCommand(6.0, Ov_MentalDotTick(oTarget, nDmg, nTicksLeft - 1));
    }}
}}

void Ov_PlagueTick(object oCaster, object oTarget, int nTier, int nTicksLeft)
{{
    if (!GetIsObjectValid(oTarget) || nTicksLeft <= 0) return;
    if (GetIsDead(oTarget))
    {{
        // Propagation 5m a la mort de la cible
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
    int nDC = Ov_GetSpellDC(oCaster) + ((nTier - 1) * 4);
    if (FortitudeSave(oTarget, nDC, SAVING_THROW_TYPE_POISON, oCaster))
    {{
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
    if (nTicksLeft > 1)
    {{
        DelayCommand(6.0, Ov_PlagueTick(oCaster, oTarget, nTier, nTicksLeft - 1));
    }}
    else
    {{
        SetLocalNumber(oTarget, 26, 0);
    }}
}}

void Ov_StigmateTick(object oCaster, int nTicksLeft)
{{
    if (!GetIsObjectValid(oCaster) || GetIsDead(oCaster) || nTicksLeft <= 0) return;
    int nMaxHP = GetMaxHitPoints(oCaster);
    int nCurHP = GetCurrentHitPoints(oCaster);
    if (nCurHP <= (nMaxHP / 4)) return; // Arret auto <= 25% PV max
    int nDrain = nMaxHP / 20;
    if (nDrain < 1) nDrain = 1;
    ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectDamage(nDrain, DAMAGE_TYPE_DARK_SIDE), oCaster);
    if (nTicksLeft > 1)
    {{
        DelayCommand(6.0, Ov_StigmateTick(oCaster, nTicksLeft - 1));
    }}
}}

int Ov_HandleCustomPower(int nSpell)
{{
    object oCaster = OBJECT_SELF;
    object oTarget = GetSpellTargetObject();
    int nLevel = GetHitDice(oCaster);
    if (nLevel < 1) nLevel = 1;
    int nDC = Ov_GetSpellDC(oCaster);

    // 1. CHOC / FOUDRE / TEMPETE DE FORCE (1d6/Niv sans cap, Reflexes 1/2, sans drain PF, Esquive Totale)
    if (nSpell == FORCE_POWER_SHOCK || nSpell == FORCE_POWER_LIGHTNING || nSpell == FORCE_POWER_FORCE_STORM)
    {{
        float fRadius = 0.0;
        if (nSpell == FORCE_POWER_LIGHTNING) fRadius = 6.0;
        else if (nSpell == FORCE_POWER_FORCE_STORM) fRadius = 10.0;

        object oCur = (fRadius > 0.0)
            ? GetFirstObjectInShape(SHAPE_SPHERE, fRadius, GetSpellTargetLocation(), FALSE, OBJECT_TYPE_CREATURE)
            : oTarget;
        while (GetIsObjectValid(oCur))
        {{
            if (GetIsEnemy(oCur, oCaster) && !GetIsDead(oCur))
            {{
                SignalEvent(oCur, EventSpellCastAt(oCaster, nSpell, TRUE));
                int nDmg = Sp_CalcDamage(oCur, nLevel, 6);
                int bSaved = ReflexSave(oCur, nDC, SAVING_THROW_TYPE_ELECTRICAL, oCaster);
                if (bSaved)
                {{
                    if (GetHasFeat(FEAT_EVASION, oCur)) nDmg = 0;
                    else nDmg = nDmg / 2;
                }}
                ApplyEffectToObject(DURATION_TYPE_TEMPORARY, EffectBeam(VFX_BEAM_LIGHTNING_DARK_L, oCaster, BODY_NODE_HAND), oCur, 1.0);
                ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectVisualEffect(VFX_PRO_LIGHTNING_L), oCur);
                if (nDmg > 0) ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectDamage(nDmg, DAMAGE_TYPE_ELECTRICAL), oCur);
            }}
            if (fRadius <= 0.0) break;
            oCur = GetNextObjectInShape(SHAPE_SPHERE, fRadius, GetSpellTargetLocation(), FALSE, OBJECT_TYPE_CREATURE);
        }}
        return TRUE;
    }}

    // 2. TERREUR / HORREUR / INSANITE (DoT mental Niv/rd + -4/-6/-8 Atq, sans stun, 24s echec / 6s reussite Vol)
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

    // 3. BLESSURE / ETOUFFEMENT / MISE A MORT (1d4 / 1d6+stun / 1d8+stun sans 50% PV max, Vig 1/2 & annule stun)
    if (nSpell == FORCE_POWER_WOUND || nSpell == FORCE_POWER_CHOKE || nSpell == FORCE_POWER_KILL)
    {{
        if (GetIsObjectValid(oTarget) && !GetIsDead(oTarget))
        {{
            SignalEvent(oTarget, EventSpellCastAt(oCaster, nSpell, TRUE));
            int nDie = (nSpell == FORCE_POWER_WOUND) ? 4 : ((nSpell == FORCE_POWER_CHOKE) ? 6 : 8);
            int nDmg = Sp_CalcDamage(oTarget, nLevel, nDie);
            int bSaved = FortitudeSave(oTarget, nDC, SAVING_THROW_TYPE_NONE, oCaster);
            if (bSaved) nDmg = nDmg / 2;
            ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectVisualEffect(VFX_IMP_CHOKE), oTarget);
            ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectDamage(nDmg, DAMAGE_TYPE_DARK_SIDE), oTarget);
            if (!bSaved && (nSpell == FORCE_POWER_CHOKE || nSpell == FORCE_POWER_KILL))
            {{
                ApplyEffectToObject(DURATION_TYPE_TEMPORARY, EffectStunned(), oTarget, 6.0);
            }}
        }}
        return TRUE;
    }}

    // 4. ABSORPTION DE VIE / CHAMP DE MORT / FESTIN DE MORT (1d3/Niv, 100% soin, L3 Niv>=18 PV temp 24s)
    if (nSpell == FORCE_POWER_DRAIN_LIFE || nSpell == FORCE_POWER_DEATH_FIELD)
    {{
        float fRad = (nSpell == FORCE_POWER_DEATH_FIELD) ? 10.0 : 0.0;
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
                if (FortitudeSave(oCur, nDC, SAVING_THROW_TYPE_NONE, oCaster)) nDmg = nDmg / 2;
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
            if (nSpell == FORCE_POWER_DEATH_FIELD && nLevel >= 18 && nTotalHeal > nMissing)
            {{
                int nOver = nTotalHeal - nMissing;
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

    // 6. VAGUE DE FORCE -> TOURBILLON AoE 6m / 12s
    if (nSpell == FORCE_POWER_FORCE_WAVE)
    {{
        object oCur = GetFirstObjectInShape(SHAPE_SPHERE, 6.0, GetSpellTargetLocation(), FALSE, OBJECT_TYPE_CREATURE);
        while (GetIsObjectValid(oCur))
        {{
            if (GetIsEnemy(oCur, oCaster) && !GetIsDead(oCur))
            {{
                SignalEvent(oCur, EventSpellCastAt(oCaster, nSpell, TRUE));
                int nDmg = Sp_CalcDamage(oCur, 0, 0, nLevel);
                if (ReflexSave(oCur, nDC, SAVING_THROW_TYPE_NONE, oCaster))
                {{
                    ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectDamage(nDmg / 2, DAMAGE_TYPE_BLUDGEONING), oCur);
                }}
                else
                {{
                    ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectDamage(nDmg, DAMAGE_TYPE_BLUDGEONING), oCur);
                    effect eWhirl = EffectLinkEffects(EffectWhirlWind(), EffectVisualEffect(VFX_IMP_FORCE_WHIRLWIND));
                    ApplyEffectToObject(DURATION_TYPE_TEMPORARY, eWhirl, oCur, Sp_CalcDuration(12.0));
                }}
            }}
            oCur = GetNextObjectInShape(SHAPE_SPHERE, 6.0, GetSpellTargetLocation(), FALSE, OBJECT_TYPE_CREATURE);
        }}
        return TRUE;
    }}

    // 7. BARRIERE DE FORCE & RESISTANCE A L'ENERGIE (RD 4/8/12, personnel, 60s)
    if (nSpell == FORCE_POWER_FORCE_BARRIER || nSpell == FORCE_POWER_IMPROVED_FORCE_BARRIER || nSpell == FORCE_POWER_MASTER_FORCE_BARRIER)
    {{
        int nRD = (nSpell == FORCE_POWER_FORCE_BARRIER) ? 4 : ((nSpell == FORCE_POWER_IMPROVED_FORCE_BARRIER) ? 8 : 12);
        effect eB = EffectLinkEffects(EffectDamageResistance(DAMAGE_TYPE_BLUDGEONING, nRD), EffectDamageResistance(DAMAGE_TYPE_PIERCING, nRD));
        eB = EffectLinkEffects(eB, EffectDamageResistance(DAMAGE_TYPE_SLASHING, nRD));
        ApplyEffectToObject(DURATION_TYPE_TEMPORARY, eB, oCaster, Sp_CalcDuration(60.0));
        return TRUE;
    }}
    if (nSpell == FORCE_POWER_RESIST_COLD_HEAT_ENERGY || nSpell == FORCE_POWER_RESIST_POISON_DISEASE_SONIC || nSpell == FORCE_POWER_MASTER_ENERGY_RESISTANCE)
    {{
        int nRD = (nSpell == FORCE_POWER_RESIST_COLD_HEAT_ENERGY) ? 4 : ((nSpell == FORCE_POWER_RESIST_POISON_DISEASE_SONIC) ? 8 : 12);
        effect eE = EffectLinkEffects(EffectDamageResistance(DAMAGE_TYPE_BLASTER, nRD), EffectDamageResistance(DAMAGE_TYPE_FIRE, nRD));
        eE = EffectLinkEffects(eE, EffectDamageResistance(DAMAGE_TYPE_COLD, nRD));
        eE = EffectLinkEffects(eE, EffectDamageResistance(DAMAGE_TYPE_ELECTRICAL, nRD));
        eE = EffectLinkEffects(eE, EffectDamageResistance(DAMAGE_TYPE_SONIC, nRD));
        ApplyEffectToObject(DURATION_TYPE_TEMPORARY, eE, oCaster, Sp_CalcDuration(60.0));
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

    // 9. ULTIMES : STIGMATE (FURY I-III), ECRASEMENT (FORCE_CRUSH), DECHIRURE (CRUSH_OPPOSITION I-III)
    if (nSpell == FORCE_POWER_FURY || nSpell == FORCE_POWER_IMPROVED_FURY || nSpell == FORCE_POWER_MASTER_FURY)
    {{
        int nBon = (nSpell == FORCE_POWER_FURY) ? 2 : ((nSpell == FORCE_POWER_IMPROVED_FURY) ? 4 : 6);
        effect eF = EffectLinkEffects(EffectAbilityIncrease(ABILITY_STRENGTH, nBon), EffectAbilityIncrease(ABILITY_DEXTERITY, nBon));
        eF = EffectLinkEffects(eF, EffectModifyAttacks(1));
        eF = EffectLinkEffects(eF, EffectImmunity(IMMUNITY_TYPE_PARALYSIS));
        ApplyEffectToObject(DURATION_TYPE_TEMPORARY, eF, oCaster, Sp_CalcDuration(30.0));
        DelayCommand(6.0, Ov_StigmateTick(oCaster, 5));
        return TRUE;
    }}
    if (nSpell == FORCE_POWER_FORCE_CRUSH)
    {{
        if (GetIsObjectValid(oTarget) && !GetIsDead(oTarget))
        {{
            SignalEvent(oTarget, EventSpellCastAt(oCaster, nSpell, TRUE));
            int nDmg = Sp_CalcDamage(oTarget, nLevel, 8);
            int bSaved = FortitudeSave(oTarget, nDC, SAVING_THROW_TYPE_NONE, oCaster);
            if (bSaved) nDmg = nDmg / 2;
            ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectDamage(nDmg, DAMAGE_TYPE_BLUDGEONING), oTarget);
            if (!bSaved) ApplyEffectToObject(DURATION_TYPE_TEMPORARY, EffectParalyze(), oTarget, 6.0);
        }}
        return TRUE;
    }}
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
            }}
            oCur = GetNextObjectInShape(SHAPE_SPHERE, 15.0, GetLocation(oCaster), FALSE, OBJECT_TYPE_CREATURE);
        }}
        return TRUE;
    }}

    return FALSE;
}}
'''
    (SRC_DIR / "ov_inc_powers.nss").write_text(code, encoding="latin1")
    return code


def build_force_powers(fids: dict[str, int]) -> None:
    """Patch k_inc_force.nss (Metamagie: Amplifie +15/30/50%, Penetrant +2/4/6 DD, Prolonge x2)
    et compile k_sp1_generic.nss -> k_sp1_generic.ncs."""
    inc = (REF_SCRIPTS / "k_inc_force.nss").read_text(encoding="latin1")

    emp1, emp2, emp3 = fids["MOD_META_EMPOWER_1"], fids["MOD_META_EMPOWER_2"], fids["MOD_META_EMPOWER_3"]
    pen1, pen2, pen3 = fids["MOD_META_PENETRATE_1"], fids["MOD_META_PENETRATE_2"], fids["MOD_META_PENETRATE_3"]
    ext1 = fids["MOD_META_EXTEND"]

    # 1. Sp_CalcDamage : Pouvoir Amplifie I-III (+15% / +30% / +50%)
    dmg_anchor = "if( IsFormActive( OBJECT_SELF, FORM_FORCE_I_FOCUS ) )"
    assert dmg_anchor in inc, "Sp_CalcDamage anchor not found"
    emp_code = f'''// Overhaul Metamagie : Pouvoir Amplifie I-III (+15% / +30% / +50%)
    if (GetHasFeat({emp3}, OBJECT_SELF)) {{ nDamage = (nDamage * 150) / 100; }}
    else if (GetHasFeat({emp2}, OBJECT_SELF)) {{ nDamage = (nDamage * 130) / 100; }}
    else if (GetHasFeat({emp1}, OBJECT_SELF)) {{ nDamage = (nDamage * 115) / 100; }}
    ''' + dmg_anchor
    inc = inc.replace(dmg_anchor, emp_code, 1)

    # 2. Sp_CalcDuration : Pouvoir Prolonge (x2)
    dur_anchor = "if( IsFormActive( OBJECT_SELF, FORM_FORCE_IV_MASTERY ) )"
    assert dur_anchor in inc, "Sp_CalcDuration anchor not found"
    ext_code = f'''// Overhaul Metamagie : Pouvoir Prolonge (duree x2)
    if (GetHasFeat({ext1}, OBJECT_SELF)) {{ fFinalDuration = fFinalDuration * 2.0f; }}
    ''' + dur_anchor
    inc = inc.replace(dur_anchor, ext_code, 1)

    # 3. Sp_MySavingThrows : Pouvoir Penetrant I-III (+2 / +4 / +6 DD)
    dc_anchor = "if( IsFormActive( OBJECT_SELF, FORM_FORCE_IV_MASTERY ) ) {\n        // +2 bonus to DC."
    if dc_anchor not in inc:
        dc_anchor = "if( IsFormActive( OBJECT_SELF, FORM_FORCE_IV_MASTERY ) ) {\r\n        // +2 bonus to DC."
    assert dc_anchor in inc, "Sp_MySavingThrows anchor not found"
    pen_code = f'''// Overhaul Metamagie : Pouvoir Penetrant I-III (+2 / +4 / +6 DD)
    if (GetHasFeat({pen3}, OBJECT_SELF)) {{ nMod += 6; }}
    else if (GetHasFeat({pen2}, OBJECT_SELF)) {{ nMod += 4; }}
    else if (GetHasFeat({pen1}, OBJECT_SELF)) {{ nMod += 2; }}
    ''' + dc_anchor
    inc = inc.replace(dc_anchor, pen_code, 1)

    (SRC_DIR / "k_inc_force.nss").write_text(inc, encoding="latin1")
    build_ov_inc_powers(fids)
    sp1 = (REF_SCRIPTS / "k_sp1_generic.nss").read_text(encoding="latin1")
    # Inclure ov_inc_powers apres k_inc_force
    sp1 = sp1.replace('#include "k_inc_force"', '#include "k_inc_force"\n#include "ov_inc_powers"', 1)
    # Garde-fou armures legeres speciales (baseitem 98 Ubese / 102 Zeison Sha, Jal Shey, Malak) :
    # aucune exception aux restrictions de pouvoirs (bloque tous les pouvoirs 0x003f Robe uniquement).
    zs_guard = '''
int Ov_IsRobeOnlyPower(int nSp)
{
    if (nSp == FORCE_POWER_SPEED_BURST || nSp == FORCE_POWER_KNIGHT_SPEED || nSp == FORCE_POWER_SPEED_MASTERY) return TRUE;
    if (nSp == FORCE_POWER_FORCE_AURA || nSp == FORCE_POWER_FORCE_SHIELD || nSp == FORCE_POWER_FORCE_ARMOR) return TRUE;
    if (nSp == FORCE_POWER_SHOCK || nSp == FORCE_POWER_LIGHTNING || nSp == FORCE_POWER_FORCE_STORM) return TRUE;
    if (nSp == FORCE_POWER_DRAIN_LIFE || nSp == FORCE_POWER_DEATH_FIELD) return TRUE;
    if (nSp == FORCE_POWER_WOUND || nSp == FORCE_POWER_CHOKE || nSp == FORCE_POWER_KILL) return TRUE;
    if (nSp == FORCE_POWER_STUN || nSp == FORCE_POWER_HOLD || nSp == FORCE_POWER_SLEEP) return TRUE;
    if (nSp == FORCE_POWER_RESIST_FORCE || nSp == FORCE_POWER_SUPRESS_FORCE) return TRUE;
    if (nSp == FORCE_POWER_BATTLE_MEDITATION_PC || nSp == FORCE_POWER_IMPROVED_BATTLE_MEDITATION_PC || nSp == FORCE_POWER_MASTER_BATTLE_MEDITATION_PC) return TRUE;
    if (nSp == FORCE_POWER_FORCE_CAMOUFLAGE || nSp == FORCE_POWER_IMPROVED_FORCE_CAMOUFLAGE || nSp == FORCE_POWER_MASTER_FORCE_CAMOUFLAGE) return TRUE;
    if (nSp == FORCE_POWER_BATTLE_PRECOGNITION) return TRUE;
    return FALSE;
}
'''
    m_main = re.search(r"void\s+main\s*\(\s*\)\s*\{", sp1)
    assert m_main, "main() not found in k_sp1_generic.nss"
    guard_call = '''
    {
        object oArm = GetItemInSlot(INVENTORY_SLOT_BODY, OBJECT_SELF);
        if (GetIsObjectValid(oArm))
        {
            int nBI = GetBaseItemType(oArm);
            if ((nBI == 98 || nBI == 102) && Ov_IsRobeOnlyPower(GetSpellId()))
            {
                ApplyEffectToObject(DURATION_TYPE_INSTANT, EffectHealForcePoints(30), OBJECT_SELF);
                return;
            }
        }
        if (Ov_HandleCustomPower(GetSpellId()))
        {
            return;
        }
    }
'''
    sp1 = sp1[:m_main.start()] + zs_guard + "\n" + sp1[m_main.start():m_main.end()] + guard_call + sp1[m_main.end():]
    compile_script("k_sp1_generic", sp1)


def build_personal_crystal_script() -> None:
    """Compile a_q_cryst_change.ncs : attribue automatiquement le Cristal personnel 3 paliers
    (ov_crys_<tier>_<s1><s2>) selon les 2 meilleures caracs de base et le niveau de l'Exile."""
    code = '''//:: a_q_cryst_change - Cristal personnel de l'Exile 3 paliers (KotOR 2 Overhaul)
void main()
{
    object oPC = GetFirstPC();
    if (!GetIsObjectValid(oPC)) return;

    int nLvl = GetHitDice(oPC);
    int nTier = 1;
    if (nLvl >= 22) nTier = 3;
    else if (nLvl >= 15) nTier = 2;

    // Trouver les 2 meilleures caracteristiques de base (0=FOR..5=CHA)
    int nBest1 = 0;
    int nVal1 = -1;
    int i = 0;
    while (i < 6)
    {
        int v = GetAbilityScore(oPC, i);
        if (v > nVal1) { nVal1 = v; nBest1 = i; }
        i += 1;
    }
    int nBest2 = (nBest1 == 0) ? 1 : 0;
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
    print(f"=== Build Jalon 3 (NWScript .nss -> .ncs) -> {OVR_DIR} ===")
    build_ov_inc_core(fids)
    build_wrappers()
    build_grenades(fids)
    build_force_powers(fids)
    build_personal_crystal_script()
    print("=== Jalon 3 BUILD OK (tous les scripts compilés sans erreur) ===")


if __name__ == "__main__":
    main()
