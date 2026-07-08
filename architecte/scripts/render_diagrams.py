#!/usr/bin/env python
"""Rend en PNG les diagrammes Mermaid de diagrammes.md — robuste, sans intervention.

Chaine de methodes a repli automatique (aucune interaction, aucune permission demandee) :
  1. mermaid-cli local `mmdc` + navigateur systeme (Edge/Chrome), SANS telecharger Chromium
  2. `npx @mermaid-js/mermaid-cli@<pin>` (idem ; installe a la volee si besoin)
  3. Kroki auto-heberge (http://localhost:8000) si disponible
  4. API publique (kroki.io) UNIQUEMENT si RENDER_ALLOW_PUBLIC=1 (le diagramme quitte la machine)

Confidentialite : par defaut tout est LOCAL (methodes 1 a 3) ; la 4 est opt-in explicite.
TLS d'entreprise : on fait confiance a la CA du systeme (NODE_USE_SYSTEM_CA=1) ; on ne
desactive JAMAIS la verification TLS. Le telechargement de Chromium par Puppeteer (le point
de rupture derriere un proxy) est evite en pointant sur un navigateur deja installe.

Usage:
    py -3 render_diagrams.py [chemin/vers/architecte-out/diagrammes.md]

Exit 0 si au moins un diagramme rendu ; 1 sinon (le skill continue sans bloquer).
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request

FENCE_RE = re.compile(r"```mermaid\s*\n(.*?)\n```", re.DOTALL)
HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+(.*?)\s*#*\s*$", re.MULTILINE)

# Version epinglee de mermaid-cli. Surchargeable ; architecte-init peut fixer l'exact.
MERMAID_CLI_SPEC = os.environ.get("MERMAID_CLI_SPEC", "@mermaid-js/mermaid-cli@11")
KROKI_LOCAL = os.environ.get("KROKI_URL", "http://localhost:8000")
KROKI_PUBLIC = "https://kroki.io"
ALLOW_PUBLIC = os.environ.get("RENDER_ALLOW_PUBLIC", "") not in ("", "0", "false", "False")


def slugify(text, fallback):
    text = (text or "").lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text or fallback


def heading_before(md, pos):
    last = None
    for m in HEADING_RE.finditer(md):
        if m.start() < pos:
            last = m.group(1)
        else:
            break
    return last


def find_system_browser():
    """Chemin d'un navigateur base Chromium deja installe (Edge/Chrome), ou None."""
    env = os.environ.get("PUPPETEER_EXECUTABLE_PATH")
    if env and os.path.isfile(env):
        return env
    for exe in ("microsoft-edge", "msedge", "google-chrome", "chromium", "chromium-browser", "chrome"):
        found = shutil.which(exe)
        if found:
            return found
    candidates = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ]
    for c in candidates:
        if os.path.isfile(c):
            return c
    return None


def subprocess_env(browser):
    """Env des sous-processus Node : pas de telechargement Chromium, CA systeme, TLS intact."""
    env = dict(os.environ)
    env["PUPPETEER_SKIP_DOWNLOAD"] = "1"
    env.setdefault("NODE_USE_SYSTEM_CA", "1")
    if browser:
        env["PUPPETEER_EXECUTABLE_PATH"] = browser
    return env


def puppeteer_config(project_root, browser):
    """Ecrit/retrouve <project>/.factory/puppeteer.json (executablePath = navigateur systeme)."""
    factory = os.path.join(project_root, ".factory")
    cfg_path = os.path.join(factory, "puppeteer.json")
    if os.path.isfile(cfg_path):
        return cfg_path
    if browser and os.path.isdir(factory):
        try:
            with open(cfg_path, "w", encoding="utf-8") as f:
                json.dump({"executablePath": browser, "headless": True, "args": ["--no-sandbox"]}, f)
            return cfg_path
        except OSError:
            return None
    return None


def _adjust_for_windows(args):
    """Sur Windows, un shim .cmd/.bat (npm/npx/mmdc) doit passer par cmd.exe pour s'executer."""
    if not args:
        return args
    exe = shutil.which(args[0]) or args[0]
    out = [exe] + list(args[1:])
    if os.name == "nt" and exe.lower().endswith((".cmd", ".bat")):
        return ["cmd", "/c"] + out
    return out


def mmdc_base():
    """Commande de base pour mermaid-cli, ou None si ni mmdc ni npx sur le PATH."""
    if shutil.which("mmdc"):
        return ["mmdc"]
    if shutil.which("npx"):
        return ["npx", "-y", MERMAID_CLI_SPEC]
    return None


