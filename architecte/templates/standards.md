---
version: 1
date: AAAA-MM-JJ
---
<!-- version : compteur d'itération de ce document (entier, +1 à chaque régénération). date : jour de génération (format AAAA-MM-JJ, à remplacer par la date réelle). -->

# Standards d'ingénierie

<!-- Public visé : Claude Code + humains. -->
<!-- Ces règles s'appliquent à TOUT le code du projet. Les formuler comme des règles
     applicables, pas des recommandations. Claude Code vérifiera le nouveau code par
     rapport à ces standards. -->
<!-- Remplir chaque [placeholder]. Utiliser les marqueurs [À VALIDER] / [À CHIFFRER]
     là où une valeur manque.  -->

> Le style de code, le formatage et le nommage sont matérialisés par les fichiers de
> `conventions/` (un par langage) ; ce document couvre les standards non couverts par
> le linter.

## Style de code, formatage & nommage

Ces aspects ne sont **pas** redéfinis ici : ils sont matérialisés par des fichiers de
configuration exécutables, installés dans `conventions/` à la racine du projet et
appliqués automatiquement (à la sauvegarde et en CI). La source de vérité est le
fichier de config, pas une table de nommage dupliquée.

| Périmètre                         | Fichier de config                          | Couvre                                                        |
|-----------------------------------|--------------------------------------------|---------------------------------------------------------------|
| Inter-langages (fallback)         | `conventions/.editorconfig`                | encodage, fins de ligne, indentation, longueur de ligne       |
| Python                            | `conventions/ruff.toml`                    | lint + format + tri des imports + nommage (Ruff)              |
| JavaScript / TypeScript           | `conventions/biome.json`                   | lint + format + nommage (Biome)                               |
| JavaScript / TypeScript (variante)| `conventions/eslint.config.js` + `conventions/.prettierrc` | lint (ESLint) + format (Prettier)         |
| C                                 | `conventions/.clang-format`                | format + style de nommage (clang-format)                      |

<!-- Ne garder que les lignes correspondant aux langages réellement présents dans la
     stack (voir tech-stack.md). Pour JS/TS, choisir UNE approche : soit Biome (tout-en-un),
     soit le couple ESLint + Prettier — pas les deux. Ajouter une ligne par langage
     supplémentaire et pointer vers le fichier de config correspondant dans `conventions/`. -->

Règles transverses :

- Tout commit doit passer le formateur et le linter du langage concerné avant d'être poussé.
- Les configs de `conventions/` ne sont pas contournées localement (pas de désactivation de règle ad hoc sans justification commentée).
- En cas de divergence entre un fichier de config et ce document, le fichier de config fait foi pour le style ; ce document fait foi pour tout le reste.

## Gestion des erreurs

- Toutes les erreurs doivent être [typées / encapsulées dans une classe d'erreur de domaine / ...].
- Les erreurs se propagent [par levée d'exception / par retour de types Result / ...].
- Les erreurs d'API externes doivent être interceptées à [la couche adaptateur / ...] et traduites en erreurs de domaine avant d'atteindre la logique métier.
- Les réponses d'erreur destinées à l'utilisateur ne doivent jamais exposer de stack trace ni de détails internes du système.
- Toute erreur interceptée et non relevée doit être journalisée au niveau [warn / error] avec son contexte.

## Journalisation (logging)

- Format : [JSON structuré / texte brut] — champs : `timestamp`, `level`, `service`, `traceId`, `message`, plus les champs spécifiques au contexte.
- Niveaux utilisés : `debug` (dev uniquement), `info` (fonctionnement normal), `warn` (problèmes récupérables), `error` (action requise).
- **Ne jamais journaliser :** mots de passe, jetons, clés d'API, données personnelles complètes (nom + email + adresse ensemble), données de cartes de paiement.
- **Toujours journaliser :** l'identifiant de requête / trace ID sur chaque ligne de log dans le périmètre d'une requête, le nom du composant.
- Les logs doivent être écrits sur stdout — aucun puits de fichier (file sink) dans le code applicatif.

## Socle de sécurité

- Toutes les entrées de sources externes (corps HTTP, paramètres de requête, en-têtes, messages de file) doivent être validées et assainies avant usage.
- Les secrets sont chargés exclusivement depuis les variables d'environnement ou le gestionnaire de secrets désigné ([outil]) — jamais codés en dur ni commités.
- Les dépendances sont scannées à la recherche de vulnérabilités connues en CI via [outil] ; les builds échouent sur les findings HIGH ou CRITICAL.
- Toutes les réponses HTTP doivent positionner les en-têtes de sécurité appropriés ([CSP, HSTS, X-Frame-Options, ...]).
- [Toute règle de sécurité spécifique au projet — ex. « toutes les requêtes base de données utilisent des requêtes paramétrées »]

## Exigences de test (stratégie)

**Écrire les tests EN MÊME TEMPS que le code.** Dès qu'une fonction est créée, son test est écrit dans
le même changement — aucune source ne part sans son test. (Appliqué par des garde-fous déterministes :
hooks Claude Code + pre-commit — voir la constitution du projet.)

**Tests unitaires — un par règle métier.** Chaque règle métier implémentée par une fonction a un test
unitaire couvrant **le cas passant, le(s) cas d'échec et les cas limites** (valeurs aux bornes, entrées
vides/nulles, erreurs attendues). La couverture chiffrée est un plancher, pas la stratégie.

**Tests d'intégration — composants complets, dépendances externes MOCKÉES** (pas d'« infrastructure
réelle » dans le test). Pour chaque composant livrable :
- **Frontend** : tester en **simulant les interactions utilisateur** et en **mockant les appels d'API
  externes** (le réseau ne sort jamais du test).
