#!/usr/bin/env python
"""Compteur de cout EN TEMPS REEL, par tour — hooks Claude Code `Stop` (+ `SessionEnd` en backstop).

Sous-commandes :
  turn       : (hook `Stop`, tire a chaque tour) lit UNIQUEMENT les nouvelles lignes du transcript
               depuis le dernier tour (curseur par session), deduplique par (message.id, requestId) en
               gardant la DERNIERE valeur, somme les 4/5 categories, tarife par TIER, et AJOUTE une
               ligne-tour dans .factory/costs/<aaaa-mm>/<session-id>.jsonl -- immediatement.
  reconcile  : (hook `SessionEnd`, backstop) recalcule le total du transcript complet et, si le journal
               de la session est en-dessous (un Stop rate), ajoute une ligne de reconciliation pour le delta.

Best-effort : ne bloque jamais la session (exit 0). Le cout local est une ESTIMATION (simulation).

Entree : JSON sur stdin {transcript_path, session_id, cwd, hook_event_name, ...}.
Deux caches : ephemeral_5m (1.25x) + ephemeral_1h (2x) tarifes separement ; cache_read (0.1x).
"""
import json
import os
import re
import subprocess
import sys

SCHEMA = 2
PLUGINS = ("cadrage", "architecte", "designer", "assembleur")
BRANCH_FEATURE_RE = re.compile(r"^(\d{3})-")
SLASH_RE = re.compile(r"/(cadrage|architecte|designer|assembleur)\s*:")
SKILL_RE = re.compile(r"\b(cadrage|architecte|designer|assembleur)-[a-z\-]+", re.IGNORECASE)
GITBRANCH_RE = re.compile(r'"gitBranch"\s*:\s*"([^"]*)"')
TIERS = ("haiku", "sonnet", "opus", "fable")


def _log(msg):
    sys.stderr.write(f"turn_cost: {msg}\n")


def project_root(cwd_hint):
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
        return json.load(open(os.path.join(root, ".factory", "cost", "price-table.json"), encoding="utf-8"))
    except (OSError, ValueError):
        return None


def resolve_prices(model, table):
    """Renvoie (tier, prices) pour un model-id, ou (None, None)."""
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


def cost_of(cats, prices, mult_1h):
    return (cats["input"] * prices["input"]
            + cats["output"] * prices["output"]
            + cats["cache_read"] * prices["cache_read"]
            + cats["cache_write_5m"] * prices["cache_write_5m"]
            + cats["cache_write_1h"] * (prices["input"] * mult_1h))


def collect_usage(raw_lines):
    """{(message.id, requestId): rec} en gardant la derniere/max valeur (dedup streaming)."""
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
            seen[key] = {"model": msg.get("model") or "unknown", "usage": usage,
                         "out": out, "ts": obj.get("timestamp")}
    return seen


def sum_by_model(seen):
    per, last_ts = {}, None
    for rec in seen.values():
        u = rec["usage"]
        d = per.setdefault(rec["model"], dict(input=0, output=0, cache_read=0,
                                              cache_write_5m=0, cache_write_1h=0))
        d["input"] += u.get("input_tokens", 0) or 0
        d["output"] += u.get("output_tokens", 0) or 0
        d["cache_read"] += u.get("cache_read_input_tokens", 0) or 0
        cc = u.get("cache_creation")
        if isinstance(cc, dict):
            d["cache_write_5m"] += cc.get("ephemeral_5m_input_tokens", 0) or 0
            d["cache_write_1h"] += cc.get("ephemeral_1h_input_tokens", 0) or 0
        else:
            d["cache_write_5m"] += u.get("cache_creation_input_tokens", 0) or 0
        if rec.get("ts"):
            last_ts = rec["ts"]
    return per, last_ts


def price_all(per_model, table):
    """(cout total, tokens totaux, modele principal, tier principal, non-tarifes)."""
    mult_1h = (table or {}).get("cache_write_1h_multiplier", 2.0)
    total_cost, unpriced = 0.0, []
    totals = dict(input=0, output=0, cache_read=0, cache_write_5m=0, cache_write_1h=0)
    best_model, best_tokens, best_tier = None, -1, None
    for model, cats in per_model.items():
        for k in totals:
            totals[k] += cats[k]
        tier, prices = resolve_prices(model, table)
        if prices:
            total_cost += cost_of(cats, prices, mult_1h)
        else:
            unpriced.append(model)
        tok = sum(cats.values())
        if tok > best_tokens:
            best_model, best_tokens, best_tier = model, tok, tier
    return round(total_cost, 6), totals, best_model, best_tier, unpriced


