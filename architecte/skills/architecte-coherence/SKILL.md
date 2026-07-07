---
name: architecte-coherence
description: Valide la cohérence du contrat technique et prépare le passage à l'assembleur.
---

# architecte-coherence

Dernière étape de la phase technique : la **porte de validation de cohérence** (def :
« la porte humaine est l'arbitrage des ADR, puis la validation de cohérence »).
Vérifie que le contrat technique tient ensemble, sans contradiction ni trou, avant
de passer le relais à l'assembleur.

## Pré-requis (vérification silencieuse)
Le contrat technique a été produit (le bloc `architecture` est rempli). Vérifier sans
l'annoncer ; sinon, orienter en clair vers `/architecte:architecte-contrat`.

## Entrées
Les artefacts d'architecture dans `architecte-out/` : `drivers-quality.md`,
`components.md`, `tech-stack.md`, `standards.md`, `decisions/ADR-*.md`,
`diagrams.md`, `risks.md`, `design-impact.md` ; le dossier `conventions/` ; les
briefs sous `cadrage-out/features-fonctionnels-brief/*.md` ; le manifeste.

## Contrôles de cohérence — stricts et adversariaux
Ne **pas** se contenter de vérifier la présence. **Challenger** chaque contrat : ce
qui manque, ce qui se contredit, ce qui pourrait casser. Au minimum :

1. **Aucun marqueur résiduel & front-matter valide** : aucun `[À VALIDER]` / `[À CHIFFRER]`
   / `[À DÉFINIR]` ne subsiste dans un fichier `architecte-out/` ; **chaque fichier porte son
   front-matter `version:` (entier) / `date:` (ISO `AAAA-MM-JJ`)**. Chaque manque est un point
   à **résoudre en session** (voir ci-dessous).
2. **Composants ↔ stack (deux sens, cohérence des technos)** : chaque composant a une techno
   **définie** dans la matrice (pas « à définir ») ; aucune ligne de matrice sans composant ;
   aucun orphelin d'aucun côté. **La stack inline d'un composant (`components.md` → Technologies)
   doit CORRESPONDRE à `tech-stack.md`** — mêmes technos, mêmes **versions exactes**. **Échec**
   si un composant décrit une stack que `tech-stack.md` ne retient pas (ex. un composant en .NET
   alors que la stack retient Python), une version divergente, ou une version « latest »/vague.
   **Un composant Frontend/UI existe** si le produit a des écrans.
3. **Drivers vs attributs de qualité — distincts, non redondants, dérivés** :
   - un **driver** (objectif métier / contrainte / risque) est **concret** et **adressé** par un
     composant, un ADR et/ou un attribut de qualité — pas forcément chiffré ;
   - un **attribut de qualité** (-ilité) a une **cible mesurable** + un **scénario QAW** observable
     et chiffré, **et** est adressé par un composant et/ou un ADR ;
   - **aucune redondance** : un driver et un attribut de qualité ne désignent jamais le **même
     concept** (ex. un driver « Maintenabilité » alors qu'un attribut « Maintenabilité » existe =
     doublon à fusionner) ; **chaque attribut de qualité découle d'un driver** (sinon : driver
     manquant à ajouter, ou -ilité injustifiée à retirer).
4. **Contradictions inter-artefacts** : confronter drivers ⨉ stack ⨉ ADR ⨉ déploiement.
   Ex. : un driver « hébergement UE / pas de fuite » contredit-il un service externe
   choisi ? la cible de disponibilité/performance est-elle réellement tenue par le
   déploiement décrit ? un ADR contredit-il un autre ?
