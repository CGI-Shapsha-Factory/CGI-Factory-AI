#!/usr/bin/env python
"""Garde-fou "tests ecrits avec le code" — hook Claude Code + pre-commit (multi-langage).

Sous-commandes :
  posttooluse  : (hook PostToolUse) lit le JSON stdin ; si la source editee n'a pas de test,
                 imprime {"decision":"block","reason":...} pour relancer Claude (exit 0).
  check [files]: (pre-commit) echoue (exit 1) si un des fichiers donnes (ou l'index git) est
                 une source sans test associe.

Un fichier source "a un test" si un fichier de test correspondant existe dans le depot
(nom derive du langage : test_x.py / x_test.py ; x.test.ts / x.spec.ts ; x_test.go ;
XTests.cs / XTest.cs ; XTest.java / XTests.java).

Portable : pur Python + git, aucune dependance. Adapter la commande `python` si besoin.
"""
import json
import os
import subprocess
import sys

SOURCE_EXTS = {".py", ".ts", ".tsx", ".js", ".jsx", ".go", ".cs", ".java"}
SKIP_NAME = {"__init__.py", "conftest.py", "setup.py", "manage.py", "index.ts", "index.js"}
SKIP_DIR = {"node_modules", "dist", "build", ".venv", "venv", "__pycache__", ".git",
            "migrations", ".angular", "bin", "obj", "coverage"}
SKIP_SUFFIX = (".config.js", ".config.ts", ".d.ts", ".module.ts")


def _norm(path):
    return path.replace("\\", "/")


def is_test_file(path):
    p = _norm(path)
    n = os.path.basename(p)
    low = n.lower()
    return (
        low.startswith("test_") or low.endswith("_test.py") or low.endswith("_test.go")
        or ".test." in low or ".spec." in low
        or n.endswith("Test.cs") or n.endswith("Tests.cs")
        or n.endswith("Test.java") or n.endswith("Tests.java")
        or "/tests/" in p or "/test/" in p or "__tests__" in p
    )


def is_gated_source(path):
    p = _norm(path)
    if any(part in SKIP_DIR for part in p.split("/")):
        return False
    name = os.path.basename(p)
    _, ext = os.path.splitext(name)
    if ext not in SOURCE_EXTS:
        return False
    if name in SKIP_NAME or p.endswith(SKIP_SUFFIX):
        return False
    return not is_test_file(p)


def candidate_test_names(path):
    stem, ext = os.path.splitext(os.path.basename(path))
    if ext == ".py":
        return {f"test_{stem}.py", f"{stem}_test.py"}
    if ext in (".ts", ".tsx", ".js", ".jsx"):
        e = ext.lstrip(".")
        return {f"{stem}.test.{e}", f"{stem}.spec.{e}",
                f"{stem}.test.ts", f"{stem}.spec.ts", f"{stem}.test.tsx", f"{stem}.spec.tsx"}
    if ext == ".go":
        return {f"{stem}_test.go"}
    if ext == ".cs":
        return {f"{stem}Tests.cs", f"{stem}Test.cs", f"{stem}.Tests.cs"}
    if ext == ".java":
        return {f"{stem}Test.java", f"{stem}Tests.java"}
    return set()


def git_root():
    d = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    try:
        out = subprocess.run(["git", "-C", d, "rev-parse", "--show-toplevel"],
                             capture_output=True, text=True, check=True)
        return out.stdout.strip() or d
    except (subprocess.CalledProcessError, OSError):
        return d


def _git(root, args):
    try:
        out = subprocess.run(["git", "-C", root, *args], capture_output=True, text=True, check=True)
        return [ln for ln in out.stdout.splitlines() if ln.strip()]
    except (subprocess.CalledProcessError, OSError):
        return []


def repo_test_basenames(root):
    files = set(_git(root, ["ls-files"])) | set(_git(root, ["ls-files", "--others", "--exclude-standard"]))
    return {os.path.basename(f) for f in files if is_test_file(f)}


def missing_tests(root, source_paths):
    have = repo_test_basenames(root)
    return [s for s in source_paths if is_gated_source(s) and not (candidate_test_names(s) & have)]


def cmd_posttooluse():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0
    path = (data.get("tool_input") or {}).get("file_path", "")
    if not path or not is_gated_source(path):
        return 0
    if candidate_test_names(path) & repo_test_basenames(git_root()):
        return 0
    reason = (f"Aucun test trouve pour {os.path.basename(path)}. "
              f"Lance /architecte:gen-tests pour generer le test automatiquement, "
              f"ou ecris-le manuellement (cas passant / echec / limite).")
    print(json.dumps({"decision": "block", "reason": reason}))
    return 0


def cmd_check(files):
    root = git_root()
    if not files:
        files = _git(root, ["diff", "--cached", "--name-only", "--diff-filter=ACM"])
    miss = missing_tests(root, files)
    if miss:
        sys.stderr.write("Commit bloque — source sans test associe :\n  - " + "\n  - ".join(miss) +
                         "\nAjoute le(s) test(s) puis recommite (ou --no-verify en dernier recours).\n")
        return 1
    return 0


def main(argv):
    mode = argv[1] if len(argv) > 1 else "posttooluse"
    if mode == "posttooluse":
        return cmd_posttooluse()
    if mode == "check":
        return cmd_check(argv[2:])
    sys.stderr.write("usage: tests_guard.py [posttooluse|check <files...>]\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
