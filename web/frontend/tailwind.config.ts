import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        canvas: '#F8FAFC',
        skywash: '#F0F9FF',
        surface: '#FFFFFF',
        'surface-soft': '#F8FBFF',
        ink: '#0F172A',
        muted: '#475569',
        subtle: '#64748B',
        line: '#DCEBFA',
        primary: '#0EA5E9',
        'primary-strong': '#0369A1',
        blue: '#2563EB',
        accent: '#F97316',
        success: '#10B981',
        code: '#0F172A',
      },
      boxShadow: {
        soft: '0 24px 70px rgba(15, 23, 42, 0.08)',
        card: '0 16px 40px rgba(2, 132, 199, 0.10)',
        glow: '0 20px 60px rgba(14, 165, 233, 0.18)',
      },
      fontFamily: {
        display: [
          'Space Grotesk',
          'Inter',
          'ui-sans-serif',
          'system-ui',
          'sans-serif',
        ],
        sans: [
          'DM Sans',
          'Inter',
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
