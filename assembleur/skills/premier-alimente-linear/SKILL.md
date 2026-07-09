---
name: premier-alimente-linear
description: Première alimentation de Linear — transforme les features approuvées en tickets Linear (un par feature, label Feature), avec confirmation ticket par ticket, via le MCP linear-prism — juste avant install-speckit. Les sous-tickets par phase (label Task) sont créés plus tard par creation-task-linear, après /speckit.tasks.
---

# premier-alimente-linear

**Pont vers Linear.** À lancer **après `assembleur-convergence`** (le paquet est produit, la
cohérence validée, les features **déjà approuvées**) et **avant `install-speckit`**. Ce skill lit
la liste des features, la présente en **tableau de revue**, puis — **ticket par ticket, avec
confirmation** — crée **un ticket Linear par feature** pour que l'équipe pilote la fabrication
SpecKit feature par feature.

## Objectif
Créer, dans Linear, **un ticket par feature approuvée** : un **titre**, une **description d'une
ligne**, et — pour une feature **volumineuse** — une **liste de contrôle** (cases à cocher dans l'issue) pour suivre
l'avancement. Chaque ticket est **confirmé avant création**. Idempotent : on ne recrée jamais un
ticket déjà posé.

## Frontière (exception assumée)
L'assembleur ne produit que son paquet (`assembleur-out/`) et **n'écrit jamais dans le repo cible**.
Créer des tickets Linear est une **exception explicitement bornée** à « pas de Linear » : Linear est
un **système externe** (pas le repo cible, pas un fichier que SpecKit génère). La seule écriture
propre à la Factory est le bloc `linear` du manifeste. La création passe par le **MCP du plugin
`linear-prism`** (externe à la Factory) — voir `references/linear-guide.md`.

## Pré-requis (vérification silencieuse)
Lire `manifest.json` **sans l'annoncer** :
- la convergence a tourné et la **cohérence est validée**, et le paquet est présent
  (`assembleur-out/feature-map.md` + au moins une graine `assembleur-out/features/*.md`) ;
- sinon → le dire en clair et orienter vers `/assembleur:assembleur-convergence` :
  > « Les tickets ne peuvent pas être créés : il faut d'abord la convergence terminée et la
  > cohérence validée (le paquet de features approuvées). »

Le registre des features est `architecture.feature_sequence` (`{id, ucs, name}` + le
`walking_skeleton`). **Ne rien inventer** : on ne crée de ticket que pour les features approuvées.

## Étape 1 — Détecter Linear (MCP linear-prism)
Sonder `mcp__plugin_linear-prism_linear__list_teams` (cf. `references/linear-guide.md`).
- Disponible → continuer.
- Indisponible → **ne rien créer** : refuser en clair (« Je ne peux pas créer de tickets Linear :
  le MCP `linear-prism` n'est pas disponible. ») et afficher les **instructions d'installation**
  (section « Installation du plugin linear-prism » de `references/linear-guide.md` : marketplace,
  `/plugin install`, redémarrage, `/mcp`). Installer puis **relancer** une fois authentifié.

## Étape 2 — Charger et présenter les features (tableau de revue)
Lire `architecture.feature_sequence`, `assembleur-out/feature-map.md` (ordre, couplage, **Dépend
de**, parallélisable) et chaque graine `assembleur-out/features/<id>-*.md` (User Stories,
`FR-xxx`, `SC-xxx`, cas limites). Afficher **un tableau de revue unique** (c'est l'exception au
« pas de tableau » — une revue, comme `feature-map.md`) :

| Ordre | Feature | Use cases | Walking skeleton | Dépend de | Titre proposé | Description (1 ligne) | Volumineuse ? |
|-------|---------|-----------|------------------|-----------|---------------|-----------------------|---------------|

Puis **demander (oui/non) : « Créer un ticket par feature ? »**
- **Oui** → passer à l'Étape 3.
- **Non** → **boucle d'ajustement** (un point à la fois, cf. `references/interactive-loop.md` :
  recommandée + alternative + « saisir ») : quelles features **fusionner / renommer / écarter /
  réordonner** ? Refléter chaque décision (consigner `status: "merged"`/`"skipped"` pour celles
  écartées), **réafficher** le tableau, et **confirmer l'ensemble** avant de créer.

## Étape 3 — Cible Linear (une seule fois)
Choisir l'**équipe** (`list_teams` → recommandée + alternative + saisir) et, optionnellement, le
**projet** (`list_projects`), l'**état initial** (Todo/unstarted). Consigner `team`/`project` dans
le manifeste **en silence**. Détails : `references/linear-guide.md`.

## Étape 4 — Boucle par ticket (un à la fois, confirmation obligatoire)
Pour **chaque** feature retenue, **dans l'ordre** :
1. **Préparer** : un **titre** (intitulé métier, ex. `001 — Recherche Q&A sourcée`), une
   **description d'une ligne** (parcours principal / rôle de la feature, depuis la graine), et — si
   la feature est **volumineuse** — une **liste de contrôle** = cases à cocher (`- [ ] …`) à
   inclure dans la **description** de l'issue (dérivées des `FR-xxx` / scénarios d'acceptation /
   `SC-xxx`). **Volumineuse** = bundle **> 1 use case** (`ucs`), **ou** ≥ 4 exigences
   fonctionnelles, **ou** ≥ 2 user stories dans la graine.
