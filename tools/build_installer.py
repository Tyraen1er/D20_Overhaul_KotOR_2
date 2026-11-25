#!/usr/bin/env python3
"""KotOR 2 Overhaul — Générateur de l'installateur TSLPatcher standard.

Crée une distribution complète de l'installateur dans `installer/` :
  - `INSTALL.exe` (exécutable TSLPatcher de stoffe / K2CP)
  - `Readme.rtf` (documentation utilisateur)
  - `tslpatchdata/info.rtf` (affiché dans l'interface de TSLPatcher)
  - `tslpatchdata/append.tlk` (nouvelles chaînes TLK extraites de dialog.tlk, langue FR)
  - `tslpatchdata/*.2da` (les 7 tables TSLRCM de base requises par TSLPatcher si absentes d'Override)
  - `tslpatchdata/changes.ini` (patch dynamique des 7 tables .2da + [GFFList] 2DAMEMORY + copie Override)
  - `tslpatchdata/*.uti`, `*.utc`, `*.ncs` (fichiers d'Override copiés pour le patcher)

Garanties de compatibilité TSLPatcher :
  - Nettoyage complet de `tslpatchdata/` à chaque build (aucun fichier fantôme).
  - Les 7 `.2da` de référence sont incluses dans `tslpatchdata/` (indispensable sur jeu propre).
  - Cellules effacées dans `ChangeRow` écrites en `****` (syntaxe officielle TSLPatcher / HoloPatcher).
  - `ExclusiveColumn=label` sur tous les ajouts de lignes 2DA (idempotent & compatible K2CP).
  - Résolution dynamique des `StrRef` via `[TLKList]` (`StrRef0..StrRefN`).
  - Résolution dynamique des `BaseItem` ajoutés (`>= 104`) via `2DAMEMORY` + `[GFFList]` (`Replace`).
"""

from __future__ import annotations

import shutil
from pathlib import Path

from pykotor.resource.formats.tlk import TLK, read_tlk, write_tlk
from pykotor.resource.formats.twoda import read_2da
from pykotor.resource.generics.uti import read_uti

ROOT = Path(__file__).resolve().parent.parent
BASE_TLK = ROOT / "mods" / "04-engine-tests" / "backup" / "dialog.tlk.bak"
if not BASE_TLK.exists():
    BASE_TLK = ROOT / "mods" / "00-test-feat" / "backup" / "dialog.tlk.bak"

REF_2DA = ROOT / "_reference" / "2da"
OUT_MOD = ROOT / "mods" / "overhaul"
OVR_DIR = OUT_MOD / "Override"
MOD_TLK = OUT_MOD / "dialog.tlk"

INSTALLER_DIR = ROOT / "installer"
TSL_DATA_DIR = INSTALLER_DIR / "tslpatchdata"
SOURCE_INSTALL_EXE = Path(r"C:\Users\emman\Desktop\kotor 2 updates\K2CP_v1.6.3\INSTALL.exe")
if not SOURCE_INSTALL_EXE.exists():
    SOURCE_INSTALL_EXE = ROOT / "_reference" / "autres_mods" / "Content Pack-57-1-67-1616632489" / "TSLPatcher.exe"

# Ordre important : feat.2da AVANT baseitems.2da afin que les 2DAMEMORY de dons soient résolus avant baseitems
TABLE_NAMES = [
    "feat.2da",
    "featgain.2da",
    "classpowergain.2da",
    "baseitems.2da",
    "spells.2da",
    "itemcreate.2da",
    "itemcreatemira.2da",
    "forceshields.2da",
    "autobalance.2da",
]


def rtf_escape(text: str) -> str:
    """Échappe le texte pour le format RTF (caractères accentués et spéciaux)."""
    out = []
    for char in text:
        code = ord(char)
        if char == "\\":
            out.append("\\\\")
        elif char == "{":
            out.append("\\{")
        elif char == "}":
            out.append("\\}")
        elif char == "\n":
            out.append("\\par\n")
        elif code > 127:
            out.append(f"\\u{code}?")
        else:
            out.append(char)
    return "".join(out)


