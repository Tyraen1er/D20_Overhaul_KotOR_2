#!/usr/bin/env python3
"""KotOR 2 Overhaul — Générateur des guides joueur PDF (FR & EN).

Pipeline (historique validé, à l'identique depuis le 25/11/2026) :
  docs/README.md + docs/01..08_*.md  ──┐
                                        ├─> HTML (convertisseur MD maison)
  docs/en/README.md + docs/en/01..08 ──┘      + couverture / sommaire / CSS A4
                                        ──> Chrome headless --print-to-pdf
                                        ──> docs/KotOR2_D20_Overhaul_Guide_Joueur_FR.pdf
                                            docs/KotOR2_D20_Overhaul_Player_Guide_EN.pdf

Ce script est la version dépôt (chemins relatifs) de `build_pdfs.py` utilisé
par les sessions de doc : la sortie est identique au pipeline d'origine
(vérifié par hash le 26/11/2026). Modifier les .md puis relancer :

    python tools/build_pdf.py

Le HTML intermédiaire est écrit en temporaire système puis supprimé.
Chrome est requis (fallback Edge si absent).
"""

from __future__ import annotations

import html
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHROME_CANDIDATES = [
    Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
]

CSS = """
@page {
  size: A4;
  margin: 16mm 15mm 18mm 15mm;
  @bottom-center {
    content: counter(page) " / " counter(pages);
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 9pt;
    color: #64748b;
  }
}
@page :first {
  margin: 14mm 14mm 16mm 14mm;
}
* { box-sizing: border-box; }
body {
  font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, Arial, sans-serif;
  font-size: 9.4pt;
  line-height: 1.48;
  color: #1e293b;
  margin: 0;
}
.cover {
  background: linear-gradient(145deg, #0b1628 0%, #10243d 55%, #0d3b52 100%);
  color: #f8fafc;
  border-radius: 10px;
  padding: 58mm 18mm 46mm 18mm;
  text-align: center;
  min-height: 256mm;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  page-break-after: always;
}
.cover .badge {
  display: inline-block;
  border: 1px solid #38bdf8;
  color: #7dd3fc;
  padding: 5px 16px;
  border-radius: 999px;
  font-size: 8.5pt;
  letter-spacing: 2.2px;
  text-transform: uppercase;
  margin-bottom: 18px;
}
.cover h1 {
  font-size: 26pt;
  line-height: 1.22;
  margin: 0 0 14px 0;
  color: #ffffff;
  border: none;
  padding: 0;
}
.cover .subtitle {
  font-size: 11.5pt;
  color: #cbd5e1;
  max-width: 125mm;
  margin: 0 auto 28px auto;
}
.cover .toc-box {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(125, 211, 252, 0.25);
  border-radius: 8px;
  padding: 16px 22px;
  text-align: left;
  width: 135mm;
  font-size: 9.2pt;
  color: #e2e8f0;
}
.cover .toc-box .toc-title {
  font-weight: 700;
  color: #ffffff;
  margin-bottom: 8px;
}
.cover .toc-box ul {
  margin: 0;
  padding-left: 18px;
}
.cover .toc-box li {
  margin: 4px 0;
}
.chapter {
  page-break-before: always;
}
.chapter.first-chapter {
  page-break-before: auto;
}
h1 {
  font-size: 17pt;
  color: #0f172a;
  border-bottom: 2px solid #0284c7;
  padding-bottom: 5px;
  margin: 0 0 12px 0;
}
h2 {
  font-size: 12.2pt;
  color: #0369a1;
  margin: 16px 0 7px 0;
  page-break-after: avoid;
}
h3 {
  font-size: 10.3pt;
  color: #0f172a;
  margin: 12px 0 5px 0;
  page-break-after: avoid;
}
p { margin: 5px 0 7px 0; }
ul, ol { margin: 5px 0 8px 0; padding-left: 18px; }
li { margin: 3px 0; }
hr { border: none; border-top: 1px solid #cbd5e1; margin: 12px 0; }
code {
  font-family: Consolas, "Courier New", monospace;
  font-size: 8.4pt;
  background: #f1f5f9;
  color: #0f172a;
  padding: 1px 4px;
  border-radius: 3px;
}
blockquote {
  margin: 9px 0;
  padding: 8px 12px;
  background: #f0f9ff;
  border-left: 3.5px solid #0284c7;
  border-radius: 0 4px 4px 0;
  color: #1e293b;
}
blockquote p:first-child { margin-top: 0; }
blockquote p:last-child { margin-bottom: 0; }
a { color: #0284c7; text-decoration: underline; }
table {
  width: 100%;
  border-collapse: collapse;
  margin: 8px 0 12px 0;
  font-size: 8.5pt;
  line-height: 1.38;
}
thead { display: table-header-group; }
tr { page-break-inside: avoid; }
th {
  background: #0f1e36;
  color: #ffffff;
  font-weight: 600;
  text-align: left;
  padding: 6px 7px;
  border: 1px solid #1e293b;
}
td {
  padding: 5.5px 7px;
  border: 1px solid #cbd5e1;
  vertical-align: top;
}
tbody tr:nth-child(even) { background: #f8fafc; }
"""