2. **Confirmer** (recommandée + ajuster + saisir) : le **titre**, la **description d'une ligne**,
   et **la liste de contrôle (seulement si volumineuse)**. **Ne rien créer** tant que ce
   n'est pas approuvé ; « ajuster »/« saisir » corrige en place.
3. **Créer** (cf. `references/linear-guide.md`) : `save_issue({team, title, description: <1 ligne
   + '\n\n**Checklist :**\n- [ ] item…'>, labels, state})` → récupérer `identifier`/`url`. La
   liste de contrôle est dans la `description` (Markdown `- [ ] item` — Linear les rend
   interactifs, pas de sous-ticket ici — les vrais sous-tickets par phase viennent plus tard, via
   `creation-task-linear`). Poser les **relations bloquantes** (`blockedBy`) d'après « Dépend de ».
   Labels : **`Feature`** (label plat de taxonomie, **résolu par nom** via `list_issue_labels`, jamais
   créé ici) + `feature:<id>` (clé de jointure) (+ `walking-skeleton` si concerné) — **jamais `MVP`**.
4. **Consigner** dans `linear.issues[]` (en silence), puis **passer à la feature suivante**.
   **Répéter jusqu'à ce que toutes soient traitées.**

**Idempotence** : une feature déjà consignée avec un `issue_id` n'est **pas recréée**.

## Vérification avant de conclure
- Chaque feature approuvée a **son ticket** (ou une décision `skipped`/`merged`) ; les grosses
  features ont leur **liste de contrôle** dans la description ; les **dépendances** sont posées.
- Lancer le garde-fou : `python "${CLAUDE_PLUGIN_ROOT}/scripts/check_linear.py" <racine>/manifest.json`.
- Le bloc `linear` du manifeste **reparse sans erreur** ; restitution **en prose** (« j'ai créé N
  tickets, un par feature »), manifeste mis à jour **en silence**.

## Règles invariantes
- **Exception Linear bornée.** On n'écrit que dans Linear (externe) + le bloc `linear` du manifeste ;
  jamais dans le repo cible.
- **Confirmer avant de créer.** Chaque ticket est validé par l'humain avant création (action
  externe, difficile à défaire).
- **Un point à la fois.** Questions et confirmations en prose, une par une (cf.
  `interactive-loop.md`) ; le seul tableau autorisé est le tableau de revue de l'Étape 2.
- **Idempotent.** On ne crée jamais deux fois le même ticket.
- **Rien d'inventé.** Seulement les features approuvées par la convergence.
- **Manifeste en silence.** Aucun nom de clé à l'écran ; restitution en prose.

Étape suivante : `/assembleur:install-speckit` — poser SpecKit dans le repo, puis fabriquer feature par feature (chaque ticket Linear pilote un cycle `/speckit.specify` → `/speckit.plan` → `/speckit.tasks` → `/speckit.implement`). **Après `/speckit.tasks`** (une fois `specs/<feature>/tasks.md` produit), lancer `/assembleur:creation-task-linear` pour créer un **sous-ticket par phase** (label `Task`) rattaché au ticket `Feature` de chaque feature.
