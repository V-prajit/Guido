import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'bg-primary': '#0f1729',
        'bg-secondary': '#1a2332', 
        'bg-tertiary': '#243040',
        'border': '#3a4553',
        'text-primary': '#e6edf3',
        'text-secondary': '#8d96a0',
        'text-muted': '#656d76',
        'gold': '#daa520',
        'gold-light': '#f4d03f',
        'gold-dark': '#b8860b',
        'navy': '#0f1729',
      },
    },
  },
  plugins: [],
}
export default config