def generate_info_rtf() -> str:
    """Génère le texte RTF affiché dans la fenêtre de TSLPatcher."""
    title = "Star Wars: Knights of the Old Republic II - The Sith Lords"
    subtitle = "D20 Overhaul Mod - Version 1.0"
    content = (
        "Bienvenue dans l'installateur du mod D20 Overhaul pour KotOR 2 !\n\n"
        "DESCRIPTION DU MOD :\n"
        "Ce mod transforme le système de combat et d'équipement de KotOR 2 pour rétablir "
        "une fidélité mathématique rigoureuse aux règles d20 Star Wars Roleplaying Game (WotC) :\n\n"
        "1. DONS & POUVOIRS :\n"
        "  - 73 nouveaux dons d20 (Familles d'armes Laser, Assaut, Lourdes, etc., Styles de combat, "
        "Dons de Caractéristiques rééquilibrés).\n"
        "  - 29 dons redondants ou déséquilibrés masqués proprement.\n"
        "  - Progression des dons et pouvoirs réétalonnée (budgets 22/18/15 dons sur 30 niveaux).\n\n"
        "2. ARMES & ARMURES :\n"
        "  - Refonte d20 des profils d'armes (dégâts, plages de coups critiques, maniement 1M/2M).\n"
        "  - Armures légères, moyennes et lourdes rééquilibrées avec bonus de DEX max et CA d20.\n"
        "  - Levée des restrictions de Force sous armure légère pour les pouvoirs adaptés.\n\n"
        "3. FABRICATION & ÉQUIPEMENT :\n"
        "  - Établi d'artisanat enrichi avec 18 armes de base, verrous de niveau et 60 améliorations d'armures\n"
        "    (30 sous-couches + 30 sur-couches exclusives Armure intermédiaire).\n"
        "  - Plafonds de stats lore pour tous les casques, gants, implants et ceintures.\n"
        "  - Cristal personnel de l'Exilé personnalisable auprès de Kreia (auto ou choix manuel).\n\n"
        "4. ÉQUILIBRAGE DU BESTIAIRE :\n"
        "  - Autobalance calibrée pour des affrontements plus tactiques et stimulants.\n\n"
        "COMPATIBILITÉ :\n"
        "  - Compatible avec TSLRCM (The Sith Lords Restored Content Mod) 1.8.6 / 2022.\n"
        "  - Compatible avec K2CP (KotOR 2 Community Patch) v1.6.3.\n"
        "  - Le patcher effectue une fusion dynamique et crée une sauvegarde automatique dans 'backup/'.\n\n"
        "INSTRUCTIONS :\n"
        "Cliquez sur le bouton 'Install Mod' ci-dessous, puis sélectionnez le répertoire racine "
        "de votre jeu KotOR 2 (le dossier contenant swkotor2.exe, PAS le sous-dossier Override).\n"
    )

    rtf = (
        "{\\rtf1\\ansi\\ansicpg1252\\deff0\\deflang1036\n"
        "{\\fonttbl{\\f0\\fnil\\fcharset0 Segoe UI;}{\\f1\\fnil\\fcharset0 Calibri;}}\n"
        "{\\colortbl ;\\red0\\green51\\blue102;\\red180\\green0\\blue0;\\red60\\green60\\blue60;}\n"
        "\\viewkind4\\uc1\\pard\\cf1\\b\\f0\\fs28 " + rtf_escape(title) + "\\par\n"
        "\\fs22\\cf2 " + rtf_escape(subtitle) + "\\b0\\par\\par\n"
        "\\cf3\\f1\\fs20 " + rtf_escape(content) + "\n"
        "}"
    )
    return rtf


def build_append_tlk_and_map() -> tuple[TLK, dict[int, str], int]:
    """Extrait les chaînes ajoutées au TLK et produit append.tlk + table de remplacement StrRef."""
    base_tlk = read_tlk(BASE_TLK)
    mod_tlk = read_tlk(MOD_TLK)
    base_len = len(base_tlk)
    mod_len = len(mod_tlk)

    append_tlk = TLK(base_tlk.language)
    strref_map: dict[int, str] = {}

    for i in range(base_len, mod_len):
        entry = mod_tlk.get(i)
        idx_append = len(append_tlk)
        voice = str(entry.voiceover) if entry.voiceover else ""
        append_tlk.add(entry.text, voice)
        strref_map[i] = f"StrRef{idx_append}"

    return append_tlk, strref_map, base_len


