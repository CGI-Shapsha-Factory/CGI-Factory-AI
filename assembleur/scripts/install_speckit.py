#!/usr/bin/env python
"""Installeur deterministe de GitHub Spec Kit (`specify`) dans le repo cible.

Objectif : poser SpecKit COMPLETEMENT et SANS MANIP, et surtout **sans rien qui bloque**.
Le script est le bras arme du skill `install-speckit` (plugin assembleur) : il verifie si le
projet a deja SpecKit, sinon il l'installe bout en bout dans UN seul processus :

  1. diagnostic par CAPACITE (.specify/ + commandes /speckit.* + CLI) : complet -> ne touche a rien ;
     PARTIEL (cas du clone ou seul .specify/ est commite, ou init interrompu) -> REPARE ;
  2. `uv` garanti (auto-installe en espace utilisateur, SANS admin, PATH rafraichi en cours de
     processus) ; `uv` gere lui-meme Python 3.11+, donc la version de Python systeme n'est PAS
     un pre-requis bloquant ;
  3. Git verifie (pre-requis dur : la source est git+https et `specify init` fait `git init`) ;
  4. CLI `specify` acquis (persistant via `uv tool install`, repli ephemere `uvx`) ;
  5. flags de `specify init` construits par INTROSPECTION de `--help` (version-proof :
     absorbe le renommage `--ai` -> `--integration` et les versions qui omettent `--script`) ;
  6. `specify init` joue en non-interactif (timeouts, messages reseau/quotas clairs) ;
  7. test de fumee (.specify/ + commandes /speckit.*) ;
  8. registre de hooks `.specify/extensions.yml` pose depuis le gabarit Factory
     `references/speckit-extensions.yml` (config d'equipe, NON generee par specify init ; idempotent) ;
  9. hook PostToolUse de sync tasks.md -> Linear pose dans `.claude/` (via
     `references/linear-sync/install_tasks_linear_hook.py` ; best-effort, fusion idempotente) ;
 10. numerotation figee en SEQUENTIEL (`.specify/init-options.json feature_numbering:sequential` +
     `--branch-numbering sequential` si le CLI l'expose) et garde-fou d'alignement anti-collision de
     numero pose dans `.claude/` (via `references/speckit-sync/install_align_hook.py` : copie
     `check_speckit_alignment.py` + fusion PostToolUse ; best-effort) — pour que le NNN de SpecKit reste
     l'`id` du registre canonique et que deux developpeurs ne collisionnent jamais un numero ;
 11. bloc `speckit` ecrit dans manifest.json a la racine (repli cadrage-out/ legacy ; lecture-modif-ecriture + revalidation JSON).

Il n'ecrit JAMAIS a la main un fichier que SpecKit GENERE : c'est `specify init` qui cree `.specify/`
et les commandes. Les seules ecritures propres a la Factory sont le bloc de manifeste, le registre de
hooks `.specify/extensions.yml`, et le hook `.claude/hooks/tasks_linear_hook.py` (config/enforcement
d'equipe branchant les automations Factory sur le cycle).

Usage :
    python install_speckit.py [racine-projet] [options]

Options :
    --cli-only        installe/persiste le CLI mais NE joue PAS `specify init`
    --ephemeral       force le repli `uvx` (pas d'installation persistante du CLI)
    --ref <tag>       epingle une version de spec-kit (ex. v0.12.3) ; defaut : ref deja enregistree
                      au manifeste par la 1re installation de l'equipe, sinon main/latest
    --upgrade         ignore la ref epinglee au manifeste et reprend main/latest (bump volontaire)
    --integration <a> agent cible (defaut : claude)
    --allow-pypi      repli garde : tente PyPI si l'acquisition git echoue (non garanti)
    --no-manifest     n'ecrit pas le bloc `speckit` du manifeste
    --verbose         detail complet + traceback en cas d'echec (sinon message court)
"""
import argparse
import glob
import json
import os
import shutil
import subprocess
import sys

