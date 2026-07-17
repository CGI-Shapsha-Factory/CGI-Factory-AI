# Rapport de cohérence : convergence des 3 contrats

<!-- Livré en `assembleur-out/coherence-report.md`. Pas de vert tant qu'une feature a une face
     manquante ou contradictoire. La validation finale est un geste humain. Contenu seul ; aucun
     marqueur résiduel (tout point se tranche en session avant de conclure). -->

## Synthèse par feature
| Feature | Fonctionnel | Technique | Design | Cohérente ? | Problème |
|---------|-------------|-----------|--------|-------------|----------|
| 001 - [..] | Oui | Oui | Oui | oui | - |
| 00X - [..] | Oui | Oui | Non | NON | [face manquante / contradiction] |

## Contradictions vérifiées
- [feature] : [ex. la face design référence un composant absent de la face technique]
- [feature] : [ex. un parcours sans FR ; une FR sans critère d'acceptation ; une cible perf non
  tenable par la stack]

## Verdict
[atteint / non atteint] - la cohérence n'est validée (par l'humain) que si **toutes** les
features sont cohérentes (3 faces complètes et non contradictoires) et qu'**aucun point**
ne reste à trancher.