def build_installer() -> None:
    print(f"=== Création de l'installateur TSLPatcher dans {INSTALLER_DIR} ===")
    INSTALLER_DIR.mkdir(parents=True, exist_ok=True)

    # 0. Nettoyer tslpatchdata/ pour éviter tout fichier fantôme d'un ancien build
    if TSL_DATA_DIR.exists():
        shutil.rmtree(TSL_DATA_DIR)
    TSL_DATA_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Copier l'exécutable INSTALL.exe
    if SOURCE_INSTALL_EXE.exists():
        dst_exe = INSTALLER_DIR / "INSTALL.exe"
        shutil.copy2(SOURCE_INSTALL_EXE, dst_exe)
        print(f"[OK] INSTALL.exe copié depuis {SOURCE_INSTALL_EXE.name} ({dst_exe.stat().st_size} octets)")
    else:
        print(f"[WARN] INSTALL.exe non trouvé dans {SOURCE_INSTALL_EXE}")

    # 2. Générer info.rtf et Readme.rtf
    info_rtf_path = TSL_DATA_DIR / "info.rtf"
    readme_rtf_path = INSTALLER_DIR / "Readme.rtf"
    rtf_content = generate_info_rtf()
    info_rtf_path.write_text(rtf_content, encoding="ascii")
    readme_rtf_path.write_text(rtf_content, encoding="ascii")
    print("[OK] info.rtf & Readme.rtf générés")

    # 3. Extraire append.tlk et la table de correspondance StrRef
    append_tlk, strref_map, _ = build_append_tlk_and_map()
    append_tlk_path = TSL_DATA_DIR / "append.tlk"
    write_tlk(append_tlk, append_tlk_path)
    print(f"[OK] append.tlk généré ({len(append_tlk)} nouvelles chaînes, langue={append_tlk.language.name})")

    # 4. Copier les 7 tables .2da de référence (TSLRCM) dans tslpatchdata/
    # Indispensable pour TSLPatcher classique si le fichier n'est pas déjà dans Override/ chez le joueur.
    copied_2das = 0
    for tname in TABLE_NAMES:
        ref_file = REF_2DA / tname.replace(".2da", "_tslrcm.2da")
        if not ref_file.exists():
            raise FileNotFoundError(f"Table de référence manquante : {ref_file}")
        shutil.copy2(ref_file, TSL_DATA_DIR / tname)
        copied_2das += 1
    print(f"[OK] {copied_2das} tables .2da de base (TSLRCM) copiées dans tslpatchdata/")

    # 5. Identifier les .uti qui référencent un baseitem ajouté (>= len(baseitems_tslrcm))
    # Ils seront patchés via [GFFList] avec BaseItem=2DAMEMORYx pour une compatibilité totale multi-mods.
    ref_bi = read_2da(REF_2DA / "baseitems_tslrcm.2da")
    mod_bi = read_2da(OVR_DIR / "baseitems.2da")
    ref_bi_len = len(ref_bi)

    # Allouer les jetons 2DAMEMORY :
    #   - 1..N_bi pour les lignes ajoutées de baseitems.2da (index -> token_id)
    #   - N_bi+1 pour le don MOD_HEAVY_WEAPON_2 (utilisé par reqfeat0 des variantes 1M)
    next_mem_id = 1
    baseitem_row_to_mem: dict[int, int] = {}
    for bi_idx in range(ref_bi_len, len(mod_bi)):
        baseitem_row_to_mem[bi_idx] = next_mem_id
        next_mem_id += 1

    # Repérer l'index du don MOD_GAMORREAN_2 dans feat.2da pour le lier via 2DAMEMORY (reqfeat0 des variantes 1M)
    ref_feat = read_2da(REF_2DA / "feat_tslrcm.2da")
    mod_feat = read_2da(OVR_DIR / "feat.2da")
    feat_row_to_mem: dict[int, int] = {}
    gam2_feat_idx: int | None = None
    for f_idx in range(len(ref_feat), len(mod_feat)):
        if mod_feat.get_row(f_idx).get_string("label") in ("MOD_GAMORREAN_2", "MOD_GAMORRAN_2"):
            gam2_feat_idx = f_idx
            feat_row_to_mem[f_idx] = next_mem_id
            next_mem_id += 1
            break

    # 6. Copier les fichiers .uti, .utc, .ncs dans tslpatchdata/
    # Séparer les fichiers copiés directement ([install_folder0]) de ceux patchés par [GFFList]
    loose_files: list[str] = []
    gff_baseitem_patches: list[tuple[str, int]] = []  # (filename, mem_id)

    for f in sorted(OVR_DIR.iterdir()):
        if not f.is_file() or f.suffix.lower() not in {".uti", ".utc", ".ncs", ".dlg"}:
            continue
        shutil.copy2(f, TSL_DATA_DIR / f.name)
        if f.suffix.lower() == ".uti":
            uti = read_uti(f)
            if uti.base_item in baseitem_row_to_mem:
                gff_baseitem_patches.append((f.name, baseitem_row_to_mem[uti.base_item]))
                continue
        loose_files.append(f.name)

    print(
        f"[OK] {len(loose_files)} fichiers Override + {len(gff_baseitem_patches)} .uti patchés via [GFFList] "
        f"copiés dans tslpatchdata/"
    )

    # 7. Construire changes.ini
    ini_lines: list[str] = [
        "; //////////////////////////////////////////////////////////////////////////////",
        "; KOTOR 2: THE SITH LORDS - D20 OVERHAUL MOD",
        "; TSLPatcher configuration file",
        "; //////////////////////////////////////////////////////////////////////////////",
        "",
        "[Settings]",
        "FileExists=1",
        "ConfirmMessage=N/A",
        "LogLevel=3",
        "InstallerMode=1",
        "BackupFiles=1",
        "PlaintextLog=1",
        "LookupGameFolder=0",
        "LookupGameNumber=2",
        "SaveProcessedScripts=0",
        "WindowCaption=KotOR 2: The Sith Lords - D20 Overhaul Mod",
        "",
        "[TLKList]",
    ]

    for i in range(len(append_tlk)):
        ini_lines.append(f"StrRef{i}={i}")

    ini_lines.extend([
        "",
        "[InstallList]",
        "install_folder0=Override",
        "",
        "[2DAList]",
    ])

    for idx, tname in enumerate(TABLE_NAMES):
        ini_lines.append(f"Table{idx}={tname}")

    ini_lines.extend(["", "[GFFList]"])
    for idx, (fname, _) in enumerate(gff_baseitem_patches):
        ini_lines.append(f"Replace{idx}={fname}")

    ini_lines.extend([
        "",
        "[CompileList]",
        "",
        "[SSFList]",
        "",
        "; ===================================================================",
        "[install_folder0]",
    ])

    for idx, fname in enumerate(loose_files):
        ini_lines.append(f"File{idx}={fname}")

    # 8. Génération des sections [2da] avec ChangeRow et AddRow
    for tname in TABLE_NAMES:
        ref_file = REF_2DA / tname.replace(".2da", "_tslrcm.2da")
        ovr_file = OVR_DIR / tname
        if not ref_file.exists() or not ovr_file.exists():
            continue

        ref_2da = read_2da(ref_file)
        ovr_2da = read_2da(ovr_file)
        headers = ovr_2da.get_headers()
        has_label = "label" in headers

        change_rows: list[tuple[int, str, dict[str, str]]] = []
        add_rows: list[tuple[int, str, dict[str, str], int | None]] = []

        common_len = min(len(ref_2da), len(ovr_2da))
        for r_idx in range(common_len):
            r_row = ref_2da.get_row(r_idx)
            o_row = ovr_2da.get_row(r_idx)
            diff_cols: dict[str, str] = {}
            for h in headers:
                rv = r_row.get_string(h)
                ov = o_row.get_string(h)
                if rv != ov:
                    if ov == "":
                        # Syntaxe officielle TSLPatcher / HoloPatcher pour vider une cellule 2DA
                        diff_cols[h] = "****"
                    elif ov.isdigit() and int(ov) in strref_map:
                        diff_cols[h] = strref_map[int(ov)]
                    else:
                        diff_cols[h] = ov
            if diff_cols:
                lbl = o_row.get_string("label") if has_label else str(r_idx)
                safe_lbl = "".join(c if c.isalnum() else "_" for c in lbl.lower()).strip("_")
                sec_name = f"{tname.replace('.2da', '')}_mod_{safe_lbl}_{r_idx}"
                change_rows.append((r_idx, sec_name, diff_cols))

        for r_idx in range(len(ref_2da), len(ovr_2da)):
            o_row = ovr_2da.get_row(r_idx)
            row_cols: dict[str, str] = {}
            for h in headers:
                ov = o_row.get_string(h)
                if ov.isdigit() and int(ov) in strref_map:
                    row_cols[h] = strref_map[int(ov)]
                elif (
                    tname == "baseitems.2da"
                    and h == "reqfeat0"
                    and gam2_feat_idx is not None
                    and ov == str(gam2_feat_idx)
                ):
                    row_cols[h] = f"2DAMEMORY{feat_row_to_mem[gam2_feat_idx]}"
                else:
                    row_cols[h] = ov
            lbl = o_row.get_string("label") if has_label else str(r_idx)
            safe_lbl = "".join(c if c.isalnum() else "_" for c in lbl.lower()).strip("_")
            sec_name = f"{tname.replace('.2da', '')}_row_{safe_lbl}_{r_idx}"

            mem_id: int | None = None
            if tname == "baseitems.2da" and r_idx in baseitem_row_to_mem:
                mem_id = baseitem_row_to_mem[r_idx]
            elif tname == "feat.2da" and r_idx in feat_row_to_mem:
                mem_id = feat_row_to_mem[r_idx]

            add_rows.append((r_idx, sec_name, row_cols, mem_id))

        # Écriture de la section table
        ini_lines.extend(["", f"; {'=' * 67}", f"[{tname}]"])
        for c_i, (_, sec_name, _) in enumerate(change_rows):
            ini_lines.append(f"ChangeRow{c_i}={sec_name}")
        for a_i, (_, sec_name, _, _) in enumerate(add_rows):
            ini_lines.append(f"AddRow{a_i}={sec_name}")

        # Détails des ChangeRows
        for r_idx, sec_name, cols in change_rows:
            ini_lines.extend(["", f"[{sec_name}]", f"RowIndex={r_idx}"])
            for ch, cv in cols.items():
                ini_lines.append(f"{ch}={cv}")

        # Détails des AddRows (uniquement colonnes non-vides)
        for _, sec_name, cols, mem_id in add_rows:
            ini_lines.extend(["", f"[{sec_name}]"])
            if has_label and "label" in cols and cols["label"]:
                ini_lines.append("ExclusiveColumn=label")
            for ch, cv in cols.items():
                if cv != "":
                    ini_lines.append(f"{ch}={cv}")
            if mem_id is not None:
                ini_lines.append(f"2DAMEMORY{mem_id}=RowIndex")

    # 9. Sections [GFFList] pour les .uti à BaseItem dynamique
    if gff_baseitem_patches:
        ini_lines.extend(["", f"; {'=' * 67}", "; GFF Patches (BaseItem dynamique via 2DAMEMORY)"])
        for fname, mem_id in gff_baseitem_patches:
            ini_lines.extend([
                "",
                f"[{fname}]",
                f"BaseItem=2DAMEMORY{mem_id}",
            ])

    changes_ini_path = TSL_DATA_DIR / "changes.ini"
    with open(changes_ini_path, "w", encoding="windows-1252", errors="replace", newline="") as fh:
        fh.write("\r\n".join(ini_lines) + "\r\n")
    print(f"[OK] changes.ini généré ({changes_ini_path.stat().st_size} octets, {len(ini_lines)} lignes)")

    # 10. Validation automatique de cohérence
    _validate_installer(loose_files, [f for f, _ in gff_baseitem_patches], len(append_tlk))
    print(f"=== INSTALLATEUR PRÊT DANS {INSTALLER_DIR} ===")


