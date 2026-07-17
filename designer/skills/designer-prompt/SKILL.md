---
name: designer-prompt
description: Génère le prompt Claude Design (direction visuelle concrète, anti-slop) et le rapport de couverture, une fois la couverture jugée suffisante.
---

# designer-prompt

Génération des **sorties de l'atelier** : le **prompt Claude Design** (corps prêt à coller) et le **rapport
de couverture**. Elle n'a lieu **que** lorsque plus rien n'est "à traiter" et que la **couverture est
jugée suffisante**. **Le design system naît dans Claude Design** (pas ici) ; ce skill produit le prompt qui
le fait naître, puis la trace de la rigueur de l'atelier.

## Objectif
Matérialiser les deux sorties de l'atelier - le **prompt Claude Design** et le **rapport de couverture** -
et basculer `design.phase = "atelier"`.

## Entrées
- La **checklist finalisée** (`design.checklist`, tous items statués : `deduced` / `decided` / `sans_objet`).
- `cadrage-out/product-brief.md`, `cadrage-out/spec-index.md`, `cadrage-out/glossaire.md`,
  `architecte-out/impact-design.md` - pour remplir les `<...>` du gabarit (domaine, stack, parcours).
- Gabarits : `templates/claude-design-prompt.md`, `templates/coverage-report.md` (installés dans
  `.factory/designer/`).
- Convention : `references/ux-conventions.md` §3bis (fichier prompt = corps seul).

## Pré-requis (vérification silencieuse)
La **couverture est jugée suffisante** (`design.coverage_sufficient = true`) et plus aucun item n'est "à
traiter". Sinon, orienter en clair (sans nom de champ) : "le prompt ne se génère que lorsque la couverture
est jugée suffisante - termine d'abord l'atelier via `/designer:designer-atelier`".

## Porte de régénération (relance)
Avant toute (re)génération, appliquer `references/regeneration-gate.md`. Si les sorties **de ce
skill** existent déjà, proposer le choix **Repartir de zéro** (supprimer puis générer à neuf,
`version: 1`) ou **Garder les deux (versionner)** (archiver l'existant sous `_archives/`, régénérer
au nom canonique en `version: N+1`) et **attendre** le choix. Les prompts sous `prompts/` sont des
**fichiers plats numérotés** (`<NNN>-<JJ-MM>-...md`) : un nouveau prompt prend le **numéro suivant**
sans jamais écraser les précédents (déjà non destructif) - la porte ne vise donc que les livrables au
nom canonique. Premier passage (rien n'existe) : générer directement, sans porte.

## Procédure : générer les sorties
- **Prompt Claude Design** -> `designer-out/prompts/<NNN>-<JJ-MM>-claude-design.md` (fichier plat ; gabarit
  `templates/claude-design-prompt.md`) : fondation à produire, direction stylistique (maquette =
  inspiration, marque si présente sinon direction à poser), **stack cible**, et **consignes de discipline**
  (tous les états par composant, tous les parcours, erreurs + états vides, marquer ce qui manque). Les items
  **sans objet** sont omis. **Aucun `[À VALIDER]` n'est émis** : tous les points ayant été résolus en
  session à l'atelier, le prompt ne contient que des décisions actées.
  - **Rôle + viser haut (prompt engineering).** Ouvrir le prompt par le **rôle** du gabarit en
    **remplissant `<domaine>`** depuis le `product-brief.md`/`impact-design.md`, puis reprendre **tel
    quel** le bloc "Avant de concevoir" (décider la langue visuelle + **un parti pris signature** +
    décider-puis-appliquer + north-star "viser l'excellence, pas la moyenne"). Rôle **court** (1 ligne) -
    il signale les priorités mieux qu'une liste.
  - **Direction visuelle délibérée et CONCRÈTE (anti-slop).** Remplir la section "Direction visuelle"
    du gabarit avec des **valeurs NOMMÉES, jamais des placeholders** : palette en **hexadécimal + rôle**
    (`--couleur-primaire: #... (CTA)`, `--fond: #...` légèrement teinté, `--texte: #...`, + succès/erreur/
    alerte), **polices nommées** (titrage + corps), **unité d'espacement + rayons par composant** -
    **déduits du domaine, du public et du ton** (ou de la **marque** du client si elle existe).
    **Jamais** le violet/indigo par défaut ni les polices par défaut (Inter, Roboto, Poppins, Space
    Grotesk, Geist...). Principe : **"tout choix non spécifié retombe sur un défaut générique"** - ne
    rien laisser au hasard. Exemples de raisonnement : cabinet d'avocats -> encre/bleu nuit + neutres
    chauds + serif éditoriale (ex. Fraunces) ; santé -> teal apaisant + sans-serif humaniste ; finance ->
    anthracite + un accent mesuré. Reprendre **tel quel** le bloc "À éviter absolument" **et la phrase
    de verrou** du gabarit.
  > **Le fichier sauvegardé ne contient que le corps du prompt prêt à coller** (le bloc de code rempli du
  > gabarit) : **pas de titre H1, pas de note en blockquote, pas de métadonnée, pas de pied de page**. La
  > métadonnée (sujet, date, version) vit dans l'entrée `prompts[]` du manifeste, **jamais** dans le
  > fichier. Voir `references/ux-conventions.md` §3bis.
- **Rapport de couverture** -> `designer-out/coverage-report.md` (gabarit `.factory/designer/coverage-report.md`).

## Sortie
- Les **deux fichiers produits** (mêmes chemins) : le prompt Claude Design (corps seul) et le rapport de
  couverture.
- **Traçabilité** : chaque énoncé porte sa source `(src: cadrage | architecte | maquette | atelier)` **dans
  l'artefact** (jamais dans le prompt sauvegardé). **Rien d'inventé.**
- En chat : dire **ce qui a été produit** + **la suite** ; pas de tableau, pas de nom de champ.

## Mise à jour du manifeste
Read-modify-write + revalidation JSON, **en silence** (ne pas narrer la mise à jour du manifeste ; dire à
l'utilisateur **ce qui a été produit** et **la suite**) :
- `design.prompt_path`, `design.coverage_report_path`, `design.phase = "atelier"`.
- Métadonnée du prompt (sujet, date, version) dans l'entrée `prompts[]` du manifeste (jamais dans le
  fichier ; voir `references/ux-conventions.md` §3bis).

## Règles invariantes appliquées ici
- **Aucun `[À VALIDER]` émis** : tous les points ayant été résolus en session à l'atelier, le prompt ne
  contient que des décisions actées.
- **Corps seul prêt à coller** (plein texte, aucun Markdown) : pas de titre H1, pas de blockquote, pas de
  métadonnée, pas de pied de page ; la métadonnée vit dans `prompts[]`.
- **Direction visuelle concrète (anti-slop)** : valeurs nommées, jamais de placeholder ni de défaut
  générique.
- **Le plugin ne génère pas le design system** (il naît dans Claude Design ; son export est committé dans
  `designer-out/maquette-de-claude-design/`).
- **Pas de fuite de champ** ni de jargon en sortie utilisateur ; **manifeste mis à jour en silence** (voir
  `references/ux-conventions.md`).

Étape suivante : lance **Claude Design** avec le prompt produit, **dépose l'export dans
`designer-out/maquette-de-claude-design/`** (dossier ou ZIP), puis `/designer:designer-coherence` -
valider le système généré et préparer le handoff.
