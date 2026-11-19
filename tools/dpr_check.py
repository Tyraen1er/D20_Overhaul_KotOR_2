#!/usr/bin/env python3
"""KotOR 2 Overhaul — DPR Checker (outils d'équilibrage).

Simule le DPR (Damage Per Round) d'un build défini par une SÉRIE DE DONS CHOISIS,
contre les boss étalons du contrat mathématique (§9 de decisions_finales.md),
en sélectionnant automatiquement la MEILLEURE CONFIGURATION possible :

  • meilleure arme (et elle CHANGE selon les dons : une Spé Arme Laser favorise
    les sabres, le Maniement d'Arme Lourde favorise les 2M, les dons de crit
    favorisent les larges plages de menace, etc.) ;
  • meilleur mode de port (1M / 2M / deux armes / arme double) ;
  • meilleure arme de main gauche (si Ambidextrie) ;
  • meilleure attaque active (Déluge / Puissance / Critique ou aucun) ;
  • meilleures améliorations d'établi (mode plafonné §3.A `+2/+5/+10` pondéré par les
    emplacements autorisés par famille d'arme, ou mode vanilla depuis WIP Améliorations.csv, ou aucune) ;
  • pouvoirs de la Force ACTIFS selon l'armure portée (`--armor`) : Vitesse, Armure de Force,
    Barrière et Talent de Force sont filtrés par armure max (logique forbiditemmask du WIP Spé Pouvoirs.csv) ;
  • défense et survie du build (CA, RD, Immunité %, Esquive %, PV + Bouclier, DTPS subi et
    TTD en rounds contre le boss `Set_5` et l'escouade d'élites `3× Set_3`).

Toutes les VALEURS (armes, dons, améliorations, boss) vivent dans
`tools/dpr_data.json` : c'est LE fichier à éditer pour équilibrer — le moteur
ne doit pas être touché pour changer l'équilibrage. Les pools d'améliorations
peuvent être régénérés depuis le CSV utilisateur :

    python tools/dpr_check.py --reingest-upgrades

Exemples :

    .venv\\Scripts\\python.exe tools\\dpr_check.py --feats "Duel 3,Spécialisation Arme Laser 3,Coup critique 3"
    .venv\\Scripts\\python.exe tools\\dpr_check.py --feats "Ambidextrie 3,Tir d'Assaut 3,Tir rapide 3" --char sentinelle
    .venv\\Scripts\\python.exe tools\\dpr_check.py --feats "Maniement d'Arme Lourde 3,Tir Pénétrant 3,Décharge 3" --upgrades vanilla
    .venv\\Scripts\\python.exe tools\\dpr_check.py --feats "..." --level 12 --enemy 200,26,5 --speed none
    :: même build en armure — les pouvoirs se gatent tout seuls :
    .venv\\Scripts\\python.exe tools\\dpr_check.py --feats "Duel 3,Spécialisation Arme Laser 3,Coup critique 3" ^
        --armor lourde --buffs "Vitesse 3,Talent de Force 3"

Conventions moteur (héritées de tools/k2balance.py) :
  • toucher = (21 - (CA - Atq)) / 20, borné [5 %, 95 %] (1 auto-raté, 20 auto-touché) ;
  • critique = menace sur la plage puis confirmation (≈ proba de toucher) ;
  • la RD du boss est soustraite APRÈS multiplication critique, par coup ;
  • la Vitesse (Force) ajoute +1/+2 attaques main directrice (mid/late par défaut).
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DATA_FILE = HERE / "dpr_data.json"
DEFAULT_UPGRADES_CSV = ROOT / "Kotor 2 - rééquilibrage - WIP Améliorations.csv"

ROMAN = {"i": 1, "ii": 2, "iii": 3, "iv": 4, "v": 5}
TIER_ORDER = {"sans": 0, "legere": 1, "moyenne": 2, "lourde": 3}
ARMOR_ALIASES = {
    "sans": "sans", "robe": "sans", "aucune": "sans", "none": "sans", "nu": "sans",
    "legere": "legere", "leger": "legere", "legere armure": "legere", "light": "legere",
    "moyenne": "moyenne", "intermediaire": "moyenne", "medium": "moyenne", "inte": "moyenne",
    "lourde": "lourde", "lourd": "lourde", "heavy": "lourde",
}


# ============================================================================
# Utilitaires
# ============================================================================

def norm(s: str) -> str:
    """minuscule + sans accents + apostrophes → espaces + espaces simples (résolution de noms)."""
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.replace("'", " ").replace("\u2019", " ")
    return re.sub(r"\s+", " ", s.lower()).strip()


def avg_dice(expr: str) -> float:
    """'2d6' -> 7.0 ; '5' -> 5.0 ; '' -> 0.0"""
    expr = expr.strip().replace(" ", "")
    m = re.fullmatch(r"(\d+)d(\d+)", expr)
    if m:
        return int(m.group(1)) * (int(m.group(2)) + 1) / 2.0
    m = re.fullmatch(r"\d+", expr)
    if m:
        return float(m.group(0))
    return 0.0


def clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def hit_probability(attack_bonus: float, target_defense: float) -> float:
    needed = target_defense - attack_bonus
    return clamp((21.0 - needed) / 20.0, 0.05, 0.95)


def save_fail_probability(dc: float, save_bonus: float) -> float:
    return clamp((dc - save_bonus - 1) / 20.0, 0.05, 0.95)


# ============================================================================
# Données
# ============================================================================

@dataclass(frozen=True)
class Weapon:
    key: str
    name: str
    family: str
    wield: str          # "1M" | "2M" | "D"
    ranged: bool
    dmg_avg: float
    crit_range: int     # largeur de plage (1 = 20-20)
    crit_mult: int
    balanced: bool = False
    upgrade_pool: str | None = None
    slots: int = 0
    allowed_slots: list[str] = field(default_factory=list)
    massive_avg: float = 0.0


@dataclass
class Upgrades:
    damage: float = 0.0        # dégâts moyens/coup (dés + bonus)
    onhit: float = 0.0         # dégâts « en cas de coup au but »
    attack: int = 0
    keen: bool = False
    massive: float = 0.0       # dés de critiques massifs
    detail: str = ""

    @property
    def per_hit(self) -> float:
        return self.damage + self.onhit


class Data:
    def __init__(self, raw: dict):
        self.raw = raw
        self.phases: dict[str, dict] = raw["phases"]
        self.enemies: dict[str, dict] = raw["enemies"]
        self.presets: dict[str, dict] = raw["char_presets"]
        self.weapons: list[Weapon] = [Weapon(**w) for w in raw["weapons"]]
        self.weapon_by_key = {w.key: w for w in self.weapons}
        self.feats: dict = raw["feats"]
        self.model: dict = raw

    # -------- index des alias de dons (résolu paresseusement) ---------------
    def alias_index(self) -> dict[str, tuple[str, str, int]]:
        """Retourne {alias_norm -> (catégorie, clé, max_rank)} pour toutes les entrées."""
        idx: dict[str, tuple[str, str, int]] = {}
        for cat in ("styles", "familles", "caracs", "armures", "actives"):
            for key, feat in self.feats.get(cat, {}).items():
                idx[norm(feat["label"])] = (cat, key, feat.get("max", 3))
                idx.setdefault(norm(feat["label"].split("(")[0]), (cat, key, feat.get("max", 3)))
                for alias in feat.get("aliases", []):
                    idx[norm(alias)] = (cat, key, feat.get("max", 3))
        return idx


# ============================================================================
# Dons choisis
# ============================================================================

@dataclass
class Feats:
    styles: dict[str, int] = field(default_factory=dict)
    familles: dict[str, int] = field(default_factory=dict)
    caracs: dict[str, int] = field(default_factory=dict)
    armures: dict[str, int] = field(default_factory=dict)
    actives: dict[str, int] = field(default_factory=dict)
    unknown: list[str] = field(default_factory=list)

    def rank(self, cat: str, key: str) -> int:
        return getattr(self, cat).get(key, 0)


def parse_feats(data: Data, spec: str) -> Feats:
    feats = Feats()
    if not spec:
        return feats
    idx = data.alias_index()
    for token in re.split(r"[;,/]", spec):
        token = token.strip()
        if not token:
            continue
        rank = 0
        m = re.search(r"\s+(\d+|I{1,3}|IV|V)$", token, re.IGNORECASE)
        if m:
            suffix = m.group(1).lower()
            rank = ROMAN.get(suffix, 0) or int(suffix)
            token = token[: m.start()].strip()
        # support des labels 2DA : MOD_SPEC_LASER_2
        m2 = re.fullmatch(r"(mod_[a-z_]+)_(\d)", token, re.IGNORECASE)
        if m2 and norm(token) not in idx:
            token, rank = m2.group(1), int(m2.group(2))
        hit = idx.get(norm(token))
        if hit is None:
            # tentative sans le rang collé (« Ambidextrie3 »)
            m3 = re.fullmatch(r"(.+?)(\d)", token)
            if m3:
                hit = idx.get(norm(m3.group(1)))
                if hit:
                    rank = rank or int(m3.group(2))
        if hit is None:
            feats.unknown.append(token)
            continue
        cat, key, max_rank = hit
        rank = max(1, min(rank or 1, max_rank))
        getattr(feats, cat)[key] = rank
    return feats


# ============================================================================
# Armure portée & buffs de la Force
# ============================================================================

def parse_armor(spec: str) -> str:
    key = ARMOR_ALIASES.get(norm(spec))
    if key is None:
        raise SystemExit(f"Armure inconnue « {spec} » — valeurs : sans/légère/moyenne/lourde")
    return key


def parse_buffs(data: Data, spec: str) -> tuple[dict[str, int], list[str]]:
    """Parse \"Vitesse 3,Talent de Force 2\" -> ({"vitesse":3,"valor":2}, [inconnus])."""
    if not spec:
        return {}, []
    idx: dict[str, str] = {}
    for key, buff in data.raw.get("force_buffs", {}).items():
        idx[norm(buff["label"])] = key
        idx.setdefault(norm(buff["label"].split("(")[0]), key)
        for alias in buff.get("aliases", []):
            idx[norm(alias)] = key
    ranks: dict[str, int] = {}
    unknown: list[str] = []
    for token in re.split(r"[;,/]", spec):
        token = token.strip()
        if not token:
            continue
        rank = 0
        m = re.search(r"\s+(\d+|I{1,3}|IV|V)$", token, re.IGNORECASE)
        if m:
            suffix = m.group(1).lower()
            rank = ROMAN.get(suffix, 0) or int(suffix)
            token = token[: m.start()].strip()
        key = idx.get(norm(token))
        if key is None:
            m3 = re.fullmatch(r"(.+?)(\d)", token)
            if m3:
                key = idx.get(norm(m3.group(1)))
                if key:
                    rank = rank or int(m3.group(2))
        if key is None:
            unknown.append(token)
            continue
        ranks[key] = max(1, min(rank or 1, 3))
    return ranks, unknown


