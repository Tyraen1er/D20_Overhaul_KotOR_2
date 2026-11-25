# -*- coding: utf-8 -*-
"""Revue d'équilibrage systématique du contrat §9 (decisions_finales.md).

Pilote `dpr_check.py` en module : matrice de builds réalistes (styles × familles ×
phases × contextes mêlée/distance/bure) évaluée contre les plages DPR du contrat
mathématique, en ne gardant pour chaque posture que la meilleure configuration du
mode correspondant :

  Duel (1M) -> mode `single` · Ambidextrie -> `dual` · Arme Lourde (2M) -> `twohand` ·
  Haute Cadence (double) -> `double`

Conditions identiques aux simulations de référence : équipement réaliste `--gear`
(6 CSV + Cristal personnel), améliorations `mod` (vraies pièces d'Améliorations.csv),
plafonds moteur réels, boss étalons de `dpr_data.json` (mid = 400 PV Jalon 4).

Usage :
  python tools/dpr_review.py                # matrice complète + verdicts vs contrat §9
  python tools/dpr_review.py --phase mid    # une seule phase
  python tools/dpr_review.py --md           # synthèse markdown (rapport)
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dpr_check as dc  # noqa: E402


def load_data() -> dc.Data:
    import json
    return dc.Data(json.loads(dc.DATA_FILE.read_text(encoding="utf-8")))

# ---------------------------------------------------------------------------
# Contrat §9 — plages DPR cibles par posture × phase (decisions_finales.md §9,
# vérifiées sous dpr_check.py le 19/11 ; boss mid rehaussé à 400 PV en Jalon 4).
# ---------------------------------------------------------------------------
CONTRACT: dict[str, dict[str, tuple[int, int]]] = {
    "early": {"single": (11, 23), "dual": (9, 18), "twohand": (14, 26), "double": (17, 30)},
    "mid":   {"single": (26, 67), "dual": (23, 65), "twohand": (36, 66), "double": (36, 81)},
    "late":  {"single": (55, 140), "dual": (49, 150), "twohand": (86, 186), "double": (61, 170)},
}
MODE_LABEL = {"single": "Duel (1M)", "dual": "Ambidextrie", "twohand": "Arme Lourde (2M)", "double": "Haute Cadence"}

# ---------------------------------------------------------------------------
# Matrice de builds réalistes (budgets de dons cohérents avec le niveau de phase :
# early ~4 dons, mid ~8, late ~13 + spé caractéristique).
# (phase, mode, contexte, preset, armure, buffs, dons, optionnel)
# ---------------------------------------------------------------------------
BUILDS: list[tuple[str, str, str, str, str, str, str, dict]] = [
    # --- EARLY (Niv. 8) ------------------------------------------------------
    ("early", "single",   "Gardien mêlée",         "gardien",    "lourde", "", "Duel 2,Spécialisation Arme Laser 1,Coup critique 1", {}),
    ("early", "dual",     "Gardien mêlée",         "gardien",    "lourde", "", "Ambidextrie 2,Spécialisation Arme Laser 1,Déluge de coups 1", {}),
    ("early", "twohand",  "Gardien mêlée",         "gardien",    "lourde", "", "Maniement d'Arme Lourde 2,Spécialisation Arme à Résonance 1,Attaque en puissance 1", {}),
    ("early", "twohand",  "Gardien mêlée (trad.)", "gardien",    "lourde", "", "Maniement d'Arme Lourde 2,Spécialisation Arme Traditionnelle 1,Attaque en puissance 1", {}),
    ("early", "double",   "Gardien mêlée",         "gardien",    "lourde", "", "Maniement d'Arme haute cadence 2,Spécialisation Arme Laser 1,Déluge de coups 1", {}),
    ("early", "single",   "Sentinelle distance",   "sentinelle", "lourde", "", "Duel 2,Spécialisation de Tir Pénétrant 1,Coup critique 1", {}),
    ("early", "dual",     "Sentinelle distance",   "sentinelle", "lourde", "", "Ambidextrie 2,Spécialisation de Tir d'Assaut 1,Déluge de coups 1", {}),
    ("early", "twohand",  "Sentinelle distance",   "sentinelle", "lourde", "", "Maniement d'Arme Lourde 2,Spécialisation de Tir Pénétrant 1,Attaque en puissance 1", {}),
    ("early", "double",   "Sentinelle distance",   "sentinelle", "lourde", "", "Maniement d'Arme haute cadence 2,Spécialisation de Tir Pénétrant 1,Déluge de coups 1", {}),
    ("early", "double",   "Sentinelle distance (assaut)", "sentinelle", "lourde", "", "Maniement d'Arme haute cadence 2,Spécialisation de Tir d'Assaut 1,Déluge de coups 1", {}),
    # --- MID (Niv. 16) -------------------------------------------------------
    ("mid", "single",   "Gardien mêlée",           "gardien",    "lourde", "", "Duel 3,Spécialisation Arme Laser 2,Coup critique 2,Robustesse 1", {}),
    ("mid", "dual",     "Gardien mêlée",           "gardien",    "lourde", "", "Ambidextrie 3,Spécialisation Arme Laser 2,Déluge de coups 2", {}),
    ("mid", "twohand",  "Gardien mêlée",           "gardien",    "lourde", "", "Maniement d'Arme Lourde 3,Spécialisation Arme à Résonance 2,Attaque en puissance 2", {}),
    ("mid", "twohand",  "Gardien mêlée (trad.)",   "gardien",    "lourde", "", "Maniement d'Arme Lourde 3,Spécialisation Arme Traditionnelle 2,Attaque en puissance 2", {}),
    ("mid", "double",   "Gardien mêlée",           "gardien",    "lourde", "", "Maniement d'Arme haute cadence 3,Spécialisation Arme Laser 2,Déluge de coups 2", {}),
    ("mid", "single",   "Sentinelle distance",     "sentinelle", "lourde", "", "Duel 3,Spécialisation de Tir Pénétrant 2,Coup critique 2,Robustesse 1", {}),
    ("mid", "dual",     "Sentinelle distance",     "sentinelle", "lourde", "", "Ambidextrie 3,Spécialisation de Tir d'Assaut 2,Déluge de coups 2", {}),
    ("mid", "twohand",  "Sentinelle distance",     "sentinelle", "lourde", "", "Maniement d'Arme Lourde 3,Spécialisation de Tir Pénétrant 2,Attaque en puissance 2", {}),
    ("mid", "double",   "Sentinelle distance",     "sentinelle", "lourde", "", "Maniement d'Arme haute cadence 3,Spécialisation de Tir Pénétrant 2,Déluge de coups 2", {}),
    ("mid", "double",   "Sentinelle distance (assaut)", "sentinelle", "lourde", "", "Maniement d'Arme haute cadence 3,Spécialisation de Tir d'Assaut 2,Déluge de coups 2", {}),
    # --- LATE (Niv. 26) ------------------------------------------------------
    ("late", "single",  "Gardien mêlée",           "gardien",    "lourde", "", "Duel 3,Spécialisation Arme Laser 3,Coup critique 3,Robustesse 3,Techniques Echanis 2", {}),
    ("late", "dual",    "Gardien mêlée",           "gardien",    "lourde", "", "Ambidextrie 3,Spécialisation Arme Laser 3,Déluge de coups 3,Robustesse 3,Techniques Echanis 2", {}),
    ("late", "twohand", "Gardien mêlée",           "gardien",    "lourde", "", "Maniement d'Arme Lourde 3,Spécialisation Arme à Résonance 3,Attaque en puissance 3,Robustesse 3,Voie du dragon Kraith 2", {}),
    ("late", "twohand", "Gardien mêlée (trad.)",   "gardien",    "lourde", "", "Maniement d'Arme Lourde 3,Spécialisation Arme Traditionnelle 3,Attaque en puissance 3,Robustesse 3,Raffinement Gamoréen 2", {}),
    ("late", "double",  "Gardien mêlée",           "gardien",    "lourde", "", "Maniement d'Arme haute cadence 3,Spécialisation Arme Laser 3,Déluge de coups 3,Robustesse 3,Techniques Echanis 2", {}),
    ("late", "single",  "Sentinelle distance",     "sentinelle", "lourde", "", "Duel 3,Spécialisation de Tir Pénétrant 3,Coup critique 3,Robustesse 3,Chasseur de prime Gand 2", {}),
    ("late", "dual",    "Sentinelle distance",     "sentinelle", "lourde", "", "Ambidextrie 3,Spécialisation de Tir d'Assaut 3,Déluge de coups 3,Robustesse 3,Chasseur de prime Gand 2", {}),
    ("late", "twohand", "Sentinelle distance",     "sentinelle", "lourde", "", "Maniement d'Arme Lourde 3,Spécialisation de Tir Pénétrant 3,Attaque en puissance 3,Robustesse 3,Chasseur de prime Gand 2", {}),
    ("late", "double",  "Sentinelle distance",     "sentinelle", "lourde", "", "Maniement d'Arme haute cadence 3,Spécialisation de Tir Pénétrant 3,Déluge de coups 3,Robustesse 3,Chasseur de prime Gand 2", {}),
    ("late", "single",  "Consulaire bure (buffs)", "consulaire", "sans",   "Vitesse 3,Talent de Force 3,Armure de Force 3", "Duel 3,Spécialisation Arme Laser 3,Coup critique 3,Robustesse 3,Héritage de Nomi 2", {}),
    ("late", "dual",    "Consulaire bure (buffs)", "consulaire", "sans",   "Vitesse 3,Talent de Force 3,Armure de Force 3", "Ambidextrie 3,Spécialisation Arme Laser 3,Déluge de coups 3,Robustesse 3,Héritage de Nomi 2", {}),
    ("late", "twohand", "Consulaire bure (buffs)", "consulaire", "sans",   "Vitesse 3,Talent de Force 3,Armure de Force 3", "Maniement d'Arme Lourde 3,Spécialisation Arme à Résonance 3,Attaque en puissance 3,Robustesse 3,Héritage de Nomi 2", {}),
    ("late", "double",  "Consulaire bure (buffs)", "consulaire", "sans",   "Vitesse 3,Talent de Force 3,Armure de Force 3", "Maniement d'Arme haute cadence 3,Spécialisation Arme Laser 3,Déluge de coups 3,Robustesse 3,Héritage de Nomi 2", {}),
    # --- Extra : plafond Maraudeur (Stigmate de Force en armure lourde) ------
    ("late", "twohand", "Gardien + Stigmate 3",    "gardien",    "lourde", "Stigmate de Force 3", "Maniement d'Arme Lourde 3,Spécialisation Arme à Résonance 3,Attaque en puissance 3,Robustesse 3", {"extra": True}),
    ("late", "double",  "Gardien + Stigmate 3",    "gardien",    "lourde", "Stigmate de Force 3", "Maniement d'Arme haute cadence 3,Spécialisation Arme Laser 3,Déluge de coups 3,Robustesse 3", {"extra": True}),
]

MELEE_CONTEXTS = ("Gardien mêlée", "Gardien mêlée (trad.)", "Gardien + Stigmate 3")
RANGED_CONTEXTS = ("Sentinelle distance", "Sentinelle distance (assaut)")


def setup_char(data: dc.Data, feats: dc.Feats, pk: str, preset: str, armor_tier: str,
               buff_spec: str, gear: bool = True) -> dc.Char:
    """Reproduit la préparation de personnage de run_report (gear + buffs + phase)."""
    phase = data.phases[pk]
    overrides: dict[str, int] = {}
    char = dc.build_char(data, pk, preset, overrides, "auto", armor_tier=armor_tier)
    if gear:
        carac_prio = {
            "gamorrean": ("FOR", "CON"), "echani": ("DEX", "CON"), "kraith": ("CON", "FOR"),
            "gand": ("INT", "DEX"), "matukai": ("SAG", "DEX"), "nomi": ("CHA", "SAG"),
        }
        preset_prio = {"gardien": ("FOR", "CON"), "sentinelle": ("DEX", "CON"), "consulaire": ("SAG", "CHA")}
        p_stat, s_stat = preset_prio.get(preset, ("FOR", "CON"))
        for ck, pair in carac_prio.items():
            if feats.rank("caracs", ck) > 0:
                p_stat, s_stat = pair
                break
        cand_cfgs = dc.enumerate_configs(data, feats, None)
        any_saber = any(data.weapon_by_key[c.main].family == "laser" for c in cand_cfgs)
        any_melee = any(not data.weapon_by_key[c.main].ranged for c in cand_cfgs)
        g = dc.equip_best_gear(data, pk, preset, armor_tier, p_stat, s_stat,
                               is_melee=any_melee, is_saber=any_saber)
        char.stats = dict(g["mods"])
        char.use_gear = True
        char.gear_ac = g["gear_ac"]
        char.gear_saves = g["gear_saves"]
        char.gear_save_vig = g.get("gear_save_vig", 0)
        char.gear_save_ref = g.get("gear_save_ref", 0)
        char.gear_save_vol = g.get("gear_save_vol", 0)
        char.gear_attack = g["gear_attack"]
        char.gear_melee_dmg = g["gear_melee_dmg"]
        char.gear_rd = g["gear_rd"]
        char.gear_equipped = g["equipped"]
    buff_ranks, _unknown = dc.parse_buffs(data, buff_spec)
    buffs = dc.resolve_buffs(data, buff_ranks, armor_tier, phase, "auto")
    for k in char.stats:
        char.stats[k] += buffs["mod_all"]
    char.stats["FOR"] += buffs["for_add"]
    char.stats["DEX"] += buffs.get("dex_add", 0)
    char.speed_attacks = buffs["attacks"]
    char.speed_ac = buffs["speed_ac"]
    char.armor_force_ac = buffs["armor_ac"]
    char.buff_ac = max(buffs["speed_ac"], buffs["armor_ac"])
    char.buff_rd = buffs["barrier_rd"]
    return char


def make_enemy(data: dc.Data, pk: str) -> dc.Enemy:
    raw = data.enemies[pk]
    return dc.Enemy("", raw["hp"], raw["defense"], raw["rd"],
                    dc.enemy_fort_save(data, data.phases[pk]["level"]),
                    attack=raw.get("attack", 0), dmg_hit=raw.get("dmg_hit", 0.0),
                    attacks=raw.get("attacks", 1),
                    will_save=raw.get("will_save", 0), ref_save=raw.get("ref_save", 0))


def run_matrix(phases: list[str], data: dc.Data | None = None) -> list[dict]:
    data = data or dc.Data()
    rows: list[dict] = []
    for phase, mode, ctx, preset, armor, buffs, feat_spec, opt in BUILDS:
        if phase not in phases:
            continue
        feats = dc.parse_feats(data, feat_spec)
        char = setup_char(data, feats, phase, preset, dc.parse_armor(armor), buffs)
        eff_stats = dc.effective_stats(data, feats, char.stats)
        char.stats = eff_stats
        enemy = make_enemy(data, phase)
        squad = data.raw.get("squad_enemies", {}).get(phase, {})
        ranged = ctx in RANGED_CONTEXTS
        results = []
        for cfg in dc.enumerate_configs(data, feats, None):
            w = data.weapon_by_key[cfg.main]
            if cfg.mode != mode or w.ranged != ranged:
                continue
            r = dc.evaluate(cfg, data, feats, char, phase, enemy, "mod", 0, 0.0, squad=squad)
            r["_mode"] = cfg.mode
            results.append(r)
        if not results:
            rows.append({"phase": phase, "mode": mode, "ctx": ctx, "missing": True})
            continue
        best = max(results, key=lambda r: r["dpr"])
        lo, hi = CONTRACT[phase][mode]
        best["_in_contract"] = lo <= best["dpr"] <= hi
        best["_contract"] = (lo, hi)
        best["_extra"] = bool(opt.get("extra"))
        rows.append({"phase": phase, "mode": mode, "ctx": ctx, "missing": False, "best": best})
    return rows


def main() -> None:
    ap = argparse.ArgumentParser(description="Revue d'équilibrage vs contrat §9")
    ap.add_argument("--phase", default="all", help="early,mid,late ou all (défaut)")
    ap.add_argument("--md", action="store_true", help="synthèse markdown finale")
    args = ap.parse_args()

    phases = list(load_data().phases.keys()) if args.phase == "all" else [p.strip() for p in args.phase.split(",")]
    data = load_data()
    rows = run_matrix(phases, data)

    flags = 0
    for ph in phases:
        print()
        print("=" * 118)
        label = data.phases[ph]["label"]
        en = data.enemies[ph]
        print(f" {label} (Niv. {data.phases[ph]['level']} — boss {en['hp']} PV / CA {en['defense']} / RD {en['rd']})")
        print("=" * 118)
        print(f" {'Posture':<18} | {'Contexte':<28} | {'Meilleure config':<38} | {'Atq':>4} | {'DPR':>6} | {'TTK':>5} | {'CA':>3} | {'TTD':>5} | Contrat §9")
        print("-" * 118)
        for row in rows:
            if row["phase"] != ph:
                continue
            mode = row["mode"]
            if row["missing"]:
                print(f" {MODE_LABEL[mode]:<18} | {row['ctx']:<28} | — AUCUNE CONFIG CANDIDATE —")
                flags += 1
                continue
            b = row["best"]
            lo, hi = b["_contract"]
            mark = "OK " if b["_in_contract"] else ("BASSE" if b["dpr"] < lo else "HAUTE")
            extra = "  [extra]" if b["_extra"] else ""
            print(f" {MODE_LABEL[mode]:<18} | {row['ctx']:<28} | {b['label'][:38]:<38} | {b['attack_main']:>+4d} "
                  f"| {b['dpr']:>6.1f} | {b['ttk']:>5.1f} | {b['player_ac']:>3} | {b['boss_ttd']:>5.1f} "
                  f"| {lo}-{hi} {mark}{extra}")
            if not b["_in_contract"]:
                flags += 1

    # Enveloppe min-max par posture/phase vs contrat
    print()
    print("=" * 118)
    print(" ENVELOPPE (min-max des builds échantillonnés) vs CONTRAT §9")
    print("=" * 118)
    for ph in phases:
        for mode in ("single", "dual", "twohand", "double"):
            vals = [r["best"]["dpr"] for r in rows
                    if r["phase"] == ph and r["mode"] == mode and not r.get("missing")]
            if not vals:
                continue
            lo, hi = CONTRACT[ph][mode]
            vmin, vmax = min(vals), max(vals)
            status = "OK" if (lo <= vmin and vmax <= hi) else "ÉCART"
            print(f" {data.phases[ph]['label']:<6} {MODE_LABEL[mode]:<18} : échantillon {vmin:6.1f} – {vmax:6.1f} | contrat {lo:3d} – {hi:3d} | {status}")

    n_ok = sum(1 for r in rows if not r.get("missing") and r["best"]["_in_contract"])
    n_total = sum(1 for r in rows if not r.get("missing"))
    print()
    print(f" BUILDS DANS LE CONTRAT : {n_ok}/{n_total}" + (f" — {flags} écart(s) à examiner" if flags else " — AUCUN ÉCART"))

    if args.md:
        print()
        print("## Synthèse (markdown)")
        for ph in phases:
            for r in rows:
                if r["phase"] != ph or r.get("missing"):
                    continue
                b = r["best"]
                lo, hi = b["_contract"]
                mark = "OK" if b["_in_contract"] else ("BASSE" if b["dpr"] < lo else "HAUTE")
                print(f"- **{data.phases[ph]['label']} {MODE_LABEL[r['mode']]}** — {r['ctx']} : "
                      f"{b['label']} → **DPR {b['dpr']}** ({mark}, contrat {lo}–{hi})")


if __name__ == "__main__":
    main()
