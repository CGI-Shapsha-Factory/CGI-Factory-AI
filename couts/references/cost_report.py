#!/usr/bin/env python
"""Rapport de couts — les 2 restitutions, a partir du journal + de la config.

- COUT REEL (comptable) : abonnements Max fixes (config) + usages API reels + Cowork (config, lus
  Console). C'est la verite comptable.
- COUT DE SIMULATION (estimation) : les tokens du journal .factory/costs/ valorises au tarif API,
  VENTILES par phase amont, par feature, ligne 'autre', + ligne Cowork globale.

Ne JAMAIS presenter la simulation comme du reel. Chaque montant est date (table de prix, taux de change).
USD natif ; conversion EUR via le taux de la config.

Usage : python cost_report.py [racine_projet] [--json]
Ecrit aussi .factory/cost/rapport-couts.md
"""
import glob
import json
import os
import sys

PLUGIN_LABELS = {"cadrage": "Cadrage", "architecte": "Architecture",
                 "designer": "Design", "assembleur": "Assemblage"}


def project_root(hint):
    root = hint or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    cur = os.path.abspath(root)
    for _ in range(6):
        if os.path.isdir(os.path.join(cur, ".factory")):
            return cur
        parent = os.path.dirname(cur)
        if parent == cur:
            break
        cur = parent
    return os.path.abspath(root)


def load_journal(root):
    records, seen = {}, set()
    for path in glob.glob(os.path.join(root, ".factory", "costs", "**", "*.jsonl"), recursive=True):
        try:
            for line in open(path, encoding="utf-8"):
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                sid = rec.get("session_id")
                # dedup par session_id : garder le plus recent (ts)
                if sid in records and (rec.get("ts") or "") <= (records[sid].get("ts") or ""):
                    continue
                records[sid] = rec
        except (OSError, ValueError):
            continue
    return list(records.values())


def load_config(root):
    try:
        return json.load(open(os.path.join(root, ".factory", "cost", "cost-config.json"), encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def price_table_date(root):
    try:
        return json.load(open(os.path.join(root, ".factory", "cost", "price-table.json"),
                              encoding="utf-8")).get("date")
    except (OSError, ValueError):
        return None


def aggregate(records):
    phases = {k: 0.0 for k in PLUGIN_LABELS}
    features, autre, total = {}, 0.0, 0.0
    for r in records:
        c = r.get("sim_cost_usd") or 0.0
        total += c
        attr = r.get("attribution") or {}
        kind = attr.get("kind")
        if kind == "phase" and attr.get("label") in phases:
            phases[attr["label"]] += c
        elif kind == "feature":
            fid = attr.get("id") or attr.get("label")
            f = features.setdefault(fid, {"name": attr.get("label"), "cost": 0.0})
            f["cost"] += c
        else:
            autre += c
    return phases, features, autre, total


def eur(usd, rate):
    return None if (usd is None or rate is None) else round(usd * rate, 2)


def money(usd, rate):
    if usd is None:
        return "— (à compléter)"
    e = eur(usd, rate)
    return f"{e:.2f} € ({usd:.2f} $)" if e is not None else f"{usd:.2f} $"


def build_report(root):
    records = load_journal(root)
    cfg = load_config(root)
    fx = (cfg.get("fx_usd_eur") or {})
    rate = fx.get("rate")
    pdate = price_table_date(root)
    phases, features, autre, sim_total = aggregate(records)

    subs = cfg.get("subscriptions") or []
    subs_total = sum((s.get("price_usd_month") or 0) * (s.get("count") or 0) for s in subs)
    plat = cfg.get("platform_real") or {}
    api_real = plat.get("api_cost_usd")
    cowork_real = plat.get("cowork_cost_usd")

    lines = []
    lines.append("# Rapport de couts — Factory")
    lines.append("")
    lines.append("## Cout REEL (comptable)")
    subs_detail = ", ".join(f"{s.get('plan', '?')}x{s.get('count', 0)}"
                            for s in subs if s.get("count"))
    lines.append(f"- Abonnements Max (fixe/mois) : {money(subs_total, rate)}"
                 + (f" — {subs_detail}" if subs_detail else " — aucun forfait renseigne"))
    lines.append(f"- Usages API reels (Console) : {money(api_real, rate)}")
    lines.append(f"- Cowork (Console) : {money(cowork_real, rate)}")
    real_known = [x for x in (subs_total, api_real, cowork_real) if x]
    lines.append(f"- **Total reel connu** : {money(sum(real_known), rate) if real_known else '—'}"
                 + ("  _(compléter les montants plateforme dans cost-config.json)_" if api_real is None or cowork_real is None else ""))
    lines.append("")
    lines.append(f"## Cout de SIMULATION (estimation, tarif API — table du {pdate or '?'})")
    lines.append("_« Combien cette fabrication couterait en API. » Ce n'est PAS le cout reel._")
    lines.append("")
    lines.append("**Phases amont :**")
    for key, label in PLUGIN_LABELS.items():
        lines.append(f"- {label} : {money(phases[key], rate)}")
    lines.append("")
    lines.append("**Features :**")
    if features:
        for fid in sorted(features):
            f = features[fid]
            nm = f["name"] if f["name"] and f["name"] != fid else ""
            lines.append(f"- {fid}{(' — ' + nm) if nm else ''} : {money(f['cost'], rate)}")
    else:
        lines.append("- (aucune feature mesuree pour l'instant)")
    lines.append("")
    lines.append(f"- Autre (non attribue) : {money(autre, rate)}")
    lines.append(f"- Cowork (global, lu plateforme) : {money(cowork_real, rate)}")
    lines.append(f"- **Total simulation (sessions)** : {money(sim_total, rate)}")
    lines.append("")
    lines.append(f"_Sessions mesurees : {len(records)}. Taux de change : "
                 f"{rate if rate is not None else '?'} ({fx.get('date','?')}). Devise native USD._")
    return "\n".join(lines), {
        "real": {"subscriptions_usd_month": subs_total, "api_cost_usd": api_real,
                 "cowork_cost_usd": cowork_real},
        "simulation_usd": {"phases": phases, "features": features, "autre": autre,
                           "cowork": cowork_real, "total_sessions": round(sim_total, 6)},
        "sessions": len(records), "price_table_date": pdate, "fx": fx,
    }


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    root = project_root(args[0] if args else None)
    md, data = build_report(root)
    if "--json" in argv:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(md)
    try:
        outdir = os.path.join(root, ".factory", "cost")
        os.makedirs(outdir, exist_ok=True)
        open(os.path.join(outdir, "rapport-couts.md"), "w", encoding="utf-8").write(md + "\n")
    except OSError:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
