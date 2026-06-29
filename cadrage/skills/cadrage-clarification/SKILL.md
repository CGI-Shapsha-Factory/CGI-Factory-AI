---
name: cadrage-clarification
description: Repose en session, une à une, les questions du projet restées sans réponse.
---

# cadrage-clarification

Boucle de feedback. Reprend les questions du projet **restées sans réponse** et les
**repose à l'utilisateur en session**, une à une — notamment au moment de la
validation du démonstrateur. Rien n'est listé dans un fichier : tout se tranche dans
le chat.

## Objectif

Faire le tour des points encore ouverts du projet et les **lever en conversation**,
sans noyer l'utilisateur. Le skill ne produit pas de checklist persistée : il **pose
les bonnes questions** et applique les réponses dans les artefacts concernés.

## Entrée

- Les questions de découverte encore `pending`/`deferred` (bloc `discovery`).
- Le glossaire pas encore validé en bloc.
- Les acquis marqués `[REMIS EN CAUSE]` (retour de démonstrateur à retrancher).
- Les souhaits hors périmètre repérés, à confirmer.

## Pré-requis (vérification silencieuse)

**Au moins un point reste à trancher.** Sinon, indiquer en clair qu'il n'y a rien à
clarifier et s'arrêter.

## Procédure

1. **Recenser** (en mémoire de session, sans écrire de liste) ce qui reste ouvert :
   questions de découverte sans réponse, glossaire non validé, acquis remis en cause,
   souhaits hors périmètre.
2. **Prioriser** : d'abord ce qui bloque un artefact, ensuite le raffinement.
3. **Reposer chaque point en session, un à la fois**, via la boucle interactive
   (`references/interactive-loop.md`) : exposer le point en clair, proposer une
   **réponse recommandée** (suggestion étiquetée), l'utilisateur accepte ou donne la
   sienne. **Pas de menu numéroté.** Attendre la réponse avant le point suivant.
4. **Formuler des questions spécifiques et répondables** — pas « préciser le besoin »
   mais « quelle est la cible chiffrée de réduction du temps d'appel ? ».
5. **Appliquer chaque réponse tout de suite** dans l'artefact concerné (project-frame,
   glossaire, spec-index…). Un point que l'utilisateur ne tranche pas reste ouvert,
   **n'est écrit nulle part**.
6. **Plafonner par session** (~8–10 questions) pour ne pas noyer l'utilisateur ; le
   reste sera reposé à un prochain passage.

## Vérification

- Les points reposés sont **spécifiques et répondables**.
- Chaque réponse est **appliquée dans l'artefact** qu'elle débloque.
- **Aucune liste de points ouverts n'est écrite** dans un fichier, **aucune
  provenance** (pas de `(src:)`).

## Mise à jour du manifeste

Read-modify-write puis revalidation JSON :
- Met à jour les statuts `discovery[]` des questions tranchées en session.
- `updated_at`.
- Ne modifie aucune porte (ni `decoupage_arbitrated`, ni `demonstrateur_converged` —
  calculés ailleurs).

## Règles invariantes appliquées ici

- **Tout interactif.** On repose les questions en session, on ne génère pas de
  checklist persistée.
- **Ne pas inventer.** On aide l'utilisateur à trancher ; un point non tranché reste
  ouvert et n'est pas comblé.
- **Skill indépendant.** Lit les artefacts et le manifeste, sans orchestrateur.

Étape suivante : `/cadrage:cadrage-retour-demonstrateur` — ingérer le retour client après la validation de la maquette.
