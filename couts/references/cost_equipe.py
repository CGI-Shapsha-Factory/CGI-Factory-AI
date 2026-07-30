#!/usr/bin/env python
"""Consolidation d'equipe : un tableau, une ligne par developpeur.

Le journal `.factory/couts/` est git-ignore, donc individuel : chaque developpeur envoie
son repertoire de couts, on les depose cote a cote dans un dossier de collecte, et ce
script les agrege en un seul tableau.

    couts-equipe/
      naif/    2026-07/*.jsonl  +  identite.json
      sarah/   2026-07/*.jsonl  +  identite.json
      rapport-equipe.md   <- produit ici

Un sous-dossier = un developpeur. Le prenom et le nom de projet viennent de
`identite.json` (pose par couts-init) ; a defaut on retombe sur l'email git porte par les
enregistrements, puis sur le nom du dossier - et le repli est SIGNALE, jamais silencieux.

Rien n'est retarife cote simulation : `sim_cost_usd` a deja ete calcule par le hook de
chaque developpeur. Seul le cout reel Gemini est tarife ici, avec UNE table pour tout le
monde, pour que les lignes soient comparables.

Usage : python cost_equipe.py <dossier-de-collecte>
Ecrit <dossier-de-collecte>/rapport-equipe.md (versionne, jamais ecrase).
"""
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cost_report  # noqa: E402 - meme dossier, resolution garantie

HERE = os.path.dirname(os.path.abspath(__file__))


def _fmt_int(n):
    """Entier groupe par espaces : 1 234 567 (separateur '_' insensible a la locale)."""
    return f"{int(n or 0):_}".replace("_", " ")


def dossiers_devs(collecte):
    """Sous-dossiers directs du dossier de collecte, tries. Un dossier = un developpeur."""
    try:
        noms = sorted(d for d in os.listdir(collecte)
                      if os.path.isdir(os.path.join(collecte, d)) and not d.startswith("."))
    except OSError:
        return []
    return [(n, os.path.join(collecte, n)) for n in noms]


def _fichiers_journal(dossier):
    """Les .jsonl du dossier, quelle que soit la forme envoyee.

    Un developpeur peut envoyer le contenu de son `.factory/couts/`, son `.factory/` entier,
    ou sa racine projet : on accepte les trois plutot que d'imposer une forme et d'echouer
    sur un dossier legitime.
    """
    vus = {}
    for motif in (os.path.join(dossier, "**", "*.jsonl"),
                  os.path.join(dossier, ".factory", "couts", "**", "*.jsonl")):
        for p in glob.glob(motif, recursive=True):
            vus[os.path.abspath(p)] = True
    return sorted(vus)


def charge_dossier(dossier):
    """Enregistrements d'UN developpeur, dedupliques par 'key' a l'interieur de son dossier.

    La dedup reste LOCALE : deduire globalement (comme le rapport individuel) ferait
    disparaitre en silence les messages d'un developpeur au profit d'un autre si deux
    dossiers se recouvraient. Le recouvrement est detecte plus haut, et signale.
    """
    records = {}
    for path in _fichiers_journal(dossier):
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
    return records


def identite(dossier, nom_dossier, records):
    """(prenom, projet, origine) - origine dit d'ou vient l'identite, pour pouvoir la signaler."""
    for cand in (os.path.join(dossier, "identite.json"),
                 os.path.join(dossier, ".factory", "couts", "identite.json")):
        try:
            data = json.load(open(cand, encoding="utf-8"))
        except (OSError, ValueError):
            continue
        prenom = (data.get("prenom") or "").strip()
        projet = (data.get("projet") or "").strip()
        if prenom or projet:
            return prenom or nom_dossier, projet or "?", "identite"
    # Repli 1 : l'email git stampe sur chaque enregistrement de simulation.
    devs = sorted({r.get("dev") for r in records.values()
                   if not cost_report.est_reel(r) and r.get("dev")})
    if devs:
        return ", ".join(devs), "?", "git"
    # Repli 2 : le nom du dossier depose.
    return nom_dossier, "?", "dossier"


def agrege_dev(records, gtable):
    """Totaux d'un developpeur : tokens + cout estime (deja calcule) + cout reel (tarife ici)."""
    sess = cost_report.sessions_of(records.values())
    tot = {"sessions": len(sess), "input": 0, "output": 0, "cache_read": 0,
           "cache_write": 0, "sim_usd": 0.0}
    for s in sess.values():
        tot["input"] += s["input"]
        tot["output"] += s["output"]
        tot["cache_read"] += s["cache_read"]
        tot["cache_write"] += s["cache_write"]
        tot["sim_usd"] += s["usd"]
    jours, inconnus = cost_report.jours_reels(list(records.values()), gtable)
    tot["reel_usd"] = sum(d["usd"] for d in jours.values()) if jours else None
    tot["reel_inconnus"] = inconnus
    return tot


