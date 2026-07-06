# Catalogue enforcement — « tests écrits avec le code »

Garde-fou déterministe posé **à la racine du projet** par `architecte-init` (dès l'amorçage de la phase), en miroir de
`conventions/`. Objectif : garantir qu'**aucune source ne part sans son test** (cas passant / échec /
limite), en **défense en profondeur**.

## Ce que l'architecte copie à la racine
- `.claude/settings.json` — hooks Claude Code (partagés, **commités** : c'est l'enforcement de
  l'équipe, distinct d'un `settings.local.json` personnel).
- `.claude/hooks/tests_guard.py` — la logique multi-langage (pur Python + git, sans dépendance).
- `lefthook.yml` — garde-fou pre-commit git.
- `.githooks/` — **protection de branche locale** (`branch_guard.py` + `pre-push` + `pre-commit`),
  posée par `install_branch_protection.py`.

## Protection de branche locale (`.githooks/` + `core.hooksPath`)
Garde-fou git **pur (git + Python, sans dépendance)** qui applique la règle « Aucun push direct sur
`main` » de `standards.md` :
- `pre-push` — **refuse** un push (normal, force-push ou suppression) vers une branche protégée
  (`main`/`master` par défaut ; override via `.githooks/protected-branches`).
- `pre-commit` — **refuse** un commit fait *sur* une branche protégée, puis **relaie** l'enforcement
  de tests (`.claude/hooks/tests_guard.py`) s'il est présent (comportement préservé sans dépendre de lefthook).
- **Pas de blocage du `merge` en local** (choix best practice) : un `pre-merge-commit` casserait
  `git pull` sur `main` (un pull non fast-forward est un merge) et n'est pas idiomatique ; de plus un
  merge **fast-forward** ne crée pas de commit → non interceptable. Le vrai verrou anti-merge
  multi-personnes est un **ruleset serveur GitHub** (require PR + review + CI), **hors** de ce garde-fou local.
- **Activation automatique** : `install_branch_protection.py` pose `git config core.hooksPath .githooks`
  pour le clone courant **et** fusionne un hook **`SessionStart`** dans `.claude/settings.json` qui
  relance cette commande à chaque ouverture de session → **réactivation automatique** pour quiconque
  ouvre le repo dans Claude Code (plus besoin de le lancer à la main). Caveat : la 1ʳᵉ session, Claude
  Code demande la confiance des hooks (un « oui » par personne, une fois).
- **Interaction lefthook** : poser `core.hooksPath` fait de `.githooks/` le système de hooks git ; le
  `pre-commit` ci-dessus rappelle donc lui-même le tests-guard (pas besoin de `lefthook install`).
- **Limite** : **local et contournable** (`--no-verify`), par-clone, sans effet sur un autre clone/CI.
  La vraie protection multi-personnes est un **ruleset serveur GitHub** (require PR + review + check
  CI, block force-push/delete) — **hors** de ce garde-fou local.

## Les couches (du plus faible au non contournable)
1. **Hook Claude Code** (en session) : `PostToolUse` relance dès qu'une source est éditée sans test.
   Actif dès que le fichier `.claude/settings.json` est présent.
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
