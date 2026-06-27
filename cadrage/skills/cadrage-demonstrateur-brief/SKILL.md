---
name: cadrage-demonstrateur-brief
description: Produit le prompt Claude Design de la maquette de validation (mode initial ou adaptatif).
---

# cadrage-demonstrateur-brief

Produit la **matière de travail** qui amorce ou fait évoluer le démonstrateur : un
prompt Claude Design. Le skill ne dessine rien ; il cadre ce que Claude Design
doit produire. Deux modes selon le moment de la boucle.

## Objectif

Donner un prompt prêt à coller dans Claude Design pour obtenir (mode initial) ou
faire évoluer (mode adaptatif) un démonstrateur qui sert à **valider la direction
produit avec le client**, pas à figer le design.

## Règle dure de calibrage

Le démonstrateur est **grossier et non contractuel sur le pixel**, pas un design
system. **Système tôt, écrans tard.** Le prompt demande de couvrir les parcours
clés et la logique, pas de fixer une charte, une grille fine ou des composants
définitifs. Un brief trop précis fige trop tôt et télescope l'étage Design en
aval. **Le démonstrateur est la semence, pas la loi.**

## Mode INITIAL (étape 3)

**Porte d'entrée.** La vision est disponible (`product_brief` existe ; idéalement
`vision_complete`). Le découpage fournit les parcours clés.

**Entrée.** `work/product-brief.md` et les parcours / activités utilisateur
du `work/spec-index.md`.

**Sortie.** Un prompt Claude Design pour un **démonstrateur de validation de
direction** : couvre les parcours clés (walking skeleton + features MVP),
matérialise le problème résolu et la valeur, reste volontairement grossier
(wireframe / basse fidélité), aucun engagement visuel. Le prompt rappelle la
direction de marque sobre (violet sobre) sans imposer de design fin.

## Mode ADAPTATIF (étape 8b)

**Porte d'entrée.** Un retour de démonstrateur a été ingéré
(`cadrage-retour-demonstrateur` a tourné ; `demonstrateur.iterations` contient
un retour récent) et la maquette courante est référencée
(`demonstrateur.external_ref`).

**Entrée.** L'état du démonstrateur courant (`demonstrateur.external_ref`,
`current_version`) et le transcript de retour, plus les `validation_points`
adressés.

**Sortie.** Un **prompt DELTA** : il référence explicitement la maquette existante
(« à partir de la maquette vX… »), décrit **uniquement les changements** demandés
par le client (écrans à corriger, parcours à ajuster, éléments à retirer), et
**préserve ce qui a été validé**. Pas de régénération à blanc — l'itération doit
rester rapide et ne pas casser l'acquis.

## Sauvegarde du prompt

Le prompt généré est **tracé** : l'écrire dans
`factory-prompts/<NNN>-<JJ-MM>-<nom>/prompt.md` où `NNN` est le prochain numéro
global (incrément du dernier `prompts[].n` du manifeste), `JJ-MM` la date du jour,
et `<nom>` le sujet (ex. `demonstrateur-initial`, `demonstrateur-delta-v2`). Ceci
garde l'historique exact de chaque version de maquette (auditabilité de la boucle).

## Porte de sortie (commune)

- Le prompt **cadre un démonstrateur grossier**, pas un design contractuel
  (auto-contrôle : ai-je évité de figer la charte / le pixel ?).
- Mode initial : les **parcours clés sont couverts**.
- Mode adaptatif : le prompt est un **delta** référençant la maquette existante,
  **borné aux changements** du retour, sans repartir de zéro.
- Le prompt est **sauvegardé** sous `factory-prompts/` et tracé au manifeste.

## Mise à jour du manifeste

Read-modify-write puis revalidation JSON :
- Ajoute une entrée `prompts[]` : `{ n, date, name, source: "demonstrateur-brief",
  path }` pointant le fichier sauvegardé.
- Ajoute / met à jour une entrée `demonstrateur.iterations[]` avec
  `brief_mode = "initial" | "adaptatif"`, `prompt_path` (le fichier sauvegardé)
  et, en adaptatif, `feedback_source` (réf du transcript de retour).
- **Ne touche pas** `demonstrateur.client_validated` (geste humain) ni
  `current_version` / `external_ref` (mis à jour par l'humain après génération de
  la maquette dans Claude Design).
- `updated_at`.

## Règles invariantes appliquées ici

- **Le plugin ne génère pas la maquette.** Il produit un prompt ; Claude Design
  produit la maquette.
- **Grossier et non contractuel.** Le détail visuel se fige plus tard, dans le
  plugin Design.
- **Proposer, ne pas décider.** Le prompt propose ; le client valide la maquette,
  hors plugin.
- **Skill indépendant.** Lit la vision / le retour et le manifeste, sans
  orchestrateur.

Étape suivante : `/cadrage:cadrage-retour-demonstrateur` — confronter la maquette au client puis ingérer son retour.
