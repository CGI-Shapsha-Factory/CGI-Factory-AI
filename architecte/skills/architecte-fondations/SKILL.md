---
name: architecte-fondations
description: Lit le cadrage puis pose les fondations du contrat technique - drivers, attributs de qualité et composants - en interactif.
---

# architecte-fondations

Première étape de la construction du contrat technique. **Discipline le raisonnement de
l'architecte et grave ses décisions en contrats.** L'IA propose et structure ; **l'humain
tranche**. Ne décide jamais l'architecture à la place de l'architecte. Ce skill **lit tout le
cadrage**, puis pose les **fondations** : drivers & attributs de qualité, puis composants.

## Pré-requis (vérification silencieuse)
`architecte-init` a tourné (le manifeste contient le bloc `architecture`). Vérifier
sans l'annoncer ; sinon, orienter en clair vers `/architecte:architecte-init`.

## Entrées (lues depuis le cadrage : relues des fichiers committés, jamais de la mémoire du chat)
`cadrage-out/` : `project-frame.md`, `product-brief.md`, `glossaire.md`,
`spec-index.md` (use cases + walking skeleton candidat + couverture), les briefs sous
`cadrage-out/features-fonctionnels-brief/*.md`. Conventions d'interaction :
`references/interactive-loop.md` et `references/ux-conventions.md`.

