#!/usr/bin/env python
"""Compteur de cout — hook Claude Code `SessionEnd`.

A chaque fin de session : lit le transcript de la session, extrait les 4 categories de tokens
(entree, sortie, lecture cache, ecriture cache 5min/1h), DEDUPLIQUE par (message.id, requestId)
en gardant la DERNIERE valeur, valorise au tarif (table de prix datee), determine l'etiquette
d'attribution (plugin amont OU branche de feature, jamais les deux), et journalise UNE ligne dans
un fichier par session : .factory/costs/<aaaa-mm>/<session-id>.jsonl.

Best-effort : n'echoue jamais la session (SessionEnd ne peut pas bloquer). Tout est capture ;
en cas de probleme on ecrit sur stderr et on sort 0.

Entree : JSON sur stdin {transcript_path, session_id, cwd, hook_event_name, reason}.
Le cout local est une ESTIMATION (cout de simulation), pas le cout reel (= plateforme + abonnements).
"""
import json
import os
import re
import subprocess
import sys

SCHEMA = 1
PLUGINS = ("cadrage", "architecte", "designer", "assembleur")
BRANCH_FEATURE_RE = re.compile(r"^(\d{3})-")
SLASH_RE = re.compile(r"/(cadrage|architecte|designer|assembleur)\s*:")
SKILL_RE = re.compile(r"\b(cadrage|architecte|designer|assembleur)-[a-z\-]+", re.IGNORECASE)


def _log(msg):
    sys.stderr.write(f"session_cost: {msg}\n")


def project_root(cwd_hint):
    root = os.environ.get("CLAUDE_PROJECT_DIR") or cwd_hint or os.getcwd()
    # remonter jusqu'a trouver .factory/ (au plus 6 niveaux)
    cur = os.path.abspath(root)
    for _ in range(6):
        if os.path.isdir(os.path.join(cur, ".factory")):
            return cur
        parent = os.path.dirname(cur)
        if parent == cur:
            break
        cur = parent
    return os.path.abspath(root)


def load_price_table(root):
    path = os.path.join(root, ".factory", "cost", "price-table.json")
    try:
        return json.load(open(path, encoding="utf-8"))
    except (OSError, ValueError):
        return None


def norm_model(model, table_models):
    if not model:
        return None
    if model in table_models:
        return model
    m = re.sub(r"-\d{8}$", "", model)          # retirer un suffixe date -AAAAMMJJ
    if m in table_models:
        return m
    # correspondance par famille + version (opus/sonnet/haiku/fable + x-y)
    fam = re.search(r"(opus|sonnet|haiku|fable)", model)
    ver = re.search(r"(\d+)[.\-](\d+)", model)
    if fam:
        for key in table_models:
            if fam.group(1) in key and (not ver or f"{ver.group(1)}-{ver.group(2)}" in key):
                return key
    return None


def read_transcript(path):
    """Renvoie (usages_par_cle, texte_concatene, git_branch). usages: {(id,req): line_usage_dict}."""
    seen = {}
    texts = []
    branch = None
    with open(path, encoding="utf-8") as f:
        for raw in f:
            raw = raw.strip()
            if not raw:
                continue
            try:
                obj = json.loads(raw)
            except ValueError:
                continue
            if not branch and obj.get("gitBranch"):
                branch = obj["gitBranch"]
            typ = obj.get("type")
            if typ in ("user", "assistant"):
                c = obj.get("message", {}).get("content")
                if isinstance(c, str):
                    texts.append(c)
                elif isinstance(c, list):
                    for part in c:
                        if isinstance(part, dict) and isinstance(part.get("text"), str):
                            texts.append(part["text"])
            if typ != "assistant":
                continue
            msg = obj.get("message") or {}
            usage = msg.get("usage")
            if not isinstance(usage, dict):
                continue
            key = (msg.get("id"), obj.get("requestId"))
            if key == (None, None):
                key = (obj.get("uuid"), None)   # ligne sans id : traiter comme unique
            rec = {"model": msg.get("model"), "usage": usage,
                   "out": usage.get("output_tokens", 0) or 0,
                   "ts": obj.get("timestamp")}
            prev = seen.get(key)
            # DERNIERE occurrence = valeur finale ; on garde le max d'output_tokens (robuste a l'ordre)
            if prev is None or rec["out"] >= prev["out"]:
                seen[key] = rec
    return seen, "\n".join(texts), branch