def buff_allowed(data: Data, buff_key: str, armor_tier: str) -> bool:
    return TIER_ORDER[armor_tier] <= TIER_ORDER[data.raw["force_buffs"][buff_key]["armor_max"]]


def resolve_buffs(data: Data, buff_ranks: dict[str, int], armor_tier: str,
                  phase: dict, speed_mode: str) -> dict:
    """Détermine les effets de buffs FINALEMENT actifs selon l'armure portée.

    Retourne {attacks, mod_all, for_add, speed_ac, armor_ac, barrier_rd, active[], blocked[], notes[]}.
    Vitesse/Fureur non cumulables → on garde le meilleur nombre d'attaques
    (la Fureur l'emporte en cas d'égalité pour son bonus de FOR).
    --speed ≠ auto = override manuel qui bypass le gating (tests rapides).
    """
    fb = data.raw["force_buffs"]
    active: list[str] = []
    blocked: list[str] = []
    notes: list[str] = []

    lvl = phase.get("level", 30)
    if lvl < 9:
        max_r, max_af, allow_illum = 1, 2, False
    elif lvl < 19:
        max_r, max_af, allow_illum = 2, 3, True
    else:
        max_r, max_af, allow_illum = 3, 3, True

    # Illumination : accorde Vitesse + Talent (et Armure si défini) plafonnés au palier de la phase
    granted: dict[str, int] = {}
    if "illumination" in buff_ranks:
        if not allow_illum:
            notes.append("Illumination (Niv. 15+ requis)")
        elif buff_allowed(data, "illumination", armor_tier):
            granted = {
                k: min(v, max_af if k == "armure_force" else max_r)
                for k, v in fb["illumination"]["grants"].items()
            }
            parts = [f"Vitesse {granted.get('vitesse', 0)}", f"Talent {granted.get('valor', 0)}"]
            if granted.get("armure_force"):
                parts.append(f"Armure {granted['armure_force']}")
            active.append(f"Illumination (lance {' + '.join(parts)} au rang max)")
        else:
            blocked.append("Illumination")

    # Vitesse / Talent / Armure de Force : actifs s'ils ont au moins une source autorisée
    vit_att = 0
    vit_ac = 0
    vit_rank = 0
    src = []
    if buff_ranks.get("vitesse"):
        if buff_allowed(data, "vitesse", armor_tier):
            vit_rank = min(buff_ranks["vitesse"], max_r)
            src.append(f"Vitesse {vit_rank}")
        else:
            blocked.append(f"Vitesse (armure max : {fb['vitesse']['armor_max']})")
    if granted.get("vitesse"):
        vit_rank = max(vit_rank, granted["vitesse"])
        src.append(f"Vitesse {granted['vitesse']} via Illumination")
    if vit_rank:
        vit_att = fb["vitesse"]["attacks_by_rank"][str(vit_rank)]
        vit_ac = fb["vitesse"].get("ac_by_rank", {}).get(str(vit_rank), 0)
        active.append(f"{' + '.join(src)} (+{vit_att} att/rd, +{vit_ac} CA)")

    mod_all = 0
    val_rank = 0
    src = []
    if buff_ranks.get("valor"):
        if buff_allowed(data, "valor", armor_tier):
            val_rank = min(buff_ranks["valor"], max_r)
            src.append(f"Talent de Force {val_rank}")
        else:
            blocked.append(f"Talent de Force (armure max : {fb['valor']['armor_max']})")
    if granted.get("valor"):
        val_rank = max(val_rank, granted["valor"])
        src.append(f"Talent {granted['valor']} via Illumination")
    if val_rank:
        mod_all = fb["valor"]["mod_by_rank"][str(val_rank)]
        active.append(f"{' + '.join(src)} (+{mod_all} à tous les mod.)")

    armor_ac = 0
    af_rank = 0
    src = []
    if buff_ranks.get("armure_force"):
        if buff_allowed(data, "armure_force", armor_tier):
            af_rank = min(buff_ranks["armure_force"], max_af)
            src.append(f"Armure de Force {af_rank}")
        else:
            blocked.append(f"Armure de Force (armure max : {fb['armure_force']['armor_max']})")
    if granted.get("armure_force"):
        af_rank = max(af_rank, granted["armure_force"])
        src.append(f"Armure {granted['armure_force']} via Illumination")
    if af_rank:
        armor_ac = fb["armure_force"]["ac_by_rank"][str(af_rank)]
        active.append(f"{' + '.join(src)} (+{armor_ac} CA)")

    barrier_rd = 0
    if buff_ranks.get("barriere") and "barriere" in fb:
        if buff_allowed(data, "barriere", armor_tier):
            r = min(buff_ranks["barriere"], max_r)
            barrier_rd = fb["barriere"]["rd_by_rank"][str(r)]
            active.append(f"Barrière de Force {r} (RD {barrier_rd})")
        else:
            blocked.append(f"Barrière de Force (armure max : {fb['barriere']['armor_max']})")

    # Fureur (non cumulable avec Vitesse)
    fur_att, fur_for, fury_used = 0, 0, False
    if "fureur" in buff_ranks:
        if buff_allowed(data, "fureur", armor_tier):
            r = min(buff_ranks["fureur"], max_r)
            fur_att = fb["fureur"]["attacks_by_rank"][str(r)]
            fur_for = fb["fureur"]["for_mod_by_rank"][str(r)]
            if fur_att >= vit_att and fur_att > 0:
                fury_used = True
                active.append(f"Fureur {r} (+{fur_att} att/rd, +{fur_for} FOR)")
                if vit_att:
                    notes.append("Fureur retenue sur Vitesse (non cumulables)")
            else:
                notes.append(f"Fureur ignorée : Vitesse donne autant/plus d'attaques (+{vit_att})")
        else:
            blocked.append(f"Fureur (armure max : {fb['fureur']['armor_max']})")

    # Attaques & CA bonus finales
    if speed_mode == "auto":
        if fury_used:
            attacks, speed_ac = fur_att, 0
        elif vit_att:
            attacks, speed_ac = vit_att, vit_ac
        elif buff_allowed(data, "vitesse", armor_tier):
            attacks = phase["speed_attacks"]
            impl_rank = "2" if attacks == 1 else "3"
            speed_ac = fb["vitesse"].get("ac_by_rank", {}).get(impl_rank, 0) if attacks > 0 else 0
            if attacks:
                notes.append(f"Vitesse implicite au palier de phase (+{attacks} att/rd, +{speed_ac} CA)")
        else:
            attacks, speed_ac = 0, 0
            if phase["speed_attacks"]:
                notes.append("Vitesse indisponible sous cette armure → bonus de phase ignoré")
    else:
        attacks = {"none": 0, "knight": 1, "master": 2}[speed_mode]
        speed_ac = 0 if speed_mode == "none" else fb["vitesse"].get("ac_by_rank", {}).get("2" if speed_mode == "knight" else "3", 0)
        notes.append(f"--speed {speed_mode} : override manuel (bypass armure)")

    return {
        "attacks": attacks,
        "mod_all": mod_all,
        "for_add": fur_for if fury_used else 0,
        "speed_ac": speed_ac,
        "armor_ac": armor_ac,
        "barrier_rd": barrier_rd,
        "active": active,
        "blocked": blocked,
        "notes": notes,
    }


