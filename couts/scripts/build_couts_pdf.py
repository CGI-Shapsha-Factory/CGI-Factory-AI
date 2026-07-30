#!/usr/bin/env python
"""Rendu du rapport de couts en PDF (A4 paysage), a cote du markdown.

Les generateurs (`references/cost_report.py`, `references/cost_equipe.py`) calculent deja tout ;
ce module met en page le dict `data` avec `templates/rapport-couts.html` et imprime via Chrome
headless. Aucun fichier intermediaire, aucun recalcul.

Deux documents, meme gabarit :
  - `kind="session"` : une ligne par session, repartition du cout par categorie de tokens ;
  - `kind="equipe"`  : une ligne par developpeur, repartition du cout par developpeur.

La mecanique d'impression (decoupe du gabarit, substitution de jetons, pagination equilibree,
decouverte de Chrome, comptage des pages du PDF) reprend celle eprouvee de
`validation/scripts/build_rapport_pdf.py`. Elle est COPIEE et non importee : les plugins sont
distribues separement par la marketplace, un import inter-plugins casserait a l'installation.
La mise en page, elle, n'a rien de commun : un rapport de couts ne prononce pas de verdict.

JAMAIS BLOQUANT : sans Chrome ou sans gabarit, le markdown reste le livrable et l'appelant
recoit simplement `ok=False` avec un message actionnable.
"""
import html
import os
import re
import shutil
import subprocess
import sys
import tempfile

LIGNES_PAR_PAGE = 16
GABARIT = "rapport-couts.html"

CHROME_CANDIDATS = (
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
)
CHROME_PATH = ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser",
               "chrome", "msedge")

# Rampe monochrome : les parts sont les morceaux d'UNE meme depense, pas des natures
# differentes. Une rampe le dit ; des teintes vives le nieraient. Elle est CALCULEE pour n parts
# (4 categories de tokens, ou autant de developpeurs qu'il y en a) : une liste figee donnerait
# la meme teinte a tous les developpeurs au-dela du quatrieme.
RAMPE_SOMBRE = (15, 76, 82)      # #0f4c52
RAMPE_CLAIRE = (201, 229, 230)   # #c9e6e6


def _rampe(n):
    """n teintes du plus sombre au plus clair, et l'index a partir duquel le fond est trop
    clair pour du texte blanc."""
    if n <= 1:
        return [f"#{RAMPE_SOMBRE[0]:02x}{RAMPE_SOMBRE[1]:02x}{RAMPE_SOMBRE[2]:02x}"], n
    teintes = []
    for i in range(n):
        f = i / (n - 1)
        r, v, b = (int(round(a + (z - a) * f))
                   for a, z in zip(RAMPE_SOMBRE, RAMPE_CLAIRE))
        teintes.append(f"#{r:02x}{v:02x}{b:02x}")
    # Au-dela de la moitie de la rampe, le fond est clair : texte sombre.
    return teintes, (n + 1) // 2


# --------------------------------------------------------------------------- gabarit

def _fragments(source):
    """Decoupe le gabarit sur les marqueurs `<!-- ##NOM## -->` (le preambule est ignore)."""
    blocs = {}
    morceaux = re.split(r"<!--\s*##([A-Z_]+)##\s*-->", source)
    for i in range(1, len(morceaux), 2):
        blocs[morceaux[i]] = morceaux[i + 1].strip("\n")
    return blocs


def _remplir(gabarit, valeurs):
    """Substitue les jetons `{{NOM}}` ; un jeton non fourni devient une chaine vide."""
    def _sub(match):
        return str(valeurs.get(match.group(1), ""))
    return re.sub(r"\{\{([A-Z0-9_]+)\}\}", _sub, gabarit)


def _texte(valeur, sanitize=None):
    """Texte echappe (aucune balise ne passe), typographie nettoyee si un nettoyeur est fourni."""
    brut = str(valeur if valeur is not None else "")
    if sanitize:
        brut = sanitize(brut)
    return html.escape(brut, quote=False)


