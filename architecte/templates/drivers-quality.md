# Drivers d'architecture & attributs de qualité

<!-- Public visé : architectes + humains qui tranchent ; sert de socle aux ADR et au
     walking skeleton. -->
<!-- Remplir chaque [placeholder]. Utiliser les marqueurs [À VALIDER] / [À CHIFFRER]
     là où une valeur manque. Conserver la convention (src: …). -->

> Ces drivers et attributs dérivent des *seeds qualité* du cadrage
> (project-frame Q2/Q6/Q7) + contraintes ; chaque entrée porte sa source `(src: …)`.

---

## Drivers d'architecture

<!-- Ce qui compte le plus pour CE produit, classé par priorité (P1 = le plus
     structurant). Un driver est une force qui oriente l'architecture : enjeu métier,
     contrainte forte, attribut de qualité dominant, risque majeur. -->

| Priorité | Driver                                  | Pourquoi il pèse sur l'architecture                     | Source        |
|----------|-----------------------------------------|---------------------------------------------------------|---------------|
| P1       | [driver le plus structurant]            | [conséquence concrète sur les choix techniques]         | (src: …)      |
| P2       | [driver suivant]                        | [...]                                                   | (src: …)      |
| P3       | [...]                                    | [...]                                                   | (src: …)      |

<!-- Ajouter une ligne par driver. Tout driver non confirmé par une source reste [À VALIDER]. -->

## Attributs de qualité

<!-- Attributs de qualité (qualités non fonctionnelles) classés par importance pour ce
     produit. Classer chaque attribut sous une caractéristique ISO/IEC 25010:2023 :
     pertinence fonctionnelle, efficacité de performance, compatibilité, capacité
     d'interaction (utilisabilité), fiabilité, sécurité, maintenabilité, flexibilité
     (portabilité), sûreté (safety). Ne garder que celles qui s'appliquent. -->

| Priorité | Attribut                      | Cible / exigence (mesurable si possible)        | Source        |
|----------|-------------------------------|-------------------------------------------------|---------------|
| 1        | [ex. Performance]             | [ex. p95 < 200 ms sur les lectures] [À CHIFFRER]| (src: …)      |
| 2        | [ex. Disponibilité]           | [ex. 99,9 % de dispo mensuelle] [À CHIFFRER]    | (src: …)      |
| 3        | [ex. Sécurité]                | [ex. toutes les données au repos chiffrées]     | (src: …)      |
| 4        | [ex. Charge / scalabilité]    | [ex. N utilisateurs simultanés au pic]          | (src: …)      |
| 5        | [ex. Évolutivité / maintenabilité] | [ex. nouveau type d'intégration en < 1 sprint] | (src: …)      |

<!-- Classer du plus prioritaire au moins prioritaire. Un attribut sans cible chiffrée
     porte [À CHIFFRER] ; un attribut sans source porte [À VALIDER]. -->

## Scénarios de qualité testables (QAW)

<!-- Pour CHAQUE attribut prioritaire ci-dessus, un scénario de qualité au format
     canonique ATAM en SIX parties : Source du stimulus · Stimulus · Environnement ·
     Artefact · Réponse · Mesure de réponse. La mesure de réponse doit être observable
     et chiffrée (ex. p95 < X ms à N utilisateurs simultanés), sinon le scénario n'est
     pas testable. -->

### Scénario QS-1 — [Attribut : ex. Efficacité de performance]

- **Source du stimulus** : [qui/quoi génère le stimulus : ex. un utilisateur]
- **Stimulus** : [la condition : ex. demande l'historique de ses commandes]
- **Environnement** : [conditions : ex. charge nominale, base de 1 M de commandes]
- **Artefact** : [élément stimulé : ex. le service de lecture / l'API]
- **Réponse** : [activité déclenchée : ex. l'historique est renvoyé]
- **Mesure de réponse** : [mesurable : ex. p95 < 200 ms à 500 utilisateurs simultanés] [À CHIFFRER]
- Source : (src: …)

### Scénario QS-2 — [Attribut : ex. Fiabilité / disponibilité]

- **Source du stimulus** : [ex. une instance applicative]
- **Stimulus** : [ex. tombe en panne]
- **Environnement** : [ex. production, charge de pointe]
- **Artefact** : [ex. le pool d'instances / le répartiteur de charge]
- **Réponse** : [ex. l'instance est retirée, bascule sur une autre]
- **Mesure de réponse** : [ex. aucune requête en échec, bascule < 5 s] [À CHIFFRER]
- Source : (src: …)

### Scénario QS-3 — [Attribut : ex. Sécurité]

- **Source du stimulus** : [ex. un client non authentifié]
- **Stimulus** : [ex. envoie une requête sans jeton valide]
- **Environnement** : [ex. fonctionnement nominal]
- **Artefact** : [ex. un endpoint protégé]
- **Réponse** : [ex. la requête est rejetée et journalisée]
- **Mesure de réponse** : [ex. rejet 401 en < 50 ms, tentative journalisée] [À CHIFFRER]
- Source : (src: …)

<!-- Ajouter un scénario QS-N par attribut prioritaire. Numéroter en continu. -->
