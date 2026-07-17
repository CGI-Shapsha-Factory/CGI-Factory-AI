# MEMORY.md : index mémoire projet

<!-- Livré directement dans `.claude/memory/MEMORY.md` du projet. Index concis (≤ 200 lignes) : des
     POINTEURS cliquables (liens Markdown `[titre](chemin) - accroche`), jamais de contenu dupliqué.
     Ne LIER EN DUR que les voisins de `memory/` (nom nu, ex. `domain.md` - jamais `memory/domain.md`) :
     ce sont les seuls fichiers qui voyagent avec l'index. Les fichiers du paquet `assembleur-out/`
     (contexte technique, carte des features, pré-constitution) sont cités EN TEXTE SIMPLE, jamais en
     lien `../` (ils ne voyagent pas avec `.claude/`). Contenu seul. -->

## Le projet en une phrase
[Ce que fait le produit.]

## Contrats (3 faces) : où regarder
- **Fonctionnel** : les graines de feature (`assembleur-out/features/`) - User Scenarios + FR ; langage = [domaine](domain.md).
- **Technique** : `assembleur-out/technical-context.md` + [architecture](architecture.md) (stack, composants, ADR, conventions).
- **Design** : [design](design.md) (design system synchronisé + états + erreurs + a11y).

## Constitution
`assembleur-out/pre-constitution.md` - principes non négociables (P1..Pn) + gouvernance (donnée à `/speckit.constitution`).

## Découpage
`assembleur-out/feature-map.md` - séquence, couplage/dépendances, walking skeleton.

## Fichiers thématiques : lus par Claude au besoin
- [Domaine](domain.md) - langage ubiquitaire & entités.
- [Architecture](architecture.md) - stack, composants, décisions (ADR), conventions, qualité.
- [Design](design.md) - design system, états, accessibilité.
- [Features](features.md) - séquence & 3 faces par feature.
