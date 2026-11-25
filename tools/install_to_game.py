import shutil
from pathlib import Path
from pykotor.resource.formats.twoda import read_2da
from pykotor.resource.generics.uti import read_uti

GAME_DIR = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Knights of the Old Republic II")
GAME_OVR = GAME_DIR / "Override"
MOD_DIR = Path(r"C:\Users\emman\Desktop\dev\Kotor 2 Mods\mods\overhaul")
MOD_OVR = MOD_DIR / "Override"

# 1. Nettoyer les anciens fichiers fantômes de la v0 (m_w_*_1m.uti et anciens scripts ov_gam_*)
removed_old = 0
for old_f in list(GAME_OVR.glob("m_w_*_1m.uti")) + [GAME_OVR / f"{x}.ncs" for x in ("ov_gam_c_s2", "ov_gam_a_s1", "ov_gam_a_s2", "ov_gam_a_rst", "ov_gam_a_p3", "ov_gam_a_swup", "ov_gam_a_go", "ov_gam_a_p1", "ov_gam_a_p2")]:
    if old_f.exists():
        old_f.unlink()
        removed_old += 1

# 2. Copier dialog.tlk
shutil.copy2(MOD_DIR / "dialog.tlk", GAME_DIR / "dialog.tlk")

# 3. Copier tous les fichiers Override (.2da, .uti, .utc, .ncs, .dlg)
copied = 0
for src in sorted(MOD_OVR.iterdir()):
    if src.is_file():
        shutil.copy2(src, GAME_OVR / src.name)
        copied += 1

print(f"[OK] Nettoyé {removed_old} anciens fichiers m_w_*_1m.uti")
print(f"[OK] dialog.tlk installé ({(GAME_DIR / 'dialog.tlk').stat().st_size} octets)")
print(f"[OK] {copied} fichiers copiés dans {GAME_OVR}")

# 4. Vérification post-copie dans le dossier du jeu
for fname in ["ov_gam_adapt.uti", "ov_gam_term.utp", "ov_gam_conv.dlg", "ov_gam_use.ncs", "ov_gam_end.ncs", "ov_gam_c_can.ncs", "ov_gam_c_wb.ncs", "ov_gam_a_upgr.ncs", "ov_gam_a_swap.ncs", "ov_gam_a_ref.ncs", "heavymininglaser.uti", "advancedminingla.uti", "guidonbeacon.uti", "ov1m_069.uti", "k_hen_heartbt01.ncs", "k_def_heartbt01.ncs", "kreia.dlg", "baseitems.2da", "iprp_resistcost.2da", "forceshields.2da", "itemcreatemira.2da"]:
    pg = GAME_OVR / fname
    pm = MOD_OVR / fname
    assert pg.exists() and pg.stat().st_size == pm.stat().st_size, f"Mismatch on {fname}"

u_ad = read_uti(GAME_OVR / "ov_gam_adapt.uti")
assert u_ad.base_item == 54 and u_ad.charges == 1 and not u_ad.plot and any(p.property_name == 10 and p.cost_value == 13 for p in u_ad.properties), f"ov_gam_adapt.uti invalid in GAME_OVR: bi={u_ad.base_item}, chg={u_ad.charges}, plot={u_ad.plot}"
ft = read_2da(GAME_OVR / "feat.2da")
sp = read_2da(GAME_OVR / "spells.2da")
rc = read_2da(GAME_OVR / "iprp_resistcost.2da")
fs = read_2da(GAME_OVR / "forceshields.2da")
print(f"[VERIF OK] GAME/Override: ov_gam_adapt bi={u_ad.base_item} plot={u_ad.plot} | feat={len(ft)}, spells={len(sp)}, iprp_resistcost={len(rc)}, forceshields={len(fs)}")
