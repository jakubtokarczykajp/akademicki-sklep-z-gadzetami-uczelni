/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        "./templates/**/*.html", 
        "./**/templates/**/*.html",
        "./templates/oscar/**/*.html",
    ],
    safelist: [
        'bg-gray-800',
        'bg-gray-600',
        'bg-blue-100',
        'bg-red-600',
        'w-[60px]',
        'w-8',
        'h-8',
        'h-[70px]',
        'h-full',
        'p-6',
        'p-8',
        'pb-6',
        'flex',
        'flex-col',
        'right-2',
        'justify-between',
        'bg-[#1e1e1e]',
        'backdrop-blur-sm'
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
