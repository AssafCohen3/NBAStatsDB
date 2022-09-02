<template>
	<v-app-bar
		app
		class="flex justify-items-stretch myappbar"
		color="transparent"
		elevation="0">
		<v-spacer />
		<v-btn
			color="white"
			size="x-large"
			icon="mdi-message-text-outline">
		</v-btn>
		<locale-selector
			class="pe-8" />
	</v-app-bar>
</template>

<script>
import LocaleSelector from './LocaleSelector.vue';

export default {
	components: { LocaleSelector },
};
</script>

<style>
</style>
