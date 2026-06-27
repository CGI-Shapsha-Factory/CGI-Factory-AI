#!/usr/bin/env node
// Installeur de la Factory IA — facon BMAD (wrapper npx, Node pur, zero dependance).
//
//   npx github:CGI-Shapsha-Factory/CGI-Factory-AI            # menu interactif
//   npx github:CGI-Shapsha-Factory/CGI-Factory-AI --all --yes
//   npx github:CGI-Shapsha-Factory/CGI-Factory-AI --modules cadrage,designer
//
// Equivalent Node de install.py. Enrobe `claude plugin install`. N'affiche aucun secret.
import { spawnSync } from "node:child_process";
import readline from "node:readline";
import process from "node:process";

const MARKETPLACE_NAME = "Shapsha-Factory";
const MARKETPLACE_REPO = "CGI-Shapsha-Factory/CGI-Factory-AI";
const ORDER = ["cadrage", "architecte", "designer", "assembleur"];
const MODULES = {
  cadrage:    ["Contrat fonctionnel : captation -> vision, glossaire, decoupage, briefs, pre-constitution.", "ex. chef de projet / PO"],
  architecte: ["Contrat technique : drivers & qualite, composants, stack, ADR, walking skeleton, conventions.", "ex. architecte"],
  designer:   ["Contrat de design : design system executable (tokens DTCG, composants & etats, parcours, WCAG 2.2).", "ex. dev front / UX"],
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
function runCmd(cmdArr, dry) {
  const printable = cmdArr.join(" ");
  console.log((dry ? "  [dry-run] " : "  $ ") + printable);
  if (dry) return true;
  const r = spawnSync(cmdArr[0], cmdArr.slice(1), { stdio: "inherit", shell: true });
  return r.status === 0;
}
const addMarketplaceCmd = () => ["claude", "plugin", "marketplace", "add", MARKETPLACE_REPO];
const installCmd = (m, scope) => ["claude", "plugin", "install", `${m}@${MARKETPLACE_NAME}`, "--scope", scope];

function ask(question) {
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  return new Promise((res) => rl.question(question, (ans) => { rl.close(); res(ans); }));
}
async function selectNumbered(defaultAll) {
  printList();
  if (defaultAll) return [...ORDER];
  const raw = (await ask("Numeros a installer (ex. 1,3) ou 'all' : ")).trim().toLowerCase();
  if (["all", "*", "tout"].includes(raw)) return [...ORDER];
  const picked = new Set();
  for (const tok of raw.replace(/\s/g, "").split(",")) {
    const n = Number(tok);
    if (Number.isInteger(n) && n >= 1 && n <= ORDER.length) picked.add(ORDER[n - 1]);
  }
  return ORDER.filter((m) => picked.has(m));
}
function selectCheckbox() {
  if (!process.stdin.isTTY) return selectNumbered(false);
  return new Promise((resolve) => {
    const sel = Object.fromEntries(ORDER.map((m) => [m, false]));
    let cur = 0;
    readline.emitKeypressEvents(process.stdin);
    process.stdin.setRawMode(true);
    process.stdin.resume();
    const render = () => {
      process.stdout.write("\x1b[2J\x1b[H");
      process.stdout.write("Factory IA — coche les modules a installer\n");
      process.stdout.write("  (fleches haut/bas, ESPACE = cocher, ENTREE = valider)\n\n");
      ORDER.forEach((m, i) => {
        const box = sel[m] ? "[x]" : "[ ]";
        const ptr = i === cur ? ">" : " ";
        const [desc, role] = MODULES[m];
        process.stdout.write(` ${ptr} ${box} ${m.padEnd(11)} ${desc}  (${role})\n`);
      });
    };
    const cleanup = () => {
      process.stdin.setRawMode(false);
      process.stdin.pause();
      process.stdin.removeListener("keypress", onKey);
    };
    const onKey = (str, key) => {
      if (!key) return;
      if (key.name === "up") cur = (cur - 1 + ORDER.length) % ORDER.length;
      else if (key.name === "down") cur = (cur + 1) % ORDER.length;
      else if (key.name === "space") sel[ORDER[cur]] = !sel[ORDER[cur]];
      else if (key.name === "return" || key.name === "enter") { cleanup(); console.log(); resolve(ORDER.filter((m) => sel[m])); return; }
      else if (key.ctrl && key.name === "c") { cleanup(); console.log("\nAnnule."); process.exit(1); }
      render();
    };
    process.stdin.on("keypress", onKey);
    render();
  });
}

async function main() {
  let a;
  try { a = parseArgs(process.argv.slice(2)); }
  catch (e) { console.error(`Erreur : ${e.message}`); return 2; }
  if (a.help) { printHelp(); return 0; }
  if (a.list) { printList(); return 0; }

  let modules;
  try {
    if (a.all) modules = [...ORDER];
    else if (a.modules != null) modules = parseModules(a.modules);
    else modules = await selectCheckbox();
  } catch (e) { console.error(`Erreur : ${e.message}`); return 2; }
  if (!modules.length) { console.log("Aucun module selectionne. Rien a faire."); return 0; }

  if (!a.dryRun) {
    const probe = spawnSync("claude", ["--version"], { stdio: "ignore", shell: true });
    if (probe.status !== 0) {
      console.error("Le CLI `claude` est introuvable. Installe Claude Code puis relance.\n  https://code.claude.com/docs");
      return 3;
    }
  }

  console.log(`\nModules a installer : ${modules.join(", ")} (scope: ${a.scope})`);
  if (!a.yes && process.stdin.isTTY && !a.dryRun) {
    const ans = (await ask("Continuer ? [o/N] ")).trim().toLowerCase();
    if (!["o", "oui", "y", "yes"].includes(ans)) { console.log("Annule."); return 1; }
  }

  if (!a.noAdd) {
    console.log(`\nMarketplace ${MARKETPLACE_NAME} (${MARKETPLACE_REPO}) :`);
    const ok = runCmd(addMarketplaceCmd(), a.dryRun);
    if (!ok && !a.dryRun) console.log("  (note: ajout non confirme — peut-etre deja presente ; je continue)");
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
  if (ko.length) {
    console.error(`\n${ko.length} module(s) en echec : ${ko.join(", ")} (verifie ton acces au repo de la marketplace, puis relance).`);
    return 4;
  }
  return 0;
}

main().then((code) => process.exit(code)).catch((e) => { console.error(e); process.exit(1); });
