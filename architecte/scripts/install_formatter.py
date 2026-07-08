#!/usr/bin/env python
"""Installe l'outil de formatage/lint retenu a l'Etape 4 (best-effort, sans admin, non bloquant).

- python        -> `pip install ruff`  (repli `--user` si l'install systeme echoue)
- ts-js-biome   -> `npm install --save-dev @biomejs/biome`  (cree package.json via `npm init -y` si absent)
- ts-js-eslint  -> `npm install --save-dev eslint prettier`  (idem)

Idempotent : saute si l'outil est deja present. **Non bloquant** : si le gestionnaire (pip/npm) est
absent ou si l'install echoue, on avertit et on sort 0 -- l'equipe installera a la main. Aucun droit
admin requis (pip `--user` en repli ; npm en local, jamais `-g`).

Usage: python install_formatter.py <racine> <python|ts-js-biome|ts-js-eslint> [--dry-run]
"""
import os
import shutil
import subprocess
import sys

TIMEOUT = 300


def _run(cmd, cwd, dry, label):
    line = " ".join(cmd)
    if dry:
        print(f"DRY-RUN: {line}  (cwd={cwd})")
        return 0
    try:
        r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=TIMEOUT)
    except (OSError, subprocess.TimeoutExpired) as exc:
        print(f"ATTENTION: {label} impossible ({exc}) -- ignore (non bloquant).", file=sys.stderr)
        return None
    if r.returncode != 0:
        print(f"ATTENTION: `{line}` a echoue (code {r.returncode}) -- non bloquant.\n"
              f"{(r.stderr or '').strip()[:400]}", file=sys.stderr)
        return r.returncode
    return 0


def _install_python(root, dry):
    if shutil.which("ruff"):
        print("ruff deja installe -> rien a faire.")
        return 0
    base = [sys.executable, "-m", "pip", "install"]
    rc = _run(base + ["ruff"], root, dry, "install ruff")
    if dry:
        return 0
    if rc != 0:  # repli sans admin
        rc = _run(base + ["--user", "ruff"], root, dry, "install ruff --user")
    print("ruff installe." if rc == 0 else "ruff NON installe (a faire a la main : pip install ruff).")
    return 0


def _install_npm(root, key, dry):
    pkgs = ["@biomejs/biome"] if key == "ts-js-biome" else ["eslint", "prettier"]
    binname = "biome" if key == "ts-js-biome" else "eslint"
    binp = os.path.join(root, "node_modules", ".bin", binname)
    if os.path.isfile(binp) or os.path.isfile(binp + ".cmd"):
        print(f"{binname} deja installe (node_modules) -> rien a faire.")
        return 0
    npm = shutil.which("npm")
    if not npm:
        print("npm introuvable -> installation ignoree (non bloquant). Installe Node/npm puis relance.",
              file=sys.stderr)
        return 0
    # `npm install --save-dev` exige un package.json : le creer si absent (non destructif).
    if not os.path.isfile(os.path.join(root, "package.json")):
        _run([npm, "init", "-y"], root, dry, "npm init")
    rc = _run([npm, "install", "--save-dev", *pkgs], root, dry, f"install {', '.join(pkgs)}")
    if not dry:
        print(f"{binname} installe." if rc == 0 else f"{binname} NON installe (a faire a la main).")
    return 0


def main(argv):
    dry = "--dry-run" in argv
    pos = [a for a in argv[1:] if not a.startswith("--")]
    if len(pos) < 2:
        print("usage: install_formatter.py <racine> <python|ts-js-biome|ts-js-eslint> [--dry-run]",
              file=sys.stderr)
        return 2
    root, key = os.path.abspath(pos[0]), pos[1]
    if not os.path.isdir(root):
        print(f"ERREUR: racine introuvable: {root}", file=sys.stderr)
        return 2
    if key == "python":
        return _install_python(root, dry)
    if key in ("ts-js-biome", "ts-js-eslint"):
        return _install_npm(root, key, dry)
    print(f"ERREUR: cle inconnue: {key} (attendu python|ts-js-biome|ts-js-eslint)", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
