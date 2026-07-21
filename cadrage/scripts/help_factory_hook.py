#!/usr/bin/env python
"""Hook UserPromptExpansion : sert la carte de la Factory sans passer par le modele.

Branche sur /cadrage:help-factory. Il bloque l'expansion de la commande et rend la carte
directement a l'utilisateur : le prompt n'atteint jamais le modele, donc zero token de sortie
et aucune latence de generation.

La source unique reste skills/help-factory/SKILL.md : on en extrait la partie affichable
(tout ce qui suit le marqueur MARKER). Si quoi que ce soit echoue, on sort en silence pour
laisser l'expansion normale reprendre la main - une aide degradee vaut mieux qu'une aide cassee.
"""
import json
import os
import sys

MARKER = "## A afficher tel quel"
SKILL = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     "skills", "help-factory", "SKILL.md")


def carte(text):
    """Renvoie la partie affichable du SKILL.md, sans frontmatter ni consignes internes."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        # comparaison sans accents : le marqueur porte un "A" accentue dans le fichier
        if line.strip().lstrip("#").strip().lower().replace("à", "a") == \
                MARKER.lstrip("#").strip().lower():
            return "\n".join(lines[i + 1:]).strip()
    return None


def main():
    try:
        sys.stdin.read()  # vider le pipe du hook, son contenu ne sert pas ici
    except (OSError, ValueError):
        pass
    try:
        with open(SKILL, encoding="utf-8-sig") as fh:
            body = carte(fh.read())
    except OSError:
        return 0
    if not body:
        return 0
    payload = json.dumps({"decision": "block", "reason": body}, ensure_ascii=False)
    # ecriture en octets : la sortie console Windows est en cp1252 et ne sait pas encoder les accents
    sys.stdout.buffer.write(payload.encode("utf-8"))
    sys.stdout.buffer.flush()
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:  # noqa: BLE001 - un hook casse ne doit jamais casser l'aide
        sys.exit(0)
