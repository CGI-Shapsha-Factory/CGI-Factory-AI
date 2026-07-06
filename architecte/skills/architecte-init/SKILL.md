---
name: architecte-init
description: Amorce la phase architecture : crée le dossier conventions, installe les gabarits, pose l'enforcement (hooks de test + protection de branche) et étend le manifeste.
---

# architecte-init

Skill d'amorçage de la phase **architecture** : **tout premier skill** à lancer
après le cadrage. Il prépare le terrain technique sans prendre aucune décision
d'architecture (zéro choix IA). Les autres skills (`architecte`,
`architecte-coherence`) supposent qu'il a tourné.

## Objectif
Rendre un projet **prêt pour la phase technique** : installer les gabarits
d'architecture, créer le dossier `conventions/`, **poser tous les hooks de l'architecte**
(enforcement des tests + protection de branche, déterministe) et étendre le manifeste
partagé avec un bloc `architecture`.

## Ancrage du répertoire (impératif)
**La racine du projet est le dossier courant** — celui où la session est lancée (le
cwd) — **jamais** un dossier parent, **jamais** un `.factory/` / `factory-docs/` /
`*-out/` situé plus haut. Tous les chemins de ce skill (`.factory/manifest.json`,
`.factory/templates/`, `conventions/`, `architecte-out/`, `.claude/`, `.githooks/`,
`lefthook.yml`) se résolvent **sous ce dossier**. **Ne jamais remonter l'arborescence**
pour trouver le manifeste du cadrage : un `.factory/manifest.json` situé dans un dossier
**parent** n'appartient **pas** à ce projet — le traiter comme **absent** (donc refuser
via la porte d'entrée ci-dessous, sans jamais le lire ni l'étendre). En cas de doute sur
un chemin relatif, l'écrire en **absolu à partir du cwd**.

## Porte d'entrée
**Le cadrage doit être prêt.** Lire `.factory/manifest.json` :
- s'il est absent, ou si la phase amont n'est pas prête (le verdict « cadrage
  complet » n'est pas atteint, ou les artefacts clés manquent), **refuser** avec un
  message en clair :
  > « La phase technique ne peut pas démarrer : le cadrage n'est pas encore prêt.
  > Termine d'abord la phase de cadrage (jusqu'au handoff). »
- Vérifier la présence des artefacts cadrage attendus : `cadrage-out/project-frame.md`,
  `cadrage-out/product-brief.md`, `cadrage-out/glossaire.md`, `cadrage-out/spec-index.md`,
  et les briefs sous `cadrage-out/features-fonctionnels-brief/*.brief.md`.

**Refus précis (fichier réellement manquant).** Nommer en clair **ce qui manque** : soit le(s)
**fichier(s) `cadrage-out/…` absent(s), par chemin**, soit le fait que le **verdict cadrage n'est pas
scellé dans le manifeste** (côté amont : relancer `/cadrage:cadrage-completude`, **puis committer
`.factory/manifest.json`**). Rappel : `.factory/manifest.json` **et** `cadrage-out/` doivent avoir été
**committés** par la phase précédente — s'ils manquent du clone, c'est un fichier réellement absent, le dire.

**Idempotent** : ne réécrit aucun fichier existant ; n'installe que le manquant.

## Procédure
1. **Installer les gabarits d'architecture** dans `.factory/templates/` (à côté
   des gabarits de cadrage) : copier depuis le plugin `templates/` :
   `drivers-quality.md`, `components.md`, `tech-stack.md`, `standards.md`,
   `diagrams.md`, `adr.md`, `risks.md`, `design-impact.md`.
2. **Créer le dossier `conventions/`** à la **racine du projet** et y déposer le
   socle universel `.editorconfig` (copie de
   `references/conventions/.editorconfig`). **Les fichiers de conventions par
   langage ne sont PAS installés ici** : le langage n'est connu qu'après le workflow
   stack — c'est le skill `architecte` qui les déposera (voir son étape conventions).
3. **Créer `architecte-out/decisions/`** (dossier des ADR, vide).
4. **Étendre le manifeste** `.factory/manifest.json` : ajouter le bloc
   `architecture` ci-dessous s'il est absent (read-modify-write + revalidation JSON) :

