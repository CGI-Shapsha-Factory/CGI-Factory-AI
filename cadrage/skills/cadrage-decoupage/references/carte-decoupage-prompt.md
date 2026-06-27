# Prompt Claude Design — Carte de découpage et dépendances

À coller dans Claude Design, avec les données du `spec-index.md` et du
`coupling-map.md` en matière source. Sert de support à la revue de couplage.
Direction de marque : violet sobre en primaire, sobre, sans-serif, aucun
emoji.

```
Crée une visualisation HTML interactive d'un découpage produit en features, à
partir des données que je te fournirai. Objectif : me servir de support pour
arbitrer le découpage en revue de couplage.

Style : violet #5336AB en primaire, sobre, lisible, sans-serif, aucun emoji.

Représentation :
- Chaque feature est un bloc, avec son identifiant, son nom et une étiquette MVP
  ou hors MVP, les blocs MVP visuellement distingués.
- Les dépendances entre features sont des flèches orientées, l'ordre de
  fabrication doit se lire.
- Les couplages, états partagés entre deux features, sont signalés par un lien
  distinct et une couleur d'alerte, parce que ce sont les points de vigilance.
- Une vue de parallélisme : ce qui peut avancer en même temps, ce qui doit
  attendre.
- Le walking skeleton, première tranche de bout en bout, mis en avant.

Ajoute une légende claire. La visualisation doit rendre évidents trois choses :
l'ordre, le périmètre du MVP, et les couplages à surveiller.
```
