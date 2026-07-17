---
version: 1
date: AAAA-MM-JJ
---
<!-- version : compteur d'itération de ce document (entier, +1 à chaque régénération). date : jour de génération (format AAAA-MM-JJ, à remplacer par la date réelle). -->

# Registre des risques techniques

<!-- Public visé : architectes + humains qui tranchent. Sert à piloter les spikes/POC
     et le contenu du walking skeleton. -->
<!-- Remplir chaque [placeholder]. Utiliser les marqueurs [À VALIDER] / [À CHIFFRER]
     là où une valeur manque.  -->

> Les risques qui nécessitent un spike avant de s'engager sont signalés (colonne
> "Spike/POC nécessaire ?" = Oui) ; le walking skeleton en dérisque une partie en
> traversant de bout en bout le chemin technique le plus incertain.

## Registre

<!-- Probabilité : Faible / Moyenne / Élevée. Impact : Faible / Moyen / Élevé / Critique.
     Statut : Ouvert / En cours / Dérisqué / Accepté / Clos. -->

| Risque                                  | Probabilité | Impact   | Mitigation                                  | Spike/POC nécessaire ? | Statut  |
|-----------------------------------------|-------------|----------|---------------------------------------------|------------------------|---------|
| [ex. La latence du fournisseur tiers dépasse le budget] | Moyenne | Élevé | [ex. cache + circuit breaker ; POC de charge] | Oui                    | Ouvert  |
| [ex. Le volume de données dépasse la capacité du moteur retenu] | Faible | Critique | [ex. partitionnement ; valider à N lignes]  | Oui                    | Ouvert  |
| [ex. Montée en compétence de l'équipe sur le framework] | Élevée | Moyen | [ex. pairing + spike d'apprentissage]        | Non                    | En cours|
| [risque - 4]                            | [...]       | [...]    | [...]                                        | [Oui / Non]            | [...]   |

<!-- Ajouter une ligne par risque identifié. Tout risque dont la probabilité ou l'impact
     n'est pas évalué porte [À VALIDER]. -->

## Spikes / POC à mener avant engagement

<!-- Détailler chaque ligne marquée "Oui" ci-dessus : ce qu'on cherche à prouver et le
     critère d'arrêt (ce qui permet de déclarer le risque dérisqué). -->

- **[Risque X]** - Hypothèse à valider : [...]. Critère de succès : [mesurable, ex. p95 < X ms à N req/s]. [À CHIFFRER]
- **[Risque Y]** - Hypothèse à valider : [...]. Critère de succès : [...].

## Lien avec le walking skeleton

<!-- Indiquer quels risques le walking skeleton adresse en priorité (la traversée
     bout-en-bout doit couvrir le chemin technique le plus incertain). -->

[Le walking skeleton traverse [composants concernés] et dérisque ainsi : [liste des
risques couverts]. Les risques restants sont traités par des spikes dédiés ci-dessus.] [À VALIDER]
