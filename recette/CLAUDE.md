# CLAUDE.md : plugin `recette`

This file provides guidance to Claude Code (claude.ai/code) when working **on the
`recette` plugin** (this directory). Factory-wide overview: `../CLAUDE.md`.

## Ce qu'est le plugin
`recette` = **phase 6** de la Factory (après la livraison d'une feature, en aval de la
validation fonctionnelle). Il comble le trou
post-fabrication : quand le PO teste une feature livrée et trouve un écart, tout devient un
**objet suivi dans Linear** (anomalie ou évolution). La **détection amont** peut aussi venir du
plugin `validation` (recette fonctionnelle : plan de test dérivé de la spec, exécution
navigateur, rapport tracé) : son bilan **renvoie ici** (contenu pré-rempli pour l'anomalie,
simple orientation pour l'évolution) - la **porte de création unique** reste
`creation-anomalie`/`creation-evolution`. Le développeur réalise en
orchestrant les **commandes SpecKit existantes** (`/speckit.clarify`, `/speckit.plan`,
`/speckit.tasks`, `/speckit.implement` cadré) - jamais en les réinventant. Ce sont des
**skills Markdown** ; pas de build/test. **Le plugin n'écrit pas d'artefacts committés** : les
objets de recette vivent dans **Linear** (tickets, statuts, commentaires) et les mises à jour
de spécification dans **`specs/<feature>/`** (repo SpecKit du projet) - pas de `recette-out/`
(comme `couts`, exception assumée au dossier `-out/`, cohérente avec la règle "l'avancement
concurrent ne va jamais dans un fichier committé").

**Frontière de la livraison** (le principe structurant) : avant la livraison, tout est
fabrication et rien ne se trace ; après, tout écart se trace. **Quatre règles d'or** : ne
jamais écraser le travail d'autrui (rouvrir une feature livrée = geste volontaire et tracé),
une vérité partagée remonte au niveau central, pas de clôture sans trace à jour, la
spécification commande et le reste se régénère. Tout est détaillé dans
`references/regles-recette.md`.

## Langue & invocation
- **Tout en français** (skills, gabarits, tickets, interaction). Seuls les identifiants/valeurs
  machine et noms d'outils/formats (Linear, SpecKit, `spec.md`, `tasks.md`) restent tels quels.
- **Skills uniquement, pas de `commands/`**. Invocation : `/recette:<skill>` + auto par le modèle.

## Les 5 skills
- `recette-init` - setup (zéro décision) : installe les 2 gabarits dans `.factory/recette/`,
  étend le manifeste (bloc `recette`, configuration statique seule), complète le `.gitignore`
  (ligne `.factory/`), puis **sonde Linear** (équipe du bloc `linear`, labels
  `Anomalie`/`Evolution` résolus par nom et créés best-effort, statut **"Requalifiée en
  évolution"** vérifié via `list_issue_statuses` - le MCP ne sait pas créer de statut : marche
  à suivre **manuelle** affichée s'il manque). **Jamais bloquant** : signale l'amont manquant
  (tickets Feature absents, pas de `specs/`) sans refuser.
- `creation-anomalie` - **le PO crée une anomalie** (le logiciel ne respecte pas sa
  spécification) : boucle interactive sur le gabarit (attendu, constaté, critère en échec,
  reproduction), **porte de complétude** (aucune section vide), **anti-orphelin** (toujours un
  ticket Feature parent), création `save_issue` (label `Anomalie`, Backlog). **Porte de
  création unique** : un outil de recette automatisé passe par ce même skill (contenu
  pré-rempli, validation humaine finale).
- `correction-anomalie` - **le développeur corrige** : prise en charge (`started`), **tri
  vraie anomalie / évolution déguisée** (si le code respecte la spec -> statut "Requalifiée en
  évolution" + commentaire, **sans créer l'évolution** - geste du PO), **analyse d'impact**
  (feature-map + composants, alerte vérité partagée), **enquête code** (cause racine validée
  par le développeur - pas de `/speckit.clarify` ici), correction sous constitution, et
  **clôture refusée** tant que spec vérifiée + tâches/tests + commentaire Linear ne sont pas à
  jour (`completed` ensuite).
- `creation-evolution` - **le PO crée une évolution** (la spec doit changer) : mêmes portes
  que l'anomalie, plus la section clé **proposition de mise à jour de la spécification** = un
  **écart précis et circonscrit** (exigences nommées, ancré sur `specs/<feature>/spec.md`),
  jamais une réécriture. Label `Evolution`. Lien best-effort vers une anomalie requalifiée.
- `realisation-evolution` - **le développeur réalise, chirurgical** : tri propre/partagé
  (sources lues, jamais jugé de mémoire) qui se termine **toujours par une décision humaine**,
  jamais par un arrêt nu - faux positif tracé, arbitrage déjà rendu et cité, ou arbitrage à
  rendre (**amender le contrat avant la spec** via `/speckit.constitution`, voie recommandée ;
  ou parquer en Backlog avec la condition de reprise nommée), **réouverture volontaire et tracée**
  (confirmation + commentaire Linear - point d'accroche de la future protection
  anti-écrasement côté assembleur), **spec d'abord** (écart seul) -> `/speckit.clarify` ->
  `/speckit.plan` (**plan validé par l'humain**, alerte périmètre) -> `/speckit.tasks` ->
  `/speckit.implement` **cadré au périmètre** -> **preuve de non-régression** (tests feature +
  couplées) -> clôture avec trace complète (`completed`).

## Workspace & manifeste
Lit `specs/<feature>/` (SpecKit), `assembleur-out/feature-map.md`,
`architecte-out/composants.md`, `.specify/memory/constitution.md` et le bloc `linear` du
manifeste (configuration : équipe - les tickets Feature se relèvent dans Linear via
`list_issues({team, label Feature})`). Les **gabarits** vivent dans `.factory/recette/`
(git-ignoré, reposés par `recette-init`) ; le **manifeste** est **committé** dans
`manifest.json`. Bloc `recette` (configuration statique **seulement**) :
`{phase, team, labels{anomalie, evolution}, statut_requalification{name, present}}`.
Écriture = read-modify-write + revalidation JSON. **Aucun état d'avancement dans le
manifeste** : anomalies, évolutions, statuts et commentaires vivent **dans Linear**
(concurrence multi-développeurs), cf. `references/linear-recette.md`.

## Identité des objets (Linear natif, pas de convention de titre)
Pas de numérotation `A0x-F0y` / `E0x-F0y` dans les titres : l'**identifiant natif Linear**
(`<TEAM>-<n>`) porte le numéro. Le **lien à la feature** (clé de l'analyse d'impact) =
**`parentId` vers le ticket `Feature`** posé par `premier-alimente-linear` (désigné par son
`identifier` retrouvé dans Linear, ex. `FAC-12` - `save_issue` l'accepte) + labels plats
**`Anomalie`** / **`Evolution`** (passés par nom via le paramètre `labels`). Écritures d'état
**par nom de statut** (jamais le type brut, ambigu) et **vérifiées sur la réponse** (le MCP
ignore en silence un état inconnu).
**Règle dure anti-orphelin** : pas de ticket Feature rattachable = pas de création.

## Frontière SpecKit (wrapper, jamais de réécriture)
Les skills **orchestrent** les commandes SpecKit au bon moment, ils ne deviennent pas des
commandes SpecKit et ne modifient jamais `.specify/`. Correction d'anomalie : pas de
clarification de besoin (l'enquête est dans le code) ; le code change, la spec non ; plan et
tâches régénérés si besoin depuis la spec inchangée. Réalisation d'évolution : la spec change
d'abord (écart seul), puis `/speckit.clarify`, puis régénération plan + tâches, puis
`/speckit.implement` **cadré**. On ne modifie **jamais** plan ni tâches à la main.

## Conventions partagées
`references/interactive-loop.md`, `references/ux-conventions.md`,
`references/regles-recette.md` (frontière de la livraison, 4 règles d'or, tri
propre/partagé, 4 disciplines chirurgicales, partage humain/automatisé),
`references/linear-recette.md` (usage du MCP linear-prism : détection, installation,
rattachement `parentId`, labels, statut de requalification + marche à suivre manuelle,
`save_issue`/`save_comment`, idempotence, "l'état vit dans Linear").
Garde-fou déterministe : `scripts/check_recette.py` (bloc `recette` + équipe/labels résolus +
statut de requalification déclaré + gabarits en place ; ne force jamais un constat).
Gabarits : `templates/gabarit-anomalie.md`, `templates/gabarit-evolution.md`.

## Vérifications (à la place des tests)
```bash
python -c "import json; json.load(open('.claude-plugin/plugin.json', encoding='utf-8'))"
grep -L "^name:" skills/*/SKILL.md          # doit ne rien retourner
python -m py_compile scripts/check_recette.py
python scripts/check_recette.py <projet>/manifest.json
```

## Invariants
**L'IA propose, l'humain tranche** : la nature d'un écart (anomalie/évolution) est décidée par
le PO à la création ; la cause racine, le plan d'une évolution et la réouverture d'une feature
sont validés par le développeur ; l'ouverture d'une évolution après requalification reste un
geste du PO. **Requalification automatique** (constat technique clair) mais jamais de création
d'évolution automatique. **Jamais de clôture incomplète** (spec + tâches/tests + Linear).
**Chirurgical** : borner, plan validé avant code, implémentation cadrée, non-régression
prouvée. **Aucun état d'avancement dans le manifeste** (Linear est la source de vérité).
**MCP absent = refus clair + instructions d'installation** (jamais d'écriture silencieuse
ratée). Restitutions en prose, manifeste mis à jour en silence ; **typographie humaine** :
aucun glyphe de style IA dans les tickets/commentaires/sorties (pas de tiret cadratin, de
points de suspension unicode, de flèches unicode, de guillemets à chevrons, ni de coche/croix ;
équivalents clavier, cf. la section Typographie de `references/ux-conventions.md`).
