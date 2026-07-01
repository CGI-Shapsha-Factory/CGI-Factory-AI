#!/usr/bin/env python
"""Provisionne (silencieusement) de quoi rendre les diagrammes Mermaid — appele par architecte-init.

Idempotent, best-effort, sans prompt : detecte le navigateur systeme et ecrit
.factory/puppeteer.json ; installe mermaid-cli epingle SANS telecharger Chromium ; fait
confiance a la CA du systeme (NODE_USE_SYSTEM_CA=1) sans desactiver TLS. N'echoue JAMAIS
la phase : ce qui manque sera de toute facon retente par render_diagrams.py.

Usage:
    py -3 provision_render.py [chemin/vers/.factory]   (defaut: ./.factory)
"""
import json
import os
import shutil
import subprocess
import sys

MERMAID_CLI_SPEC = os.environ.get("MERMAID_CLI_SPEC", "@mermaid-js/mermaid-cli@11")

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


def _adjust_for_windows(args):
    """Sur Windows, un shim .cmd/.bat (npm) doit passer par cmd.exe pour s'executer."""
    exe = shutil.which(args[0]) or args[0]
    out = [exe] + list(args[1:])
    if os.name == "nt" and exe.lower().endswith((".cmd", ".bat")):
        return ["cmd", "/c"] + out
    return out


def main(argv):
    factory = argv[1] if len(argv) > 1 else ".factory"
    if not os.path.isdir(factory):
        print(f"provision-render: dossier .factory introuvable ({factory}) - ignore.", file=sys.stderr)
        return 0

    # 1) navigateur systeme -> puppeteer.json (evite le telechargement de Chromium)
    browser = find_browser()
    cfg = os.path.join(factory, "puppeteer.json")
    if browser and not os.path.isfile(cfg):
        try:
            with open(cfg, "w", encoding="utf-8") as f:
                json.dump({"executablePath": browser, "headless": True, "args": ["--no-sandbox"]}, f)
            print(f"provision-render: navigateur systeme -> {cfg}")
        except OSError:
            pass
    elif browser:
        print("provision-render: puppeteer.json deja present.")
    else:
        print("provision-render: aucun navigateur systeme detecte (Kroki local possible en repli).")

    # 2) mermaid-cli epingle, SANS Chromium, CA systeme
    if shutil.which("mmdc"):
        print("provision-render: mmdc deja installe.")
    elif shutil.which("npm"):
        env = dict(os.environ)
        env["PUPPETEER_SKIP_DOWNLOAD"] = "1"
        env.setdefault("NODE_USE_SYSTEM_CA", "1")
        try:
            subprocess.run(_adjust_for_windows(["npm", "install", "-g", MERMAID_CLI_SPEC]),
                           check=True, capture_output=True, text=True, env=env)
            print(f"provision-render: mermaid-cli installe ({MERMAID_CLI_SPEC}, sans Chromium).")
        except (subprocess.CalledProcessError, OSError) as exc:
            msg = getattr(exc, "stderr", "") or str(exc)
            print(f"provision-render: install mermaid-cli differee ({str(msg).strip()[:150]}). "
                  "npx / Kroki prendront le relais au rendu.", file=sys.stderr)
    else:
        print("provision-render: Node/npm absents - le rendu utilisera Kroki local si dispo.", file=sys.stderr)

    return 0   # best-effort : ne bloque jamais l'init


if __name__ == "__main__":
    sys.exit(main(sys.argv))