def ensure_mermaid_cli(env):
    """Si mermaid-cli est indisponible, tente une install globale silencieuse (sans Chromium)."""
    base = mmdc_base()
    if base is not None:
        return base
    if shutil.which("npm"):
        try:
            subprocess.run(
                _adjust_for_windows(["npm", "install", "-g", MERMAID_CLI_SPEC]),
                check=True, capture_output=True, text=True, env=env,
            )
        except (subprocess.CalledProcessError, OSError):
            return None
        return mmdc_base()
    return None


def render_with_mermaid_cli(mmd_path, png_path, env, cfg_path):
    base = ensure_mermaid_cli(env)
    if base is None:
        return False, "mermaid-cli indisponible (Node/npm absents)"
    cmd = list(base) + ["-i", mmd_path, "-o", png_path, "-b", "white"]
    if cfg_path:
        cmd += ["--puppeteerConfigFile", cfg_path]
    try:
        subprocess.run(_adjust_for_windows(cmd), check=True, capture_output=True, text=True, env=env)
        return True, ""
    except subprocess.CalledProcessError as exc:
        return False, ((exc.stderr or exc.stdout or "").strip())[:300]
    except OSError as exc:
        return False, str(exc)[:300]


def render_with_kroki(source, png_path, base_url):
    try:
        req = urllib.request.Request(
            base_url.rstrip("/") + "/mermaid/png",
            data=source.encode("utf-8"),
            headers={"Content-Type": "text/plain"},
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
        if getattr(resp, "status", 200) == 200 and data:
            with open(png_path, "wb") as f:
                f.write(data)
            return True, ""
        return False, "reponse kroki vide/invalide"
    except Exception as exc:  # noqa: BLE001 - repli : on veut juste savoir si ca a marche
        return False, str(exc)[:300]


def kroki_available(base_url):
    try:
        with urllib.request.urlopen(base_url, timeout=3):
            return True
    except Exception:  # noqa: BLE001
        return False


def main(argv):
    md_path = argv[1] if len(argv) > 1 else "architecte-out/diagrammes.md"
    if not os.path.isfile(md_path):
        print(f"ERREUR: fichier introuvable: {md_path}", file=sys.stderr)
        return 1

    md = open(md_path, encoding="utf-8").read()
    blocks = list(FENCE_RE.finditer(md))
    if not blocks:
        print("Aucun bloc mermaid trouve dans le fichier - rien a rendre.")
        return 1

    out_parent = os.path.dirname(os.path.abspath(md_path))   # <project>/architecte-out
    out_dir = os.path.join(out_parent, "diagrammes")
    project_root = os.path.dirname(out_parent)               # <project>
    os.makedirs(out_dir, exist_ok=True)

    browser = find_system_browser()
    env = subprocess_env(browser)
    cfg_path = puppeteer_config(project_root, browser)
    local_kroki = kroki_available(KROKI_LOCAL)

    rendered, used = 0, {}
    for i, m in enumerate(blocks, 1):
        slug = slugify(heading_before(md, m.start()), f"diagramme-{i}")
        slug = re.sub(r"^\d+-", "", slug) or f"diagramme-{i}"   # retirer un numero de titre en tete
        if slug in used:
            used[slug] += 1
            slug = f"{slug}-{used[slug]}"
        else:
            used[slug] = 1
        name = f"{i:02d}-{slug}"          # nom deterministe : prefixe numerique stable
        png = os.path.join(out_dir, f"{name}.png")
        source = m.group(1).strip() + "\n"

        errors = []
        with tempfile.NamedTemporaryFile("w", suffix=".mmd", delete=False, encoding="utf-8") as tf:
            tf.write(source)
            mmd = tf.name
        try:
            ok, err = render_with_mermaid_cli(mmd, png, env, cfg_path)
        finally:
            try:
                os.unlink(mmd)
            except OSError:
                pass
        if not ok:
            errors.append(f"mermaid-cli: {err}")
            if local_kroki:
                ok, err = render_with_kroki(source, png, KROKI_LOCAL)
                if not ok:
                    errors.append(f"kroki-local: {err}")
            if not ok and ALLOW_PUBLIC:
                ok, err = render_with_kroki(source, png, KROKI_PUBLIC)
                if not ok:
                    errors.append(f"kroki-public: {err}")

        if ok:
            print(f"  rendu : diagrammes/{name}.png")
            rendered += 1
        else:
            print(f"  echec rendu '{name}': {' | '.join(errors)[:400]}", file=sys.stderr)

    if rendered:
        print(f"{rendered}/{len(blocks)} diagramme(s) rendus dans {out_dir}")
        return 0
    print(
        "Aucun diagramme rendu. Installer Node.js (mermaid-cli) ou lancer un Kroki local "
        "(docker run -d -p 8000:8000 yuzutech/kroki). Le markdown reste la source.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
