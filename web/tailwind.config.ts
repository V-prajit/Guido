import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Main palette
        'bg-primary': '#0f1419',
        'bg-secondary': '#1c2128', 
        'bg-tertiary': '#262c36',
        'border': '#373e47',
        'text-primary': '#e6edf3',
        'text-secondary': '#8d96a0',
        'text-muted': '#656d76',
        // Accent colors
        'green': '#2ea043',
        'orange': '#fb8500',
        'red': '#da3633',
        'blue': '#0969da',
        'yellow': '#d29922',
      },
    },
  },
  plugins: [],
}
export default config