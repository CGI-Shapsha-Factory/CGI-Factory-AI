# Catalogue de templates de fichiers d'environnement

Ce dossier regroupe des **gabarits** de fichiers d'environnement, un sous-dossier par stack (`python`, `node`, `vite`, `go`, `angular`, `dotnet`, `spring`).

À l'**Étape 10** de `architecte-contrat`, le sous-dossier correspondant à la stack retenue est copié à la racine du projet généré, puis les placeholders sont remplis depuis `tech-stack.md`, `components.md` et les ADR.

Conventions :
- Le catalogue ne fournit que le **`.env.example`** (les `.env` ne se committent jamais) ; l'Étape 10
  écrit `.env.example` **et** en dérive un **`.env`** (à remplir) à la racine du projet, qu'elle gitignore.
- `.env` contient les **vraies valeurs** et reste **gitignored** (jamais committé).
- `.env.example` est **committé** comme référence à copier.
- Les fichiers **Angular** (`environment*.ts`) et **Vite** (variables `VITE_*`) sont inclus dans le **bundle client** = **publics** : ils ne doivent JAMAIS contenir de secret. Les secrets restent côté serveur.
