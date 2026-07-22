#!/usr/bin/env python
"""Hook PostToolUse (Write|Edit) - sync tasks.md SpecKit -> Linear (declencheur, best-effort).

A chaque ecriture/edition d'un `specs/<feature>/tasks.md`, si le fichier contient des **phases**
(`## Phase N:`), POUSSE l'agent (message `decision:block`) a lancer `/assembleur:creation-tasks-linear`,
qui - cote agent, avec le MCP - **verifie sur Linear** (par `parentId` du ticket Feature) et cree les
sous-tickets `Task` manquants (label `Task`, Backlog, rattaches au ticket Feature).

**Les tickets et l'etat d'avancement vivent DANS Linear, jamais dans le manifeste committe** (pas de
conflit de merge multi-dev). Le hook n'a pas acces au MCP ; il ne peut donc rien lire de Linear. Il
lit seulement :
  - le manifeste committe pour savoir si le pont Linear est CONFIGURE (bloc `linear` avec `team`,
    pose une fois par premier-alimente-linear) - jamais une carte de tickets ;
  - un **marqueur de debounce PAR DEV**, git-ignore (`.factory/linear/tasks-hook-seen.json`), pour ne
    pousser qu'une fois par jeu de phases et ne pas re-harceler a chaque edition. Ce marqueur est
    NON autoritatif et regenerable - l'autorite d'idempotence reste **Linear** (interrogee par le skill).

**Une phase deja possedee par un ticket de maintenance n'est jamais poussee.** Quand une anomalie ou une
evolution fait regenerer tasks.md, la phase creee nomme son ticket proprietaire dans son titre
(`## Phase 7: Evolution RAG-12 - ...`). Ce travail est deja suivi par RAG-12 : pousser a creer un
sous-ticket Task produirait un doublon, frere du ticket d'origine sous la meme Feature, avec deux
etats a synchroniser. Ces phases sont donc filtrees ici (cf. OWNED_PHASE_RE).

Le hook NE PARLE JAMAIS a Linear et n'ecrit jamais le manifeste. Toujours exit 0 (ne casse jamais un
Write) ; silencieux si le fichier n'est pas un tasks.md, s'il n'a pas de phases a synchroniser (aucune,
ou toutes deja possedees), ou si ses phases ont deja ete signalees.

Usage : hook PostToolUse. Lit le JSON du tool sur stdin.
    python tasks_linear_hook.py posttooluse
"""
import json
import os
import re
import sys

TASKS_RE = re.compile(r"(^|[\\/])specs[\\/]([^\\/]+)[\\/]tasks\.md$", re.IGNORECASE)
PHASE_RE = re.compile(r"^##\s+Phase\s+(\d+)\s*:(.*)$", re.IGNORECASE | re.MULTILINE)

# Phase DEJA POSSEDEE par un ticket de maintenance (anomalie / evolution). Le titre nomme son
# proprietaire, ex. `## Phase 7: Evolution RAG-12 - Ingestion des pieces PNG`. Une telle phase
# est deja suivie : ne jamais pousser a creer un sous-ticket Task pour elle (ce serait un
# doublon, frere du ticket d'origine sous la meme Feature, avec deux etats a synchroniser).
# Le mot litteral Evolution/Anomalie est OBLIGATOIRE avant l'identifiant : un motif large
# `[A-Z]+-\d+` matcherait FR-006, ADR-010, SC-001, TC-001 et ferait disparaitre en silence
# les tickets de phases de fabrication normales.
OWNED_PHASE_RE = re.compile(
    r"^\s*(?:Évolution|Evolution|Anomalie)\s+([A-Za-z][A-Za-z0-9]*-\d+)\b", re.IGNORECASE
)


def _manifest_path(root):
    p = os.path.join(root, "manifest.json")
    return p if os.path.isfile(p) else os.path.join(root, "cadrage-out", "manifest.json")


def _feature_dir(path):
    """Renvoie le dossier de feature (ex. '001-recherche') d'un chemin specs/<dir>/tasks.md, sinon None."""
    m = TASKS_RE.search(path.replace("\\", "/"))
    return m.group(2) if m else None


def _feature_id(feature_dir):  # conserve pour compat (plus utilise par le nudge)
    """Prefixe numerique NNN du dossier feature (ex. '001' pour '001-recherche'), sinon le dossier entier."""
    m = re.match(r"(\d+)\b", feature_dir)
    return m.group(1) if m else feature_dir


def _phases_in_file(tasks_path):
    """Numeros des phases A SYNCHRONISER : les phases deja possedees par un ticket de maintenance
    (titre `Evolution <id> -` / `Anomalie <id> -`) sont exclues - leur travail est deja suivi."""
    try:
        text = open(tasks_path, encoding="utf-8").read()
    except OSError:
        return set()
    return {
        int(n) for n, titre in PHASE_RE.findall(text) if not OWNED_PHASE_RE.match(titre)
    }


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
        return 0  # pas encore de phases (tasks.md en cours de generation) - rien a synchroniser

    root = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    try:
        manifest = json.load(open(_manifest_path(root), encoding="utf-8-sig"))
    except (OSError, ValueError):
        manifest = {}

    linear = manifest.get("linear")
    if not isinstance(linear, dict) or not linear.get("team"):
        return _block(
            f"Le fichier tasks.md de la feature '{feature_dir}' a change, mais le pont Linear n'est pas "
            f"encore configure. Lance /assembleur:premier-alimente-linear (tickets Feature) puis "
            f"/assembleur:creation-tasks-linear pour creer les sous-tickets Task (un par phase, label Task, "
            f"en Backlog, rattaches au ticket Feature)."
        )

    # Debounce PAR DEV (git-ignore) : ne pousser que pour des phases pas encore signalees. L'autorite
    # d'idempotence reste Linear (le skill interroge Linear par parentId) ; ce marqueur evite juste de
    # re-harceler a chaque edition et n'est jamais committe.
    seen = _load_seen(root)
    already = set(seen.get(feature_dir) or [])
    fresh = sorted(phases - already)
    if not fresh:
        return 0  # phases deja signalees - silencieux

    seen[feature_dir] = sorted(already | phases)
    _save_seen(root, seen)
    phases_txt = ", ".join(f"Phase {n}" for n in fresh)
    return _block(
        f"Le tasks.md de la feature '{feature_dir}' a change : {len(fresh)} phase(s) a synchroniser vers "
        f"Linear ({phases_txt}). Lance /assembleur:creation-tasks-linear - il verifie sur Linear (par "
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
