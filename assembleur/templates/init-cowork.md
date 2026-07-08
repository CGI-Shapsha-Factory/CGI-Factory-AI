# init-cowork — contexte de supervision (PO / Quark)

<!-- Genere par `create-cowork-md` a la RACINE du projet. Document de contexte UNIQUE pour le PO
     qui supervise depuis Quark. Ne contient QUE ce qui existe a la phase assembleur : les sorties
     des 3 contrats (cadrage / architecte / designer) + les liens GitHub et Linear. AUCUNE section
     sur le workflow SpecKit, la fabrication feature-par-feature, ni l'avancement d'implementation
     (rien de tout cela n'existe encore). Contenu seul (aucune provenance, aucun horodatage). -->

> Ce document centralise les liens et le contexte dont tu as besoin pour superviser le projet.
> C'est un **instantané** de la convergence : pour l'**état vivant** (code, avancement, tâches),
> consulte toujours **GitHub** et **Linear** (liens ci-dessous).

## Projet

- **Nom** : [nom du produit]
- **Résumé** : [une à deux phrases — l'objectif du produit, tiré du product-brief cadrage]

## Dépôt GitHub

[URL du dépôt, ex. `https://github.com/<org>/<repo>`]

> Pour toute information sur l'**implémentation**, l'**avancement du code** ou les **détails
> techniques**, consulte le dépôt GitHub ci-dessus.

<!-- Si aucun remote GitHub n'est encore configuré : mettre `<à renseigner>` + garder cette note :
     « Le dépôt n'a pas encore de remote GitHub ; renseigner l'URL dès qu'il est créé. » -->

## Projet Linear

[URL du projet Linear, ex. `https://linear.app/<workspace>/project/<slug>`]

> Suis l'**avancement du projet** depuis Linear : issues **terminées**, tâches **en cours**, et
> les dernières issues livrées.

<!-- Si le projet Linear n'est pas détecté (MCP absent, ou tickets pas encore créés) : mettre
     `<à renseigner>` + la note d'installation (section « Accès Linear pour Quark » ci-dessous),
     et — si aucun ticket n'existe — orienter vers `/assembleur:premier-alimente-linear`. -->

## Périmètre & features

<!-- Depuis `architecture.feature_sequence` + `assembleur-out/feature-map.md`. La colonne « Ticket
     Linear » n'est remplie que si `premier-alimente-linear` a déjà tourné (bloc manifeste `linear`) ;
     sinon indiquer « à créer via premier-alimente-linear ». -->

| Feature | Intitulé | Ticket Linear | Lien |
|---------|----------|---------------|------|
| 001 | [intitulé] | [ENG-123 / à créer] | [url ou —] |
| 002 | [intitulé] | [ENG-124 / à créer] | [url ou —] |

## Contexte technique (synthèse)

[Stack principale figée par l'architecte, en bref — langages/frameworks/services clés. Tiré de
`architecte-out/stack-technique.md`. Une synthèse, pas une copie : le détail est dans le dépôt.]

## Contexte design

[Référence du **design system** (handoff designer / système synchronisé via Claude Design). Où le
trouver, et le principe : tout écran en dérive. Tiré de `designer-out/design-guidelines.md`.]

## Accès Linear pour Quark (écriture)

Pour que Quark puisse **agir** sur Linear (créer / mettre à jour des issues), il faut le MCP
`linear-prism` **et** une authentification.

**Installer le MCP `plugin:linear-prism:linear`** (si absent) :
1. **Ajouter la marketplace** : `/plugin marketplace add shinpr/linear-prism`
2. **Installer le plugin** : `/plugin install linear-prism@linear-prism`
3. **Redémarrer** Claude Code (pour charger le serveur MCP).
4. **S'authentifier** : `/mcp` → serveur `linear` → login OAuth (aucune clé à gérer).

**Ou par clé API** (environnement sans OAuth) :
1. Linear → **Settings → Security & access → Personal API keys → New API key**.
2. Nommer la clé, choisir un **accès en écriture** (*Write* / *Create issues*), la **restreindre à
   l'équipe** du projet, puis **Create** (la clé n'est affichée **qu'une fois** — la copier).
3. La stocker dans un fichier **`.env`** (jamais commité) : `LINEAR_API_KEY=lin_api_…`.
4. Le MCP `linear-prism` lit alors `LINEAR_API_KEY` pour s'authentifier.
