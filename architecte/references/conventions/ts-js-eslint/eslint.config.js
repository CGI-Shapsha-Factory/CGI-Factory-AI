// Conventions TS/JS — ESLint « flat config » (v9+), pour les équipes déjà sur ESLint.
// Alternative à Biome (choisir l'un OU l'autre, pas les deux). Se combine avec Prettier
// pour le formatage (.prettierrc). Copié dans conventions/ du projet si retenu.
import js from '@eslint/js';
import tseslint from 'typescript-eslint';

export default tseslint.config(
  js.configs.recommended,
  ...tseslint.configs.recommended,
  {
    languageOptions: {
      ecmaVersion: 2024,
      sourceType: 'module',
    },
    rules: {
      'no-unused-vars': 'off',
      '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
      'no-console': 'warn',
    },
  },
  { ignores: ['dist/', 'build/', 'node_modules/', 'coverage/'] },
);
