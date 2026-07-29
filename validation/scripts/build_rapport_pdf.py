#!/usr/bin/env python
"""Rendu deterministe du rapport de recette en PDF (A4 paysage).

Le skill `rapport-de-validation` assemble les DONNEES du rapport dans
`.factory/validation/rapport-<feature>.json` ; ce script les met en page avec le gabarit
`templates/rapport-de-validation.html` et imprime le resultat via Chrome headless dans
`validation-out/<feature>/rapport-de-validation.pdf`.

Le modele ne fabrique jamais de HTML ni de CSS : tout le visuel vit dans le gabarit, toute la
mise en page (pagination, numeros de page, pastilles, encadres) vit ici.

Usage:
    python build_rapport_pdf.py [chemin/vers/manifest.json] <feature>

Sorties: le chemin du PDF, son nombre de pages et sa taille. Exit 0 si le PDF est ecrit,
sinon 1 (le message nomme ce qui manque).

Dependances: Chrome ou Edge installe (rendu PDF). Pillow est FACULTATIF : present, il recadre
la capture de preuve sur sa bande haute pour qu'elle reste lisible au videoprojecteur ; absent,
l'image entiere est integree.
"""
import base64
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata

LIGNES_PAR_PAGE_DEFAUT = 14
LIGNES_RESERVEES_SIGNATURE = 4
GABARIT = "rapport-de-validation.html"

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


# --------------------------------------------------------------------------- gabarit

def _fragments(source):
    """Decoupe le gabarit sur les marqueurs `<!-- ##NOM## -->` (le preambule est ignore)."""
    blocs = {}
    morceaux = re.split(r"<!--\s*##([A-Z_]+)##\s*-->", source)
    for i in range(1, len(morceaux), 2):
        blocs[morceaux[i]] = morceaux[i + 1].strip("\n")
    return blocs


def _remplir(gabarit, valeurs):
    """Substitue les jetons `{{NOM}}` ; un jeton non fourni est remplace par une chaine vide."""
    def _sub(match):
        return str(valeurs.get(match.group(1), ""))
    return re.sub(r"\{\{([A-Z0-9_]+)\}\}", _sub, gabarit)


def _texte(valeur):
    """Texte simple echappe (aucune balise ne passe)."""
    return html.escape(str(valeur or ""), quote=False)


def _rich(valeur):
    """Texte echappe + micro-formatage : **gras**, `code`, retour a la ligne.

    Le modele ecrit du texte, jamais du HTML : on lui laisse ces trois marques et rien d'autre.
    """
    texte = html.escape(str(valeur or ""), quote=False)
    texte = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", texte, flags=re.DOTALL)
    texte = re.sub(r"`([^`]+?)`", r'<span class="mono">\1</span>', texte)
    return texte.replace("\n", "<br>")


# --------------------------------------------------------------------------- donnees

def _classe_verdict(valeur):
    """Ambre pour les reserves, rouge pour un refus, vert sinon."""
    v = _sans_accent(valeur).lower()
    if "refus" in v:
        return "v-ko"
    if "reserve" in v:
        return "v-reserve"
    return "v-ok"


def _sans_accent(texte):
    """Comparaisons insensibles aux accents (le testeur ecrit "validee" ou "validée")."""
    decompose = unicodedata.normalize("NFD", str(texte or ""))
    return "".join(c for c in decompose if not unicodedata.combining(c))


def _classe_tag(nature):
    n = _sans_accent(nature).lower()
    if "anomalie" in n:
        return "tag-ano"
    if "evolution" in n:
        return "tag-evo"
    return "tag-neutre"


def _badge(verdict):
    v = _sans_accent(verdict).upper().strip()
    if v.startswith("OK"):
        return "badge-ok", ""
    if v.startswith("KO"):
        return "badge-ko", "row-ko"
    return "badge-nt", "row-nt"


def _image_b64(chemin, hauteur_recadrage, avertissements):
    """Image encodee en base64, recadree sur sa bande haute si Pillow est disponible."""
    if not os.path.isfile(chemin):
        avertissements.append(f"capture introuvable, figure omise: {chemin}")
        return None
    brut = open(chemin, "rb").read()
    if hauteur_recadrage:
        try:
            import io

            from PIL import Image
            src = Image.open(io.BytesIO(brut))
            if src.height > hauteur_recadrage:
                tampon = io.BytesIO()
                src.crop((0, 0, src.width, hauteur_recadrage)).save(tampon, "PNG")
                brut = tampon.getvalue()
        except ImportError:
            avertissements.append(
                "Pillow absent: capture integree en pleine hauteur (installer pillow pour le recadrage)")
        except Exception as exc:  # image illisible : on integre l'original
            avertissements.append(f"recadrage impossible ({exc}), capture integree telle quelle")
    return base64.b64encode(brut).decode("ascii")


