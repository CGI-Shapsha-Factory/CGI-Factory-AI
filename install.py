#!/usr/bin/env python
"""Installeur de la Factory IA — facon BMAD.

Une seule commande -> menu interactif -> tu coches les modules voulus (choix libre) ->
seuls ceux-la s'installent (avec leurs templates). Enrobe le CLI `claude plugin`.

Exemples :
  python install.py                              # menu interactif (cases a cocher)
  python install.py --all --yes                 # tout, sans prompt
  python install.py --modules cadrage,designer  # selection directe
  python install.py --list                       # lister les modules
  python install.py --modules cadrage --dry-run  # montrer les commandes sans installer

Prerequis : le CLI `claude` installe + acces (auth gh/git) au repo de la marketplace.
Aucun secret n'est lu ni affiche par ce script.
"""
import argparse, shutil, subprocess, sys

MARKETPLACE_NAME = "Shapsha-Factory"
MARKETPLACE_REPO = "CGI-Shapsha-Factory/CGI-Factory-AI"

# module -> (description, indication de role NON contraignante)
MODULES = {
    "cadrage":    ("Contrat fonctionnel : captation -> vision, glossaire, decoupage, briefs, pre-constitution.", "ex. chef de projet / PO"),
    "architecte": ("Contrat technique : drivers & qualite, composants, stack, ADR, walking skeleton, conventions.", "ex. architecte"),
    "designer":   ("Contrat de design : design system executable (tokens DTCG, composants & etats, parcours, WCAG 2.2).", "ex. dev front / UX"),
    "assembleur": ("Convergence des 3 contrats -> repo SpecKit + init Linear + hook de suivi.", "ex. lead / convergence"),
}
ORDER = ["cadrage", "architecte", "designer", "assembleur"]
NEXT_STEP = {
    "cadrage": "/cadrage:cadrage-init", "architecte": "/architecte:architecte-init",
    "designer": "/designer:designer-init", "assembleur": "/assembleur:assembleur-init",
}


# ---------------- logique pure (testable) ----------------
def parse_modules(s):
    """'cadrage, designer' -> ['cadrage','designer'] ; valide contre MODULES ; garde l'ordre canonique."""
    wanted = [m.strip().lower() for m in s.split(",") if m.strip()]
    unknown = [m for m in wanted if m not in MODULES]
    if unknown:
        raise ValueError(f"module(s) inconnu(s) : {', '.join(unknown)} (connus : {', '.join(ORDER)})")
    return [m for m in ORDER if m in wanted]


def install_cmd(module, scope):
    return ["claude", "plugin", "install", f"{module}@{MARKETPLACE_NAME}", "--scope", scope]


def add_marketplace_cmd():
    return ["claude", "plugin", "marketplace", "add", MARKETPLACE_REPO]


# ---------------- I/O ----------------
def print_list():
    print(f"\nModules de la Factory (marketplace : {MARKETPLACE_NAME})\n")
    for i, m in enumerate(ORDER, 1):
        desc, role = MODULES[m]
        print(f"  {i}. {m:<11} {desc}")
        print(f"     {'':<11} ({role})")
    print()


def print_marketplace_alt():
    print("\n— Alternative (toujours disponible) : install via le marketplace Claude Code —")
    print(f"  /plugin marketplace add {MARKETPLACE_REPO}")
    print(f"  /plugin install <module>@{MARKETPLACE_NAME}     # ex. cadrage@{MARKETPLACE_NAME}")
    print("  (ou /plugin -> onglet Discover : modules groupes par role)")


def select_checkbox(default_all=False):
    """Selection interactive robuste (liste numerotee) — fiable dans cmd/PowerShell/tout terminal."""
    return select_numbered(default_all)


def select_numbered(default_all=False):
    """Repli universel : liste numerotee, saisie '1,3' ou 'all'."""
    print_list()
    if default_all:
        return list(ORDER)
    raw = input("Numeros a installer (ex. 1,3) ou 'all' : ").strip().lower()
    if raw in ("all", "*", "tout"):
        return list(ORDER)
    picked = []
    for tok in raw.replace(" ", "").split(","):
        if tok.isdigit() and 1 <= int(tok) <= len(ORDER):
            picked.append(ORDER[int(tok) - 1])
    return [m for m in ORDER if m in picked]  # ordre canonique, dedup


def confirm(question):
    return input(f"{question} [o/N] ").strip().lower() in ("o", "oui", "y", "yes")


def run(cmd, dry):
    print(("  [dry-run] " if dry else "  $ ") + " ".join(cmd))
    if dry:
        return True
    r = subprocess.run(cmd)
    return r.returncode == 0


def main():
    ap = argparse.ArgumentParser(description="Installeur de la Factory IA (facon BMAD).")
    ap.add_argument("--modules", help="liste separee par des virgules (ex. cadrage,designer)")
    ap.add_argument("--all", action="store_true", help="installer tous les modules")
    ap.add_argument("--scope", choices=["user", "project", "local"], default="user", help="portee d'install (defaut: user)")
    ap.add_argument("--yes", "-y", action="store_true", help="ne pas demander de confirmation")
    ap.add_argument("--list", action="store_true", help="lister les modules et quitter")
    ap.add_argument("--no-add-marketplace", action="store_true", help="ne pas (re)ajouter la marketplace")
    ap.add_argument("--dry-run", action="store_true", help="montrer les commandes sans rien installer")
    a = ap.parse_args()

    if a.list:
        print_list(); print_marketplace_alt(); return 0

    # selection des modules
    try:
        if a.all:
            modules = list(ORDER)
        elif a.modules:
            modules = parse_modules(a.modules)
        else:
            modules = select_checkbox()
    except ValueError as e:
        print(f"Erreur : {e}", file=sys.stderr); return 2
    if not modules:
        print("Aucun module selectionne. Rien a faire."); return 0

    # CLI claude present ?
    if not a.dry_run and shutil.which("claude") is None:
        print("Le CLI `claude` est introuvable. Installe Claude Code puis relance.\n"
              "  https://code.claude.com/docs", file=sys.stderr)
        return 3

    print("\nModules a installer :", ", ".join(modules), f"(scope: {a.scope})")
    if not a.yes and sys.stdin.isatty() and not a.dry_run and not confirm("Continuer ?"):
        print("Annule."); return 1

    # 1) marketplace (idempotent ; un echec = peut-etre deja ajoutee -> on continue)
    if not a.no_add_marketplace:
        print(f"\nMarketplace {MARKETPLACE_NAME} ({MARKETPLACE_REPO}) :")
        ok = run(add_marketplace_cmd(), a.dry_run)
        if not ok and not a.dry_run:
            print("  (note: ajout non confirme — peut-etre deja presente ; je continue)")

    # 2) installation des modules choisis
    print("\nInstallation :")
    results = {}
    for m in modules:
        results[m] = run(install_cmd(m, a.scope), a.dry_run)

    # 3) restitution
    ok = [m for m in modules if results[m]]
    ko = [m for m in modules if not results[m]]
    print("\n=== Resume ===")
    for m in modules:
        print(f"  {'OK ' if results[m] else 'ECHEC'}  {m}")
    if ok:
        print("\nProchaines etapes (dans Claude Code) :")
        print("  /reload-plugins")
        for m in ok:
            print(f"  {NEXT_STEP[m]}   # demarrer le module {m}")
    print_marketplace_alt()
    if ko:
        print(f"\n{len(ko)} module(s) en echec : {', '.join(ko)} "
              "(verifie ton acces au repo de la marketplace, puis relance).", file=sys.stderr)
        return 4
    return 0


if __name__ == "__main__":
    sys.exit(main())
