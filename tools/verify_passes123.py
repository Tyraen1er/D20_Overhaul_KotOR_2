"""Comprehensive verification suite for Passes 1, 2, and 3 of KotOR 2 D20 Overhaul."""
import configparser
import json
import re
from pathlib import Path
from pykotor.common.language import Gender, Language
from pykotor.resource.formats.gff import read_gff
from pykotor.resource.generics.dlg import read_dlg
from pykotor.resource.formats.tlk import read_tlk
from pykotor.resource.formats.twoda import read_2da
from pykotor.resource.generics.utc import read_utc
from pykotor.resource.generics.uti import read_uti

ROOT = Path(r"C:\Users\emman\Desktop\dev\Kotor 2 Mods")
MOD = ROOT / "mods" / "overhaul"
OVR = MOD / "Override"
SRC = MOD / "src"
TSL = ROOT / "installer" / "tslpatchdata"

errors: list[str] = []
passed: list[str] = []

def check(cond: bool, msg: str) -> None:
    if cond:
        passed.append(msg)
    else:
        errors.append(msg)

fids = json.loads((MOD / "feat_ids.json").read_text(encoding="utf-8"))
sids = json.loads((MOD / "spell_ids.json").read_text(encoding="utf-8"))
tlk = read_tlk(MOD / "dialog.tlk")

# =========================================================================
# PASS 1 CHECKS
# =========================================================================
sp = read_2da(OVR / "spells.2da")
sp_by_lbl = {sp.get_row(i).get_string("label"): i for i in range(len(sp))}

# 1.1 Previously missed 17+6 spells synced cleanly
expected_spells = [
    ("FORCE_POWER_DROID_STUN", "0x0030", "10"),
    ("FORCE_POWER_DROID_DISABLE", "0x0030", "20"),
    ("FORCE_POWER_DROID_DESTROY", "0x0030", "35"),
    ("FORCE_POWER_LIGHTNING", "0x003f", "30"),
    ("FORCE_POWER_SPEED_MASTERY", "0x003f", "45"),
    ("FORCE_POWER_MASS_STASIS", "0x003f", "50"),
    ("FORCE_POWER_RESIST_ENERGY_1", "0x0030", "15"),
    ("FORCE_POWER_RESIST_ENERGY_2", "0x0030", "25"),
    ("FORCE_POWER_MASTER_ENERGY_RESISTANCE", "0x0030", "35"),
    ("FORCE_POWER_RESIST_FORCE", "0x0000", "20"),
    ("FORCE_POWER_SUPRESS_FORCE", "0x003c", "20"),
    ("FORCE_POWER_BATTLE_MEDITATION_PC", "0x0030", "25"),
    ("FORCE_POWER_IMPROVED_BATTLE_MEDITATION_PC", "0x0030", "35"),
    ("FORCE_POWER_MASTER_BATTLE_MEDITATION_PC", "0x0030", "50"),
    ("FORCE_POWER_FORCE_CAMOUFLAGE", "0x0030", "0"),
    ("FORCE_POWER_IMPROVED_FORCE_CAMOUFLAGE", "0x0030", "0"),
    ("FORCE_POWER_MASTER_FORCE_CAMOUFLAGE", "0x0030", "0"),
    ("FORCE_POWER_MIND_TRICK", "0x0030", "15"),
    ("FORCE_POWER_CONFUSION", "0x0030", "35"),
    ("FORCE_POWER_DOMINATE", "0x0000", "0"),
    ("FORCE_POWER_FORCE_BODY", "0x0000", "0"),
    ("FORCE_POWER_FORCE_REPULSION", "0x0000", "0"),
    ("FORCE_POWER_FORCE_REDIRECTION", "0x0000", "0"),
    ("FORCE_POWER_BATTLE_PRECOGNITION", "0x0000", "0"),
    ("FORCE_POWER_PRECOGNITION", "0x0000", "0"),
    ("FORCE_POWER_DEATH_FIELD", "0x003f", "40"),
    ("FORCE_POWER_DEATH_FEAST", "0x003f", "55"),
    ("FORCE_POWER_FORCE_SCAR_I", "0x0000", "20"),
    ("FORCE_POWER_FORCE_SCAR_II", "0x0000", "30"),
    ("FORCE_POWER_FORCE_SCAR_III", "0x0000", "40"),
]
for lbl, exp_mask, exp_fp in expected_spells:
    r = sp.get_row(sp_by_lbl[lbl])
    check(r.get_string("forbiditemmask") == exp_mask and r.get_string("forcepoints") == exp_fp,
          f"spells.2da {lbl}: mask={r.get_string('forbiditemmask')}({exp_mask}) fp={r.get_string('forcepoints')}({exp_fp})")

