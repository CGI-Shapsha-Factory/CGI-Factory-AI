---
version: 1
date: AAAA-MM-JJ
---
<!-- version : compteur d'itération de ce document (entier, +1 à chaque régénération). date : jour de génération (format AAAA-MM-JJ, à remplacer par la date réelle). -->

# Diagrammes d'architecture

<!-- Public visé : humains - pour revoir et valider les décisions d'architecture. -->
<!-- Tous les diagrammes utilisent la syntaxe D2 (https://d2lang.com), rendue avec le moteur
     de layout ELK : routage orthogonal, sans chevauchement de flèches ni de libellés.
     Remplacer chaque [placeholder] par des noms réels de l'architecture. Ajouter ou retirer
     des nœuds pour coller au système réel. -->
<!-- Conserver la syntaxe D2 intacte. Une valeur manquante se tranche en session, pas laissée
     en marqueur dans le fichier final. Après écriture, les blocs D2 sont rendus en SVG
     (source de vérité, vectoriel) + PNG (best-effort) dans `architecte-out/diagrammes/` par
     `scripts/render_diagrams.py`. Le thème se choisit par bloc via l'info-string du fence
     (ouvrir le bloc avec "d2 theme=0" ; thèmes utiles : 0 = neutre par défaut, 303 = C4,
     200 = sombre). -->
<!-- Conventions visuelles C4 conservées ici avec le thème neutre : système = rectangle bleu
     plein ; conteneurs = rectangles bleus ; base de données = shape cylinder ; systèmes
     externes = rectangles gris ; acteurs = shape person. -->
<!-- Couleur de trait par entité source. Dans les diagrammes denses (conteneurs, flux,
     déploiement), plusieurs flèches partent du même composant et se croisent : on donne à
     chaque entité émettrice une couleur de trait dédiée, pour suivre l'origine de chaque
     flèche d'un coup d'oeil. Syntaxe D2 (glob de connexion, écrit APRÈS les connexions
     ciblées, chemin qualifié complet si la source est imbriquée) :
       (system.containerA -> **)[*].style.stroke: "#c2410c"
     Le double glob `**` est obligatoire : avec un simple `*`, les cibles imbriquées dans un
     conteneur ne sont pas atteintes. La couleur d'une entité émettrice sert AUSSI de contour
     à son rectangle - sur la déclaration du noeud, `style.stroke: "<même hex>"` et
     `style.stroke-width: 3` - pour qu'on retrouve du premier coup d'oeil la boîte d'où part
     un faisceau. Les entités qui n'émettent rien (bases, secrets, journalisation, systèmes
     externes) gardent leur contour d'origine : c'est ce contraste qui désigne les émetteurs.
     Palette fixe, à prendre dans cet ordre : #c2410c (orange brûlé), #0891b2 (cyan),
     #7c3aed (violet), #15803d (vert), #b91c1c (rouge), #a16207 (ocre). Au-delà de six
     sources, recycler la palette sans donner la même teinte à deux sources dont les flèches
     se croisent. La couleur complète les libellés, elle ne les remplace pas. Ne s'applique
     PAS au diagramme de contexte (peu de flèches) ni à l'ERD (relations de données). -->

---

## 1. Diagramme de contexte (C4 niveau 1)

<!-- Montre le système comme une boîte noire et tous les acteurs / systèmes externes qui
     interagissent avec lui. Une boîte par acteur ou système externe ; les flèches indiquent
     le sens de l'interaction avec un libellé court (action + protocole entre crochets).
     Pas de coloriage par source ici : les flèches sont peu nombreuses et ne se croisent pas. -->

