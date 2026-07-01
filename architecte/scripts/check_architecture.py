#!/usr/bin/env python
"""Garde-fou deterministe (sans IA) de la phase architecture.

Lit le manifeste partage d'un projet (.factory/manifest.json par defaut) et
echoue si le contrat technique est incomplet :
  - bloc `architecture` absent ;
  - profil d'equipe non renseigne (seule reponse demandee a l'utilisateur) ;
  - aucun composant ;
  - stack sans langage ;
  - un langage de la stack sans fichier de conventions installe ;
  - aucune feature sequencee (numerotation non figee) ;
  - walking skeleton non designe ;
  - section `Decisions a impact design` non produite (handoff designer) ;
  - un marqueur residuel ([A VALIDER]/[A CHIFFRER]/[A DEFINIR]) subsiste dans un
    fichier de `architecte-out/` (tout point doit etre tranche en session) ;
  - une techno de `tech-stack.md` n'a pas de version exacte (vide / 'latest' / ...) ;
  - un fichier de `architecte-out/` n'a pas de front-matter version(entier)/date(ISO).

Exit 0 si tout est present et coherent, sinon 1. Reutilisable a la main, en hook
git, ou en CI (socle deterministe de la factory).

Usage:
    python check_architecture.py [chemin/vers/manifest.json]
"""
import glob
import json
import os
import re
import sys

MARKER_RE = re.compile(r"\[\s*(?:À|A)\s+(?:VALIDER|CHIFFRER|D[ÉE]FINIR)\s*\]", re.IGNORECASE)

# Valeurs de version interdites : on exige une version exacte et epinglee.
FORBIDDEN_VERSION_RE = re.compile(
    r"^(?:latest|stable|current|newest|rolling|edge|nightly|tbd|n/?a|"
    r"derni[eè]re(?:\s+version)?|\.\.\.|…|—|-)$",
    re.IGNORECASE,
)
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def residual_markers(manifest_path):
    """Renvoie la liste (fichier, marqueur) des marqueurs residuels dans architecte-out/."""
    root = os.path.dirname(os.path.dirname(os.path.abspath(manifest_path)))
    out_dir = os.path.join(root, "architecte-out")
    hits = []
    for md in glob.glob(os.path.join(out_dir, "**", "*.md"), recursive=True):
        try:
            text = open(md, encoding="utf-8").read()
        except OSError:
            continue
        for m in set(MARKER_RE.findall(text)):
            hits.append((os.path.relpath(md, root), m))
    return hits


def parse_frontmatter(text):
    """Renvoie le dict du front-matter YAML minimal en tete de fichier, ou None."""
    if not text.startswith("---"):
        return None
    lines = text.splitlines()
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return None
    fm = {}
    for line in lines[1:end]:
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        if ":" in s:
            key, _, val = s.partition(":")
            fm[key.strip()] = val.strip()
    return fm


def frontmatter_issues(manifest_path):
    """Chaque .md de architecte-out/ doit porter un front-matter version(entier)/date(ISO)."""
    root = os.path.dirname(os.path.dirname(os.path.abspath(manifest_path)))
    out_dir = os.path.join(root, "architecte-out")
    issues = []
    for md in glob.glob(os.path.join(out_dir, "**", "*.md"), recursive=True):
        try:
            text = open(md, encoding="utf-8").read()
        except OSError:
            continue
        rel = os.path.relpath(md, root)
        fm = parse_frontmatter(text)
        if fm is None:
            issues.append(f"{rel}: front-matter version/date absent")
            continue
        ver = str(fm.get("version", "")).strip()
        if not ver.isdigit() or int(ver) < 1:
            issues.append(f"{rel}: 'version:' manquant ou non entier positif")
        date = str(fm.get("date", "")).strip()
        if not DATE_RE.match(date):
            issues.append(f"{rel}: 'date:' manquante ou non ISO (AAAA-MM-JJ)")
    return issues


