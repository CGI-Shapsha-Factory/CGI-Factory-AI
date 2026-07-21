#!/usr/bin/env python
"""Hook UserPromptExpansion : sert la carte de la Factory sans passer par le modele.

Branche sur /cadrage:help-factory. Il bloque l'expansion de la commande et rend la carte
directement a l'utilisateur : le prompt n'atteint jamais le modele, donc zero token de sortie
et aucune latence de generation.

La source unique reste skills/help-factory/SKILL.md : on en extrait la partie affichable
(tout ce qui suit le marqueur MARKER). Le texte rendu par un hook n'est PAS interprete comme
du markdown - les tableaux pipe et les ** s'afficheraient tels quels -, donc on convertit en
colonnes alignees avant de le rendre. Le SKILL.md, lui, reste en markdown : c'est le chemin
de repli quand les hooks sont desactives.

Si quoi que ce soit echoue, on sort en silence pour laisser l'expansion normale reprendre la
main - une aide degradee vaut mieux qu'une aide cassee.
"""
import json
import os
import re
import sys
import textwrap
from itertools import zip_longest

MARKER = "## A afficher tel quel"
SKILL = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     "skills", "help-factory", "SKILL.md")

WIDTH = 96          # largeur de rendu, confortable dans un terminal standard
NAME_W = 28         # colonne du nom de skill (le plus long en fait exactement 28)
ROLE_W = WIDTH - NAME_W - 7     # le reste, une fois retires les bordures et separateurs


def sans_accent(text):
    for a, b in (("à", "a"), ("é", "e"), ("è", "e"), ("ê", "e"), ("ô", "o"), ("û", "u")):
        text = text.replace(a, b)
    return text


def nettoie(text):
    """Retire la syntaxe markdown qui ne serait pas interpretee a l'affichage."""
    text = text.replace("**", "").replace("`", "")
    text = re.sub(r"(?<!\w)\*(\S(?:.*?\S)?)\*(?!\w)", r"\1", text)   # italiques
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)             # liens
    return text.strip()


def cellules(ligne):
    return [c.strip() for c in ligne.strip().strip("|").split("|")]


def plie(texte, largeur):
    """Habille un texte. Sans coupure sur les tirets : les chemins doivent rester entiers."""
    return textwrap.wrap(texte, largeur, break_on_hyphens=False)


def rangee(gauche, droite):
    return "| " + gauche.ljust(NAME_W) + " | " + droite.ljust(ROLE_W) + " |"


def rend_tableau(lignes, titre):
    """Encadre un tableau markdown : une ligne par skill, nom puis role. Rien d'autre."""
    entetes = [c.lower() for c in cellules(lignes[0])]
    i_nom = next((i for i, h in enumerate(entetes) if h == "skill"), 0)
    i_porte = next((i for i, h in enumerate(entetes) if h.startswith("porte")), len(entetes) - 1)
    # colonne "#" (numerote des lignes deja ordonnees) et colonne porte : hors sujet ici
    ignores = {i_nom, i_porte} | {i for i, h in enumerate(entetes) if h in ("#", "")}
    separateur = "+" + "-" * (NAME_W + 2) + "+" + "-" * (ROLE_W + 2) + "+"
    entete = "-- " + titre + " " if titre else "-"
    sortie = ["+" + entete + "-" * (WIDTH - 2 - len(entete)) + "+",
              rangee("skill", "role"), separateur]
    for ligne in lignes[2:]:                                        # [1] = separateur |---|
        cols = cellules(ligne)
        if len(cols) <= i_nom:
            continue
        nom = plie(nettoie(cols[i_nom]), NAME_W) or [""]
        role = " ".join(nettoie(c) for j, c in enumerate(cols) if j not in ignores and nettoie(c))
        role = plie(role, ROLE_W) or [""]
        # une rangee par skill, sur autant de lignes que necessaire, puis un trait de separation
        for g, d in zip_longest(nom, role, fillvalue=""):
            sortie.append(rangee(g, d))
        sortie.append(separateur)
    return sortie + [""]


def rend(body):
    """Ne garde que les tableaux de skills, encadres et titres par leur phase."""
    lignes = body.splitlines()
    sortie, titre, i = [], "", 0
    while i < len(lignes):
        ligne = lignes[i]
        if ligne.startswith("#"):
            titre = nettoie(ligne.lstrip("#")).replace(" : ", " : ")
            i += 1
            continue
        if ligne.lstrip().startswith("|"):
            bloc = []
            while i < len(lignes) and lignes[i].lstrip().startswith("|"):
                bloc.append(lignes[i])
                i += 1
            if len(bloc) >= 3:
                sortie.extend(rend_tableau(bloc, titre))
            titre = ""
            continue
        i += 1                                                      # prose : ignoree
    return "\n".join(sortie).strip() + "\n"


def carte(text):
    """Renvoie la partie affichable du SKILL.md, sans frontmatter ni consignes internes."""
    cible = sans_accent(MARKER.lstrip("#").strip().lower())
    for i, ligne in enumerate(text.splitlines()):
        if sans_accent(ligne.strip().lstrip("#").strip().lower()) == cible:
            return "\n".join(text.splitlines()[i + 1:]).strip()
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
    payload = json.dumps({"decision": "block", "reason": rend(body)}, ensure_ascii=False)
    # ecriture en octets : la sortie console Windows est en cp1252 et ne sait pas encoder les accents
    sys.stdout.buffer.write(payload.encode("utf-8"))
    sys.stdout.buffer.flush()
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:  # noqa: BLE001 - un hook casse ne doit jamais casser l'aide
        sys.exit(0)
