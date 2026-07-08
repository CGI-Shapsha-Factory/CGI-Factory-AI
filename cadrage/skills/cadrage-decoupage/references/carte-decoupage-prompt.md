# Prompt Claude Design — Carte de découpage et dépendances

À coller dans Claude Design, avec les données du `spec-index.md` et du
`coupling-map.md` en matière source. Sert de support à la revue de couplage.
Direction visuelle : une palette délibérée et sobre adaptée au contenu
(jamais le violet/indigo par défaut des interfaces générées par IA),
sans-serif, aucun emoji.

```
Crée une visualisation HTML interactive d'un découpage produit en features, à
partir des données que je te fournirai. Objectif : me servir de support pour
arbitrer le découpage en revue de couplage.

Style : une palette délibérée et sobre adaptée au contenu (jamais le violet/indigo
par défaut des interfaces générées par IA), lisible, sans-serif, aucun emoji.

Représentation :
- Chaque feature est un bloc, avec son identifiant et son nom.
- Les dépendances entre features sont des flèches orientées, l'ordre de
  fabrication doit se lire.
- Les couplages, états partagés entre deux features, sont signalés par un lien
  distinct et une couleur d'alerte, parce que ce sont les points de vigilance.
- Une vue de parallélisme : ce qui peut avancer en même temps, ce qui doit
  attendre.
- Le walking skeleton, première tranche de bout en bout, mis en avant.

Ajoute une légende claire. La visualisation doit rendre évidents deux choses :
l'ordre de fabrication, et les couplages à surveiller.
```
