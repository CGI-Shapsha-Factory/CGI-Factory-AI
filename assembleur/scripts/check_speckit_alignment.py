#!/usr/bin/env python
"""Garde-fou d'alignement SpecKit <-> registre canonique de features (anti-collision multi-dev).

Le numero de feature (`NNN`) est **propose** par l'architecte puis **finalise et fige par l'assembleur**
(arbitrage split/merge dans `assembleur-convergence`, gel a l'init Linear) dans le manifeste committe
(`architecture.feature_sequence[].id`, `id` = `001, 002, ...`). SpecKit, lui, auto-incremente `NNN`
en scannant l'etat local ; sans garde-fou, deux developpeurs partis de `main` en parallele produisent
tous deux `specs/003-...` -> collision au merge. Ce script verifie que chaque `specs/NNN-slug/` du repo
de fabrication reste aligne sur le registre canonique, et ECHOUE FERME sur une derive.

Deux modes (comme `tests_guard.py`) :
  - `check`       : scan complet de `specs/` (pre-commit / CI / manuel). Exit 1 si collision/derive.
  - `posttooluse` : hook Claude Code (Write|Edit). Lit le JSON de l'outil sur stdin ; si le fichier
                    edite est sous `specs/<dir>/`, evalue CE dossier et emet `{"decision":"block",
                    "reason": ...}` (exit 0) si le numero est en collision / timestamp / hors registre —
                    pour pousser l'agent a recreer avec `SPECIFY_FEATURE_DIRECTORY=specs/NNN-slug`.

Verifications (contre `specs/*/`) :
  1. Registre fige (`architecture.feature_sequence` non vide) — sinon ECHEC en mode `check`
     (« registre canonique non fige ») ; en `posttooluse` on saute le controle « numero inconnu »
     pour ne pas harceler pendant l'amorcage.
  2. Bannissement timestamp : un dossier `^\\d{8}-\\d{6}-` -> ECHEC (turn_cost.py:27 et le hook Linear
     lisent `^\\d{3}-` : la numerotation horodatee casserait l'attribution des couts et la sync Linear).
  3. Numero connu : le `NNN` de chaque `specs/NNN-...` doit appartenir au registre -> sinon ECHEC.
  4. Pas de doublon : deux dossiers pour le meme `NNN` -> ECHEC (le detecteur direct de collision).
  5. Slug divergent (dossier != slug canonique de la graine) -> AVERTISSEMENT non fatal.
  6. Dossiers manquants = OK (fabrication incrementale ; l'absence n'echoue jamais).

Manifeste : `manifest.json` a la racine (repli `cadrage-out/manifest.json` legacy) ; ancrage projet
via `CLAUDE_PROJECT_DIR` en mode hook. Slugs canoniques : basenames de
`assembleur-out/features/<id>-<slug>.md`.

Usage :
    python check_speckit_alignment.py check [racine_projet]
    python check_speckit_alignment.py posttooluse            # lit le JSON de l'outil sur stdin
"""
import json
import os
import re
import sys

TS_RE = re.compile(r"^\d{8}-\d{6}-")                 # numerotation timestamp SpecKit (interdite ici)
NUM_RE = re.compile(r"^(\d+)-")                       # prefixe NNN- d'un dossier de feature
SPEC_FILE_RE = re.compile(r"(^|/)specs/([^/]+)/", re.IGNORECASE)  # .../specs/<dir>/<fichier>


def _root(argv, mode):
    # posttooluse : ancrer sur la racine projet (le hook ne tourne pas depuis la racine) ; cf. la
    # meme regle que tasks_linear_hook.py / tests_guard.py.
    if mode == "posttooluse":
        return os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    for a in argv[2:]:  # check [racine]
        if not a.startswith("-"):
            return os.path.abspath(a)
    return os.getcwd()


def _load_manifest(root):
    p = os.path.join(root, "manifest.json")
    if not os.path.isfile(p):
        p = os.path.join(root, "cadrage-out", "manifest.json")
    try:
        with open(p, encoding="utf-8-sig") as f:  # utf-8-sig : tolere un BOM (outil Windows)
            return json.load(f) or {}
    except (OSError, ValueError):
        return {}


def _registry_ids(manifest):
    """{numero base-10: forme d'origine 'NNN'} des features figees par l'architecte."""
    seq = (manifest.get("architecture") or {}).get("feature_sequence") or []
    nums = {}
    for it in seq:
        fid = it.get("id") if isinstance(it, dict) else it
        if not fid:
            continue
        m = re.match(r"^(\d+)", str(fid))
        if m:
            nums[int(m.group(1))] = str(fid)
    return nums


def _canonical_slugs(root):
    """{numero base-10: slug canonique} depuis assembleur-out/features/<id>-<slug>.md."""
    out = {}
    fdir = os.path.join(root, "assembleur-out", "features")
    if not os.path.isdir(fdir):
        return out
    for name in os.listdir(fdir):
        m = re.match(r"^(\d+)-(.+)\.md$", name)
        if m:
            out[int(m.group(1))] = m.group(2)
    return out