def _validate_installer(
    expected_loose_files: list[str],
    expected_gff_files: list[str],
    expected_tlk_count: int,
) -> None:
    """Valide l'intégrité structurelle de l'arborescence générée pour TSLPatcher."""
    import configparser

    ini_path = TSL_DATA_DIR / "changes.ini"
    cfg = configparser.RawConfigParser(strict=False)
    cfg.read(ini_path, encoding="windows-1252")

    # TLKList
    tlk_list = cfg["TLKList"]
    assert len(tlk_list) == expected_tlk_count, f"TLKList ({len(tlk_list)}) != {expected_tlk_count}"

    # Fichiers d'Override
    inst_folder = cfg["install_folder0"]
    assert len(inst_folder) == len(expected_loose_files), (
        f"Fichiers listés ({len(inst_folder)}) != {len(expected_loose_files)}"
    )
    for _, fname in inst_folder.items():
        assert (TSL_DATA_DIR / fname).exists(), f"Fichier manquant dans tslpatchdata/ : {fname}"

    # Fichiers GFFList
    gff_list = cfg["GFFList"]
    assert len(gff_list) == len(expected_gff_files), (
        f"GFFList ({len(gff_list)}) != {len(expected_gff_files)}"
    )
    for _, fname in gff_list.items():
        assert (TSL_DATA_DIR / fname).exists(), f"Fichier GFF manquant dans tslpatchdata/ : {fname}"
        assert fname in cfg, f"Section GFF [{fname}] manquante dans changes.ini"

    # Tables 2DA (présence physique + intégrité sections)
    tables = [v for _, v in cfg["2DAList"].items()]
    total_changes = 0
    total_adds = 0
    for t in tables:
        assert (TSL_DATA_DIR / t).exists(), f"Table de base {t} manquante dans tslpatchdata/"
        assert t in cfg, f"Section de table [{t}] manquante dans changes.ini"
        sec = cfg[t]
        for k, target_sec in sec.items():
            assert target_sec in cfg, f"Sous-section [{target_sec}] manquante pour {t}"
            if k.startswith("changerow"):
                total_changes += 1
            elif k.startswith("addrow"):
                total_adds += 1

    print(
        f"[OK] Validation intégrité réussie : {len(tables)} tables "
        f"({total_changes} ChangeRows, {total_adds} AddRows), "
        f"{len(inst_folder)} fichiers Override + {len(gff_list)} patchs GFF, "
        f"{expected_tlk_count} chaînes TLK."
    )


