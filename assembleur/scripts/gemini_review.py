#!/usr/bin/env python
"""Reviewer de code INDEPENDANT via l'API Gemini — UNE dimension de revue par invocation.

Objectif : contrer l'exces de confiance de Claude en introduisant un relecteur **externe et non
biaise** (Gemini) juste avant la creation/le merge d'une PR. Ce script est le **bras arme** du skill
`revue-gemini` : la skill fan-out N sous-agents Claude (un par dimension) et chaque sous-agent lance ce
script pour SA dimension ; Gemini fait la revue, le script rend un JSON de findings que Claude agrege.

Contrat de sortie : le script imprime sur stdout **un seul objet JSON** (le resultat machine) :
  {"dimension": "...", "status": "ok|failed|empty", "model": "...", "chunks": N, "truncated": bool,
   "reason": "auth|quota|model|network|server|no_key|no_genai|git|api|parse", "error": "...",
   "findings": [{"severity":"critical|high|medium|low","file":"...","line":<int|null>,
                 "title":"...","detail":"...","recommendation":"..."}]}
Exit 0 si status ok/empty, 2 si failed (le JSON est TOUJOURS imprime pour que le sous-agent le relaie).

Le script NE bloque JAMAIS la chaine : toute erreur (cle absente/invalide, quota, reseau, modele
introuvable, diff trop gros) devient un `status:"failed"` clair, jamais une trace brute.

Usage :
    python gemini_review.py --dimension security [--diff-file <f> | --base origin/main] [--model <id>]
    python gemini_review.py --check            # valide seulement la cle/API (aucune revue)
    python gemini_review.py --list-dimensions
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time

# --- Le "prompt de l'agent" : role commun + mandat par dimension --------------------------------
BASE_ROLE = (
    "Tu es un reviewer de code SENIOR, INDEPENDANT et SCEPTIQUE. Le code t'est soumis AVANT une "
    "PR/merge, apres avoir ete ecrit par un assistant IA (Claude) qui a tendance a surestimer son "
    "propre code. Ton role est de CONTRER cet exces de confiance : cherche activement les vrais "
    "problemes, ne felicite pas, ne resume pas le code, ne parle QUE de ce qui cloche. Tu recois un "
    "DIFF git unifie. Signale uniquement des problemes CONCRETS et ACTIONNABLES, ancres sur un "
    "fichier:ligne visible dans le diff. Pas de generalites, pas d'invention : si tu n'es pas sur "
    "qu'il s'agit d'un vrai probleme, baisse la severite ou ne le signale pas. Severites : "
    "'critical' (faille/bug qui casse en prod), 'high' (probleme serieux probable), "
    "'medium' (a corriger), 'low' (amelioration mineure)."
)

DIMENSIONS = {
    "security": "SECURITE. Vulnerabilites : injection (SQL/commande/XSS/template), secrets/cles en "
                "dur, authz/authn manquante ou cassee, deserialisation non sure, path traversal, "
                "SSRF, crypto faible ou mal utilisee, entrees non validees, permissions trop larges.",
    "correctness": "CORRECTION & GESTION D'ERREURS. Bugs : cas limites, null/None/undefined, "
                   "conditions de course, exceptions avalees ou trop larges, erreurs non gerees, "
                   "valeurs de retour incoherentes, off-by-one, contrats d'API/type violes, "
                   "ressources non liberees.",
    "performance": "PERFORMANCE. Complexite algorithmique excessive, requetes N+1, boucles/requetes "
                   "couteuses, allocations inutiles, I/O ou appels bloquants dans un chemin chaud, "
                   "absence de pagination/cache/index, travail redondant.",
    "architecture": "ARCHITECTURE & REFACTORING. Couplage fort, responsabilites melangees, "
                    "duplication de logique, abstractions qui fuient, violations de couches/frontieres, "
                    "code mort, et opportunites de refactoring concretes qui reduiraient la dette.",
    "quality": "QUALITE & BONNES PRATIQUES. Lisibilite, nommage trompeur, fonctions trop longues, "
               "nombres magiques, commentaires faux/obsoletes, conventions du langage ou du projet "
               "non respectees, complexite inutile.",
    "testing": "TESTS. Couverture manquante sur le nouveau code, chemins critiques non testes, cas "
               "d'erreur/limites non couverts, assertions faibles ou tautologiques, tests fragiles, "
               "mocks trop larges qui masquent les bugs.",
}

SCHEMA_INSTRUCTION = (
    "Reponds STRICTEMENT par un objet JSON de la forme "
    '{"findings":[{"severity":"critical|high|medium|low","file":"chemin/relatif","line":<entier ou null>,'
    '"title":"resume court","detail":"pourquoi c\'est un vrai probleme","recommendation":"quoi faire concretement"}]}. '
    "Liste vide si rien de valable. AUCUNE prose hors du JSON."
)

# Prefixe des cles "Auth key" (Gemini Enterprise Agent Platform, ex-Vertex) : elles exigent
# vertexai=True (mode Express). Les cles standard "AIza..." restent en mode Developer.
ENTERPRISE_KEY_PREFIX = "AQ."

DEFAULT_MODEL = os.environ.get("GEMINI_REVIEW_MODEL", "gemini-2.5-flash")
MAX_CHARS = int(os.environ.get("GEMINI_REVIEW_MAX_CHARS", "120000"))  # ~30k tokens/chunk, borne le contexte
MAX_CHUNKS = int(os.environ.get("GEMINI_REVIEW_MAX_CHUNKS", "8"))
RETRIES = 3


def emit(obj, code):
    """Imprime l'unique objet JSON de resultat sur stdout et sort avec le code voulu."""
    print(json.dumps(obj, ensure_ascii=False))
    sys.exit(code)


