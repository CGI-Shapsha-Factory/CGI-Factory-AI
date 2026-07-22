# Features : séquence & 3 faces

<!-- Fichier mémoire (.claude/memory/features.md), lu par Claude au besoin. Pointe vers les
     graines et résume la séquence/couplage. Contenu seul. -->

## Séquence
| Feature | Graine | Walking skeleton | Dépend de |
|---------|--------|------------------|-----------|
| 001 - [intitulé] | `assembleur-out/features/001-<slug>.md` | oui | - |
| 002 - [intitulé] | `assembleur-out/features/002-<slug>.md` | non | 001 |

## Couplage
[Renvoi à `assembleur-out/feature-map.md` : états partagés et dépendances entre features.]

## Les 3 faces (par feature)
- **Fonctionnelle** : la graine `assembleur-out/features/<id>-<slug>.md` - User Scenarios + FR.
- **Technique** : `assembleur-out/technical-context.md` + l'annexe technique de la graine.
- **Design** : [design](design.md) (système synchronisé + guidelines), appliqué à tous les écrans.
