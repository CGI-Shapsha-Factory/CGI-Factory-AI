#!/usr/bin/env python
"""Hook Claude Code PostToolUse : formate un fichier Python edite via `ruff format`.

Pourquoi ce hook : Claude Code (Write/Edit) ne lit PAS `.editorconfig` ; et `ruff` non plus. Ce hook
fait le pont. Deux sources de preferences, dans l'ordre :
  1. **Fichier de config ruff dedie** s'il existe (`ruff.toml`/`.ruff.toml`, ou l'emplacement Factory
     `conventions/ruff.toml` / `conventions/python/ruff.toml`) -> `ruff format --config <fichier>`.
     C'est la source COMPLETE des preferences du formateur (quote-style, line-ending, magic comma…).
  2. **Sinon**, `.editorconfig` applicable (recherche ascendante + fallback `conventions/`, arret sur
     `root = true`, sections en glob) traduit en options `ruff format --config` (les 4 reglages de base).

Focus Python (`.py`/`.pyi`) pour l'instant (extensible : ajouter d'autres extensions + formateurs).

Garde-fous (lecons apprises) :
  - JAMAIS bloquant : exit 0 quoi qu'il arrive (un formateur ne doit pas casser la session).
  - Chemins ABSOLUS, robuste au cwd (le hook peut tourner depuis n'importe ou).
  - Best-effort sur l'outil : `ruff` sur le PATH, sinon `python -m ruff`, sinon `uvx ruff` ; si rien,
    on avertit une fois et on sort proprement.
  - Reglages `.editorconfig` -> ruff : max_line_length->line-length, indent_size->indent-width,
    indent_style->format.indent-style, end_of_line(lf|crlf)->format.line-ending. Les autres
    (trim_trailing_whitespace, insert_final_newline, charset) sont deja garantis par ruff format.

Usage (hook) : reçoit le JSON PostToolUse sur stdin ; utilise `tool_input.file_path`.
"""
import json
import os
import re
import shutil
import subprocess
import sys

PY_EXTS = (".py", ".pyi")


def _stdin_path():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return ""
    return (data.get("tool_input") or {}).get("file_path", "") or ""


def _is_root_editorconfig(path):
    """True si le fichier declare `root = true` (avant toute section)."""
    try:
        with open(path, encoding="utf-8-sig") as f:
            for line in f:
                s = line.strip()
                if not s or s.startswith(("#", ";")):
                    continue
                if s.startswith("["):
                    return False
                if "=" in s:
                    k, v = (x.strip().lower() for x in s.split("=", 1))
                    if k == "root":
                        return v == "true"
    except OSError:
        pass
    return False


def _editorconfig_chain(start_dir):
    """Liste des `.editorconfig` du plus HAUT au plus PROCHE (le proche override), arret sur root.

    A chaque niveau on regarde `<dir>/.editorconfig` (emplacement standard) ET
    `<dir>/conventions/.editorconfig` (emplacement de la Factory — `architecte-init` y range le socle,
    or la decouverte editorconfig ne fouille QUE les dossiers ancetres, pas un sous-dossier).
    """
    chain = []
    d = os.path.abspath(start_dir)
    while True:
        for p in (os.path.join(d, ".editorconfig"), os.path.join(d, "conventions", ".editorconfig")):
            if os.path.isfile(p):
                chain.append(p)
                if _is_root_editorconfig(p):
                    return list(reversed(chain))
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    return list(reversed(chain))


def _expand_braces(pat):
    m = re.search(r"\{([^}]*)\}", pat)
    if not m:
        return [pat]
    pre, mid, post = pat[: m.start()], m.group(1).split(","), pat[m.end():]
    out = []
    for opt in mid:
        out.extend(_expand_braces(pre + opt + post))
    return out


def _section_matches(section, filename):
    import fnmatch
    return any(fnmatch.fnmatch(filename, pat) for pat in _expand_braces(section))


def _editorconfig_props(file_path):
    """Proprietes `.editorconfig` resolues pour ce fichier (basename), sections fusionnees."""
    props = {}
    filename = os.path.basename(file_path)
    for ec in _editorconfig_chain(os.path.dirname(os.path.abspath(file_path))):
        matching = False
        try:
            with open(ec, encoding="utf-8-sig") as f:
                for line in f:
                    s = line.strip()
                    if not s or s.startswith(("#", ";")):
                        continue
                    if s.startswith("[") and s.endswith("]"):
                        matching = _section_matches(s[1:-1], filename)
                        continue
                    if "=" not in s:
                        continue
                    key, val = (x.strip() for x in s.split("=", 1))
                    if matching:
                        props[key.lower()] = val.lower()
        except OSError:
            continue
    return props


def _ruff_config_args(props):
    args = []
    ll = props.get("max_line_length", "")
    if ll.isdigit():
        args += ["--config", f"line-length={int(ll)}"]
    iw = props.get("indent_size", "")
    if iw.isdigit():
        args += ["--config", f"indent-width={int(iw)}"]
    style = props.get("indent_style")
    if style in ("space", "tab"):
        args += ["--config", f"format.indent-style='{style}'"]
    eol = {"lf": "lf", "crlf": "crlf"}.get(props.get("end_of_line", ""))
    if eol:
        args += ["--config", f"format.line-ending='{eol}'"]
    return args


def _find_ruff_config(start_dir):
    """Cherche un fichier de config ruff dans les dossiers ancetres.

    Priorite (par dossier, du plus proche au plus haut) : `ruff.toml` / `.ruff.toml` (config du
    projet, auto-decouverte par ruff) puis `conventions/ruff.toml` / `conventions/python/ruff.toml`
    (emplacement de la Factory, que ruff ne trouve PAS seul). Renvoie le chemin, ou None.

    Ce fichier porte les preferences COMPLETES du formateur (quote-style, magic trailing comma,
    line-ending, docstring, etc.) — bien plus riches que les 4 reglages de `.editorconfig`.
    """
    d = os.path.abspath(start_dir)
    while True:
        for cand in ("ruff.toml", ".ruff.toml",
                     os.path.join("conventions", "ruff.toml"),
                     os.path.join("conventions", "python", "ruff.toml")):
            p = os.path.join(d, cand)
            if os.path.isfile(p):
                return p
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent


def _ruff_candidates():
    cands = []
    if shutil.which("ruff"):
        cands.append(["ruff"])
    try:
        import importlib.util
        if importlib.util.find_spec("ruff") is not None:
            cands.append([sys.executable, "-m", "ruff"])
    except (ImportError, ValueError):
        pass
    if shutil.which("uvx"):
        cands.append(["uvx", "ruff"])
    return cands


def main():
    path = _stdin_path()
    if not path or os.path.splitext(path)[1] not in PY_EXTS:
        return 0
    path = os.path.abspath(path)
    if not os.path.isfile(path):
        return 0

    # 1) Config ruff dediee si presente (preferences completes) ; 2) sinon, derive de `.editorconfig`.
    cfg = _find_ruff_config(os.path.dirname(path))
    args = ["--config", cfg] if cfg else _ruff_config_args(_editorconfig_props(path))
    for cand in _ruff_candidates():
        try:
            # --no-cache : ne pas polluer le projet avec un dossier `.ruff_cache`.
            r = subprocess.run(cand + ["format", "--no-cache", *args, path],
                               capture_output=True, text=True)
        except OSError:
            continue
        # ruff a tourne (succes OU erreur de syntaxe) -> on ne bloque pas, on ne reessaie pas.
        return 0

    sys.stderr.write(
        "format_guard: ruff introuvable — formatage Python ignore "
        "(installe-le : `uv tool install ruff` ou `pip install ruff`).\n"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