def load_feature_name(root, fid):
    try:
        man = json.load(open(os.path.join(root, ".factory", "manifest.json"), encoding="utf-8"))
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


def state_path(root, sid):
    return os.path.join(root, ".factory", "costs", ".state", f"{sid}.json")


def load_state(root, sid):
    try:
        return json.load(open(state_path(root, sid), encoding="utf-8"))
    except (OSError, ValueError):
        return {"line": 0, "turn": 0}


def save_state(root, sid, st):
    p = state_path(root, sid)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(st, f)


def append_record(root, sid, record, ts):
    month = (ts or "")[:7] or "0000-00"
    out_dir = os.path.join(root, ".factory", "costs", month)
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, f"{sid}.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def journaled_totals(root, sid):
    """Somme (cout, tokens) deja journalisee pour la session, tous mois confondus."""
    import glob
    cost = 0.0
    tok = dict(input=0, output=0, cache_read=0, cache_write_5m=0, cache_write_1h=0)
    for jf in glob.glob(os.path.join(root, ".factory", "costs", "**", f"{sid}.jsonl"), recursive=True):
        try:
            for line in open(jf, encoding="utf-8"):
                line = line.strip()
                if not line:
                    continue
                r = json.loads(line)
                cost += r.get("sim_cost_usd") or 0.0
                for k in tok:
                    tok[k] += (r.get("tokens") or {}).get(k, 0)
        except (OSError, ValueError):
            continue
    return round(cost, 6), tok


def read_stdin():
    try:
        return json.load(sys.stdin)
    except (ValueError, OSError):
        return None


def context(raw_all_text, root):
    branches = GITBRANCH_RE.findall(raw_all_text)
    branch = branches[-1] if branches else None
    return branch, attribution(root, branch, raw_all_text)


def cmd_turn():
    data = read_stdin()
    if not data:
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

    st = load_state(root, sid)
    line0 = st.get("line", 0)
    new = raw[line0:]
    seen = collect_usage(new)
    if not seen:                       # rien de nouveau a compter
        st["line"] = len(raw)
        save_state(root, sid, st)
        return 0

    per_model, last_ts = sum_by_model(seen)
    table = load_price_table(root)
    cost, totals, model, tier, unpriced = price_all(per_model, table)
    branch, attr = context("".join(raw), root)
    turn_no = st.get("turn", 0) + 1

    append_record(root, sid, {
        "schema": SCHEMA, "session_id": sid, "turn": turn_no, "dev": dev_identity(root),
        "ts": last_ts, "branch": branch, "model": model, "tier": tier,
        "tokens": totals, "attribution": attr, "sim_cost_usd": cost,
        "price_table_date": (table or {}).get("date"), "unpriced_models": unpriced,
    }, last_ts)
    save_state(root, sid, {"line": len(raw), "turn": turn_no})
    return 0


def cmd_reconcile():
    data = read_stdin()
    if not data:
        return 0
    tpath, sid = data.get("transcript_path"), data.get("session_id") or "session"
    root = project_root(data.get("cwd"))
    if not tpath or not os.path.isfile(tpath):
        return 0
    try:
        raw = open(tpath, encoding="utf-8").readlines()
    except OSError:
        return 0

    seen = collect_usage(raw)
    if not seen:
        return 0
    per_model, last_ts = sum_by_model(seen)
    table = load_price_table(root)
    full_cost, full_tok, model, tier, unpriced = price_all(per_model, table)
    jcost, jtok = journaled_totals(root, sid)

    delta = {k: full_tok[k] - jtok.get(k, 0) for k in full_tok}
    dcost = round(full_cost - jcost, 6)
    if dcost <= 1e-9 and all(v <= 0 for v in delta.values()):
        return 0                       # journal deja complet
    branch, attr = context("".join(raw), root)
    append_record(root, sid, {
        "schema": SCHEMA, "session_id": sid, "turn": "R", "kind": "reconciliation",
        "dev": dev_identity(root), "ts": last_ts, "branch": branch, "model": model, "tier": tier,
        "tokens": {k: max(0, v) for k, v in delta.items()},
        "attribution": attr, "sim_cost_usd": max(0.0, dcost),
        "price_table_date": (table or {}).get("date"), "unpriced_models": unpriced,
    }, last_ts)
    save_state(root, sid, {"line": len(raw), "turn": load_state(root, sid).get("turn", 0)})
    return 0


def main(argv):
    mode = argv[1] if len(argv) > 1 else "turn"
    if mode == "turn":
        return cmd_turn()
    if mode == "reconcile":
        return cmd_reconcile()
    _log("usage: turn_cost.py [turn|reconcile]")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