5. **Couverture inverse** : chaque contrainte des briefs et chaque entité du glossaire
   est-elle adressée par ≥1 composant ou ADR ? une entité de l'ERD sans composant qui
   la gère = orpheline. un besoin de sécurité/droits/audit est-il reflété par un
   composant **et** un ADR (journal d'audit présent si exigé) ?
6. **Use cases ↔ features** : chaque use case du `spec-index.md` a une feature dans la
   séquence ; aucune feature ne référence un use case inexistant.
7. **Walking skeleton** : traverse-t-il réellement le **couplage le plus risqué** (pas
   juste la première feature) ?
8. **Diagrammes ↔ réel** : noms réels partout, aucun placeholder ; les composants des
   diagrammes existent dans `components.md` ; les images PNG sont présentes dans
   `architecte-out/diagrammes/`.
9. **Conventions ↔ stack** : chaque langage retenu a son fichier de conventions.
10. **Cohérence de nommage** : un même concept est nommé pareil partout (alignement
    glossaire) — pas deux noms pour la même chose, pas deux choses sous le même nom.
11. **Risques** : chaque risque porte impact + mitigation + déclencheur ; les spikes
    bloquants sont identifiés avant la première feature.
12. **Design-impact** : produit et couvrant la tranche qui se voit (stack front + style,
    contrats transverses visibles, conventions d'API → états d'UI, NFR qui touchent l'UX).
13. **Passe « ce qui manque / ce qui peut casser »** : une lecture critique finale, pas
    une checklist de présence.

Garde-fou déterministe (**obligatoire, jamais sauté**) : lancer
`python "${CLAUDE_PLUGIN_ROOT}/scripts/check_architecture.py" <racine>/.factory/manifest.json` — il
échoue notamment s'il **reste un marqueur** dans un fichier `architecte-out/`, si un
composant n'a pas de techno, si un langage retenu n'a pas son fichier de conventions,
**si une techno de `tech-stack.md` n'a pas de version exacte (ou dit « latest »)**, ou
**si un fichier `architecte-out/` n'a pas de front-matter `version`/`date` valide**. Si le
script est **introuvable** (chemin plugin non résolu) ou renvoie **exit 1**, **s'arrêter** et
**rapporter en clair** ce qui manque — **ne jamais** basculer en vérification « à la main ».

## Résolution interactive des points (obligatoire avant d'avancer)
Tout point relevé — **bloquant ou non** — n'est **pas seulement affiché** : on **pose
la question** à l'utilisateur, **un par un** (réponse recommandée adaptée au projet +
alternative + saisir, cf. `references/interactive-loop.md`), et on **corrige en place**
dans le fichier `architecte-out/` concerné. **Aucun fichier annexe.** **Ne pas passer**
à `/designer:designer-init` tant qu'il reste un point ou un marqueur non résolu.

## Sortie
- Un **rapport de cohérence** `architecte-out/coherence-report.md` : ce qui a été
  vérifié et ce qui a été corrigé, en clair — **sans marqueur résiduel**.
- En chat : un **court bilan en prose** (pas de tableau, pas de nom de variable, pas
  d'identifiant codé), puis la confirmation que tout est résolu.
- **Décision humaine** : l'architecte **valide** la cohérence (geste humain). Le skill
  ne valide jamais de lui-même ; il le propose, l'humain confirme.

## Mise à jour du manifeste (en silence)
Une fois la validation humaine actée, mettre à jour le manifeste **sans le narrer**
(jamais « je passe `coherence_validated = true` et `phase = "valide"` »).

## Handoff (vers l'assembleur)
Une fois validé, le contrat technique prêt à transmettre comprend : les ADR et
contrats transverses, les normes (`standards.md` + `conventions/`), les diagrammes,
le walking skeleton et la **séquence de features numérotée** (convergence des deux
découpages), le registre de risques, et les **Décisions à impact design**
(`design-impact.md`, consommées par le designer). (L'assembleur coud ensuite ces
contrats par feature, une fois le contrat de design figé.)

## Règles invariantes
- **Challenger, pas cocher.** Cohérence stricte et adversariale ; on cherche ce qui
  manque et ce qui se contredit, pas la simple présence.
- **Rien laissé indéfini.** Chaque point se résout en session, en place, avant
  d'avancer. Aucun marqueur ne survit.
- **L'humain valide.** La cohérence n'est jamais auto-validée par l'IA.
- **Rien de la mécanique affiché.** Aucun nom de variable/clé manifeste, aucun
  identifiant codé, aucun tableau (voir `references/ux-conventions.md`). Manifeste
  mis à jour en silence ; à l'utilisateur, seulement le bilan en clair et la suite.

**Handoff (avant de passer la main).** Committer `.factory/manifest.json` (avec la cohérence **scellée**)
**et** `architecte-out/` — la phase suivante lit le **repo committé**, pas ta session ni ta machine. Un
manifeste non re-committé après la validation ferait échouer `designer-init` (flag à `false`) sur un autre poste.

Étape suivante : `/designer:designer-init` — démarrer le contrat de design (la phase design exige le cadrage ET l'architecture validés). Ou corriger d'abord les points signalés via `/architecte:architecte-contrat`.