def inline_md(text: str) -> str:
    # Preserve <br>
    text = text.replace("<br>", "\x00BR\x00").replace("<br/>", "\x00BR\x00").replace("<br />", "\x00BR\x00")
    # Protect inline code first
    codes = []
    def repl_code(m):
        codes.append(f"<code>{html.escape(m.group(1))}</code>")
        return f"\x00CODE{len(codes)-1}\x00"
    text = re.sub(r"`([^`]+)`", repl_code, text)

    # Escape HTML
    text = html.escape(text)

    # Links [label](url)
    text = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r'<a href="\2">\1</a>', text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)

    # Bold+italic ***...***, bold **...**, italic *...*
    text = re.sub(r"\*\*\*([^*]+)\*\*\*", r"<strong><em>\1</em></strong>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", text)

    for i, c in enumerate(codes):
        text = text.replace(f"\x00CODE{i}\x00", c)
    text = text.replace("\x00BR\x00", "<br>")
    return text


def md_to_html(md_text: str) -> str:
    lines = md_text.splitlines()
    out = []
    i = 0
    n = len(lines)

    def is_nav(line):
        st = line.strip()
        return st.startswith("[\u2190")

    while i < n:
        line = lines[i]
        st = line.strip()
        if not st or is_nav(line):
            i += 1
            continue
        if re.match(r"^---+$", st):
            out.append("<hr>")
            i += 1
            continue
        # Headings
        hm = re.match(r"^(#{1,3})\s+(.*)$", st)
        if hm:
            lvl = len(hm.group(1))
            out.append(f"<h{lvl}>{inline_md(hm.group(2))}</h{lvl}>")
            i += 1
            continue
        # Blockquote
        if st.startswith(">"):
            bq_lines = []
            while i < n and lines[i].strip().startswith(">"):
                bq_lines.append(re.sub(r"^>\s?", "", lines[i].strip()))
                i += 1
            out.append(f"<blockquote>{md_to_html(chr(10).join(bq_lines))}</blockquote>")
            continue
        # Table
        if st.startswith("|") and i + 1 < n and re.match(r"^\|[\s:|-]+\|$", lines[i + 1].strip()):
            headers = [c.strip() for c in st.strip("|").split("|")]
            aligns = [c.strip() for c in lines[i + 1].strip().strip("|").split("|")]
            i += 2
            body_rows = []
            while i < n and lines[i].strip().startswith("|"):
                body_rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            thtml = ["<table><thead><tr>"]
            for h in headers:
                thtml.append(f"<th>{inline_md(h)}</th>")
            thtml.append("</tr></thead><tbody>")
            for row in body_rows:
                thtml.append("<tr>")
                for ci, cell in enumerate(row):
                    al = aligns[ci] if ci < len(aligns) else ""
                    style = ' style="text-align:center"' if al.startswith(":") and al.endswith(":") else ""
                    thtml.append(f"<td{style}>{inline_md(cell)}</td>")
                thtml.append("</tr>")
            thtml.append("</tbody></table>")
            out.append("".join(thtml))
            continue
        # Unordered / Ordered lists (with 1 level nesting)
        if re.match(r"^[-*]\s+", st) or re.match(r"^\d+\.\s+", st):
            ordered = bool(re.match(r"^\d+\.\s+", st))
            tag = "ol" if ordered else "ul"
            lhtml = [f"<{tag}>"]
            while i < n:
                cur = lines[i]
                cur_st = cur.strip()
                if not cur_st:
                    break
                indent = len(cur) - len(cur.lstrip(" "))
                m_u = re.match(r"^[-*]\s+(.*)$", cur_st)
                m_o = re.match(r"^\d+\.\s+(.*)$", cur_st)
                if indent >= 2 and (m_u or m_o):
                    # nested list inside previous li
                    sub_items = []
                    while i < n and (len(lines[i]) - len(lines[i].lstrip(" "))) >= 2 and re.match(r"^[-*]\s+", lines[i].strip()):
                        sub_items.append(re.sub(r"^[-*]\s+", "", lines[i].strip()))
                        i += 1
                    if lhtml[-1].endswith("</li>"):
                        lhtml[-1] = lhtml[-1][:-5] + "<ul>" + "".join(f"<li>{inline_md(x)}</li>" for x in sub_items) + "</ul></li>"
                    continue
                if ordered and m_o:
                    lhtml.append(f"<li>{inline_md(m_o.group(1))}</li>")
                    i += 1
                elif not ordered and m_u:
                    lhtml.append(f"<li>{inline_md(m_u.group(1))}</li>")
                    i += 1
                else:
                    break
            lhtml.append(f"</{tag}>")
            out.append("".join(lhtml))
            continue
        # Paragraph
        para = [st]
        i += 1
        while i < n:
            nxt = lines[i].strip()
            if not nxt or nxt.startswith(("#", ">", "|", "---", "- ", "* ")) or re.match(r"^\d+\.\s+", nxt) or is_nav(lines[i]):
                break
            para.append(nxt)
            i += 1
        out.append(f"<p>{inline_md(' '.join(para))}</p>")
    return "\n".join(out)