def _specs_dirs(root):
    d = os.path.join(root, "specs")
    if not os.path.isdir(d):
        return []
    return sorted(n for n in os.listdir(d) if os.path.isdir(os.path.join(d, n)))


def _evaluate(dirs, ids, slugs):
    """Renvoie {dossier: (niveau, message)} pour les dossiers problematiques. niveau in {fatal, warn}.
    `ids` peut etre vide (amorcage) : on saute alors le controle « numero inconnu »."""
    by_num = {}  # groupement pour detecter les doublons (hors timestamp)
    for name in dirs:
        if TS_RE.match(name):
            continue
        m = NUM_RE.match(name)
        if m:
            by_num.setdefault(int(m.group(1)), []).append(name)

    problems = {}
    for name in dirs:
        if TS_RE.match(name):
            problems[name] = ("fatal",
                f"'specs/{name}' utilise la numerotation timestamp — le sequentiel NNN est requis "
                f"(turn_cost.py:27 et le hook Linear lisent ^\\d{{3}}-). Recree le dossier avec "
                f"SPECIFY_FEATURE_DIRECTORY=specs/NNN-slug (NNN pris dans assembleur-out/feature-map.md).")
            continue
        m = NUM_RE.match(name)
        if not m:
            continue  # dossier non numerote : ni collision, ni feature Factory -> ignore
        num = int(m.group(1))
        others = [d for d in by_num.get(num, []) if d != name]
        if others:
            keep = f"{ids.get(num, f'{num:03d}')}-slug"
            problems[name] = ("fatal",
                f"numero de feature {num:03d} en double: {', '.join(sorted([name] + others))} — deux "
                f"features ne peuvent pas partager un numero. Une seule garde specs/{keep} ; "
                f"renumerote l'autre depuis assembleur-out/feature-map.md.")
            continue
        if ids and num not in ids:
            problems[name] = ("fatal",
                f"'specs/{name}' : numero {num:03d} absent du registre canonique "
                f"(architecture.feature_sequence). Utilise un NNN de assembleur-out/feature-map.md.")
            continue
        # numero conforme : verifier le slug (derive = simple avertissement, non bloquant)
        slug = name[m.end():]
        if num in slugs and slug and slug != slugs[num]:
            problems[name] = ("warn",
                f"'specs/{name}' : slug '{slug}' != slug canonique '{slugs[num]}' "
                f"(assembleur-out/features/{ids.get(num, f'{num:03d}')}-{slugs[num]}.md). Tolere.")
    return problems


def _block(reason):
    print(json.dumps({"decision": "block", "reason": reason}, ensure_ascii=False))
    return 0


def cmd_check(root):
    manifest = _load_manifest(root)
    ids = _registry_ids(manifest)
    if not ids:
        print("ALIGNEMENT SPECKIT: registre non renseigne (architecture.feature_sequence vide) — "
              "l'architecte propose la sequence, l'assembleur la fige avant la fabrication.", file=sys.stderr)
        return 1
    slugs = _canonical_slugs(root)
    dirs = _specs_dirs(root)
    problems = _evaluate(dirs, ids, slugs)
    for name, (lvl, msg) in sorted(problems.items()):
        if lvl == "warn":
            print(f"AVERTISSEMENT: {msg}", file=sys.stderr)
    fatals = {n: m for n, (lvl, m) in problems.items() if lvl == "fatal"}
    if fatals:
        print("ALIGNEMENT SPECKIT — collisions / derives de numerotation :", file=sys.stderr)
        for name in sorted(fatals):
            print(f"  - {fatals[name]}", file=sys.stderr)
        return 1
    n = sum(1 for d in dirs if NUM_RE.match(d) and not TS_RE.match(d))
    print(f"ALIGNEMENT SPECKIT OK — {n} feature(s) sous specs/ alignee(s) sur le registre "
          f"({len(ids)} figee(s)), aucune collision.")
    return 0


def cmd_posttooluse(root):
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0
    path = (data.get("tool_input") or {}).get("file_path", "") or ""
    m = SPEC_FILE_RE.search(path.replace("\\", "/"))
    if not m:
        return 0  # pas un fichier sous specs/<dir>/
    touched = m.group(2)
    manifest = _load_manifest(root)
    ids = _registry_ids(manifest)   # peut etre vide en cours d'amorcage -> check « inconnu » saute
    slugs = _canonical_slugs(root)
    dirs = _specs_dirs(root)
    if touched not in dirs:
        dirs = dirs + [touched]     # le Write vient peut-etre de creer le dossier
    lvlmsg = _evaluate(dirs, ids, slugs).get(touched)
    if lvlmsg and lvlmsg[0] == "fatal":
        return _block(lvlmsg[1])
    return 0


def main(argv):
    mode = argv[1] if len(argv) > 1 else "check"
    root = _root(argv, mode)
    if mode == "posttooluse":
        return cmd_posttooluse(root)
    return cmd_check(root)


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except Exception:  # noqa: BLE001 - en hook, ne jamais casser un Write ; en check, remonter.
        if len(sys.argv) > 1 and sys.argv[1] == "posttooluse":
            sys.exit(0)
        raise
