---
name: architecte-init
description: Amorce la phase architecture : crée le dossier conventions, installe les gabarits, pose l'enforcement (hooks de test + formatage) et étend le manifeste.
---

# architecte-init

Skill d'amorçage de la phase **architecture** : à lancer au démarrage de la phase
technique (idéalement après le cadrage — mais le socle technique s'installe **même si le
cadrage n'est pas encore là**). Il prépare le terrain sans prendre aucune décision
d'architecture (zéro choix IA). Les autres skills (`architecte-fondations`,
`architecte-stack`, `architecte-livrables`, `architecte-coherence`) supposent qu'il a tourné.

## Objectif
Rendre un projet **prêt pour la phase technique** : installer les gabarits
d'architecture, créer le dossier `conventions/`, **poser les hooks de l'architecte**
(enforcement des tests + formatage, déterministe) et étendre le manifeste
partagé avec un bloc `architecture`.

## Ancrage du répertoire (impératif)
**La racine du projet est le dossier courant** — celui où la session est lancée (le
cwd) — **jamais** un dossier parent, **jamais** un `.factory/` / `factory-docs/` /
`*-out/` situé plus haut. Tous les chemins de ce skill (`manifest.json`,
`.factory/architecte/`, `conventions/`, `architecte-out/`, `.claude/`,
`lefthook.yml`) se résolvent **sous ce dossier**. **Ne jamais remonter l'arborescence**
pour trouver le manifeste du cadrage : un `manifest.json` situé dans un dossier
**parent** n'appartient **pas** à ce projet — le traiter comme **absent** (ne jamais le lire
ni l'étendre ; on crée/étend le manifeste **du cwd**, cf. procédure). En cas de doute sur
un chemin relatif, l'écrire en **absolu à partir du cwd**.

## `.factory/` d'abord — clone frais, `.factory/` git-ignoré (impératif)
`.factory/` est **entièrement git-ignoré** : il ne voyage **jamais** avec le repo. Cette phase peut être
menée par **une autre personne**, sur une **autre machine**, à partir d'un **clone frais** où **aucun
`.factory/` n'existe encore**. Ce skill ne présuppose donc **jamais** un `.factory/` déjà présent :
**avant toute autre chose**, il (re)pose dans `.factory/` **tout ce dont la phase a besoin** — les
gabarits d'architecture (`.factory/architecte/`) et le bloc `architecture` du manifeste
`manifest.json` (créé s'il manque). Le **handoff** entre phases passe **uniquement** par les
dossiers `-out/` committés, jamais par `.factory/` (régénérable en relançant ce `-init`).

## Setup inconditionnel + état du cadrage (jamais bloquant)
**Ce skill ne bloque jamais.** Tout le setup technique — gabarits, `conventions/`, hooks
d'enforcement, provisionnement du rendu, bloc `architecture` du manifeste — est **déterministe et
sans dépendance au cadrage** : il s'installe **toujours**, dans le dossier courant, que le cadrage
soit là ou non. **Ne jamais refuser** au motif que le cadrage manque.

Après le setup, **vérifier l'état du cadrage** dans le cwd (présence, par chemin, de) :
`manifest.json` (verdict cadrage scellé), `cadrage-out/project-frame.md`,
`cadrage-out/product-brief.md`, `cadrage-out/glossaire.md`, `cadrage-out/spec-index.md`, et les
briefs `cadrage-out/features-fonctionnels-brief/*.md`. Puis :

- **Cadrage présent et prêt** → rien à signaler ; enchaîner sur `/architecte:architecte-fondations`.
- **Cadrage absent ou incomplet** → **ne pas refuser**. Confirmer que le socle technique est posé,
  puis **avertir en clair** ce qui manque (par chemin) et la marche à suivre :
  > « Socle technique installé (gabarits + hooks + conventions). En revanche, le **cadrage n'est pas
  > encore là** dans ce dossier : `cadrage-out/…` manquant(s). La **construction** du contrat technique
  > (`/architecte:architecte-fondations`) a besoin du cadrage. Lance la phase de cadrage
  > (`/cadrage:cadrage-init` → … → `/cadrage:cadrage-completude`), puis reviens à
  > `/architecte:architecte-fondations`. »

But : **poser tout ce qui est installable maintenant**, jamais bloquer sur le cadrage, et laisser
l'utilisateur décider de la suite.

**Idempotent** : ne réécrit aucun fichier existant ; n'installe que le manquant.

## Procédure
1. **Installer les gabarits d'architecture** dans `.factory/architecte/` : copier depuis le plugin `templates/` :
   `facteurs-et-qualite.md`, `composants.md`, `stack-technique.md`, `standards-ingenierie.md`,
   `diagrammes.md`, `adr.md`, `risques.md`, `impact-design.md`.
2. **Créer le dossier `conventions/`** à la **racine du projet** et y déposer :
   - le socle universel `.editorconfig` (copie de `references/conventions/.editorconfig`) ;
   - **la config du formateur Python** `conventions/python/ruff.toml` (copie de
     `references/conventions/python/ruff.toml`) — c'est le fichier que le **hook de formatage**
     (étape 6) passe à `ruff format --config` (préférences complètes, alignées sur `.editorconfig`).
     On l'installe dès l'init car le hook de formatage est **centré Python**. *(Extensible : d'autres
     formateurs viendront avec leur langage.)*

   **Les autres configs de conventions par langage** (biome/eslint pour TS-JS, clang pour C…) **ne
   sont PAS installées ici** : la stack n'est connue qu'après le workflow stack — c'est
   `architecte-stack` qui les déposera (voir son étape conventions).
3. **Créer `architecte-out/decisions/`** (dossier des ADR, vide).
4. **Manifeste** `manifest.json` **du dossier courant** :
   - **S'il existe** → ajouter le bloc `architecture` ci-dessous s'il est absent (read-modify-write
     + revalidation JSON), **sans toucher aux autres blocs**.
   - **S'il n'existe pas** (cadrage pas encore lancé ici) → **créer d'abord le dossier `cadrage-out/`
     s'il est absent** (même sans cadrage), puis y **créer** le manifeste comme objet JSON valide
     `{ "architecture": { … } }` contenant au minimum le bloc ci-dessous. **Ne pas fabriquer de faux
     blocs de cadrage** : `cadrage-init` complétera le manifeste plus tard **par fusion** (il ajoute
     ses clés manquantes sans écraser le bloc `architecture`).

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
   si `py` est absent). Il détecte un navigateur système (Edge/Chrome — pour le PNG optionnel),
   puis installe le **binaire D2 épinglé** en espace utilisateur (`.factory/d2/`, **sans admin**,
   sans télécharger de Chromium ; la CA du système est respectée, TLS jamais désactivé). S'il ne
   peut rien installer (hors ligne), il le dit et **continue** — `render_diagrams.py` retentera au
   rendu (repli Kroki local).
