<template>
	<router-view />
</template>

<script>

import { useI18n } from 'vue-i18n';

export default {
	name: 'App',
	setup(){
		const { t } = useI18n({
			useScope: 'global'
		});
		return { t };
	},
};
</script>
<style>

html{
	overflow-y: auto !important;
}

/* Turn on custom 8px wide scrollbar */
::-webkit-scrollbar {
	--scrollbar-width: 10px;
	--scrollbar-radius: 100px;

	width: var(--scrollbar-width);
	background-color: rgba(0, 0, 0, 0.25);
	-webkit-border-radius: 100px;
	border-radius: 100px;
}


/* hover effect for both scrollbar area, and scrollbar 'thumb' */
::-webkit-scrollbar:hover {
	background-color: rgba(0, 0, 0, 0.25);
}

/* The scrollbar 'thumb' ...that marque oval shape in a scrollbar */
::-webkit-scrollbar-thumb:vertical {
	background: rgba(0, 0, 0, 0.5);
	-webkit-border-radius: 100px;
	border-radius: 100px;
}

::-webkit-scrollbar-thumb:vertical:active {
	background: rgba(0, 0, 0, 0.61);
	-webkit-border-radius: 100px;
	border-radius: 100px;
}

</style>