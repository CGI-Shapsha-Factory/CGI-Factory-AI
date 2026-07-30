---
name: couts-equipe
description: Consolide les répertoires de coûts reçus de plusieurs développeurs en un seul tableau, une ligne par développeur (prénom, projet, tokens, coût estimé et coût réel). À lancer sur le dossier où les répertoires reçus ont été déposés.
---

# couts-equipe

Produit **un tableau d'équipe** : chaque développeur envoie son répertoire de coûts, on les dépose
côte à côte, et ce skill les agrège en **une ligne par développeur**. C'est la voie de consolidation
**sans infrastructure** (pour du temps réel avec dashboards, voir `references/OTEL.md`).

## Dossier de collecte

**Un sous-dossier par développeur**, nommé librement :

```
couts-equipe/
  naif/     2026-07/*.jsonl  +  identite.json
  sarah/    2026-07/*.jsonl  +  identite.json
  rapport-equipe.md          <- produit par ce skill
```

Ce que le développeur envoie, c'est le contenu de son `.factory/couts/` (dossier caché, à la racine
du projet mesuré). La forme exacte est **tolérée** : contenu de `.factory/couts/`, `.factory/` entier
ou racine du projet, les trois fonctionnent.

Le **prénom** et le **nom de projet** viennent de son `identite.json`, posé par `couts-init`.

## Procédure

1. Lancer le collecteur sur le dossier de collecte :
   ```
   python "${CLAUDE_PLUGIN_ROOT}/references/cost_equipe.py" <dossier-de-collecte>
   ```
   (Adapter `python` -> `py -3` si besoin sur Windows.)

2. **Afficher le tableau en session**, tel que produit.

3. Donner **les deux chemins absolus** : `rapport-equipe.md` et le **PDF** produit à côté, même nom
   et même numéro (`rapport-equipe-2.md` / `rapport-equipe-2.pdf`). Les deux sont versionnés, jamais
   écrasés. Le PDF est le document présentable : synthèse chiffrée, répartition du coût par
   développeur, puis le tableau.

   **Le PDF est un bonus, jamais une condition.** Sans navigateur (Chrome, Chromium ou Edge), le
   Markdown est écrit quand même et le script affiche une ligne `_PDF : ..._`. Le dire simplement,
   proposer d'installer Chrome et de relancer ; ne jamais présenter ça comme un échec du rapport.

4. **Relayer en clair la section "À vérifier"** si elle est présente. Ne jamais la passer sous
   silence : un total d'équipe faux et silencieux est pire que pas de total. Les cas possibles :
   - **identité manquante** -> la ligne existe quand même, identifiée par l'email git ou le nom du
     dossier ; demander au développeur concerné de relancer `/couts:couts-init` ;
   - **enregistrements présents dans plusieurs dossiers** -> total probablement gonflé, il faut
     vérifier les dépôts (un même répertoire déposé deux fois, par exemple) ;
   - **sous-dossier sans journal** -> ignoré, à signaler pour que le développeur renvoie le bon
     dossier ;
   - **modèle hors table de prix** -> non tarifé, jamais compté à zéro en silence.

## Cas limites (aucun n'est bloquant)
- **Dossier de collecte absent** -> le dire en clair et s'arrêter.
- **Dossier vide / aucun journal exploitable** -> le rapport le dit et rappelle la structure attendue.
- **Aucun appel API externe** chez un développeur -> colonne Réel à `-`, jamais un zéro trompeur.

## Règles invariantes
- **Estimé et réel jamais additionnés.** Deux colonnes, deux natures : le coût estimé est une
  simulation au tarif API (pas un montant facturé), le coût réel est ce qui a été payé.
- **Une seule table de prix pour toute l'équipe** (celle du dossier de collecte, sinon celle du
  plugin) : tarifer chaque développeur avec sa propre table rendrait les lignes incomparables.
- **Rien n'est retarifé côté simulation** : le coût vient du compteur de chaque développeur.
- **Aucune dédup entre développeurs.** Un recouvrement est **signalé**, jamais fusionné en silence.
- **Interaction en français, sans mécanique exposée** (pas de chemins de scripts, pas de détail
  d'implémentation).

**Étape suivante : demander une relance de `/couts:couts-init` aux développeurs signalés sans
identité, puis relancer ce skill.**
