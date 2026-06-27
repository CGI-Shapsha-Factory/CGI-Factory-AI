# Cadre projet — <Nom du projet>

> Document de travail. Contraintes de cadrage du **projet** à cadrer,
> dérivées de la **passe de découverte** de `cadrage-extraction` (13 questions). Chaque
> champ porte sa source `(src: <ref>)` ; tout élément non capté reste `[À VALIDER]`.
> Ce n'est PAS l'architecture : c'est le cadre à partir duquel l'architecte travaillera. Les
> champs **(seed qualité)** seront transformés par l'architecte en drivers qualité /
> scénarios (QAW).

## 1. Utilisateurs & rôles
- **Qui utilise l'application (Q1)** : <profils utilisateurs> (src: …)
- **Rôles utilisateurs (Q3)** : <rôles> (src: …)
- **Volume d'utilisateurs (Q2) (seed qualité — charge)** : nombre total / nombre concurrent (src: …)

## 2. Données
- **Données stockées (Q4)** : quantité, contenu, **sensibilité** (personnelles/réglementées ?) (src: …)

## 3. Intégrations
- **Systèmes externes à intégrer (Q5)** : <systèmes + sens du flux> (src: …)

## 4. Disponibilité & performance *(seeds qualité → architecte)*
- **Disponibilité requise (Q6)** : <SLA / fenêtres / criticité> (src: …)
- **Contraintes de performance (Q7)** : <temps de réponse, débit, volumes> (src: …)

## 5. Légal / réglementaire
- **Contraintes légales (Q8)** : <RGPD, secteur réglementé, rétention, résidence> (src: …)

## 6. Type de projet
- **Type (Q9)** : MVP | projet long terme | autre — et implications (src: …)

## 7. Exploitation / production
- **Qui exploite la production (Q10)** : le client | nous | un tiers (src: …)

## 8. Hébergement & déploiement
- **Cible de déploiement (Q11)** : on-premise | cloud (lequel) | hybride ; infra **existante ou nouvelle** ; souveraineté/localisation (src: …)

## 9. Budget d'infrastructure
- **Budget infra (Q12)** : enveloppe, limites de coûts récurrents, licences (src: …)

## 10. Authentification & autorisation
- **Besoins d'authentification (Q13)** : SSO/fournisseur, MFA, modèle d'autorisation, exigences de rôles (src: …)

<!--
Ces champs correspondent aux 13 questions de découverte
(skills/cadrage-extraction/references/discovery-questions.md). Marquer, ne pas
inventer : tout point non tranché par la matière source reste `[À VALIDER]` et alimente
`cadrage-clarification`. Le statut par question vit dans le bloc `discovery` du
manifeste ; le validateur `scripts/check_discovery.py` vérifie la complétude.
-->
