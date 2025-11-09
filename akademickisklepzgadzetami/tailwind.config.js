/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        "./templates/**/*.html", 
        "./**/templates/**/*.html",
    ],
    theme: {
        extend: {
            backgroundImage: {
                'drop-shadow': 'radial-gradient(50% 50% at 50% 50%, rgba(0, 0, 0, 0.4) 33%, rgba(0, 0, 0, 0) 100%)',
                'drop-hover': 'radial-gradient(50% 50% at 50% 50%, rgba(0, 0, 0, 0.3) 33%, rgba(0, 0, 0, 0) 100%)'
            },
            keyframes: {
                scroll: {
                    '0%': { transform: 'translateX(0)' },
                    '100%': { transform: 'translateX(calc(-50% - 0.25rem))' },
                },
                scrollbanner:{
                    '0%': { transform: 'translateX(0)' },
                    '100%': { transform: 'translateX(calc(-50% - 10px))' },
                }
            },
            animation: {
                'scroll-slow': 'scroll 30s linear infinite',
                'scroll-banner': 'scrollbanner 60s linear infinite'
            },
             fontFamily: {
                exo: ['"Exo 2"', 'sans-serif'],
            },
        },
    },
    plugins: [],
}
