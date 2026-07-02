---
name: cadrage-briefs
description: Génère un brief auto-portant par feature, repris par l'architecte.
---

# cadrage-briefs

Quatrième étape. Produit l'artefact dont tout le pipeline dépend : un brief
auto-portant par feature, au contrat central, repris en aval par l'architecte
puis l'assembleur.

## Objectif

Pour chaque feature, générer un **brief auto-suffisant** : un lecteur qui ne lit
que ce brief a de quoi comprendre et spécifier la feature. Inclut la
**formalisation** des critères de succès (outcome → métrique cible) et
d'acceptation (scénarios Étant donné / quand / alors).

**Pas d'horodatage, pas de date, pas de nom de personne** issu du transcript : on
capte le **cœur fonctionnel** de la feature, pas qui l'a dite ni quand.

## Entrée

- `cadrage-out/spec-index.md` **arbitré**
- `cadrage-out/product-brief.md`
- `cadrage-out/glossaire.md`

Gabarit de sortie : `.factory/templates/feature-brief.md` (le **contrat
central**, copie installée par cadrage-init).

## Pré-requis (vérification silencieuse)

Deux conditions doivent être réunies avant de finaliser un brief : la revue de
couplage a arbitré le découpage, **et** la boucle démonstrateur a convergé (maquette
validée par le client, aucun point bloquant). Un brief dérive d'une **vision
stable** ; tant que la boucle n'a pas convergé, la vision peut encore bouger.

Vérifier ces conditions **sans les annoncer** : ne jamais afficher de statut de
« porte » ni de nom d'attribut. Si quelque chose manque, le dire **en clair** et
orienter. Message cible :

> « Avant de rédiger les briefs, il reste à faire la revue de couplage et à valider
> le prototype — on s'en occupe d'abord ? »

**Garde-fou déterministe (anti-contournement, obligatoire).** Avant toute génération, lancer
`python "${CLAUDE_PLUGIN_ROOT}/scripts/check_ready.py" <projet>/.factory/manifest.json` : il échoue
(exit 1) si la revue de couplage ou la convergence du démonstrateur n'est pas faite. **Ne jamais
contourner** : en cas d'échec — ou si le script est **introuvable** (chemin plugin non résolu) —
**s'arrêter**, le dire en clair et orienter vers la revue de couplage (`/cadrage:cadrage-decoupage`)
puis la boucle démonstrateur (`/cadrage:cadrage-demonstrateur-brief`). **Jamais** de vérification « à
la main » à la place du script.

Adapter selon ce qui manque (en restant en clair) : si le prototype n'est pas
encore validé, renvoyer vers la boucle (clarification → retour-démonstrateur →
brief-démonstrateur) puis le point de complétude ; s'il manque la revue de
couplage, renvoyer vers cette revue. Ne **jamais** afficher de nom d'attribut ni de
statut de gate.

## Procédure

Pour **chaque feature** du spec index arbitré, produire
`cadrage-out/features-fonctionnels-brief/<feature>.brief.md` aux **10 sections du
contrat central** (`<feature>` = l'intitulé métier en clair, sans préfixe codé) :

1. **Narratif** — 2 à 4 phrases héritées de la vision. Problème résolu, valeur.
   Aucune techno.
2. **Utilisateurs concernés** — personas, repris de la vision.
3. **User stories** — En tant que <rôle>, je veux <action>, afin de <bénéfice>.
   Plusieurs par feature, chacune testable isolément.
4. **Critères d'acceptation** — par story, **au moins un** scénario Étant donné /
   quand / alors. Cas nominal + cas limites connus.
5. **Critères de succès mesurables** — outcomes en métriques avec cible chiffrée,
   agnostiques de la techno. Si la cible n'a pas été captée, l'écrire en clair
   « cible à préciser à l'architecture ».
6. **Périmètre** — IN et OUT (OUT explicite).
7. **Dépendances** — reprises du spec index, ordre induit.
8. **Contraintes héritées** — celles de la vision applicables.
9. **Glossaire pertinent** — extrait du glossaire global, termes mobilisés.
10. **Trous** — section conservée par contrat ; rien d'ouvert n'y est laissé (les
    points se tranchent en session). Vide quand le brief est complet.

**Formalisation à fournir :**
- *Succès* : traduire chaque outcome capté en métrique + cible (ou « à préciser à
  l'architecture »).
- *Acceptation* : pour chaque story, dériver au moins un scénario testable.

**Ne rien inventer.** Un élément absent de la matière se **tranche en session** (on
pose la question), il n'est pas marqué ni comblé. Aucun critère fabriqué. **Aucune
provenance écrite** (pas de `(src:)`).

## Vérification avant écriture

Pour chaque brief, vérifier :
- **Sections 1 à 9 présentes** (contrat central respecté).
- **Chaque story a au moins un critère d'acceptation.**
- **Critères de succès chiffrés ou marqués « cible à préciser à l'architecture ».**
- **Périmètre OUT non vide.**
- **Brief auto-suffisant** (auto-contrôle : lisible seul).
- **Fidélité à la matière** : chaque story / critère est soutenu par la matière
  (grounding interne) ; un point manquant se tranche en session. **Aucune `(src:)`
  ni provenance écrite.**
- **Auto-contrôle qualité INVEST / QUS** :
  - chaque story est **I**ndependent, **N**egotiable, **V**aluable, **E**stimable,
    **S**mall, **T**estable ;
  - chaque critère d'acceptation est **non ambigu** (bannir « rapide », « simple »,
    « convivial », « performant »…), **atomique** et **testable**.
- **Statut** : `complete` si aucun point bloquant ne reste ; sinon `draft`. Un brief
  `complete` **peut** porter des cibles « à préciser à l'architecture » **non-bloquantes**
  (déférées) : `complete` signifie « aucun point bloquant », pas « tout chiffré ».

## Mise à jour du manifeste

Read-modify-write puis revalidation JSON :
- `artifacts.briefs[]` : une entrée par feature (`id` = l'**identifiant de use case**
  `UC…` du spec-index — identité fonctionnelle stable et **clé de jointure** réutilisée par
  l'architecte (`feature_sequence`) et l'assembleur ; `name`, `path`, `status`).
- `definition_of_ready.all_briefs_complete = true` **si et seulement si** tous
  les briefs sont au statut `complete`.
- `phase = "briefs"`.
- `updated_at`.

## Règles invariantes appliquées ici

- **Pré-requis d'arbitrage.** Le skill ne finalise rien tant que la revue de
  couplage et la convergence du démonstrateur ne sont pas faites — vérifié en
  silence, jamais annoncé comme « porte ».
- **Ne pas inventer.** Un manque se tranche en session, jamais comblé ni marqué.
- **Contenu, pas provenance.** Aucune `(src:)`, aucun MVP.
- **Contrat central.** Les 10 sections, sans dérive de structure.
- **Skill indépendant.** Pré-requis et mise à jour via le manifeste.

Étape suivante : `/cadrage:cadrage-completude` — confronter les briefs à la Definition of Ready et faire le point.
