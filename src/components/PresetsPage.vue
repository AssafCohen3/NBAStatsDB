<template>
	<div>
		<div
			v-if="fetchingPresets"
			class="app-section p-[30px] w-[fit-content]">
			<v-progress-circular
				class="text-primary-light"
				indeterminate />
		</div>
		<!-- content wrappe -->
		<div
			v-else>
			<div
				class="flex flex-col h-full">
				<div
					v-for="preset in presets"
					:key="preset.preset_id">
					<!-- TODO preset div -->
					<preset-card 
						:preset="preset" />
				</div>
			</div>
		</div>
	</div>
</template>

<script>
import { mapActions, mapGetters } from 'vuex';
import PresetCard from './PresetCard.vue';
export default {
	components: { PresetCard },
	computed: {
		...mapGetters('presets', {
			'fetchingPresets': 'fetchingExtendedPresets',
			'presets': 'extendedPresets'
		}),
	},
	mounted(){
		this.refreshPage();
	},
	methods: {
		...mapActions('presets', {
			'fetchPresets': 'fetchExtendedPresets'
		}),
		refreshPage(){
			this.fetchPresets();
		},
	},
	onLocaleChange(){
		this.refreshPage();
	},
};
</script>

<style
	lang="postcss"
	scoped>
</style>