// Fichier COMMITTÉ et INCLUS dans le bundle client = PUBLIC.
// N'y mettez JAMAIS de secret (clé API, mot de passe, token).
// Les secrets doivent rester côté serveur (proxy / gestionnaire de secrets).
// Ici, uniquement des URLs et des flags publics.
export const environment = {
  production: false,
  apiUrl: 'http://localhost:3000/api'
};
