/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#ffffff",
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
        },
        // Emergent Aliases
        'retro-yellow': "#F4D73B",
        'retro-coral': "#F27870",
        'retro-purple': "#635BFF",
        'retro-blue': "#A7E8E0",
      },
      borderWidth: {
        '3': '3px',
      },
      keyframes: {
        "accordion-down": {
          from: { height: "0" },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: "0" },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
      },
      // Aliases for Emergent Design Portability
      boxShadow: {
        'neo': '4px 4px 0px 0px rgba(0,0,0,1)',
        'neo-lg': '8px 8px 0px 0px rgba(0,0,0,1)',
        'brutal': '4px 4px 0px 0px rgba(0,0,0,1)', // Alias for neo
        'brutal-lg': '8px 8px 0px 0px rgba(0,0,0,1)', // Alias for neo-lg
        'brutal-sm': '2px 2px 0px 0px rgba(0,0,0,1)',
      },
      fontFamily: {
        sans: ['"Roboto Mono"', 'monospace'], // Default body font
        heading: ['"Oswald"', 'sans-serif'], // Heading font
      },
    },
    plugins: [],
  }
}
