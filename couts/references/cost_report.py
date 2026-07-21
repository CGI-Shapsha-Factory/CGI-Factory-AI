#!/usr/bin/env python
"""Rapport de couts : cout de SIMULATION seul, un tableau PAR SESSION.

Les tokens du journal .factory/couts/ sont valorises au tarif API (table de prix datee), puis
convertis en EUR via un taux FIGE dans ce script. Ce n'est PAS un montant facture : c'est une
estimation "combien cette fabrication couterait au tarif API".

Le tableau donne, par session : date de debut -> date de fin (JJ-MM), tokens d'entree (bruts, hors
cache), tokens de sortie, tokens de cache lu, tokens de cache ecrit (5m + 1h cumules), et le cout en
euros (cout complet : input + output + cache lu + cache ecrit, au tarif par tier). Une ligne Total
agrege les colonnes numeriques.

Usage : python cost_report.py [racine_projet] [--json]
Ecrit aussi .factory/couts/rapport-couts.md
"""
import glob
import json
import os
import sys

# Taux de change USD -> EUR fige (1 USD = USD_EUR EUR). A mettre a jour a la main avec sa date.
USD_EUR = 0.92
RATE_DATE = "2026-07-06"


_SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build", ".factory"}


def _has_journal(d):
    return bool(glob.glob(os.path.join(d, ".factory", "couts", "**", "*.jsonl"), recursive=True))


def project_root(hint):
    """Localise le dossier dont .factory/couts/ contient REELLEMENT le journal (la ou le hook ecrit).

    On IGNORE `CLAUDE_PROJECT_DIR` (= git root), qui peut differer du dossier d'install couts : le hook
    est ancre sur son emplacement, le rapport doit lire ce meme emplacement, pas le git root parent.
    """
    start = os.path.abspath(hint or os.getcwd())

    # 1. Remonter : 1er ancetre dont .factory/couts/ contient des .jsonl.
    cur = start
    for _ in range(8):
        if _has_journal(cur):
            return cur
        parent = os.path.dirname(cur)
        if parent == cur:
            break
        cur = parent

    # 2. Descendre (profondeur <= 3) : 1er sous-dossier avec un journal (cas "lance depuis le git
    #    root, journal dans un sous-dossier"). On saute les dossiers lourds.
    base = start.rstrip(os.sep).count(os.sep)
    for dirpath, dirnames, _ in os.walk(start):
        dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS]
        if dirpath.rstrip(os.sep).count(os.sep) - base >= 3:
            dirnames[:] = []
        if _has_journal(dirpath):
            return dirpath

    # 3. Repli : 1er ancetre qui a un .factory/ (install sans journal encore), sinon le depart.
    cur = start
    for _ in range(8):
        if os.path.isdir(os.path.join(cur, ".factory")):
            return cur
        parent = os.path.dirname(cur)
        if parent == cur:
            break
        cur = parent
    return start


def load_journal(root):
    # un enregistrement PAR MESSAGE ; dedup GLOBALE par 'key' (message.id:requestId)
    # -> gere reprise / fork / replay (chaque requete comptee une seule fois).
    records = {}
    for path in glob.glob(os.path.join(root, ".factory", "couts", "**", "*.jsonl"), recursive=True):
        try:
            for line in open(path, encoding="utf-8"):
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                key = rec.get("key")
                records[key if key else f"_nokey{len(records)}"] = rec
        except (OSError, ValueError):
            continue
    return list(records.values())


def price_table_date(root):
    try:
        return json.load(open(os.path.join(root, ".factory", "couts", "price-table.json"),
                              encoding="utf-8")).get("date")
    except (OSError, ValueError):
        return None


def eur(usd):
    return None if usd is None else round(usd * USD_EUR, 2)


def _int(n):
    # separateur de milliers par espace : 12 345
    return f"{int(n or 0):,}".replace(",", " ")


def _jjmm(ts):
    # ISO 'AAAA-MM-JJThh:mm:...' -> 'JJ-MM' ; '?' si absent.
    return f"{ts[8:10]}-{ts[5:7]}" if (ts and len(ts) >= 10) else "?"