# ============================================================================
# Améliorations (établi)
# ============================================================================

def best_upgrades(data: Data, weapon: Weapon, level: int, mode: str, phase: dict) -> Upgrades:
    if weapon.upgrade_pool is None or weapon.slots == 0 or mode == "none":
        return Upgrades()

    pools: dict[str, list[dict]] = data.raw["upgrade_pools"].get(weapon.upgrade_pool, {})
    allowed = set(weapon.allowed_slots) if weapon.allowed_slots else None
    avail: dict[str, list[dict]] = {}
    for slot, items in pools.items():
        if allowed is not None and slot not in allowed:
            continue
        avail[slot] = [it for it in items if it.get("level_req", 99) <= level]

    if mode == "cap":
        # Plafond acté §3.A pondéré selon les slots autorisés par famille d'arme.
        up = Upgrades()
        weights = data.raw.get("slot_damage_weights", {}).get(weapon.upgrade_pool, {})
        if allowed is not None and weights:
            ratio = min(1.0, sum(weights.get(s, 0.0) for s in allowed))
        else:
            ratio = 1.0
        up.damage = round(float(phase["upgrade_cap"]) * ratio, 2)
        # les bonus d'Attaque (sans dégâts) restent autorisés sur les slots actifs : meilleur par emplacement
        for slot, items in avail.items():
            pure = [it for it in items if it["damage"] == 0 and it["onhit"] == 0]
            if pure:
                up.attack += max(it["attack"] for it in pure)
        slot_txt = f", {weapon.slots} slot{'s' if weapon.slots > 1 else ''}" if allowed is not None else ""
        up.detail = f"cap §3.A (+{up.damage:g} dég{slot_txt})"
        return up

    # mode "vanilla" : meilleur objet par emplacement (score dégâts > attaque > acéré)
    up = Upgrades()
    names = []
    for slot, items in avail.items():
        if not items:
            continue
        best = max(
            items,
            key=lambda it: (
                it["damage"] + it["onhit"] + 0.6 * it["massive"] + 2.0 * it["attack"] + (1.5 if it["keen"] else 0.0),
            ),
        )
        up.damage += best["damage"]
        up.onhit += best["onhit"]
        up.attack += best["attack"]
        up.massive += best["massive"]
        up.keen = up.keen or best["keen"]
        names.append(best["resref"])
    up.detail = ",".join(names) if names else "rien dispo"
    return up


def reingest_upgrades(csv_path: Path) -> dict:
    """Parse `WIP Améliorations.csv` → {pool: {slot: [items]}} et met à jour dpr_data.json."""
    slot_map = [
        ("Lame (mêlée)", "melee", "Lame"),
        ("Cellule d'énergie (mêlée)", "melee", "Cellule"),
        ("Poignée", "melee", "Poignée"),
        ("Chambre", "ranged", "Chambre"),
        ("Pack d'énergie", "ranged", "Pack"),
        ("Lunette", "ranged", "Lunette"),
        ("Émetteur", "saber", "Émetteur"),
        ("Lentille", "saber", "Lentille"),
        ("Cellule d'énergie (sabre)", "saber", "Cellule"),
        ("Cristal (sabre)", "saber", "Cristal"),
    ]
    pools: dict[str, dict[str, list[dict]]] = {"melee": {}, "ranged": {}, "saber": {}}
    with open(csv_path, encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.reader(fh))
    for row in rows[1:]:
        if len(row) < 6 or not row[0].startswith("u_"):
            continue
        resref, _name, empl, _tier, effects_van, loot = row[0], row[1], row[2], row[3], row[4], row[5]
        effects = row[6].strip() if len(row) > 6 and row[6].strip() else effects_van
        pool = slot = None
        for needle, p, s in slot_map:
            if needle.lower() in empl.lower():
                pool, slot = p, s
                break
        if pool is None:  # surcouches / sous-couches armures, cristaux de couleur, uniques
            continue
        effects_n = norm(effects)
        if effects_n.startswith("—") or "aucun effet" in effects_n:
            effects_n = ""
        dmg = sum(avg_dice(m) for m in re.findall(r"bonus aux degats \([^)]*\) \+(\d+d\d+|\d+)", effects_n))
        atk = sum(int(m) for m in re.findall(r"bonus d attaque \+(-?\d+)", effects_n))
        onhit = sum(float(m) for m in re.findall(r"en cas de coup au but \+(\d+)", effects_n))
        massive = sum(avg_dice(m) for m in re.findall(r"coups critiques plus importants \+(\d+d\d+|\d+)", effects_n))
        m_lvl = re.search(r"niv\. (\d+)\+", loot)
        level_req = int(m_lvl.group(1)) if m_lvl else 99
        pools[pool].setdefault(slot, []).append(
            {
                "resref": resref,
                "name": _name,
                "damage": round(dmg, 1),
                "onhit": round(onhit, 1),
                "attack": atk,
                "keen": "acere" in effects_n,
                "massive": round(massive, 1),
                "level_req": level_req,
            }
        )
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    data["upgrade_pools"] = pools
    DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    n = sum(len(items) for p in pools.values() for items in p.values())
    return n


def reingest_pouvoirs(csv_path: Path) -> list[str]:
    """Resynchronise force_buffs[].armor_max depuis la colonne « Armure max autorisée »
    du CSV WIP Spé Pouvoirs.csv (les '?' sont conservés tels quels). Retourne les mises à jour."""
    armor_map = [
        (("armure interdite", "interdite"), "sans"),
        (("armure legere", "legere"), "legere"),
        (("armure moyenne", "moyenne"), "moyenne"),
        (("armure lourde", "lourde"), "lourde"),
    ]
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    buffs = data["force_buffs"]
    updates: list[str] = []
    with open(csv_path, encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.reader(fh))
    for row in rows[1:]:
        if len(row) < 2:
            continue
        name, armor_raw = row[0], row[1]
        for key, buff in buffs.items():
            csv_key = buff.get("csv_key")
            if not csv_key or norm(csv_key) not in norm(name):
                continue
            a = norm(armor_raw)
            if a in ("?", ""):
                updates.append(f"{key} : '?' dans le CSV → valeur actuelle conservée ({buff['armor_max']})")
                continue
            for needles, tier in armor_map:
                if any(n in a for n in needles):
                    if buff["armor_max"] != tier:
                        updates.append(f"{key} : {buff['armor_max']} → {tier} (« {armor_raw.strip()} »)")
                        buff["armor_max"] = tier
                    else:
                        updates.append(f"{key} : {tier} (inchangé)")
                    break
    DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return updates


# ============================================================================
# Personnage & cible
# ============================================================================

@dataclass
class Enemy:
    name: str
    hp: int
    defense: int
    rd: int
    fort_save: int
    attack: int = 0
    dmg_hit: float = 0.0
    attacks: int = 1
    will_save: int = 0
    ref_save: int = 0


def enemy_fort_save(data: Data, level: int) -> int:
    f = data.raw["enemy_fort_save_formula"]
    return int(f["base"] + math.floor(level * f["savemult"]) + f["fort_bonus"])


@dataclass
class Char:
    preset: str
    level: int
    bab: int
    stats: dict[str, int]
    speed_attacks: int
    vp_per_level: int = 10
    class_ac: int = 0
    armor_tier: str = "sans"
    buff_ac: int = 0
    buff_rd: int = 0


def build_char(data: Data, phase_key: str, preset: str, overrides: dict[str, int],
               speed_mode: str, armor_tier: str = "sans") -> Char:
    phase = data.phases[phase_key]
    pr = data.presets[preset]
    stats = dict(pr["stats"][phase_key])
    stats.update(overrides)
    level = phase["level"]
    bab = int(level * pr["bab_progression"])
    if speed_mode == "auto":
        sp = phase["speed_attacks"]
    else:
        sp = {"none": 0, "knight": 1, "master": 2}[speed_mode]
    return Char(
        preset=preset,
        level=level,
        bab=bab,
        stats=stats,
        speed_attacks=sp,
        vp_per_level=pr.get("vp_per_level", 10),
        class_ac=pr.get("class_ac", {}).get(phase_key, 0),
        armor_tier=armor_tier,
    )


# ============================================================================
# Configurations candidates (arme × mode × main gauche × active)
# ============================================================================

@dataclass(frozen=True)
class Config:
    main: str
    off: str | None
    mode: str            # single | dual | double | twohand
    active: str          # none | flurry | power | critstrike

    def label(self, data: Data) -> str:
        m = data.weapon_by_key[self.main].name
        o = data.weapon_by_key[self.off].name if self.off else ""
        mode_fr = {"single": "1M", "dual": "2 armes", "double": "double", "twohand": "2M"}[self.mode]
        txt = f"{m} [{mode_fr}]"
        if self.off:
            txt += f" + {o}"
        return txt


