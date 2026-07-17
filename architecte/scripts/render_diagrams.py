#!/usr/bin/env python
"""Rend les diagrammes D2 de diagrammes.md en SVG (+ PNG best-effort) — robuste, sans intervention.

Chaine de methodes a repli automatique (aucune interaction, aucune permission demandee) :
  1. binaire D2 local (`d2` sur le PATH, ou `.factory/d2/d2.exe` vendorise) -> SVG.
     AUCUN navigateur requis : le SVG (vectoriel, net) est la source de verite.
  2. Kroki auto-heberge (http://localhost:8000) si disponible -> SVG.
  3. API publique (kroki.io) UNIQUEMENT si RENDER_ALLOW_PUBLIC=1 (le diagramme quitte la machine).

PNG (optionnel, confort d'integration) : le SVG est rasterise via un navigateur systeme deja
installe (Edge/Chrome), SANS jamais telecharger Chromium. Desactivable par RENDER_D2_PNG=0.

Confidentialite : par defaut tout est LOCAL (methodes 1-2) ; la 3 est opt-in explicite.
Layout ELK (par defaut) : routage orthogonal, sans chevauchement de fleches ni de libelles.

Usage:
    py -3 render_diagrams.py [chemin/vers/architecte-out/diagrammes.md]

Exit 0 si au moins un diagramme rendu ; 1 sinon (le skill continue sans bloquer).
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request

# Bloc D2 : ```d2  [info-string optionnelle, ex. "theme=303"]  \n  <corps>  \n```
FENCE_RE = re.compile(r"```d2(?:[ \t]+([^\n]*))?\s*\n(.*?)\n```", re.DOTALL)
HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+(.*?)\s*#*\s*$", re.MULTILINE)
THEME_RE = re.compile(r"theme\s*=\s*(\d+)")

D2_LAYOUT = os.environ.get("D2_LAYOUT", "elk")
D2_THEME_DEFAULT = os.environ.get("D2_THEME", "0")
D2_PAD = os.environ.get("D2_PAD", "20")
WANT_PNG = os.environ.get("RENDER_D2_PNG", "1") not in ("", "0", "false", "False")
PNG_SCALE = os.environ.get("RENDER_PNG_SCALE", "2")

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


def parse_theme(info):
    if info:
        m = THEME_RE.search(info)
        if m:
            return m.group(1)
    return D2_THEME_DEFAULT


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


def find_d2(project_root):
    """Binaire D2 : env D2_PATH -> PATH -> <project>/.factory/d2/, sinon None."""
    env = os.environ.get("D2_PATH") or os.environ.get("D2_EXECUTABLE_PATH")
    if env and os.path.isfile(env):
        return env
    found = shutil.which("d2")
    if found:
        return found
    if project_root:
        for name in ("d2.exe", "d2"):
            cand = os.path.join(project_root, ".factory", "d2", name)
            if os.path.isfile(cand):
                return cand
    return None


def _adjust_for_windows(args):
    """Sur Windows, un shim .cmd/.bat (ex. d2 via scoop) doit passer par cmd.exe."""
    if not args:
        return args
    exe = shutil.which(args[0]) or args[0]
    out = [exe] + list(args[1:])
    if os.name == "nt" and exe.lower().endswith((".cmd", ".bat")):
        return ["cmd", "/c"] + out
    return out


def render_with_d2(d2_bin, src_path, out_svg, theme, layout):
    cmd = [d2_bin, "--theme", str(theme), "--layout", str(layout), "--pad", str(D2_PAD),
           src_path, out_svg]
    try:
        subprocess.run(_adjust_for_windows(cmd), check=True, capture_output=True, text=True)
        return True, ""
    except subprocess.CalledProcessError as exc:
        return False, ((exc.stderr or exc.stdout or "").strip())[:300]
    except OSError as exc:
        return False, str(exc)[:300]


def render_with_kroki(source, out_path, base_url, diagram_type, fmt):
    try:
        req = urllib.request.Request(
            base_url.rstrip("/") + f"/{diagram_type}/{fmt}",
            data=source.encode("utf-8"),
            headers={"Content-Type": "text/plain"},
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
        if getattr(resp, "status", 200) == 200 and data:
            with open(out_path, "wb") as f:
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


def _svg_size(svg_path):
    """(largeur, hauteur) en px depuis l'entete SVG produit par D2, ou None."""
    try:
        head = open(svg_path, encoding="utf-8").read(4000)
    except OSError:
        return None
    w = re.search(r'width="(\d+(?:\.\d+)?)', head)
    h = re.search(r'height="(\d+(?:\.\d+)?)', head)
    if w and h:
        return int(float(w.group(1))), int(float(h.group(1)))
    vb = re.search(r'viewBox="[\d.\- ]*?([\d.]+) ([\d.]+)"', head)
    if vb:
        return int(float(vb.group(1))), int(float(vb.group(2)))
    return None