def sum_tokens(seen):
    """Agrege par modele : {model: {input, output, cache_read, cache_write_5m, cache_write_1h}}."""
    per = {}
    last_ts = None
    for rec in seen.values():
        u = rec["usage"]
        model = rec["model"] or "unknown"
        d = per.setdefault(model, dict(input=0, output=0, cache_read=0, cache_write_5m=0, cache_write_1h=0))
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


def price(per_model, table):
    """Cout de simulation (USD) + drapeau modeles non tarifes."""
    if not table:
        return None, list(per_model)
    models = table.get("models", {})
    mult_1h = table.get("cache_write_1h_multiplier", 2.0)
    total, unpriced = 0.0, []
    for model, d in per_model.items():
        key = norm_model(model, models)
        if not key:
            unpriced.append(model)
            continue
        p = models[key]
        total += (d["input"] * p["input"]
                  + d["output"] * p["output"]
                  + d["cache_read"] * p["cache_read"]
                  + d["cache_write_5m"] * p["cache_write_5m"]
                  + d["cache_write_1h"] * (p["input"] * mult_1h))
    return round(total, 6), unpriced


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
    # 1) branche de feature NNN- => feature (phase de fabrication)
    if branch:
        m = BRANCH_FEATURE_RE.match(branch)
        if m:
            fid = m.group(1)
            name = load_feature_name(root, fid)
            return {"kind": "feature", "id": fid, "label": name or fid}
    # 2) plugin amont : namespace de skill invoque, sinon nom de skill mentionne
    counts = {p: 0 for p in PLUGINS}
    for m in SLASH_RE.finditer(text):
        counts[m.group(1)] += 3          # une commande explicite pese plus
    for m in SKILL_RE.finditer(text):
        counts[m.group(1).lower()] += 1
    best = max(counts, key=counts.get)
    if counts[best] > 0:
        return {"kind": "phase", "label": best}
    return {"kind": "autre", "label": "autre"}


def dev_identity(root):
    for cmd in (["git", "-C", root, "config", "user.email"],):
        try:
            out = subprocess.run(cmd, capture_output=True, text=True, check=True)
            v = out.stdout.strip()
            if v:
                return v
        except (subprocess.CalledProcessError, OSError):
            pass
    return os.environ.get("USERNAME") or os.environ.get("USER") or "inconnu"


def main():
    try:
        data = json.load(sys.stdin)
    except (ValueError, OSError):
        _log("stdin illisible")
        return 0
    tpath = data.get("transcript_path")
    sid = data.get("session_id") or "session"
    root = project_root(data.get("cwd"))

    if not tpath or not os.path.isfile(tpath):
        _log(f"transcript introuvable: {tpath}")
        return 0
    try:
        seen, text, branch = read_transcript(tpath)
    except OSError as exc:
        _log(f"lecture transcript: {exc}")
        return 0
    if not seen:
        return 0   # rien a mesurer

    per_model, last_ts = sum_tokens(seen)
    table = load_price_table(root)
    sim_cost, unpriced = price(per_model, table)
    attr = attribution(root, branch, text)

    totals = dict(input=0, output=0, cache_read=0, cache_write_5m=0, cache_write_1h=0)
    for d in per_model.values():
        for k in totals:
            totals[k] += d[k]

    record = {
        "schema": SCHEMA,
        "session_id": sid,
        "dev": dev_identity(root),
        "ts": last_ts,
        "branch": branch,
        "models": sorted(per_model),
        "tokens": totals,
        "attribution": attr,
        "sim_cost_usd": sim_cost,
        "price_table_date": (table or {}).get("date"),
        "unpriced_models": unpriced,
    }

    month = (last_ts or "")[:7] or "0000-00"
    out_dir = os.path.join(root, ".factory", "costs", month)
    try:
        os.makedirs(out_dir, exist_ok=True)
        # un fichier par session (sans conflit multi-dev) ; on ecrase (dedup par session-id)
        with open(os.path.join(out_dir, f"{sid}.jsonl"), "w", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError as exc:
        _log(f"ecriture journal: {exc}")
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
