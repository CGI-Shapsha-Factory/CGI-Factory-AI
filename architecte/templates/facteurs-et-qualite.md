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

> **Drivers** = objectifs métier + contraintes + risques (le *pourquoi* et les limites).
> **Attributs de qualité** = les -ilités **dérivées** de ces drivers, chacune mesurée + un scénario
> testable. Les deux **ne se recouvrent pas** : une -ilité ne se reliste pas comme driver, un driver
> ne se reliste pas comme -ilité. Le tout dérive des seeds qualité du cadrage (charge / disponibilité /
> performance) et des contraintes. On écrit le contenu, jamais qui l'a dit ni quand.

---

## Drivers d'architecture

<!-- Ce qui ORIENTE l'architecture pour CE produit, classé par priorité (1 = le plus
     structurant). Un driver est de l'une de ces 3 espèces, JAMAIS une -ilité :
       - un OBJECTIF MÉTIER (ex. "zéro réponse non sourcée est éliminatoire") ;
       - une CONTRAINTE légale / organisationnelle / technique / d'usage (ex. "hébergement UE
         obligatoire", "équipe de 3,5 personnes", "3 sources documentaires hétérogènes") ;
       - un RISQUE majeur.
     Une -ilité (fiabilité, sécurité, performance, disponibilité, maintenabilité...) n'est PAS un
     driver : elle va dans "Attributs de qualité" ci-dessous (elle en DÉCOULE). Désigner chaque
     driver par son NOM en clair, jamais par un code. -->

| Priorité | Driver                                  | Pourquoi il pèse sur l'architecture                     |
|----------|-----------------------------------------|---------------------------------------------------------|
| 1        | [driver le plus structurant]            | [conséquence concrète sur les choix techniques]         |
| 2        | [driver suivant]                        | [...]                                                   |
| 3        | [...]                                    | [...]                                                   |

<!-- Ajouter une ligne par driver. Un driver non confirmé par la matière se tranche en
     session (on pose la question), jamais laissé indéfini dans le fichier. -->

## Attributs de qualité

<!-- Les -ilités (qualités non fonctionnelles) qui DÉCOULENT des drivers ci-dessus, classées par
     importance. Chacune : une CIBLE MESURABLE + le driver dont elle découle. Classer chaque attribut
     sous une caractéristique ISO/IEC 25010:2023 : pertinence fonctionnelle, efficacité de performance,
     compatibilité, capacité d'interaction (utilisabilité), fiabilité, sécurité, maintenabilité,
     flexibilité (portabilité), sûreté (safety). Ne garder que celles qui s'appliquent.
     RÈGLE ANTI-REDONDANCE : ne jamais recopier ici un driver (objectif/contrainte/risque), ni relister
     un attribut de qualité dans la table des drivers. Chaque ligne pointe le driver source. -->

| Priorité | Attribut                      | Cible / exigence (mesurable)                    | Découle du driver           |
|----------|-------------------------------|-------------------------------------------------|-----------------------------|
| 1        | [ex. Performance]             | [ex. p95 < 200 ms sur les lectures]             | [nom du driver source]      |
| 2        | [ex. Disponibilité]           | [ex. 99,9 % de dispo mensuelle]                 | [nom du driver source]      |
| 3        | [ex. Sécurité]                | [ex. toutes les données au repos chiffrées]     | [nom du driver source]      |
| 4        | [ex. Charge / scalabilité]    | [ex. N utilisateurs simultanés au pic]          | [nom du driver source]      |
| 5        | [ex. Évolutivité / maintenabilité] | [ex. nouveau type d'intégration en < 1 sprint] | [nom du driver source] |

<!-- Classer du plus prioritaire au moins prioritaire. Une cible non chiffrée se précise
     en session avec l'utilisateur (réponse recommandée + alternative + saisir), écrite
     en place - jamais laissée indéfinie. -->

## Scénarios de qualité testables (QAW)

<!-- Pour CHAQUE attribut prioritaire ci-dessus, un scénario de qualité au format
     canonique ATAM en SIX parties : Source du stimulus · Stimulus · Environnement ·
     Artefact · Réponse · Mesure de réponse. La mesure de réponse doit être observable
     et chiffrée (ex. p95 < X ms à N utilisateurs simultanés), sinon le scénario n'est
     pas testable. -->

### Scénario 1 : [Attribut : ex. Efficacité de performance]

- **Source du stimulus** : [qui/quoi génère le stimulus : ex. un utilisateur]
- **Stimulus** : [la condition : ex. demande l'historique de ses commandes]
- **Environnement** : [conditions : ex. charge nominale, base de 1 M de commandes]
- **Artefact** : [élément stimulé : ex. le service de lecture / l'API]
- **Réponse** : [activité déclenchée : ex. l'historique est renvoyé]
- **Mesure de réponse** : [mesurable : ex. p95 < 200 ms à 500 utilisateurs simultanés]

### Scénario 2 : [Attribut : ex. Fiabilité / disponibilité]

- **Source du stimulus** : [ex. une instance applicative]
- **Stimulus** : [ex. tombe en panne]
- **Environnement** : [ex. production, charge de pointe]
- **Artefact** : [ex. le pool d'instances / le répartiteur de charge]
- **Réponse** : [ex. l'instance est retirée, bascule sur une autre]
- **Mesure de réponse** : [ex. aucune requête en échec, bascule < 5 s]

### Scénario 3 : [Attribut : ex. Sécurité]

- **Source du stimulus** : [ex. un client non authentifié]
- **Stimulus** : [ex. envoie une requête sans jeton valide]
- **Environnement** : [ex. fonctionnement nominal]
- **Artefact** : [ex. un endpoint protégé]
- **Réponse** : [ex. la requête est rejetée et journalisée]
- **Mesure de réponse** : [ex. rejet 401 en < 50 ms, tentative journalisée]

<!-- Ajouter un scénario par attribut prioritaire. Numéroter en continu. -->