# --- Constantes ---------------------------------------------------------------
SPEC_GIT = "git+https://github.com/github/spec-kit.git"  # source par defaut (append @<ref>)
PKG = "specify-cli"
DEFAULT_INTEGRATION = "claude"
UV_INSTALL_PS = "irm https://astral.sh/uv/install.ps1 | iex"
UV_INSTALL_SH = "curl -LsSf https://astral.sh/uv/install.sh | sh"
IS_WIN = os.name == "nt"
SCRIPT_FLAVOR = "ps" if IS_WIN else "sh"

# Timeouts (s) : bornent chaque sous-processus pour qu'un telechargement pendu ne bloque jamais.
T_QUICK, T_UV, T_TOOL, T_INIT, T_CHECK = 60, 180, 420, 420, 90

MARKER = "SPECKIT_RESULT"  # ligne machine finale (JSON) ; le skill relaie en prose, pas ca.


# --- Sous-processus borne -----------------------------------------------------
def run(cmd, timeout, shell=False, env=None, cwd=None):
    # why: ne jamais laisser un telechargement pendu bloquer ; capturer la sortie pour messages nets.
    # encoding/errors forces: les CLI (specify/Rich, uv) emettent de l'UTF-8 (box-drawing, emoji) ;
    # sans ca, `text=True` decode avec la locale Windows (cp1252) -> UnicodeDecodeError dans le
    # thread lecteur -> pipe bloque -> deadlock jusqu'au timeout. `errors="replace"` ne casse jamais.
    try:
        p = subprocess.run(
            cmd, shell=shell, env=env, cwd=cwd,
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout,
        )
        return p.returncode, p.stdout or "", p.stderr or ""
    except subprocess.TimeoutExpired:
        return 124, "", f"timeout apres {timeout}s"
    except (FileNotFoundError, OSError) as exc:
        return 127, "", str(exc)


# --- PATH : rafraichir en cours de processus ----------------------------------
def user_bin_dirs():
    home = os.path.expanduser("~")
    up = os.environ.get("USERPROFILE", home)
    if IS_WIN:
        return [os.path.join(up, ".local", "bin"), os.path.join(home, ".local", "bin")]
    return [os.path.join(home, ".local", "bin"), os.path.join(home, ".cargo", "bin")]


def refresh_path():
    # why: uv s'installe dans ~/.local/bin (%USERPROFILE%\.local\bin) ; le rendre utilisable dans
    # CE processus sans redemarrer le shell (shutil.which lit os.environ["PATH"]).
    cur = os.environ.get("PATH", "")
    parts = cur.split(os.pathsep)
    for d in user_bin_dirs():
        if os.path.isdir(d) and d not in parts:
            os.environ["PATH"] = d + os.pathsep + cur
            cur = os.environ["PATH"]
            parts = cur.split(os.pathsep)


# --- Detection cible + idempotence --------------------------------------------
def detect_target(argv_target):
    # why: une cible passee EXPLICITEMENT est un ordre : on ne remonte pas les ancetres (sinon, dans un
    # repo imbrique, l'install part dans le projet parent au lieu du dossier demande).
    if argv_target:
        return os.path.realpath(os.path.abspath(argv_target))
    # defaut = CWD ; si un ancetre contient .factory/, prefere cette racine de projet.
    # why: on ne remonte JAMAIS jusqu'au dossier home (ni au-dessus) -- sinon un `~/.factory`
    # parasite ferait installer SpecKit dans le home au lieu du projet. Repli sur `start`.
    # why: realpath canonicalise (resout les noms courts 8.3 Windows, ex. NAIF~1.ASS -> naif.asswiel)
    # pour que la comparaison au home tienne malgre la forme courte renvoyee par %TEMP%.
    start = os.path.realpath(os.path.abspath(argv_target or os.getcwd()))
    home = os.path.realpath(os.path.abspath(os.path.expanduser("~")))
    cur = start
    while True:
        if os.path.normcase(cur) == os.path.normcase(home):
            return start
        if os.path.isdir(os.path.join(cur, ".factory")):
            return cur
        parent = os.path.dirname(cur)
        if parent == cur:
            return start
        cur = parent


