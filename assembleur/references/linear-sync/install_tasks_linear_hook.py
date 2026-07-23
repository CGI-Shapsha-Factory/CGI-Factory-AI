#!/usr/bin/env python
"""Installe le hook de sync tasks->Linear : copie le script PUIS fusionne le hook PostToolUse.

Deux gestes deterministes (jamais laisses au modele), miroir de l'enforcement architecte :
  1. COPIE `tasks_linear_hook.py` -> `<racine>/.claude/hooks/` (depuis ce dossier de plugin ;
     idempotent : inchange si identique, remplace avec sauvegarde .bak si la copie est obsolete).
  2. FUSIONNE le hook `PostToolUse` dans `.claude/settings.json` SANS ecraser un hook existant
     (tests_guard/format_guard de l'architecte, SessionEnd du compteur de couts).

Le hook lui-meme ne parle jamais a Linear : il detecte une derive tasks.md -> manifeste et pousse
l'agent a lancer /assembleur:creation-taches-par-phase-de-spec (cf. tasks_linear_hook.py).

Usage : python install_tasks_linear_hook.py [racine_projet]   (defaut : cwd)
"""
import json
import os
import shutil
import subprocess
import sys

MARKER = "tasks_linear_hook.py"

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "tasks_linear_hook.py")


def _interpreter():
    """Interpreteur a inscrire dans la commande du hook.

    why: `python` en dur echoue a CHAQUE Write/Edit sur un poste ou seul `py` (ou `python3`) resout —
    un hook qui plante en boucle est pire qu'un hook absent. On prefere un nom PORTABLE (settings.json
    est committe et partage : un chemin absolu casserait chez les autres) et on ne retombe sur le
    chemin absolu de CE poste que si aucun nom ne repond. Chaque candidat est reellement execute :
    sur Windows, `python` peut resoudre vers le stub Microsoft Store, qui ne lance rien.
    """
    for cand in ("python", "python3", "py"):
        if not shutil.which(cand):
            continue
        try:
            if subprocess.run([cand, "-c", "pass"], capture_output=True, timeout=20).returncode == 0:
                return cand
        except (OSError, subprocess.SubprocessError):
            continue
    exe = sys.executable
    return f'"{exe}"' if exe and os.path.isfile(exe) else "python"


def _entry():
    cmd = (_interpreter()
           + ' "${CLAUDE_PROJECT_DIR}/.claude/hooks/tasks_linear_hook.py" posttooluse')
    return {"matcher": "Write|Edit",
            "hooks": [{"type": "command", "command": cmd, "timeout": 30}]}


def _copy_asset(root):
    dst = os.path.join(root, ".claude", "hooks", "tasks_linear_hook.py")
    if not os.path.isfile(SRC):
        print(f"ATTENTION: source introuvable, non copiee : {SRC}", file=sys.stderr)
        return
    if os.path.isfile(dst):
        # why: une copie OBSOLETE (posee par une version precedente du plugin, ou commitee par
        # l'equipe) restait en place a vie. On rafraichit, en gardant une sauvegarde.
        with open(SRC, "rb") as f:
            src_bytes = f.read()
        with open(dst, "rb") as f:
            if f.read() == src_bytes:
                print("hook sync tasks->Linear : deja a jour (.claude/hooks/tasks_linear_hook.py)")
                return
        shutil.copyfile(dst, dst + ".bak")
        shutil.copyfile(SRC, dst)
        print("hook sync tasks->Linear : version obsolete remplacee (sauvegarde : tasks_linear_hook.py.bak)")
        return
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copyfile(SRC, dst)
    print("hook sync tasks->Linear : copie -> .claude/hooks/tasks_linear_hook.py")


def main(argv):
    root = os.path.abspath(argv[1] if len(argv) > 1 else os.getcwd())
    claude_dir = os.path.join(root, ".claude")
    settings = os.path.join(claude_dir, "settings.json")
    os.makedirs(claude_dir, exist_ok=True)

    _copy_asset(root)

    data = {}
    if os.path.isfile(settings):
        try:
            data = json.load(open(settings, encoding="utf-8")) or {}
        except ValueError:
            print(f"ERREUR: {settings} JSON invalide - abandon (pas d'ecrasement).", file=sys.stderr)
            return 1

    arr = data.setdefault("hooks", {}).setdefault("PostToolUse", [])
    found = any(MARKER in (h.get("command") or "")
                for g in arr for h in g.get("hooks", []))
    if found:
        print("hook PostToolUse sync tasks->Linear : deja enregistre dans .claude/settings.json")
        return 0
    arr.append(_entry())
    with open(settings, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"hook PostToolUse sync tasks->Linear : ajoute ; evenements presents : {', '.join(sorted(data['hooks']))}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
