/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        ink: '#18212f',
        paper: '#f7f5ef',
        sage: '#4f7661',
        coral: '#d96a52',
      },
      boxShadow: {
        soft: '0 18px 55px rgba(24, 33, 47, 0.12)',
      },
    },
  },
  plugins: [],
};
