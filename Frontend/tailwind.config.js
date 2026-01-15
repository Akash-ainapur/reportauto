/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#ffffff", // Use white as base, dots will be CSS
        foreground: "#000000",
        primary: {
          DEFAULT: "#F4D73B", // Primary Yellow
          hover: "#EAC200", 
        },
        secondary: {
          DEFAULT: "#E6E1F9", // Lavender
        },
        accent: {
          coral: "#F27870",
          purple: "#635BFF",
          teal: "#A7E8E0",
        },
        retro: {
          beige: "#E8E6D9",
        }
      },
      fontFamily: {
        sans: ['"Roboto Mono"', 'monospace'], // Default body font
        heading: ['"Oswald"', 'sans-serif'], // Heading font
      },
      boxShadow: {
        'neo': '4px 4px 0px 0px rgba(0,0,0,1)', // The hard shadow
        'neo-lg': '8px 8px 0px 0px rgba(0,0,0,1)',
      },
      borderWidth: {
        '3': '3px',
      }
    },
  },
  plugins: [],
}
