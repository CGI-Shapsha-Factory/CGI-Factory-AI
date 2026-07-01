---
version: 1
date: AAAA-MM-JJ
---
<!-- version : compteur d'itération de ce document (entier, +1 à chaque régénération). date : jour de génération (format AAAA-MM-JJ, à remplacer par la date réelle). -->

# Drivers d'architecture & attributs de qualité

<!-- Public visé : architectes + humains qui tranchent ; sert de socle aux ADR et au
     walking skeleton. -->
<!-- Remplir chaque [placeholder]. Une valeur manquante n'est PAS laissée en marqueur
     dans le fichier final : elle se résout en session (on pose la question à
     l'utilisateur, on écrit la réponse en place). Contenu seul : aucune provenance,
     aucun horodatage, aucun nom de personne. -->

> Ces drivers et attributs dérivent des seeds qualité du cadrage (charge / disponibilité /
> performance) et des contraintes. On écrit le contenu, jamais qui l'a dit ni quand.

---

## Drivers d'architecture

<!-- Ce qui compte le plus pour CE produit, classé par priorité (1 = le plus
     structurant). Un driver est une force qui oriente l'architecture : enjeu métier,
     contrainte forte, attribut de qualité dominant, risque majeur. Le désigner par son
     NOM en clair, jamais par un code. -->

| Priorité | Driver                                  | Pourquoi il pèse sur l'architecture                     |
|----------|-----------------------------------------|---------------------------------------------------------|
| 1        | [driver le plus structurant]            | [conséquence concrète sur les choix techniques]         |
| 2        | [driver suivant]                        | [...]                                                   |
| 3        | [...]                                    | [...]                                                   |

<!-- Ajouter une ligne par driver. Un driver non confirmé par la matière se tranche en
     session (on pose la question), jamais laissé indéfini dans le fichier. -->

## Attributs de qualité

<!-- Attributs de qualité (qualités non fonctionnelles) classés par importance pour ce
     produit. Classer chaque attribut sous une caractéristique ISO/IEC 25010:2023 :
     pertinence fonctionnelle, efficacité de performance, compatibilité, capacité
     d'interaction (utilisabilité), fiabilité, sécurité, maintenabilité, flexibilité
     (portabilité), sûreté (safety). Ne garder que celles qui s'appliquent. -->

| Priorité | Attribut                      | Cible / exigence (mesurable)                    |
|----------|-------------------------------|-------------------------------------------------|
| 1        | [ex. Performance]             | [ex. p95 < 200 ms sur les lectures]             |
| 2        | [ex. Disponibilité]           | [ex. 99,9 % de dispo mensuelle]                 |
| 3        | [ex. Sécurité]                | [ex. toutes les données au repos chiffrées]     |
| 4        | [ex. Charge / scalabilité]    | [ex. N utilisateurs simultanés au pic]          |
| 5        | [ex. Évolutivité / maintenabilité] | [ex. nouveau type d'intégration en < 1 sprint] |

<!-- Classer du plus prioritaire au moins prioritaire. Une cible non chiffrée se précise
     en session avec l'utilisateur (réponse recommandée + alternative + saisir), écrite
     en place — jamais laissée indéfinie. -->

## Scénarios de qualité testables (QAW)

<!-- Pour CHAQUE attribut prioritaire ci-dessus, un scénario de qualité au format
     canonique ATAM en SIX parties : Source du stimulus · Stimulus · Environnement ·
     Artefact · Réponse · Mesure de réponse. La mesure de réponse doit être observable
     et chiffrée (ex. p95 < X ms à N utilisateurs simultanés), sinon le scénario n'est
     pas testable. -->

### Scénario 1 — [Attribut : ex. Efficacité de performance]

- **Source du stimulus** : [qui/quoi génère le stimulus : ex. un utilisateur]
- **Stimulus** : [la condition : ex. demande l'historique de ses commandes]
- **Environnement** : [conditions : ex. charge nominale, base de 1 M de commandes]
- **Artefact** : [élément stimulé : ex. le service de lecture / l'API]
- **Réponse** : [activité déclenchée : ex. l'historique est renvoyé]
- **Mesure de réponse** : [mesurable : ex. p95 < 200 ms à 500 utilisateurs simultanés]

### Scénario 2 — [Attribut : ex. Fiabilité / disponibilité]

- **Source du stimulus** : [ex. une instance applicative]
- **Stimulus** : [ex. tombe en panne]
- **Environnement** : [ex. production, charge de pointe]
- **Artefact** : [ex. le pool d'instances / le répartiteur de charge]
- **Réponse** : [ex. l'instance est retirée, bascule sur une autre]
- **Mesure de réponse** : [ex. aucune requête en échec, bascule < 5 s]

### Scénario 3 — [Attribut : ex. Sécurité]

- **Source du stimulus** : [ex. un client non authentifié]
- **Stimulus** : [ex. envoie une requête sans jeton valide]
- **Environnement** : [ex. fonctionnement nominal]
- **Artefact** : [ex. un endpoint protégé]
- **Réponse** : [ex. la requête est rejetée et journalisée]
- **Mesure de réponse** : [ex. rejet 401 en < 50 ms, tentative journalisée]

<!-- Ajouter un scénario par attribut prioritaire. Numéroter en continu. -->
