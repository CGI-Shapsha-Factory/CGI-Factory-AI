#!/usr/bin/env python
"""Garde-fou deterministe (sans IA) du document de supervision Cowork (create-cowork-md).

Le skill `create-cowork-md` genere `init-cowork.md` a la racine du projet (contexte unique pour le
PO qui supervise depuis Quark : liens vers le depot GitHub et le projet Linear + le contexte issu
des 3 contrats). Ce garde-fou lit le manifeste (`manifest.json` a la racine par defaut ; repli
`cadrage-out/manifest.json` legacy), en deduit la racine du projet, et echoue si :
  - le bloc `cowork` est absent (le skill n'a pas tourne) ;
  - `init-cowork.md` n'existe pas a la racine ;
  - le document n'expose pas une section GitHub ET une section Linear (les deux points d'entree
    vivants que le PO doit pouvoir atteindre).

Ecriture racine = exception bornee assumee (fichier de contexte de supervision, jamais un fichier
que SpecKit genere). Exit 0 si tout est coherent, sinon 1.

Usage:
    python check_cowork.py [chemin/vers/manifest.json]
"""
import json
import os
import re
import sys

GITHUB_RE = re.compile(r"github", re.IGNORECASE)
LINEAR_RE = re.compile(r"linear", re.IGNORECASE)


def _manifest_path(argv):
    """Manifeste a la racine (`manifest.json`) par defaut ; repli `cadrage-out/manifest.json` (legacy)."""
    if len(argv) > 1:
        return argv[1]
    return "manifest.json" if os.path.isfile("manifest.json") else "cadrage-out/manifest.json"


def _project_root(manifest_path):
    """Racine = dossier du manifeste ; si le manifeste est dans `cadrage-out/` (legacy), on remonte."""
    d = os.path.dirname(os.path.abspath(manifest_path))
    return os.path.dirname(d) if os.path.basename(d) == "cadrage-out" else d


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

    cowork = manifest.get("cowork")
    if not isinstance(cowork, dict):
        print("ERREUR: bloc `cowork` absent (lancer create-cowork-md).", file=sys.stderr)
        return 1

    root = _project_root(path)
    rel_path = cowork.get("path") or "init-cowork.md"
    doc = os.path.join(root, rel_path)
    problems = []

    if not os.path.isfile(doc):
        problems.append(f"document de supervision manquant: {rel_path}")
        text = ""
    else:
        try:
            text = open(doc, encoding="utf-8").read()
        except OSError as exc:
            problems.append(f"document illisible ({rel_path}): {exc}")
            text = ""

    # Les deux points d'entree vivants doivent etre presents (section GitHub + section Linear).
    if text:
        headings = re.findall(r"^#{1,6}\s+.*$", text, flags=re.MULTILINE)
        joined = "\n".join(headings)
        if not GITHUB_RE.search(joined):
            problems.append("section GitHub absente du document (depot du code introuvable)")
        if not LINEAR_RE.search(joined):
            problems.append("section Linear absente du document (suivi du projet introuvable)")

    if problems:
        print("DOCUMENT COWORK INCOMPLET - points bloquants :", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1

    print(f"COWORK OK - {rel_path} expose le depot GitHub et le projet Linear.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