```d2 theme=0
title: "Contexte système - [Nom du système]" { near: top-center; shape: text; style.font-size: 24; style.bold: true }
direction: down

userA: "[Type d'acteur]\n[Brève description de cet acteur]" { shape: person; width: 96; height: 96 }
userB: "[Type d'acteur]\n[Brève description]" { shape: person; width: 96; height: 96 }

system: "[Nom du système]\n[Objet du système en une ligne]" {
  style.fill: "#1f6feb"; style.font-color: "#ffffff"; style.stroke: "#0b3b8c"; style.bold: true
}

extA: "[Système externe]\n[Ce qu'il fournit]" { style.fill: "#8a8a8a"; style.font-color: "#ffffff"; style.stroke: "#5f5f5f" }
extB: "[Système externe]\n[Ce qu'il fournit]" { style.fill: "#8a8a8a"; style.font-color: "#ffffff"; style.stroke: "#5f5f5f" }

userA -> system: "[Action] [protocole]"
userB -> system: "[Action] [protocole]"
system -> extA: "[Action] [protocole]"
system -> extB: "[Action] [protocole]"
```

---

## 2. Diagramme de conteneurs (C4 niveau 2)

<!-- Montre toutes les unités déployables majeures (conteneurs) à l'intérieur de la frontière
     du système et comment elles communiquent. La stack technique de chaque conteneur est
     notée entre crochets. La frontière est un conteneur D2 (`[Nom] { ... }`) ; les systèmes
     externes restent en dehors. Garder les libellés de flèche courts pour éviter de
     surcharger les zones où plusieurs flèches convergent. Chaque conteneur qui émet
     plusieurs flèches reçoit sa couleur de trait (bloc de globs en fin de diagramme). -->

```d2 theme=0
title: "Diagramme de conteneurs - [Nom du système]" { near: top-center; shape: text; style.font-size: 24; style.bold: true }
direction: down

user: "[Acteur]\n[Description]" { shape: person; width: 96; height: 96 }

system: "[Nom du système]" {
  style.stroke: "#1f6feb"; style.fill: "#f5f9ff"; style.font-color: "#0b3b8c"; style.bold: true

  containerA: "[Nom du conteneur]\n[Technologie]\n[Responsabilité]" { style.fill: "#4a90e2"; style.font-color: "#ffffff"; style.stroke: "#c2410c"; style.stroke-width: 3 }
  containerB: "[Nom du conteneur]\n[Technologie]\n[Responsabilité]" { style.fill: "#4a90e2"; style.font-color: "#ffffff"; style.stroke: "#0891b2"; style.stroke-width: 3 }
  db: "[Nom de la base]\n[Technologie]\n[Ce qu'elle stocke]" { shape: cylinder; style.fill: "#3b7dd8"; style.font-color: "#ffffff"; style.stroke: "#2f6fb0" }
}

ext: "[Système externe]\n[Description]" { style.fill: "#8a8a8a"; style.font-color: "#ffffff"; style.stroke: "#5f5f5f" }

user -> system.containerA: "[Action] [HTTPS]"
system.containerA -> system.containerB: "[Action] [protocole]"
system.containerB -> system.db: "Lit/écrit [pilote/protocole]"
system.containerB -> ext: "[Action] [HTTPS]"

# Couleur de trait par entité source (une ligne par conteneur émetteur)
(system.containerA -> **)[*].style.stroke: "#c2410c"
(system.containerB -> **)[*].style.stroke: "#0891b2"
```

---

## 3. Diagramme de flux / séquence : [Nom du parcours critique]

<!-- Trace les données à travers le système pour le parcours utilisateur le plus important.
     L'ordre des messages = l'ordre d'affichage. Répéter cette section pour un second parcours
     critique si pertinent. Le libellé du conteneur de séquence est vide ("") pour ne pas
     afficher un titre parasite. -->

```d2 theme=0
title: "Flux - [Nom du parcours critique]" { near: top-center; shape: text; style.font-size: 22; style.bold: true }

flow: "" {
  shape: sequence_diagram

  user: "[Acteur]" { shape: person; style.stroke: "#c2410c"; style.stroke-width: 3 }
  a: "[Composant A]" { style.stroke: "#0891b2"; style.stroke-width: 3 }
  b: "[Composant B]" { style.stroke: "#7c3aed"; style.stroke-width: 3 }
  db: "[Base de données]" { shape: cylinder; style.stroke: "#15803d"; style.stroke-width: 3 }
  ext: "[Système externe]" { style.stroke: "#b91c1c"; style.stroke-width: 3 }

  user -> a: "[Action / requête]"
  a -> b: "[Appel interne]"
  b -> ext: "[Appel externe]"
  ext -> b: "[Réponse]"
  b -> db: "[Requête / écriture]"
  db -> b: "[Résultat]"
  b -> a: "[Résultat]"
  a -> user: "[Réponse]"

  # Couleur de trait par émetteur de message
  (user -> **)[*].style.stroke: "#c2410c"
  (a -> **)[*].style.stroke: "#0891b2"
  (b -> **)[*].style.stroke: "#7c3aed"
  (db -> **)[*].style.stroke: "#15803d"
  (ext -> **)[*].style.stroke: "#b91c1c"
}
```