def find_chrome() -> Path:
    for c in CHROME_CANDIDATES:
        if c.exists():
            return c
    raise FileNotFoundError("Chrome ou Edge introuvable pour le rendu PDF")


def build_pdf(lang: str, pdf_out: Path, cover_meta: dict, md_files: list[Path]) -> None:
    toc_items = "".join(f"<li>{html.escape(t)}</li>" for t in cover_meta["toc"])
    cover_html = f"""
    <div class="cover">
      <div class="badge">{html.escape(cover_meta["badge"])}</div>
      <h1>{cover_meta["title_html"]}</h1>
      <div class="subtitle">{html.escape(cover_meta["subtitle"])}</div>
      <div class="toc-box">
        <div class="toc-title">{html.escape(cover_meta["toc_title"])}</div>
        <ul>{toc_items}</ul>
      </div>
    </div>
    """
    sections = []
    for idx, mdp in enumerate(md_files):
        cls = "chapter first-chapter" if idx == 0 else "chapter"
        sections.append(f'<div class="{cls}">{md_to_html(mdp.read_text(encoding="utf-8"))}</div>')

    full_html = f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<title>{html.escape(cover_meta["doc_title"])}</title>
<style>{CSS}</style>
</head>
<body>
{cover_html}
{"".join(sections)}
</body>
</html>"""

    # HTML intermediaire en temporaire systeme, supprime apres le rendu
    html_path = Path(tempfile.gettempdir()) / f"kotor2_guide_{lang}.html"
    html_path.write_text(full_html, encoding="utf-8")

    chrome = find_chrome()
    cmd = [
        str(chrome),
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_out}",
        html_path.as_uri(),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    html_path.unlink(missing_ok=True)
    if res.returncode != 0:
        raise RuntimeError(f"PDF build failed ({lang}): {res.stderr}")
    print(f"OK: {pdf_out} ({pdf_out.stat().st_size:,} bytes)")


def main() -> None:
    build_pdf(
        "fr",
        ROOT / "docs" / "KotOR2_D20_Overhaul_Guide_Joueur_FR.pdf",
        {
            "doc_title": "KotOR 2 : D20 Overhaul \u2014 Guide du Joueur",
            "badge": "STAR WARS : KNIGHTS OF THE OLD REPUBLIC II",
            "title_html": "KotOR 2 : D20 Overhaul \u2014<br>Guide du Joueur",
            "subtitle": "Documentation compl\u00e8te en fran\u00e7ais des changements apport\u00e9s par le mod de r\u00e9\u00e9quilibrage",
            "toc_title": "Contenu de ce guide :",
            "toc": [
                "Introduction : Philosophie, Lexique & R\u00e8gles de base",
                "1. Classes & Progression",
                "2. Dons : Postures, Sp\u00e9cialisations, Caract\u00e9ristiques & \u00c9veil de Force",
                "3. Armures, Boucliers & D\u00e9fenses",
                "4. Pouvoirs de la Force",
                "5. Acc\u00e8s aux Dons par Classe & Compagnons",
                "6. Armes, Am\u00e9liorations, \u00c9tabli & Cristal de l'Exil\u00e9",
                "7. Combat & Guide tactique des Ennemis",
                "Annexe : Accessoires, Armures & Bures r\u00e9\u00e9quilibr\u00e9s",
            ],
        },
        [
            ROOT / "docs" / "README.md",
            ROOT / "docs" / "01_classes_et_progression.md",
            ROOT / "docs" / "02_dons_postures_et_specialisations.md",
            ROOT / "docs" / "03_armures_et_defenses.md",
            ROOT / "docs" / "04_pouvoirs_de_la_force.md",
            ROOT / "docs" / "05_acces_dons_et_compagnons.md",
            ROOT / "docs" / "06_armes_ameliorations_et_cristal.md",
            ROOT / "docs" / "07_combat_et_ennemis.md",
            ROOT / "docs" / "08_annexe_equipements_reequilibres.md",
        ],
    )

    build_pdf(
        "en",
        ROOT / "docs" / "KotOR2_D20_Overhaul_Player_Guide_EN.pdf",
        {
            "doc_title": "KotOR 2: D20 Overhaul \u2014 Player Guide",
            "badge": "STAR WARS: KNIGHTS OF THE OLD REPUBLIC II",
            "title_html": "KotOR 2: D20 Overhaul \u2014<br>Player Guide",
            "subtitle": "Complete English player documentation covering every gameplay change in the rebalancing mod",
            "toc_title": "Inside this guide:",
            "toc": [
                "Introduction: Design Philosophy, Glossary & Core Rules",
                "1. Classes & Progression",
                "2. Feats: Stances, Weapon Specializations, Attributes & Force Awakening",
                "3. Armor, Shields & Defenses",
                "4. Force Powers",
                "5. Feat Access by Class & Companions",
                "6. Weapons, Upgrades, Workbench & The Exile's Crystal",
                "7. Combat & Tactical Enemy Guide",
                "Appendix: Rebalanced Accessories, Armors & Robes",
            ],
        },
        [
            ROOT / "docs" / "en" / "README.md",
            ROOT / "docs" / "en" / "01_classes_and_progression.md",
            ROOT / "docs" / "en" / "02_feats_stances_and_specializations.md",
            ROOT / "docs" / "en" / "03_armor_and_defenses.md",
            ROOT / "docs" / "en" / "04_force_powers.md",
            ROOT / "docs" / "en" / "05_feat_access_and_companions.md",
            ROOT / "docs" / "en" / "06_weapons_workbench_and_crystal.md",
            ROOT / "docs" / "en" / "07_combat_and_enemies.md",
            ROOT / "docs" / "en" / "08_appendix_rebalanced_equipment.md",
        ],
    )


if __name__ == "__main__":
    main()
