# Spécification fonctionnelle - Le fichier cowork.md

Document de cadrage pour la génération du fichier `cowork.md`, le fichier de consignes qui transforme un Cowork générique en membre du projet. Objectif : que tu comprennes le besoin et la logique, puis que tu construises la génération de ce fichier par l'assembleur. Le document décrit ce que le fichier doit contenir et ce que Cowork doit savoir faire, pas comment le coder.

---

## 1. Contexte et objectif

Quand un développeur ou le pilote lance Cowork sur son poste pour accompagner un projet, Cowork ne connaît rien du projet par défaut. Le `cowork.md` est le fichier qui lui donne cette connaissance : qui il est sur ce projet, où lire la vérité, ce qu'il a le droit de faire, et comment se comporter.

Trois choses à comprendre avant tout.

**Cowork n'est pas un cinquième plugin.** Les quatre plugins (cadrage, architecte, designer, assembleur) construisent les contrats en amont et s'arrêtent quand le projet est amorcé. Cowork, lui, intervient pendant la fabrication, à côté du développeur et du pilote. Le livrable de cette spécification n'est donc pas un plugin avec des phases, c'est **un seul fichier de consignes, généré par l'assembleur**, au même titre que la constitution et le CLAUDE.md.

**Cowork est proposé, jamais imposé.** Le pipeline reste valide sans lui. Un développeur qui ne l'utilise pas suit exactement le même chemin et produit les mêmes artefacts. Cowork est un accélérateur que l'on peut retirer, pas un maillon dont la chaîne dépend. Cette règle doit rester vraie dans toute la conception.

**Cowork est un assistant par instance, pas un cerveau central partagé.** Quand le pilote lance son Cowork et qu'un développeur lance le sien, ce sont deux instances séparées, chacune sur sa machine, qui chargent le même `cowork.md`. Ce qu'on unifie, c'est la configuration (le fichier), pas l'assistant. Il n'existe pas un Cowork central du projet auquel tout le monde se connecte.

**Le fichier est vivant, il évolue avec le projet.** Le `cowork.md` n'est pas figé une fois pour toutes au démarrage. Au fil du projet, on va repérer des actions qui reviennent souvent et qu'on voudra structurer en nouveaux skills, et on va ajouter ou changer des outils. Chaque fois, le `cowork.md` doit être mis à jour pour que Cowork connaisse ces nouvelles capacités et sache quand les déclencher. Conséquence pour la conception : Naeif doit traiter ce fichier comme un document qui se révise, pas comme une consigne définitive. C'est pour ça que l'en-tête de version existe, et c'est pour ça que les capacités d'action doivent être décrites de façon à pouvoir s'allonger proprement quand un nouveau skill arrive. La règle « une action régulière se structure en skill, puis se déclare dans le cowork.md » est le bon réflexe à graver.

---

## 2. Ce que Cowork doit savoir faire

Cowork est un assistant de projet qui **voit large**. Sur ce premier projet, à quatre personnes dans une équipe soudée, tout le monde peut tout voir à travers lui, et c'est même un avantage. Il sait répondre à chacun selon sa question :

