#!/usr/bin/env python
"""Hook Claude Code (PostToolUse) — passe l'issue Linear de la feature en cours
« Todo → En cours » dès la 1re edition de code.

Genere par /assembleur:assembleur-amorce dans <repo>/.claude/hooks/linear-start.py.
Cable via <repo>/.claude/settings.json (matcher Edit|Write|MultiEdit).

INVARIANTS (ne pas casser) :
- FAIL-SAFE : ne bloque JAMAIS l'edition. Quoi qu'il arrive -> exit 0.
- SECRET : la cle LINEAR_API_KEY est lue depuis .env, JAMAIS affichee/loguee.
- IDEMPOTENT : seul le 1er edit par issue touche le reseau (cache local d'abord).
- DETERMINISTE : aucune dependance externe (stdlib only : urllib).

Resolution de l'issue active :
  branche git -> identifiant Linear (ENG-123) ou feature:<id> -> .claude/linear-map.json
  (ecrit par init-linear : [{feature, id, identifier, url, branch_slug}]).
"""
import sys, os, json, re, subprocess, urllib.request, urllib.error

API = "https://api.linear.app/graphql"
LINEAR_ID_RE = re.compile(r"\b([A-Za-z][A-Za-z0-9]*-\d+)\b")  # ex. ENG-123
FEATURE_RE = re.compile(r"feature[:/-](\d{3,})")               # ex. feature:001 / feature-001


# ---------- fonctions pures (testables) ----------
def parse_env(text):
    """Parse un .env minimal -> dict. Ignore commentaires et lignes vides."""
    out = {}
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k, v = s.split("=", 1)
        out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def resolve_issue(branch, mapping):
    """Trouve l'entree {feature,id,identifier,...} correspondant a la branche git.
    Ordre : identifiant Linear exact > feature:<id> > branch_slug > id Linear brut (regex)."""
    if not branch:
        return None
    b = branch.lower()
    by_ident = {(e.get("identifier") or "").lower(): e for e in mapping if e.get("identifier")}
    # 1) identifiant Linear present dans la branche (ENG-123)
    for m in LINEAR_ID_RE.findall(branch):
        e = by_ident.get(m.lower())
        if e:
            return e
    # 2) feature:<id> dans la branche
    fm = FEATURE_RE.search(b)
    if fm:
        fid = fm.group(1)
        for e in mapping:
            if str(e.get("feature")) == fid:
                return e
    # 3) branch_slug connu present dans la branche
    for e in mapping:
        slug = (e.get("branch_slug") or "").lower()
        if slug and slug in b:
            return e
    # 4) repli : identifiant Linear brut meme absent du map (l'API accepte la forme courte)
    raw = LINEAR_ID_RE.findall(branch)
    if raw:
        return {"feature": None, "id": raw[0], "identifier": raw[0], "url": None}
    return None


def pick_started_state(states):
    """Choisit l'etat « En cours ». Une equipe peut avoir PLUSIEURS etats type `started`
    (ex. « In Progress » ET « In Review »). On prefere « In Progress »/« En cours », sinon le
    `started` de plus petite `position` (le plus a gauche = travail commence) — JAMAIS « In Review ».
    Repli : 1er etat ni unstarted/backlog/fini, par position."""
    started = sorted([s for s in states if s.get("type") == "started"],
                     key=lambda s: s.get("position", 0))
    if started:
        for s in started:
            n = (s.get("name") or "").lower()
            if "progress" in n or "cours" in n:
                return s
        return started[0]
    for s in sorted(states, key=lambda s: s.get("position", 0)):
        if s.get("type") not in ("backlog", "unstarted", "completed", "canceled", "triage"):
            return s
    return None


# ---------- I/O (non testee directement ; toujours exit 0) ----------
def _gql(key, query, variables=None):
    body = json.dumps({"query": query, "variables": variables or {}}).encode()
    req = urllib.request.Request(API, data=body,
                                 headers={"Authorization": key, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=8) as r:
        data = json.loads(r.read())
    if data.get("errors"):
        raise RuntimeError("graphql error")
    return data["data"]


def _read_json(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def main():
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except Exception:
        payload = {}
    root = payload.get("cwd") or os.getcwd()
    claude_dir = os.path.join(root, ".claude")

    try:
        with open(os.path.join(root, ".env"), encoding="utf-8") as f:
            env = parse_env(f.read())
    except Exception:
        env = {}
    key = env.get("LINEAR_API_KEY")
    if not key or not key.startswith("lin_"):
        return  # pas de cle -> silencieux

    mapping = _read_json(os.path.join(claude_dir, "linear-map.json"), [])
    if not isinstance(mapping, list):
        mapping = []

    branch = ""
    # symbolic-ref marche AUSSI sur une branche non-nee (repo sans commit) ; rev-parse echoue (exit 128).
    for _cmd in (["git", "symbolic-ref", "--quiet", "--short", "HEAD"],
                 ["git", "rev-parse", "--abbrev-ref", "HEAD"]):
        try:
            branch = subprocess.check_output(_cmd, cwd=root, stderr=subprocess.DEVNULL, timeout=5).decode().strip()
            if branch and branch != "HEAD":
                break
        except Exception:
            continue

    issue = resolve_issue(branch, mapping)
    if not issue:
        return  # rien a faire

    issue_id = issue.get("id")
    cache_path = os.path.join(claude_dir, ".linear-started.json")
    started = _read_json(cache_path, [])
    if not isinstance(started, list):
        started = []
    if issue_id in started:
        return  # deja passe en cours (court-circuit, aucun reseau)

    try:
        # etat courant + team de l'issue
        d = _gql(key, "query($id:String!){ issue(id:$id){ id identifier team{ id } state{ type } } }",
                 {"id": issue_id})
        iss = d.get("issue") or {}
        cur = (iss.get("state") or {}).get("type")
        if cur in ("started", "completed", "canceled"):
            started.append(issue_id)
            _write_cache(cache_path, started)
            return
        team_id = (iss.get("team") or {}).get("id")
        sd = _gql(key, "query($t:String!){ team(id:$t){ states{ nodes{ id name type position } } } }",
                  {"t": team_id})
        states = ((sd.get("team") or {}).get("states") or {}).get("nodes") or []
        target = pick_started_state(states)
        if not target:
            return
        _gql(key, "mutation($id:String!,$s:String!){ issueUpdate(id:$id, input:{stateId:$s}){ success } }",
             {"id": issue_id, "s": target["id"]})
        started.append(issue_id)
        _write_cache(cache_path, started)
        ident = iss.get("identifier") or issue.get("identifier") or issue_id
        print(f"[linear] {ident} -> En cours")  # confirmation breve, jamais la cle
    except Exception:
        return  # toute erreur reseau/API -> silencieux, on ne bloque rien


def _write_cache(path, data):
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


if __name__ == "__main__":
    try:
        main()
    finally:
        sys.exit(0)  # FAIL-SAFE : ne bloque jamais l'edition
