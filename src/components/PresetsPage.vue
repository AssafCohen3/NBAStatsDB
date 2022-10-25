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
			<!-- title -->
			<div
				class="flex flex-col w-[fit-content]">
				<div
					v-for="preset in presets"
					:key="preset.preset_id">
					<!-- TODO preset div -->
					{{ preset.preset_name }}
				</div>
			</div>
		</div>
	</div>
</template>

<script>
import { mapActions, mapGetters } from 'vuex';
export default {
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