def diagnose(target):
    """Etat REEL de SpecKit dans le repo, par CAPACITE (pas par presence de dossier).

    why: `.specify/` est commite ; un nouveau membre qui clone l'a donc deja, alors qu'il n'a NI le CLI
    `specify` NI les commandes `/speckit.*` (`.claude/` est souvent git-ignore). Se fier au seul dossier
    faisait dire « rien a faire » a quelqu'un qui ne pouvait rien lancer. Meme piege apres un
    `specify init` interrompu.

    Renvoie (etat, has_cli) avec etat dans {'absent', 'partiel', 'complet'}.
    """
    has_dir = os.path.isdir(os.path.join(target, ".specify"))
    has_cmds = bool(speckit_commands(target))
    refresh_path()
    has_cli = bool(shutil.which("specify"))
    if has_dir and has_cmds:
        return "complet", has_cli
    if has_dir or has_cmds:
        return "partiel", has_cli
    return "absent", has_cli


# --- Pre-requis ---------------------------------------------------------------
def ensure_uv(verbose):
    if shutil.which("uv"):
        return True
    refresh_path()
    if shutil.which("uv"):
        return True
    # installation espace utilisateur, sans admin ; TLS jamais desactive (on respecte la CA systeme).
    if IS_WIN:
        rc, out, err = run(
            ["powershell", "-ExecutionPolicy", "ByPass", "-NoProfile", "-c", UV_INSTALL_PS], T_UV
        )
    else:
        rc, out, err = run(UV_INSTALL_SH, T_UV, shell=True)
    refresh_path()
    if shutil.which("uv"):
        return True
    print(
        "ERREUR: uv est requis et son installation automatique a echoue (reseau ? proxy ?). "
        "Installe uv puis relance : https://docs.astral.sh/uv/getting-started/installation/",
        file=sys.stderr,
    )
    if verbose:
        print((err or out).strip(), file=sys.stderr)
    return False


def ensure_git():
    if shutil.which("git"):
        return True
    print(
        "ERREUR: Git est requis (la source d'installation est git+https, et `specify init` "
        "initialise un depot). Installe Git puis relance : https://git-scm.com/downloads",
        file=sys.stderr,
    )
    return False


# --- Acquisition du CLI -------------------------------------------------------
def spec_source(ref):
    return SPEC_GIT + (f"@{ref}" if ref else "")


def acquire_cli(ref, ephemeral, allow_pypi, verbose):
    """Retourne le prefixe d'invocation du CLI (tuple), ou None si echec total."""
    src = spec_source(ref)
    if not ephemeral:
        rc, out, err = run(["uv", "tool", "install", PKG, "--from", src], T_TOOL)
        refresh_path()
        if rc == 0 and shutil.which("specify"):
            return ("specify",)
        if verbose and (out or err):
            print((err or out).strip(), file=sys.stderr)
        # repli garde PyPI (non garanti) : sans @git, uv resout specify-cli depuis l'index.
        if allow_pypi:
            rc, out, err = run(["uv", "tool", "install", PKG], T_TOOL)
            refresh_path()
            if rc == 0 and shutil.which("specify"):
                return ("specify",)
    # repli ephemere : uvx (pas besoin de shim sur le PATH).
    return ("uvx", "--from", src, "specify")


# --- Introspection des flags (version-proof) ----------------------------------
def init_help(cli_prefix):
    rc, out, err = run(list(cli_prefix) + ["init", "--help"], T_QUICK)
    return out + "\n" + err  # l'aide sort parfois sur stderr selon la version


def build_init_argv(cli_prefix, target, dir_nonempty, integration, help_text):
    argv = list(cli_prefix) + ["init"]
    has = lambda flag: flag in help_text  # noqa: E731 - Typer/Click impriment chaque option litteralement
    # cible : on lance le sous-processus avec cwd=target, donc --here initialise au bon endroit.
    if has("--here"):
        argv += ["--here"]
    else:
        argv += ["."]
    if has("--integration"):
        argv += ["--integration", integration]
    elif has("--ai"):  # ancien flag (retire des versions recentes)
        argv += ["--ai", integration]
    if has("--script"):
        argv += ["--script", SCRIPT_FLAVOR]
    # why: figer la numerotation en SEQUENTIEL des l'init (jamais timestamp) — le NNN 3 chiffres doit
    # rester l'`id` du registre canonique ; turn_cost.py:27 et le hook Linear lisent `^\d{3}-`.
    if has("--branch-numbering"):
        argv += ["--branch-numbering", "sequential"]
    if dir_nonempty and has("--force"):
        argv += ["--force"]
    if has("--ignore-agent-tools"):
        argv += ["--ignore-agent-tools"]
    return argv


