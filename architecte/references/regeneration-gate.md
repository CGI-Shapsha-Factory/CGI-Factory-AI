# Porte de régénération (relance sur des sorties existantes)

Convention partagée : que faire quand un skill de génération est **relancé** alors que
**ses propres sorties existent déjà** (documents d'un `-out/`, images de diagrammes). But :
ne **jamais** supprimer ni écraser un livrable sans un **choix explicite** de l'utilisateur.

## Quand la porte s'ouvre
- **Au début du skill**, après les pré-requis, **avant de (re)générer** : vérifier si les
  fichiers que **ce skill produit** existent déjà sur le disque (les siens uniquement, jamais
  ceux de l'amont).
- **Aucun n'existe (premier passage)** : générer directement, **pas de porte**.
- **Au moins un existe (relance)** : poser **la décision ci-dessous** (un seul message, puis
  attendre - cf. `interactive-loop.md`). Ne rien toucher tant que l'utilisateur n'a pas tranché.

## La décision (deux options, on attend le choix)
Exposer en clair **les fichiers concernés par leur nom métier** (jamais un code), puis poser la
décision **avec `AskUserQuestion`** - les deux options ci-dessous, jamais une troisième écrite à la
main (l'outil ajoute lui-même la saisie libre) :

1. **Repartir de zéro** *(recommandé si la relance vise à tout refaire)* - **supprimer** les
   sorties existantes de ce skill, puis **générer à neuf** aux noms canoniques (front-matter
   `version: 1`). L'ancienne version n'est pas conservée.
2. **Garder les deux (versionner)** - **archiver** chaque sortie existante sous
   `<-out>/_archives/<nom>-v<N>.<ext>` (`N` = son `version:` courant ; pour un fichier sans
   front-matter, ex. une image, un index croissant), puis **générer à neuf** au **nom canonique**
   avec `version: N+1`. Rien n'est perdu ; le **nom canonique porte toujours la version la plus
   récente**, donc l'aval lit toujours la dernière.

Pas de troisième voie silencieuse : sans choix explicite, **on ne supprime, ne déplace, ni
n'écrase rien**.

## Cas des diagrammes (images)
Les images vivent dans `<-out>/diagrammes/` (SVG/PNG déterministes). Même règle :
- **Repartir de zéro** : vider `diagrammes/` puis re-rendre.
- **Garder les deux** : déplacer le `diagrammes/` existant vers `<-out>/_archives/diagrammes-v<N>/`,
  puis re-rendre à neuf.

## Périmètre et invariants
- **Sorties du skill uniquement.** La porte ne concerne que les fichiers **produits par ce skill**,
  pas tout le `-out/`, ni les contrats amont.
- **Archives à la racine du `-out/`.** Toujours écrire sous `<-out>/_archives/` (jamais dans un
  sous-dossier livrable comme `features-fonctionnels-brief/`), pour que les balayages de l'aval ne
  confondent jamais une archive avec un livrable courant.
- **`_archives/` est committé** (c'est l'historique voulu par "garder les deux") et **ignoré des
  balayages** de l'aval : aucun skill ne relit `_archives/` comme un livrable, aucun glob de
  livrables (`*.md`, `features-fonctionnels-brief/*.md`, ...) ne l'inclut.
- **Manifeste en silence.** Mettre à jour le manifeste comme d'habitude, sans narration.
- **Typographie humaine.** Messages et noms de fichiers sans glyphe de style IA (tiret simple,
  `->`, guillemets droits).