```json
"architecture": {
  "phase": "init",
  "team_profile": null,
  "drivers": [],
  "quality_attributes": [],
  "components": [],
  "stack": {},
  "conventions_installed": [],
  "adrs": [],
  "walking_skeleton": null,
  "feature_sequence": [],
  "risks": [],
  "design_impact": false,
  "env_files": null,
  "test_enforcement": null,
  "coherence_validated": false
}
```

5. **Provisionner le rendu des diagrammes** (silencieux, best-effort, sans prompt) : lancer
   `py -3 "${CLAUDE_PLUGIN_ROOT}/scripts/provision_render.py" <projet>/.factory` (ou `python`
   si `py` est absent). Il détecte un navigateur système (Edge/Chrome) et écrit
   `.factory/puppeteer.json`, puis installe **mermaid-cli épinglé sans télécharger Chromium**
   (la CA du système est respectée, TLS jamais désactivé). S'il ne peut rien installer (hors
   ligne, Node absent), il le dit et **continue** — `render_diagrams.py` retentera au rendu.
6. **Poser l'enforcement (déterministe — TOUS les hooks de l'architecte, dès l'init)** depuis le
   catalogue `references/enforcement/` :
   - **Hook de test** : copier `references/enforcement/.claude/hooks/tests_guard.py` →
     `<racine>/.claude/hooks/tests_guard.py` et `references/enforcement/lefthook.yml` → `<racine>/`,
     puis **fusionner** le hook `PostToolUse` dans `.claude/settings.json` via
     `python "${CLAUDE_PLUGIN_ROOT}/references/enforcement/install_test_hooks.py" <racine>` (relance
     dès qu'une source est éditée sans test ; **sans écraser** un hook `SessionEnd` du compteur de
     coûts). Puis mettre `architecture.test_enforcement = true` dans le manifeste (en silence).
   - **Protection de branche** :
     `python "${CLAUDE_PLUGIN_ROOT}/references/enforcement/install_branch_protection.py" <racine>` — il
     copie `.githooks/` (pur git+Python), pose `git config core.hooksPath .githooks` pour ce clone **et
     fusionne un hook `SessionStart`** qui le réactive à chaque session (auto pour toute l'équipe) ;
     il écrit `architecture.branch_protection` au manifeste. Refuse le push/commit direct sur
     `main`/`master`.
   - Adapter `python` → `py -3` si besoin. Confirmer en clair. *(Caveats honnêtes : la 1ʳᵉ session,
     Claude Code demande la confiance des hooks — un « oui » par personne, une fois ; un dev hors
     Claude Code ou un `--no-verify` contourne ; la seule barrière non contournable multi-personnes est
     un **ruleset serveur GitHub** + check CI ; le backstop CI diff-coverage requis est produit par
     l'assembleur.)*

## Porte de sortie
- `conventions/` existe à la racine avec `.editorconfig`.
- Les 8 gabarits d'architecture (dont `design-impact.md`) sont dans `.factory/templates/`.
- `architecte-out/decisions/` existe.
- Le manifeste contient le bloc `architecture` (`phase: "init"`), et reparse sans erreur.
- Rendu diagrammes provisionné (best-effort) : `.factory/puppeteer.json` écrit si un
  navigateur système est présent, mermaid-cli installé si possible — non bloquant.
- **Enforcement posé** : `.claude/hooks/tests_guard.py` + hook `PostToolUse` dans
  `.claude/settings.json` ; `.githooks/` + `core.hooksPath` + hook `SessionStart` ; manifeste
  `test_enforcement: true` + bloc `branch_protection`.
- Rien d'existant n'a été écrasé (idempotence).

## Règles invariantes
- **Aucune décision IA.** Ce skill prépare ; il ne classe pas de drivers, ne choisit
  pas de composants ni de stack. (Installer l'outillage de rendu des diagrammes **et
  l'enforcement des tests / la protection de branche** est de la préparation déterministe,
  pas une décision d'architecture.)
- **Skill indépendant.** La cohérence passe par le manifeste partagé.

Étape suivante : `/architecte:architecte-contrat` — construire le contrat technique (drivers, composants, stack, ADR, walking skeleton, diagrammes).