# --- Lancer specify init ------------------------------------------------------
def run_init(argv, target, verbose):
    env = dict(os.environ)  # passe GH_TOKEN/GITHUB_TOKEN -> quota GitHub releve
    rc, out, err = run(argv, T_INIT, env=env, cwd=target)
    if rc == 0:
        return True
    blob = (out + err).lower()
    if any(s in blob for s in ("rate limit", "429", "temporarily")):
        print(
            "ERREUR: GitHub a limite le debit pendant `specify init`. Reessaie plus tard, ou "
            "definis GITHUB_TOKEN/GH_TOKEN pour relever la limite, puis relance.",
            file=sys.stderr,
        )
    elif any(s in blob for s in ("network", "resolve", "timed out", "timeout", "ssl", "certificate", "proxy", "connection")):
        print(
            "ERREUR: echec reseau pendant `specify init` (hors ligne / proxy / TLS ?). "
            "Verifie la connexion, puis relance.",
            file=sys.stderr,
        )
    else:
        print("ERREUR: `specify init` a echoue. Relance avec --verbose pour le detail.", file=sys.stderr)
    if verbose:
        print((err or out).strip(), file=sys.stderr)
    return False


# --- Test de fumee ------------------------------------------------------------
def speckit_commands(target):
    # l'integration Claude de SpecKit peut etre a base de commandes OU de skills selon la version.
    found = glob.glob(os.path.join(target, ".claude", "commands", "speckit*.md"))
    found += glob.glob(os.path.join(target, ".claude", "commands", "*speckit*"))
    found += glob.glob(os.path.join(target, ".claude", "skills", "*speckit*"))
    found += glob.glob(os.path.join(target, ".claude", "skills", "**", "*speckit*"), recursive=True)
    return sorted(set(found))


def smoke(target):
    ok_dir = os.path.isdir(os.path.join(target, ".specify"))
    cmds = speckit_commands(target)
    if shutil.which("specify"):
        run(["specify", "check"], T_CHECK)  # informational ; son echec ne nous fait pas echouer
    return ok_dir and len(cmds) > 0


# --- Manifeste (silencieux) ---------------------------------------------------
def manifest_path(target):
    """Chemin du manifeste committe (repli legacy cadrage-out/), ou None hors workspace Factory."""
    mpath = os.path.join(target, "manifest.json")
    if os.path.isfile(mpath):
        return mpath
    legacy = os.path.join(target, "cadrage-out", "manifest.json")
    return legacy if os.path.isfile(legacy) else None


def read_speckit_block(target):
    """Bloc `speckit` deja ecrit par une installation precedente (ou {} si rien/illisible)."""
    mpath = manifest_path(target)
    if not mpath:
        return {}
    try:
        with open(mpath, encoding="utf-8-sig") as f:
            return (json.load(f) or {}).get("speckit") or {}
    except (OSError, ValueError):
        return {}


def resolve_head_sha():
    """SHA de `main` chez l'upstream, pour epingler EXACTEMENT ce qui vient d'etre installe.

    why: `main` est une cible mouvante — sans SHA, le membre suivant recoit une autre version. Un tag
    devine depuis `specify --version` (ex. `0.13.3.dev0`) designerait une version differente : seul le
    SHA est exact. Best-effort : None si git/reseau ne repondent pas (on n'epingle alors rien).
    """
    rc, out, _ = run(["git", "ls-remote", "https://github.com/github/spec-kit.git", "HEAD"], T_QUICK)
    if rc != 0 or not out.strip():
        return None
    sha = out.split()[0].strip()
    return sha if len(sha) == 40 and all(c in "0123456789abcdef" for c in sha) else None


def cli_version(cli_prefix):
    """Version reellement installee (informative, enregistree au manifeste). None si indisponible."""
    rc, out, err = run(list(cli_prefix) + ["--version"], T_QUICK)
    if rc != 0:
        return None
    line = (out or err).strip().splitlines()
    return line[0].strip() if line else None


