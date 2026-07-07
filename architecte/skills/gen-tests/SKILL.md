---
name: gen-tests
description: Generate missing pytest/jest/vitest/go tests for source files that have none. Real assertions only — no stubs.
---

# gen-tests

Génère les tests manquants pour les fichiers source qui n'en ont pas encore. À utiliser dès
que le hook `tests_guard.py` bloque, ou de façon préventive avant un commit.

## Invocation

```
/architecte:gen-tests [chemin/vers/fichier.py]
```

- **Avec argument** : génère les tests pour ce seul fichier source.
- **Sans argument** : découvre tous les fichiers source du projet sans test associé et les traite
  tous (fan-out séquentiel, un fichier à la fois).

## Procédure

### Étape 1 — Découverte des fichiers sans test

**Avec argument :**
- Vérifier que le fichier est un fichier source géré (pas `__init__.py`, pas un fichier de config,
  pas déjà un fichier de test).
- Vérifier qu'il n'a pas déjà un test correspondant (nommage : `test_x.py` / `x_test.py` pour
  Python, `x.test.ts` / `x.spec.ts` pour TS, `x_test.go` pour Go, etc.).

**Sans argument :**
- Exécuter `python .claude/hooks/tests_guard.py check` sur les fichiers de l'index git
  (`git ls-files`) pour obtenir la liste des sources sans test.
- Si `.claude/hooks/tests_guard.py` est absent, dériver manuellement :
  lire `git ls-files`, filtrer les extensions source (`.py`, `.ts`, `.tsx`, `.js`, `.jsx`,
  `.go`, `.cs`, `.java`), exclure les noms `__init__.py`, `conftest.py`, `index.ts`,
  fichiers de config (`.config.js`, `.d.ts`), et tout fichier déjà dans `tests/` / `__tests__/`
  / nommé `test_*` / `*_test.*` / `*.test.*` / `*.spec.*`.

### Étape 2 — Lecture du contexte de test

Lire `architecte-out/standards.md` (si présent) pour connaître :
- Le **framework de test** du projet (pytest, jest, vitest, go testing, xUnit, JUnit…).
- Les conventions : dossier de tests, conventions de nommage, mocking, fixtures.

Si `standards.md` est absent, **inférer** :
- Python → `pytest` (toujours)
- TypeScript/JavaScript → chercher `jest` ou `vitest` dans `package.json` ; défaut `vitest`
- Go → `testing` natif
- C# → `xUnit`
- Java → `JUnit 5`

### Étape 3 — Layout miroir

Calculer le chemin du fichier de test **en miroir** du fichier source :

| Source | Test |
|--------|------|
| `src/foo/bar.py` | `tests/src/foo/test_bar.py` |
| `foo/bar.py` (à la racine) | `tests/foo/test_bar.py` |
| `src/api/user.ts` | `tests/src/api/user.test.ts` |
| `internal/pkg/service.go` | `internal/pkg/service_test.go` *(Go : même dossier)* |

Règles :
- Conserver l'intégralité du sous-dossier.
- Préfixer par `tests/` sauf pour Go (convention Go = même package, même dossier).
- Ne jamais écraser un fichier de test existant — si le fichier cible existe déjà, **passer au suivant**.

### Étape 4 — Génération du contenu

Lire le fichier source en entier, puis générer le fichier de test avec :

1. **Imports** corrects (importer le module/classe/fonction testé, les fixtures nécessaires).
2. Au moins **3 cas de test**, chacun avec un nom explicite :
   - **Golden path** : usage nominal, assertion sur la valeur de retour ou l'effet.
   - **Cas d'erreur** : entrée invalide, erreur attendue (`pytest.raises`, `expect().toThrow()`, etc.).
   - **Cas limite** : valeur vide, zéro, None/null, liste vide, chaîne très longue…
3. **Vraies assertions** — jamais de `pytest.skip`, `todo`, `pass` seul, ou `assert True`.
4. Commentaires uniquement si le WHY n'est pas évident (pas de description du WHAT).

**Exemples de structure par langage :**

*Python (pytest) :*
```python
from mon_module.foo import bar

def test_bar_nominal():
    assert bar(2) == 4

def test_bar_valeur_negative():
    with pytest.raises(ValueError):
        bar(-1)

def test_bar_zero():
    assert bar(0) == 0
```

*TypeScript (vitest) :*
```typescript
import { describe, it, expect } from 'vitest'
import { bar } from '../src/foo'

describe('bar', () => {
  it('retourne le double pour une entrée positive', () => {
    expect(bar(2)).toBe(4)
  })
  it('lève une erreur pour une entrée négative', () => {
    expect(() => bar(-1)).toThrow()
  })
  it('gère zéro', () => {
    expect(bar(0)).toBe(0)
  })
})
```

*Go :*
```go
package mypkg

import "testing"

func TestBar_Nominal(t *testing.T) {
    got := Bar(2)
    if got != 4 { t.Errorf("got %d, want 4", got) }
}

func TestBar_Negatif(t *testing.T) {
    _, err := BarWithErr(-1)
    if err == nil { t.Error("expected error for negative input") }
}
```

### Étape 5 — Écriture + récapitulatif

- Créer les dossiers intermédiaires si nécessaires.
- Écrire chaque fichier de test (ne jamais écraser un existant).
- **Si un import échoue** (module source cassé, nom de fonction introuvable) : corriger le
  fichier source d'abord, puis générer le test. Le hook se redéclenchera — c'est attendu.
- Afficher un récapitulatif :

```
Tests générés :
  ✓ tests/src/foo/test_bar.py       (3 cas)
  ✓ tests/src/api/test_user.py      (4 cas)
  ⚠ tests/src/utils/test_config.py  déjà présent — ignoré
```

## Règles invariantes

- **Jamais de stubs** (`pytest.skip`, `pass`, `assert True`, `todo`).
- **Jamais d'écrasement** d'un fichier de test existant.
- **Un fichier source = un fichier de test** (pas de regroupements multi-sources).
- **Lire le source en entier** avant de générer (pas de génération à l'aveugle).
- **Inférer le framework** si `standards.md` est absent — ne jamais demander.

## Étape suivante

Une fois les tests générés, relancer `python .claude/hooks/tests_guard.py check` pour confirmer
qu'aucune source ne reste sans test, puis committer avec `/starter:commit`.
