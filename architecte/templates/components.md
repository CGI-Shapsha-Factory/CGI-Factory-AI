# Catalogue des composants

<!-- Public visé : Claude Code — référencé lors de l'implémentation ou de la
     modification de tout composant. -->
<!-- Ajouter une entrée par composant. Inclure TOUS les composants : services,
     workers d'arrière-plan, outils CLI, ordonnanceurs (schedulers) et adaptateurs
     d'intégration externe. -->
<!-- Remplir chaque [placeholder]. Utiliser les marqueurs [À VALIDER] / [À CHIFFRER]
     là où une valeur manque encore.  -->

---

## [NomDuComposant]

- **Objet :** [Une phrase — la raison d'être de ce composant.]
- **Responsabilités :**
  - [ce qu'il fait — 1]
  - [ce qu'il fait — 2]
- **NON responsable de :**
  - [limite explicite — 1]
  - [limite explicite — 2]
- **Interfaces :**
  - Expose : [endpoints d'API / événements publiés / commandes CLI / fonctions exportées]
  - Consomme : [API appelées / événements souscrits / files lues / bibliothèques partagées utilisées]
- **Technologies :**
  - Runtime : [langage + version]
  - Framework : [framework + version, ou « aucun »]
  - Stockages de données : [chaque base/cache/file que ce composant lit ou écrit directement]
  - Services externes : [API tierces, fournisseurs d'authentification, stockage objet, etc.]
- **Contraintes clés :**
  - [règle dure pour ce composant — ex. « ne doit jamais écrire directement dans la base de ServiceB »]
  - [règle dure — ex. « tous les appels HTTP sortants passent par le wrapper du client HTTP »]

---

## [NomDuComposant]

- **Objet :** [...]
- **Responsabilités :**
  - [...]
- **NON responsable de :**
  - [...]
- **Interfaces :**
  - Expose : [...]
  - Consomme : [...]
- **Technologies :**
  - Runtime : [...]
  - Framework : [...]
  - Stockages de données : [...]
  - Services externes : [...]
- **Contraintes clés :**
  - [...]

---

<!-- Répéter le bloc ci-dessus pour chaque composant supplémentaire. -->
<!-- Principe : chaque entrée est AUTO-PORTANTE. Le champ « Technologies » ne liste
     que ce que CE composant utilise directement — pas la stack globale — de sorte
     qu'une IA lisant un seul composant isolément dispose de tout le contexte. -->