def write_manifest(target, block, no_manifest):
    if no_manifest:
        return
    mpath = manifest_path(target)
    if not mpath:  # pas un workspace Factory -> on saute
        return
    try:
        # utf-8-sig: tolere un BOM (manifeste touche par un outil Windows/PowerShell) sans casser.
        with open(mpath, encoding="utf-8-sig") as f:
            data = json.load(f) or {}
    except ValueError:
        print("AVERTISSEMENT: manifeste JSON invalide -- bloc speckit non ecrit (pas d'ecrasement).", file=sys.stderr)
        return
    data["speckit"] = block
    tmp = json.dumps(data, ensure_ascii=False, indent=2)
    json.loads(tmp)  # why: revalider avant d'ecrire pour ne jamais laisser un manifeste corrompu
    with open(mpath, "w", encoding="utf-8") as f:
        f.write(tmp + "\n")


def write_extensions(target):
    """Pose le registre de hooks SpecKit (.specify/extensions.yml) — config d'equipe, NON generee par
    `specify init` (sans elle les /speckit.* rapportent "No hooks"). Copie le gabarit Factory
    `references/speckit-extensions.yml`. Idempotent (ne touche pas un fichier existant) et best-effort
    (ne bloque jamais l'installation). Renvoie 'created' / 'present' / None."""
    spec = os.path.join(target, ".specify")
    if not os.path.isdir(spec):
        return None
    dest = os.path.join(spec, "extensions.yml")
    if os.path.isfile(dest):
        return "present"
    tpl = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "references", "speckit-extensions.yml")
    try:
        with open(tpl, encoding="utf-8") as f:
            content = f.read()
        with open(dest, "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
        return "created"
    except OSError:
        return None


def _report_extensions(status):
    if status == "created":
        print("Hooks SpecKit initialises : .specify/extensions.yml (registre Factory, branche les automations Linear en hooks optionnels).")
    elif status == "present":
        print(".specify/extensions.yml deja present -- hooks inchanges.")


def write_init_options(target):
    """Fige la numerotation SpecKit en SEQUENTIEL dans `.specify/init-options.json` — c'est ce que lit
    le command `/speckit.specify` pour numeroter les features. Sequentiel = NNN 3 chiffres, aligne sur
    l'`id` du registre canonique de l'architecte ; le timestamp est BANNI (turn_cost.py:27 et le hook
    Linear lisent `^\\d{3}-`, une numerotation horodatee casserait l'attribution des couts et la sync).
    Read-merge-write si le fichier existe, creation sinon. Idempotent, best-effort ; ne jamais ecraser
    un JSON qu'on ne comprend pas. Renvoie 'set' / 'present' / None."""
    spec = os.path.join(target, ".specify")
    if not os.path.isdir(spec):
        return None
    dest = os.path.join(spec, "init-options.json")
    data = {}
    if os.path.isfile(dest):
        try:
            with open(dest, encoding="utf-8-sig") as f:
                data = json.load(f) or {}
        except ValueError:
            return None
    # why: les deux cles coexistent selon la version de SpecKit (`feature_numbering` ecrit par
    # `specify init`, `branch_numbering` lu par la strategie de nommage de branche). Meme valeur, aucun
    # risque : on les pose toutes les deux pour ne dependre d'aucune version.
    if all(data.get(k) == "sequential" for k in ("feature_numbering", "branch_numbering")):
        return "present"
    data["feature_numbering"] = "sequential"
    data["branch_numbering"] = "sequential"
    try:
        with open(dest, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")
        return "set"
    except OSError:
        return None


def install_tasks_hook(target):
    """Pose le hook PostToolUse de sync tasks.md -> Linear (script + fusion settings.json) via
    l'installeur `references/linear-sync/install_tasks_linear_hook.py`. Best-effort (ne bloque jamais
    l'install de SpecKit). Renvoie True si l'installeur a tourne sans erreur, False sinon."""
    installer = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "..", "references", "linear-sync", "install_tasks_linear_hook.py")
    if not os.path.isfile(installer):
        return False
    try:
        r = subprocess.run([sys.executable, installer, target],
                           capture_output=True, text=True, timeout=60)
        for line in (r.stdout or "").splitlines():
            if line.strip():
                print(line)
        return r.returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def install_align_hook(target):
    """Pose le hook PostToolUse d'alignement SpecKit (garde-fou anti-collision de numero de feature)
    via `references/speckit-sync/install_align_hook.py` (copie `check_speckit_alignment.py` + fusionne
    settings.json). Best-effort (ne bloque jamais l'install). Renvoie True si l'installeur a tourne sans
    erreur, False sinon."""
    installer = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "..", "references", "speckit-sync", "install_align_hook.py")
    if not os.path.isfile(installer):
        return False
    try:
        r = subprocess.run([sys.executable, installer, target],
                           capture_output=True, text=True, timeout=60)
        for line in (r.stdout or "").splitlines():
            if line.strip():
                print(line)
        return r.returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def emit_result(block, target):
    print(MARKER + " " + json.dumps({**block, "target": target}, ensure_ascii=False))


