#!/usr/bin/env python
"""Compteur de cout - hook Claude Code `SessionEnd` (ecriture a la FIN de session).

A la fin de chaque session, lit le transcript COMPLET, produit UN enregistrement par message assistant
(= une requete/reponse API), tarife par tier, attribue (phase amont XOR feature), et REECRIT (overwrite)
le fichier de la session .factory/couts/<aaaa-mm>/<session-id>.jsonl.

Pourquoi a la fin de session (pas par tour) : les hooks sont bloquants ; un hook par tour ralentit le dev.
`SessionEnd` tire une seule fois, a la fin -> zero latence pendant les tours. La granularite par message est
conservee (un enregistrement par message, relu du transcript complet).

Reprise de session : (1) reecriture idempotente (meme id -> fichier mis a jour depuis le transcript complet) ;
(2) chaque enregistrement porte sa cle (message.id, requestId) -> le rapport deduplique GLOBALEMENT
(reprise/fork nouvel-id qui rejoue l'historique -> compte une fois).

Best-effort : ne bloque jamais (exit 0). Cout local = ESTIMATION (simulation), pas le cout reel.
Entree : JSON stdin {transcript_path, session_id, cwd, hook_event_name, ...}.
"""
import json
import os
import re
import subprocess
import sys

SCHEMA = 3
PLUGINS = ("cadrage", "architecte", "designer", "assembleur")
BRANCH_FEATURE_RE = re.compile(r"^(\d{3})-")
SLASH_RE = re.compile(r"/(cadrage|architecte|designer|assembleur)\s*:")
SKILL_RE = re.compile(r"\b(cadrage|architecte|designer|assembleur)-[a-z\-]+", re.IGNORECASE)
TIERS = ("haiku", "sonnet", "opus", "fable")


def _log(msg):
    sys.stderr.write(f"turn_cost: {msg}\n")


def project_root(cwd_hint):
    # La copie installee du hook vit a <racine>/.claude/hooks/turn_cost.py : on ANCRE la racine sur
    # cet emplacement et on ne remonte JAMAIS. Ainsi le hook n'ecrit que dans le .factory/couts/ du
    # dossier ou il a ete installe, et ne mesure que les sessions lancees dans ce dossier.
    d = os.path.dirname(os.path.abspath(__file__))
    if os.path.basename(d) == "hooks" and os.path.basename(os.path.dirname(d)) == ".claude":
        return os.path.dirname(os.path.dirname(d))
    # Repli (execution hors installation, ex. tests depuis le plugin) : recherche ascendante.
    cur = os.path.abspath(os.environ.get("CLAUDE_PROJECT_DIR") or cwd_hint or os.getcwd())
    for _ in range(6):
        if os.path.isdir(os.path.join(cur, ".factory")):
            return cur
        parent = os.path.dirname(cur)
        if parent == cur:
            break
        cur = parent
    return os.path.abspath(cwd_hint or os.getcwd())


def load_price_table(root):
    try:
        return json.load(open(os.path.join(root, ".factory", "couts", "price-table.json"), encoding="utf-8"))
    except (OSError, ValueError):
        return None


def resolve_prices(model, table):
    if not table:
        return None, None
    ov = (table.get("overrides") or {}).get(model)
    tiers = table.get("tiers") or {}
    tier = next((t for t in TIERS if t in (model or "")), None)
    if ov:
        return (tier or model), ov
    if tier and tier in tiers:
        return tier, tiers[tier]
    return None, None


def cats_of(u):
    cc = u.get("cache_creation")
    if isinstance(cc, dict):
        w5 = cc.get("ephemeral_5m_input_tokens", 0) or 0
        w1 = cc.get("ephemeral_1h_input_tokens", 0) or 0
    else:
        w5 = u.get("cache_creation_input_tokens", 0) or 0
        w1 = 0
    return {"input": u.get("input_tokens", 0) or 0, "output": u.get("output_tokens", 0) or 0,
            "cache_read": u.get("cache_read_input_tokens", 0) or 0,
            "cache_write_5m": w5, "cache_write_1h": w1}


def cost_of(cats, prices, mult_1h):
    return round(cats["input"] * prices["input"]
                 + cats["output"] * prices["output"]
                 + cats["cache_read"] * prices["cache_read"]
                 + cats["cache_write_5m"] * prices["cache_write_5m"]
                 + cats["cache_write_1h"] * (prices["input"] * mult_1h), 8)


