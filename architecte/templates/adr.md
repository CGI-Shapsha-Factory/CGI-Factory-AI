---
version: 1
date: AAAA-MM-JJ
---
<!-- version : reste à 1 (un ADR accepté est immuable - l'évolution passe par le champ Statut et un ADR successeur). date : jour de la décision (AAAA-MM-JJ, à remplacer par la date réelle). -->

# ADR-NNN : [Titre de la décision]

<!-- Un ADR par décision technique majeure. Remplacer NNN par un numéro de séquence
     complété par des zéros (001, 002, ...). Nom de fichier : ADR-NNN-titre-court.md -->
<!-- Remplir chaque [placeholder]. Utiliser les marqueurs [À VALIDER] / [À CHIFFRER]
     là où une valeur manque.  -->
<!-- FIDÉLITÉ (obligatoire) : un ADR ne consigne QU'UNE décision explicitement validée
     par l'humain en session. Ne jamais graver une décision que l'utilisateur n'a pas
     tranchée, ni une formule du type "décision non remise en question" sur un choix
     jamais proposé. Les "Options considérées" ci-dessous sont celles réellement
     présentées à l'utilisateur. N'inventer AUCUNE prémisse (composition d'équipe, infra
     existante, contrainte...) : si une prémisse est nécessaire, la demander d'abord. -->

**Statut :** Accepté
<!-- Statut : Proposé | Accepté | Déprécié | Remplacé par ADR-NNN -->

## Contexte

[Pourquoi cette décision était nécessaire. Quel problème ou quelle contrainte l'a rendue
nécessaire. Ce qui se passe si cette décision n'est pas prise. 2 à 4 phrases. N'énoncer
que des faits établis avec l'utilisateur (issus du cadrage ou tranchés en session) -
aucune prémisse supposée.]

## Décision

[Ce qui a été décidé, énoncé clairement. Un court paragraphe.]

## Options considérées

| Option              | Avantages                               | Inconvénients                            |
|---------------------|-----------------------------------------|------------------------------------------|
| [Option retenue]    | [avantage 1] · [avantage 2]             | [inconvénient 1] · [inconvénient 2]      |
| [Alternative 1]     | [avantage 1] · [avantage 2]             | [inconvénient 1] · [inconvénient 2]      |
| [Alternative 2]     | [avantage 1] · [avantage 2]             | [inconvénient 1] · [inconvénient 2]      |

## Conséquences

**Positives :**
- [bénéfice - 1]
- [bénéfice - 2]

**Négatives / compromis :**
- [compromis - 1]
- [compromis - 2]

**Risques :**
- [risque - 1 avec probabilité et mitigation]

## Déclencheur de revue

[La condition précise sous laquelle cette décision devra être réexaminée.
Exemples : "Si les utilisateurs actifs mensuels dépassent 1 M", "Si l'équipe dépasse
10 ingénieurs", "Si le SLA de latence passe sous 99,5 % deux semaines consécutives".]
