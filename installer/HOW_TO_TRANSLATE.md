# How to Add a New Language (Translation Guide for Modders)

This guide explains how to translate **KotOR 2: The Sith Lords — D20 Overhaul** into any new language (German, Spanish, Italian, Polish, Russian, etc.) and register it in the TSLPatcher installer (`INSTALL.exe`) so players can pick it from the dropdown menu.

---

## 1. How the Multi-Language Installer Works

The installer uses TSLPatcher's native **`namespaces.ini`** system inside `tslpatchdata/`.
All gameplay files (`.2da` tables, `.utc` enemies, `.ncs` scripts, `.utp` placeables) are **shared** across languages. Only text-bearing files are duplicated per language:

```text
tslpatchdata/
├── namespaces.ini          <-- Language selector menu shown when launching INSTALL.exe
├── changes_en.ini          <-- English install config (default)
├── changes_fr.ini          <-- French install config
├── info_en.rtf             <-- English welcome text in TSLPatcher UI
├── info_fr.rtf             <-- French welcome text in TSLPatcher UI
├── append_en.tlk           <-- 232 English strings (feats, Force powers, resistances)
├── append_fr.tlk           <-- 232 French strings
├── kreia_en.dlg            <-- Kreia personal crystal dialogue (EN)
├── kreia_fr.dlg            <-- Kreia personal crystal dialogue (FR)
├── ov_gam_conv_en.dlg      <-- Gamorrean portable workbench dialogue (EN)
├── ov_gam_conv_fr.dlg      <-- Gamorrean portable workbench dialogue (FR)
└── [shared game files: 10 base .2da, .uti, .utc, .ncs, .utp]
```

> **Note on `.uti` item descriptions:** KotOR 2 `.uti` files use BioWare's `LocalizedString` structure, which natively supports multiple languages inside the same file (`0 = English`, `1 = French`, `2 = German`, `3 = Italian`, `4 = Spanish`, `5 = Polish`). English and French are already embedded in every `.uti`.

---

## 2. Step-by-Step: Adding Your Language (Example: German `de`)

### Step 1 — Translate the 232 TLK strings (`append_de.tlk`)
1. Copy `tslpatchdata/append_en.tlk` → `tslpatchdata/append_de.tlk`.
2. Open `append_de.tlk` with a KotOR TLK editor:
   - **[Holocron Toolset](https://github.com/NickHugi/PyKotor)** *(recommended, supports UTF-8 / Windows-1252 / Windows-1250 / Windows-1251)*, or
   - **TalkEd** (classic KotOR TLK editor).
3. Set the TLK header language to your game language (`2 = German`, `3 = Italian`, `4 = Spanish`, `5 = Polish`, or `0 = English` if your game uses an English-language `dialog.tlk` with a fan translation).
4. Translate all **232 entries** (`0` to `231`). **Do not add or delete entries**, as `changes_de.ini` maps them by exact index (`StrRef0`..`StrRef231`).

### Step 2 — Translate the 2 custom dialogues (`kreia_de.dlg`, `ov_gam_conv_de.dlg`)
1. Copy:
   - `tslpatchdata/kreia_en.dlg` → `tslpatchdata/kreia_de.dlg`
   - `tslpatchdata/ov_gam_conv_en.dlg` → `tslpatchdata/ov_gam_conv_de.dlg`
2. Open each `.dlg` in **Holocron Toolset** or **DLGEditor**:
   - **`ov_gam_conv_de.dlg`**: translate the 3 Entries and 6 Replies (portable Gamorrean workbench menu).
   - **`kreia_de.dlg`**: translate only the custom entries/replies with `StrRef = -1` (the personal crystal stat-selection branch at the end of the dialogue). Leave all vanilla `StrRef` nodes untouched!
3. Tip: Write your translated text into **both** your target language slot AND the `English (Male)` slot of each custom `LocalizedString`, so it displays properly even on English-base fan-translated installs.

### Step 3 — Create `info_de.rtf` and `changes_de.ini`
1. Copy `tslpatchdata/info_en.rtf` → `tslpatchdata/info_de.rtf` and translate it in WordPad / LibreOffice Writer (save as `.rtf`).
2. Copy `tslpatchdata/changes_en.ini` → `tslpatchdata/changes_de.ini`.
3. Open `changes_de.ini` in a text editor (Notepad++ / VS Code) and replace **only these 5 occurrences**:
   - `!SourceFile=append_en.tlk` → `!SourceFile=append_de.tlk`
   - `kreia_en.dlg` → `kreia_de.dlg` *(in `[install_folder0]` AND the `[kreia_en.dlg]` section header)*
   - `ov_gam_conv_en.dlg` → `ov_gam_conv_de.dlg` *(in `[install_folder0]` AND the `[ov_gam_conv_en.dlg]` section header)*
   - *(Optional)* `WindowCaption=KotOR 2: The Sith Lords - D20 Overhaul Mod (Deutsch)`

### Step 4 — Register your language in `tslpatchdata/namespaces.ini`
Open `tslpatchdata/namespaces.ini` and add a new `Namespace` entry:

```ini
[Namespaces]
Namespace1=english
Namespace2=francais
Namespace3=deutsch

; ... existing [english] and [francais] sections ...

[deutsch]
IniName=changes_de.ini
InfoName=info_de.rtf
DataPath=
Name=Deutsch
Description=Installiert KotOR 2 D20 Overhaul auf Deutsch.
```

### Step 5 — (Optional) Translate `.uti` item descriptions
If you also want to translate the ~304 custom equipment/upgrade descriptions:
- Either add your language slot (`Language.GERMAN`, `SPANISH`, `ITALIAN`, `POLISH`) directly into the `.uti` files in `tslpatchdata/` using Holocron Toolset or a short `pykotor` script;
- Or translate the CSV files in `csv/en/` and submit a Pull Request so the build script generates your language automatically!

---

## 3. Testing Your Translation
1. Double-click `INSTALL.exe` — verify your language appears in the dropdown list.
2. Select your language, click **Install Mod**, and point to a test copy of KotOR 2 (or use `HoloPatcher`).
3. Check `installlog.txt` for `0 errors, 0 warnings`.
4. Launch the game and verify feat/power names & descriptions, the Gamorrean workbench dialogue, and Kreia's crystal dialogue.

---

## 4. Language ID Reference (Odyssey Engine / KotOR 2)

| Language | ID | Codepage |
| :--- | :---: | :--- |
| English | `0` | Windows-1252 |
| French | `1` | Windows-1252 |
| German | `2` | Windows-1252 |
| Italian | `3` | Windows-1252 |
| Spanish | `4` | Windows-1252 |
| Polish | `5` | Windows-1250 |
