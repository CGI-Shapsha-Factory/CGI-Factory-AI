# Rapport de cohérence — convergence des 3 contrats

> **Porte humaine : garant de cohérence.** Pas de vert tant qu'une feature a une face
> manquante ou contradictoire. La validation finale est un geste humain. (src: …)

## Synthèse par feature
| Feature | Fonctionnel | Technique | Design | Cohérente ? | Problème |
|---------|-------------|-----------|--------|-------------|----------|
| 001 — [..] | ✓ | ✓ | ✓ | oui | — |
| 00X — [..] | ✓ | ✓ | ✗ | NON | [face manquante / contradiction] |

## Contradictions détectées
- [feature] : [ex. la face design référence un composant absent de la face technique]
- [feature] : [ex. un parcours sans FR ; une FR sans critère d'acceptation]

## Trous bloquants
- [feature / face] : [À VALIDER]

## Verdict
[atteint / non atteint] — la cohérence n'est validée (par l'humain) que si **toutes** les
features sont cohérentes (3 faces complètes et non contradictoires).
