# ci-watch

Mod Claude Code qui suit la CI **GitHub Actions** d'une pull request dans un panneau latéral, et résume en français les jobs en échec.

## Ce qu'il fait

- **Démarrage automatique** : dès que Claude crée une PR avec `gh pr create`, le panneau s'ouvre et suit ses checks.
- **Ticket lié** : affiche l’issue GitHub liée à la PR (« Closes #12 », lien via la section *Development*, ou issue qui mentionne la PR) ou à la branche (`12-titre`), avec son état, ses assignés, ses labels, un résumé et, si le token a le scope `read:project`, la carte et le statut dans le GitHub Project.
- **Suivi en direct** : checks groupés par workflow (✓ vert, ✗ rouge, … en cours, – ignoré), rafraîchis toutes les 12 s. La barre de statut affiche `CI #42 : 3/7`.
- **Fin de CI** : une notification donne le verdict (tout vert, ou nombre de jobs en échec). Le suivi s'arrête seul, ou au bout de 3 h.
- **Clic sur un job rouge** : lit ses logs d'échec (`gh run view --log-failed`) et en affiche un résumé de 3 à 5 puces (étape, erreur, fichier:ligne, cause probable, piste de correction), généré par Haiku, avec un lien vers les logs GitHub.
- **Bouton « Débuguer avec Claude »** : sous le résumé, envoie à Claude un prompt avec le contexte de l’échec (PR, job, résumé, commande pour lire les logs complets) pour qu’il trouve la cause dans le code et propose un correctif, sans commiter ni pousser.

## Commandes

| Commande | Effet |
| --- | --- |
| `/ci` | Suit la PR de la branche courante |
| `/ci 42` ou `/ci <url>` | Suit une PR précise |
| `/ci stop` | Arrête le suivi |

## Prérequis

- [GitHub CLI](https://cli.github.com/) installé et connecté (`gh auth status`), avec accès au dépôt suivi.
- Pour le statut GitHub Project du ticket : `gh auth refresh -s read:project`.
- Claude Code avec le support des mods (function hooks).

## Installation

Depuis la marketplace Shapsha-Factory, dans une session Claude Code lancée depuis un terminal :

```
/plugin marketplace add CGI-Shapsha-Factory/CGI-Factory-AI
/plugin install ci-watch@Shapsha-Factory
```

Choisis la portée utilisateur : le mod se charge alors dans toutes tes sessions, y compris dans l'onglet Code de l'app desktop.

## Développement

```
claude plugin validate .
claude plugin test .
claude --plugin-dir .
```

- `hooks/register.tsx` : interrogation de GitHub, panneau, résumés
- `hooks/ci.ts` : lecture de la sortie de `gh`, nettoyage des logs
- `types/index.d.ts` : contrat de l'état du mod
- `tests/` : tests (`claude plugin test`)