def collect_messages(raw_lines):
    """{(id,req): {model, usage, out, ts, branch}} en gardant la DERNIERE/max valeur (dedup streaming)."""
    seen = {}
    for raw in raw_lines:
        raw = raw.strip()
        if not raw:
            continue
        try:
            obj = json.loads(raw)
        except ValueError:
            continue
        if obj.get("type") != "assistant":
            continue
        msg = obj.get("message") or {}
        usage = msg.get("usage")
        if not isinstance(usage, dict):
            continue
        key = (msg.get("id"), obj.get("requestId"))
        if key == (None, None):
            key = (obj.get("uuid"), None)
        out = usage.get("output_tokens", 0) or 0
        prev = seen.get(key)
        if prev is None or out >= prev["out"]:
            seen[key] = {"model": msg.get("model") or "unknown", "usage": usage, "out": out,
                         "ts": obj.get("timestamp"), "branch": obj.get("gitBranch")}
    return seen


def load_feature_name(root, fid):
    try:
        mpath = os.path.join(root, "manifest.json")
        if not os.path.isfile(mpath):  # repli legacy cadrage-out/
            mpath = os.path.join(root, "cadrage-out", "manifest.json")
        man = json.load(open(mpath, encoding="utf-8"))
        for it in (man.get("architecture", {}) or {}).get("feature_sequence", []) or []:
            if str(it.get("id")) == fid:
                return it.get("name")
    except (OSError, ValueError):
        pass
    return None


def attribution(root, branch, text):
    if branch:
        m = BRANCH_FEATURE_RE.match(branch)
        if m:
            fid = m.group(1)
            return {"kind": "feature", "id": fid, "label": load_feature_name(root, fid) or fid}
    counts = {p: 0 for p in PLUGINS}
    for m in SLASH_RE.finditer(text):
        counts[m.group(1)] += 3
    for m in SKILL_RE.finditer(text):
        counts[m.group(1).lower()] += 1
    best = max(counts, key=counts.get)
    return {"kind": "phase", "label": best} if counts[best] > 0 else {"kind": "autre", "label": "autre"}


def dev_identity(root):
    try:
        out = subprocess.run(["git", "-C", root, "config", "user.email"],
                             capture_output=True, text=True, check=True)
        if out.stdout.strip():
            return out.stdout.strip()
    except (subprocess.CalledProcessError, OSError):
        pass
    return os.environ.get("USERNAME") or os.environ.get("USER") or "inconnu"


def main():
    try:
        data = json.load(sys.stdin)
    except (ValueError, OSError):
        return 0
    tpath, sid = data.get("transcript_path"), data.get("session_id") or "session"
    root = project_root(data.get("cwd"))
    if not tpath or not os.path.isfile(tpath):
        _log(f"transcript introuvable: {tpath}")
        return 0
    try:
        raw = open(tpath, encoding="utf-8").readlines()
    except OSError as exc:
        _log(f"lecture: {exc}")
        return 0

    seen = collect_messages(raw)
    if not seen:
        return 0
    table = load_price_table(root)
    mult_1h = (table or {}).get("cache_write_1h_multiplier", 2.0)
    pdate = (table or {}).get("date")
    dev = dev_identity(root)
    text = "".join(raw)

    records, last_ts = [], None
    for (mid, req), rec in seen.items():
        cats = cats_of(rec["usage"])
        tier, prices = resolve_prices(rec["model"], table)
        cost = cost_of(cats, prices, mult_1h) if prices else None
        records.append({
            "schema": SCHEMA, "session_id": sid, "key": f"{mid}:{req}", "dev": dev,
            "ts": rec["ts"], "branch": rec["branch"], "model": rec["model"], "tier": tier,
            "tokens": cats, "attribution": attribution(root, rec["branch"], text),
            "sim_cost_usd": cost, "price_table_date": pdate, "unpriced": prices is None,
        })
        if rec["ts"]:
            last_ts = rec["ts"]

    records.sort(key=lambda r: r["ts"] or "")
    month = (last_ts or "")[:7] or "0000-00"
    out_dir = os.path.join(root, ".factory", "couts", month)
    try:
        os.makedirs(out_dir, exist_ok=True)
        # REECRITURE (overwrite) : le fichier de session reflete tout le transcript (reprise idempotente)
        with open(os.path.join(out_dir, f"{sid}.jsonl"), "w", encoding="utf-8") as f:
            for r in records:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
    except OSError as exc:
        _log(f"ecriture: {exc}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
