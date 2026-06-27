# Journal d'arbitrage — Revue de couplage

> Journal **append-only** des décisions humaines de la revue de couplage. Une entrée
> n'est jamais supprimée : un nouveau passage de `cadrage-decoupage` rouvre la revue de couplage,
> mais l'historique des décisions reste ici.
> Chaque revue de couplage approuvée ajoute une entrée.

## Entrées

### <JJ-MM-AAAA> — <décideur>
- **Décision** : <ce qui a été tranché (frontière, fusion, couplage, ordre par valeur…)>
- **Use cases / états concernés** : <ids ou noms>
- **Raison** : <pourquoi cette décision, sur quelle matière source>
- **Conséquence** : <impact sur le découpage proposé / l'hypothèse de couplage>

<!--
À chaque revue de couplage, AJOUTER une entrée (ne jamais réécrire les
précédentes). Le compteur `artifacts.arbitrage_log.entries` du manifeste reflète
le nombre d'entrées. Si un nouveau passage du découpage réinitialise l'arbitrage, la
nouvelle revue ajoute une entrée expliquant ce qui a changé.
-->
