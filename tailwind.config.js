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
	theme: {
		colors: {
			'primary-light': '#d4e1ff',
			'dimmed-white': '#a8adc9',
			'section-bg': '#1d1548A0',
		}
	}
};