6. **Poser l'enforcement (déterministe — TOUS les hooks de l'architecte, dès l'init)** depuis le
   catalogue `references/enforcement/` :
   - **Hook de test** : lancer **une seule commande**
     `python "${CLAUDE_PLUGIN_ROOT}/references/enforcement/install_test_hooks.py" <racine>` — elle
     **copie elle-même** `tests_guard.py` → `<racine>/.claude/hooks/` **et** `lefthook.yml` →
     `<racine>/` (sans écraser), **puis fusionne** le hook `PostToolUse` dans `.claude/settings.json`
     (relance dès qu'une source est éditée sans test ; **sans écraser** un hook `SessionEnd` du
     compteur de coûts). **Ne jamais copier ces fichiers à la main** : le script est la source
     déterministe — sinon le hook enregistré pointerait vers un script absent (hook mort). Puis mettre
     `architecture.test_enforcement = true` dans le manifeste (en silence).
   - **Hook de formatage** : lancer **une seule commande**
     `python "${CLAUDE_PLUGIN_ROOT}/references/enforcement/install_format_hook.py" <racine>` — elle
     **copie** `format_guard.py` → `<racine>/.claude/hooks/` (sans écraser) **puis fusionne** un
     second hook `PostToolUse` dans `.claude/settings.json` (**sans écraser** les hooks existants —
     tests_guard, SessionEnd coûts). À chaque `Write`/`Edit` d'un fichier **Python** (`.py`/`.pyi`),
     il applique le formatage : il **lit le `.editorconfig`** applicable (line-length, indent, fins de
     ligne) et le traduit en options `ruff format --config`. Claude Code ne lit pas `.editorconfig`
     lui-même — ce hook fait le pont. Best-effort et **non bloquant** : si `ruff` est absent, il
     l'indique et n'échoue pas. *(Portée actuelle : Python. Extensible à d'autres langages/formateurs.)*
   - *(Pas de protection de branche locale.* La règle « aucun push direct sur `main` » est gérée par un
     **ruleset serveur GitHub**, pas par des hooks git locaux — ceux-ci ont été retirés de la Factory.)*
   - Adapter `python` → `py -3` si besoin. Confirmer en clair. *(Caveat : la 1ʳᵉ session, Claude Code
     demande la confiance des hooks — un « oui » par personne, une fois.)*
7. **Git-ignore `.factory/` (compléter, jamais réécrire)** : le **`.gitignore` est généré en premier
   par le cadrage** (`cadrage-init`) et **committé** — il voyage avec le repo, donc présent dans un clone
   frais. Ici, **ne jamais le réécrire ni l'écraser** : s'assurer seulement qu'il **contient** la ligne
   `.factory/` — l'**ajouter** si elle manque (sans dupliquer), en **préservant** tout le reste du
   fichier. **Le créer uniquement s'il est absent** (clone où le cadrage n'a pas tourné dans ce dossier).
   Tout `.factory/` est local, non versionné.

