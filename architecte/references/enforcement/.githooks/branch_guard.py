#!/usr/bin/env python
"""Garde-fou local de branche (deterministe, pur git+Python, sans dependance).

Deux protections, appelees par les hooks `pre-push` et `pre-commit` (via `core.hooksPath .githooks`) :
  - `pre_push(stdin)`  : refuse un push (normal, force ou suppression) vers une branche protegee.
  - `pre_commit()`     : refuse un commit fait DIRECTEMENT sur une branche protegee, puis enchaine
                         l'enforcement de tests existant (`.claude/hooks/tests_guard.py`) s'il est la.

Branches protegees : `main`, `master`, `develop` par defaut ; surchargeables via un fichier
`.githooks/protected-branches` (une branche par ligne, `#` = commentaire).

LIMITES (assumees) : local + par-clone + contournable (`--no-verify`). La vraie protection
multi-personnes est un ruleset serveur GitHub (hors perimetre de ce garde-fou local).
"""
import os
import subprocess
import sys

DEFAULT_PROTECTED = ("main", "master", "develop")
HOOK_DIR = os.path.dirname(os.path.abspath(__file__))


def protected_branches():
    """Liste des branches protegees : defaut, ou override `.githooks/protected-branches`."""
    override = os.path.join(HOOK_DIR, "protected-branches")
    if os.path.isfile(override):
        try:
            with open(override, encoding="utf-8-sig") as f:
                names = [ln.strip() for ln in f if ln.strip() and not ln.strip().startswith("#")]
            if names:
                return set(names)
        except OSError:
            pass
    return set(DEFAULT_PROTECTED)


def current_branch():
    try:
        out = subprocess.run(
            ["git", "symbolic-ref", "--short", "HEAD"],
            capture_output=True, text=True,
        )
        return out.stdout.strip()
    except OSError:
        return ""


def _fail(msg):
    sys.stderr.write("\n" + msg + "\n\n")
    return 1


def pre_commit():
    """Bloque un commit sur une branche protegee, puis relaie l'enforcement de tests s'il existe."""
    protected = protected_branches()
    branch = current_branch()
    if branch in protected:
        return _fail(
            f"Commit direct sur '{branch}' interdit (branche protegee).\n"
            f"Cree une branche de travail puis recommite :\n"
            f"    git switch -c feat/ma-modif\n"
            f"(contournement d'urgence : git commit --no-verify)"
        )

    # Preserver l'enforcement de tests de l'architecte (comportement inchange) s'il est present.
    tests_guard = os.path.join(".claude", "hooks", "tests_guard.py")
    if os.path.isfile(tests_guard):
        staged = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
            capture_output=True, text=True,
        ).stdout.split()
        rc = subprocess.run(
            [sys.executable, tests_guard, "check", *staged]
        ).returncode
        return rc
    return 0


def pre_push(stream):
    """Bloque tout push visant une branche protegee (push normal, force-push ou suppression).

    Git fournit sur stdin, une ligne par ref poussee :
        <local ref> <local sha> <remote ref> <remote sha>
    """
    protected = protected_branches()
    for line in stream:
        parts = line.split()
        if len(parts) < 3:
            continue
        remote_ref = parts[2]
        name = remote_ref[len("refs/heads/"):] if remote_ref.startswith("refs/heads/") else remote_ref
        if name in protected:
            return _fail(
                f"Push direct sur '{name}' interdit (branche protegee).\n"
                f"Pousse ta branche de travail et ouvre une Pull Request :\n"
                f"    git push origin HEAD:feat/ma-modif\n"
                f"(contournement d'urgence : git push --no-verify)"
            )
    return 0
