#!/usr/bin/env python
"""Hook PostToolUse (Write|Edit) — sync tasks.md SpecKit -> Linear (declencheur, best-effort).

A chaque ecriture/edition d'un `specs/<feature>/tasks.md`, verifie que chaque **phase** du fichier
(`## Phase N:`) a bien un sous-ticket `Task` deja consigne pour cette feature dans le manifeste
(`linear.issues[].sub_issues[].phase`). S'il en manque, POUSSE l'agent (message `decision:block`) a
lancer `/assembleur:creation-task-linear`, qui — cote agent, avec le MCP — verifie sur Linear et cree
les sous-tickets manquants (label `Task`, en Backlog, rattaches au ticket `Feature`).

Le hook NE PARLE JAMAIS a Linear (un hook `command` n'a pas acces au MCP) et ne touche a rien : il
detecte une derive et declenche le skill. Toujours exit 0 (ne casse jamais un Write) ; ne parle que
s'il manque quelque chose (silencieux si tout est deja couvert, ou si le fichier n'est pas un tasks.md).

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


def _created_phases(issue):
    out = set()
    for sub in issue.get("sub_issues") or []:
        if not isinstance(sub, dict):
            continue
        ph = sub.get("phase")
        created = (sub.get("status") or "created").lower() == "created" and (
            sub.get("issue_id") or sub.get("identifier"))
        if ph is not None and created:
            try:
                out.add(int(ph))
            except (TypeError, ValueError):
                pass
    return out


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

    missing = sorted(phases - _created_phases(issue))
    if not missing:
        return 0  # deja synchronise — silencieux

    phases_txt = ", ".join(f"Phase {n}" for n in missing)
    return _block(
        f"Le tasks.md de la feature '{feature_dir}' a change : {len(missing)} phase(s) sans sous-ticket "
        f"Task Linear ({phases_txt}). Lance /assembleur:creation-task-linear pour creer les sous-tickets "
        f"manquants (label Task, en Backlog, rattaches au ticket Feature). Le hook ne touche pas Linear "
        f"et ne modifie pas les sous-tickets deja existants."
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
