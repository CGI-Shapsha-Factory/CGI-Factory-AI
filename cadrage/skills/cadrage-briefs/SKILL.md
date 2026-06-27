---
name: cadrage-briefs
description: Génère un brief auto-portant par feature, prêt pour SpecKit.
---

# cadrage-briefs

Quatrième étape. Produit l'artefact dont tout le pipeline dépend : un brief
auto-portant par feature, au contrat central, consommable par SpecKit.

## Objectif

Pour chaque feature, générer un **brief auto-suffisant** : un développeur qui ne
lit que ce brief plus la pré-constitution a de quoi spécifier la feature. Inclut la
**formalisation** des critères de succès (outcome → métrique cible) et
d'acceptation (scénarios Étant donné / quand / alors).

## Entrée

- `factory-docs/work/spec-index.md` **arbitré**
- `factory-docs/work/product-brief.md`
- `factory-docs/work/glossaire.md`

Gabarit de sortie : `factory-docs/templates/feature-brief.md` (le **contrat
central**, copie installée par cadrage-init).

## Porte d'entrée — DURE (double condition)

**`decoupage_arbitrated == true` ET `demonstrateur_converged == true`.** Porte
dure : aucun brief n'est finalisé tant que ces deux conditions ne sont pas
réunies.

- **`decoupage_arbitrated`** : la revue de couplage humaine a arbitré le découpage.
- **`demonstrateur_converged`** : la boucle démonstrateur a convergé — aucun point
  de validation bloquant ouvert et maquette validée par le client. Un brief dérive
  d'une **vision stable** ; tant que la boucle n'a pas convergé, la vision peut
  encore bouger, donc les briefs ne se finalisent pas.

Si l'une des deux conditions n'est pas réunie, le skill **refuse de tourner**. La
logique de gate ci-dessus reste intacte, mais le **message de refus est en
français naturel**, sans aucun nom d'attribut ni tableau de booléens (convention
`references/ux-conventions.md`). Message cible :

> « Cette étape ne peut pas démarrer encore : la revue de couplage et la validation
> du prototype doivent d'abord être faites. »

**Garde-fou déterministe (anti-contournement).** Avant toute génération, lancer
`python scripts/check_ready.py <projet>/factory-docs/manifest.json` : il échoue (exit 1)
si `decoupage_arbitrated` ou `demonstrateur_converged` n'est pas vrai. **Ne jamais
contourner** : en cas d'échec, refuser (message ci-dessus) et orienter vers la revue de
couplage (`/cadrage:cadrage-decoupage`) puis la boucle démonstrateur
(`/cadrage:cadrage-demonstrateur-brief`). C'est la garantie déterministe que les deux
portes humaines ont bien été franchies avant les briefs.

Adapter selon ce qui manque (en restant en clair) : si le prototype n'est pas
encore validé, renvoyer vers la boucle (clarification → retour-démonstrateur →
brief-démonstrateur) puis le point de complétude ; s'il manque la revue de
couplage, renvoyer vers cette revue. Ne **jamais** afficher
`decoupage_arbitrated == false` ni équivalent. Ne contourne jamais cette porte.

## Procédure

Pour **chaque feature** du spec index arbitré, produire
`work/00X-<feature>.brief.md` aux **10 sections du contrat central** :

1. **Narratif** — 2 à 4 phrases héritées de la vision. Problème résolu, valeur.
   Aucune techno.
2. **Utilisateurs concernés** — personas, repris de la vision.
3. **User stories** — En tant que <rôle>, je veux <action>, afin de <bénéfice>.
   Plusieurs par feature, chacune testable isolément.
4. **Critères d'acceptation** — par story, **au moins un** scénario Étant donné /
   quand / alors. Cas nominal + cas limites connus.
5. **Critères de succès mesurables** — outcomes en métriques avec cible chiffrée,
   agnostiques de la techno. **`[À CHIFFRER]` si la cible n'a pas été captée.**
6. **Périmètre** — IN et OUT (OUT explicite).
7. **Dépendances** — reprises du spec index, ordre induit.
8. **Contraintes héritées** — celles de la vision/pré-constitution applicables.
9. **Glossaire pertinent** — extrait du glossaire global, termes mobilisés.
10. **Trous** — liste des `[À VALIDER]`. Vide quand le brief est complet.

**Formalisation à fournir :**
- *Succès* : traduire chaque outcome capté en métrique + cible (ou `[À CHIFFRER]`).
- *Acceptation* : pour chaque story, dériver au moins un scénario testable.

**Ne rien inventer.** Tout élément absent de la matière → `[À VALIDER]` en
section 10. Aucun critère fabriqué.

## Porte de sortie

Pour chaque brief, vérifier :
- **Sections 1 à 9 présentes** (contrat central respecté).
- **Chaque story a au moins un critère d'acceptation.**
- **Critères de succès chiffrés ou marqués `[À CHIFFRER]`.**
- **Périmètre OUT non vide.**
- **Brief auto-suffisant** (auto-contrôle : lisible seul + pré-constitution).
- **Traçabilité** : chaque story / critère d'acceptation / critère de succès porte
  sa source `(src: <réf>)` ; sinon `[À VALIDER]`.
- **Auto-contrôle qualité INVEST / QUS** :
  - chaque story est **I**ndependent, **N**egotiable, **V**aluable, **E**stimable,
    **S**mall, **T**estable ;
  - chaque critère d'acceptation est **non ambigu** (bannir « rapide », « simple »,
    « convivial », « performant »…), **atomique** et **testable**.
- **Statut** : `complete` si la section 10 n'a aucun trou **bloquant** ; sinon
  `draft`. Un brief `complete` **peut** porter des `[À CHIFFRER]` **non-bloquants** (déférés à
  l'architecture) : `complete` signifie « aucun trou bloquant », pas « zéro marqueur ».

## Mise à jour du manifeste

Read-modify-write puis revalidation JSON :
- `artifacts.briefs[]` : une entrée par feature (`id` = l'**identifiant de use case**
  `UC…` du spec-index — identité fonctionnelle stable et **clé de jointure** réutilisée par
  l'architecte (`feature_sequence`) et l'assembleur ; `name`, `path`, `status`, `gaps`, `mvp`).
- `definition_of_ready.all_briefs_complete = true` **si et seulement si** tous
  les briefs sont au statut `complete`.
- `phase = "briefs"`.
- `validation_points[]` : trous bloquants des briefs, `status = "open"`,
  `raised_by = "briefs"`.
- `updated_at`.

## Règles invariantes appliquées ici

- **Porte dure d'arbitrage.** Le skill ne génère rien sans `decoupage_arbitrated`
  vrai. C'est la matérialisation de la revue de couplage humaine.
- **Marquer, ne pas inventer.** Trous en section 10, jamais de comblement.
- **Contrat central.** Les 10 sections, sans dérive de structure.
- **Skill indépendant.** Porte d'entrée et mise à jour via le manifeste.

Étape suivante : `/cadrage:cadrage-completude` — confronter les briefs à la Definition of Ready et faire le point.
