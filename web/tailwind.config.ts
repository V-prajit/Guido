import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'f1-red': '#FF1801',
        'f1-black': '#000000',
        'f1-white': '#FFFFFF',
        'f1-gray': '#333333',
        'f1-blue': '#00A0E9',
      },
    },
  },
  plugins: [],
}
export default config