def enumerate_configs(data: Data, feats: Feats, weapon_filter: str | None) -> list[Config]:
    gam2 = feats.rank("caracs", "gamorrean") >= 2
    flt = norm(weapon_filter) if weapon_filter else None
    melee_1m = [w.key for w in data.weapons if not w.ranged and w.wield == "1M" and w.key != "unarmed"]
    ranged_1m = [w.key for w in data.weapons if w.ranged and w.wield == "1M"]

    def keep(w: Weapon) -> bool:
        return flt in (None,) or flt in norm(w.name) or flt in norm(w.key) or flt in norm(w.family) or flt in norm(w.name.replace(" ", ""))

    actives = ["none"] + [a for a in ("flurry", "power", "critstrike") if feats.rank("actives", a) > 0]
    configs: list[Config] = []
    for w in data.weapons:
        if not keep(w):
            continue
        if w.key == "unarmed":
            configs += [Config(w.key, None, "single", a) for a in actives]
            continue
        modes: list[str] = []
        if w.wield == "1M":
            modes = ["single", "dual"]
        elif w.wield == "2M":
            modes = ["twohand"] + (["single", "dual"] if gam2 and not w.ranged else [])
        elif w.wield == "D":
            modes = ["double"] + (["single", "dual"] if gam2 and not w.ranged else [])
        for mode in modes:
            offs: list[str | None] = [None]
            if mode == "dual":
                pool = ranged_1m if w.ranged else melee_1m
                offs = [o for o in pool if o != w.key]
            for off in offs:
                configs += [Config(w.key, off, mode, a) for a in actives]
    return configs


# ============================================================================
# Évaluation
# ============================================================================

def spec_rank_for(feats: Feats, weapon: Weapon, data: Data) -> int:
    """Rang de spécialisation de famille s'appliquant à cette arme (0 sinon)."""
    fam = weapon.family
    if not fam:
        return 0
    if weapon.key == "unarmed" and not data.model.get("unarmed_counts_as_impact", True):
        return 0
    return feats.rank("familles", fam)


def effective_stats(data: Data, feats: Feats, base_stats: dict[str, int]) -> dict[str, int]:
    """Applique aux modificateurs de base les bonus des arbres de Spé caractéristique."""
    stats = dict(base_stats)
    for carac_key, rank in feats.caracs.items():
        if rank > 0:
            cdef = data.feats["caracs"].get(carac_key, {})
            sname = cdef.get("stat")
            inc = cdef.get("stat_mod_by_rank", {}).get(str(rank), 0)
            if sname and inc:
                stats[sname] = stats.get(sname, 0) + inc
    return stats


