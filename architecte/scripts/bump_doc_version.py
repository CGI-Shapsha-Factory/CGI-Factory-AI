#!/usr/bin/env python
"""Incremente le front-matter `version` d'un document architecte (mecanisme de versionnage).

- `py bump_doc_version.py <fichier>` : imprime la PROCHAINE version (version actuelle + 1, ou
   1 si le fichier n'existe pas / n'a pas de front-matter). A lire AVANT de regenerer un doc.
- `py bump_doc_version.py <fichier> --write <AAAA-MM-JJ>` : reecrit en place le front-matter
   (version = actuelle + 1, date = celle donnee), corps inchange. Cree le front-matter s'il
   manque (version 1).

Les ADR sont immuables : ne pas les bumper (ils restent a version 1, evoluent via Statut).
"""
import os
import re
import sys

FENCE = "---"


def read_frontmatter(text):
    """Renvoie (fm_dict, index_ligne_fermeture, lignes) ou (None, 0, None)."""
    if not text.startswith(FENCE):
        return None, 0, None
    lines = text.splitlines(keepends=True)
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == FENCE:
            end = i
            break
    if end is None:
        return None, 0, None
    fm = {}
    for line in lines[1:end]:
        s = line.strip()
        if ":" in s and not s.startswith("#"):
            key, _, val = s.partition(":")
            fm[key.strip()] = val.strip()
    return fm, end, lines


def current_version(path):
    if not os.path.isfile(path):
        return 0
    fm, _, _ = read_frontmatter(open(path, encoding="utf-8").read())
    if not fm:
        return 0
    v = str(fm.get("version", "")).strip()
    return int(v) if v.isdigit() else 0


def main(argv):
    if len(argv) < 2:
        print("usage: bump_doc_version.py <fichier> [--write AAAA-MM-JJ]", file=sys.stderr)
        return 2
    path = argv[1]
    nxt = current_version(path) + 1
    if "--write" in argv:
        idx = argv.index("--write")
        date = argv[idx + 1] if idx + 1 < len(argv) else ""
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", date):
            print("ERREUR: --write attend une date ISO AAAA-MM-JJ", file=sys.stderr)
            return 2
        body = ""
        if os.path.isfile(path):
            text = open(path, encoding="utf-8").read()
            fm, end, lines = read_frontmatter(text)
            body = "".join(lines[end + 1:]) if fm is not None else text
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"---\nversion: {nxt}\ndate: {date}\n---\n" + body)
        print(f"{path}: version {nxt}, date {date}")
    else:
        print(nxt)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