def tech_stack_versions(manifest_path):
    """Chaque techno d'une table a colonne 'Version' de tech-stack.md porte une version exacte."""
    root = os.path.dirname(os.path.dirname(os.path.abspath(manifest_path)))
    ts = os.path.join(root, "architecte-out", "tech-stack.md")
    if not os.path.isfile(ts):
        return []
    try:
        text = open(ts, encoding="utf-8").read()
    except OSError:
        return []
    name_prefs = ("outil", "bibliotheque / framework", "bibliothèque / framework",
                  "langage", "stockage")
    issues = []
    header = None
    ver_idx = None
    name_idx = 0
    for raw in text.splitlines():
        line = raw.strip()
        if not line.startswith("|"):
            header, ver_idx, name_idx = None, None, 0
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if cells and all(re.fullmatch(r":?-{2,}:?", c or "-") for c in cells):
            continue
        if header is None:
            header = [c.lower() for c in cells]
            ver_idx = next((i for i, c in enumerate(header) if c == "version"), None)
            name_idx = 0
            for pref in name_prefs:
                if pref in header:
                    name_idx = header.index(pref)
                    break
            continue
        if ver_idx is None or ver_idx >= len(cells):
            continue
        if not any(c and c not in ("[...]", "[…]") for c in cells):
            continue  # ligne de gabarit non remplie
        row_text = " ".join(cells).lower()
        if "aucun" in row_text or "non applicable" in row_text or "sans objet" in row_text:
            continue  # outil explicitement non utilise : pas de version requise
        val = cells[ver_idx]
        name = cells[name_idx] if name_idx < len(cells) and cells[name_idx] else (cells[0] if cells else "?")
        if val in ("", "[...]", "[…]") or FORBIDDEN_VERSION_RE.match(val):
            issues.append(f"tech-stack.md: techno '{name}' sans version exacte (valeur: '{val or 'vide'}')")
    return issues


def main(argv):
    path = argv[1] if len(argv) > 1 else ".factory/manifest.json"
    try:
        with open(path, encoding="utf-8") as f:
            manifest = json.load(f)
    except FileNotFoundError:
        print(f"ERREUR: manifeste introuvable: {path}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"ERREUR: manifeste JSON invalide: {exc}", file=sys.stderr)
        return 1

    arch = manifest.get("architecture")
    if not isinstance(arch, dict):
        print("ERREUR: bloc `architecture` absent (lancer architecte-init).", file=sys.stderr)
        return 1

    problems = []

    if not arch.get("team_profile"):
        problems.append("profil d'equipe non renseigne (question #13 a poser)")

    if not arch.get("components"):
        problems.append("aucun composant defini")

    stack = arch.get("stack") or {}
    languages = stack.get("languages") or []
    if not languages:
        problems.append("stack sans langage")

    installed = arch.get("conventions_installed") or []
    installed_norm = {str(x).lower() for x in installed}
    for lang in languages:
        if str(lang).lower() not in installed_norm:
            problems.append(f"langage '{lang}' sans fichier de conventions installe")

    seq = arch.get("feature_sequence") or []
    if not seq:
        problems.append("liste de features numerotee/sequencee non figee")
    else:
        for it in seq:
            ucs = it.get("ucs") if isinstance(it, dict) else None
            ok = isinstance(it, dict) and it.get("id") and ((isinstance(ucs, list) and ucs) or it.get("uc"))
            if not ok:
                problems.append("feature_sequence : entree sans {id, ucs} (registre canonique incomplet)")
                break

    if not arch.get("walking_skeleton"):
        problems.append("walking skeleton non designe")

    if not arch.get("design_impact"):
        problems.append("section `Decisions a impact design` non produite (handoff designer)")

    for rel, marker in residual_markers(path):
        problems.append(f"marqueur residuel {marker} dans {rel} (a trancher en session)")

    for issue in tech_stack_versions(path):
        problems.append(f"version imprecise - {issue}")

    for issue in frontmatter_issues(path):
        problems.append(f"versionnage doc - {issue}")

    if problems:
        print("ARCHITECTURE INCOMPLETE - points bloquants :", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1

    print("ARCHITECTURE OK - contrat technique present et coherent.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
