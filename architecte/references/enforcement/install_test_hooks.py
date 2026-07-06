#!/usr/bin/env python
"""Installe le hook de test PostToolUse : copie le script garde-fou PUIS fusionne le hook.

Deux gestes, atomiques et deterministes (jamais laisses au modele) :
  1. COPIE `tests_guard.py` -> `<racine>/.claude/hooks/` et `lefthook.yml` -> `<racine>/`
     (depuis ce dossier de plugin ; ne jamais ecraser un fichier existant — idempotent).
  2. FUSIONNE le hook `PostToolUse` dans `.claude/settings.json` sans ecraser un evenement
     existant (ex. le hook `SessionEnd` du compteur de couts).
Sans l'etape 1, le hook enregistre pointerait vers un script absent (hook mort).

Usage : python install_test_hooks.py [racine_projet]   (defaut : cwd)
"""
import json
import os
import shutil
import sys

MARKER = "tests_guard.py"
ENTRIES = {
    "PostToolUse": {"matcher": "Write|Edit",
                    "hooks": [{"type": "command",
                               "command": "python .claude/hooks/tests_guard.py posttooluse",
                               "timeout": 30}]},
}

HERE = os.path.dirname(os.path.abspath(__file__))
# (source, destination-relative-a-la-racine) — copies deterministes, sans ecrasement
FILE_COPIES = [
    (os.path.join(HERE, ".claude", "hooks", "tests_guard.py"),
     os.path.join(".claude", "hooks", "tests_guard.py")),
    (os.path.join(HERE, "lefthook.yml"), "lefthook.yml"),
]


def _copy_assets(root):
    copied, skipped = [], []
    for src, rel in FILE_COPIES:
        dst = os.path.join(root, rel)
        if os.path.isfile(dst):
            skipped.append(rel)
            continue
        if not os.path.isfile(src):
            print(f"ATTENTION: source introuvable, non copiee : {src}", file=sys.stderr)
            continue
        os.makedirs(os.path.dirname(dst) or root, exist_ok=True)
        shutil.copyfile(src, dst)
        copied.append(rel)
    print(f"fichiers garde-fou : {('copies ' + ', '.join(copied)) if copied else 'aucun a copier'}"
          f"{(' ; deja presents ' + ', '.join(skipped)) if skipped else ''}")


def main(argv):
    root = os.path.abspath(argv[1] if len(argv) > 1 else os.getcwd())
    claude_dir = os.path.join(root, ".claude")
    settings = os.path.join(claude_dir, "settings.json")
    os.makedirs(claude_dir, exist_ok=True)

    _copy_assets(root)

    data = {}
    if os.path.isfile(settings):
        try:
            data = json.load(open(settings, encoding="utf-8")) or {}
        except ValueError:
            print(f"ERREUR: {settings} JSON invalide — abandon (pas d'ecrasement).", file=sys.stderr)
            return 1

    hooks = data.setdefault("hooks", {})
    added = []
    for event, entry in ENTRIES.items():
        arr = hooks.setdefault(event, [])
        if any(MARKER in (h.get("command") or "") for g in arr for h in g.get("hooks", [])):
            continue
        arr.append(entry)
        added.append(event)
    with open(settings, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"hooks de test : {('ajoutes ' + ', '.join(added)) if added else 'deja presents'}"
          f" ; evenements presents : {', '.join(sorted(hooks))}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