# --------------------------------------------------------------------------- pages

def _bloc_kpis(blocs, chiffres):
    modele = blocs["FRAGMENT_KPI"]
    ecarts = int(chiffres.get("ecarts", 0) or 0)
    lignes = [
        ("", chiffres.get("criteres", 0), "Criteres couverts"),
        ("", chiffres.get("cas", 0), "Cas joues"),
        ("ok", chiffres.get("ok", 0), "Cas conformes"),
        # pas d'encadre rouge quand il n'y a aucun ecart
        ("ko" if ecarts else "", ecarts, "Ecarts constates" if ecarts > 1 else "Ecart constate"),
        ("", chiffres.get("non_testable", 0), "Non testable"),
    ]
    return "\n".join(
        _remplir(modele, {"KPI_CLASSE": classe, "KPI_N": nombre, "KPI_L": libelle})
        for classe, nombre, libelle in lignes)


def _bloc_info(blocs, recette):
    modele = blocs["FRAGMENT_INFO_ROW"]
    confirmatives = recette.get("executions_confirmatives") or []
    champs = [
        ("Environnement teste", recette.get("environnement"), "mono"),
        ("Outil d'execution", recette.get("outil"), ""),
        ("Fichier de resultats", recette.get("fichier_resultats"), "mono"),
        ("Executions confirmatives", "<br>".join(_texte(c) for c in confirmatives), "mono"),
        ("Plan de test", recette.get("plan"), "mono"),
        ("Specification", recette.get("specification"), "mono"),
    ]
    lignes = []
    for cle, valeur, classe in champs:
        if not valeur:
            continue
        # les executions confirmatives sont deja echappees et portent des <br>
        rendu = valeur if cle == "Executions confirmatives" else _texte(valeur)
        lignes.append(_remplir(modele, {"INFO_K": cle, "INFO_V": rendu, "INFO_CLASSE": classe}))
    return "\n".join(lignes)


