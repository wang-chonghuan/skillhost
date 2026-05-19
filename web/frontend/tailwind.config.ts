import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        ink: '#05060A',
        panel: 'rgba(255,255,255,0.035)',
        line: 'rgba(255,255,255,0.10)',
        muted: '#9AA4B2',
        bright: '#F8FAFC',
      },
      boxShadow: {
        glow: '0 0 80px rgba(56, 189, 248, 0.16)',
        panel: '0 24px 80px rgba(0, 0, 0, 0.42)',
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