def svg_to_png(svg_path, png_path, browser):
    """Rasterise le SVG en PNG via le navigateur systeme (best-effort, fond blanc)."""
    if not browser:
        return False, "aucun navigateur systeme"
    w, h = _svg_size(svg_path) or (1600, 1200)
    svg_uri = "file:///" + os.path.abspath(svg_path).replace("\\", "/")
    html = (
        "<!doctype html><meta charset='utf-8'>"
        "<style>html,body{margin:0;padding:0;background:#fff}"
        "img{display:block}</style>"
        f"<img src='{svg_uri}'>"
    )
    html_path = None
    try:
        with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as tf:
            tf.write(html)
            html_path = tf.name
        html_uri = "file:///" + os.path.abspath(html_path).replace("\\", "/")
        cmd = [
            browser, "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
            f"--force-device-scale-factor={PNG_SCALE}",
            f"--window-size={w},{h}",
            f"--screenshot={os.path.abspath(png_path)}",
            html_uri,
        ]
        subprocess.run(_adjust_for_windows(cmd), check=True, capture_output=True, text=True, timeout=90)
        if os.path.isfile(png_path):
            return True, ""
        return False, "png non produit"
    except (subprocess.CalledProcessError, OSError, subprocess.TimeoutExpired) as exc:
        return False, str(getattr(exc, "stderr", "") or exc)[:300]
    finally:
        if html_path:
            try:
                os.unlink(html_path)
            except OSError:
                pass


def main(argv):
    md_path = argv[1] if len(argv) > 1 else "architecte-out/diagrammes.md"
    if not os.path.isfile(md_path):
        print(f"ERREUR: fichier introuvable: {md_path}", file=sys.stderr)
        return 1

    md = open(md_path, encoding="utf-8").read()
    blocks = list(FENCE_RE.finditer(md))
    if not blocks:
        print("Aucun bloc d2 trouve dans le fichier - rien a rendre.")
        return 1

    out_parent = os.path.dirname(os.path.abspath(md_path))   # <project>/architecte-out
    out_dir = os.path.join(out_parent, "diagrammes")
    project_root = os.path.dirname(out_parent)               # <project>
    os.makedirs(out_dir, exist_ok=True)

    d2_bin = find_d2(project_root)
    browser = find_system_browser() if WANT_PNG else None
    local_kroki = kroki_available(KROKI_LOCAL)

    rendered, used = 0, {}
    for i, m in enumerate(blocks, 1):
        theme = parse_theme(m.group(1))
        slug = slugify(heading_before(md, m.start()), f"diagramme-{i}")
        slug = re.sub(r"^\d+-", "", slug) or f"diagramme-{i}"   # retirer un numero de titre en tete
        if slug in used:
            used[slug] += 1
            slug = f"{slug}-{used[slug]}"
        else:
            used[slug] = 1
        name = f"{i:02d}-{slug}"          # nom deterministe : prefixe numerique stable
        svg = os.path.join(out_dir, f"{name}.svg")
        png = os.path.join(out_dir, f"{name}.png")
        source = m.group(2).strip() + "\n"

        errors = []
        with tempfile.NamedTemporaryFile("w", suffix=".d2", delete=False, encoding="utf-8") as tf:
            tf.write(source)
            d2src = tf.name
        try:
            if d2_bin:
                ok, err = render_with_d2(d2_bin, d2src, svg, theme, D2_LAYOUT)
                if not ok:
                    errors.append(f"d2: {err}")
            else:
                ok, err = False, "binaire introuvable"
                errors.append("d2: binaire introuvable (installer via provision_render.py)")
        finally:
            try:
                os.unlink(d2src)
            except OSError:
                pass

        if not ok and local_kroki:
            ok, err = render_with_kroki(source, svg, KROKI_LOCAL, "d2", "svg")
            if not ok:
                errors.append(f"kroki-local: {err}")
        if not ok and ALLOW_PUBLIC:
            ok, err = render_with_kroki(source, svg, KROKI_PUBLIC, "d2", "svg")
            if not ok:
                errors.append(f"kroki-public: {err}")

        if ok:
            print(f"  rendu : diagrammes/{name}.svg")
            rendered += 1
            if WANT_PNG and browser:
                pok, perr = svg_to_png(svg, png, browser)
                if pok:
                    print(f"  rendu : diagrammes/{name}.png")
                else:
                    print(f"  (png ignore pour '{name}': {perr[:150]})", file=sys.stderr)
        else:
            print(f"  echec rendu '{name}': {' | '.join(errors)[:400]}", file=sys.stderr)

    if rendered:
        print(f"{rendered}/{len(blocks)} diagramme(s) rendus dans {out_dir}")
        return 0
    print(
        "Aucun diagramme rendu. Installer D2 (py -3 scripts/provision_render.py <projet>/.factory) "
        "ou lancer un Kroki local (docker run -d -p 8000:8000 yuzutech/kroki). "
        "Le markdown reste la source.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