def _tranches(lignes, par_page, reserve_derniere):
    """Decoupe la matrice en pages equilibrees, la derniere pouvant porter moins de lignes.

    Pages equilibrees plutot que remplies a ras : une derniere page a deux lignes est laide, et
    c'est ce que donne un decoupage glouton.
    """
    if not lignes:
        return [[]]
    capacite_derniere = max(1, par_page - reserve_derniere)
    pages = 1
    while (pages - 1) * par_page + capacite_derniere < len(lignes):
        pages += 1
    taille = -(-len(lignes) // pages)  # division entiere par exces
    return [lignes[i:i + taille] for i in range(0, len(lignes), taille)]


def _lignes_matrice(blocs, cas):
    modele = blocs["FRAGMENT_ROW_CAS"]
    lignes = []
    for entree in cas:
        classe_badge, classe_ligne = _badge(entree.get("verdict", ""))
        verdict = _texte(entree.get("verdict", ""))
        decision = entree.get("decision") or ""
        if decision:
            cellule = f'<span class="tag {_classe_tag(decision)}">{_texte(decision)}</span>'
        else:
            cellule = '<span class="muted">-</span>'
        lignes.append(_remplir(modele, {
            "ROW_CLASSE": classe_ligne,
            "CAS_REF": _texte(entree.get("ref", "")),
            "CAS_PHRASE": _rich(entree.get("phrase", "")),
            "CAS_BADGE": f'<span class="badge {classe_badge}">{verdict}</span>',
            "CAS_PREUVE": _texte(entree.get("preuve", "")) or '<span class="muted">-</span>',
            "CAS_SOURCE": _rich(entree.get("source", "")),
            "CAS_DECISION": cellule,
        }))
    return lignes


def _pages(blocs, data, avertissements):
    """Liste de (gabarit_de_page, valeurs) : synthese, matrice(s), puis un ecart par page."""
    feature = data.get("feature", {})
    recette = data.get("recette", {})
    chiffres = data.get("chiffres", {})
    verdict = data.get("verdict", {})
    numero = feature.get("numero", "")
    intitule = feature.get("intitule", "")

    pages = []

    synthese = "".join(f"      <p>{_rich(p)}</p>\n" for p in data.get("synthese", []))
    callout = ""
    if data.get("encadre_synthese"):
        callout = _remplir(blocs["FRAGMENT_CALLOUT_SIDE"],
                           {"CALLOUT_TEXTE": _rich(data["encadre_synthese"])})
    pages.append((blocs["PAGE_SYNTHESE"], {
        "FEATURE_INTITULE": _texte(intitule),
        "FEATURE_SOUS_TITRE": _texte(feature.get("sous_titre")
                                     or f"Feature {numero} - {data.get('projet', '')}"),
        "DATE": _texte(recette.get("date", "")),
        "PERIMETRE": _texte(f"{chiffres.get('criteres', 0)} criteres, "
                            f"{chiffres.get('cas', 0)} cas de test"),
        "OUTIL_COURT": _texte(recette.get("outil_court") or recette.get("outil", "")),
        "VERDICT_CLASSE": _classe_verdict(verdict.get("valeur", "")),
        "VERDICT_VALEUR": _texte(verdict.get("valeur", "")),
        "VERDICT_NOTE": _rich(verdict.get("note", "")),
        "VERDICT_ASIDE_K": _texte(verdict.get("aside_libelle", "Reserves ouvertes")),
        "VERDICT_ASIDE_V": _texte(verdict.get("aside_valeur", "aucune")),
        "KPIS": _bloc_kpis(blocs, chiffres),
        "SYNTHESE": synthese.rstrip("\n"),
        "INFO_ROWS": _bloc_info(blocs, recette),
        "CALLOUT": callout,
    }))

    lignes = _lignes_matrice(blocs, data.get("cas", []))
    par_page = int(data.get("lignes_par_page") or LIGNES_PAR_PAGE_DEFAUT)
    # Sans ecart, le bloc de signature atterrit sur la derniere page de matrice : elle porte
    # donc moins de lignes, sinon elle deborde.
    tranches = _tranches(lignes, par_page,
                         0 if data.get("ecarts") else LIGNES_RESERVEES_SIGNATURE)
    for index, tranche in enumerate(tranches, start=1):
        suffixe = f" - partie {index} sur {len(tranches)}" if len(tranches) > 1 else ""
        callout_matrice = ""
        if index == len(tranches) and data.get("encadre_matrice"):
            callout_matrice = _remplir(blocs["FRAGMENT_CALLOUT"],
                                       {"CALLOUT_TEXTE": _rich(data["encadre_matrice"])})
        pages.append((blocs["PAGE_MATRICE"], {
            "MATRICE_SOUS_TITRE": _texte(f"{intitule} ({numero}) - exigence par exigence{suffixe}"),
            "ROWS": "\n".join(tranche),
            "CALLOUT_MATRICE": callout_matrice,
        }))

    ecarts = data.get("ecarts", [])
    for index, ecart in enumerate(ecarts, start=1):
        position = f" - ecart {index} sur {len(ecarts)}" if len(ecarts) > 1 else ""
        figure = ""
        if ecart.get("preuve_image"):
            b64 = _image_b64(ecart["_chemin_image"], ecart.get("recadrage_hauteur", 340),
                             avertissements)
            if b64:
                figure = _remplir(blocs["FRAGMENT_FIGURE"], {
                    "IMAGE_B64": b64,
                    "ECART_ID": _texte(ecart.get("ref", "")),
                    "LEGENDE": _rich(ecart.get("legende", "")),
                })
        nature = ecart.get("nature", "")
        pages.append((blocs["PAGE_ECART"], {
            "ECART_SOUS_TITRE": _texte(
                f"{len(ecarts)} ecart sur {chiffres.get('cas', 0)} cas{position}"
                if len(ecarts) == 1 else
                f"{len(ecarts)} ecarts sur {chiffres.get('cas', 0)} cas{position}"),
            "ECART_ID": _texte(ecart.get("ref", "")),
            "ECART_TITRE": _rich(ecart.get("titre", "")),
            "ECART_TAG": (f'<span class="tag {_classe_tag(nature)}">{_texte(nature)}</span>'
                          if nature else ""),
            "ATTENDU": _rich(ecart.get("attendu", "")),
            "CONSTATE": _rich(ecart.get("constate", "")),
            "CRITERES": _rich(ecart.get("criteres_echec", "")),
            "NATURE": _rich(ecart.get("nature_motif", "")),
            "DIAGNOSTIC": _rich(ecart.get("diagnostic", "")),
            "SUITE": _rich(ecart.get("suite", "")),
            "FIGURE": figure,
        }))

    return pages


def _document(blocs, data, avertissements):
    pages = _pages(blocs, data, avertissements)
    verdict = data.get("verdict", {})
    recette = data.get("recette", {})
    feature = data.get("feature", {})
    total = len(pages)

    signature = _remplir(blocs["FRAGMENT_SIGNATURE"], {
        "SIGN_VERDICT": _rich(verdict.get("signature") or verdict.get("valeur", "")),
        "SIGN_DATE": _texte(recette.get("date", "")),
        "SIGN_TESTEUR": _texte(recette.get("testeur", "")) or "&nbsp;",
    })
    pied_gauche = _texte(f"{data.get('projet', '')} | Recette fonctionnelle de la feature "
                         f"{feature.get('numero', '')}")

    rendus = []
    for index, (gabarit, valeurs) in enumerate(pages, start=1):
        valeurs = dict(valeurs)
        valeurs["SIGNATURE"] = signature if index == total else ""
        valeurs["PIED_GAUCHE"] = pied_gauche
        valeurs["PIED_DROIT"] = _texte(
            f"Document interne - {recette.get('date', '')} - page {index} / {total}")
        rendus.append(_remplir(gabarit, valeurs))

    titre = f"Rapport de recette - {feature.get('intitule', '')} ({feature.get('numero', '')})"
    return _remplir(blocs["DOCUMENT"], {"TITRE_DOC": _texte(titre),
                                        "PAGES": "\n\n".join(rendus)}), total


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
    """Nombre de pages du PDF produit (sert a detecter un debordement de mise en page)."""
    try:
        with open(chemin, "rb") as fh:
            contenu = fh.read()
    except OSError:
        return None
    trouves = len(re.findall(rb"/Type\s*/Page(?![sR])", contenu))
    return trouves or None


def _imprimer(html_source, sortie):
    chrome = _chrome()
    if not chrome:
        print("ERREUR: aucun navigateur Chrome/Chromium/Edge trouve pour imprimer le PDF.\n"
              "        Installer Google Chrome (ou Chromium), puis relancer.", file=sys.stderr)
        return False

    fichier = tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8")
    try:
        fichier.write(html_source)
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
            print(f"ERREUR: le rendu PDF a echoue (code {resultat.returncode}).", file=sys.stderr)
            if resultat.stderr.strip():
                print(f"        {resultat.stderr.strip()[-600:]}", file=sys.stderr)
            return False
        return True
    finally:
        try:
            os.unlink(fichier.name)
        except OSError:
            pass


# --------------------------------------------------------------------------- entree

def _manifest_path(argv):
    if len(argv) > 2:
        return argv[1]
    return "manifest.json" if os.path.isfile("manifest.json") else "cadrage-out/manifest.json"


def _project_root(manifest_path):
    root = os.path.dirname(os.path.abspath(manifest_path))
    if os.path.basename(root) == "cadrage-out":
        root = os.path.dirname(root)
    return root


def main(argv):
    if len(argv) < 2:
        print("Usage: python build_rapport_pdf.py [manifest.json] <feature>", file=sys.stderr)
        return 1
    feature = argv[-1]
    root = _project_root(_manifest_path(argv))

    donnees_path = os.path.join(root, ".factory", "validation", f"rapport-{feature}.json")
    if not os.path.isfile(donnees_path):
        print(f"ERREUR: donnees du rapport absentes: .factory/validation/rapport-{feature}.json\n"
              f"        Le skill rapport-de-validation les ecrit avant d'appeler ce script.",
              file=sys.stderr)
        return 1
    try:
        with open(donnees_path, encoding="utf-8-sig") as fh:
            data = json.load(fh)
    except json.JSONDecodeError as exc:
        print(f"ERREUR: donnees du rapport JSON invalide: {exc}", file=sys.stderr)
        return 1

    if not (data.get("verdict") or {}).get("valeur"):
        print("ERREUR: aucun verdict de recette dans les donnees - le PDF ne s'ecrit qu'apres\n"
              "        la porte de recette (verdict humain).", file=sys.stderr)
        return 1

    gabarit_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "templates",
                                GABARIT)
    if not os.path.isfile(gabarit_path):
        gabarit_path = os.path.join(root, ".factory", "validation", GABARIT)
    if not os.path.isfile(gabarit_path):
        print(f"ERREUR: gabarit {GABARIT} introuvable (relancer validation-init).", file=sys.stderr)
        return 1

    with open(gabarit_path, encoding="utf-8-sig") as fh:
        blocs = _fragments(fh.read())

    fdir = os.path.join(root, "validation-out", feature)
    os.makedirs(fdir, exist_ok=True)
    for ecart in data.get("ecarts", []):
        if ecart.get("preuve_image"):
            ecart["_chemin_image"] = os.path.join(fdir, ecart["preuve_image"])

    avertissements = []
    document, attendues = _document(blocs, data, avertissements)

    sortie = os.path.join(fdir, "rapport-de-validation.pdf")
    if not _imprimer(document, sortie):
        return 1

    reelles = _pages_pdf(sortie)
    taille = os.path.getsize(sortie)
    print(f"PDF ecrit: validation-out/{feature}/rapport-de-validation.pdf "
          f"({reelles or attendues} pages, {taille // 1024} Ko)")
    if reelles and reelles != attendues:
        avertissements.append(
            f"mise en page: {attendues} pages attendues, {reelles} produites - une page deborde "
            f"(reduire lignes_par_page ou raccourcir un texte)")
    for message in avertissements:
        print(f"  attention: {message}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
