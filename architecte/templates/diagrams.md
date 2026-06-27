# Diagrammes d'architecture

<!-- Public visé : humains — pour revoir et valider les décisions d'architecture. -->
<!-- Tous les diagrammes utilisent la syntaxe Mermaid. Remplacer chaque [placeholder]
     par des noms réels de l'architecture. Ajouter ou retirer des nœuds pour coller au
     système réel. -->
<!-- Conserver la syntaxe Mermaid intacte. Utiliser [À VALIDER] là où une valeur manque. -->

---

## 1. Diagramme de contexte (C4 niveau 1)

<!-- Montre le système comme une boîte noire et tous les acteurs / systèmes externes
     qui interagissent avec lui. Une boîte par acteur ou système externe ; les flèches
     indiquent le sens de l'interaction avec un libellé court. -->

```mermaid
C4Context
  title Contexte système — [Nom du système]

  Person(userA, "[Type d'acteur]", "[Brève description de cet acteur]")
  Person(userB, "[Type d'acteur]", "[Brève description]")

  System(system, "[Nom du système]", "[Objet du système en une ligne]")

  System_Ext(extA, "[Système externe]", "[Ce qu'il fournit]")
  System_Ext(extB, "[Système externe]", "[Ce qu'il fournit]")

  Rel(userA, system, "[Action]", "[protocole/canal]")
  Rel(userB, system, "[Action]", "[protocole/canal]")
  Rel(system, extA, "[Action]", "[protocole/canal]")
  Rel(system, extB, "[Action]", "[protocole/canal]")
```

---

## 2. Diagramme de conteneurs (C4 niveau 2)

<!-- Montre toutes les unités déployables majeures (conteneurs) à l'intérieur de la
     frontière du système et comment elles communiquent. La stack technique de chaque
     conteneur est notée. -->

```mermaid
C4Container
  title Diagramme de conteneurs — [Nom du système]

  Person(user, "[Acteur]", "[Description]")

  System_Boundary(sys, "[Nom du système]") {
    Container(containerA, "[Nom du conteneur]", "[Technologie]", "[Responsabilité]")
    Container(containerB, "[Nom du conteneur]", "[Technologie]", "[Responsabilité]")
    Container(containerC, "[Nom du conteneur]", "[Technologie]", "[Responsabilité]")
    ContainerDb(db1, "[Nom de la base]", "[Technologie]", "[Ce qu'elle stocke]")
    ContainerDb(db2, "[Nom de la base]", "[Technologie]", "[Ce qu'elle stocke]")
  }

  System_Ext(ext, "[Système externe]", "[Description]")

  Rel(user, containerA, "[Action]", "HTTPS")
  Rel(containerA, containerB, "[Action]", "[protocole]")
  Rel(containerB, db1, "lit/écrit", "[pilote/protocole]")
  Rel(containerC, db2, "lit/écrit", "[pilote/protocole]")
  Rel(containerB, ext, "[Action]", "HTTPS")
```

---

## 3. Diagramme de flux / séquence — [Nom du parcours critique]

<!-- Trace les données à travers le système pour le parcours utilisateur le plus
     important. Répéter cette section pour un second parcours critique si pertinent. -->

```mermaid
sequenceDiagram
  actor User as [Acteur]
  participant A as [Composant A]
  participant B as [Composant B]
  participant DB as [Base de données]
  participant Ext as [Système externe]

  User->>A: [Action / requête]
  A->>B: [Appel interne]
  B->>DB: [Requête / écriture]
  DB-->>B: [Résultat]
  B->>Ext: [Appel externe]
  Ext-->>B: [Réponse]
  B-->>A: [Résultat]
  A-->>User: [Réponse]
```

---

## 4. Diagramme entité-association (ERD)

<!-- Modèle de données central. Montrer les entités, leurs attributs clés et les
     associations. Utiliser la notation patte-d'oie (crow's foot) pour la cardinalité. -->

```mermaid
erDiagram
  [ENTITE_A] {
    uuid   id          PK
    string [champ]
    string [champ]
    timestamp created_at
    timestamp updated_at
  }

  [ENTITE_B] {
    uuid   id          PK
    uuid   entity_a_id FK
    string [champ]
    timestamp created_at
  }

  [ENTITE_C] {
    uuid   id          PK
    string [champ]
  }

  [ENTITE_A] ||--o{ [ENTITE_B] : "a plusieurs"
  [ENTITE_B] }o--|| [ENTITE_C] : "appartient à"
```

---

## 5. Diagramme de déploiement

<!-- Topologie d'infrastructure : comment les conteneurs sont mappés sur les ressources
     d'infrastructure, et comment ils se connectent. -->

```mermaid
graph TB
  subgraph Internet
    User([Utilisateur])
  end

  subgraph "[Fournisseur cloud / Région]"
    subgraph "[Réseau / VPC]"
      LB[Répartiteur de charge]

      subgraph "[Cluster de calcul / AZ 1]"
        A1[[Conteneur A — instance 1]]
        B1[[Conteneur B — instance 1]]
      end

      subgraph "[Cluster de calcul / AZ 2]"
        A2[[Conteneur A — instance 2]]
        B2[[Conteneur B — instance 2]]
      end

      DB[(Base primaire)]
      DBR[(Réplica de base)]
      Cache[(Cache)]
      Queue([File])
    end
  end

  subgraph "Externe"
    Ext([Service externe])
  end

  User -->|HTTPS| LB
  LB --> A1 & A2
  A1 & A2 --> B1 & B2
  B1 & B2 --> DB
  DB -->|réplication| DBR
  B1 & B2 --> Cache
  B1 & B2 --> Queue
  B1 & B2 --> Ext
```
