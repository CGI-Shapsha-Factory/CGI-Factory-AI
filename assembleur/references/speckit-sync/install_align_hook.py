#!/usr/bin/env python
"""Installe le hook d'alignement SpecKit : copie le garde-fou PUIS fusionne le hook PostToolUse.

Deux gestes deterministes (jamais laisses au modele), miroir de l'enforcement architecte et du hook
sync tasks->Linear :
  1. COPIE `check_speckit_alignment.py` (depuis `assembleur/scripts/`) -> `<racine>/.claude/hooks/`
     (idempotent : inchange si identique, remplace avec sauvegarde .bak si la copie est obsolete).
  2. FUSIONNE le hook `PostToolUse` (matcher Write|Edit) dans `.claude/settings.json` SANS ecraser un
     hook existant (tests_guard/format_guard de l'architecte, tasks_linear_hook, SessionEnd des couts).

Le garde-fou detecte, a chaque edition d'un fichier sous `specs/<dir>/`, un numero de feature en
collision / timestamp / hors registre canonique, et pousse l'agent a recreer le dossier avec
`SPECIFY_FEATURE_DIRECTORY=specs/NNN-slug`. Il ne parle a aucun systeme externe.

Usage : python install_align_hook.py [racine_projet]   (defaut : cwd)
"""
import json
import os
import shutil
import subprocess
import sys

MARKER = "check_speckit_alignment.py"

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "..", "scripts", "check_speckit_alignment.py")


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
           + ' "${CLAUDE_PROJECT_DIR}/.claude/hooks/check_speckit_alignment.py" posttooluse')
    return {"matcher": "Write|Edit",
            "hooks": [{"type": "command", "command": cmd, "timeout": 30}]}


def _copy_asset(root):
    dst = os.path.join(root, ".claude", "hooks", "check_speckit_alignment.py")
    if not os.path.isfile(SRC):
        print(f"ATTENTION: source introuvable, non copiee : {SRC}", file=sys.stderr)
        return
    if os.path.isfile(dst):
        # why: une copie OBSOLETE (version precedente du plugin, ou commitee par l'equipe) restait en
        # place a vie. On rafraichit, en gardant une sauvegarde.
        with open(SRC, "rb") as f:
            src_bytes = f.read()
        with open(dst, "rb") as f:
            if f.read() == src_bytes:
                print("garde-fou alignement SpecKit : deja a jour (.claude/hooks/check_speckit_alignment.py)")
                return
        shutil.copyfile(dst, dst + ".bak")
        shutil.copyfile(SRC, dst)
        print("garde-fou alignement SpecKit : version obsolete remplacee (sauvegarde : check_speckit_alignment.py.bak)")
        return
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copyfile(SRC, dst)
    print("garde-fou alignement SpecKit : copie -> .claude/hooks/check_speckit_alignment.py")


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
        print("hook PostToolUse alignement SpecKit : deja enregistre dans .claude/settings.json")
        return 0
    arr.append(_entry())
    with open(settings, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"hook PostToolUse alignement SpecKit : ajoute ; evenements presents : {', '.join(sorted(data['hooks']))}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