if __name__ == "__main__":
    import argparse
    import subprocess
    import sys

    parser = argparse.ArgumentParser(description="Générateur de l'installateur TSLPatcher")
    parser.add_argument(
        "-f", "--full",
        action="store_true",
        help="Reconstruit d'abord tout le mod (build_overhaul, build_items, build_scripts, build_enemies) avant de packager l'installateur.",
    )
    args = parser.parse_args()

    if args.full:
        print("=== RECONSTRUCTION COMPLÈTE DU MOD (--full) ===")
        scripts = [
            ("Jalon 1 (2DA & TLK)", ROOT / "tools" / "build_overhaul.py"),
            ("Jalon 2 (Items UTI)", ROOT / "tools" / "build_items.py"),
            ("Jalon 3 (Scripts NCS)", ROOT / "tools" / "build_scripts.py"),
            ("Bestiaire (Créatures UTC)", ROOT / "tools" / "build_enemies.py"),
        ]
        for name, script_path in scripts:
            print(f"\n--- Exécution : {name} ---")
            res = subprocess.run([sys.executable, str(script_path)], check=False)
            if res.returncode != 0:
                print(f"[ERREUR] Échec de {script_path.name} (code {res.returncode})")
                sys.exit(res.returncode)
        print("\n=== RECONSTRUCTION DES FICHIERS SOURCE TERMINÉE ===\n")

    build_installer()