# Enlightenment instant cast
r_enl = sp.get_row(180)
check(r_enl.get_string("conjtime") == "0" and r_enl.get_string("casttime") == "0",
      f"FORCE_ENLIGHTENMENT instant cast: conj={r_enl.get_string('conjtime')} cast={r_enl.get_string('casttime')}")

# Prestige names renamed in TLK & ranks IV-VI masked
for lbl, exp_nm in [
    ("FORCE_POWER_INSPIRE_FOLLOWERS_I", "Écho des Liens I"),
    ("FORCE_POWER_CRUSH_OPPOSITION_I", "Déchirure de la Force I"),
    ("FORCE_POWER_FURY", "Stigmate de Force I"),
    ("FORCE_POWER_FORCE_CAMOUFLAGE", "Spectre de la Force I"),
    ("FORCE_POWER_FORCE_SCAR_I", "Cicatrice de Force I"),
    ("FORCE_POWER_DEATH_FEAST", "Festin de mort"),
]:
    nm_ref = int(sp.get_row(sp_by_lbl[lbl]).get_string("name"))
    check(tlk.get(nm_ref).text == exp_nm, f"TLK rename {lbl} = {tlk.get(nm_ref).text!r}")
for dead_r in (147, 148, 149, 170, 171, 172):
    r = sp.get_row(dead_r)
    check(r.get_string("sithlord") == "-1" and r.get_string("jedimaster") == "-1" and r.get_string("prerequisites") == "",
          f"spells.2da row {dead_r} (rank IV-VI) masked")

# 1.2 classpowergain jgd Lv 1 = 2
pg = read_2da(OVR / "classpowergain.2da")
jgd_vals = [int(pg.get_row(i).get_string("jgd")) for i in range(30)]
check(jgd_vals[0] == 2 and sum(jgd_vals[:15]) == 6 and sum(jgd_vals[:30]) == 12,
      f"classpowergain jgd: lv1={jgd_vals[0]}, lv15={sum(jgd_vals[:15])}, lv30={sum(jgd_vals[:30])}")

# 1.3 itemcreate.2da & itemcreatemira.2da + 2 missing weapon UTIs
ic = read_2da(OVR / "itemcreate.2da")
ic_map = {ic.get_row(i).get_string("label").lower(): ic.get_row(i) for i in range(len(ic))}
check("w_rocket_01" not in ic_map, "itemcreate.2da excludes Mira rockets")
for wrr, exp_sk in [("w_melee_01", "2"), ("w_melee_ww_base", "6"), ("w_brifle_hr_base", "8"), ("w_blaste_01", "2")]:
    check(wrr in ic_map and ic_map[wrr].get_string("group") == "4" and ic_map[wrr].get_string("skill") == exp_sk,
          f"itemcreate.2da {wrr}: grp={ic_map[wrr].get_string('group')} sk={ic_map[wrr].get_string('skill')}")
check((OVR / "w_melee_ww_base.uti").exists() and (OVR / "w_brifle_hr_base.uti").exists(),
      "2 missing craftable weapon UTIs generated")
icm = read_2da(OVR / "itemcreatemira.2da")
icm_map = {icm.get_row(i).get_string("label").lower(): icm.get_row(i) for i in range(len(icm))}
for rrr, exp_lv in [("w_rocket_01", "0"), ("w_rocket_02", "10"), ("w_rocket_03", "15"), ("w_rocket_04", "20"), ("w_rocket_05", "20")]:
    check(rrr in icm_map and icm_map[rrr].get_string("level") == exp_lv,
          f"itemcreatemira.2da {rrr}: level={icm_map[rrr].get_string('level')}({exp_lv})")

# 1.4 Enemy hides fixed (prop 25, subtype 5, no combat regen on beast_l, no phys imm on assn)
for hrr, exp_prop in [("ov_hide_sith_l2", 25), ("ov_hide_sith_l3", 25)]:
    u = read_uti(OVR / f"{hrr}.uti")
    props = [p.property_name for p in u.properties]
    check(exp_prop in props and 39 not in props, f"{hrr}: props={props} (25 present, 39 absent)")