def table_gemini(collecte):
    """UNE table de prix Gemini pour toute l'equipe : celle du dossier de collecte, sinon
    celle du plugin. Tarifer chaque developpeur avec sa propre table rendrait les lignes
    incomparables sans que ca se voie."""
    direct = os.path.join(collecte, "gemini-price-table.json")
    if os.path.isfile(direct):
        try:
            return json.load(open(direct, encoding="utf-8")), "collecte"
        except (OSError, ValueError):
            pass
    try:
        return json.load(open(os.path.join(HERE, "gemini-price-table.json"),
                              encoding="utf-8")), "plugin"
    except (OSError, ValueError):
        return {}, "absente"


def build_equipe(collecte):
    """Construit le rapport d'equipe. Retourne (markdown, anomalies, data).

    `data` porte les memes chiffres que le tableau, sous forme structuree, pour le rendu PDF :
    le Markdown n'est jamais reparse.
    """
    gtable, origine_table = table_gemini(collecte)
    anomalies = []

    devs = []
    vu_ailleurs = {}       # key -> nom du premier dossier qui la porte
    doublons = {}          # key -> [dossiers]
    ignores = []
    for nom, dossier in dossiers_devs(collecte):
        records = charge_dossier(dossier)
        if not records:
            ignores.append(nom)
            continue
        for key in records:
            if key.startswith("_nokey"):
                continue
            if key in vu_ailleurs and vu_ailleurs[key] != nom:
                doublons.setdefault(key, [vu_ailleurs[key]]).append(nom)
            else:
                vu_ailleurs.setdefault(key, nom)
        prenom, projet, origine = identite(dossier, nom, records)
        devs.append({"nom": nom, "prenom": prenom, "projet": projet, "origine": origine,
                     **agrege_dev(records, gtable)})

    lines = ["# Coûts consolidés : équipe", ""]
    if not devs:
        lines.append("_Aucun répertoire de coûts exploitable dans le dossier de collecte._")
        lines.append("")
        lines.append("_Attendu : un sous-dossier par développeur, contenant son répertoire "
                     "de coûts (les fichiers `.jsonl` et son `identite.json`)._")
        return cost_report.sanitize_typo("\n".join(lines)), anomalies, {"devs": []}

    lines.append("| Développeur | Projet | Sessions | Input | Output | Cache lu | "
                 "Cache écrit | Estimé (€) | Réel (€) |")
    lines.append("|---|---|---|---|---|---|---|---|---|")

    t = {"sessions": 0, "input": 0, "output": 0, "cache_read": 0, "cache_write": 0}
    t_sim = 0.0
    t_reel = 0.0
    a_du_reel = False
    ordonnes = sorted(devs, key=lambda x: (x["prenom"] or "").lower())
    for d in ordonnes:
        e = cost_report.eur(d["sim_usd"])
        estime = f"{e:.2f} €" if e is not None else "-"
        if d["reel_usd"] is None:
            reel = "-"
        else:
            r = cost_report.eur(d["reel_usd"])
            reel = f"{r:.2f} €" if r is not None else "-"
            t_reel += d["reel_usd"]
            a_du_reel = True
        lines.append(f"| {d['prenom']} | {d['projet']} | {d['sessions']} | "
                     f"{_fmt_int(d['input'])} | {_fmt_int(d['output'])} | "
                     f"{_fmt_int(d['cache_read'])} | {_fmt_int(d['cache_write'])} | "
                     f"{estime} | {reel} |")
        for k in t:
            t[k] += d[k]
        t_sim += d["sim_usd"]

    # Total converti UNE fois depuis la somme USD, jamais une somme d'euros arrondis.
    te = cost_report.eur(t_sim)
    tr = cost_report.eur(t_reel) if a_du_reel else None
    lines.append(f"| **Total** | | **{t['sessions']}** | **{_fmt_int(t['input'])}** | "
                 f"**{_fmt_int(t['output'])}** | **{_fmt_int(t['cache_read'])}** | "
                 f"**{_fmt_int(t['cache_write'])}** | "
                 f"**{te:.2f} €** | " + (f"**{tr:.2f} €** |" if tr is not None else "- |"))
    lines.append("")
    lines.append(f"_{len(devs)} développeur(s). Input = tokens d'entrée hors cache ; Cache écrit = "
                 f"écriture 5m + 1h cumulée. Estimé = simulation au tarif API, pas un montant "
                 f"facturé ; Réel = appels API externes effectivement payés. Les deux ne "
                 f"s'additionnent pas. Taux {cost_report.USD_EUR} €/$ au {cost_report.RATE_DATE}._")

    gdate = gtable.get("date")
    if origine_table == "absente":
        anomalies.append("Table de prix Gemini introuvable : la colonne Réel est vide.")
    elif gdate:
        lines.append("")
        lines.append(f"_Coût réel tarifé pour toute l'équipe avec la même table Gemini "
                     f"(table du {gdate}), pour que les lignes restent comparables._")

    # Anomalies : ce qui rendrait le total faux doit se voir, jamais passer en silence.
    sans_identite = [d for d in devs if d["origine"] != "identite"]
    if sans_identite:
        quoi = ", ".join(f"{d['prenom']} (dossier {d['nom']})" for d in sans_identite)
        anomalies.append(f"Identité manquante, ligne identifiée par repli : {quoi}. "
                         f"Leur demander de relancer couts-init pour fixer prénom et projet.")
    if doublons:
        paires = sorted({" et ".join(sorted(set(v))) for v in doublons.values()})
        anomalies.append(f"{len(doublons)} enregistrement(s) présent(s) dans plusieurs dossiers "
                         f"({'; '.join(paires)}) : total probablement gonflé, vérifier les dépôts.")
    if ignores:
        anomalies.append(f"Sous-dossier(s) sans aucun journal, ignoré(s) : {', '.join(ignores)}.")
    inconnus = sorted({m for d in devs for m in d["reel_inconnus"]})
    if inconnus:
        anomalies.append(f"Modèle(s) hors table de prix, non tarifé(s) : {', '.join(inconnus)}.")

    if anomalies:
        lines.append("")
        lines.append("## À vérifier")
        lines.append("")
        for a in anomalies:
            lines.append(f"- {a}")

    # Donnees structurees pour le PDF. La repartition est ici PAR DEVELOPPEUR : sur un rapport
    # d'equipe, savoir qui consomme quoi est plus parlant que la ventilation par categorie de
    # tokens, qui a sa place sur le rapport individuel.
    data = {
        "devs": [{"prenom": d["prenom"], "projet": d["projet"], "sessions": d["sessions"],
                  "input": d["input"], "output": d["output"], "cache_read": d["cache_read"],
                  "cache_write": d["cache_write"], "sim_eur": cost_report.eur(d["sim_usd"]),
                  "reel_eur": cost_report.eur(d["reel_usd"]) if d["reel_usd"] is not None else None}
                 for d in ordonnes],
        "total": {**t, "sim_cost_eur": te},
        "reel": {"jours": [], "total": {"cost_eur": tr}, "modeles_non_tarifes": inconnus},
        "price_table_date": gdate,
        "fx": {"usd_eur": cost_report.USD_EUR, "date": cost_report.RATE_DATE},
        "projet": ", ".join(sorted({d["projet"] for d in ordonnes if d["projet"] != "?"})) or "",
        "periode": "",
        "repartition": [(d["prenom"], d["sim_usd"]) for d in
                        sorted(ordonnes, key=lambda x: -x["sim_usd"])],
    }
    return cost_report.sanitize_typo("\n".join(lines)), anomalies, data


