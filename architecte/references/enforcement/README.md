# Catalogue enforcement — « tests écrits avec le code »

Garde-fou déterministe posé **à la racine du projet** par l'architecte (Étape 11), en miroir de
`conventions/`. Objectif : garantir qu'**aucune source ne part sans son test** (cas passant / échec /
limite), en **défense en profondeur**.

## Ce que l'architecte copie à la racine
- `.claude/settings.json` — hooks Claude Code (partagés, **commités** : c'est l'enforcement de
  l'équipe, distinct d'un `settings.local.json` personnel).
- `.claude/hooks/tests_guard.py` — la logique multi-langage (pur Python + git, sans dépendance).
- `lefthook.yml` — garde-fou pre-commit git.

## Les couches (du plus faible au non contournable)
1. **Hooks Claude Code** (en session) : `PostToolUse` relance dès qu'une source est éditée sans test ;
   **`Stop` bloque la fin de tour** (exit 2) tant qu'une source modifiée n'a pas de test. Actifs dès
   que le fichier `.claude/settings.json` est présent.
2. **Pre-commit git** (`lefthook install`) : rejette un commit ajoutant de la source sans test.
   Contournable avec `--no-verify`.
3. **CI diff-coverage requis** (produit par l'**assembleur** dans le paquet) : **la seule couche non
   contournable** — à poser comme *required status check* sur la branche.

## Langages couverts
Python, TS/JS(x), Go, C#, Java. Correspondance test : `test_x.py`/`x_test.py`, `x.test.ts`/`x.spec.ts`,
`x_test.go`, `XTests.cs`/`XTest.cs`, `XTest.java`. Adapter `SKIP_*`/`candidate_test_names` dans
`tests_guard.py` si le projet suit d'autres conventions.

## Notes
- Les hooks appellent `python` (adapter en `py -3` si nécessaire sur Windows). `tests_guard.py`
  retrouve la racine git tout seul (`CLAUDE_PROJECT_DIR` sinon le cwd).
- La *stratégie* de test (quoi tester, comment mocker) vit dans `architecte-out/standards.md` ; ce
  catalogue ne fait que l'**appliquer**.
