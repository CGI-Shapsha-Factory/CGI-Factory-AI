#!/usr/bin/env python
"""Garde-fou deterministe (sans IA) de la phase architecture.

Lit le manifeste partage d'un projet (`manifest.json` a la racine par defaut ; repli
`cadrage-out/manifest.json` pour les projets legacy) et echoue si le contrat technique est incomplet :
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
  - une techno de `stack-technique.md` n'a pas de version exacte (vide / 'latest' / ...) ;
  - un fichier de `architecte-out/` n'a pas de front-matter version(entier)/date(ISO) ;
  - la strategie de test de `standards-ingenierie.md` est incomplete (unit cas passant/echec/limite,
    integration avec mocks, tests en meme temps que le code) ;
  - les fichiers d'environnement ne sont pas generes (etape 10 : `env_files` absent, ou fichiers
    declares manquants a la racine, ou `.env` non gitignore), ou l'enforcement des tests n'est pas
    pose (etape 11).

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
import unicodedata

MARKER_RE = re.compile(r"\[\s*(?:À|A)\s+(?:VALIDER|CHIFFRER|D[ÉE]FINIR)\s*\]", re.IGNORECASE)

# Valeurs de version interdites : on exige une version exacte et epinglee.
FORBIDDEN_VERSION_RE = re.compile(
    r"^(?:latest|stable|current|newest|rolling|edge|nightly|tbd|n/?a|"
    r"derni[eè]re(?:\s+version)?|\.\.\.|…|—|-)$",
    re.IGNORECASE,
)
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _manifest_path(argv):
    """Manifeste a la racine (`manifest.json`) par defaut ; repli `cadrage-out/manifest.json` (legacy)."""
    if len(argv) > 1:
        return argv[1]
    return "manifest.json" if os.path.isfile("manifest.json") else "cadrage-out/manifest.json"


def _project_root(manifest_path):
    """Racine du projet = dossier du manifeste ; si le manifeste est dans `cadrage-out/` (legacy), on remonte."""
    d = os.path.dirname(os.path.abspath(manifest_path))
    return os.path.dirname(d) if os.path.basename(d) == "cadrage-out" else d


def _fold(s):
    """minuscule + sans accents (comparaisons robustes)."""
    return "".join(c for c in unicodedata.normalize("NFD", s.lower())
                   if unicodedata.category(c) != "Mn")


def testing_strategy_issues(manifest_path):
    """standards-ingenierie.md doit porter une vraie strategie de test (pas un tableau mince)."""
    root = _project_root(manifest_path)
    std = os.path.join(root, "architecte-out", "standards-ingenierie.md")
    if not os.path.isfile(std):
        return []
    try:
        folded = _fold(open(std, encoding="utf-8").read())
    except OSError:
        return []
    if "exigences de test" not in folded:
        return ["section 'Exigences de test' absente de standards-ingenierie.md"]
    checks = [
        ("meme temps", "regle 'tests en meme temps que le code' absente"),
        ("cas passant", "cas passant non exige"),
        ("echec", "cas d'echec non exige"),
        ("limite", "cas limite non exige"),
        ("integration", "tests d'integration non decrits"),
        ("mock", "integration avec mocks non exigee"),
    ]
    return [msg for needle, msg in checks if needle not in folded]


def residual_markers(manifest_path):
    """Renvoie la liste (fichier, marqueur) des marqueurs residuels dans architecte-out/."""
    root = _project_root(manifest_path)
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
    root = _project_root(manifest_path)
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
    """Chaque techno d'une table a colonne 'Version' de stack-technique.md porte une version exacte."""
    root = _project_root(manifest_path)
    ts = os.path.join(root, "architecte-out", "stack-technique.md")
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
            issues.append(f"stack-technique.md: techno '{name}' sans version exacte (valeur: '{val or 'vide'}')")
    return issues


def _dotenv_gitignored(root):
    """.env doit etre ignore par le .gitignore de la racine."""
    gi = os.path.join(root, ".gitignore")
    if not os.path.isfile(gi):
        return False
    try:
        for line in open(gi, encoding="utf-8"):
            s = line.strip().rstrip("/")
            # patterns qui ignorent VRAIMENT le fichier `.env` (pas `.env.*.local` seul).
            if s in (".env", ".env*", "*.env", "**/.env") or s.endswith("/.env"):
                return True
    except OSError:
        return False
    return False


def env_files_issues(manifest_path, arch):
    """Etape 10 : verifie que les fichiers d'environnement declares existent vraiment a la racine.

    - `env_files` absent (None) -> etape non faite (echec).
    - dict {initialized:false, ...} -> cas explicite « aucune variable necessaire » (OK).
    - dict {initialized:true, files:[...]} -> chaque fichier NON-`.env` doit exister a la racine.
      `.env` est gitignore (propre a chaque machine, absent d'un clone frais) : on n'exige PAS sa
      presence, seulement qu'il soit gitignore ET que `.env.example` (reference committee) existe.
    - valeur historique non structuree (chaine) -> toleree, non verifiable.
    """
    env = arch.get("env_files")
    if env is None:
        return ["fichiers d'environnement non generes (etape 10 : generer, ou noter l'absence de besoin)"]
    if not isinstance(env, dict):
        return []  # valeur historique non structuree : toleree
    if not env.get("initialized"):
        return []  # cas explicite « aucune dependance necessitant des variables »
    root = _project_root(manifest_path)
    issues = []
    files = env.get("files") or []
    if not files:
        issues.append("env_files initialise mais aucun fichier liste (champ `files` vide)")
    declares_dotenv = any(os.path.basename(str(f)) == ".env" for f in files)
    for rel in files:
        # `.env` est gitignore et propre a chaque machine : absent d'un clone frais -> pas exige.
        if os.path.basename(str(rel)) == ".env":
            continue
        if not os.path.isfile(os.path.join(root, str(rel))):
            issues.append(f"fichier d'environnement manquant a la racine : {rel}")
    if declares_dotenv and not os.path.isfile(os.path.join(root, ".env.example")):
        issues.append("`.env.example` (reference committee) manquant a la racine")
    if declares_dotenv and not _dotenv_gitignored(root):
        issues.append(".env non gitignore (completer le .gitignore de la racine)")
    return issues


def main(argv):
    path = _manifest_path(argv)
    try:
        with open(path, encoding="utf-8-sig") as f:
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

    for issue in testing_strategy_issues(path):
        problems.append(f"strategie de test - {issue}")

    for issue in env_files_issues(path, arch):
        problems.append(f"env - {issue}")
    if not arch.get("test_enforcement"):
        problems.append("enforcement des tests non pose (etape 11 : hooks + pre-commit a la racine)")

    if problems:
        print("ARCHITECTURE INCOMPLETE - points bloquants :", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1

    print("ARCHITECTURE OK - contrat technique present et coherent.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