- À un **développeur**, sur le code : il connaît la codebase et peut l'expliquer.
- À un **pilote**, sur l'avancement : il lit l'état des sujets et le restitue, pour que celui qui demande n'ait pas à aller lui-même dans l'outil de suivi. Il vient en complément de Linear, pas à sa place : Linear reste la source de vérité du suivi, Cowork la lit et la met en perspective (recouper l'avancement avec le code réel, les coûts, les risques en cours), pour donner au pilote une lecture d'ensemble qu'un simple tableau de bord ne donne pas.
- À un **PO**, sur le fonctionnel : il connaît la base fonctionnelle (briefs, glossaire, spécifications) et répond aux questions métier.

C'est un besoin de **savoir**, pas de **pouvoir**. Cowork connaît largement et répond. Il n'a pas besoin des outils d'action des différents profils pour ça, il a besoin de la visibilité sur leurs domaines.

À cette visibilité, on ajoute **la lecture des coûts du projet** (voir section 5, point sur les coûts), pour que Cowork puisse répondre à « combien la fabrication a-t-elle coûté jusqu'ici ».

---

## 3. Le principe d'action : Cowork n'agit qu'à travers des skills cadrés

C'est la règle la plus importante du fichier, et elle remplace l'idée de « lecture seule » qui n'est plus exacte.

Cowork **lit tout**, mais il **n'écrit jamais directement**, ni dans le code, ni dans Linear. Quand Cowork doit produire un effet (créer une anomalie, créer une évolution), il le fait **uniquement en appelant un skill cadré de la factory**, et **toujours après validation humaine**. Il ne fait jamais de modification triviale ou hors cadre de son propre chef.

La différence est essentielle. Un skill cadré porte ses propres règles, son format, ses portes de validation. En passant par lui, Cowork hérite de cette discipline. S'il écrivait en direct, il deviendrait un acteur incontrôlé sur le poste de chacun, et on perdrait toute la sécurité du dispositif.

À retenir, c'est la phrase à graver : **Cowork peut déclencher un skill cadré sous validation humaine, mais il ne modifie jamais rien directement et ne fait jamais de geste hors cadre.**

---

## 4. Les deux usages d'action prévus

Au-delà de répondre aux questions, Cowork a deux usages où il agit, tous deux conformes au principe ci-dessus.

**Côté PO, accompagner la recette.** Cowork peut aider le PO à tester, détecter un écart, et **proposer la création d'une anomalie ou d'une évolution en appelant le skill de création dédié**. Deux garde-fous obligatoires. D'une part, c'est le skill qui écrit dans Linear, pas Cowork, donc le format et la rigueur sont garantis. D'autre part, **rien n'est créé sans la validation du PO, et cette validation se fait anomalie par anomalie, jamais en lot**. Si Cowork propose dix écarts après une passe de recette, le PO regarde chacun. C'est le prix pour que l'automatisation de la recette ne dégrade pas la qualité du suivi.

**Côté développeur, aider à la relecture avant la PR.** Cowork peut comparer le code d'une branche à la spécification de la feature et signaler au développeur les écarts, pour qu'il les corrige avant de soumettre. Point important de cohérence : **avant la PR, il n'y a pas d'anomalie**, par définition, parce qu'on est encore en fabrication. Cowork **aide donc à voir**, il ne crée rien à ce stade. Il conseille, le développeur corrige dans sa fabrication normale, et rien ne se trace. La frontière de la PR reste la ligne qui décide si un objet existe ou pas, et Cowork la respecte des deux côtés.

---

## 5. Le gabarit du fichier cowork.md

Le fichier contient six blocs. Pour chacun, on distingue ce qui est **fixe** (vrai pour tout projet, l'assembleur l'écrit tel quel) de ce que l'assembleur **injecte** par projet (les chemins, le nom du projet).

**1. En-tête de version.** Un numéro et une date. C'est ce qui rend visible une désynchronisation, le jour où le fichier évolue et que des Cowork déjà initialisés tournent sur une version périmée. Forme fixe, valeur injectée.

**2. Identité et rôle.** Qui est Cowork sur ce projet : un assistant de projet qui connaît le contexte et aide à l'analyse, au cadrage de feature et au suivi. C'est ce qui le distingue d'un assistant générique. Forme fixe, nom du projet injecté.

**3. Où lire la vérité, et l'ordre de lecture en début de session.** Les pointeurs vers les sources vivantes, à lire au démarrage avant toute analyse :
- la constitution (chemin injecté),
- le CLAUDE.md du projet (chemin injecté),
- la codebase, pour les questions techniques,
- la base fonctionnelle, briefs, glossaire, spécifications (chemins injectés),
- Linear, pour l'état d'avancement,
- la source des coûts du projet (voir le point dédié plus bas).

Principe gravé ici : **des pointeurs, pas un instantané.** On ne recopie jamais dans ce fichier une information qui vit ailleurs (les membres, l'état des features, les règles). On pointe vers la source vivante, qui fait foi. Sinon le fichier ment dès que l'équipe ou les features changent.

**4. Le principe d'action.** Le texte de la section 3 : Cowork lit tout, n'écrit jamais en direct, agit uniquement via des skills cadrés sous validation humaine, ne fait aucune modification hors cadre. Bloc entièrement fixe.

**5. Les capacités et le contrat de sortie.** Ce que Cowork sait faire (répondre aux questions de chaque profil, accompagner la recette via les skills, aider à la relecture avant PR) et la nature de sa sortie. Point clé sur la sortie : **Cowork ne dépose aucun artefact persistant dans le pipeline.** Il analyse et fabrique ses prompts en conversation, il aide à préparer l'entrée des commandes, mais il ne crée pas de fichier qui entrerait dans le flux de fabrication. C'est ce qui garantit que le développeur sans Cowork suit exactement le même rail. Quand Cowork doit produire un effet, il passe par un skill, comme dit au bloc 4. Bloc fixe.

**6. La discipline partagée.** Un rappel court que Cowork suit les mêmes principes que le reste de la factory : marquer ce qui manque plutôt que l'inventer, signaler ce qu'il ne sait pas, ne pas réimplémenter les règles qui vivent déjà ailleurs. Pour qu'il ait le même tempérament que les plugins. Bloc fixe.

**Le point sur les coûts.** Cowork doit pouvoir lire et restituer les coûts du projet, c'est à dire la consommation de tokens et donc le coût de fabrication, pour répondre à « combien ça a coûté jusqu'ici ». À ce stade, on ne construit pas le système de mesure lui-même : il fera l'objet d'une spécification séparée. Mais le `cowork.md` doit déjà prévoir, dans le bloc 3, **un pointeur vers la source des coûts (à définir)**, pour que cette source puisse s'y brancher plus tard sans reprendre la structure du fichier. Autrement dit, on laisse la place maintenant, on remplira le pointeur quand le système de coûts existera.

---

## 6. Consignes de construction pour l'assembleur

**Génération dans la même passe.** L'assembleur génère le `cowork.md` en même temps que la constitution et le CLAUDE.md, comme un artefact de plus, avec un drapeau au manifeste pour tracer qu'il a été produit.

**Fichier versionné.** Le numéro et la date de l'en-tête rendent les désynchronisations visibles. Au démarrage de session, Cowork peut signaler sur quelle version de consignes il tourne.

**Récupération manuelle au démarrage.** Pour ce premier projet, chaque membre récupère le fichier et le met dans les consignes de son Cowork au moment d'initialiser le projet. C'est une étape d'onboarding, assumée telle quelle, pas encore automatisée. L'automatisation de cette récupération viendra plus tard si la fréquence le justifie.

**Règle anti-doublon, le fil rouge.** Le `cowork.md` ne redit jamais ce que portent la constitution et le CLAUDE.md. Il pointe vers eux et n'ajoute que ce qui lui est propre : le comportement et la posture de Cowork. Si on hésite à mettre une information dans le CLAUDE.md ou dans le cowork.md, la question tranche : est-ce que ça concerne l'écriture du code (CLAUDE.md) ou l'analyse, le cadrage et le suivi (cowork.md) ?

---

## 7. Ce qui n'est pas dans cette spécification

**Le système de mesure des coûts.** Cette spécification prévoit que Cowork lise les coûts et réserve un pointeur pour ça, mais la construction du système qui mesure et stocke ces coûts fait l'objet d'une spécification séparée, à venir.

**L'automatisation de la récupération du fichier.** Pour le v0, la récupération est manuelle. Un mécanisme central d'où Cowork tirerait ses consignes viendra plus tard si le besoin se confirme.

**La mécanique interne des skills appelés par Cowork.** Les skills de création d'anomalie et d'évolution sont décrits dans leur propre spécification. Ici, on dit seulement que Cowork peut les appeler, sous validation humaine.

---

## 8. Récapitulatif

Le `cowork.md` est un fichier mince, généré par l'assembleur, qui fait d'un Cowork générique un membre du projet. Cowork voit large (code, fonctionnel, avancement, coûts) et répond à chacun selon sa question. Il n'agit jamais en direct : il lit tout, et quand il doit produire un effet, il appelle un skill cadré sous validation humaine, jamais une modification triviale ou hors cadre.

Deux usages d'action sont prévus : accompagner le PO en recette pour proposer la création d'anomalies ou d'évolutions via les skills, validées une par une, et aider le développeur à relire avant la PR sans rien créer, parce qu'avant la PR il n'y a pas d'objet à tracer.

Le fichier est versionné, généré dans la même passe que la constitution et le CLAUDE.md, et il ne redit jamais ce qu'ils portent : il pointe vers les sources vivantes et n'ajoute que la posture de Cowork. La lecture des coûts est prévue dès maintenant par un pointeur, pour que le futur système de mesure s'y branche sans reprise.
