# Prompt Claude Design — Dashboard Definition of Ready

À coller dans Claude Design, avec l'état du manifeste / le `completude-report.md`
en matière source. Direction visuelle : une palette délibérée et sobre adaptée au
contenu (jamais le violet/indigo par défaut des interfaces générées par IA), premium,
sans-serif, aucun emoji. Un vert sobre uniquement pour les états atteints.

```
Crée un tableau de bord HTML qui montre si la phase amont d'un projet est prête
à passer en fabrication SpecKit, à partir d'un état que je te fournirai.
Objectif : voir d'un coup d'œil ce qui est complet et ce qui manque.

Style : une palette délibérée et sobre adaptée au contenu (jamais le violet/indigo
par défaut des interfaces générées par IA), premium, sans-serif, aucun emoji.
Une jauge de complétude globale en pourcentage. Un vert sobre uniquement pour
les états atteints.

Contenu :
- Une jauge de complétude globale.
- La liste des critères de Definition of Ready avec leur statut : vision
  complète, glossaire validé, découpage arbitré, tous les briefs complets,
  aucun trou bloquant, démonstrateur convergé.
- Un verdict maître bien visible : prêt à lancer /speckit.specify, qui ne
  s'allume que si tous les critères sont atteints.
- La liste de ce qui manque, actionnable, chaque manque relié à l'étape qui le
  résout.
- Un tableau des features avec, par feature, le statut de son brief et le
  nombre de trous restants.

Ton : tableau de pilotage, factuel, lisible en réunion.
```