# --- Orchestration ------------------------------------------------------------
def parse_args(argv):
    ap = argparse.ArgumentParser(add_help=True, description="Installeur SpecKit (specify) pour le repo cible.")
    ap.add_argument("target", nargs="?", default=None)
    ap.add_argument("--cli-only", action="store_true")
    ap.add_argument("--ephemeral", action="store_true")
    ap.add_argument("--ref", default=None)
    ap.add_argument("--integration", default=DEFAULT_INTEGRATION)
    ap.add_argument("--allow-pypi", action="store_true")
    ap.add_argument("--no-manifest", action="store_true")
    ap.add_argument("--upgrade", action="store_true",
                    help="bumpe volontairement la version : ignore la ref epinglee au manifeste")
    ap.add_argument("--verbose", "--debug", dest="verbose", action="store_true")
    return ap.parse_args(argv[1:])


def resolve_ref(target, args):
    """Ref a installer. why: sans epinglage, deux membres qui installent a deux semaines d'ecart
    n'ont pas la meme version de SpecKit ni les memes templates. La 1re installation enregistre sa ref
    dans le manifeste committe ; les suivantes la REUTILISENT (sauf --ref explicite ou --upgrade)."""
    if args.ref or args.upgrade:
        return args.ref, None
    pinned = read_speckit_block(target).get("ref")
    if pinned:
        return pinned, f"Version SpecKit epinglee par l'equipe (manifeste) : {pinned} -- meme version pour tout le monde."
    return None, None


def _finish(target, args, ref, cli_desc, version, note):
    """Pose la config d'equipe (hooks, numerotation), ecrit le manifeste, restitue le statut."""
    ext = write_extensions(target)
    tasks_hook = install_tasks_hook(target)
    init_options = write_init_options(target)
    align_hook = install_align_hook(target)
    block = {"installed": True, "initialized": True, "path": ".specify",
             "integration": args.integration, "script": SCRIPT_FLAVOR, "cli": cli_desc,
             "ref": ref, "version": version,
             "extensions_hooks": ext, "tasks_hook": tasks_hook,
             "init_options": init_options, "align_hook": align_hook}
    write_manifest(target, block, args.no_manifest)
    _report_extensions(ext)
    if init_options in ("set", "present"):
        print("Numerotation SpecKit figee en SEQUENTIEL (.specify/init-options.json) — chaque feature garde son NNN canonique ; jamais d'auto-numerotation entre developpeurs.")
    if note:
        print(note)
    if tasks_hook or align_hook:
        print("Les hooks poses dans .claude/settings.json ne deviennent actifs qu'au REDEMARRAGE de la session Claude Code (une revue des hooks peut etre demandee).")
    print("Prochaine etape : /speckit.constitution avec assembleur-out/pre-constitution.md, puis les /speckit.specify dans l'ordre de feature-map.md (une branche NNN-slug par feature, SPECIFY_FEATURE_DIRECTORY=specs/NNN-slug).")
    emit_result(block, target)
    return 0