for hrr in ("ov_hide_beast_m", "ov_hide_beast_l"):
    u = read_uti(OVR / f"{hrr}.uti")
    imm_subs = [p.subtype for p in u.properties if p.property_name == 24]
    has_regen = any(p.property_name == 35 for p in u.properties)
    check(imm_subs == [5] and not has_regen, f"{hrr}: imm_subs={imm_subs} regen={has_regen}")
u_assn = read_uti(OVR / "ov_hide_assn.uti")
check(not any(p.property_name == 14 for p in u_assn.properties), f"ov_hide_assn: no phys immunity")

# 1.5 Items fixed (e_imp4_08 + 5 saber deflect penalties + Hold_Out_Blaster Massive Crits)
u_imp = read_uti(OVR / "e_imp4_08.uti")
ab_vals = sorted((p.subtype, p.cost_value) for p in u_imp.properties if p.property_name == 0)
check(ab_vals == [(i, 1) for i in range(6)], f"e_imp4_08 stats = {ab_vals}")

for srr, exp_pen in [("u_l_emit_04", 1), ("u_l_emit_08", 1), ("u_l_lens_03", 2), ("u_l_lens_08", 2), ("u_l_lens_13", 3)]:
    u = read_uti(OVR / f"{srr}.uti")
    pens = [(p.cost_table, p.cost_value) for p in u.properties if p.property_name == 56]
    check(pens == [(21, exp_pen)], f"{srr} deflect penalty = {pens} (expected [(21, {exp_pen})])")

for hrr, min_cv in [("w_blaste_03", 8), ("w_blaste_07", 8), ("g_w_hldoblstr002", 8), ("w_blaste_27", 10)]:
    u = read_uti(OVR / f"{hrr}.uti")
    mcs = [p.cost_value for p in u.properties if p.property_name == 49]
    check(bool(mcs) and max(mcs) >= min_cv, f"{hrr} Massive Criticals cv={mcs} (>={min_cv})")

# =========================================================================
# PASS 2 CHECKS
# =========================================================================
ft = read_2da(OVR / "feat.2da")
ft_by_lbl = {ft.get_row(i).get_string("label"): i for i in range(len(ft))}

# Evasion selectable JWA/SAS/JSN(Visas) at Lv 15
r_ev = ft.get_row(125)
check(r_ev.get_string("jwa_list") == "1" and r_ev.get_string("sas_list") == "1"
      and r_ev.get_string("mincharlevel") == "15"
      and r_ev.get_string("prereqfeat1") == str(fids["MOD_PRESTIGE_HYBRID"]),
      "FEAT_EVASION configured for JWA/SAS/Visas Lv15")

# Unbound Force auto-granted 1/5/9
for i, lvl in enumerate(("1", "5", "9"), 1):
    r = ft.get_row(fids[f"MOD_UNBOUND_FORCE_{i}"])
    check(r.get_string("jwa_list") == "4" and r.get_string("jwa_granted") == lvl,
          f"MOD_UNBOUND_FORCE_{i}: auto-granted jwa_granted={r.get_string('jwa_granted')}")

# R1 prereqs & Droid/Laser gating
check(ft.get_row(fids["MOD_ARMOR_LIGHT_1"]).get_string("prereqfeat1") == "5", "MOD_ARMOR_LIGHT_1 prereq=5")
check(ft.get_row(fids["MOD_ARMOR_MED_1"]).get_string("prereqfeat1") == "6", "MOD_ARMOR_MED_1 prereq=6")
check(ft.get_row(fids["MOD_ARMOR_HEAVY_1"]).get_string("prereqfeat1") == "4", "MOD_ARMOR_HEAVY_1 prereq=4")
check(ft.get_row(fids["MOD_SPEC_LASER_1"]).get_string("prereqfeat1") == "43", "MOD_SPEC_LASER_1 prereq=43")
check(ft.get_row(fids["MOD_SPEC_BLUNT_1"]).get_string("prereqfeat1") == "44", "MOD_SPEC_BLUNT_1 prereq=44")
check(ft.get_row(fids["MOD_SPEC_ASSAULT_1"]).get_string("orreqfeat0") == "39"
      and ft.get_row(fids["MOD_SPEC_ASSAULT_1"]).get_string("orreqfeat1") == "40", "MOD_SPEC_ASSAULT_1 orreq 39|40")

