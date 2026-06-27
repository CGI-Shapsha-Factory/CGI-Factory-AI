# Stack technique

<!-- Public visé : Claude Code + humains. -->
<!-- Remplir chaque [placeholder]. La matrice composant × techno doit lister CHAQUE
     composant de components.md — garder les deux fichiers synchronisés. -->
<!-- Utiliser les marqueurs [À VALIDER] / [À CHIFFRER] là où une valeur manque.
     Conserver la convention (src: …) pour tracer l'origine d'un choix. -->

## Langages & runtimes

| Langage  | Version | Utilisé pour                    |
|----------|---------|---------------------------------|
| [...]    | [...]   | [quels composants / couches]    |

## Frameworks & bibliothèques

| Bibliothèque / Framework | Version | Rôle                          | Composant(s)         |
|--------------------------|---------|-------------------------------|----------------------|
| [...]                    | [...]   | [ce qu'il fournit]            | [quels composants]   |

## Stockages de données

| Stockage   | Type        | Version | Utilisé par          | Rôle                 |
|------------|-------------|---------|----------------------|----------------------|
| [...]      | [relationnel / document / cache / file / ...] | [...] | [...] | [...] |

## Infrastructure & déploiement

| Préoccupation        | Technologie / Service | Notes                         |
|----------------------|-----------------------|-------------------------------|
| Conteneur            | [...]                 | [...]                         |
| Orchestration        | [...]                 | [aucun si non applicable]     |
| Fournisseur cloud    | [...]                 | [région, structure de comptes]|
| CDN                  | [...]                 | [aucun si non applicable]     |
| Gestion des secrets  | [...]                 | [...]                         |
| Stockage objet       | [...]                 | [aucun si non applicable]     |

## Outillage

| Catégorie         | Outil         | Version | Notes                  |
|-------------------|---------------|---------|------------------------|
| CI/CD             | [...]         | [...]   | [...]                  |
| Linter            | [...]         | [...]   | [...]                  |
| Formateur         | [...]         | [...]   | [...]                  |
| Lanceur de tests  | [...]         | [...]   | [...]                  |
| Couverture de code| [...]         | [...]   | [...]                  |
| SAST / scan       | [...]         | [...]   | [aucun si non applicable] |

## Matrice composant × techno

<!-- Marquer chaque cellule : ✓ runtime/langage principal · DB stockage de données ·
     🔗 appel externe · — non utilisé. -->
<!-- Colonnes = technologies des sections ci-dessus. Lignes = chaque composant de
     components.md. RÈGLE : une ligne de la matrice par composant. -->

| Composant       | [Lang] | [Framework] | [DB 1] | [DB 2] | [Cache] | [File] | [Svc auth] |
|-----------------|--------|-------------|--------|--------|---------|--------|-----------|
| [ComposantA]    | ✓      | ✓           | DB     | —      | 🔗      | —      | 🔗        |
| [ComposantB]    | ✓      | ✓           | —      | DB     | —       | 🔗     | 🔗        |
| [WorkerC]       | ✓      | —           | DB     | —      | —       | 🔗     | —         |

## Politique de versions

<!-- Comment les versions de dépendances sont gérées sur l'ensemble du projet. Exemples :
- Toutes les dépendances directes sont épinglées à une version exacte ; mises à jour via PR automatisées.
- Les versions de runtime suivent le fichier `.tool-versions` / `.nvmrc` du projet.
- Les correctifs de sécurité sont appliqués dans les 72 h suivant la divulgation. -->

[À VALIDER]

## Justification des décisions

Toutes les décisions techniques majeures — y compris les options considérées et la
justification de chaque choix — sont consignées dans `architecture/decisions/`.