def fail(dimension, reason, error, findings=None):
    emit({"dimension": dimension, "status": "failed", "reason": reason, "error": error,
          "findings": findings or []}, 2)


# --- Cle API ------------------------------------------------------------------------------------
def read_env_file(repo):
    """Lit GEMINI_API_KEY / GOOGLE_API_KEY depuis un .env a la racine (parse minimal, sans dependance)."""
    path = os.path.join(repo, ".env")
    if not os.path.isfile(path):
        return None
    try:
        for raw in open(path, encoding="utf-8-sig"):
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            if k.strip() in ("GEMINI_API_KEY", "GOOGLE_API_KEY"):
                return v.strip().strip('"').strip("'") or None
    except OSError:
        return None
    return None


def resolve_key(repo):
    # Cette fonctionnalite GERE la cle dans le `.env` du projet (la skill revue-gemini l'y ecrit) : le
    # `.env` PRIME donc sur d'eventuelles variables d'environnement ambiantes, qui peuvent etre perimees
    # et masquer silencieusement la cle voulue (ex. un vieux GOOGLE_API_KEY invalide). Repli sur
    # l'environnement uniquement si aucun `.env` ne porte de cle (ex. usage CI).
    return (read_env_file(repo)
            or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"))


# --- SDK google-genai (import paresseux + auto-install best-effort) ------------------------------
def ensure_genai():
    try:
        from google import genai  # noqa: F401
        from google.genai import errors, types  # noqa: F401
        return True
    except ImportError:
        pass
    # auto-install espace utilisateur, sans admin, best-effort borne
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "--user", "-q", "google-genai"],
                       capture_output=True, text=True, timeout=180)
    except (OSError, subprocess.SubprocessError):
        return False
    try:
        from google import genai  # noqa: F401,F811
        return True
    except ImportError:
        return False


# --- Diff git -----------------------------------------------------------------------------------
def detect_base(repo):
    for ref in ("origin/main", "main", "origin/master", "master"):
        r = subprocess.run(["git", "-C", repo, "rev-parse", "--verify", "--quiet", ref],
                           capture_output=True, text=True)
        if r.returncode == 0:
            return ref
    return None


def get_diff(repo, base, diff_file):
    if diff_file:
        try:
            return open(diff_file, encoding="utf-8", errors="replace").read(), None
        except OSError as e:
            return None, f"diff-file illisible : {e}"
    if subprocess.run(["git", "-C", repo, "rev-parse", "--is-inside-work-tree"],
                      capture_output=True, text=True).returncode != 0:
        return None, "pas un depot git"
    base = base or detect_base(repo)
    if not base:
        return None, "branche de base introuvable (ni origin/main ni main) — precise --base"
    r = subprocess.run(["git", "-C", repo, "diff", "--no-color", f"{base}...HEAD"],
                       capture_output=True, text=True, errors="replace")
    if r.returncode != 0:
        return None, f"git diff a echoue : {(r.stderr or '').strip()[:200]}"
    return r.stdout, None


def chunk_diff(diff):
    """Decoupe le diff par fichier (`diff --git`) en morceaux <= MAX_CHARS ; borne a MAX_CHUNKS."""
    if len(diff) <= MAX_CHARS:
        return [diff], False
    parts = re.split(r"(?=^diff --git )", diff, flags=re.MULTILINE)
    chunks, cur = [], ""
    for p in parts:
        if not p:
            continue
        if len(cur) + len(p) > MAX_CHARS and cur:
            chunks.append(cur)
            cur = ""
        # un seul fichier depasse la borne : on tronque ce fichier (note truncated)
        cur += p[:MAX_CHARS] if len(p) > MAX_CHARS else p
    if cur:
        chunks.append(cur)
    truncated = len(chunks) > MAX_CHUNKS
    return chunks[:MAX_CHUNKS], truncated