- **API / pipelines / batch** : couvrir **toutes les fonctionnalités exposées** en **mockant toutes les
  dépendances externes** (base, files, services tiers, horloge).

**Frameworks & mocking par langage** (selon la stack de `tech-stack.md`) :
- Python → pytest (+ `pytest-mock`/`monkeypatch`, `responses`/`respx` pour HTTP).
- TS/JS → Vitest ou Jest (+ `msw` pour le réseau).
- Angular → TestBed + `HttpTestingController` (ou Jest) ; spies pour les services.
- .NET → xUnit + Moq/NSubstitute. Java/Spring → JUnit 5 + Mockito. Go → `testing` + `httptest`.

**Hygiène :**
- Les fichiers de test résident [à côté du code source / dans un dossier `tests/` dédié].
- Nommage : `[unité testée].[scénario].[résultat attendu]` — ex. `createOrder.withInvalidPayload.throwsValidationError`.
- Chaque test met en place et démonte son propre état ; aucun état partagé entre tests.
- Aucun code de production ne référence d'utilitaires ou modules réservés aux tests.
- (Optionnel) Tests E2E des parcours critiques : [parcours listés], à passer avant tout déploiement.

## Règles de conception d'API

- Versionnage : [préfixe d'URL `/v1/` / en-tête `API-Version` / ...].
- Pagination : [par curseur / par offset] — champs : `[data, nextCursor / data, total, page, pageSize]`.
- Format de réponse d'erreur :
  ```json
  {
    "error": {
      "code": "CODE_LISIBLE_PAR_MACHINE",
      "message": "Description lisible par un humain.",
      "traceId": "..."
    }
  }
  ```
- En-tête d'authentification : `Authorization: Bearer <token>`.
- Tous les horodatages au format ISO 8601 UTC (`2024-01-15T10:30:00Z`).

## Règles d'accès aux données

- [ORM / query builder / SQL brut] est la méthode d'accès aux données approuvée.
- Aucun composant ne peut interroger directement les tables de la base d'un autre composant ; l'accès passe par l'API du composant propriétaire.
- Toutes les mutations en base doivent s'exécuter dans des transactions explicites.
- Les migrations sont [en avant uniquement / réversibles] ; les fichiers de migration ne sont jamais modifiés après avoir été appliqués à un environnement.
- Nommage des migrations : `YYYYMMDDHHMMSS_courte_description.sql`.

## Workflow Git

- Nommage des branches : `[type]/[courte-description]` — types : `feat`, `fix`, `chore`, `docs`, `refactor`.
- Les messages de commit suivent les [Conventional Commits] : `type(scope): description à l'impératif` — ex. `feat(orders): add cancellation endpoint`.
- Les pull requests doivent compter [N] fichiers ou moins ; les changements plus volumineux sont découpés en PR empilées (stacked PRs).
- Aucun push direct sur `main` ou `master` ; tout changement passe par une PR avec au moins [N] approbation(s).
  Cette règle est **appliquée localement** par les garde-fous git `.githooks/` (posés par l'architecte) :
  `pre-push` refuse le push vers `main`/`master`, `pre-commit` refuse le commit *sur* ces branches.
  Les hooks se **réactivent automatiquement** à chaque session Claude Code (hook `SessionStart` →
  `git config core.hooksPath .githooks`) ; garde-fou local, contournable `--no-verify` ; la garantie
  forte reste le ruleset serveur GitHub.
- La CI doit être verte avant fusion.

## Règles de documentation

- Chaque fonction/méthode publique doit avoir un commentaire de doc expliquant **pourquoi** elle existe (pas quoi — le code le montre), plus tout invariant ou effet de bord non évident.
- Les décisions de niveau architecture vont dans `architecture/decisions/` ; les commentaires en ligne n'expliquent que le comportement local non évident.
- Le `README.md` à la racine du dépôt doit toujours contenir : objet, prérequis, comment lancer en local, comment lancer les tests, comment déployer.
- Les commentaires obsolètes doivent être supprimés, pas laissés avec un « TODO: remove ».
