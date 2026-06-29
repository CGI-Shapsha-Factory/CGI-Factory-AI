#!/usr/bin/env python
"""Rend en images PNG les diagrammes Mermaid d'un fichier diagrams.md.

Lit `architecte-out/diagrams.md` (ou le chemin passe en argument), extrait chaque
bloc ```mermaid (nomme d'apres le titre markdown qui le precede), et produit un
PNG par diagramme dans `architecte-out/diagrammes/` via mermaid-cli (`mmdc`).
Si `mmdc` n'est pas installe, tente `npx -y @mermaid-js/mermaid-cli`.

Aucun service externe : le rendu est local (mermaid-cli embarque un Chromium headless).

Usage:
    python render_diagrams.py [chemin/vers/architecte-out/diagrams.md]

Sortie : EXIT 0 si au moins un diagramme rendu ; 1 si l'outil est indisponible ou
si aucun diagramme n'a pu etre rendu (le skill continue sans bloquer dans ce cas).
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

FENCE_RE = re.compile(r"```mermaid\s*\n(.*?)\n```", re.DOTALL)
HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+(.*?)\s*#*\s*$", re.MULTILINE)


def slugify(text, fallback):
    text = text.lower()
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


def mermaid_runner():
    """Retourne la commande de base pour invoquer mermaid-cli, ou None."""
    if shutil.which("mmdc"):
        return ["mmdc"]
    if shutil.which("npx"):
        return ["npx", "-y", "@mermaid-js/mermaid-cli"]
    return None


def main(argv):
    md_path = argv[1] if len(argv) > 1 else "architecte-out/diagrams.md"
    if not os.path.isfile(md_path):
        print(f"ERREUR: fichier introuvable: {md_path}", file=sys.stderr)
        return 1

    md = open(md_path, encoding="utf-8").read()
    blocks = list(FENCE_RE.finditer(md))
    if not blocks:
        print("Aucun bloc mermaid trouve dans le fichier — rien a rendre.")
        return 1

    out_dir = os.path.join(os.path.dirname(os.path.abspath(md_path)), "diagrammes")
    os.makedirs(out_dir, exist_ok=True)

    runner = mermaid_runner()
    if runner is None:
        print(
            "mermaid-cli indisponible (ni `mmdc` ni `npx` sur le PATH). "
            "Installer Node.js puis `npm i -g @mermaid-js/mermaid-cli`, ou installer npx. "
            "Les diagrammes restent disponibles en markdown dans le fichier.",
            file=sys.stderr,
        )
        return 1

    rendered, used_names = 0, {}
    for i, m in enumerate(blocks, 1):
        title = heading_before(md, m.start()) or f"diagramme-{i}"
        name = slugify(title, f"diagramme-{i}")
        # eviter les collisions de noms
        if name in used_names:
            used_names[name] += 1
            name = f"{name}-{used_names[name]}"
        else:
            used_names[name] = 1
        png = os.path.join(out_dir, f"{name}.png")
        with tempfile.NamedTemporaryFile("w", suffix=".mmd", delete=False, encoding="utf-8") as tf:
            tf.write(m.group(1).strip() + "\n")
            mmd = tf.name
        try:
            subprocess.run(
                runner + ["-i", mmd, "-o", png, "-b", "white"],
                check=True,
                capture_output=True,
                text=True,
            )
            print(f"  rendu : diagrammes/{name}.png")
            rendered += 1
        except subprocess.CalledProcessError as exc:
            print(f"  echec rendu '{name}': {exc.stderr.strip()[:300]}", file=sys.stderr)
        finally:
            try:
                os.unlink(mmd)
            except OSError:
                pass

    if rendered:
        print(f"{rendered}/{len(blocks)} diagramme(s) rendus dans {out_dir}")
        return 0
    print("Aucun diagramme n'a pu etre rendu.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
