#!/usr/bin/env node
// Installeur de la Factory IA — facon BMAD (wrapper npx).
//
//   npx github:CGI-Shapsha-Factory/CGI-Factory-AI            # menu interactif (cases a cocher)
//   npx github:CGI-Shapsha-Factory/CGI-Factory-AI --all --yes
//   npx github:CGI-Shapsha-Factory/CGI-Factory-AI --modules cadrage,designer
//
// Menu via @inquirer/prompts (vraies cases a cocher cross-platform). Enrobe `claude plugin install`.
// N'affiche aucun secret. L'install via le marketplace Claude Code reste TOUJOURS dispo (cf. fin).
import { spawnSync } from "node:child_process";
import process from "node:process";
import path from "node:path";
import { checkbox, confirm } from "@inquirer/prompts";

// Sous Windows, l'env de npx peut ne pas transmettre `git` au sous-processus -> l'install
// git-subdir echoue. On garantit que le dossier de git est sur le PATH des enfants.
function findGitDir() {
  const probe = spawnSync(process.platform === "win32" ? "where git" : "command -v git",
                          { shell: true, encoding: "utf8" });
  if (probe.status === 0 && probe.stdout) {
    const line = probe.stdout.split(/\r?\n/).map((s) => s.trim()).find(Boolean);
    if (line) return path.dirname(line);
  }
  const b = process.env.CLAUDE_CODE_GIT_BASH_PATH; // …\Git\[usr\]bin\bash.exe -> …\Git\cmd
  if (b) {
    const root = b.replace(/[\\/](usr[\\/])?bin[\\/]bash\.exe$/i, "");
    if (root !== b) return path.join(root, "cmd");
  }
  return null;
}
const CHILD_ENV = { ...process.env };
const _gd = findGitDir();
if (_gd) {
  const cur = CHILD_ENV.PATH || CHILD_ENV.Path || "";
  if (!cur.toLowerCase().split(path.delimiter).includes(_gd.toLowerCase()))
    CHILD_ENV.PATH = _gd + path.delimiter + cur;
}

const MARKETPLACE_NAME = "Shapsha-Factory";
const MARKETPLACE_REPO = "CGI-Shapsha-Factory/CGI-Factory-AI";
const ORDER = ["cadrage", "architecte", "designer", "assembleur"];
const MODULES = {
  cadrage:    ["Contrat fonctionnel : captation -> vision, glossaire, decoupage, briefs.", "ex. chef de projet / PO"],
  architecte: ["Contrat technique : drivers & qualite, composants, stack, ADR, walking skeleton.", "ex. architecte"],
  designer:   ["Contrat de design : design system executable (tokens DTCG, etats, parcours, WCAG 2.2).", "ex. dev front / UX"],
  assembleur: ["Convergence des 3 contrats -> repo SpecKit + init Linear + hook de suivi.", "ex. lead / convergence"],
};
const NEXT_STEP = {
  cadrage: "/cadrage:cadrage-init", architecte: "/architecte:architecte-init",
  designer: "/designer:designer-init", assembleur: "/assembleur:assembleur-init",
};

// ---------- logique pure ----------
function parseModules(s) {
  const wanted = s.split(",").map((m) => m.trim().toLowerCase()).filter(Boolean);
  const unknown = wanted.filter((m) => !(m in MODULES));
  if (unknown.length) throw new Error(`module(s) inconnu(s) : ${unknown.join(", ")} (connus : ${ORDER.join(", ")})`);
  return ORDER.filter((m) => wanted.includes(m));
}
function parseArgs(argv) {
  const a = { scope: "user", yes: false, all: false, list: false, dryRun: false, noAdd: false, help: false, modules: null };
  for (let i = 0; i < argv.length; i++) {
    const t = argv[i];
    if (t === "--all") a.all = true;
    else if (t === "--yes" || t === "-y") a.yes = true;
    else if (t === "--list") a.list = true;
    else if (t === "--dry-run") a.dryRun = true;
    else if (t === "--no-add-marketplace") a.noAdd = true;
    else if (t === "--help" || t === "-h") a.help = true;
    else if (t === "--modules") a.modules = argv[++i] ?? "";
    else if (t.startsWith("--modules=")) a.modules = t.slice("--modules=".length);
    else if (t === "--scope") a.scope = argv[++i] ?? "user";
    else if (t.startsWith("--scope=")) a.scope = t.slice("--scope=".length);
    else throw new Error(`option inconnue : ${t}`);
  }
  if (!["user", "project", "local"].includes(a.scope)) throw new Error(`scope invalide : ${a.scope} (user|project|local)`);
  return a;
}

