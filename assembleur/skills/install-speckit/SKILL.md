---
name: install-speckit
description: Installe et initialise GitHub Spec Kit (specify) dans le repo cible — uv auto-installé sans admin, specify init non-interactif — pour que l'équipe lance tout de suite les /speckit.*.
---

# install-speckit

**Pont vers la phase SpecKit.** À lancer **après `assembleur-convergence`** (et, si l'équipe crée des
tickets, après `premier-alimente-linear`), quand le paquet de handoff (`assembleur-out/`) est prêt et que
l'équipe s'apprête à fabriquer. Ce skill **automatise l'étape `specify init`** du `attack-plan.md` : il vérifie si SpecKit est déjà posé dans le repo et,
sinon, l'installe **complètement et sans aucune manip** — pour que les commandes `/speckit.*`
soient disponibles **immédiatement**. Principe directeur : **rien ne doit bloquer l'installation**.

## Objectif
Garantir que SpecKit (`specify`) est **installé et initialisé** dans le repo courant : le CLI est
acquis via `uv` (auto-installé si absent, en **espace utilisateur, sans admin**), puis `specify
init` est joué en **non-interactif** pour l'agent Claude Code. À la fin, `.specify/` (constitution,
scripts, templates) et les commandes `/speckit.*` existent dans le repo.

## Frontière (exception assumée)
L'assembleur **n'écrit jamais lui-même** un fichier que SpecKit génère. Ce skill **ne rédige à la
main aucun contenu de `.specify/`** : il **invoque `specify init`**, et c'est **SpecKit** qui
produit `.specify/` et les `/speckit.*`. La seule écriture propre à la Factory est le bloc
`speckit` du **manifeste committé** `cadrage-out/manifest.json` (comme chaque plugin y écrit son bloc).
C'est donc une exception **explicitement bornée** à l'invariant « paquet seul » — pas une violation.

## Pré-requis (vérification silencieuse)
Lire `cadrage-out/manifest.json` **sans l'annoncer**, uniquement pour situer la racine (dossier
contenant `.factory/`) et l'état d'avancement. **Aucune porte dure** ici :
- si `.factory/` est absent : on n'est pas dans un workspace Factory ; le dire en clair, mais
  **ne pas refuser** — l'installation reste possible dans le dossier courant (best-effort) ;
- si le bloc `assembly` manque ou que la cohérence n'est pas validée : ajouter **une** ligne de
  prose invitant à finir la convergence d'abord, **puis continuer quand même**.

> Ce skill est prévu après la convergence, une fois le paquet prêt. Il n'en fait pas une
> condition : par conception, **rien ne bloque l'installation de SpecKit**.

Les seuls messages d'arrêt viennent d'un environnement réellement non installable (ex. Git absent
**et** hors ligne) ; ils sortent du **script**, jamais d'une gate de ce skill.

## Procédure
1. **Lancer l'installeur déterministe** (il fait tout, bout en bout, dans un seul processus) :
   `py -3 "${CLAUDE_PLUGIN_ROOT}/scripts/install_speckit.py" <racine-projet>` (utiliser `python`
   si `py` est absent ; `python3` sur macOS/Linux). Le script : détecte si `.specify/` est déjà là
   (**idempotent**), s'assure de `uv` (l'auto-installe sans admin, rafraîchit le PATH dans son
   propre processus), vérifie Git, acquiert le CLI `specify`, **introspecte `specify init --help`**
   pour bâtir les bons flags (version-proof), joue `specify init` non-interactif, fait un **test de
   fumée**, écrit le bloc `speckit` du manifeste, et affiche un statut clair en français.
2. **Relayer le résultat en prose** (voir `references/ux-conventions.md`) : dire **ce qui s'est
   passé** et **la prochaine étape** ; ne jamais afficher de nom de clé du manifeste ni de tableau.
3. Si le script **sort en échec** : relayer son message **actionnable** tel quel (ex. « Git est
   requis : installe Git puis relance »), **sans** dumper de trace. Au besoin, le relancer avec
   `--verbose` pour le détail.

## Vérification avant de conclure
- `.specify/` existe à la racine du repo cible (généré par `specify init` : `memory/constitution.md`,
  `scripts/`, `templates/`).
- Au moins une commande `/speckit.*` est présente sous `.claude/` (commandes ou skills selon la version).
- Le CLI `specify` est disponible (installation persistante) — `specify check` a pu tourner (informatif).
- Le manifeste contient le bloc `speckit` (installé + initialisé) et **reparse sans erreur**.
- **Idempotence** : si `.specify/` préexistait, rien n'a été réinitialisé ni écrasé.
- **Aucun fichier SpecKit rédigé à la main** : tout `.specify/` provient de `specify init`.
- Le script est sorti **0** ; en cas d'échec, un message **actionnable** a été relayé (pas de trace).
- Restitution faite **en prose**, manifeste mis à jour **en silence**.

## Règles invariantes
- **N'écrit aucun fichier SpecKit à la main.** Seul `specify init` génère `.specify/` et les
  `/speckit.*`. Exception bornée à l'invariant « paquet seul ».
- **Rien ne bloque l'installation.** `uv` auto-installé sans admin ; PATH rafraîchi en cours de
  processus ; flags construits par introspection ; sous-processus bornés par timeout ; échecs
  réseau attrapés proprement.
- **Idempotent.** `.specify/` déjà présent → ne réinitialise pas, ne réécrit rien.
- **Manifeste en silence.** Le bloc `speckit` est écrit sans le narrer ; restitution en prose.
- **TLS jamais désactivé.** On respecte la CA système (proxys d'entreprise) ; jamais `--skip-tls`.

Étape suivante : `/speckit.constitution` en fournissant `assembleur-out/pre-constitution.md`, puis les `/speckit.specify` dans l'ordre de `assembleur-out/feature-map.md` (walking skeleton d'abord).