def evaluate(cfg: Config, data: Data, feats: Feats, char: Char, phase_key: str,
             enemy: Enemy, up_mode: str, sneak_dice: int, sneak_uptime: float,
             squad: dict | None = None) -> dict:
    w = data.weapon_by_key[cfg.main]
    off_w = data.weapon_by_key[cfg.off] if cfg.off else None
    phase = data.phases[phase_key]
    stats = effective_stats(data, feats, char.stats)
    F, D = stats.get("FOR", 0), stats.get("DEX", 0)
    C, I = stats.get("CON", 0), stats.get("INT", 0)
    S, CH = stats.get("SAG", 0), stats.get("CHA", 0)

    echani = feats.rank("caracs", "echani")
    gand = feats.rank("caracs", "gand")
    matukai = feats.rank("caracs", "matukai")
    duel_r = feats.rank("styles", "duel")
    amb_r = feats.rank("styles", "ambidextrie")
    heavy_r = feats.rank("styles", "arme_lourde")
    hc_r = feats.rank("styles", "haute_cadence")

    # ---- malus d'attaque par mode --------------------------------------------
    if cfg.mode == "dual":
        mal = data.feats["styles"]["ambidextrie"]["malus_by_rank"][str(amb_r)][:]
        if off_w and off_w.balanced:
            mal[0] += data.model["balanced_bonus"][0]
            mal[1] += data.model["balanced_bonus"][1]
    else:
        # En mode double (Arme haute cadence), le -5/-3/-2/-1 CA remplace le -6/-10 Atq vanilla.
        mal = [0, 0]

    # ---- attaque --------------------------------------------------------------
    style_atq = 0
    duel_ok = cfg.mode == "single" and (not w.ranged or data.model.get("duel_applies_ranged", False))
    if duel_ok:
        style_atq += duel_r * data.feats["styles"]["duel"]["attack_per_rank"]
    if cfg.mode == "twohand":
        style_atq += heavy_r * data.feats["styles"]["arme_lourde"]["attack_per_rank"]

    if w.ranged:
        attr_atk = I if (gand >= 1 and I > D) else D
    else:
        attr_atk = D if (echani >= 1 and D > F) else F
    if matukai >= 1:
        attr_atk += S

    active = {"attacks": 0, "attack": 0, "damage": 0, "range_mult": 1, "ac": 0}
    if cfg.active != "none":
        active.update(data.feats["actives"][cfg.active]["by_rank"][str(feats.rank("actives", cfg.active))])
    power_doubled = (
        cfg.active == "power"
        and not w.ranged
        and cfg.mode in ("dual", "double")
        and data.feats["actives"]["power"].get("dual_double_doubled", False)
    )
    power_dmg = active["damage"] * (2 if power_doubled else 1)
    if data.model.get("power_attack_cap"):
        power_dmg = min(power_dmg, data.model["power_attack_cap"])

    # ---- améliorations (une par arme physique ; l'arme double = UN SEUL jeu appliqué aux deux bouts) --
    up_main = best_upgrades(data, w, char.level, up_mode, phase)
    if cfg.mode == "double":
        off_w, up_off = w, up_main  # second bout de la même arme
    elif off_w:
        up_off = best_upgrades(data, off_w, char.level, up_mode, phase)
    else:
        up_off = Upgrades()

    def hand_static(weapon: Weapon, up: Upgrades, is_off: bool) -> float:
        dmg = weapon.dmg_avg + up.per_hit
        # multiplicateur de caractéristique
        if weapon.ranged:
            attr = I if (gand >= 2 and I > D) else D
            if cfg.mode == "twohand":
                mult = data.feats["styles"]["arme_lourde"]["ranged_mult_by_rank"][str(heavy_r)]
            elif cfg.mode == "double":
                mult = 1.5 if not is_off else 0.5
            elif cfg.mode == "dual":
                r_mults = data.model.get("ranged_1m_d_mult", [1.0, 0.5])
                mult = r_mults[1 if is_off else 0]
            else:
                mult = data.model.get("ranged_1m_duel_mult", 1.5)
            dmg += attr * mult
        else:
            if cfg.mode == "twohand":
                mult = data.feats["styles"]["arme_lourde"]["melee_mult_by_rank"][str(heavy_r)]
            elif cfg.mode == "double":
                mult = 1.5 if not is_off else 0.5
            elif cfg.mode == "dual":
                mult = 1.0 if not is_off else 0.5
            else:
                mult = 1.5
            attr = D if (echani >= 2 and D > F) else F
            dmg += attr * mult
        # arme haute cadence : +N dégâts par bout
        if cfg.mode == "double" and hc_r:
            dmg += hc_r * data.feats["styles"]["haute_cadence"]["dmg_per_rank_per_hand"]
        # spécialisation de famille (par arme équipée de la famille)
        sr = spec_rank_for(feats, weapon, data)
        if sr >= 1:
            dmg += 2
            if weapon.family == "penetrant" and sr >= 3:
                dmg += data.feats["familles"]["penetrant"]["rank3"]["damage"]
        dmg += power_dmg
        return dmg

    d_main = hand_static(w, up_main, False)
    d_off = hand_static(off_w, up_off, True) if off_w else 0.0

    # ---- critique -------------------------------------------------------------
    def crit_params(weapon: Weapon, up: Upgrades) -> tuple[int, int, float]:
        rng = weapon.crit_range * (2 if up.keen else 1)
        rng = rng * active["range_mult"]
        if duel_ok and data.model.get("duel_crit_mode") == "range_ext":
            rng += duel_r * data.feats["styles"]["duel"]["crit_range_per_rank"]
        rng = min(rng, 20)
        mult = weapon.crit_mult
        if weapon.family == "assassin" and spec_rank_for(feats, weapon, data) >= 3:
            mult += data.feats["familles"]["assassin"]["rank3"]["crit_mult"]
        massive = weapon.massive_avg + up.massive
        return rng, mult, massive

    rng_m, mult_m, massive_m = crit_params(w, up_main)
    rng_o, mult_o, massive_o = crit_params(off_w, up_off) if off_w else (0, 2, 0.0)

    # ---- défense effective (bris d'armure de la Spé Traditionnelle) -----------
    def_eff = enemy.defense
    brk = 0.0
    for hw in (w, off_w):
        if hw and hw.family == "traditionnelle":
            sr = spec_rank_for(feats, hw, data)
            if sr >= 3:
                brk = max(brk, abs(data.feats["familles"]["traditionnelle"]["rank3"]["armor_break"]))
            elif sr >= 2:
                brk = max(brk, 0.5 * abs(data.feats["familles"]["traditionnelle"]["rank2"]["armor_break"]))
    def_eff -= brk

    # ---- attaques par round ----------------------------------------------------
    n_main = 1 + active["attacks"] + char.speed_attacks
    if w.family == "assaut" and spec_rank_for(feats, w, data) >= 3:
        n_main += data.feats["familles"]["assaut"]["rank3"]["extra_main_attack"]
    n_off = 1 if cfg.mode in ("dual", "double") else 0

    # ---- attaque totale par main ----------------------------------------------
    atq_common = char.bab + attr_atk + style_atq + active["attack"]
    atq_m = atq_common + mal[0] + up_main.attack + (spec_rank_for(feats, w, data) >= 1) * 2
    atq_o = atq_common + mal[1] + up_off.attack + ((spec_rank_for(feats, off_w, data) >= 1) * 2 if off_w else 0)

    # ---- attaque sournoise (cible contrôlée / dépourvue) ------------------------
    def sneak_avg(weapon: Weapon) -> float:
        dice = sneak_dice
        if weapon.family == "assassin" and spec_rank_for(feats, weapon, data) >= 2:
            dice += data.feats["familles"]["assassin"]["rank2"]["sneak_dice"]
        return 3.5 * dice * sneak_uptime

    sn_m, sn_o = sneak_avg(w), (sneak_avg(off_w) if off_w else 0.0)

    # ---- dégâts attendus, RD après multiplication critique ----------------------
    def expected(dmg: float, atq: float, rng: int, mult: int, massive: float, sn: float) -> float:
        p = hit_probability(atq, def_eff)
        p_threat = rng / 20.0
        p_crit = p * p_threat
        base = max(dmg - enemy.rd, 0.0) + sn
        crit = max(dmg * mult + massive * mult - enemy.rd, 0.0) + sn
        return (p - p_crit) * base + p_crit * crit

    e_main = expected(d_main, atq_m, rng_m, mult_m, massive_m, sn_m)
    e_off = expected(d_off, atq_o, rng_o, mult_o, massive_o, sn_o) if off_w else 0.0
    dpr_weapons = n_main * e_main + n_off * e_off

    # ---- procs de contrôle (Impact / Tactique) et Mutilation (Résonance) ------
    p_no_ctrl = 1.0
    ctrl_dur = 0
    ctrl_dc = 10 + char.level + attr_atk
    p_fail_fort = save_fail_probability(ctrl_dc, enemy.fort_save)
    for hw, h_atq, h_rng, h_cnt in ((w, atq_m, rng_m, n_main), (off_w, atq_o, rng_o, n_off)):
        if hw and hw.family in ("impact", "tactique") and spec_rank_for(feats, hw, data) >= 2 and h_cnt > 0:
            dur = 1 + (spec_rank_for(feats, hw, data) >= 3)
            ctrl_dur = max(ctrl_dur, dur)
            p_one = hit_probability(h_atq, def_eff) * (h_rng / 20.0) * p_fail_fort
            p_no_ctrl *= (1.0 - p_one) ** h_cnt
    p_ctrl = 1.0 - p_no_ctrl
    ctrl_uptime = (1.0 - (1.0 - p_ctrl) ** 2) if ctrl_dur >= 2 else (p_ctrl if ctrl_dur == 1 else 0.0)

    mut_debuff = 0.0
    p_no_mut = 1.0
    mut_rank = 0
    mut_dc = 5 + char.level + attr_atk
    p_fail_ref = save_fail_probability(mut_dc, enemy.ref_save)
    for hw, h_atq, h_cnt in ((w, atq_m, n_main), (off_w, atq_o, n_off)):
        if hw and hw.family == "resonance" and spec_rank_for(feats, hw, data) >= 2 and h_cnt > 0:
            mut_rank = max(mut_rank, spec_rank_for(feats, hw, data))
            p_one = hit_probability(h_atq, def_eff) * p_fail_ref
            p_no_mut *= (1.0 - p_one) ** h_cnt
    if mut_rank >= 2:
        p_mut_round = 1.0 - p_no_mut
        max_pen = 4.0 if mut_rank == 2 else 8.0
        mut_debuff = min(max_pen, max_pen * p_mut_round)

    # ---- défense et survie du build (CA, RD, Immunité, Esquive, TTD) ----------
    armor_tier = char.armor_tier
    armor_def = data.raw["armor_stats"][armor_tier]
    item_ac = armor_def["item_ac_by_phase"].get(phase_key, 0)
    upg_ac = armor_def.get("upg_ac_by_phase", {}).get(phase_key, 0)
    upg_rd = armor_def.get("upg_rd_by_phase", {}).get(phase_key, 0)
    upg_imm = armor_def.get("upg_imm_by_phase", {}).get(phase_key, 0.0)

    dex_for_ac = S if matukai >= 3 else D
    ac_dex = dex_for_ac if echani >= 3 else min(dex_for_ac, armor_def["max_dex"])

    style_ac = 0
    if cfg.mode == "dual":
        style_ac = data.feats["styles"]["ambidextrie"].get("ac_by_rank", {}).get(str(amb_r), 0)
    elif cfg.mode == "double":
        style_ac = data.feats["styles"]["haute_cadence"].get("ac_by_rank", {}).get(str(hc_r), -5)

    active_ac = active.get("ac", 0)

    jugg_r = feats.rank("armures", "juggernaut")
    blind_r = feats.rank("armures", "blindage")
    peau_r = feats.rank("armures", "seconde_peau")
    tough_r = feats.rank("armures", "robustesse")

    armor_feat_ac = 0
    armor_feat_rd = 0
    armor_feat_imm = 0.0
    player_dodge = 0.0
    shield_mult = 1.0

    if armor_tier == "lourde" and jugg_r > 0:
        j_def = data.feats["armures"]["juggernaut"]
        armor_feat_rd = j_def["rd_by_rank"].get(str(jugg_r), 0)
        armor_feat_imm = j_def["immunity_by_rank"].get(str(jugg_r), 0.0)
    elif armor_tier == "moyenne" and blind_r > 0:
        b_def = data.feats["armures"]["blindage"]
        armor_feat_rd = b_def["rd_by_rank"].get(str(blind_r), 0)
        armor_feat_ac = b_def["ac_by_rank"].get(str(blind_r), 0)
        shield_mult = b_def["shield_mult_by_rank"].get(str(blind_r), 1.0)
    elif armor_tier == "legere" and peau_r > 0:
        p_def = data.feats["armures"]["seconde_peau"]
        armor_feat_ac = p_def["ac_by_rank"].get(str(peau_r), 0)
        player_dodge = p_def["dodge_by_rank"].get(str(peau_r), 0.0)

    nomi_ac = max(0, CH) if feats.rank("caracs", "nomi") >= 3 else 0
    kraith_rd = max(0, C) if feats.rank("caracs", "kraith") >= 1 else 0
    tough_rd = data.feats["armures"]["robustesse"]["rd_by_rank"].get(str(tough_r), 0) if tough_r > 0 else 0
    tough_hp = data.feats["armures"]["robustesse"]["hp_per_level_by_rank"].get(str(tough_r), 0) if tough_r > 0 else 0

    player_ac = (
        10 + char.class_ac + armor_def["base_ac"] + item_ac + upg_ac
        + ac_dex + style_ac + active_ac + armor_feat_ac + nomi_ac + char.buff_ac
    )
    player_rd = armor_def["native_rd"] + upg_rd + armor_feat_rd + tough_rd + kraith_rd + char.buff_rd
    imm_cap = data.model.get("immunity_cap", 0.50)
    player_imm = min(imm_cap, upg_imm + armor_feat_imm)

    player_hp = max(1, (char.vp_per_level + C + tough_hp) * char.level)
    shield_hp = armor_def.get("shield_hp_by_phase", {}).get(phase_key, 0) * shield_mult
    player_ehp = player_hp + shield_hp

    def survival_vs(att_attack: int, att_dmg_hit: float, att_attacks: int, allow_ctrl: bool = True) -> dict:
        if att_attacks <= 0 or att_dmg_hit <= 0:
            return {"p_enemy_hit": 0.0, "dtps": 0.0, "ttd": float("inf"), "p_miss": 0.0, "active_frac": 1.0}
        debuff = mut_debuff if allow_ctrl else 0.0
        eff_atk = att_attack - debuff
        eff_dmg = max(0.0, att_dmg_hit - debuff)
        p_e_hit = hit_probability(eff_atk, player_ac)
        active_frac = (1.0 - ctrl_uptime) if allow_ctrl else 1.0
        dmg_after = max(0.0, eff_dmg * (1.0 - player_imm) - player_rd)
        dtps = att_attacks * active_frac * p_e_hit * (1.0 - player_dodge) * dmg_after
        p_e_miss = 1.0 - p_e_hit * (1.0 - player_dodge)
        ttd = player_ehp / dtps if dtps > 0 else float("inf")
        return {"p_enemy_hit": p_e_hit, "dtps": dtps, "ttd": ttd, "p_miss": p_e_miss, "active_frac": active_frac}

    boss_surv = survival_vs(enemy.attack, enemy.dmg_hit, enemy.attacks, allow_ctrl=True)
    sq_src = squad or data.raw.get("squad_enemies", {}).get(phase_key, {})
    squad_surv = survival_vs(sq_src.get("attack", 0), sq_src.get("dmg_hit", 0.0), sq_src.get("attacks", 0), allow_ctrl=False)

    thorn_dpr = enemy.attacks * boss_surv["active_frac"] * boss_surv["p_miss"] * max(0, S) if matukai >= 3 else 0.0
    dpr = dpr_weapons + thorn_dpr
    ttk = enemy.hp / dpr if dpr > 0 else float("inf")

    # ---- texte effets secondaires ---------------------------------------------
    procs: list[str] = []
    if ctrl_dur > 0:
        procs.append(f"proc contrôle ~{p_ctrl * 100:.0f}%/rd (DD Vigueur {ctrl_dc}, {ctrl_dur} tour(s), uptime {ctrl_uptime * 100:.0f}%) → sournoise possible")
    if brk:
        procs.append(f"bris d'armure −{brk:g} CA soutenu")
    if mut_debuff > 0:
        procs.append(f"Mutilation −{mut_debuff:.1f} Atq/Dég ennemi")
    if thorn_dpr > 0:
        procs.append(f"riposte Matukai +{thorn_dpr:.1f} DPR")

    return {
        "cfg": cfg,
        "label": cfg.label(data),
        "active": cfg.active,
        "attack_main": round(atq_m),
        "p_hit": hit_probability(atq_m, def_eff),
        "attacks": n_main + n_off,
        "dmg_hit_net": round(max(d_main - enemy.rd, 0.0) + sn_m, 1),
        "dpr_weapons": round(dpr_weapons, 1),
        "dpr_thorns": round(thorn_dpr, 1),
        "dpr": round(dpr, 1),
        "ttk": ttk,
        "player_ac": player_ac,
        "player_rd": player_rd,
        "player_imm": player_imm,
        "player_dodge": player_dodge,
        "player_hp": player_hp,
        "shield_hp": shield_hp,
        "boss_hit_pct": boss_surv["p_enemy_hit"] * 100,
        "boss_dtps": boss_surv["dtps"],
        "boss_ttd": boss_surv["ttd"],
        "squad_hit_pct": squad_surv["p_enemy_hit"] * 100,
        "squad_dtps": squad_surv["dtps"],
        "squad_ttd": squad_surv["ttd"],
        "upgrades": f"main: {up_main.detail}" + (f" | off: {up_off.detail}" if cfg.off else ""),
        "procs": " ; ".join(procs),
    }


