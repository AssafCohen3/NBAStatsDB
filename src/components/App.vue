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
