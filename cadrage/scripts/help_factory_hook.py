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

MARKER = "## A afficher tel quel"
SKILL = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     "skills", "help-factory", "SKILL.md")

WIDTH = 96          # largeur de rendu, confortable dans un terminal standard
NAME_COL = 30       # colonne du nom de skill
INDENT = "  "


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


def plie(texte, largeur=None):
    """Habille un texte. Sans coupure sur les tirets : les chemins doivent rester entiers."""
    return textwrap.wrap(texte, largeur or (WIDTH - NAME_COL), break_on_hyphens=False)


def rend_tableau(lignes):
    """Transforme un tableau markdown en lignes alignees : nom, role, puis la porte."""
    entetes = [c.lower() for c in cellules(lignes[0])]
    i_nom = next((i for i, h in enumerate(entetes) if h == "skill"), 0)
    i_porte = next((i for i, h in enumerate(entetes) if h.startswith("porte")), len(entetes) - 1)
    # la colonne "#" ne sert qu'a numeroter des lignes deja dans l'ordre : elle parasite le rendu
    ignores = {i_nom, i_porte} | {i for i, h in enumerate(entetes) if h in ("#", "")}
    sortie, marge = [], " " * NAME_COL
    for ligne in lignes[2:]:                                        # [1] = separateur |---|
        cols = cellules(ligne)
        if len(cols) <= i_nom:
            continue
        nom = nettoie(cols[i_nom])
        porte = nettoie(cols[i_porte]) if i_porte != i_nom and len(cols) > i_porte else ""
        role = " ".join(nettoie(c) for j, c in enumerate(cols) if j not in ignores and nettoie(c))
        corps = plie(role) or [""]
        if len(nom) > NAME_COL - 2:                                 # nom trop long : role en dessous
            sortie.append(INDENT + nom)
        else:
            sortie.append(INDENT + nom.ljust(NAME_COL - 2) + "  " + corps.pop(0))
        sortie.extend(INDENT + marge + suite for suite in corps)
        if porte:
            # crochets et non parentheses : la porte contient deja souvent un "(humain)"
            sortie.extend(INDENT + marge + suite for suite in plie("[" + porte + "]"))
        sortie.append("")
    return sortie


def rend(body):
    """Convertit la carte markdown en texte aligne lisible sans rendu markdown."""
    lignes = body.splitlines()
    sortie, i = [], 0
    while i < len(lignes):
        ligne = lignes[i]
        if ligne.lstrip().startswith("|"):
            bloc = []
            while i < len(lignes) and lignes[i].lstrip().startswith("|"):
                bloc.append(lignes[i])
                i += 1
            if len(bloc) >= 3:
                sortie.extend(rend_tableau(bloc))
            continue
        if ligne.startswith("#"):
            titre = nettoie(ligne.lstrip("#")).upper()
            sortie.extend(["", titre, "=" * min(len(titre), WIDTH)])
            i += 1
            continue
        if not ligne.strip():
            if sortie and sortie[-1]:
                sortie.append("")
            i += 1
            continue
        # paragraphe : on recolle les lignes jusqu'au prochain saut, puis on rehabille
        bloc = []
        while i < len(lignes) and lignes[i].strip() and not lignes[i].lstrip().startswith(("|", "#")):
            bloc.append(lignes[i].strip())
            i += 1
        texte = nettoie(" ".join(bloc)).strip('"')
        sortie.extend(plie(texte, WIDTH))
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
