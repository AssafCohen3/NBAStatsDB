module.exports = {
	mode: 'jit',
	purge: [
		'./public/*.html',
		'./src/**/*.{vue,js}',
	],
	darkMode: false, // or 'media' or 'class'
	variants: {
		extend: {},
	},
	plugins: [
		require('tailwindcss-rtl'),
	],
};