r_las3 = ft.get_row(fids["MOD_SPEC_LASER_3"])
check(r_las3.get_string("jwm_list") == "1" and r_las3.get_string("sma_list") == "1"
      and r_las3.get_string("sol_list") == "4" and r_las3.get_string("drc_list") == "4",
      "MOD_SPEC_LASER_3 restricted strictly to JWM/SMA")
r_vib3 = ft.get_row(fids["MOD_SPEC_VIBRO_3"])
check(r_vib3.get_string("drc_list") == "4" and r_vib3.get_string("drx_list") == "4", "Melee R3 blocks droids")
r_ass3 = ft.get_row(fids["MOD_SPEC_ASSAULT_3"])
check(r_ass3.get_string("drc_list") == "1" and r_ass3.get_string("drx_list") == "4", "Ranged R3 allows drc, blocks drx")

# forceshields.2da
fs = read_2da(OVR / "forceshields.2da")
check(len(fs) == 126 and fs.get_row(6).get_string("amount") == "40"
      and fs.get_row(27).get_string("amount") == "50"
      and fs.get_row(48).get_string("amount") == "80"
      and fs.get_row(69).get_string("amount") == "100"
      and fs.get_row(90).get_string("amount") == "120"
      and fs.get_row(111).get_string("amount") == "150",
      f"forceshields.2da 126 rows with exact x1/x1.25/x2/x2.5/x3/x3.75 amounts")

# =========================================================================
# PASS 3 & SCRIPTS CHECKS
# =========================================================================
expected_ncs = [
    "k_sp1_generic.ncs", "k_hen_heartbt01.ncs", "k_def_heartbt01.ncs",
    "k_hen_damage01.ncs", "k_def_damage01.ncs", "k_hen_attacked01.ncs",
    "k_def_attacked01.ncs", "k_def_death01.ncs", "k_sup_bands.ncs",
    "k_sup_healing.ncs", "k_trp_generic.ncs", "k_sup_grenade.ncs",
    "a_addcombatpre.ncs", "a_q_cryst_change.ncs",
    "ov_gam_use.ncs", "ov_gam_end.ncs", "ov_gam_c_can.ncs", "ov_gam_a_upgr.ncs", "ov_gam_a_swap.ncs", "ov_gam_a_ref.ncs",
]
for ncs in expected_ncs:
    check((OVR / ncs).exists() and (OVR / ncs).stat().st_size >= 80, f"Compiled {ncs}")

core_txt = (SRC / "ov_inc_core.nss").read_text(encoding="latin1")
pow_txt = (SRC / "ov_inc_powers.nss").read_text(encoding="latin1")
sp1_txt = (SRC / "k_sp1_generic.nss").read_text(encoding="latin1")
gr_txt = (SRC / "k_sup_grenade.nss").read_text(encoding="latin1")

check("LocalNumber(oAtk, 29)" not in core_txt and ", 29)" not in core_txt, "No invalid LocalNumber 29 in ov_inc_core")
check("Ov_PartyTick6s" in core_txt and "GetTimeSecond()" in core_txt and "SetLocalNumber(oPC, 16, nSlot)" in core_txt, "1x/6s clock-based party tick gate active (save/load safe)")
check("Ov_HasPersonalCrystal" in core_txt and "GetItemHasItemProperty(oR, 62)" in core_txt, "Personal crystal checks prop 62 mounted")
check("Ov_IsRobeOnlyPower" not in sp1_txt, "Broken Ov_IsRobeOnlyPower removed from k_sp1_generic")
check("(nSpell == FORCE_POWER_RESIST_POISON_DISEASE_SONIC) ? 4" in pow_txt, "Energy Resistance L1/L2 inversion fixed")
check("SHAPE_SPELLCONE" in pow_txt and "16.0" in pow_txt, "Lightning restored to 16m cone")
check("DAMAGE_TYPE_ACID" in pow_txt, "Force Crush & Saber Throw L2 use Unstoppable (ACID)")
check("nSpell == 185 || (nSpell >= 190 && nSpell <= 199)" in gr_txt, "Rocket/Dart +2 DC fixed in k_sup_grenade")
check("Ov_GetGrenadeResRef" in gr_txt and "Ov_HasGand3" in gr_txt, "Gand III implemented in k_sup_grenade")
check("Ov_CheckMatukaiPunish" in core_txt and "Ov_CheckMatukaiPunish" in pow_txt and "Ov_CheckMatukaiPunish" in gr_txt, "Matukai II punish wired across combat/powers/grenades")

