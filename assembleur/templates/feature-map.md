# Carte des features — séquence, couplage, walking skeleton

<!-- Livrable de `assembleur-out/`. Porte l'info de DÉCOUPAGE que SpecKit doit connaître pour
     ordonner les `/speckit.specify`. Source : registre canonique architecte (feature_sequence)
     + carte de couplage cadrage. Contenu seul (aucune provenance). -->

## Séquence (ordre des dépendances)

| Ordre | Feature | Walking skeleton | Use cases (ucs) | Dépend de | Peut avancer en parallèle |
|-------|---------|------------------|-----------------|-----------|---------------------------|
| 1 | 001 — [intitulé] | oui | [ucs] | — | non |
| 2 | 002 — [intitulé] | non | [ucs] | 001 | [oui/non] |

> Le **walking skeleton** (feature 001) est la première tranche de bout en bout qui dé-risque la
> stack ; à fabriquer en premier.

## Couplage / états partagés
[Les features qui partagent une entité ou un état (lecture/écriture concurrente), et le point de
vigilance associé. C'est ce qui contraint l'ordre et signale les risques d'intégration.]

| État partagé | Features concernées | Nature du couplage | Attention |
|--------------|---------------------|--------------------|-----------|
| [entité / donnée] | 001, 003 | [lecture / écriture concurrente] | [...] |

## Chemin critique
[La plus longue chaîne de dépendances — ce qui dimensionne le calendrier.]
