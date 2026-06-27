# États d'écran & patterns d'interface

<!-- Public visé : designers + Claude Code. Couvre la « couverture des états ». -->
<!-- Remplir chaque [placeholder]. (src: …). -->

## États canoniques d'un écran (UI Stack)
<!-- Tout écran data-driven doit traiter ces états. -->

| État | Quand | Rendu attendu | Composants mobilisés |
|------|-------|---------------|----------------------|
| Initial / vide | aucune donnée encore | [message + action] | [empty state] |
| Chargement | données en attente | [skeleton / spinner ; `aria-busy`] | [...] |
| Partiel | données incomplètes | [...] | [...] |
| Erreur | échec de chargement/action | [message clair + reprise] | [...] |
| Idéal / succès | données présentes | [contenu nominal] | [...] |

## Patterns transverses
- **Formulaires & validation :** [moment de validation, messages d'erreur, focus sur la 1ʳᵉ erreur].
- **Retours (feedback) :** [toasts / inline ; durée ; rôle `status`/`alert`].
- **Navigation :** [structure, état actif, fil d'Ariane].
- **Modales / overlays :** [piège de focus, Échap, retour du focus].
- **Hors-ligne / dégradé :** [le cas échéant].

<!-- Tout état non traité pour un parcours reste [À VALIDER]. -->
