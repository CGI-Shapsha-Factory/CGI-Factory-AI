---
version: 1
date: AAAA-MM-JJ
---
<!-- version : compteur d'itération de ce document (entier, +1 à chaque régénération). date : jour de génération (format AAAA-MM-JJ, à remplacer par la date réelle). -->

# Stack technique

<!-- Public visé : Claude Code + humains. -->
<!-- Remplir chaque [placeholder]. La matrice composant × techno doit lister CHAQUE
     composant de components.md — garder les deux fichiers synchronisés. -->
<!-- VERSION EXACTE OBLIGATOIRE : chaque ligne d'une table à colonne « Version » porte
     une version exacte et épinglée (ex. « Python 3.12.10 », « PostgreSQL 17.2 »,
     « React 19.1.0 »). INTERDIT : vide, « latest », « stable », « current »,
     « nightly », « dernière version », « — ». Pour un service managé sans numéro de
     version (ex. Azure Container Apps), inscrire le SKU / palier ou
     « service managé (pas de version épinglée) » — jamais « latest ». -->
<!-- Une version encore inconnue se tranche EN SESSION (on demande la version exacte à
     l'utilisateur, on l'écrit en place) — jamais laissée en marqueur dans le fichier final. -->

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

<!-- Règle par défaut REQUISE (pas un simple exemple) : toutes les dépendances directes
     sont épinglées à une version EXACTE (pyproject.toml / package.json), et les tables
     ci-dessus reflètent ces versions exactes. Compléter les points spécifiques au projet :
     cadence de mise à jour, source des versions de runtime (.tool-versions / .nvmrc),
     délai d'application des correctifs de sécurité. -->

- Toutes les dépendances directes sont épinglées à une version exacte ; ces versions exactes figurent dans les tables ci-dessus.
- [cadence de mise à jour — ex. via PR automatisées]
- [délai d'application des correctifs de sécurité — ex. 72 h après divulgation]

## Justification des décisions

Toutes les décisions techniques majeures — y compris les options considérées et la
justification de chaque choix — sont consignées dans `architecte-out/decisions/` (ADR).