## Porte de sortie
- `conventions/` existe à la racine avec `.editorconfig`.
- Les 8 gabarits d'architecture (dont `impact-design.md`) sont dans `.factory/architecte/`.
- `.gitignore` contient la ligne `.factory/`.
- `architecte-out/decisions/` existe.
- Le manifeste contient le bloc `architecture` (`phase: "init"`), et reparse sans erreur.
- Rendu diagrammes provisionné (best-effort) : binaire **D2** installé dans `.factory/d2/` si
  possible (sans admin), navigateur système détecté pour le PNG optionnel — non bloquant.
- **Enforcement posé** : `.claude/hooks/tests_guard.py` + `.claude/hooks/format_guard.py` + **deux**
  hooks `PostToolUse` (test + formatage) dans `.claude/settings.json` ; manifeste `test_enforcement: true`.
  *(Aucune protection de branche locale — gérée côté GitHub.)*
- **État du cadrage signalé** : si `cadrage-out/` manque, l'utilisateur a été **averti** (pas
  bloqué) que la construction du contrat a besoin du cadrage.
- Rien d'existant n'a été écrasé (idempotence).

## Message de fin (ordre imposé)
Après le setup, afficher **dans cet ordre exact** :

1. le **récapitulatif** du socle installé (table courte) ;
2. **AVANT toute autre chose**, et **en gras, bien visible**, l'**avertissement de redémarrage de
   session** — les hooks Claude Code (`PostToolUse` de test + de formatage)
   ne deviennent actifs qu'au **démarrage** d'une session ; ceux qu'on vient d'installer **ne le sont
   pas encore** dans la session courante. Afficher exactement, en gras :

   > **⚠️ REDÉMARRE LA SESSION pour que les hooks prennent effet.**
   >
   > **1. `/exit`**
   > **2. relance `claude` dans le terminal**
   > **3. reprends la session (`claude --resume`, puis choisis cette session)**

3. **seulement après** ce bloc de redémarrage, **si le cadrage manque**, l'avertissement « Cadrage
   absent » et la marche à suivre (`/cadrage:cadrage-init` → … → `/cadrage:cadrage-completude`).

**Ne jamais** afficher l'avertissement « Cadrage absent » avant le bloc de redémarrage : le
redémarrage est prioritaire (sans lui, l'enforcement ne tourne pas).

## Règles invariantes
- **Aucune décision IA.** Ce skill prépare ; il ne classe pas de drivers, ne choisit
  pas de composants ni de stack. (Installer l'outillage de rendu des diagrammes **et
  l'enforcement des tests** est de la préparation déterministe,
  pas une décision d'architecture.)
- **Jamais bloquant.** Le setup s'installe toujours ; l'absence de cadrage **avertit**, ne refuse pas.
- **Manifeste silencieux.** Ne jamais annoncer que le manifeste est créé/mis à jour ni afficher un
  `champ: valeur`/`true`/`false` ; confirmer en clair le socle installé + la suite (cf.
  `references/ux-conventions.md`).
- **Skill indépendant.** La cohérence passe par le manifeste partagé.

Étape suivante : `/architecte:architecte-fondations` — poser les fondations du contrat technique (lire le cadrage, drivers & attributs de qualité, composants).