# kreia.dlg check
dlg_path = OVR / "kreia.dlg"
check(dlg_path.exists() and dlg_path.stat().st_size > 1_000_000, f"kreia.dlg generated ({dlg_path.stat().st_size if dlg_path.exists() else 0} bytes)")
if dlg_path.exists():
    g = read_gff(dlg_path)
    entries = g.root.get_list("EntryList")
    replies = g.root.get_list("ReplyList")
    e288 = entries.at(288)
    check(str(e288.get_resref("Script")) == "" and len(e288.get_list("RepliesList")) == 2,
          "kreia.dlg Entry[288] patched with 2 choices (Auto + Manual)")
    r_auto_i = e288.get_list("RepliesList").at(0).get_uint32("Index")
    r_man_i = e288.get_list("RepliesList").at(1).get_uint32("Index")
    check(r_auto_i < len(replies) and r_man_i < len(replies),
          f"kreia.dlg Reply indices valid ({r_auto_i}, {r_man_i} < {len(replies)})")
    # Walk manual choice tree: 6 primaries -> 5 secondaries = 30 pairs with ActionParam1/2
    r_man = replies.at(r_man_i)
    e_ask1_i = r_man.get_list("EntriesList").at(0).get_uint32("Index")
    e_ask1 = entries.at(e_ask1_i)
    pairs = set()
    for p_lk_i in range(6):
        rp_i = e_ask1.get_list("RepliesList").at(p_lk_i).get_uint32("Index")
        e_ask2_i = replies.at(rp_i).get_list("EntriesList").at(0).get_uint32("Index")
        e_ask2 = entries.at(e_ask2_i)
        for s_lk_i in range(len(e_ask2.get_list("RepliesList"))):
            rs_i = e_ask2.get_list("RepliesList").at(s_lk_i).get_uint32("Index")
            rs = replies.at(rs_i)
            if str(rs.get_resref("Script")) == "a_q_cryst_change":
                pairs.add((rs.get_int32("ActionParam1"), rs.get_int32("ActionParam2")))
    check(len(pairs) == 30, f"kreia.dlg manual crystal tree covers all 30 (s1,s2) pairs (found {len(pairs)})")
    dlg_obj = read_dlg(dlg_path)
    check(len(dlg_obj.starters) > 0, f"kreia.dlg loads cleanly via read_dlg (starters={len(dlg_obj.starters)})")

# Installer checks
check((TSL / "forceshields.2da").exists() and (TSL / "itemcreatemira.2da").exists() and (TSL / "kreia.dlg").exists(),
      "Installer tslpatchdata contains forceshields.2da, itemcreatemira.2da, kreia.dlg")
info_rtf = (TSL / "info.rtf").read_text(encoding="ascii")
check("24 nouvelles" not in info_rtf and "60 am" in info_rtf, "info.rtf updated (no obsolete '24 combinées')")

# No literal **** in any Override 2DA
for p2da in sorted(OVR.glob("*.2da")):
    t = read_2da(p2da)
    has_star = any(t.get_row(i).get_string(h) == "****" for i in range(len(t)) for h in t.get_headers())
    check(not has_star, f"No literal '****' in {p2da.name}")

# Check enemy UTCs count & MOD_BOSS_RD
utc_files = list(OVR.glob("*.utc"))
boss_marked = sum(1 for p in utc_files if fids["MOD_BOSS_RD"] in read_utc(p).feats)
check(len(utc_files) >= 180 and boss_marked >= 50, f"Enemy UTCs={len(utc_files)}, boss_marked={boss_marked}")
check(not any(k in p.stem.lower() for p in utc_files for k in ("cut", "dead", "body", "dummy", "fakpc")), "Zero cutscene/dead/dummy UTCs in Override")

