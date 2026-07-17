# Catalogue enforcement : "tests écrits avec le code"

Garde-fou déterministe posé **à la racine du projet** par `architecte-init` (dès l'amorçage de la phase), en miroir de
`conventions/`. Objectif : garantir qu'**aucune source ne part sans son test** (cas passant / échec /
limite), en **défense en profondeur**.

## Ce que l'architecte copie à la racine
- `.claude/settings.json` - hooks Claude Code (partagés, **commités** : c'est l'enforcement de
  l'équipe, distinct d'un `settings.local.json` personnel).
- `.claude/hooks/tests_guard.py` - la logique multi-langage (pur Python + git, sans dépendance).
- `.claude/hooks/format_guard.py` - hook `PostToolUse` de **formatage** : à chaque `Write`/`Edit` d'un
  fichier **Python** (`.py`/`.pyi`), lance `ruff format` avec, par ordre de priorité : (1) un fichier
  **`ruff.toml`** dédié s'il existe (`ruff.toml`/`.ruff.toml`, ou l'emplacement Factory
  `conventions/ruff.toml` / `conventions/python/ruff.toml`) - **préférences complètes** ; (2) sinon les
  réglages de **`.editorconfig`** traduits en `--config`. Comble le fait que Claude Code (et ruff) ne
  lisent pas `.editorconfig`. `--no-cache` (pas de `.ruff_cache`), pur Python, **non bloquant** (si
  `ruff` absent -> ignoré). `install_format_hook.py` copie le script **+ `conventions/python/ruff.toml`**
  + fusionne le hook. *(Portée : Python ; extensible.)*
- `lefthook.yml` - garde-fou pre-commit git.

## Protection de branche : côté GitHub (pas de hooks locaux)
La règle "Aucun push direct sur `main`" **n'est plus posée localement** (les hooks git `.githooks/`
ont été retirés). Elle est gérée par un **ruleset serveur GitHub** (require PR + review + check CI,
block force-push/delete) - la **seule** garantie non contournable multi-personnes. La Factory ne pose
aucun hook de branche local (par choix : un hook local est par-clone et contournable `--no-verify`).

## Les couches (du plus faible au non contournable)
1. **Hook Claude Code** (en session) : `PostToolUse` relance dès qu'une source est éditée sans test.
   Actif dès que le fichier `.claude/settings.json` est présent.
2. **Pre-commit git** (`lefthook install`) : rejette un commit ajoutant de la source sans test.
   Contournable avec `--no-verify`.

**Note honnête** : ces deux couches sont **au moment du dev** et donc **contournables** (`--no-verify`,
autre clone). La seule couche **non contournable** multi-personnes serait un **ruleset serveur GitHub**
(require PR + review + check, block force-push/delete) - **à la charge de l'équipe** et **hors périmètre**
de la Factory, qui **ne produit aucune CI**.

## Langages couverts
Python, TS/JS(x), Go, C#, Java. Correspondance test : `test_x.py`/`x_test.py`, `x.test.ts`/`x.spec.ts`,
`x_test.go`, `XTests.cs`/`XTest.cs`, `XTest.java`. Adapter `SKIP_*`/`candidate_test_names` dans
`tests_guard.py` si le projet suit d'autres conventions.

## Notes
- Les hooks appellent `python` (adapter en `py -3` si nécessaire sur Windows). `tests_guard.py`
  retrouve la racine git tout seul (`CLAUDE_PROJECT_DIR` sinon le cwd).
- La *stratégie* de test (quoi tester, comment mocker) vit dans `architecte-out/standards-ingenierie.md` ; ce
  catalogue ne fait que l'**appliquer**.