def verdict(ttk: float) -> str:
    if ttk == float("inf"):
        return "AUCUN DÉGÂT"
    if ttk < 4:
        return "TROP VITE (<4 rds — règle d'or §3.B)"
    if ttk < 5:
        return "rapide (4-5)"
    if ttk <= 10:
        return "CIBLE ✓ (5-10)"
    if ttk <= 15:
        return "long (10-15)"
    return "TROP LONG (>15)"


def verdict_ttd(ttd: float) -> str:
    if ttd == float("inf"):
        return "INVULNÉRABLE (0 subi)"
    if ttd < 4:
        return "MORT TROP VITE (<4 rds)"
    if ttd < 5:
        return "fragile (4-5)"
    if ttd <= 10:
        return "CIBLE ✓ (5-10)"
    if ttd <= 15:
        return "solide (10-15)"
    return "TANKY (>15)"


# ============================================================================
# Rapport
# ============================================================================

def run_report(data: Data, feats: Feats, args) -> None:
    preset = args.char if args.char in data.presets else "gardien"
    overrides = {}
    if args.stats:
        for pair in args.stats.split(","):
            k, v = pair.split("=")
            overrides[norm(k).upper()] = int(v)

    armor_tier = parse_armor(args.armor)
    buff_ranks, buff_unknown = parse_buffs(data, args.buffs)
    buffs = resolve_buffs(data, buff_ranks, armor_tier, data.phases["late"], args.speed)
    armor_label = data.raw["armor_tiers"][armor_tier]
    armor_def = data.raw["armor_stats"][armor_tier]

    phase_keys = list(data.phases.keys()) if args.phases == "all" else [p.strip() for p in args.phases.split(",")]

    print()
    print("=" * 124)
    print(f" DPR CHECK — dons : {args.feats or '(aucun)'}")
    if feats.unknown:
        print(f" ⚠ Dons non reconnus (ignorés) : {', '.join(feats.unknown)}")
        print(f"   (liste : python tools/dpr_check.py --list-feats)")
    if buff_unknown:
        print(f" ⚠ Pouvoirs non reconnus (ignorés) : {', '.join(buff_unknown)}")
    print(f" Perso : {data.presets[preset]['label']} | améliorations : {args.upgrades} | "
          f"sournoise : {args.sneak_dice}d6 à {int(args.sneak_uptime * 100)}% des rounds")
    print(f" Armure portée : {armor_label} (CA base {armor_def['base_ac']}, DEX max +{armor_def['max_dex']}, "
          f"RD native {armor_def['native_rd']}, {armor_def['slots']} slot(s) — gâte aussi les pouvoirs)")
    if args.buffs:
        print(f" Pouvoirs demandés : {args.buffs}")
    if buffs["active"]:
        print(f" ✓ Actifs   : {' ; '.join(buffs['active'])}")
    if buffs["blocked"]:
        print(f" ✗ Bloqués  : {' ; '.join(buffs['blocked'])}  → armure {armor_tier} trop lourde")
    for note in buffs["notes"]:
        print(f" ℹ {note}")
    print("=" * 124)

    md_lines: list[str] = []
    for pk in phase_keys:
        phase = data.phases[pk]
        enemy_raw = data.enemies.get(pk, {})
        squad_raw = data.raw.get("squad_enemies", {}).get(pk, {})
        if args.enemy:
            parts = [float(x) for x in args.enemy.split(",")]
            hp, ca, rd = int(parts[0]), int(parts[1]), int(parts[2])
            enemy = Enemy(
                "boss custom", hp, ca, rd,
                enemy_fort_save(data, args.level or phase["level"]),
                attack=int(parts[3]) if len(parts) > 3 else enemy_raw.get("attack", 0),
                dmg_hit=float(parts[4]) if len(parts) > 4 else enemy_raw.get("dmg_hit", 0.0),
                attacks=int(parts[5]) if len(parts) > 5 else enemy_raw.get("attacks", 1),
                will_save=enemy_raw.get("will_save", 0),
                ref_save=enemy_raw.get("ref_save", 0),
            )
        else:
            enemy = Enemy(
                "", enemy_raw["hp"], enemy_raw["defense"], enemy_raw["rd"],
                enemy_fort_save(data, phase["level"]),
                attack=enemy_raw.get("attack", 0),
                dmg_hit=enemy_raw.get("dmg_hit", 0.0),
                attacks=enemy_raw.get("attacks", 1),
                will_save=enemy_raw.get("will_save", 0),
                ref_save=enemy_raw.get("ref_save", 0),
            )
        char = build_char(data, pk, preset, overrides, "auto", armor_tier=armor_tier)
        # application des buffs autorisés par l'armure
        buffs = resolve_buffs(data, buff_ranks, armor_tier, phase, args.speed)
        for k in char.stats:
            char.stats[k] += buffs["mod_all"]
        char.stats["FOR"] += buffs["for_add"]
        char.speed_attacks = buffs["attacks"]
        char.buff_ac = buffs["speed_ac"] + buffs["armor_ac"]
        char.buff_rd = buffs["barrier_rd"]
        if args.level:
            char.level = args.level

        eff_stats = effective_stats(data, feats, char.stats)
        configs = enumerate_configs(data, feats, args.weapon)
        results = []
        for cfg in configs:
            r = evaluate(cfg, data, feats, char, pk, enemy, args.upgrades,
                         args.sneak_dice, args.sneak_uptime, squad=squad_raw)
            results.append(r)
        results.sort(key=lambda r: r["dpr"], reverse=True)
        if not results:
            print(f"\n[{pk}] Aucune configuration candidate (filtre arme ?)")
            continue

        best = results[0]
        tgt = f", {enemy.name}" if enemy.name else " (boss étalon §9)"
        header = (f" {pk.upper()} (Niv. {char.level}{tgt} : {enemy.hp} PV / CA {enemy.defense} / RD {enemy.rd} / "
                  f"Atq {enemy.attack:+d}, {enemy.attacks}×{enemy.dmg_hit:g}) — BAB {char.bab} | stats "
                  + " ".join(f"{k}{v:+d}" for k, v in eff_stats.items() if v))
        print("\n" + header)
        print("-" * len(header))
        print(f" 🏆 MEILLEURE CONFIG : {best['label']} | active : {best['active']} | {best['attacks']} att/rd | "
              f"Atq {best['attack_main']:+d} | toucher {best['p_hit'] * 100:.0f}% | "
              f"{best['dmg_hit_net']} dég nets/coup | DPR {best['dpr']} | {best['ttk']:.1f} rounds → {verdict(best['ttk'])}")
        print(f" 🛡 SURVIE (Boss)    : CA {best['player_ac']} | RD {best['player_rd']} | "
              f"Imm {best['player_imm'] * 100:.0f}% | Esq {best['player_dodge'] * 100:.0f}% | "
              f"EHP {best['player_hp']:.0f}+{best['shield_hp']:.0f} | "
              f"subi {best['boss_dtps']:.1f}/rd ({best['boss_hit_pct']:.0f}% hit) → TTD {best['boss_ttd']:.1f} rds ({verdict_ttd(best['boss_ttd'])})")
        if squad_raw:
            print(f" ⚔ SURVIE (3×Set_3) : subi {best['squad_dtps']:.1f}/rd ({best['squad_hit_pct']:.0f}% hit) → TTD {best['squad_ttd']:.1f} rds")
        print(f"    améliorations : {best['upgrades']}")
        if best["procs"]:
            print(f"    effets : {best['procs']}")

        cols = f" {'#':>2} | {'arme [mode]':<36} | {'active':<10} | {'Atq':>4} | {'%':>4} | {'att':>3} | {'dég/hit':>7} | {'DPR':>6} | {'TTK':>5} | {'CA':>3} | {'TTD':>5} | verdict"
        print(cols)
        print("-" * len(cols))
        for i, r in enumerate(results[: args.top], 1):
            ttd_s = "  inf" if r["boss_ttd"] == float("inf") else f"{r['boss_ttd']:>5.1f}"
            print(f" {i:>2} | {r['label'][:36]:<36} | {r['active']:<10} | {r['attack_main']:>+4d} | "
                  f"{r['p_hit'] * 100:>3.0f}% | {r['attacks']:>3} | {r['dmg_hit_net']:>7.1f} | {r['dpr']:>6.1f} | "
                  f"{r['ttk']:>5.1f} | {r['player_ac']:>3} | {ttd_s} | {verdict(r['ttk'])}")

        ttd_md = "∞" if best["boss_ttd"] == float("inf") else f"{best['boss_ttd']:.1f}"
        md_lines.append(f"### {pk.upper()} — {best['label']} ({best['active']}) : "
                        f"**DPR {best['dpr']}** → TTK {best['ttk']:.1f} rds ({verdict(best['ttk'])}) | "
                        f"CA {best['player_ac']} / RD {best['player_rd']} / TTD {ttd_md} rds")

    print("\n" + "-" * 124)
    print(" Hypothèses : critique confirmé (≈ proba toucher) ; RD boss soustraite par coup après mult ; "
          "Vitesse = attaques main directrice ;")
    print(" 'crit chance +N' du Duel = +N de plage ; Duel = mêlée/mains nues ; arme équilibrée = "
          f"{data.model['balanced_bonus']} Atq ; mains nues = famille Impact ;")
    print(" Distance 1M/D = +100% / +50% DEX (ou INT via Gand II) ; plafonds d'upgrades pondérés par slots autorisés.")
    print(" Armure & Défenses : CA, plafond DEX, RD native, 1/2/1 slots, arbres d'armure, Boucliers & pouvoirs gatés "
          "(dpr_data.json → armor_stats, force_buffs).")
    print(" Valeurs éditables : tools/dpr_data.json (armes, dons, armures, boss, plafonds, pouvoirs). "
          "Resync après édition des CSV : --reingest-upgrades / --reingest-pouvoirs.")
    if args.md:
        print("\n## Synthèse (markdown)")
        print("\n".join(md_lines))