# =========================================================================
# DESIGN CHOICES CHECKS (RD 2/3/4/6/12 + GAMORREAN II ADAPTER 2M <-> 1M)
# =========================================================================
rc = read_2da(OVR / "iprp_resistcost.2da")
check(len(rc) == 12
      and rc.get_row(7).get_string("amount") == "2"
      and rc.get_row(8).get_string("amount") == "3"
      and rc.get_row(9).get_string("amount") == "4"
      and rc.get_row(10).get_string("amount") == "6"
      and rc.get_row(11).get_string("amount") == "12",
      "iprp_resistcost.2da extended cleanly with 2/3/4/6/12")

rd_expected = [
    ("e_imp2_08", 7), ("e_imp3_08", 7), ("a_gloves_19", 7), ("a_belt_17", 7),
    ("a_helmet_28", 8), ("a_belt_28", 8), ("g_i_cermshield", 8), ("a_heavy_12", 8), ("a_light_11", 8),
    ("a_light_10", 11), ("a_light_15", 11), ("a_medium_12", 11), ("g_a_armrdfsuit", 11),
    ("ov_hide_beast_m", 9), ("ov_hide_beast_l", 10),
]
for rrr, exp_cv in rd_expected:
    u = read_uti(OVR / f"{rrr}.uti")
    rd_cvs = {p.cost_value for p in u.properties if p.property_name == 17}
    check(rd_cvs == {exp_cv}, f"{rrr} RD cost_values={rd_cvs} (expected {{{exp_cv}}})")

check((TSL / "iprp_resistcost.2da").exists() and (TSL / "ov_gam_adapt.uti").exists() and (TSL / "ov_gam_term.utp").exists() and (TSL / "ov_gam_conv.dlg").exists() and (TSL / "ov_gam_end.ncs").exists(),
      "Installer includes iprp_resistcost.2da, ov_gam_adapt.uti, ov_gam_term.utp, ov_gam_conv.dlg, ov_gam_end.ncs")

u_adapt = read_uti(OVR / "ov_gam_adapt.uti")
adapt_name_fr = u_adapt.name.get(Language.FRENCH, Gender.MALE) or ""
adapt_desc_fr = u_adapt.description.get(Language.FRENCH, Gender.MALE) or ""
check((not u_adapt.plot) and u_adapt.base_item == 54 and u_adapt.charges == 1 and any(p.property_name == 10 and p.subtype == sids["ITEM_ABILITY_GAMORREAN_ADAPT"] and p.cost_table == 3 and p.cost_value == 13 for p in u_adapt.properties),
      f"ov_gam_adapt.uti bi={u_adapt.base_item} (54=Combat_Shots), chg={u_adapt.charges}, Unlimited_Use (cv=13), plot=False")
check("<" not in adapt_name_fr and ">" not in adapt_name_fr and "Adaptateur Gamorréen" in adapt_name_fr,
      f"ov_gam_adapt.uti clean name without token brackets: {adapt_name_fr!r}")
check("établi de campagne" in adapt_desc_fr and "posture hors combat" in adapt_desc_fr and "Raffinement Gamorréen II" in adapt_desc_fr,
      "ov_gam_adapt.uti description includes Gamorrean lore + HRP instructions + posture hors combat")

gam2_desc_ref = int(ft.get_row(fids["MOD_GAMORREAN_2"]).get_string("description"))
gam2_desc_txt = tlk.get(gam2_desc_ref).text
check(gam2_desc_txt.startswith("[Mod D20-Overhaul]") and "Adaptateur Gamorréen" in gam2_desc_txt and "Validé en jeu" not in gam2_desc_txt,
      "MOD_GAMORREAN_2 TLK description aligned cleanly (CSV col 8 fixed, no dev note leak)")

r_gam_sp = sp.get_row(sids["ITEM_ABILITY_GAMORREAN_ADAPT"])
check(r_gam_sp.get_string("category") == "0x1808" and r_gam_sp.get_string("impactscript") == "ov_gam_use",
      f"ITEM_ABILITY_GAMORREAN_ADAPT category={r_gam_sp.get_string('category')} (0x1808 stim) impactscript={r_gam_sp.get_string('impactscript')}")

from pykotor.resource.generics.utp import read_utp
u_term = read_utp(OVR / "ov_gam_term.utp")
check(u_term.tag == "ov_gam_term" and str(u_term.conversation) == "ov_gam_conv" and not u_term.useable and not u_term.static,
      f"ov_gam_term.utp invisible terminal valid (app={u_term.appearance_id}, conv={u_term.conversation})")

