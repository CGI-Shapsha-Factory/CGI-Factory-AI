#!/usr/bin/env python
"""Provisionne (silencieusement) de quoi rendre les diagrammes D2 — appele par architecte-init.

Idempotent, best-effort, sans prompt : detecte un navigateur systeme (pour le PNG optionnel)
et installe le binaire D2 epingle en espace utilisateur (.factory/d2/), SANS admin, SANS
telecharger de Chromium. Fait confiance a la CA du systeme (contexte SSL par defaut, qui lit le
magasin de certificats Windows) sans desactiver TLS ; honore HTTPS_PROXY/HTTP_PROXY. N'echoue
JAMAIS la phase : ce qui manque sera de toute facon retente par render_diagrams.py (repli Kroki).

Usage:
    py -3 provision_render.py [chemin/vers/.factory]   (defaut: ./.factory)
"""
import io
import os
import platform
import shutil
import ssl
import subprocess  # noqa: F401 - conserve pour parite/outillage eventuel
import sys
import tarfile
import urllib.request

# Version epinglee de D2. Surchargeable par l'env.
D2_VERSION = os.environ.get("D2_VERSION", "v0.7.1")

BROWSERS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
]


def find_browser():
    env = os.environ.get("PUPPETEER_EXECUTABLE_PATH")
    if env and os.path.isfile(env):
        return env
    for exe in ("microsoft-edge", "msedge", "google-chrome", "chromium", "chromium-browser", "chrome"):
        p = shutil.which(exe)
        if p:
            return p
    for c in BROWSERS:
        if os.path.isfile(c):
            return c
    return None


def d2_asset():
    """(nom d'archive GitHub, nom du binaire cible) selon l'OS/arch courant."""
    machine = platform.machine().lower()
    arch = "arm64" if machine in ("arm64", "aarch64") else "amd64"
    if os.name == "nt":
        return f"d2-{D2_VERSION}-windows-{arch}.tar.gz", "d2.exe"
    plat = "macos" if platform.system().lower() == "darwin" else "linux"
    return f"d2-{D2_VERSION}-{plat}-{arch}.tar.gz", "d2"


def find_d2(factory):
    """Binaire D2 deja disponible : env D2_PATH -> PATH -> .factory/d2/, sinon None."""
    env = os.environ.get("D2_PATH") or os.environ.get("D2_EXECUTABLE_PATH")
    if env and os.path.isfile(env):
        return env
    found = shutil.which("d2")
    if found:
        return found
    for name in ("d2.exe", "d2"):
        cand = os.path.join(factory, "d2", name)
        if os.path.isfile(cand):
            return cand
    return None


def provision_d2(factory):
    """Installe le binaire D2 dans .factory/d2/ (best-effort, sans admin, sans bloquer)."""
    existing = find_d2(factory)
    if existing:
        print(f"provision-render: d2 deja disponible ({existing}).")
        return

    asset, binname = d2_asset()
    url = f"https://github.com/terrastruct/d2/releases/download/{D2_VERSION}/{asset}"
    dest_dir = os.path.join(factory, "d2")
    try:
        os.makedirs(dest_dir, exist_ok=True)
        ctx = ssl.create_default_context()   # magasin de certificats systeme ; TLS jamais desactive
        req = urllib.request.Request(url, headers={"User-Agent": "factory-provision"})
        with urllib.request.urlopen(req, timeout=120, context=ctx) as resp:
            data = resp.read()
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tar:
            member = next(
                (m for m in tar.getmembers()
                 if m.isfile() and os.path.basename(m.name) in ("d2.exe", "d2")),
                None,
            )
            if member is None:
                print("provision-render: binaire d2 introuvable dans l'archive.", file=sys.stderr)
                return
            out = os.path.join(dest_dir, binname)
            with tar.extractfile(member) as src, open(out, "wb") as f:
                shutil.copyfileobj(src, f)
        if os.name != "nt":
            os.chmod(out, 0o755)
        print(f"provision-render: d2 {D2_VERSION} installe -> {out}")
    except Exception as exc:  # noqa: BLE001 - best-effort : on ne bloque jamais l'init
        print(
            f"provision-render: d2 non telecharge ({str(exc).strip()[:150]}). "
            "Kroki (local) prendra le relais au rendu si disponible.",
            file=sys.stderr,
        )


def main(argv):
    factory = argv[1] if len(argv) > 1 else ".factory"
    if not os.path.isdir(factory):
        print(f"provision-render: dossier .factory introuvable ({factory}) - ignore.", file=sys.stderr)
        return 0

    # 1) navigateur systeme (rasterisation PNG optionnelle du SVG ; aucun telechargement Chromium)
    browser = find_browser()
    if browser:
        print(f"provision-render: navigateur systeme detecte ({browser}) - PNG possible.")
    else:
        print("provision-render: aucun navigateur systeme (PNG desactive ; le SVG reste produit).")

    # 2) binaire D2 epingle, en espace utilisateur, sans admin
    provision_d2(factory)

    return 0   # best-effort : ne bloque jamais l'init


if __name__ == "__main__":
    sys.exit(main(sys.argv))