# ============================================================================
# CLI
# ============================================================================

def list_feats(data: Data) -> None:
    print("\nDons reconnus (catégorie — nom — alias) :")
    for cat, cat_fr in (("styles", "Styles"), ("familles", "Spécialisations"), ("caracs", "Caractéristique"),
                        ("armures", "Armures & Défenses"), ("actives", "Actives")):
        print(f"\n[{cat_fr}]")
        for key, feat in data.feats.get(cat, {}).items():
            aliases = ", ".join(feat.get("aliases", []))
            print(f"  {feat['label']:<46} (rang max {feat.get('max', 3)})  {aliases}")
    print("\n[Pouvoirs de la Force — via --buffs, gatés par --armor]")
    tiers = data.raw["armor_tiers"]
    for key, buff in data.raw.get("force_buffs", {}).items():
        aliases = ", ".join(buff.get("aliases", []))
        print(f"  {buff['label']:<46} armure max : {tiers[buff['armor_max']]:<28} {aliases}")
    print("\nSyntaxe : \"Duel 3, Spécialisation Arme Laser 2, Tir rapide\" (rang en chiffre arabe ou romain, 1 par défaut).")
    print("Buffs  : --armor moyenne --buffs \"Vitesse 3,Talent de Force 3\" (bloqués → affichés et ignorés).")