# --- Appel Gemini (avec retry backoff) ----------------------------------------------------------
def call_gemini(client, model, system, content, dimension):
    """Renvoie (findings, None) ou (None, (reason, message)). Retry sur quota/serveur/reseau."""
    from google.genai import errors, types
    for attempt in range(RETRIES):
        try:
            resp = client.models.generate_content(
                model=model, contents=content,
                config=types.GenerateContentConfig(
                    system_instruction=system, temperature=0.2,
                    response_mime_type="application/json"),
            )
            text = (resp.text or "").strip()
            if not text:
                return [], None
            try:
                data = json.loads(text)
            except ValueError:
                m = re.search(r"\{.*\}", text, re.DOTALL)  # tolere un enrobage eventuel
                if not m:
                    return None, ("parse", "reponse Gemini non-JSON")
                data = json.loads(m.group(0))
            return data.get("findings", []) if isinstance(data, dict) else [], None
        except errors.APIError as e:
            code = getattr(e, "code", None)
            msg = (getattr(e, "message", None) or str(e))[:300]
            if code in (401, 403):
                return None, ("auth", f"cle API invalide ou expiree ({code})")
            if code == 404:
                return None, ("model", f"modele '{model}' introuvable ({code})")
            if code == 429:
                if attempt < RETRIES - 1:
                    time.sleep(2 ** attempt * 2)
                    continue
                return None, ("quota", f"quota / rate limit atteint ({code})")
            if code and code >= 500:
                if attempt < RETRIES - 1:
                    time.sleep(2 ** attempt)
                    continue
                return None, ("server", f"erreur serveur Gemini ({code})")
            return None, ("api", f"erreur API Gemini : {msg}")
        except Exception as e:  # noqa: BLE001 - reseau/transport/timeout -> retry puis echec propre
            if attempt < RETRIES - 1:
                time.sleep(2 ** attempt)
                continue
            return None, ("network", f"echec reseau/transport : {str(e)[:200]}")
    return None, ("network", "epuisement des tentatives")


# --- Orchestration ------------------------------------------------------------------------------
def parse_args(argv):
    ap = argparse.ArgumentParser(description="Reviewer de code independant via Gemini (une dimension).")
    ap.add_argument("--dimension", choices=sorted(DIMENSIONS))
    ap.add_argument("--diff-file", default=None)
    ap.add_argument("--base", default=None)
    ap.add_argument("--repo", default=".")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--list-dimensions", action="store_true")
    return ap.parse_args(argv[1:])


def main(argv):
    args = parse_args(argv)
    repo = os.path.abspath(args.repo)

    if args.list_dimensions:
        print(json.dumps({"dimensions": sorted(DIMENSIONS)}, ensure_ascii=False))
        return 0

    key = resolve_key(repo)
    if not key:
        fail(args.dimension or "?", "no_key",
             "GEMINI_API_KEY absente (ni variable d'environnement, ni .env a la racine).")
    if not ensure_genai():
        fail(args.dimension or "?", "no_genai",
             "paquet 'google-genai' introuvable et auto-installation echouee "
             "(pip install --user google-genai).")

    from google import genai
    # Les cles "Auth key" (prefixe AQ.) ciblent le Gemini Enterprise Agent Platform (ex-Vertex),
    # pas l'API Gemini Developer : sans vertexai=True (mode Express, cle seule) elles renvoient un
    # 403 API_KEY_SERVICE_BLOCKED. Les cles standard AIza restent en mode Developer.
    client = (genai.Client(vertexai=True, api_key=key)
              if key.startswith(ENTERPRISE_KEY_PREFIX) else genai.Client(api_key=key))

    if args.check:
        # validation legere : un appel minimal pour verifier cle + API + modele.
        findings, err = call_gemini(client, args.model, "Reponds {\"findings\":[]}.", "ping", "check")
        if err:
            fail("check", err[0], err[1])
        emit({"dimension": "check", "status": "ok", "model": args.model, "findings": []}, 0)

    if not args.dimension:
        fail("?", "api", "argument --dimension requis (ou --check / --list-dimensions).")

    diff, derr = get_diff(repo, args.base, args.diff_file)
    if derr:
        fail(args.dimension, "git", derr)
    if not diff or not diff.strip():
        emit({"dimension": args.dimension, "status": "empty", "model": args.model,
              "findings": [], "note": "aucun changement a revoir (diff vide)."}, 0)

    chunks, truncated = chunk_diff(diff)
    system = f"{BASE_ROLE}\n\nDIMENSION A EXAMINER — {DIMENSIONS[args.dimension]}\n\n{SCHEMA_INSTRUCTION}"
    all_findings, last_err = [], None
    ok_chunks = 0
    for ch in chunks:
        findings, err = call_gemini(client, args.model, system, ch, args.dimension)
        if err:
            last_err = err
            continue
        ok_chunks += 1
        for f in findings or []:
            if isinstance(f, dict) and f.get("title"):
                all_findings.append(f)

    if ok_chunks == 0 and last_err:
        fail(args.dimension, last_err[0], last_err[1])

    emit({"dimension": args.dimension, "status": "ok", "model": args.model,
          "chunks": len(chunks), "truncated": truncated,
          "partial": bool(last_err), "findings": all_findings}, 0)


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001 - jamais de trace brute ; toujours un JSON exploitable
        print(json.dumps({"dimension": "?", "status": "failed", "reason": "api",
                          "error": f"erreur inattendue : {str(exc)[:200]}", "findings": []},
                         ensure_ascii=False))
        sys.exit(2)