def sessions_of(records):
    """Agrege le journal PAR session : debut/fin (ts min/max), tokens input/output, cache lu/ecrit, cout USD."""
    sess = {}
    for r in records:
        sid = r.get("session_id") or "?"
        s = sess.setdefault(sid, {"start": None, "end": None, "input": 0, "output": 0,
                                  "cache_read": 0, "cache_write": 0, "usd": 0.0})
        ts = r.get("ts")
        if ts:
            if s["start"] is None or ts < s["start"]:
                s["start"] = ts
            if s["end"] is None or ts > s["end"]:
                s["end"] = ts
        tok = r.get("tokens") or {}
        s["input"] += tok.get("input", 0) or 0
        s["output"] += tok.get("output", 0) or 0
        s["cache_read"] += tok.get("cache_read", 0) or 0
        s["cache_write"] += (tok.get("cache_write_5m", 0) or 0) + (tok.get("cache_write_1h", 0) or 0)
        s["usd"] += r.get("sim_cost_usd") or 0.0
    return sess


def build_report(root):
    records = load_journal(root)
    pdate = price_table_date(root)
    sess = sessions_of(records)
    order = sorted(sess, key=lambda sid: sess[sid]["start"] or "")

    lines = ["# Rapport de coûts : Factory", ""]
    lines.append(f"## Coût de simulation (estimation, tarif API - table du {pdate or '?'})")
    lines.append("")
    lines.append("| Session (début -> fin) | Tokens input | Tokens output | Cache lu | Cache écrit | Coût (€) |")
    lines.append("|---|---|---|---|---|---|")

    tot_in = tot_out = tot_cread = tot_cwrite = 0
    tot_usd = 0.0
    for sid in order:
        s = sess[sid]
        label = f"{_jjmm(s['start'])} -> {_jjmm(s['end'])}"
        e = eur(s["usd"])
        cout = f"{e:.2f} €" if e is not None else "-"
        lines.append(f"| {label} | {_int(s['input'])} | {_int(s['output'])} | "
                     f"{_int(s['cache_read'])} | {_int(s['cache_write'])} | {cout} |")
        tot_in += s["input"]
        tot_out += s["output"]
        tot_cread += s["cache_read"]
        tot_cwrite += s["cache_write"]
        tot_usd += s["usd"]

    te = eur(tot_usd)
    tot_cout = f"{te:.2f} €" if te is not None else "-"
    lines.append(f"| **Total** | **{_int(tot_in)}** | **{_int(tot_out)}** | "
                 f"**{_int(tot_cread)}** | **{_int(tot_cwrite)}** | **{tot_cout}** |")
    lines.append("")
    lines.append(f"_{len(sess)} session(s). Input = tokens d'entrée hors cache ; Cache écrit = "
                 f"écriture 5m + 1h cumulée ; le coût inclut le cache (lecture + écriture). "
                 f"Taux {USD_EUR} €/$ au {RATE_DATE}. "
                 f"Devise native USD, estimation au tarif API - pas un montant facturé._")

    data = {
        "sessions": [
            {"session_id": sid, "start": sess[sid]["start"], "end": sess[sid]["end"],
             "input": sess[sid]["input"], "output": sess[sid]["output"],
             "cache_read": sess[sid]["cache_read"], "cache_write": sess[sid]["cache_write"],
             "sim_cost_usd": round(sess[sid]["usd"], 6), "sim_cost_eur": eur(sess[sid]["usd"])}
            for sid in order
        ],
        "total": {"input": tot_in, "output": tot_out,
                  "cache_read": tot_cread, "cache_write": tot_cwrite,
                  "sim_cost_usd": round(tot_usd, 6), "sim_cost_eur": eur(tot_usd)},
        "records": len(records), "price_table_date": pdate,
        "fx": {"usd_eur": USD_EUR, "date": RATE_DATE},
    }
    return "\n".join(lines), data


def _next_report_path(outdir):
    """Versionnage : ne JAMAIS ecraser. rapport-couts.md, puis rapport-couts-2.md, -3.md, ..."""
    base = os.path.join(outdir, "rapport-couts.md")
    if not os.path.exists(base):
        return base
    n = 2
    while True:
        p = os.path.join(outdir, f"rapport-couts-{n}.md")
        if not os.path.exists(p):
            return p
        n += 1


def main(argv):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    args = [a for a in argv[1:] if not a.startswith("--")]
    root = project_root(args[0] if args else None)
    md, data = build_report(root)
    # Ecrire le livrable d'abord (UTF-8) : garanti meme si la console plante a l'affichage.
    # VERSIONNAGE : chaque execution ecrit un NOUVEAU fichier numerote, jamais un ecrasement.
    report_path = None
    try:
        outdir = os.path.join(root, ".factory", "couts")
        os.makedirs(outdir, exist_ok=True)
        report_path = _next_report_path(outdir)
        open(report_path, "w", encoding="utf-8").write(md + "\n")
    except OSError:
        pass
    data["report_path"] = report_path
    try:
        if "--json" in argv:
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            print(md)
            if report_path:
                print(f"\n_Rapport écrit : {report_path}_")
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