def _tranches(lignes, par_page):
    """Decoupe en pages equilibrees : une derniere page a deux lignes est laide."""
    if not lignes:
        return [[]]
    pages = max(1, -(-len(lignes) // par_page))
    taille = -(-len(lignes) // pages)
    return [lignes[i:i + taille] for i in range(0, len(lignes), taille)]


# --------------------------------------------------------------------------- formatage

def _int(n):
    return f"{int(n or 0):_}".replace("_", " ")


def _tok(n):
    """Ordre de grandeur lisible dans un encadre : 264.8 M, 573 k, 812."""
    n = int(n or 0)
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f} M"
    if n >= 1_000:
        return f"{n / 1_000:.0f} k"
    return str(n)


def _eur(v):
    return "-" if v is None else f"{v:.2f}"


def _jjmm(ts):
    return f"{ts[8:10]}-{ts[5:7]}" if (ts and len(ts) >= 10) else "?"


# --------------------------------------------------------------------------- blocs

def _kpis(blocs, items):
    return "\n".join(_remplir(blocs["FRAGMENT_KPI"],
                              {"KPI_CLASSE": c, "KPI_N": n, "KPI_L": l})
                     for c, n, l in items)


def _repartition(blocs, parts):
    """Barre empilee + legende. `parts` = [(libelle, usd)] deja triees, total > 0."""
    total = sum(p[1] for p in parts)
    if total <= 0:
        return "", "", "montant nul"
    teintes, pale = _rampe(len(parts))
    segments, legende = [], []
    for index, (libelle, usd) in enumerate(parts):
        pct = usd / total * 100.0
        fond = teintes[index]
        # Sous 7 %, le texte ne tient pas dans le segment : il reste dans la legende.
        segments.append(_remplir(blocs["FRAGMENT_SEG"], {
            "SEG_CLASSE": "pale" if index >= pale else "",
            "SEG_PCT": f"{pct:.4f}", "SEG_FOND": fond,
            "SEG_TEXTE": f"{pct:.0f} %" if pct >= 7 else "",
        }))
        legende.append(_remplir(blocs["FRAGMENT_LEGENDE"], {
            "LEG_FOND": fond, "LEG_LIBELLE": libelle,
            "LEG_VALEUR": f"{pct:.1f} %",
        }))
    return "\n".join(segments), "\n".join(legende), None


def _entetes(blocs, colonnes):
    return "\n".join(_remplir(blocs["FRAGMENT_TH"],
                              {"TH_CLASSE": c.get("th", ""), "TH_LARGEUR": c["largeur"],
                               "TH_LIBELLE": c["libelle"]})
                     for c in colonnes)


def _ligne(blocs, cellules, classe=""):
    rendu = "".join(_remplir(blocs["FRAGMENT_CELL"],
                             {"CELL_CLASSE": cl, "CELL_VALEUR": v})
                    for cl, v in cellules)
    return _remplir(blocs["FRAGMENT_ROW"], {"ROW_CLASSE": classe, "CELLULES": rendu})


# --------------------------------------------------------------------------- documents

COLS_SESSION = [
    {"libelle": "Session (debut -> fin)", "largeur": "15%"},
    {"libelle": "Modele", "largeur": "19%"},
    {"libelle": "Input", "largeur": "11%", "th": "n"},
    {"libelle": "Output", "largeur": "11%", "th": "n"},
    {"libelle": "Cache lu", "largeur": "13%", "th": "n"},
    {"libelle": "Cache ecrit", "largeur": "13%", "th": "n"},
    {"libelle": "Cout (EUR)", "largeur": "10%", "th": "n"},
]

COLS_EQUIPE = [
    {"libelle": "Developpeur", "largeur": "15%"},
    {"libelle": "Projet", "largeur": "13%"},
    {"libelle": "Sessions", "largeur": "8%", "th": "n"},
    {"libelle": "Input", "largeur": "9%", "th": "n"},
    {"libelle": "Output", "largeur": "10%", "th": "n"},
    {"libelle": "Cache lu", "largeur": "12%", "th": "n"},
    {"libelle": "Cache ecrit", "largeur": "11%", "th": "n"},
    {"libelle": "Estime (EUR)", "largeur": "11%", "th": "n"},
    {"libelle": "Reel (EUR)", "largeur": "10%", "th": "n"},
]

COLS_REEL = [
    {"libelle": "Periode", "largeur": "16%"},
    {"libelle": "Modele", "largeur": "34%"},
    {"libelle": "Input", "largeur": "17%", "th": "n"},
    {"libelle": "Output", "largeur": "17%", "th": "n"},
    {"libelle": "Cout (EUR)", "largeur": "16%", "th": "n"},
]


def _lignes_session(blocs, data, esc):
    lignes = []
    for s in data.get("sessions", []):
        lignes.append(_ligne(blocs, [
            ("k", f"{_jjmm(s.get('start'))} -&gt; {_jjmm(s.get('end'))}"),
            ("mono", esc(", ".join(s.get("models") or []) or "-")),
            ("n", _int(s.get("input"))), ("n", _int(s.get("output"))),
            ("n", _int(s.get("cache_read"))), ("n", _int(s.get("cache_write"))),
            ("eur", _eur(s.get("sim_cost_eur"))),
        ]))
    return lignes


def _total_session(blocs, data):
    t = data.get("total", {})
    return _ligne(blocs, [
        ("k", "Total"), ("", ""),
        ("n", _int(t.get("input"))), ("n", _int(t.get("output"))),
        ("n", _int(t.get("cache_read"))), ("n", _int(t.get("cache_write"))),
        ("eur", _eur(t.get("sim_cost_eur"))),
    ], "total")


def _lignes_equipe(blocs, data, esc):
    lignes = []
    for d in data.get("devs", []):
        reel = d.get("reel_eur")
        lignes.append(_ligne(blocs, [
            ("k", esc(d.get("prenom"))), ("", esc(d.get("projet"))),
            ("n", _int(d.get("sessions"))),
            ("n", _int(d.get("input"))), ("n", _int(d.get("output"))),
            ("n", _int(d.get("cache_read"))), ("n", _int(d.get("cache_write"))),
            ("eur", _eur(d.get("sim_eur"))),
            ("eur reel" if reel is not None else "eur muted", _eur(reel)),
        ]))
    return lignes


def _total_equipe(blocs, data):
    t = data.get("total", {})
    r = (data.get("reel") or {}).get("total", {})
    return _ligne(blocs, [
        ("k", "Total"), ("", ""),
        ("n", _int(t.get("sessions"))),
        ("n", _int(t.get("input"))), ("n", _int(t.get("output"))),
        ("n", _int(t.get("cache_read"))), ("n", _int(t.get("cache_write"))),
        ("eur", _eur(t.get("sim_cost_eur"))),
        ("eur reel", _eur(r.get("cost_eur"))),
    ], "total")


def _lignes_reel(blocs, data, esc):
    lignes = []
    for j in (data.get("reel") or {}).get("jours", []):
        lignes.append(_ligne(blocs, [
            ("k", _jjmm(j.get("jour"))), ("mono", esc(j.get("model"))),
            ("n", _int(j.get("input"))), ("n", _int(j.get("output"))),
            ("eur reel", _eur(j.get("cost_eur"))),
        ]))
    if lignes:
        t = (data.get("reel") or {}).get("total", {})
        lignes.append(_ligne(blocs, [
            ("k", "Total"), ("", ""),
            ("n", _int(t.get("input"))), ("n", _int(t.get("output"))),
            ("eur reel", _eur(t.get("cost_eur"))),
        ], "total"))
    return lignes


def _document(blocs, data, kind, esc):
    """Assemble le document complet. Retourne (html, nombre de pages)."""
    equipe = (kind == "equipe")
    projet = data.get("projet") or "Factory"
    total = data.get("total", {})
    reel = data.get("reel") or {}
    # Le rapport d'equipe porte un total facture sans detail par jour (il agrege des journaux
    # distincts) : se fier aux seules lignes ferait afficher "-" a cote d'un total non nul.
    reel_eur = (reel.get("total") or {}).get("cost_eur")
    if not reel.get("jours") and not reel_eur:
        reel_eur = None

    tokens = sum(int(total.get(k) or 0)
                 for k in ("input", "output", "cache_read", "cache_write"))
    second = ((str(len(data.get("devs", []))), "Developpeurs") if equipe
              else (str(len(data.get("sessions", []))), "Sessions"))
    kpis = _kpis(blocs, [
        ("", f"{_eur(total.get('sim_cost_eur'))} EUR", "Cout estime"),
        ("", second[0], second[1]),
        ("", _tok(tokens), "Tokens"),
        ("reel" if reel_eur is not None else "reel vide",
         f"{_eur(reel_eur)} EUR" if reel_eur is not None else "-", "Reel facture"),
    ])

    segments, legende, vide = _repartition(blocs, data.get("repartition") or [])
    rep_sous = "par developpeur" if equipe else "par categorie de tokens"
    if vide:
        rep_sous = f"{rep_sous} - {vide}"

    fx = (data.get("fx") or {}).get("usd_eur", "?")
    page1 = (blocs["PAGE_SYNTHESE"], {
        "TITRE": "Couts de fabrication",
        "SOUS_TITRE": "Consolidation d'equipe" if equipe else "Simulation au tarif API, par session",
        "PROJET": esc(projet), "PERIODE": esc(data.get("periode") or ""),
        "KPIS": kpis, "SEGMENTS": segments, "LEGENDE": legende,
        "REPARTITION_SOUS": rep_sous,
        "NOTE_ESTIME": ("<b>Cout estime</b> : ce que cette fabrication couterait au tarif API. "
                        "Ce n'est pas un montant facture. Table de prix du "
                        + esc(data.get("price_table_date") or "?")
                        + ", taux " + esc(fx) + " EUR/USD."),
        "NOTE_REEL": ("<b>Cout reel</b> : appels API externes effectivement payes, sortie incluant "
                      "les tokens de raisonnement. Les deux natures ne s'additionnent jamais en "
                      "un chiffre unique."),
    })

    if equipe:
        lignes = _lignes_equipe(blocs, data, esc)
        ligne_total, colonnes = _total_equipe(blocs, data), COLS_EQUIPE
        titre_table, sous_table = "Detail par developpeur", "une ligne par developpeur"
    else:
        lignes = _lignes_session(blocs, data, esc)
        ligne_total, colonnes = _total_session(blocs, data), COLS_SESSION
        titre_table, sous_table = "Detail par session", "une ligne par session"

    pages = [page1]
    tranches = _tranches(lignes, LIGNES_PAR_PAGE)
    for index, tranche in enumerate(tranches, start=1):
        sous = (sous_table if len(tranches) == 1
                else f"{sous_table} - partie {index} sur {len(tranches)}")
        corps = list(tranche) + ([ligne_total] if index == len(tranches) else [])
        pages.append((blocs["PAGE_TABLE"], {
            "TABLE_TITRE": titre_table, "TABLE_SOUS": sous,
            "ENTETES": _entetes(blocs, colonnes), "LIGNES": "\n".join(corps),
            "APRES_TABLE": "",
        }))

    lignes_reel = _lignes_reel(blocs, data, esc)
    if lignes_reel:
        inconnus = reel.get("modeles_non_tarifes") or []
        apres = ('<div class="note reel">Modele(s) hors table de prix, non tarife(s) : '
                 + esc(", ".join(inconnus)) + ".</div>") if inconnus else ""
        for index, tranche in enumerate(_tranches(lignes_reel, LIGNES_PAR_PAGE), start=1):
            pages.append((blocs["PAGE_TABLE"], {
                "TABLE_TITRE": "Cout reel (appels API factures)",
                "TABLE_SOUS": "une ligne par jour et par modele",
                "ENTETES": _entetes(blocs, COLS_REEL), "LIGNES": "\n".join(tranche),
                "APRES_TABLE": apres if index == 1 else "",
            }))

    # Numerotation calculee ici, jamais laissee au navigateur.
    total_pages = len(pages)
    pied_gauche = esc(projet + " | "
                      + ("Couts consolides equipe" if equipe else "Couts de fabrication"))
    rendus = []
    for index, (gabarit, valeurs) in enumerate(pages, start=1):
        valeurs = dict(valeurs)
        valeurs["PIED_GAUCHE"] = pied_gauche
        valeurs["PIED_DROIT"] = esc(f"Document interne - page {index} / {total_pages}")
        rendus.append(_remplir(gabarit, valeurs))

    return _remplir(blocs["DOCUMENT"],
                    {"TITRE_DOC": esc("Couts de fabrication - " + projet),
                     "PAGES": "\n\n".join(rendus)}), total_pages


# --------------------------------------------------------------------------- rendu

def _chrome():
    for chemin in CHROME_CANDIDATS:
        if chemin and os.path.isfile(chemin):
            return chemin
    for nom in CHROME_PATH:
        trouve = shutil.which(nom)
        if trouve:
            return trouve
    return None


def _pages_pdf(chemin):
    """Nombre de pages du PDF produit, lu dans les octets (sans dependance externe)."""
    try:
        with open(chemin, "rb") as f:
            contenu = f.read()
    except OSError:
        return None
    return len(re.findall(rb"/Type\s*/Page(?![sR])", contenu)) or None


def _imprimer(source, sortie):
    chrome = _chrome()
    if not chrome:
        return False, ("aucun navigateur Chrome, Chromium ou Edge trouve pour imprimer le PDF "
                       "(le rapport Markdown reste disponible)")
    fichier = tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8")
    try:
        fichier.write(source)
        fichier.close()
        commande = [
            chrome, "--headless=new", "--disable-gpu", "--no-sandbox",
            "--no-pdf-header-footer", "--run-all-compositor-stages-before-draw",
            "--virtual-time-budget=10000",
            f"--print-to-pdf={sortie}",
            "file:///" + fichier.name.replace("\\", "/"),
        ]
        resultat = subprocess.run(commande, capture_output=True, text=True, timeout=180)
        if not os.path.isfile(sortie):
            detail = (resultat.stderr or "").strip()[-400:]
            return False, f"impression echouee (code {resultat.returncode}) {detail}".strip()
        return True, None
    except (OSError, subprocess.SubprocessError) as exc:
        return False, f"impression impossible: {exc}"
    finally:
        try:
            os.unlink(fichier.name)
        except OSError:
            pass


def gabarit_path():
    """Gabarit du plugin (templates/ a cote de scripts/)."""
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "templates", GABARIT)


def rendre(data, kind, chemin_pdf, sanitize=None):
    """Imprime le PDF. Retourne (ok, message) ; un message non nul explique l'absence de PDF.

    N'echoue jamais bruyamment : le PDF est un bonus, le Markdown reste le livrable.
    """
    chemin = gabarit_path()
    if not os.path.isfile(chemin):
        return False, f"gabarit introuvable ({GABARIT}), PDF non produit"
    try:
        with open(chemin, encoding="utf-8-sig") as f:
            blocs = _fragments(f.read())
    except OSError as exc:
        return False, f"gabarit illisible: {exc}"

    def esc(valeur):
        return _texte(valeur, sanitize)

    try:
        source, attendues = _document(blocs, data, kind, esc)
    except (KeyError, TypeError, ValueError) as exc:
        return False, f"mise en page impossible: {exc}"

    ok, message = _imprimer(source, chemin_pdf)
    if not ok:
        return False, message
    reelles = _pages_pdf(chemin_pdf)
    if reelles and reelles != attendues:
        return True, (f"mise en page: {attendues} pages attendues, {reelles} produites "
                      f"(une page deborde)")
    return True, None
    return lignes
