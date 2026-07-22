#!/usr/bin/env python
"""Garde-fou deterministe (sans IA) de la validation fonctionnelle.

La validation produit des artefacts commites dans validation-out/<feature>/ (plan de test,
resultats d'execution, rapport de recette, scenarios rejouables) ; le verdict humain vit dans
le rapport et dans Linear, jamais dans le manifeste. Ce garde-fou valide le TERRAIN (manifeste
+ gabarits) et, si une feature est passee en argument, la TRACABILITE de ses artefacts.

Lit le manifeste partage d'un projet (`manifest.json` a la racine par defaut ; repli
`cadrage-out/manifest.json` legacy) et echoue si :
  - bloc `validation` absent ;
  - gabarits absents de `.factory/validation/` (relancer validation-init).
L'adresse de l'environnement de recette absente n'est jamais bloquante : elle est signalee
(execution-validation la demandera).

Avec une feature en second argument (le nom de son dossier sous validation-out/), echoue si :
  - le plan `validation-out/<feature>/plan-de-test.md` est absent ;
  - un cas de test du plan ne cite pas son critere source ;
  - le rapport `rapport-de-recette.md` existe mais son verdict n'est pas rempli (le gabarit
    contient toujours le titre de la section : on exige une ligne `- **Verdict** : <valeur>`
    dont la valeur n'est pas le placeholder entre parentheses du gabarit).

Exit 0 si tout est present, sinon 1.

Usage:
    python check_validation.py [chemin/vers/manifest.json] [feature]
"""
import json
import os
import re
import sys

GABARITS = ("plan-de-test.md", "execution-resultats.md", "mission-cowork.md",
            "rapport-de-recette.md", "scenario-rejouable.md")


def _manifest_path(argv):
    """Manifeste a la racine (`manifest.json`) par defaut ; repli `cadrage-out/manifest.json` (legacy)."""
    if len(argv) > 1:
        return argv[1]
    return "manifest.json" if os.path.isfile("manifest.json") else "cadrage-out/manifest.json"


def _project_root(manifest_path):
    """Racine du projet : le dossier du manifeste (remonte d'un cran si manifeste legacy dans cadrage-out/)."""
    root = os.path.dirname(os.path.abspath(manifest_path))
    if os.path.basename(root) == "cadrage-out":
        root = os.path.dirname(root)
    return root


CAS_RE = re.compile(r"^\|\s*(TC-\d{3}-\d{3})\s*\|(.*)$", re.MULTILINE)


def _section(contenu, titre_regex):
    """Contenu d'une section `## <titre>` jusqu'au prochain `## ` (chaine vide si absente)."""
    match = re.search(rf"^##\s+{titre_regex}\s*$(.*?)(?=^##\s|\Z)", contenu,
                      flags=re.MULTILINE | re.DOTALL)
    return match.group(1) if match else ""


def _lignes_tracees(section):
    """Identifiants des cas dont la derniere cellule (Source) est remplie."""
    traces = set()
    for cas, reste in CAS_RE.findall(section):
        cellules = [c.strip() for c in reste.rstrip().rstrip("|").split("|")]
        if cellules and cellules[-1]:
            traces.add(cas)
    return traces


def _check_plan(contenu, feature, problems):
    """Tracabilite du plan de test : forme tableau, avec repli sur l'ancienne forme en blocs."""
    vue = _section(contenu, r"Vue d'ensemble")
    if vue.strip():
        cas = [c for c, _ in CAS_RE.findall(vue)]
        if not cas:
            problems.append(
                f"plan de test sans aucun cas de test (validation-out/{feature}/plan-de-test.md)")
            return
        traces = _lignes_tracees(_section(contenu, r"D[eé]roul[eé] des cas"))
        traces |= _lignes_tracees(_section(contenu, r"Crit[eè]res [aà] clarifier"))
        orphelins = [c for c in cas if c not in traces]
        if orphelins:
            problems.append(
                f"tracabilite rompue: {len(orphelins)} cas sans source ({', '.join(orphelins[:5])}"
                f"{'...' if len(orphelins) > 5 else ''}) - chaque ligne de cas doit porter sa Source")
        return

    # Repli : plans ecrits avant le passage aux tableaux (un bloc `### TC-` par cas).
    cas = re.findall(r"^###\s+TC-", contenu, flags=re.MULTILINE)
    sources = re.findall(r"^\s*-\s+\*\*Crit[eè]re source\*\*", contenu, flags=re.MULTILINE)
    if not cas:
        problems.append(
            f"plan de test sans aucun cas de test (validation-out/{feature}/plan-de-test.md)")
    elif len(sources) < len(cas):
        problems.append(
            f"tracabilite rompue: {len(cas)} cas de test mais {len(sources)} criteres sources cites "
            f"(chaque cas doit citer son critere)")


def _check_feature(root, feature, problems):
    """Controles de tracabilite des artefacts d'une feature."""
    fdir = os.path.join(root, "validation-out", feature)
    plan = os.path.join(fdir, "plan-de-test.md")
    if not os.path.isfile(plan):
        problems.append(
            f"plan de test manquant: validation-out/{feature}/plan-de-test.md (lancer plan-de-validation)")
        return

    with open(plan, encoding="utf-8-sig") as f:
        contenu = f.read()
    _check_plan(contenu, feature, problems)

    rapport = os.path.join(fdir, "rapport-de-recette.md")
    if os.path.isfile(rapport):
        with open(rapport, encoding="utf-8-sig") as f:
            rcontenu = f.read()
        section = re.search(r"^##\s+Verdict de recette\s*$(.*)", rcontenu,
                            flags=re.MULTILINE | re.DOTALL)
        verdict = None
        if section:
            verdict = re.search(r"^\s*-\s+\*\*Verdict\*\*\s*:\s*(\S.*)$", section.group(1),
                                flags=re.MULTILINE)
        if not section or not verdict or verdict.group(1).lstrip().startswith("("):
            problems.append(
                f"rapport sans verdict rempli (validation-out/{feature}/rapport-de-recette.md) - "
                f"la porte de recette n'a pas ete franchie proprement")


def main(argv):
    path = _manifest_path(argv)
    feature = argv[2] if len(argv) > 2 else None
    try:
        with open(path, encoding="utf-8-sig") as f:
            manifest = json.load(f)
    except FileNotFoundError:
        print(f"ERREUR: manifeste introuvable: {path}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"ERREUR: manifeste JSON invalide: {exc}", file=sys.stderr)
        return 1

    validation = manifest.get("validation")
    if not isinstance(validation, dict):
        print("ERREUR: bloc `validation` absent (lancer validation-init).", file=sys.stderr)
        return 1

    problems = []
    root = _project_root(path)

    for gabarit in GABARITS:
        gpath = os.path.join(root, ".factory", "validation", gabarit)
        if not os.path.isfile(gpath):
            problems.append(f"gabarit manquant: .factory/validation/{gabarit} (relancer validation-init)")

    env = validation.get("environnement_recette")

    if feature:
        _check_feature(root, feature, problems)

    if problems:
        print("VALIDATION INCOMPLETE - points bloquants :", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1

    env_msg = "environnement de recette renseigne" if env else \
        "environnement de recette a renseigner (demande a l'execution)"
    if feature:
        print(f"VALIDATION OK - terrain en place, plan de la feature {feature} trace, {env_msg}.")
    else:
        print(f"VALIDATION OK - gabarits en place, {env_msg}.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
