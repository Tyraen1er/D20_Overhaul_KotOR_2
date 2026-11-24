#!/usr/bin/env python3
"""Génère des descriptions 100 % lore-friendly (en-tête `[Mod D20-Overhaul]`)
dans la colonne `Description (mod)` des 9 CSV du projet :
  - Améliorations.csv (240)
  - 6 CSV d'équipement (88)
  - WIP Feats.csv (83)
  - Spé Pouvoirs.csv (38)

Règle stricte : zéro jargon de patch/changelog (« Refondu en », « kill », « stun »,
« buffé », flèches `X → Y`) — uniquement du texte immersif Star Wars + effets clairs en VF.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

from pykotor.extract.installation import Installation
from pykotor.resource.formats.tlk import read_tlk
from pykotor.resource.generics.uti import read_uti
from pykotor.resource.type import ResourceType

ROOT = Path(__file__).resolve().parent.parent
GAME_PATH = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Knights of the Old Republic II")

HEADER_TAG = "[Mod D20-Overhaul]"

UPGRADES_CSV = ROOT / "Kotor 2 - rééquilibrage - Améliorations.csv"
FEATS_CSV = ROOT / "Kotor 2 - rééquilibrage - WIP Feats.csv"
POWERS_CSV = ROOT / "Kotor 2 - rééquilibrage - Spé Pouvoirs.csv"
GEAR_CSVS = [
    ROOT / "Kotor 2 - rééquilibrage - Casques.csv",
    ROOT / "Kotor 2 - rééquilibrage - Implants.csv",
    ROOT / "Kotor 2 - rééquilibrage - Gants.csv",
    ROOT / "Kotor 2 - rééquilibrage - Ceintures.csv",
    ROOT / "Kotor 2 - rééquilibrage - Brassards.csv",
    ROOT / "Kotor 2 - rééquilibrage - Armures items.csv",
]

STAT_LINE_PREFIXES = (
    "spécial", "special", "bonus", "malus", "dégâts", "degats", "attaque",
    "défense", "defense", "acéré", "acere", "restriction", "uniquement",
    "coups critiques", "résistance", "resistance", "immunité", "immunite",
    "régénération", "regeneration", "jets de sauvegarde", "parade",
    "en cas de coup", "don requis", "amélioration", "amelioration",
    "dex", "for", "con", "int", "sag", "cha", "classe d'armure",
)

FR_TERM_MAP = [
    (r"\(Slashing\)", "(tranchants)"),
    (r"\(Piercing\)", "(perforants)"),
    (r"\(Bludgeoning\)", "(contondants)"),
    (r"\(Energy\)", "(énergie)"),
    (r"\(Electrical\)", "(électriques)"),
    (r"\(Fire\)", "(feu)"),
    (r"\(Cold\)", "(froid)"),
    (r"\(Sonic\)", "(soniques)"),
    (r"\(Ion\)", "(ioniques)"),
    (r"\(Strength\)", "(Force)"),
    (r"\(Dexterity\)", "(Dextérité)"),
    (r"\(Constitution\)", "(Constitution)"),
    (r"\(Intelligence\)", "(Intelligence)"),
    (r"\(Wisdom\)", "(Sagesse)"),
    (r"\(Charisma\)", "(Charisme)"),
    (r"\bStun\b", "Étourdissement"),
    (r"\bstun\b", "étourdissement"),
    (r"\bkill\b", "élimination"),
    (r"\bAoE\b", "zone"),
    (r"\bbuffs\b", "améliorations"),
    (r"\bbuff\b", "amélioration"),
    (r"\bdébuffs\b", "affaiblissements"),
    (r"\bdébuff\b", "affaiblissement"),
    (r"\bproc\b", "déclenchement"),
    (r"\bProc\b", "Déclenchement"),
    (r"\bArmure moyenne\b", "Armure intermédiaire"),
    (r"\barmure moyenne\b", "armure intermédiaire"),
    (r"\bArmure interdite\b", "Bure uniquement"),
    (r"\bRobe uniquement\b", "Bure uniquement"),
]


def clean_fr(txt: str) -> str:
    out = txt.strip()
    for pat, repl in FR_TERM_MAP:
        out = re.sub(pat, repl, out)
    return out


def extract_lore_paragraph(vanilla_desc: str) -> str:
    if not vanilla_desc:
        return ""
    paras = [p.strip() for p in re.split(r"\r?\n\s*\r?\n", vanilla_desc.strip()) if p.strip()]
    lore_paras: list[str] = []
    for p in paras:
        first_line = p.splitlines()[0].strip().lower()
        if len(p) < 120 and any(first_line.startswith(pref) for pref in STAT_LINE_PREFIXES):
            continue
        lore_paras.append(re.sub(r"\s+", " ", p))
    return "\n\n".join(lore_paras)


# ============================================================================
# 1. Lore par famille de dons (WIP Feats.csv)
# ============================================================================

FEAT_LORE_BY_PREFIX = {
    "MOD_AMBIDEXTRY": (
        "Issu des disciplines de combat à deux lames et deux blasters de la Bordure Extérieure, "
        "cet entraînement coordonne main directrice et main faible pour transformer l'escrime double "
        "en véritable mur défensif."
    ),
    "MOD_HEAVY_WEAPON": (
        "Le maniement d'une arme à deux mains exige un ancrage parfait et un transfert complet du poids "
        "du corps dans chaque frappe ou chaque rafale, libérant une puissance cinétique supérieure."
    ),
    "MOD_DUEL": (
        "École d'escrime et de tir de précision privilégiant une arme unique. La main libre assure "
        "équilibre, mobilité et recherche constante des failles dans la garde adverse."
    ),
    "MOD_DOUBLE_WEAPON": (
        "Les armes doubles et blasters à haute cadence saturent l'adversaire par le volume de coups, "
        "au prix d'une garde exposée que seul un entraînement rigoureux permet de refermer."
    ),
    "MOD_SPEC_BLUNT": (
        "De la matraque de sécurité au combat à mains nues, la maîtrise des armes d'impact repose sur "
        "la force brute de percussion, capable de briser l'équilibre et de projeter l'adversaire au sol."
    ),
    "MOD_SPEC_PRIM": (
        "Forgées dans les alliages les plus denses de la galaxie, les lames traditionnelles compensent "
        "l'absence d'énergie par une masse redoutable qui fissure les plaques d'armure les plus épaisses."
    ),
    "MOD_SPEC_VIBRO": (
        "Les lames à résonance ultrasonique déchirent tendons et servomoteurs à chaque entaille, "
        "handicapant durablement la capacité de riposte de la cible."
    ),
    "MOD_SPEC_LASER": (
        "L'arme d'un Jedi ou d'un Sith n'est pas qu'une lame de plasma : son maniement érode la "
        "concentration et la volonté de ceux qui tentent de résister à son porteur."
    ),
    "MOD_SPEC_ASSAULT": (
        "Entraînement de combat rapproché des commandos républicains, conçu pour maintenir un feu "
        "soutenu au blaster sans jamais céder de terrain, même au contact."
    ),
    "MOD_SPEC_HEAVY": (
        "Spécialité des tireurs lourds et chasseurs wookies, utilisant des décharges à fort recul "
        "capables de percer les protections et de repousser physiquement l'ennemi."
    ),
    "MOD_SPEC_TAC": (
        "Tactique d'interdiction combinant décharges ioniques et ondes soniques pour neutraliser "
        "aussi bien les droïdes de combat que les systèmes nerveux organiques."
    ),
    "MOD_SPEC_ASSASSIN": (
        "Doctrine des tueurs à gages et tireurs d'élite utilisant des armes discrètes ou disruptrices "
        "pour exploiter la moindre ouverture sur une cible surprise ou neutralisée."
    ),
    "MOD_ARMOR_LIGHT": (
        "Les combattants en armure légère misent sur la lecture des lignes de tir et l'esquive mobile "
        "plutôt que sur l'épaisseur du blindage."
    ),
    "MOD_ARMOR_MED": (
        "Conçue pour les éclaireurs, sentinelles et agents d'infiltration, cette formation optimise "
        "les générateurs de boucliers et la discrétion sous armure intermédiaire."
    ),
    "MOD_ARMOR_HEAVY": (
        "Réservée aux soldats d'assaut et vétérans mandaloriens, cette discipline transforme une armure "
        "lourde en forteresse mobile capable d'encaisser les pires assauts."
    ),
    "MOD_META_EMPOWER": (
        "En puisant plus profondément dans les courants de la Force, le praticien amplifie l'intensité "
        "destructrice de ses pouvoirs offensifs au prix d'une dépense accrue."
    ),
    "MOD_META_PENETRATE": (
        "Une concentration implacable qui permet aux pouvoirs de la Force de fissurer les défenses "
        "mentales et physiques les plus résistantes."
    ),
    "MOD_META_EXTEND": (
        "Une maîtrise sereine des flux de la Force permettant de maintenir plus longtemps ses "
        "protections et améliorations sans effort supplémentaire."
    ),
    "MOD_GAMORREAN": (
        "Inspirée de la puissance brute des guerriers de Gamorr, cette voie fait de la Force physique "
        "le socle de toute prouesse martiale, jusqu'à manier d'une seule main des armes colossales."
    ),
    "MOD_ECHANI": (
        "Art martial ancestral des Echanis, pour qui le combat est un langage de grâce et d'anticipation "
        "où la Dextérité surpasse la force brute et libère le mouvement sous armure."
    ),
    "MOD_KRAITH": (
        "Discipline d'endurance nommée d'après le légendaire dragon krayt de Tatooine : le corps "
        "s'endurcit contre les coups et puise dans sa propre vitalité pour nourrir la Force."
    ),
    "MOD_GAND": (
        "Héritée des Trouveurs Gand, cette école associe sens tactique, démolition de précision et "
        "calcul balistique pour compenser l'instinct par l'Intelligence pure."
    ),
    "MOD_MATUKAI": (
        "Voie des adeptes Matukai, qui unissent discipline corporelle et Sagesse intérieure pour guider "
        "chaque frappe, esquiver par intuition et punir instantanément les attaques adverses."
    ),
    "MOD_NOMI": (
        "Inspirée de la légendaire Maître Jedi Nomi Sunrider, cette voie rayonne par la présence et le "
        "Charisme, inspirant les alliés et déviant les coups par la seule force de conviction."
    ),
    "MOD_UNBOUND_FORCE": (
        "Selon les enseignements de Kreia, s'abandonner à la Force revient à lui céder sa propre volonté. "
        "L'Exilé, qui a survécu à la coupure de Malachor V, sait mieux que quiconque que la véritable "
        "force naît de la discipline, de l'ingéniosité et de la maîtrise de soi plutôt que de la dépendance "
        "aux courants de la Force."
    ),
}

VANILLA_FEAT_LORE = {
    "EVASION": (
        "Grâce à des réflexes aiguisés par l'entraînement ou la Force, ce don permet d'anticiper les "
        "explosions et décharges de zone pour s'en extraire au dernier instant."
    ),
    "XXXFORCE_CAMOFLAGE": (
        "Kreia a enseigné que ce qui est né du vide de Malachor V peut apprendre à s'effacer du regard "
        "de la Force elle-même. Ce don permet à l'Exilé de se dissimuler sans générateur de camouflage "
        "et de se déplacer en silence dans les ombres."
    ),
    "XXXIMPROVED_FORCE_CAMOUFLAGE": (
        "En approfondissant les leçons de Kreia sur le silence et la dissimulation dans la Force, l'Exilé "
        "fait de sa propre absence un piège mortel. Ses embuscades frappent avec une violence soudaine "
        "qui peut étourdir sur place une cible prise au dépourvu."
    ),
    "XXXMASTER_FORCE_CAMOUFLAGE": (
        "À l'apogée de cet enseignement, l'écho laissé par l'Exilé dans la Force se referme sur chaque "
        "victime abattue. Chaque élimination nourrit instantanément son élan meurtrier, garantissant un "
        "coup critique sur la frappe suivante tout en le rendant presque insaisissable."
    ),
    "XXXX_CRUSH_OPPOSITION_I": (
        "Comme Kreia l'a révélé, l'Exilé porte en lui une blessure béante dans la Force. En laissant "
        "cet écho se propager autour de lui, il ébranle la résolution de ses adversaires et affaiblit "
        "leur précision, leur garde et leurs défenses."
    ),
    "XXXX_CRUSH_OPPOSITION_II": (
        "En amplifiant délibérément l'écho de Malachor V selon les préceptes de Kreia, l'Exilé fissure "
        "plus profondément la Force autour de lui, sapant gravement les attaques, la défense et les "
        "sauvegardes de tous les ennemis proches."
    ),
    "XXXX_CRUSH_OPPOSITION_III": (
        "L'Exilé ouvre pleinement la blessure qu'il porte dans la Force. L'onde silencieuse qui en "
        "émane écrase la combativité de ses adversaires à portée, réduisant lourdement leur précision, "
        "leur garde et leur résistance."
    ),
    "XXXX_INSPIRE_FOLLOWERS_I": (
        "Kreia fut la première à remarquer la faculté singulière de l'Exilé à tisser inconsciemment des "
        "Liens de Force avec ceux qui le suivent. En canalisant cet écho, il partage ses propres "
        "protections et améliorations avec l'ensemble de ses compagnons."
    ),
    "XXXX_INSPIRE_FOLLOWERS_II": (
        "Les Liens de Force tissés par l'Exilé gagnent en profondeur et en clarté. L'écho de ses "
        "pouvoirs personnels résonne plus longtemps à travers tout le groupe au cœur du combat."
    ),
    "XXXX_INSPIRE_FOLLOWERS_III": (
        "En pleine maîtrise des Liens de Force évoqués par Kreia, l'Exilé projette durablement ses "
        "améliorations personnelles sur ses compagnons tout en élevant leur défense et leur résistance."
    ),
}


def clean_changelog_prefix(txt: str) -> str:
    """Supprime les préfixes de type changelog ('Refondu en ... :', 'Renommé ... :')."""
    s = re.sub(r"^(?:Refondu en|Renommé)\s*«[^»]+»[^:]*:\s*", "", txt.strip())
    s = re.sub(r"\(base moddée[^)]*\)", "", s)
    s = re.sub(r"\(ouvert à tous\)", "", s)
    s = re.sub(r"Remplace le malus de 5 de CA d\"utilisation des armes doubles par\s*:\s*", "", s)
    return clean_fr(re.sub(r"\s+", " ", s)).strip()


def format_upgrade_desc(rr: str, emplacement: str, mod_txt: str, lore: str) -> str:
    if rr.startswith("u_a_over_"):
        slot_line = "Amélioration d'armure — Sur-couche (armure intermédiaire uniquement)"
    elif rr.startswith("u_a_unde_"):
        num = int(rr.split("_")[-1]) if rr.split("_")[-1].isdigit() else 0
        if num >= 19:
            slot_line = "Amélioration d'armure — Sous-couche (armure intermédiaire uniquement)"
        elif num in {4, 5, 10, 11, 16, 17}:
            slot_line = "Amélioration d'armure — Sous-couche (armure lourde ou intermédiaire)"
        else:
            slot_line = "Amélioration d'armure — Sous-couche (armure légère, intermédiaire ou lourde)"
    elif rr.startswith("u_l_crys_"):
        slot_line = "Cristal d'amélioration — Sabre laser"
    elif rr.startswith("u_l_"):
        slot_line = f"Amélioration de sabre laser — {emplacement}"
    elif rr.startswith("u_m_"):
        slot_line = f"Amélioration d'arme de mêlée — {emplacement}"
    elif rr.startswith("u_r_"):
        slot_line = f"Amélioration d'arme à distance — {emplacement}"
    else:
        slot_line = f"Amélioration — {emplacement}"

    effs = [f"• {clean_fr(part)}" for part in mod_txt.split(",") if part.strip()]
    parts = [HEADER_TAG, slot_line]
    if lore:
        parts.append(lore)
    if effs:
        parts.append("Effets :\n" + "\n".join(effs))
    return "\n\n".join(parts)


def format_gear_desc(mod_txt: str, lore: str) -> str:
    """Ne conserve que la valeur finale (après `→`) pour éviter tout style changelog."""
    effs: list[str] = []
    for seg in mod_txt.split(";"):
        seg = seg.strip()
        if not seg:
            continue
        if "→" in seg:
            seg = seg.split("→", 1)[1].strip()
        seg = re.sub(r"^Ajout\s*:\s*", "", seg, flags=re.IGNORECASE)
        effs.append(f"• {clean_fr(seg)}")
    parts = [HEADER_TAG]
    if lore:
        parts.append(lore)
    if effs:
        parts.append("Propriétés notables :\n" + "\n".join(effs))
    return "\n\n".join(parts)


def populate_csv(csv_path: Path, inst: Installation, tlk, is_upgrades: bool) -> int:
    with open(csv_path, encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.reader(fh))
    if not rows:
        return 0
    header = rows[0]
    if "Description (mod)" not in header:
        header.append("Description (mod)")
    desc_idx = header.index("Description (mod)")
    h = {c.strip(): i for i, c in enumerate(header)}
    mod_idx = h["Changement (mod)"]
    emp_idx = h.get("Emplacement")

    updated = 0
    for r in rows[1:]:
        while len(r) <= desc_idx:
            r.append("")
        rr = r[0].strip().lower()
        mod_txt = r[mod_idx].strip() if len(r) > mod_idx else ""
        if not rr or not mod_txt or mod_txt.lower() in ("inchangé", "inchange", "-"):
            continue
        if is_upgrades and not rr.startswith("u_"):
            continue

        lore = ""
        res = inst.resource(rr, ResourceType.UTI)
        if res:
            uti = read_uti(res.data)
            if uti.description.stringref >= 0:
                entry = tlk.get(uti.description.stringref)
                if entry:
                    lore = extract_lore_paragraph(entry.text)
        elif is_upgrades and rr.startswith(("u_a_over_", "u_a_unde_")):
            lore = (
                "Alliage composite de haute technicité, spécialement conçu pour exploiter la "
                "modularité des armures intermédiaires. Nécessite un établi équipé des outils adéquats."
            )

        if is_upgrades:
            emp = r[emp_idx].strip() if emp_idx is not None and len(r) > emp_idx else ""
            r[desc_idx] = format_upgrade_desc(rr, emp, mod_txt, lore)
        else:
            r[desc_idx] = format_gear_desc(mod_txt, lore)
        updated += 1

    with open(csv_path, "w", encoding="utf-8-sig", newline="") as fh:
        csv.writer(fh).writerows(rows)
    return updated


def populate_feats_csv() -> int:
    with open(FEATS_CSV, encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.reader(fh))
    if not rows:
        return 0
    header = rows[0]
    if "Description (mod)" not in header:
        header.append("Description (mod)")
    desc_idx = header.index("Description (mod)")
    updated = 0

    for r in rows[1:]:
        while len(r) <= desc_idx:
            r.append("")
        if not r or not r[0].strip():
            continue
        id_col = r[0].strip()
        label = r[1].strip() if len(r) > 1 else ""
        mod_txt = r[6].strip() if len(r) > 6 else ""

        if id_col.startswith("nouveau"):
            lore = ""
            for pref, text in FEAT_LORE_BY_PREFIX.items():
                if label.startswith(pref):
                    lore = text
                    break
            eff_body = clean_changelog_prefix(mod_txt or (r[5].strip() if len(r) > 5 else ""))
            parts = [HEADER_TAG, f"Effets : {eff_body}"]
            if lore:
                parts.append(lore)
            r[desc_idx] = "\n\n".join(parts)
            updated += 1
        elif id_col.isdigit() and mod_txt and "supprim" not in mod_txt.lower() and mod_txt.lower() not in ("inchangé", "inchange", "-"):
            lore = VANILLA_FEAT_LORE.get(label, "")
            eff_body = clean_changelog_prefix(mod_txt)
            parts = [HEADER_TAG, f"Effets : {eff_body}"]
            if lore:
                parts.append(lore)
            r[desc_idx] = "\n\n".join(parts)
            updated += 1

    with open(FEATS_CSV, "w", encoding="utf-8-sig", newline="") as fh:
        csv.writer(fh).writerows(rows)
    return updated


POWER_LORE_HINTS = [
    ("force aura", "Le Jedi entoure son corps d'un champ protecteur de Force qui dévie les attaques et renforce sa résistance."),
    ("force barrier", "Une barrière cinétique dense absorbe une partie de l'énergie des chocs et des lames dirigés contre le lanceur."),
    ("force valor", "La Force vivante irrigue le lanceur et ses compagnons, élevant simultanément leurs capacités physiques et mentales."),
    ("cure / heal", "En canalisant le côté Lumineux, le Jedi accélère la régénération cellulaire et referme les blessures du groupe."),
    ("revitalize", "Une vague d'énergie lumineuse rappelle les compagnons tombés au combat et leur rend une part de leur vitalité."),
    ("stun / stasis", "Le Jedi fige le système nerveux de ses adversaires dans un champ de stase qui entrave tout mouvement."),
    ("stun droid", "Une impulsion de Force perturbe les circuits internes et surchage les processeurs des unités droïdes."),
    ("battle precognition", "Une perception intuitive des intentions adverses guide la garde du Jedi au cœur de la mêlée."),
    ("force enlightenment", "Inspiré par les leçons de Kreia sur l'équilibre intérieur et la maîtrise de sa propre nature dans la Force, ce pouvoir éveille instantanément les protections lumineuses les plus élevées de l'Exilé."),
    ("inspire followers", "Kreia fut la première à déceler la faculté singulière de l'Exilé à forger des Liens de Force profonds. Ce pouvoir fait résonner ces liens pour projeter ses propres protections sur l'ensemble du groupe."),
    ("affect mind", "Une subtile inflexion de la Force oriente la pensée des esprits faibles lors des échanges."),
    ("battle meditation", "Art rare de coordination mentale qui galvanise la précision et le moral des alliés tout en sapant ceux de l'ennemi."),
    ("burst of speed", "La Force accélère les réflexes et la vélocité du Jedi bien au-delà des limites biologiques normales."),
    ("energy resistance", "Un voile énergétique dissipe la chaleur, le froid, les décharges de blaster et les ondes soniques."),
    ("force body", "Le pratiquant puise directement dans sa propre vitalité pour alimenter ses pouvoirs et accroître leur emprise."),
    ("force deflection", "La Force permet de dévier les tirs de blaster à mains nues et d'éloigner les projectiles ennemis."),
    ("force push", "Une onde télékinétique projette les adversaires ou les soulève dans un tourbillon incontrôlable."),
    ("force resistance", "Un rempart mental et spirituel dresse une barrière contre les pouvoirs hostiles de la Force."),
    ("force suppression", "Un souffle de rupture dissipe les protections et altérations de Force actives sur la cible."),
    ("mind trick", "Un brouillard mental trouble la perception de l'adversaire jusqu'à le retourner contre ses propres alliés."),
    ("throw lightsaber", "Guidé par la Force, le sabre laser décrit un arc mortel à distance avant de revenir dans la main de son porteur."),
    ("beast trick", "Le Jedi apaise ou détourne l'instinct primaire des créatures sauvages."),
    ("breath control", "Une maîtrise métabolique complète neutralise les toxines et gaz nocifs dans l'organisme."),
    ("force camouflage", "Né des enseignements de Kreia sur le vide que l'Exilé porte depuis Malachor V, ce pouvoir efface sa signature dans la Force et lui permet de frapper depuis les ombres sans générateur."),
    ("force sight", "La vision à travers la Force révèle l'alignement et la présence des êtres vivants au-delà des obstacles."),
    ("precognition", "Des éclairs de prescience avertissent le porteur des dangers imminents."),
    ("drain force", "Le côté Obscur arrache l'énergie spirituelle des adversaires pour réalimenter la réserve du lanceur."),
    ("drain life", "Un siphon sombre aspire l'essence vitale des êtres vivants pour guérir les blessures du lanceur."),
    ("fear / horror", "Une terreur glaciale s'infiltre dans l'esprit des adversaires, rongeant leur psyché et troublant leurs attaques."),
    ("force scream", "Un hurlement chargé d'énergie sombre ébranle le corps et les défenses de tous les ennemis proches."),
    ("shock / force", "Des arcs d'éclairs du côté Obscur foudroient les ennemis avec une violence électrique croissante."),
    ("slow / affliction", "Une corruption sournoise affaiblit progressivement le corps de la cible et se propage aux ennemis proches."),
    ("wound / choke", "La télékinésie sombre comprime les organes internes de la cible, lui infligeant une douleur paralysante."),
    ("crush opposition", "Comme Kreia l'a enseigné, la blessure que l'Exilé porte dans la Force peut être projetée vers l'extérieur. Cet écho silencieux sape la précision, la garde et les défenses de tous les ennemis proches."),
    ("force crush", "L'Exilé concentre tout le poids de la blessure de Malachor V sur un unique adversaire, le broyant par télékinésie et le paralysant sous une pression implacable."),
    ("fury / improved", "Guidé par les leçons de Kreia sur la douleur comme source de lucidité, l'Exilé ouvre son propre stigmate dans la Force, décuplant sa puissance martiale au prix de sa propre vitalité."),
    ("force scar", "Héritage direct de la blessure laissée par Malachor V et des enseignements de Kreia, cette cicatrice dans la Force embrase les réflexes et la force de l'Exilé tout en consumant lentement son endurance."),
    ("unbound from", "Écho le plus pur de la philosophie de Kreia : ayant survécu à l'exil hors de la Force, l'Exilé choisit de s'en affranchir et transforme son autonomie et ses compétences en véritable rempart."),
]


def populate_powers_csv() -> int:
    with open(POWERS_CSV, encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.reader(fh))
    if not rows:
        return 0
    header = rows[0]
    if "Description (mod)" not in header:
        header.append("Description (mod)")
    desc_idx = header.index("Description (mod)")
    updated = 0

    for r in rows[1:]:
        while len(r) <= desc_idx:
            r.append("")
        if len(r) < 5 or not r[0].strip():
            continue
        name_l = r[0].lower()
        arm = clean_fr(r[1].strip())
        pf = r[2].strip()
        eff_van = r[3].strip()
        chg = r[4].strip()
        if not arm and not pf and not chg:
            continue

        lore = next((txt for k, txt in POWER_LORE_HINTS if k in name_l), "")
        body_raw = chg if chg else eff_van
        body_clean = clean_changelog_prefix(body_raw)
        body_clean = re.sub(r"\(finit? le DD 100[^)]*\)", "", body_clean, flags=re.IGNORECASE)
        body_clean = re.sub(r"Suppression de la perte de 50 % des PV max\s*\.?\s*", "", body_clean, flags=re.IGNORECASE)
        body_clean = body_clean.strip()

        hdr_lines = [HEADER_TAG]
        if arm:
            hdr_lines.append(f"Armure maximale : {arm}")
        if pf:
            hdr_lines.append(f"Coût en Points de Force : {pf}")

        parts = ["\n".join(hdr_lines)]
        if lore:
            parts.append(lore)
        if body_clean:
            parts.append(body_clean)
        r[desc_idx] = "\n\n".join(parts)
        updated += 1

    with open(POWERS_CSV, "w", encoding="utf-8-sig", newline="") as fh:
        csv.writer(fh).writerows(rows)
    return updated


def main() -> None:
    inst = Installation(GAME_PATH)
    tlk = read_tlk(GAME_PATH / "dialog.tlk")
    n_up = populate_csv(UPGRADES_CSV, inst, tlk, is_upgrades=True)
    print(f"[OK] {UPGRADES_CSV.name} : {n_up} descriptions lore-friendly")
    total_gear = 0
    for path in GEAR_CSVS:
        n = populate_csv(path, inst, tlk, is_upgrades=False)
        print(f"[OK] {path.name} : {n} descriptions lore-friendly")
        total_gear += n
    n_feats = populate_feats_csv()
    print(f"[OK] {FEATS_CSV.name} : {n_feats} descriptions lore-friendly")
    n_pow = populate_powers_csv()
    print(f"[OK] {POWERS_CSV.name} : {n_pow} descriptions lore-friendly")
    print(f"=== TOTAL : {n_up + total_gear + n_feats + n_pow} descriptions lore-friendly ([Mod D20-Overhaul]) ===")


if __name__ == "__main__":
    main()
