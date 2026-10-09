# CLAUDE.md : plugin `ci-watch`

This file provides guidance to Claude Code (claude.ai/code) when working **on the `ci-watch` plugin**
(this directory). Factory-wide overview: `../CLAUDE.md`.

## Ce qu'est le plugin
`ci-watch` = **outil du harnais de dev** (pas une phase, pas un contrat). C'est un **mod** Claude
Code : un module de *function hooks* TypeScript, pas des skills Markdown. Il suit la CI GitHub
Actions d'une PR dans un **panneau latéral** :
- démarre seul quand Claude lance `gh pr create`, ou via `/ci [n° | URL | stop]` ;
- interroge `gh pr checks` toutes les 12 s, affiche un verdict, une barre de progression et les jobs
  par workflow ; notifie à la fin ;
- au clic sur un job rouge, lit `gh run view --log-failed` et en fait résumer l'erreur par Haiku,
  en français ; le bouton « Débuguer avec Claude » envoie un prompt de débogage à la session ;
- affiche le **ticket lié** (issue que la PR ferme, lien *Development*, issue qui mentionne la PR,
  ou numéro en tête de branche) avec son statut dans le GitHub Project si le token a `read:project`.

## Exception typographique
La règle typographique de la Factory (pas de coche/croix, de points de suspension unicode, de
flèches unicode, de guillemets à chevrons...) **ne s'applique pas à ce plugin** : son interface
(panneau, statut, notifications) est un outil du harnais de dev, pas un livrable de la Factory. Les
glyphes `✓ ✗ ● … « » ↗ ▦` sont voulus. La règle continue de s'appliquer aux autres plugins.

## Fichiers
- `hooks/hooks.json` : déclare le module.
- `hooks/register.tsx` : hooks (session, commande `/ci`, détection de `gh pr create`, rendu du
  panneau) et appels à `gh` / au modèle. Les fonctions qui reçoivent `$` sont déclarées au niveau du
  module (exigence du validateur).
- `hooks/ci.ts` : fonctions pures (lecture de la sortie de `gh`, nettoyage des logs, requêtes
  GraphQL, choix du ticket, barre de progression, prompt de débogage).
- `types/index.d.ts` : contrat de l'état du mod (`$.state`), cité par `plugin.json`.
- `tests/` : tests `claude plugin test` (fonctions pures + parcours complet sur terminal et desktop).

## Vérifier un changement
```
claude plugin validate ci-watch
claude plugin test ci-watch
```
Pour le développer en direct : `claude --plugin-dir ci-watch` (rechargement à chaud à la
sauvegarde).

## Dépendances
CLI `gh` installée et connectée sur le poste ; aucun secret dans le plugin. Le résumé des erreurs et
des tickets passe par le client Claude de la session (`$.model.complete`, modèle `haiku`).
