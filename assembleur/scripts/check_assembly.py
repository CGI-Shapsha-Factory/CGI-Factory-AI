#!/usr/bin/env python
"""Garde-fou deterministe (sans IA) de la phase convergence (assembleur).

L'assembleur produit un PAQUET de handoff dans `assembleur-out/` et deploie `CLAUDE.md` + `memory/`
directement dans le `.claude/` du projet (seule exception a "paquet seul"). Ce garde-fou lit le
manifeste (`manifest.json` a la racine par defaut ; repli `cadrage-out/manifest.json` legacy), en
deduit la racine du projet, et echoue si :
  - le bloc `assembly` est absent ;
  - un fichier du paquet manque (pre-constitution, >=1 graine de feature, feature-map,
    technical-context, coherence-report, attack-plan) dans `assembleur-out/` ;
  - `.claude/CLAUDE.md` ou un fichier de `.claude/memory/` (MEMORY, domain, architecture, design,
    features) manque (deploiement) ;
  - `.claude/CLAUDE.md` ne contient pas l'import `@memory/MEMORY.md` hors backticks (un import
    backtique = texte litteral, la memoire n'est jamais chargee) ;
  - il reste un marqueur ([A VALIDER]/[A CHIFFRER]/NEEDS CLARIFICATION) ou un placeholder de
    gabarit (AAAA-MM-JJ, <PROJECT_NAME>) dans `assembleur-out/` ou dans `.claude/` deploye
    (tout point doit etre tranche en session) ;
  - une feature de `architecture.feature_sequence` n'a pas sa graine dans `features/`, ou une
    graine ne correspond a aucune feature du registre (graine orpheline) ;
  - l'union des `ucs` du registre ne couvre pas exactement les `artifacts.briefs[].id`
    (use case orphelin ou fantome), quand les briefs sont declares ;
  - une graine ne contient aucun `FR-` ou aucun `SC-` (contrat avec le format spec.md et
    premier-alimente-linear, qui cree un sous-ticket par Functional Requirement).

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
    r"\[\s*(?:À|A)\s+(?:VALIDER|CHIFFRER)\s*\]|NEEDS\s+CLARIFICATION"
    r"|AAAA-MM-JJ|<PROJECT_NAME>",
    re.IGNORECASE,
)

FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
CODE_SPAN_RE = re.compile(r"`[^`\n]*`")


def _has_live_memory_import(text):
    """Vrai si `@memory/MEMORY.md` apparait hors backticks et hors bloc de code (import actif)."""
    stripped = CODE_SPAN_RE.sub("", FENCE_RE.sub("", text))
    return "@memory/MEMORY.md" in stripped


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
    # ... et le deploiement dans .claude/ (CLAUDE.md + memory/ complet : l'index MEMORY.md pointe
    # les fichiers thematiques, un absent = lien mort).
    required += [
        (".claude/CLAUDE.md", os.path.join(claude_dir, "CLAUDE.md")),
    ]
    for mem in ("MEMORY.md", "domain.md", "architecture.md", "design.md", "features.md"):
        required.append((f".claude/memory/{mem}", os.path.join(claude_dir, "memory", mem)))
    for label, p in required:
        if not os.path.isfile(p):
            problems.append(f"fichier du paquet manquant: {label}")

    # Cablage memoire : sans `@memory/MEMORY.md` hors backticks, rien n'est charge (echec silencieux).
    claude_md = os.path.join(claude_dir, "CLAUDE.md")
    if os.path.isfile(claude_md):
        try:
            text = open(claude_md, encoding="utf-8-sig").read()
        except (OSError, UnicodeDecodeError):
            text = ""
        if not _has_live_memory_import(text):
            problems.append(
                ".claude/CLAUDE.md sans import actif `@memory/MEMORY.md` "
                "(absent ou entre backticks: la memoire deployee ne serait jamais chargee)"
            )

    seeds = glob.glob(rel("features", "*.md"))
    if not seeds:
        problems.append("aucune graine de feature dans features/ (*.md)")

    # 2. Aucun marqueur residuel dans assembleur-out/ ni dans .claude/ deploye.
    # Les versions archivees par la porte de regeneration (`_archives/`) sont hors balayage.
    scan = [
        p
        for p in glob.glob(os.path.join(out, "**", "*.md"), recursive=True)
        if "_archives" not in p.replace("\\", "/").split("/")
    ]
    scan += glob.glob(os.path.join(claude_dir, "memory", "*.md"))
    scan.append(os.path.join(claude_dir, "CLAUDE.md"))
    for md in scan:
        try:
            text = open(md, encoding="utf-8-sig").read()
        except (OSError, UnicodeDecodeError):
            continue
        if MARKER_RE.search(text):
            problems.append(f"marqueur residuel dans {os.path.relpath(md, root)} (a trancher en session)")

    # 3. Couverture bidirectionnelle : chaque feature de la sequence a sa graine (par prefixe
    # d'id), et chaque graine correspond a une feature du registre (pas d'orpheline).
    seq = (manifest.get("architecture") or {}).get("feature_sequence") or []
    seq_ids = [it.get("id") if isinstance(it, dict) else it for it in seq]
    seed_names = [os.path.basename(s) for s in seeds]
    for fid in seq_ids:
        if fid and not any(n.startswith(f"{fid}-") for n in seed_names):
            problems.append(f"feature '{fid}' sans graine dans features/")
    for name in seed_names:
        m = re.match(r"^(\d{3})-", name)
        if m and m.group(1) not in seq_ids:
            problems.append(f"graine orpheline features/{name} (aucune feature '{m.group(1)}' au registre)")

    # 4. Jointure use cases : l'union des `ucs` du registre couvre exactement les briefs declares.
    briefs = (manifest.get("artifacts") or {}).get("briefs") or []
    brief_ids = {b.get("id") for b in briefs if isinstance(b, dict) and b.get("id")}
    if brief_ids and seq:
        ucs_union = set()
        for it in seq:
            if isinstance(it, dict):
                ucs_union.update(u for u in (it.get("ucs") or []) if u)
        for uc in sorted(brief_ids - ucs_union):
            problems.append(f"use case orphelin: brief '{uc}' rattache a aucune feature du registre")
        for uc in sorted(ucs_union - brief_ids):
            problems.append(f"use case fantome: la sequence reference '{uc}' sans brief declare")

    # 5. Contenu minimal des graines : au moins un FR- et un SC- (format spec.md ;
    # premier-alimente-linear cree un sous-ticket par FR).
    for s in seeds:
        try:
            text = open(s, encoding="utf-8-sig").read()
        except (OSError, UnicodeDecodeError):
            continue
        name = os.path.basename(s)
        if not re.search(r"\bFR-\d", text):
            problems.append(f"graine features/{name} sans Functional Requirement (FR-xxx)")
        if not re.search(r"\bSC-\d", text):
            problems.append(f"graine features/{name} sans Success Criteria (SC-xxx)")

    if problems:
        print("CONVERGENCE INCOMPLETE - points bloquants :", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1

    print("ASSEMBLAGE OK - le paquet de handoff SpecKit est complet dans assembleur-out/.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