gam_dlg_gff = read_gff(OVR / "ov_gam_conv.dlg")
check(str(gam_dlg_gff.root.get_resref("EndConversation")) == "ov_gam_end" and str(gam_dlg_gff.root.get_resref("EndConverAbort")) == "ov_gam_end",
      "ov_gam_conv.dlg cleans up ov_gam_term on EndConversation & EndConverAbort")
gam_dlg = read_dlg(OVR / "ov_gam_conv.dlg")
e0_txt = next(iter(gam_dlg.starters[0].node.text._substrings.values()), "")
check(len(gam_dlg.starters) == 3
      and [str(st.active1) for st in gam_dlg.starters] == ["ov_gam_c_can", "ov_gam_c_wb", ""]
      and [str(lk.node.script1) for lk in gam_dlg.starters[0].node.links] == ["ov_gam_a_upgr", "ov_gam_a_swap", ""]
      and [str(lk.node.script1) for lk in gam_dlg.starters[1].node.links] == ["ov_gam_a_upgr", ""]
      and "DÉFINITIVEMENT PERDUES" in e0_txt,
      "ov_gam_conv.dlg has 3 starters (full menu / always-available workbench / fallback) with explicit warning")
check((OVR / "ov_gam_c_wb.ncs").exists() and (OVR / "ov_gam_c_wb.ncs").stat().st_size > 100,
      "ov_gam_c_wb.ncs compiled (portable workbench always available out of real combat)")
check(not any((OVR / f"{x}.ncs").exists() for x in ("ov_gam_c_s2", "ov_gam_a_s1", "ov_gam_a_s2", "ov_gam_a_rst", "ov_gam_a_p3", "ov_gam_a_swup", "ov_gam_a_go", "ov_gam_a_p1", "ov_gam_a_p2")),
      "Zero obsolete ov_gam_* ghost scripts")
from pykotor.resource.formats.ncs import read_ncs
for fn in ("ov_gam_a_upgr.ncs", "ov_gam_a_swap.ncs"):
    ncs_obj = read_ncs(OVR / fn)
    bad_ss = [ins for ins in ncs_obj.instructions if "STORE_STATE" in str(ins) and ins.args[0] != 0]
    check(not bad_ss, f"{fn} has 0 global bytes in STORE_STATE")
ref_ncs = read_ncs(OVR / "ov_gam_a_ref.ncs")
check(not any("STORE_STATE" in str(ins) for ins in ref_ncs.instructions),
      "ov_gam_a_ref.ncs has zero STORE_STATE/DelayCommand")
check("GetLocalBoolean(oPC, 21)" in core_txt,
      "ov_inc_core uses collision-free LocalBoolean 21 for one-time adapter refresh")

# Global zero-<Unrecognized Token> check across ALL added TLK strings & Override UTI/DLG/UTP
import re
base_tlk_len = len(read_tlk(ROOT / "mods" / "04-engine-tests" / "backup" / "dialog.tlk.bak"))
bad_tlk_tokens = [i for i in range(base_tlk_len, len(tlk)) if re.search(r"<[^>]*>", tlk.get(i).text)]
check(not bad_tlk_tokens, f"Zero <...> pseudo-tokens in all added TLK strings (bad={bad_tlk_tokens})")
bad_gff_tokens = []
for ext in ("*.uti", "*.dlg", "*.utp"):
    for pf in sorted(OVR.glob(ext)):
        raw = pf.read_bytes()
        if b"<" in raw and b">" in raw:
            gg = read_gff(raw)
            def _scan_tok(st):
                for _l, _t, v in st:
                    if hasattr(v, "_substrings"):
                        for txt in v._substrings.values():
                            if isinstance(txt, str) and re.search(r"<[^>]*>", txt):
                                bad_gff_tokens.append(f"{pf.name}:{txt[:40]}")
                    elif hasattr(v, "_structs"):
                        for sub in v._structs:
                            _scan_tok(sub)
            _scan_tok(gg.root)
check(not bad_gff_tokens, f"Zero <...> pseudo-tokens in all Override UTI/DLG/UTP (bad={bad_gff_tokens})")

