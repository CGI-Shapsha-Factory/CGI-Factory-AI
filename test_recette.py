#!/usr/bin/env python
"""Smoke tests extensifs du plugin `recette` (harnais autonome, chemins relatifs).

Deux volets :
  A. STRUCTURE   - JSON valides, frontmatter des skills, references presentes, cablage des portes.
  B. GARDE-FOU   - check_recette.py sur des manifestes synthetiques couvrant TOUS les cas d'usage
                   (creation -> correction -> requalification -> evolution) + toutes les branches
                   d'echec (trace de cloture incomplete, lien feature casse, pas d'identifiant, etc.).

Exit 0 si tout passe, 1 sinon.
Usage: python test_recette.py   (depuis Factory-AI/)
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE / "recette"
GUARD = ROOT / "scripts" / "check_recette.py"
MARKETPLACE = HERE / ".claude-plugin" / "marketplace.json"
SKILLS = ["anomalie-creer", "anomalie-corriger", "evolution-creer", "evolution-realiser"]
DEV_SKILLS = ["anomalie-corriger", "evolution-realiser"]

results = []  # (name, ok, detail)


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))


# --------------------------------------------------------------------------- A. STRUCTURE
def test_structure():
    pj = ROOT / ".claude-plugin" / "plugin.json"
    try:
        d = json.loads(pj.read_text(encoding="utf-8"))
        check("plugin.json valide + name=recette", d.get("name") == "recette" and bool(d.get("version")),
              f"name={d.get('name')} version={d.get('version')}")
        check("plugin.json description non vide", len(d.get("description", "")) > 100)
    except Exception as e:
        check("plugin.json valide + name=recette", False, repr(e))

    try:
        mk = json.loads(MARKETPLACE.read_text(encoding="utf-8"))
        entry = next((p for p in mk.get("plugins", []) if p.get("name") == "recette"), None)
        check("marketplace: entree recette presente", entry is not None)
        check("marketplace: recette path=recette + git-subdir",
              bool(entry) and entry["source"]["path"] == "recette"
              and entry["source"]["source"] == "git-subdir")
    except Exception as e:
        check("marketplace: entree recette presente", False, repr(e))

    check("CLAUDE.md present", (ROOT / "CLAUDE.md").is_file())

    for sk in SKILLS:
        p = ROOT / "skills" / sk / "SKILL.md"
        if not p.is_file():
            check(f"skill {sk}: SKILL.md present", False)
            continue
        text = p.read_text(encoding="utf-8")
        lines = text.splitlines()
        fm_ok = lines and lines[0].strip() == "---"
        name_line = next((l for l in lines[:6] if l.startswith("name:")), "")
        desc_line = next((l for l in lines[:8] if l.startswith("description:")), "")
        name_val = name_line.split(":", 1)[1].strip() if name_line else ""
        check(f"skill {sk}: frontmatter name==dir", fm_ok and name_val == sk, f"name={name_val!r}")
        check(f"skill {sk}: description presente", bool(desc_line) and len(desc_line) > 30)
        check(f"skill {sk}: ligne 'Etape suivante'", "Étape suivante" in text)
        check(f"skill {sk}: cite recette-linear-guide", "recette-linear-guide.md" in text)

    for sk in DEV_SKILLS:
        text = (ROOT / "skills" / sk / "SKILL.md").read_text(encoding="utf-8")
        check(f"skill {sk}: appelle check_recette.py via CLAUDE_PLUGIN_ROOT",
              "${CLAUDE_PLUGIN_ROOT}/scripts/check_recette.py" in text)
        check(f"skill {sk}: mention fail-loud (s'arreter / exit 1)",
              "exit 1" in text and "s'arrêter" in text)

    for ref in ["interactive-loop.md", "ux-conventions.md", "recette-linear-guide.md"]:
        check(f"reference {ref} presente", (ROOT / "references" / ref).is_file())
    guide = (ROOT / "references" / "recette-linear-guide.md").read_text(encoding="utf-8")
    for tok in ["mcp__plugin_linear-prism_linear__list_teams", "save_issue", "save_comment",
                "list_issue_statuses", "feature:<id>", "anomaly", "evolution",
                "Requalifiée en évolution", "canceled"]:
        check(f"guide Linear mentionne {tok}", tok in guide)

    check("check_recette.py present", GUARD.is_file())


# --------------------------------------------------------------------------- B. GARDE-FOU
def base_manifest():
    return {
        "project": "smoke",
        "architecture": {"feature_sequence": [
            {"id": "001", "ucs": ["UC1"], "name": "Auth"},
            {"id": "002", "ucs": ["UC2"], "name": "Panier"},
        ]},
        "recette": {"phase": "active", "team": "T", "project": None,
                    "anomalies": [], "evolutions": []},
    }


def anomaly(state="in_progress", trace=None, feature="002", ident="ENG-321", title="A"):
    o = {"feature": feature, "title": title, "url": "u", "state": state}
    if ident is not None:
        o["identifier"] = ident
    if trace is not None:
        o["trace"] = trace
    return o


def evolution(state="in_progress", trace=None, feature="002", ident="ENG-322", title="E"):
    o = {"feature": feature, "title": title, "url": "u", "state": state,
         "perimeter": {"requirements": ["FR-004"], "files": ["specs/002-x/spec.md"]}}
    if ident is not None:
        o["identifier"] = ident
    if trace is not None:
        o["trace"] = trace
    return o


A_DONE = {"spec_verified": True, "tasks_updated": True, "linear_synced": True}
E_DONE = {"spec_updated": True, "plan_regenerated": True, "tasks_regenerated": True,
          "linear_synced": True, "non_regression_passed": True}

TMP = Path(tempfile.mkdtemp(prefix="recette_smoke_"))


def run_guard(manifest, *, raw=None, bom=False, cwd=None, use_default=False):
    mpath = TMP / (f"m{run_guard.n}.json")
    run_guard.n += 1
    if raw is not None:
        mpath.write_text(raw, encoding="utf-8")
    else:
        enc = "utf-8-sig" if bom else "utf-8"
        mpath.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding=enc)
    if use_default:
        fac = TMP / f"proj{run_guard.n}" / ".factory"
        fac.mkdir(parents=True, exist_ok=True)
        (fac / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
        argv = [sys.executable, str(GUARD)]
        cwd = fac.parent
    else:
        argv = [sys.executable, str(GUARD), str(mpath)]
    r = subprocess.run(argv, capture_output=True, text=True, cwd=cwd)
    return r.returncode, r.stdout, r.stderr


run_guard.n = 0


def expect(name, manifest, want_rc, want_marker=None, **kw):
    rc, out, err = run_guard(manifest, **kw)
    ok = rc == want_rc
    blob = (out + err)
    if ok and want_marker:
        ok = want_marker.lower() in blob.lower()
    check(name, ok, f"rc={rc} (attendu {want_rc}) marker={want_marker!r} :: {blob.strip()[:160]}")


def test_guard():
    m = base_manifest(); m["recette"]["anomalies"] = [anomaly()]
    expect("UC-A1 PO cree anomalie (in_progress)", m, 0, "RECETTE OK")

    m = base_manifest(); m["recette"]["anomalies"] = [anomaly(state="done", trace=A_DONE)]
    expect("UC-A2 dev corrige anomalie (done+trace)", m, 0, "RECETTE OK")

    m = base_manifest()
    m["recette"]["anomalies"] = [anomaly(state="requalified", trace={"linear_synced": True})]
    expect("UC-A3 anomalie requalifiee (linear_synced)", m, 0, "RECETTE OK")

    m = base_manifest(); m["recette"]["evolutions"] = [evolution()]
    expect("UC-E1 PO cree evolution (in_progress)", m, 0, "RECETTE OK")

    m = base_manifest(); m["recette"]["evolutions"] = [evolution(state="done", trace=E_DONE)]
    expect("UC-E2 dev realise evolution (done+5 traces)", m, 0, "RECETTE OK")

    m = base_manifest()
    m["recette"]["anomalies"] = [anomaly(), anomaly(state="done", trace=A_DONE, ident="ENG-9", title="A2")]
    m["recette"]["evolutions"] = [evolution(state="done", trace=E_DONE)]
    expect("UC-MIX anomalies+evolutions melangees", m, 0, "RECETTE OK")

    m = base_manifest()
    expect("UC-EMPTY recette vide", m, 0, "RECETTE OK")

    m = base_manifest(); m["recette"]["anomalies"] = [anomaly(state="draft", ident=None)]
    expect("UC-DRAFT brouillon sans identifiant", m, 0, "RECETTE OK")

    m = base_manifest(); m["recette"]["anomalies"] = [anomaly()]
    expect("UC-BOM manifeste avec BOM", m, 0, "RECETTE OK", bom=True)

    m = base_manifest(); m["recette"]["anomalies"] = [anomaly()]
    expect("UC-DEFAULTARG argument par defaut .factory/manifest.json", m, 0, "RECETTE OK",
           use_default=True)

    m = base_manifest()
    bad = A_DONE.copy(); bad["tasks_updated"] = False
    m["recette"]["anomalies"] = [anomaly(state="done", trace=bad)]
    expect("UC-A2-FAIL cloture anomalie sans tache a jour", m, 1, "tasks_updated")

    m = base_manifest()
    m["recette"]["anomalies"] = [anomaly(state="done")]
    expect("UC-A2-FAIL2 anomalie done sans trace", m, 1, "sans trace")

    m = base_manifest()
    m["recette"]["anomalies"] = [anomaly(state="requalified", trace={"linear_synced": False})]
    expect("UC-A3-FAIL requalifiee sans Linear synchronise", m, 1, "linear_synced")

    m = base_manifest()
    bad = E_DONE.copy(); bad["non_regression_passed"] = False
    m["recette"]["evolutions"] = [evolution(state="done", trace=bad)]
    expect("UC-E2-FAIL evolution done sans non-regression", m, 1, "non_regression_passed")

    m = base_manifest()
    m["recette"]["evolutions"] = [evolution(state="done", trace=E_DONE, feature="999")]
    expect("UC-IMPACT-FAIL feature inconnue (lien casse)", m, 1, "inconnue")

    m = base_manifest()
    m["recette"]["anomalies"] = [anomaly(ident=None)]
    expect("UC-NOID-FAIL objet cree sans identifiant Linear", m, 1, "sans identifiant")

    m = base_manifest()
    a = anomaly(); a.pop("feature")
    m["recette"]["anomalies"] = [a]
    expect("UC-NOFEATURE-FAIL objet sans feature", m, 1, "aucune feature")

    m = base_manifest(); del m["recette"]
    expect("UC-NOBLOCK-FAIL bloc recette absent", m, 1, "recette` absent")

    rc, out, err = run_guard(None, raw="{ pas du json")
    check("UC-BADJSON-FAIL JSON invalide", rc == 1 and "invalide" in (out + err).lower(),
          f"rc={rc} :: {(out+err).strip()[:120]}")
    r = subprocess.run([sys.executable, str(GUARD), str(TMP / "nexiste_pas.json")],
                       capture_output=True, text=True)
    check("UC-NOFILE-FAIL manifeste introuvable",
          r.returncode == 1 and "introuvable" in (r.stdout + r.stderr).lower(),
          f"rc={r.returncode}")


def main():
    test_structure()
    test_guard()
    passed = sum(1 for _, ok, _ in results if ok)
    failed = [(n, d) for n, ok, d in results if not ok]
    print("=" * 78)
    for n, ok, d in results:
        mark = "PASS" if ok else "FAIL"
        line = f"[{mark}] {n}"
        if not ok and d:
            line += f"\n         -> {d}"
        print(line)
    print("=" * 78)
    print(f"TOTAL: {passed}/{len(results)} PASS, {len(failed)} FAIL")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