> **Règles transverses (toutes les étapes).** Restituer **en prose**, jamais en
> tableau. Désigner chaque chose par son **nom métier en clair** - jamais un code
> (`C1`, `UC1`, `P1`...). **Aucune provenance** écrite dans les artefacts (pas de
> `(src:)`, d'horodatage, de nom de personne). Mettre à jour le manifeste **en
> silence** : ne jamais narrer "MAJ `architecture.*`" ni un nom de variable, ni **aucune ligne de
> bilan** "Manifeste à jour : ..." / liste `champ: valeur` / `true`/`false` (l'utilisateur ne s'y
> intéresse pas). Toute
> valeur manquante se **résout en session** (cf. `references/interactive-loop.md`) et
> s'écrit **en place** - aucun marqueur n'est laissé dans un fichier final.
>
> **Versionnage des documents.** Chaque fichier écrit sous `architecte-out/` commence par un
> front-matter `--- version: N / date: AAAA-MM-JJ ---`. **Première** génération d'un document :
> `version: 1`. À chaque **régénération** : relire le `version:` existant et écrire **`N+1`**,
> avec `date:` = jour courant (format ISO `AAAA-MM-JJ`) - le helper
> `scripts/bump_doc_version.py <fichier>` calcule la prochaine version. **Exception ADR** : un ADR accepté est
> immuable - il **reste `version: 1`** et évolue via son champ `Statut` (+ un ADR successeur). Ce
> front-matter `version`/`date` est une **métadonnée de document** - il n'est **pas** visé par
> l'interdiction de provenance/horodatage (qui concerne le corps : pas de `(src:)`, pas
> d'horodatage épars, pas de nom de personne).

## Procédure : ordre imposé (chaque étape consomme la précédente)

### Étape 1 : Lire le cadrage en parallèle (exhaustif), puis vérifier
**Lire tout le cadrage pertinent, en parallèle, pour ne rien manquer.** Dispatcher des
sous-agents lecteurs (`agentType: "architecte-reader"`), **un par lot**, chacun avec un
**schéma de sortie structuré**, en **un seul message** (appels parallèles) - puis
synthétiser leurs retours. Lots :
1. **Vision & cadre** - `cadrage-out/product-brief.md`, `cadrage-out/project-frame.md`.
   Extraire : identité produit, périmètre IN/OUT, contraintes (légales/sécurité/données),
   seeds qualité (charge, disponibilité, performance), réponses de cadrage (Q1-Q13).
2. **Domaine & découpage** - `cadrage-out/glossaire.md`, `cadrage-out/spec-index.md`,
   `cadrage-out/coupling-map.md`. Extraire : entités/langage, use cases + frontières,
   walking skeleton candidat, couplages/dépendances.
3. **Briefs** - `cadrage-out/features-fonctionnels-brief/*.md`. Extraire, par feature :
   user stories, critères d'acceptation/succès, contraintes héritées.

*(Garde simple : s'il n'y a quasiment rien à lire, un seul lecteur suffit ; au-delà,
fan-out. Plafonné à la concurrence - au-delà, mettre en lot.)*

**Passe de complétude** : après synthèse, vérifier que rien n'a été manqué ni contredit
(au besoin, relire un lot). Le `references/question-map.md` sert ensuite à savoir **quelle
réponse vient déjà du cadrage** : ne **poser que les trous**, en clair et **un par un**
(cf. `references/interactive-loop.md`), **sans tableau** ni identifiant `Qn` :
- **profil d'équipe** (taille, expertise langage/framework) - absent du cadrage ;
- tout point de cadrage resté à confirmer et **bloquant**.
Si un trou bloquant n'est pas tranché, **ne pas démarrer la génération** : le dire en
clair et s'arrêter. Écrire le profil d'équipe au manifeste (en silence).

### Étape 2 : Drivers & attributs de qualité (deux temps liés)
À partir des seeds qualité (charge, disponibilité, performance) + les contraintes
(légal, sécurité, données) :
1. **Identifier les drivers** = ce qui **oriente** l'architecture : **objectifs métier**,
   **contraintes** (légales / organisationnelles / techniques / d'usage) et **risques
   majeurs**, classés par priorité. **Jamais une -ilité** ici.
2. **En dériver les attributs de qualité** = les **-ilités mesurables** (ISO 25010 :
   fiabilité, sécurité, performance, disponibilité, maintenabilité...) **issues** de ces
   drivers, chacune avec une **cible chiffrée** et **reliée au driver dont elle découle** ;
   puis formuler les **scénarios de qualité testables (QAW)**.
**Les deux ne se recouvrent pas** : un attribut de qualité qui répète un driver - ou une
-ilité listée comme driver - est une **erreur à corriger**. **Restituer dans le chat sous forme de DEUX
tableaux clairs** (noms en clair, jamais de code) :
- **Drivers** - colonnes **`#`** (priorité) · **`Driver`** · **`Conséquence pour l'architecture`**.
- **Attributs de qualité** - colonnes **`Attribut`** · **`Cible`** (chiffrée) · **`Scénario (QAW)`** · **`Driver source`**.

*(Exception assumée à la règle "pas de tableau" - cf. `references/ux-conventions.md` §4 : drivers et
attributs de qualité se lisent bien mieux en tableau.)* Faire valider, puis écrire
`architecte-out/facteurs-et-qualite.md` (gabarit `templates/facteurs-et-qualite.md`). Mettre à jour le manifeste
en silence.

### Étape 3 : Workflow composants (interactif)
Dériver une **liste de composants candidats** depuis le périmètre fonctionnel
(briefs + spec-index). **Dès que le produit a un écran utilisateur, la liste inclut
TOUJOURS un composant Frontend/UI** (l'application qui rend les écrans) - composant
technique à part entière, au même titre que le back, les workers, la base. L'existence
du plugin designer **ne dispense pas** de l'architecture front : le designer produit le
design system **visuel**, pas le **composant technique** front (porté ici + sa stack au
**workflow stack**, skill `architecte-stack`). **Restituer la liste sous forme de TABLEAU clair** - deux colonnes : **`Composant`**
(nom métier) et **`Rôle`** (ce qu'il fait, en une phrase) ; **jamais de texte brut en liste**,
**jamais de code `C1`/`C2`** ni d'identifiant technique. *(Exception assumée à la règle "pas de
tableau" - cf. `references/ux-conventions.md` §4 : les composants se lisent bien mieux en tableau.)*
**Demander si ça convient ou s'il faut modifier** ; appliquer les retours (ajout/fusion/suppression) ;
**boucler jusqu'à validation**. Puis écrire `architecte-out/composants.md` (gabarit
`templates/composants.md`). Mettre à jour le manifeste en silence.

## Règles invariantes
- **Proposer, ne pas décider - jamais à la place de l'utilisateur.** Drivers, attributs de
  qualité et composants sont **présentés** puis **validés par l'humain** ; on n'avance pas sans
  sa validation.
- **Rien d'affiché de la mécanique.** Aucun nom de variable/clé manifeste, aucun identifiant
  codé ; le manifeste se met à jour en silence. Restituer en **prose** - **sauf** drivers,
  attributs de qualité et composants, restitués en **tableaux clairs** (cf.
  `references/ux-conventions.md` §4).
- **Skill indépendant.** Lit/écrit le manifeste partagé ; relit toujours le cadrage depuis les
  fichiers committés.

À la fin, dire en clair **ce qui a été produit** (en prose, sans tableau, sans ligne
de manifeste) puis l'étape suivante.

Étape suivante : `/architecte:architecte-stack` - choisir la stack, activer les conventions, arbitrer les ADR et figer le walking skeleton.
