# Suivi des coûts au niveau organisation — OpenTelemetry (sans hook par machine)

Ce guide explique comment suivre les coûts **au niveau de l'organisation** avec la télémétrie **native** de
Claude Code (OpenTelemetry), en **alternative ou en complément** du journal **local** git-ignoré (`.factory/couts/`).
C'est **de la doc**, pas un composant du plugin : rien à installer côté projet, tout se configure côté
poste/org via des variables d'environnement (idéalement un `settings.json` géré par l'admin).

## Pourquoi OTel plutôt qu'un hook, pour l'org
- **Natif et hookless** : Claude Code instrumente déjà chaque requête et émet des **métriques** — aucun hook
  par machine à poser, aucune latence par tour.
- **Coût déjà chiffré** : la métrique `claude_code.cost.usage` est émise **en USD** par Claude Code (pas
  besoin de table de prix locale). C'est plus proche du **réel** côté API que la simulation du journal.
- **Rollup temps réel** : les métriques partent vers un collecteur OTLP (Honeycomb, Datadog, Grafana,
  Prometheus, collecteur auto-hébergé…) et alimentent des dashboards par **user / modèle / équipe**.

## Les 2 métriques de coût (vérifiées — `code.claude.com/docs/en/monitoring-usage`)
- **`claude_code.token.usage`** (tokens) — attributs : `type` (`input` | `output` | `cacheRead` |
  `cacheCreation`), `model`, `query_source` (`main`|`subagent`|`auxiliary`), `plugin.name`, `skill.name`,
  `agent.name`, `mcp_server.name`, `mcp_tool.name`, + attributs standard.
- **`claude_code.cost.usage`** (USD) — attributs : `model`, `query_source`, `plugin.name`, `skill.name`,
  `agent.name`, `marketplace.name`, + attributs standard.
- **Attributs standard** (toutes métriques) : `session.id`, `app.version`, `organization.id`,
  `user.account_uuid`, `user.email`, `terminal.type`, + `OTEL_RESOURCE_ATTRIBUTES` personnalisés.
- Autres métriques utiles : `claude_code.session.count`, `claude_code.active_time.total`,
  `claude_code.lines_of_code.count`, `claude_code.commit.count`, `claude_code.pull_request.count`.

## Activation (variables d'environnement)
```bash
export CLAUDE_CODE_ENABLE_TELEMETRY=1                 # requis
export OTEL_METRICS_EXPORTER=otlp                     # otlp | prometheus | console | none
export OTEL_LOGS_EXPORTER=otlp                        # otlp | console | none (mettre 'none' si métriques seules)
export OTEL_EXPORTER_OTLP_PROTOCOL=grpc               # grpc | http/json | http/protobuf
export OTEL_EXPORTER_OTLP_ENDPOINT=http://collector.example.com:4317
export OTEL_EXPORTER_OTLP_HEADERS="Authorization=Bearer <token>"
export OTEL_METRIC_EXPORT_INTERVAL=60000             # ms (défaut 60000)
```

## Déploiement org via `settings.json` géré (recommandé)
L'admin pousse ces variables pour tous les postes (fichier géré / MDM). Elles ont **priorité haute** et ne
peuvent pas être surchargées par l'utilisateur.
```json
{
  "env": {
    "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
    "OTEL_METRICS_EXPORTER": "otlp",
    "OTEL_LOGS_EXPORTER": "none",
    "OTEL_EXPORTER_OTLP_PROTOCOL": "grpc",
    "OTEL_EXPORTER_OTLP_ENDPOINT": "http://collector.example.com:4317",
    "OTEL_EXPORTER_OTLP_HEADERS": "Authorization=Bearer <token>",
    "OTEL_METRIC_EXPORT_INTERVAL": "60000",
    "OTEL_RESOURCE_ATTRIBUTES": "department=engineering,team.id=factory,cost_center=eng-123"
  }
}
```
`OTEL_RESOURCE_ATTRIBUTES` ajoute des étiquettes d'équipe/centre de coût sur **toutes** les métriques →
ventilation par équipe côté dashboard.

## Ce qu'OTel fait / ne fait pas (vs le journal `.factory/couts/`)
| Besoin | OTel natif | Journal local git-ignoré (`couts-init`/`couts-rapport`/`couts-total`) |
|---|---|---|
| Rollup org, dashboards temps réel | **oui** (par user/modèle/équipe, hookless) | non (par projet) |
| Coût en USD sans table de prix | **oui** (`cost.usage`) | calculé via table de prix datée |
| Attribution par **plugin/skill** | oui (`plugin.name`/`skill.name`) | oui (namespace skill) |
| Attribution par **feature** (branche `NNN-`) | non | **oui** |
| Split cache **5 min vs 1 h** | non (`cacheCreation` groupé) | **oui** (5m et 1h séparés) |
| Journal **local** (git-ignoré, individuel) | non (part vers un collecteur) | oui (`.factory/couts/`, non poussé) |

## Recommandation
- **Journal local git-ignoré** (défaut du plugin) : suivi **par session**, données individuelles
  (jamais poussées), fonctionne hors-ligne — **coût de simulation** (estimation au tarif API). Partage
  au chef d'équipe via `couts-total`. C'est le livrable « coût de fabrication d'un projet ».
- **OTel** (ce guide) : suivi **transversal org**, dashboards temps réel, coût USD natif — à activer par
  l'admin quand on veut agréger tous les développeurs/projets (les journaux locaux étant git-ignorés, OTel
  est la voie d'agrégation cross-dev).

Les deux sont **complémentaires** : OTel pour le pilotage org, le journal pour le chiffrage par projet/feature.

## Source
- `code.claude.com/docs/en/monitoring-usage` (métriques `claude_code.token.usage` / `claude_code.cost.usage`,
  attributs, variables d'environnement, `settings.json` géré) — vérifié le 2026-07-02.
