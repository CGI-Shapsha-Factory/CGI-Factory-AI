#!/usr/bin/env python
"""Garde-fou deterministe (sans IA) de la phase convergence (assembleur).

L'assembleur produit un PAQUET de handoff dans `assembleur-out/` et deploie `CLAUDE.md` + `memory/`
directement dans le `.claude/` du projet (seule exception a "paquet seul"). Ce garde-fou lit le
manifeste (`manifest.json` a la racine par defaut ; repli `cadrage-out/manifest.json` legacy), en
deduit la racine du projet, et echoue si :
  - le bloc `assembly` est absent ;
  - un fichier du paquet manque (pre-constitution, >=1 graine de feature, feature-map,
    technical-context, coherence-report, attack-plan) dans `assembleur-out/` ;
  - `.claude/CLAUDE.md` ou `.claude/memory/MEMORY.md` manque (deploiement) ;
  - il reste un marqueur ([A VALIDER]/[A CHIFFRER]/NEEDS CLARIFICATION) dans `assembleur-out/`
    ou dans `.claude/memory/` (tout point doit etre tranche en session) ;
  - une feature de `architecture.feature_sequence` n'a pas sa graine dans `features/`.

La porte HUMAINE (`coherence_validated`) n'est PAS verifiee ici. Exit 0 si tout est present,
sinon 1.

Usage:
    python check_assembly.py [chemin/vers/manifest.json]
"""
import glob
import json
import os
import re
import sys

MARKER_RE = re.compile(
    r"\[\s*(?:À|A)\s+(?:VALIDER|CHIFFRER)\s*\]|NEEDS\s+CLARIFICATION", re.IGNORECASE
)


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

    asm = manifest.get("assembly")
    if not isinstance(asm, dict):
        print("ERREUR: bloc `assembly` absent (lancer assembleur-init).", file=sys.stderr)
        return 1

    root = _project_root(path)
    out = os.path.join(root, "assembleur-out")
    claude_dir = os.path.join(root, ".claude")
    problems = []

    def rel(*parts):
        return os.path.join(out, *parts)

    # 1. Presence du paquet (assembleur-out/).
    required = [
        ("pre-constitution.md", rel("pre-constitution.md")),
        ("feature-map.md", rel("feature-map.md")),
        ("technical-context.md", rel("technical-context.md")),
        ("coherence-report.md", rel("coherence-report.md")),
        ("attack-plan.md", rel("attack-plan.md")),
    ]
    # ... et le deploiement dans .claude/ (CLAUDE.md + memory/).
    required += [
        (".claude/CLAUDE.md", os.path.join(claude_dir, "CLAUDE.md")),
        (".claude/memory/MEMORY.md", os.path.join(claude_dir, "memory", "MEMORY.md")),
    ]
    for label, p in required:
        if not os.path.isfile(p):
            problems.append(f"fichier du paquet manquant: {label}")

    seeds = glob.glob(rel("features", "*.md"))
    if not seeds:
        problems.append("aucune graine de feature dans features/ (*.md)")

    # 2. Aucun marqueur residuel dans assembleur-out/ ni dans .claude/memory/.
    scan = glob.glob(os.path.join(out, "**", "*.md"), recursive=True)
    scan += glob.glob(os.path.join(claude_dir, "memory", "*.md"))
    scan.append(os.path.join(claude_dir, "CLAUDE.md"))
    for md in scan:
        try:
            text = open(md, encoding="utf-8-sig").read()
        except (OSError, UnicodeDecodeError):
            continue
        if MARKER_RE.search(text):
            problems.append(f"marqueur residuel dans {os.path.relpath(md, root)} (a trancher en session)")

    # 3. Couverture : chaque feature de la sequence a sa graine (par prefixe d'id).
    seq = (manifest.get("architecture") or {}).get("feature_sequence") or []
    seq_ids = [it.get("id") if isinstance(it, dict) else it for it in seq]
    seed_names = [os.path.basename(s) for s in seeds]
    for fid in seq_ids:
        if fid and not any(n.startswith(f"{fid}-") for n in seed_names):
            problems.append(f"feature '{fid}' sans graine dans features/")

    if problems:
        print("CONVERGENCE INCOMPLETE - points bloquants :", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1

    print("ASSEMBLAGE OK - le paquet de handoff SpecKit est complet dans assembleur-out/.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
