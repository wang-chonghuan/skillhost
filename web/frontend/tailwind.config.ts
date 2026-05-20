import type { Config } from 'tailwindcss';

const config: Config = {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      animation: {
        'spin-slow': 'spin 7s linear infinite',
      },
      fontFamily: {
        sans: [
          'ui-sans-serif',
          'system-ui',
          '-apple-system',
          'BlinkMacSystemFont',
          'Segoe UI',
          'sans-serif',
        ],
        mono: [
          'SFMono-Regular',
          'Cascadia Code',
          'Consolas',
          'Liberation Mono',
          'Menlo',
          'monospace',
        ],
      },
    },
  },
  plugins: [],
};

export default config;
