/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'cyber-dark': '#0a0e1a',
        'cyber-darker': '#050810',
        'cyber-blue': '#00d9ff',
        'cyber-green': '#00ff9f',
        'cyber-teal': '#00ffcc',
        'cyber-yellow': '#ffcc00',
        'cyber-purple': '#b366ff',
        'cyber-pink': '#ff66cc',
      },
      fontFamily: {
        'mono': ['Share Tech Mono', 'Courier New', 'monospace'],
        'orbitron': ['Orbitron', 'sans-serif'],
        'rajdhani': ['Rajdhani', 'sans-serif'],
        'game': ['Rajdhani', 'Orbitron', 'sans-serif'],
      },
      boxShadow: {
        'neon-blue': '0 0 10px #00d9ff, 0 0 20px #00d9ff, 0 0 30px #00d9ff',
        'neon-green': '0 0 10px #00ff9f, 0 0 20px #00ff9f, 0 0 30px #00ff9f',
        'neon-teal': '0 0 10px #00ffcc, 0 0 20px #00ffcc, 0 0 30px #00ffcc',
      },
      animation: {
        'pulse-glow': 'pulse-glow 2s ease-in-out infinite',
        'typing': 'typing 0.5s steps(40, end)',
        'fade-in': 'fade-in 0.5s ease-out',
        'slide-up': 'slide-up 0.4s ease-out',
        'slide-down': 'slide-down 0.4s ease-out',
        'glow': 'glow 2s ease-in-out infinite',
        'float': 'float 3s ease-in-out infinite',
        'scan': 'scan 2s linear infinite',
      },
      keyframes: {
        'pulse-glow': {
          '0%, 100%': { opacity: '1', boxShadow: '0 0 20px currentColor' },
          '50%': { opacity: '0.7', boxShadow: '0 0 40px currentColor' },
        },
        'fade-in': {
          '0%': { opacity: '0', transform: 'scale(0.95)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
        'slide-up': {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'slide-down': {
          '0%': { opacity: '0', transform: 'translateY(-20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'glow': {
          '0%, 100%': { textShadow: '0 0 10px currentColor, 0 0 20px currentColor, 0 0 30px currentColor' },
          '50%': { textShadow: '0 0 20px currentColor, 0 0 30px currentColor, 0 0 40px currentColor, 0 0 50px currentColor' },
        },
        'float': {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        'scan': {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(100%)' },
        },
      },
    },
  },
  plugins: [],
}
