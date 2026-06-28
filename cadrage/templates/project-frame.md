# Cadre projet — <Nom du projet>

> Document de travail. Contraintes de cadrage du **projet** à cadrer,
> dérivées de la **passe de découverte** de `cadrage-extraction` (13 questions).
> **Contenu uniquement, sans provenance** (pas de `(src:)`) ; un champ non tranché
> est posé en session, pas marqué `[À VALIDER]`.
> Ce n'est PAS l'architecture : c'est le cadre à partir duquel l'architecte travaillera. Les
> champs **(seed qualité)** seront transformés par l'architecte en drivers qualité /
> scénarios (QAW).

## 1. Utilisateurs & rôles
- **Qui utilise l'application (Q1)** : <profils utilisateurs>
- **Rôles utilisateurs (Q3)** : <rôles>
- **Volume d'utilisateurs (Q2) (seed qualité — charge)** : nombre total / nombre concurrent

## 2. Données
- **Données stockées (Q4)** : quantité, contenu, **sensibilité** (personnelles/réglementées ?)

## 3. Intégrations
- **Systèmes externes à intégrer (Q5)** : <systèmes + sens du flux>

## 4. Disponibilité & performance *(seeds qualité → architecte)*
- **Disponibilité requise (Q6)** : <SLA / fenêtres / criticité>
- **Contraintes de performance (Q7)** : <temps de réponse, débit, volumes>

## 5. Légal / réglementaire
- **Contraintes légales (Q8)** : <secteur réglementé, rétention, résidence des données>

## 6. Type de projet
- **Type (Q9)** : <ponctuel | long terme | périmètre visé> — et implications

## 7. Exploitation / production
- **Qui exploite la production (Q10)** : le client | nous | un tiers

## 8. Hébergement & déploiement
- **Cible de déploiement (Q11)** : on-premise | cloud (lequel) | hybride ; infra **existante ou nouvelle** ; souveraineté/localisation

## 9. Budget d'infrastructure
- **Budget infra (Q12)** : enveloppe, limites de coûts récurrents, licences

## 10. Authentification & autorisation
- **Besoins d'authentification (Q13)** : SSO/fournisseur, MFA, modèle d'autorisation, exigences de rôles

<!--
Ces champs correspondent aux 13 questions de découverte
(skills/cadrage-extraction/references/discovery-questions.md). Demander, ne pas
inventer : un point non tranché est posé en session ; s'il n'est pas tranché, il
est omis (pas de `[À VALIDER]`, pas de provenance écrite). Le statut par question
vit dans le bloc `discovery` du manifeste ; le validateur `scripts/check_discovery.py`
vérifie la complétude.
-->
