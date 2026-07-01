---
version: 1
date: AAAA-MM-JJ
---
<!-- version : compteur d'itération de ce document (entier, +1 à chaque régénération). date : jour de génération (format AAAA-MM-JJ, à remplacer par la date réelle). -->

# Catalogue des composants

<!-- Public visé : Claude Code — référencé lors de l'implémentation ou de la
     modification de tout composant. -->
<!-- Ajouter une entrée par composant. Inclure TOUS les composants : application(s)
     front-end (SPA / web app / client mobile), services, workers d'arrière-plan,
     outils CLI, ordonnanceurs (schedulers) et adaptateurs d'intégration externe. -->
<!-- RÈGLE FRONTEND (obligatoire) : dès que le produit a un écran utilisateur, le
     catalogue DOIT contenir au moins un composant Frontend/UI — l'application qui rend
     les écrans — déclaré comme composant technique à part entière, avec sa propre stack
     (framework, outil de build, cible de déploiement). L'existence du plugin designer
     n'en dispense PAS : le designer produit le design SYSTEM visuel ; l'architecte
     porte le composant front et sa stack (source de vérité = ce fichier + tech-stack.md). -->
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
  - Runtime : [langage + version EXACTE — ex. « Node.js 24.4.1 » ; pour un front : navigateur cible / cible de build]
  - Framework : [framework + version EXACTE — ex. « React 19.1.0 » ; ou « aucun ». Jamais « latest »/« dernière version »]
  - Stockages de données : [chaque base/cache/file que ce composant lit ou écrit directement — pour un front : état local / cache navigateur, ou « aucun »]
  - Services externes : [API tierces, fournisseurs d'authentification, stockage objet… — pour un front : la/les API back consommées]
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
<!-- COHÉRENCE (obligatoire) : les technos et versions inscrites ici doivent être
     EXACTES (jamais « latest ») et STRICTEMENT cohérentes avec tech-stack.md — mêmes
     technos, mêmes versions. Interdit : un composant décrivant une stack que
     tech-stack.md ne retient pas (ex. un composant en .NET alors que la stack retient
     Python). En cas de doute, tech-stack.md et ce fichier se tranchent ensemble en session. -->