bi_tbl = read_2da(OVR / "baseitems.2da")
mmap_1m = json.loads((MOD / "baseitem_1m_map.json").read_text(encoding="utf-8"))
ranged_1m_ok = all(
    bi_tbl.get_row(mmap_1m[lbl]).get_string("weaponwield") == "4"
    and bi_tbl.get_row(mmap_1m[lbl]).get_string("weaponsize") == "3"
    and bi_tbl.get_row(mmap_1m[lbl]).get_string("equipableslots") == "0x00030"
    for lbl in ("Blaster_Rifle", "Blaster_Carbine", "Repeating_Blaster", "Heavy_Repeating_Blaster", "Disrupter_Rifle", "Sonic_Rifle", "Ion_Rifle", "Bowcaster", "Adv_Mining_Laser_1M")
)
check(ranged_1m_ok, "All 9 ranged 2M/Haute-Cadence 1M mirrors (incl. Adv_Mining_Laser_1M) have weaponwield=4, weaponsize=3, slots=0x00030")
check("GetBaseItemType(oAd) != 54" in core_txt, "Ov_EnsureAutoGrants auto-migrates old bi=55 ov_gam_adapt in existing saves")

swap_map = json.loads((MOD / "gamorrean_swap_map.json").read_text(encoding="utf-8"))
gamswap_txt = (SRC / "ov_inc_gamswap.nss").read_text(encoding="latin1")
check(len(swap_map) == 69, f"gamorrean_swap_map covers all 69 playable 2M/Double weapons (found {len(swap_map)})")
check(all((OVR / f"{e['res_1m']}.uti").exists() and e["tag_2m"] in gamswap_txt and e["tag_1m"] in gamswap_txt for e in swap_map),
      "All 69 1M mirror UTIs exist and are mapped bidirectionally in ov_inc_gamswap.nss")
for per_rr in ("heavymininglaser", "advancedminingla", "guidonbeacon"):
    check((OVR / f"{per_rr}.uti").exists() and any(e["res_2m"] == per_rr for e in swap_map),
          f"Peragus module 2M/D weapon {per_rr} present in Override/ and gamorrean_swap_map")
gam2_fid = fids["MOD_GAMORREAN_2"]
all_have_req_prop = all(
    any(p.property_name == 57 and p.subtype == gam2_fid for p in read_uti(OVR / f"{e['res_1m']}.uti").properties)
    and bi_tbl.get_row(read_uti(OVR / f"{e['res_1m']}.uti").base_item).get_string("reqfeat0") == str(gam2_fid)
    for e in swap_map
)
check(all_have_req_prop, f"All 69 ov1m_*.uti double-gated with Use_Limitation_Feat(57, {gam2_fid}) AND baseitems reqfeat0={gam2_fid}")
hc_labels_v = {"Quarter_Staff", "Double_Bladed_Sword", "Vibro_Double_Blade", "Double_Bladed_Lightsaber", "Wookie_Warblade", "Repeating_Blaster", "Heavy_Repeating_Blaster"}
hc_entries = [e for e in swap_map if e["baseitem_label"] in hc_labels_v]
all_hc_have_note = all(
    "main principale" in (read_uti(OVR / f"{e['res_1m']}.uti").description.get(Language.FRENCH, Gender.MALE) or "")
    and "main gauche" in (read_uti(OVR / f"{e['res_1m']}.uti").description.get(Language.FRENCH, Gender.MALE) or "")
    for e in hc_entries
)
check(len(hc_entries) >= 20 and all_hc_have_note, f"All {len(hc_entries)} high-cadence 1M UTIs state main-hand-only bonus attack (no off-hand bonus)")
check("nTree == 1 && GetIsObjectValid(oRight) && Ov_IsDouble1MMirrorBaseItem(nBI)" in core_txt
      and "Ov_GetActiveCaracTree(oTarget) == 1 && GetHasFeat(OV_GAM_2, oTarget)" in core_txt,
      "Option B & Adaptateur Gamorréen gated by Ov_GetActiveCaracTree == 1 (strict 6-tree mutual exclusion)")
check(not list(OVR.glob("m_w_*_1m.uti")), "Zero obsolete m_w_*_1m.uti ghost files")

print(f"\n=== VERIFICATION SUMMARY: {len(passed)} PASSED, {len(errors)} FAILED ===")
if errors:
    print("FAILURES:")
    for e in errors:
        print("  [FAIL]", e)
else:
    print("ALL CHECKS PASSED 100%!")