def main(argv):
    args = parse_args(argv)
    target = detect_target(args.target)
    ref, pin_note = resolve_ref(target, args)
    cli_desc = f"{PKG} @ {spec_source(ref)}"
    if pin_note:
        print(pin_note)

    etat, has_cli = diagnose(target)

    # 1. Installation COMPLETE (dossier + commandes) -> idempotent : on ne reinitialise rien.
    if etat == "complet":
        print(f"SpecKit deja operationnel dans {target} (.specify/ + commandes /speckit.*) -- rien a reinitialiser.")
        version = None
        if not has_cli and not args.ephemeral and ensure_uv(args.verbose) and ensure_git():
            # why: le repo est complet mais le poste n'a pas le CLI (clone frais). On le pose sans
            # toucher a .specify/ : sans lui, `specify check`/`specify extension` restent hors de portee.
            cli = acquire_cli(ref, args.ephemeral, args.allow_pypi, args.verbose)
            if cli and shutil.which("specify"):
                print("CLI `specify` manquant sur ce poste : installe (le repo, lui, n'a pas ete touche).")
                version = cli_version(cli)
        elif has_cli:
            version = cli_version(("specify",))
        return _finish(target, args, ref, cli_desc, version, None)

    # 2. Installation PARTIELLE (ex. clone ou seul .specify/ est commite, ou init interrompu)
    #    -> on REPARE au lieu de declarer "rien a faire".
    repair = etat == "partiel"
    if repair:
        print("SpecKit incomplet dans ce dossier (il manque le CLI, .specify/ ou les commandes /speckit.*) : reparation en cours.")

    # 3. Pre-requis (Git est requis dans tous les cas : `specify init` initialise un depot).
    if not ensure_uv(args.verbose):
        return 1
    if not ensure_git():
        return 1

    # 4. Epinglage : figer le SHA installe pour que les membres suivants aient la MEME version.
    if ref is None:
        sha = resolve_head_sha()
        if sha:
            ref = sha
            cli_desc = f"{PKG} @ {spec_source(ref)}"
            print(f"Version SpecKit epinglee pour l'equipe : {sha[:12]} (les prochains membres installeront la meme).")

    # 5. Acquisition du CLI.
    cli = acquire_cli(ref, args.ephemeral, args.allow_pypi, args.verbose)
    if cli is None:
        print("ERREUR: impossible d'acquerir le CLI `specify`. Relance avec --verbose.", file=sys.stderr)
        return 1

    if args.cli_only:
        block = {"installed": True, "initialized": False, "path": None,
                 "integration": args.integration, "script": SCRIPT_FLAVOR, "cli": cli_desc,
                 "ref": ref, "version": cli_version(cli)}
        write_manifest(target, block, args.no_manifest)
        print("CLI `specify` installe (persistant). `specify init` NON lance (--cli-only).")
        emit_result(block, target)
        return 0

    # 6. Flags par introspection, puis init.
    help_text = init_help(cli)
    dir_nonempty = os.path.isdir(target) and bool(os.listdir(target))
    argv2 = build_init_argv(cli, target, dir_nonempty, args.integration, help_text)
    if not run_init(argv2, target, args.verbose):
        return 1

    # 7. Test de fumee.
    if not smoke(target):
        # why: tracer l'echec dans le manifeste, sinon la relance suivante croyait avoir affaire a une
        # installation terminee (.specify/ existe) et repartait sur un faux "rien a faire".
        write_manifest(target, {"installed": True, "initialized": False, "path": ".specify",
                                "integration": args.integration, "script": SCRIPT_FLAVOR,
                                "cli": cli_desc, "ref": ref},
                       args.no_manifest)
        print(
            "ERREUR: `specify init` s'est termine mais .specify/ ou les commandes /speckit.* sont "
            "introuvables. Relance avec --verbose.",
            file=sys.stderr,
        )
        return 1

    print(("SpecKit repare dans " if repair else "SpecKit installe et initialise dans ") + f"{target}.")
    print("Crees par `specify init` : .specify/ (constitution, scripts, templates) et les commandes /speckit.* dans .claude/.")
    return _finish(target, args, ref, cli_desc, cli_version(cli), None)


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except KeyboardInterrupt:
        print("\nInterrompu.", file=sys.stderr)
        sys.exit(130)
    except Exception as exc:  # noqa: BLE001 - message net par defaut ; trace seulement en --verbose
        if "--verbose" in sys.argv or "--debug" in sys.argv:
            raise
        print(f"ERREUR inattendue: {exc}. Relance avec --verbose pour le detail.", file=sys.stderr)
        sys.exit(1)