def main(argv):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, Exception):
        pass
    args = [a for a in argv[1:] if not a.startswith("--")]
    if not args:
        print("cost_equipe: usage: python cost_equipe.py <dossier-de-collecte>", file=sys.stderr)
        return 2
    collecte = os.path.abspath(args[0])
    if not os.path.isdir(collecte):
        print(f"cost_equipe: dossier de collecte introuvable: {collecte}", file=sys.stderr)
        return 2

    md, _, data = build_equipe(collecte)
    chemin = None
    try:
        chemin = cost_report.next_report_path(collecte, "rapport-equipe")
        open(chemin, "w", encoding="utf-8").write(md + "\n")
    except OSError as exc:
        print(f"cost_equipe: ecriture echouee: {exc}", file=sys.stderr)
    # PDF presentable a cote du Markdown. Jamais bloquant : le Markdown est le livrable.
    pdf_path, pdf_message = (None, None)
    if data.get("devs"):
        pdf_path, pdf_message = cost_report.rendre_pdf(data, "equipe", chemin)
    try:
        print(md)
        if chemin:
            print(f"\n_Rapport écrit : {chemin}_")
        if pdf_path:
            print(f"_PDF écrit : {pdf_path}_")
        if pdf_message:
            print(f"_PDF : {pdf_message}_")
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
