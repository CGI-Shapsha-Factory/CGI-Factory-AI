# init-cowork — contexte de supervision (PO / Quark)

<!-- Genere par `create-cowork-md` a la RACINE du projet. Document de contexte UNIQUE avec lequel le
     PO INITIALISE un projet dans Quark/Cowork pour superviser. Il porte TOUT le contexte utile issu
     des 3 contrats (cadrage / architecte / designer) + les liens GitHub et Linear. AUCUNE section sur
     le workflow SpecKit, la fabrication feature-par-feature, ni l'avancement d'implementation (rien de
     tout cela n'existe encore). Tout est SYNTHESE (pas de copie), contenu seul (aucune provenance,
     aucun horodatage). Source absente -> omettre la ligne ou mettre `<a renseigner>` ; ne rien inventer. -->

> Ce document centralise **le contexte et les liens** dont tu as besoin pour superviser le projet.
> C'est un **instantané figé** de la convergence : pour l'**état vivant** (code, avancement, tâches),
> consulte toujours **GitHub** et **Linear** (liens plus bas). Ce fichier ne se met **pas** à jour seul.

## Où chercher quoi (l'état vivant n'est PAS dans ce document)

- **Avancement, tâches, issues terminées / en cours, qui fait quoi, planning** → **Linear** (lien plus bas).
- **Code, fichiers, spécifications (`spec.md`), features implémentées, détails techniques, pull requests** → **dépôt GitHub** (lien plus bas).
- **Le « pourquoi », le périmètre et les contraintes du produit** → **ce document** (sections ci-dessous, figées à la convergence).

## Projet

- **Nom** : [nom du produit]
- **Problème** : [le besoin auquel le produit répond — le *pourquoi*, en 1–3 phrases, tiré du product-brief §Problème]
- **Objectif** : [le résultat métier visé — product-brief §Objectif métier]
- **Utilisateurs & rôles clés** : [pour qui + les rôles principaux — product-brief §Parties prenantes / project-frame §Utilisateurs & rôles]
- **Proposition de valeur** : [une phrase — ce que le produit apporte concrètement]
- **Critères de succès** : [ce qui définit la réussite, à haut niveau — product-brief §Critères de succès]

## Périmètre

- **Inclus** : [les grandes capacités couvertes — puces, synthèse du product-brief §Périmètre IN]
- **Hors périmètre** : [ce qui n'est explicitement PAS fait dans cette version — puces, product-brief §Hors périmètre OUT]
- **Contraintes clés** : [légal / RGPD, sécurité, sensibilité des données, hébergement, disponibilité, performance — puces, product-brief §Contraintes + project-frame §Légal / Données / Disponibilité / Hébergement]

## Dépôt GitHub

[URL du dépôt, ex. `https://github.com/<org>/<repo>`]

> Pour toute information sur l'**implémentation**, les **fichiers**, les **spécifications**, les
> **features développées** ou les **détails techniques**, consulte le dépôt GitHub ci-dessus.

<!-- Si aucun remote GitHub n'est encore configuré : mettre `<à renseigner>` + garder cette note :
     « Le dépôt n'a pas encore de remote GitHub ; renseigner l'URL dès qu'il est créé. » -->

## Projet Linear

[URL du projet Linear, ex. `https://linear.app/<workspace>/project/<slug>`]

> Pour l'**avancement du projet** — issues **terminées**, tâches **en cours**, qui travaille sur quoi
> et les dernières livraisons — consulte Linear ci-dessus.

<!-- Si le projet Linear n'est pas détecté (MCP absent, ou tickets pas encore créés) : mettre
     `<à renseigner>` + la note d'installation (section « Accès Linear pour Quark » ci-dessous),
     et — si aucun ticket n'existe — orienter vers `/assembleur:premier-alimente-linear`. -->

## Périmètre & features

<!-- Depuis `architecture.feature_sequence` (id, name) + `assembleur-out/feature-map.md` (description,
     dépendances, walking skeleton). La colonne « Ticket Linear » n'est remplie que si
     `premier-alimente-linear` a déjà tourné (bloc manifeste `linear`) ; sinon « à créer via
     premier-alimente-linear ». -->

| Feature | Intitulé | Description courte | Dépend de | Ticket Linear | Lien |
|---------|----------|--------------------|-----------|---------------|------|
| 001 | [intitulé] | [ce que la feature apporte, en une ligne] | — | [ENG-123 / à créer] | [url ou —] |
| 002 | [intitulé] | [une ligne] | 001 | [ENG-124 / à créer] | [url ou —] |

> **Walking skeleton** : la feature [00X] est la tranche de bout en bout à livrer d'abord (socle
> technique traversant), avant les features qui en dépendent.

## Contexte technique (synthèse)

- **Stack** : [langages / frameworks / base de données / style d'API — architecte-out/stack-technique.md, en bref]
- **Intégrations** : [systèmes externes, SSO, connecteurs — project-frame §Intégrations]
- **Hébergement** : [cible de déploiement — project-frame §Hébergement]
- **Cibles de qualité** : [attributs prioritaires + cibles chiffrées si connues — architecte-out/facteurs-et-qualite.md]

> Synthèse : le détail vit dans le dépôt GitHub (code + specs).

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
