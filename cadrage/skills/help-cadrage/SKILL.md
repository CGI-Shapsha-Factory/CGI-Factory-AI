---
name: help-cadrage
description: Montre le rôle de chaque skill de cadrage et l'ordre dans lequel les lancer.
---

# help-cadrage

Skill d'aide. Quand il est invoqué, **affiche à l'utilisateur le guide ci-dessous
en français, en bullet points** (sans noms de champs techniques). Il n'écrit aucun
fichier et ne modifie pas le manifeste.

## Guide à afficher

**Le plugin `cadrage` transforme la matière brute d'un atelier (transcripts, docs)
en un pack prêt pour SpecKit. Ordre d'exécution :**

- **0. `cadrage-init`** — initialise le projet : crée le dossier de travail et installe
  les gabarits (ne demande aucun nom). *À lancer en premier.*
- **1. `cadrage-extraction`** — te demande le **nom du projet**, dépouille tes sources
  (fichier, plusieurs fichiers ou dossier ; .txt/.md/.pdf/.docx) en une capture tracée,
  puis te pose une par une les questions de cadrage manquantes (qui utilise, données…).
- **2. `cadrage-vision`** — synthétise la capture en une vision produit : le quoi et
  le pourquoi, sans technique.
- **3. `cadrage-glossaire`** — construit le vocabulaire métier, te l'affiche et te le
  fait valider terme par terme.
- **4. `cadrage-decoupage`** — propose un découpage **fonctionnel** en use cases (par
  valeur) + une carte de couplage (hypothèse), affichés en tableau pour que tu les ajustes.
- **5. `cadrage-demonstrateur-brief`** — produit le prompt pour générer une maquette de
  validation dans Claude Design (tu la confrontes au client).
- **6. `cadrage-retour-demonstrateur`** — ingère le retour du client sur la maquette et
  propage les corrections.
- **7. `cadrage-clarification`** — regroupe tous les points à clarifier en une checklist
  à dérouler en atelier. *(rejouable à tout moment)*
- *(boucle 4→7 : maquette → retour → ajustements, jusqu'à ce que la direction produit soit validée par le client)*
- **— Revue de couplage (toi) —** tu arbitres le découpage en session avec l'assistant
  (pas en éditant un fichier). Obligatoire avant les briefs.
- **8. `cadrage-briefs`** — génère un brief auto-portant par feature, prêt pour SpecKit.
  *Ne démarre qu'une fois la revue de couplage et la maquette validées.*
- **9. `cadrage-completude`** — fait le point : ce qui manque / à corriger / complet, plus
  un résumé d'état pour reprendre après une pause. *(rejouable à tout moment)*
- **10. `cadrage-handoff`** — assemble la pré-constitution + les briefs + le spec index et
  les dépose dans le repo SpecKit. *Ne démarre que si tout est prêt.*

**Repère** : lance `cadrage-completude` quand tu veux savoir où tu en es et quelle
étape lancer ensuite.

## Étape suivante
« Étape suivante : `/cadrage:cadrage-init` pour démarrer un nouveau projet, ou `/cadrage:cadrage-completude` pour reprendre un projet en cours. »