// ---------- I/O ----------
function printList() {
  console.log(`\nModules de la Factory (marketplace : ${MARKETPLACE_NAME})\n`);
  ORDER.forEach((m, i) => {
    const [desc, role] = MODULES[m];
    console.log(`  ${i + 1}. ${m.padEnd(11)} ${desc}`);
    console.log(`     ${" ".padEnd(11)} (${role})`);
  });
  console.log();
}
function printHelp() {
  console.log(`Installeur Factory IA (facon BMAD)

Usage : factory-method [options]
  (sans option)            menu interactif (cases a cocher)
  --modules a,b            installer ces modules (ex. cadrage,designer)
  --all                    installer tous les modules
  --scope user|project|local   portee (defaut: user)
  --yes, -y                sans confirmation
  --list                   lister les modules
  --no-add-marketplace     ne pas (re)ajouter la marketplace
  --dry-run                montrer les commandes sans rien installer
  --help, -h               cette aide`);
}
function printMarketplaceAlt() {
  console.log("\n— Alternative (toujours disponible) : install via le marketplace Claude Code —");
  console.log(`  /plugin marketplace add ${MARKETPLACE_REPO}`);
  console.log(`  /plugin install <module>@${MARKETPLACE_NAME}     # ex. cadrage@${MARKETPLACE_NAME}`);
  console.log("  (ou /plugin -> onglet Discover : modules groupes par role)");
}
function runCmd(cmdStr, dry) {
  console.log((dry ? "  [dry-run] " : "  $ ") + cmdStr);
  if (dry) return true;
  // chaine unique + shell:true (pas d'array d'args -> evite la DeprecationWarning ; tokens en liste blanche)
  const r = spawnSync(cmdStr, { stdio: "inherit", shell: true, env: CHILD_ENV });
  return r.status === 0;
}
function runCapture(cmdStr, dry) {
  console.log((dry ? "  [dry-run] " : "  $ ") + cmdStr);
  if (dry) return { ok: true, out: "" };
  const r = spawnSync(cmdStr, { shell: true, encoding: "utf8", env: CHILD_ENV });
  const out = (r.stdout || "") + (r.stderr || "");
  if (out.trim()) process.stdout.write(out.replace(/^/gm, "  "));
  return { ok: r.status === 0, out };
}
function looksLikeGitError(out) {
  return /git/i.test(out) && /(not found|unsafe location|introuvable|not detected)/i.test(out);
}
function printGitHint() {
  console.log("\n⚠ Echec probable : Claude Code n'a pas trouve `git` (frequent sous Windows si git est");
  console.log("  dans AppData). Corrige une fois, puis relance :");
  console.log('  1) setx CLAUDE_CODE_GIT_BASH_PATH "C:\\\\chemin\\\\vers\\\\Git\\\\bin\\\\bash.exe"');
  console.log("     (trouve le chemin : `where.exe git` -> remplace \\cmd\\git.exe par \\bin\\bash.exe)");
  console.log("  2) ouvre un NOUVEAU terminal (et redemarre l'app Claude Code).");
}
const addMarketplaceCmd = () => `claude plugin marketplace add ${MARKETPLACE_REPO}`;
const installCmd = (m, scope) => `claude plugin install ${m}@${MARKETPLACE_NAME} --scope ${scope}`;

async function selectInteractive() {
  return checkbox({
    message: "Coche les modules a installer (Espace = cocher, Entree = valider)",
    choices: ORDER.map((m) => ({ name: `${m.padEnd(11)} ${MODULES[m][0]}  (${MODULES[m][1]})`, value: m })),
    loop: false,
  });
}

async function main() {
  let a;
  try { a = parseArgs(process.argv.slice(2)); }
  catch (e) { console.error(`Erreur : ${e.message}`); return 2; }
  if (a.help) { printHelp(); printMarketplaceAlt(); return 0; }
  if (a.list) { printList(); printMarketplaceAlt(); return 0; }

  let modules;
  try {
    if (a.all) modules = [...ORDER];
    else if (a.modules != null) modules = parseModules(a.modules);
    else if (!process.stdin.isTTY) {
      console.error("Mode non-interactif : precise --modules a,b ou --all (ou lance dans un terminal).");
      return 2;
    } else {
      modules = await selectInteractive();
      modules = ORDER.filter((m) => modules.includes(m)); // ordre canonique
    }
  } catch (e) { console.error(`Erreur : ${e.message}`); return 2; }
  if (!modules.length) { console.log("Aucun module selectionne. Rien a faire."); printMarketplaceAlt(); return 0; }

  if (!a.dryRun) {
    const probe = spawnSync("claude --version", { stdio: "ignore", shell: true, env: CHILD_ENV });
    if (probe.status !== 0) {
      console.error("Le CLI `claude` est introuvable. Installe Claude Code puis relance.\n  https://code.claude.com/docs");
      printMarketplaceAlt();
      return 3;
    }
  }

  console.log(`\nModules a installer : ${modules.join(", ")} (scope: ${a.scope})`);
  if (!a.yes && !a.dryRun && process.stdin.isTTY) {
    const ok = await confirm({ message: "Continuer ?", default: true });
    if (!ok) { console.log("Annule."); return 1; }
  }

  if (!a.noAdd) {
    console.log(`\nMarketplace ${MARKETPLACE_NAME} (${MARKETPLACE_REPO}) :`);
    const res = runCapture(addMarketplaceCmd(), a.dryRun);
    if (!res.ok && !a.dryRun) {
      if (looksLikeGitError(res.out)) { printGitHint(); printMarketplaceAlt(); return 5; }
      console.log("  (note: ajout non confirme — peut-etre deja presente ; je continue)");
    }
  }

  console.log("\nInstallation :");
  const results = {};
  for (const m of modules) results[m] = runCmd(installCmd(m, a.scope), a.dryRun);

  const ok = modules.filter((m) => results[m]);
  const ko = modules.filter((m) => !results[m]);
  console.log("\n=== Resume ===");
  for (const m of modules) console.log(`  ${results[m] ? "OK " : "ECHEC"}  ${m}`);
  if (ok.length) {
    console.log("\nProchaines etapes (dans Claude Code) :");
    console.log("  /reload-plugins");
    for (const m of ok) console.log(`  ${NEXT_STEP[m]}   # demarrer le module ${m}`);
  }
  printMarketplaceAlt();
  if (ko.length) {
    console.error(`\n${ko.length} module(s) en echec : ${ko.join(", ")} (verifie ton acces au repo, puis relance).`);
    return 4;
  }
  return 0;
}

main()
  .then((code) => process.exit(code))
  .catch((e) => {
    // Ctrl-C dans un prompt inquirer -> sortie propre
    if (e && (e.name === "ExitPromptError" || /User force closed/i.test(e.message || ""))) {
      console.log("\nAnnule."); process.exit(1);
    }
    console.error(e); process.exit(1);
  });
