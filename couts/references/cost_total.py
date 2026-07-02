#!/usr/bin/env python
"""Bilan total de consommation — un seul fichier partageable pour le chef d'equipe.

Agrege TOUTES les sessions locales (le dossier .factory/couts/ est git-ignore donc
individuel), calcule le total tokens (5 categories) + le cout estime + le nombre
de sessions, et ecrit .factory/couts/bilan-couts.md.

Le seul calcul net-new par rapport a cost_report.py : la somme des tokens (5 cles
input/output/cache_read/cache_write_5m/cache_write_1h). cost_report.py ne somme que
sim_cost_usd ; les tokens restent dans les enregistrements bruts.

Usage : python cost_total.py [racine_projet]
Ecrit .factory/couts/bilan-couts.md et imprime le meme contenu sur stdout.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cost_report  # noqa: E402 — meme dossier, resolution garantie


def _fmt_int(n):
    """Entier groupe par espaces : 1 234 567."""
    return f"{n:,}".replace(",", " ")


def _fmt_token(n):
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.0f}k"
    return str(n)


def main(argv):
    # Compatibilite encodage console Windows : reconfigurer stdout en UTF-8 si possible
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, Exception):
        pass
    args = [a for a in argv[1:] if not a.startswith("--")]
    root = cost_report.project_root(args[0] if args else None)
    # Creer .factory/couts/ si absent (peut tourner avant couts-init)
    outdir = os.path.join(root, ".factory", "couts")
    os.makedirs(outdir, exist_ok=True)
    records = cost_report.load_journal(root)   # deja deduplique par key
    cfg = cost_report.load_config(root)
    pdate = cost_report.price_table_date(root)
    fx = cfg.get("fx_usd_eur") or {}
    rate = fx.get("rate")

    # Total tokens (5 categories — net-new, cost_report.py ne somme que sim_cost_usd)
    tok = {"input": 0, "output": 0, "cache_read": 0, "cache_write_5m": 0, "cache_write_1h": 0}
    for r in records:
        t = r.get("tokens") or {}
        for k in tok:
            tok[k] += t.get(k) or 0
    total_tok = sum(tok.values())

    sim_usd = sum(r.get("sim_cost_usd") or 0.0 for r in records)
    n_sessions = len({r.get("session_id") for r in records})
    devs = sorted({r.get("dev") or "?" for r in records})
    ts_list = sorted(r.get("ts", "") or "" for r in records)
    periode = None
    if ts_list and ts_list[0]:
        debut, fin = ts_list[0][:10], ts_list[-1][:10]
        periode = f"{debut} -> {fin}" if debut != fin else debut

    lines = ["# Bilan de consommation — Factory"]
    if devs:
        lines.append(f"_Dev : {', '.join(devs)}_")
    if periode:
        lines.append(f"_Période : {periode}_")
    lines.append("")
    lines.append(f"- **Sessions** : {n_sessions}")
    lines.append(f"- **Total tokens** : {_fmt_int(total_tok)}")
    lines.append(
        f"  entrée {_fmt_token(tok['input'])} · sortie {_fmt_token(tok['output'])} · "
        f"cache lu {_fmt_token(tok['cache_read'])} · "
        f"cache 5m {_fmt_token(tok['cache_write_5m'])} · "
        f"cache 1h {_fmt_token(tok['cache_write_1h'])}"
    )
    lines.append(f"- **Coût estimé (simulation)** : {cost_report.money(sim_usd, rate)}")
    lines.append("")
    parts = []
    if pdate:
        parts.append(f"table {pdate}")
    if rate is not None:
        parts.append(f"FX {rate}")
    dline = ", ".join(parts) if parts else "table de prix locale"
    lines.append(f"_Estimation au tarif API ({dline}) — pas un montant facturé._")
    if not records:
        lines.append("")
        lines.append(
            "_Aucun enregistrement trouvé — lancer `couts-init` puis attendre la fin d'une session._"
        )

    md = "\n".join(lines)
    print(md)
    try:
        with open(os.path.join(outdir, "bilan-couts.md"), "w", encoding="utf-8") as f:
            f.write(md + "\n")
    except OSError as exc:
        print(f"cost_total: ecriture echouee: {exc}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
