# Carte des features : séquence, couplage, walking skeleton

<!-- Livrable de `assembleur-out/`. Porte l'info de DÉCOUPAGE que SpecKit doit connaître pour
     ordonner les `/speckit.specify`. Source : registre de features (feature_sequence - proposé par
     l'architecte, arbitré et figé par l'assembleur)
     + carte de couplage cadrage. Contenu seul (aucune provenance). -->

## Séquence (ordre des dépendances)

| Ordre | Feature | Répertoire / branche SpecKit | Walking skeleton | Use cases (ucs) | Dépend de | Peut avancer en parallèle |
|-------|---------|------------------------------|------------------|-----------------|-----------|---------------------------|
| 1 | 001 - [intitulé] | `001-slug` | oui | [ucs] | - | non |
| 2 | 002 - [intitulé] | `002-slug` | non | [ucs] | 001 | [oui/non] |

> Le **walking skeleton** (feature 001) est la première tranche de bout en bout qui dé-risque la
> stack ; à fabriquer en premier.

> **Numérotation canonique (imposée).** La colonne "Répertoire / branche SpecKit" (`NNN-slug`, avec
> `NNN` = l'`id` du registre de l'architecte) est **la** source du numéro : chaque feature impose
> `specs/<NNN-slug>/` et la branche git `<NNN-slug>`. **Ne jamais laisser SpecKit auto-numéroter**
> (`/speckit.specify` avec `SPECIFY_FEATURE_DIRECTORY=specs/<NNN-slug>`) - sinon deux développeurs
> partis de `main` collisionnent le même numéro. Un garde-fou (`check_speckit_alignment.py`) le vérifie.

## Couplage / états partagés
[Les features qui partagent une entité ou un état (lecture/écriture concurrente), et le point de
vigilance associé. C'est ce qui contraint l'ordre et signale les risques d'intégration.]

| État partagé | Features concernées | Nature du couplage | Attention |
|--------------|---------------------|--------------------|-----------|
| [entité / donnée] | 001, 003 | [lecture / écriture concurrente] | [...] |

> Les features couplées ci-dessus (écriture concurrente sur le même état) se traitent **en séquence**,
> via les relations `blockedBy` Linear - jamais en parallèle. Procédure d'intégration : `attack-plan.md`.

## Chemin critique
[La plus longue chaîne de dépendances - ce qui dimensionne le calendrier.]
