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
# Chemin ANCRE sur la racine du projet via ${CLAUDE_PROJECT_DIR} : un chemin relatif nu
# (.claude/hooks/...) se resout contre le cwd du hook — casse des qu'un Write cible un
# sous-dossier (le hook ne tourne pas depuis la racine). Cf. Claude Code hooks reference.
CMD = 'python "${CLAUDE_PROJECT_DIR}/.claude/hooks/tests_guard.py" posttooluse'
ENTRIES = {
    "PostToolUse": {"matcher": "Write|Edit",
                    "hooks": [{"type": "command", "command": CMD, "timeout": 30}]},
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
    added, upgraded = [], []
    for event, entry in ENTRIES.items():
        arr = hooks.setdefault(event, [])
        desired = entry["hooks"][0]["command"]
        found = False
        for g in arr:
            for h in g.get("hooks", []):
                if MARKER in (h.get("command") or ""):
                    found = True
                    if h.get("command") != desired:  # migre un ancien chemin relatif nu
                        h["command"] = desired
                        upgraded.append(event)
        if not found:
            arr.append(entry)
            added.append(event)
    with open(settings, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    state = (("ajoutes " + ", ".join(added)) if added else "deja presents")
    if upgraded:
        state += f" ; chemins migres -> CLAUDE_PROJECT_DIR ({', '.join(upgraded)})"
    print(f"hooks de test : {state} ; evenements presents : {', '.join(sorted(hooks))}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
