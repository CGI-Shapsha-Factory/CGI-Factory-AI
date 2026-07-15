#!/usr/bin/env python
"""Hook PostToolUse (Write|Edit) — sync tasks.md SpecKit -> Linear (declencheur, best-effort).

A chaque ecriture/edition d'un `specs/<feature>/tasks.md`, si le fichier contient des **phases**
(`## Phase N:`), POUSSE l'agent (message `decision:block`) a lancer `/assembleur:creation-task-linear`,
qui — cote agent, avec le MCP — **verifie sur Linear** (par `parentId` du ticket Feature) et cree les
sous-tickets `Task` manquants (label `Task`, Backlog, rattaches au ticket Feature).

**L'etat d'avancement vit DANS Linear, jamais dans le manifeste committe** (pas de conflit de merge
multi-dev). Le hook n'a pas acces au MCP ; il ne peut donc pas lire l'etat Linear. Il lit seulement :
  - le manifeste committe pour savoir si un **ticket Feature** existe pour la feature (carte amont figee,
    posee une fois par premier-alimente-linear — donnee single-owner, jamais un etat de dev mutant) ;
  - un **marqueur de debounce PAR DEV**, git-ignore (`.factory/linear/tasks-hook-seen.json`), pour ne
    pousser qu'une fois par jeu de phases et ne pas re-harceler a chaque edition. Ce marqueur est
    NON autoritatif et regenerable — l'autorite d'idempotence reste **Linear** (interrogee par le skill).

Le hook NE PARLE JAMAIS a Linear et n'ecrit jamais le manifeste. Toujours exit 0 (ne casse jamais un
Write) ; silencieux si le fichier n'est pas un tasks.md, s'il n'a pas de phases, ou si ses phases ont
deja ete signalees.

Usage : hook PostToolUse. Lit le JSON du tool sur stdin.
    python tasks_linear_hook.py posttooluse
"""
import json
import os
import re
import sys

TASKS_RE = re.compile(r"(^|[\\/])specs[\\/]([^\\/]+)[\\/]tasks\.md$", re.IGNORECASE)
PHASE_RE = re.compile(r"^##\s+Phase\s+(\d+)\s*:", re.IGNORECASE | re.MULTILINE)


def _manifest_path(root):
    p = os.path.join(root, "manifest.json")
    return p if os.path.isfile(p) else os.path.join(root, "cadrage-out", "manifest.json")


def _feature_dir(path):
    """Renvoie le dossier de feature (ex. '001-recherche') d'un chemin specs/<dir>/tasks.md, sinon None."""
    m = TASKS_RE.search(path.replace("\\", "/"))
    return m.group(2) if m else None


def _feature_id(feature_dir):
    """Prefixe numerique NNN du dossier feature (ex. '001' pour '001-recherche'), sinon le dossier entier."""
    m = re.match(r"(\d+)\b", feature_dir)
    return m.group(1) if m else feature_dir


def _phases_in_file(tasks_path):
    try:
        text = open(tasks_path, encoding="utf-8").read()
    except OSError:
        return set()
    return {int(n) for n in PHASE_RE.findall(text)}


def _seen_path(root):
    return os.path.join(root, ".factory", "linear", "tasks-hook-seen.json")


def _load_seen(root):
    """Marqueur de debounce PAR DEV, git-ignore, NON autoritatif : {feature_dir: [phases signalees]}."""
    try:
        with open(_seen_path(root), encoding="utf-8") as f:
            return json.load(f) or {}
    except (OSError, ValueError):
        return {}


def _save_seen(root, data):
    try:
        os.makedirs(os.path.dirname(_seen_path(root)), exist_ok=True)
        with open(_seen_path(root), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except OSError:
        pass  # best-effort : le marqueur est regenerable, ne jamais casser un Write


def _find_issue(linear, fid, feature_dir):
    for it in linear.get("issues") or []:
        if not isinstance(it, dict):
            continue
        if str(it.get("id")) == str(fid):
            return it
    # repli : matcher par nom de dossier (NNN-...) sur le nom de la feature
    for it in linear.get("issues") or []:
        if isinstance(it, dict) and feature_dir and feature_dir.lower() in str(it.get("name", "")).lower():
            return it
    return None


def _block(reason):
    print(json.dumps({"decision": "block", "reason": reason}, ensure_ascii=False))
    return 0


def cmd_posttooluse():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0
    path = (data.get("tool_input") or {}).get("file_path", "") or ""
    feature_dir = _feature_dir(path)
    if not feature_dir:
        return 0  # pas un specs/<feature>/tasks.md

    phases = _phases_in_file(path)
    if not phases:
        return 0  # pas encore de phases (tasks.md en cours de generation) — rien a synchroniser

    root = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    try:
        manifest = json.load(open(_manifest_path(root), encoding="utf-8-sig"))
    except (OSError, ValueError):
        manifest = {}

    fid = _feature_id(feature_dir)
    linear = manifest.get("linear")
    if not isinstance(linear, dict) or not linear.get("issues"):
        return _block(
            f"Le fichier tasks.md de la feature '{feature_dir}' a change, mais aucun ticket Linear n'est "
            f"encore consigne. Lance /assembleur:premier-alimente-linear (ticket Feature) puis "
            f"/assembleur:creation-task-linear pour creer les sous-tickets Task (un par phase, label Task, "
            f"en Backlog, rattaches au ticket Feature)."
        )

    issue = _find_issue(linear, fid, feature_dir)
    if issue is None:
        return _block(
            f"Le tasks.md de la feature '{feature_dir}' a change, mais aucun ticket Feature Linear ne lui "
            f"correspond. Lance /assembleur:creation-task-linear (il verifiera le rattachement au ticket Feature)."
        )

    # Debounce PAR DEV (git-ignore) : ne pousser que pour des phases pas encore signalees. L'autorite
    # d'idempotence reste Linear (le skill interroge Linear par parentId) ; ce marqueur evite juste de
    # re-harceler a chaque edition et n'est jamais committe.
    seen = _load_seen(root)
    already = set(seen.get(feature_dir) or [])
    fresh = sorted(phases - already)
    if not fresh:
        return 0  # phases deja signalees — silencieux

    seen[feature_dir] = sorted(already | phases)
    _save_seen(root, seen)
    phases_txt = ", ".join(f"Phase {n}" for n in fresh)
    return _block(
        f"Le tasks.md de la feature '{feature_dir}' a change : {len(fresh)} phase(s) a synchroniser vers "
        f"Linear ({phases_txt}). Lance /assembleur:creation-task-linear — il verifie sur Linear (par "
        f"parentId) et cree uniquement les sous-tickets Task manquants (label Task, Backlog, rattaches au "
        f"ticket Feature). L'avancement vit dans Linear, pas dans le manifeste committe."
    )


def main(argv):
    mode = argv[1] if len(argv) > 1 else "posttooluse"
    if mode == "posttooluse":
        return cmd_posttooluse()
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except Exception:  # noqa: BLE001 - best-effort : ne jamais casser un Write
        sys.exit(0)
