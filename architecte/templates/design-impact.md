# Décisions à impact design

> **Contrat propre Architecte → Designer.** Le designer n'a pas besoin de toute l'architecture, seulement
> de la **tranche qui se voit à l'écran**. C'est l'architecte (qui sait ce qui se voit) qui la déclare ici,
> par ordre d'importance. **Contenu seul** : aucune provenance, aucun horodatage, aucun nom de personne.
> **Ne pas inventer** : un point non décidé se **tranche en session** (on pose la question, on écrit la
> réponse en place), jamais laissé en marqueur ; un point sans objet est marqué **sans objet**.
>
> **Exclure d'ici** (pollue le designer) : tout le back, le modèle de données interne, la persistance, le
> déploiement, les ADR purement serveur.

## 1. Stack front & approche de style — (information n°1)
*C'est ce qui rend le design system exécutable et synchronisable via `/design-sync`.*
- **Framework front** : … (ex. React, Vue, Svelte, HTML/CSS)
- **Bibliothèque de composants** : … (ex. maison, shadcn, MUI, aucune)
- **Stratégie CSS / tokens** : … (ex. CSS variables, Tailwind, CSS-in-JS, Style Dictionary)

## 2. Contrats transverses qui se voient
- **Multitenance & theming par tenant** : l'app sert-elle plusieurs clients isolés, chacun avec son
  branding ? oui/non + implication design — sinon **sans objet**.
- **Identité, rôles & autorisations** : variantes par rôle, écran **non autorisé**, écran de **connexion**,
  **session expirée**, SSO.
- **Navigation & routage** : architecture de l'information, patterns de navigation imposés.

## 3. Conventions d'API qui décident des états d'UI
- **Format d'erreur de l'API** : structure (ex. `{field, message}`) → se projette en **messages par champ**.
- **Comportement asynchrone** : opérations longues, polling, websockets → squelettes/spinners/attente.
- **Pagination & listes** : style (offset/cursor), tri, filtres → composants de liste/tableau + cas vides.
- **Cas vides** : conventions de réponse vide → états vides utiles côté UI.

## 4. Exigences non fonctionnelles qui touchent l'UX
*(Déjà hiérarchisées par l'architecte ; on ne reprend QUE celles qui se voient à l'écran.)*
- **Accessibilité visée** : niveau (ex. **WCAG 2.2 AA**) → contrastes, focus visible, navigation clavier.
- **Cibles responsive & breakpoints** : formats supportés (mobile/tablette/bureau) + largeurs de bascule.
- **Internationalisation** : multi-langues / sens de lecture ? → textes de longueur variable. oui/non — sinon **sans objet**.
- **Budget de performance** : limites qui contraignent le design (ex. éviter animations lourdes). — sinon **sans objet**.

---
*Consommé par `/designer:designer` (pré-remplit le versant technique de la checklist de couverture).*