---

## 4. Diagramme entité-association (ERD)

<!-- Modèle de données central. Chaque entité est une `shape: sql_table` : les lignes sont
     `nom: type { constraint: primary_key | foreign_key }`. Les associations sont des flèches
     entre colonnes (`TABLE_A.id -> TABLE_B.a_id: "libellé"`). Pas de coloriage par source
     ici : les flèches portent des relations de données, pas des flux d'appel. -->

```d2 theme=0
title: "Modèle de données - [Nom du système]" { near: top-center; shape: text; style.font-size: 22; style.bold: true }
direction: right

ENTITE_A: {
  shape: sql_table
  id: uuid { constraint: primary_key }
  champ_1: string
  champ_2: string
  created_at: timestamp
  updated_at: timestamp
}

ENTITE_B: {
  shape: sql_table
  id: uuid { constraint: primary_key }
  entite_a_id: uuid { constraint: foreign_key }
  champ: string
  created_at: timestamp
}

ENTITE_C: {
  shape: sql_table
  id: uuid { constraint: primary_key }
  champ: string
}

ENTITE_A.id -> ENTITE_B.entite_a_id: "a plusieurs"
ENTITE_B.id -> ENTITE_C.id: "appartient à"
```

---

## 5. Diagramme de déploiement

<!-- Topologie d'infrastructure : comment les conteneurs sont mappés sur les ressources
     d'infrastructure, et comment ils se connectent. Les zones (cloud, région, réseau, cluster)
     sont des conteneurs D2 imbriqués ; les datastores sont des `shape: cylinder`. -->

```d2 theme=0
title: "Déploiement - [Fournisseur cloud / Région]" { near: top-center; shape: text; style.font-size: 22; style.bold: true }
direction: down

internet: "Internet" {
  style.fill: "#eef2f7"; style.stroke: "#b6c2d2"
  user: "[Utilisateur]" { shape: person; style.stroke: "#c2410c"; style.stroke-width: 3 }
}

cloud: "[Fournisseur cloud / Région]" {
  style.fill: "#f3f8ff"; style.stroke: "#4a90e2"; style.font-color: "#0b3b8c"; style.bold: true

  compute: "[Cluster de calcul / Runtime]" {
    style.fill: "#ffffff"; style.stroke: "#9db8d8"
    a: "[Conteneur A]" { style.stroke: "#0891b2"; style.stroke-width: 3 }
    b: "[Conteneur B]" { style.stroke: "#7c3aed"; style.stroke-width: 3 }
  }
  db: "[Base primaire]" { shape: cylinder }
  cache: "[Cache]" { shape: cylinder }
}

externe: "Externe" {
  style.fill: "#f4f4f4"; style.stroke: "#b0b0b0"
  ext: "[Service externe]" { style.fill: "#8a8a8a"; style.font-color: "#ffffff" }
}

internet.user -> cloud.compute.a: "HTTPS"
cloud.compute.a -> cloud.compute.b: "[protocole]"
cloud.compute.b -> cloud.db
cloud.compute.b -> cloud.cache
cloud.compute.b -> externe.ext

# Couleur de trait par entité source (une ligne par noeud émetteur)
(internet.user -> **)[*].style.stroke: "#c2410c"
(cloud.compute.a -> **)[*].style.stroke: "#0891b2"
(cloud.compute.b -> **)[*].style.stroke: "#7c3aed"
```