def selftest() -> None:
    assert abs(hit_probability(20, 20) - 0.95) < 1e-9
    assert abs(hit_probability(10, 20) - 0.55) < 1e-9
    assert abs(hit_probability(0, 20) - 0.05) < 1e-9
    assert avg_dice("2d6") == 7.0 and avg_dice("5") == 5.0
    data = Data(json.loads(DATA_FILE.read_text(encoding="utf-8")))
    assert "gaffi" not in data.weapon_by_key
    feats = parse_feats(data, "Duel III, Spécialisation Arme Laser 3, Coup critique 2, MOD_AMBIDEXTRY_3, Tir rapide")
    assert feats.rank("styles", "duel") == 3
    assert feats.rank("familles", "laser") == 3
    assert feats.rank("actives", "critstrike") == 2
    assert feats.rank("styles", "ambidextrie") == 3
    assert feats.rank("actives", "flurry") == 1
    assert not feats.unknown, feats.unknown
    char = build_char(data, "early", "gardien", {}, "auto")
    enemy = Enemy("t", 120, 20, 3, 19)
    res = evaluate(Config("lightsaber", None, "single", "none"), data, feats, char, "early", enemy, "cap", 0, 0.0)
    assert res["dpr"] > 0
    # --- slots d'upgrades par famille ------------------------------------------
    up_imp = best_upgrades(data, data.weapon_by_key["force_pike"], 26, "cap", data.phases["late"])
    up_trad = best_upgrades(data, data.weapon_by_key["long_sword"], 26, "cap", data.phases["late"])
    up_res = best_upgrades(data, data.weapon_by_key["vibroblade"], 26, "cap", data.phases["late"])
    assert abs(up_imp.damage - 1.5) < 1e-6, up_imp
    assert abs(up_trad.damage - 5.0) < 1e-6, up_trad
    assert abs(up_res.damage - 10.0) < 1e-6, up_res
    # --- distance +100% / +50% DEX (et INT avec Gand II) ----------------------
    c_sen = build_char(data, "late", "sentinelle", {}, "auto")  # DEX +9, INT +3
    f_none = parse_feats(data, "")
    pistol_dmg = data.weapon_by_key["blaster_pistol"].dmg_avg
    rep_dmg = data.weapon_by_key["repeating"].dmg_avg
    r_pistol = evaluate(Config("blaster_pistol", None, "single", "none"), data, f_none, c_sen, "late", enemy, "none", 0, 0.0)
    assert r_pistol["dmg_hit_net"] == round(pistol_dmg + 9.0 - 3, 1), r_pistol
    r_rep = evaluate(Config("repeating", None, "double", "none"), data, f_none, c_sen, "late", enemy, "none", 0, 0.0)
    assert r_rep["dmg_hit_net"] == round(rep_dmg + 9.0 - 3, 1), r_rep
    # En mode double (Arme haute cadence), malus attaque = [0, 0] (plus de -6/-10 vanilla)
    assert r_rep["attack_main"] == c_sen.bab + 9, r_rep
    c_int = build_char(data, "late", "sentinelle", {"DEX": 2, "INT": 8}, "auto")
    f_gand = parse_feats(data, "Chasseur de prime Gand 2")
    r_gand = evaluate(Config("blaster_pistol", None, "single", "none"), data, f_gand, c_int, "late", enemy, "none", 0, 0.0)
    assert r_gand["dmg_hit_net"] == round(pistol_dmg + (8 + 1) - 3, 1), r_gand  # +1 mod INT rang II
    # --- armure & buffs -------------------------------------------------------
    assert parse_armor("Robe") == "sans" and parse_armor("lourde") == "lourde"
    ranks, unk = parse_buffs(data, "Vitesse 3, Talent de Force 2, Illumination")
    assert ranks == {"vitesse": 3, "valor": 2, "illumination": 1} and not unk, (ranks, unk)
    assert not buff_allowed(data, "vitesse", "legere")       # interdite sous armure
    assert buff_allowed(data, "vitesse", "sans")
    assert buff_allowed(data, "valor", "legere")
    assert buff_allowed(data, "illumination", "moyenne")
    assert buff_allowed(data, "fureur", "sans") and not buff_allowed(data, "fureur", "lourde")  # CSV : « Armure interdite »
    # vitesse bloquée par armure lourde → 0 attaque bonus, talent bloqué
    r = resolve_buffs(data, {"vitesse": 3, "valor": 3}, "lourde", data.phases["late"], "auto")
    assert r["attacks"] == 0 and r["mod_all"] == 0 and len(r["blocked"]) == 2, r
    # illumination ≤ moyenne accorde vitesse+valor malgré le blocage de Vitesse seule
    r2 = resolve_buffs(data, {"illumination": 1}, "moyenne", data.phases["late"], "auto")
    assert r2["attacks"] == 2 and r2["mod_all"] == 3 and not r2["blocked"], r2
    # plafonnement des rangs en phase early (Illumination bloquée avant Niv. 15, Vitesse max 1)
    r_early = resolve_buffs(data, {"vitesse": 3, "illumination": 1}, "sans", data.phases["early"], "auto")
    assert r_early["attacks"] == 1 and r_early["speed_ac"] == 2, r_early
    # fureur ≥ vitesse → retenue (bonus FOR)
    r3 = resolve_buffs(data, {"vitesse": 3, "fureur": 3}, "sans", data.phases["late"], "auto")
    assert r3["attacks"] == 2 and r3["for_add"] == 3 and r3["speed_ac"] == 0, r3
    # --- arbres d'armures, spé carac défensives & TTD -------------------------
    e_late = data.enemies["late"]
    boss_late = Enemy("boss", e_late["hp"], e_late["defense"], e_late["rd"],
                      enemy_fort_save(data, 26), e_late["attack"], e_late["dmg_hit"], e_late["attacks"],
                      e_late["will_save"], e_late["ref_save"])
    c_heavy = build_char(data, "late", "gardien", {}, "auto", armor_tier="lourde")
    f_jugg = parse_feats(data, "Juggernaut 3, Robustesse 2, Voie du dragon Kraith 1")
    r_jugg = evaluate(Config("lightsaber", None, "single", "none"), data, f_jugg, c_heavy, "late", boss_late, "cap", 0, 0.0)
    assert r_jugg["player_rd"] == 4 + 3 + 5 + 2 + 6, r_jugg
    assert abs(r_jugg["player_imm"] - 0.45) < 1e-9, r_jugg
    assert r_jugg["boss_ttd"] > 0, r_jugg
    c_light = build_char(data, "late", "sentinelle", {}, "auto", armor_tier="legere")
    f_peau = parse_feats(data, "Seconde Peau 3, Techniques Echanis 3")
    r_peau = evaluate(Config("lightsaber", None, "single", "none"), data, f_peau, c_light, "late", boss_late, "cap", 0, 0.0)
    assert abs(r_peau["player_dodge"] - 0.30) < 1e-9, r_peau
    # Echani III supprime le plafond DEX (+9 + 1 = +10 vs max_dex +4)
    assert r_peau["player_ac"] == 10 + 10 + 5 + 4 + 3 + (9 + 1) + 3, r_peau
    c_med = build_char(data, "late", "sentinelle", {}, "auto", armor_tier="moyenne")
    f_med = parse_feats(data, "Blindage de Combat 3")
    r_med = evaluate(Config("lightsaber", None, "single", "none"), data, f_med, c_med, "late", boss_late, "cap", 0, 0.0)
    assert r_med["shield_hp"] == 180 and r_med["player_rd"] == 2 + 2 + 5, r_med
    print("selftest OK")


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):  # console Windows en cp1252 → accents/emoji
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="KotOR 2 Overhaul — DPR checker (équilibrage par dons)")
    ap.add_argument("--feats", default="", help="Dons choisis, ex. \"Duel 3,Spécialisation Arme Laser 3,Coup critique 3\"")
    ap.add_argument("--char", default="gardien", help="Preset : gardien | sentinelle | consulaire")
    ap.add_argument("--stats", help="Override de modificateurs, ex. \"FOR=5,DEX=9,SAG=7\"")
    ap.add_argument("--phases", default="all", help="early,mid,late ou all")
    ap.add_argument("--level", type=int, help="Niveau perso alternatif (remplace celui de la phase pour les paliers d'améliorations)")
    ap.add_argument("--enemy", help="Boss custom \"PV,CA,RD[,ATQ,DMG,ATT]\" (ex. 200,26,5)")
    ap.add_argument("--armor", default="sans",
                    help="Armure portée : sans | legere | moyenne | lourde (défaut : sans = robe Jedi). "
                         "Gâte les pouvoirs de la Force et simule CA, plafond DEX, RD native, boucliers et arbres d'armure")
    ap.add_argument("--buffs", default="",
                    help="Pouvoirs de la Force du build, ex. \"Vitesse 3,Talent de Force 2,Illumination\" — "
                         "appliqués uniquement si l'armure les autorise (voir dpr_data.json → force_buffs)")
    ap.add_argument("--speed", default="auto", choices=["auto", "none", "knight", "master"],
                    help="Attaques bonus de Vitesse. auto : rang de phase si l'armure l'autorise "
                         "(0/1/2, comme le contrat §9) ou rang du buff Vitesse/Fureur ; "
                         "none/knight/master : override manuel qui bypass le gating d'armure")
    ap.add_argument("--upgrades", default="cap", choices=["cap", "vanilla", "none"],
                    help="cap : plafonds actés +2/+5/+10 pondérés par slots ; vanilla : meilleurs items du CSV ; none")
    ap.add_argument("--sneak-dice", type=int, default=0, help="Dés d'Attaque sournoise de classe (ex. 4 pour 4d6)")
    ap.add_argument("--sneak-uptime", type=float, default=0.0, metavar="FRAC",
                    help="Fraction des rounds où la sournoise s'applique (0..1, ex. 0.3 cible contrôlée)")
    ap.add_argument("--weapon", help="Filtre candidats arme (nom/famille/clé, ex. \"laser\", \"sabre\", \"pistolet\")")
    ap.add_argument("--top", type=int, default=5, help="Nombre de candidats affichés par phase")
    ap.add_argument("--md", action="store_true", help="Afficher une synthèse markdown à la fin")
    ap.add_argument("--list-feats", action="store_true", help="Lister les dons reconnus et quitter")
    ap.add_argument("--list-weapons", action="store_true", help="Lister les armes et quitter")
    ap.add_argument("--reingest-upgrades", nargs="?", const=str(DEFAULT_UPGRADES_CSV), type=str,
                    help="Régénère upgrade_pools depuis le CSV WIP Améliorations (chemin optionnel)")
    ap.add_argument("--reingest-pouvoirs", nargs="?", const=str(ROOT / "Kotor 2 - rééquilibrage - WIP Spé Pouvoirs.csv"), type=str,
                    help="Resynchronise les armures max de force_buffs depuis le CSV WIP Spé Pouvoirs")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        selftest()
        return
    data = Data(json.loads(DATA_FILE.read_text(encoding="utf-8")))
    if args.list_feats:
        list_feats(data)
        return
    if args.list_weapons:
        for w in data.weapons:
            slots_str = f"slots={w.slots}" + (f"({','.join(w.allowed_slots)})" if w.allowed_slots else "")
            print(f"  {w.key:<18} {w.name:<32} famille={w.family or '—':<15} port={w.wield:<3} "
                  f"{'dist' if w.ranged else 'mêlée'} dég={w.dmg_avg:>4} plage={w.crit_range} x{w.crit_mult} "
                  f"{slots_str}{' équilibrée' if w.balanced else ''}")
        return
    if args.reingest_upgrades is not None:
        path = Path(args.reingest_upgrades)
        if not path.is_absolute():
            path = (ROOT / path.name) if not path.exists() else path
        n = reingest_upgrades(path)
        print(f"upgrade_pools régénérés ({n} objets) → {DATA_FILE}")
        return
    if args.reingest_pouvoirs is not None:
        path = Path(args.reingest_pouvoirs)
        if not path.is_absolute():
            path = (ROOT / path.name) if not path.exists() else path
        for line in reingest_pouvoirs(path):
            print(f"  • {line}")
        print(f"force_buffs resynchronisés → {DATA_FILE}")
        return

    feats = parse_feats(data, args.feats)
    run_report(data, feats, args)


if __name__ == "__main__":
    main()
