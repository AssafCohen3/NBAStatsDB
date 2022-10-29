<template>
	<div>
		<!-- resources list -->
		<div
			class="flex flex-col justify-center items-center">
			<div
				class="presets_grid_wrapper flex flex-col justify-center items-center mb-[20px]">
				<div
					class="text-primary-light text-[30px] align-self-start font-bold pb-[20px]">
					{{ $t('generic.presets') }}
				</div>
				<div
					class="presets_grid">
					<div
						v-for="preset, index in presets"
						:key="index"
						v-ripple="{class: 'white--text'}"
						class="preset_tile"
						@click="presetClicked(preset)">
						<div
							class="text-[20px] text-center font-bold p-[20px]">
							{{ preset.preset_name }}
						</div>
					</div>
				</div>
			</div>
			<div
				class="resources_grid_wrapper app-section flex flex-col justify-center items-center">
				<div
					class="text-primary-light text-[30px] font-bold pb-[20px]">
					{{ $t('generic.resources') }}
				</div>
				<div
					class="resources_grid">
					<div
						v-for="resource, index in resources"
						:key="index"
						v-ripple="{class: 'white--text'}"
						class="resource_tile"
						@click="resourceClicked(resource)">
						<div
							class="text-[20px] text-center font-bold p-[20px]">
							{{ resource.resource_name }}
						</div>
						<div
							class="text-[16px] p-[10px]">
							<div>
								{{ $t('generic.last_updated') + ':' }}
							</div>
							<div
								class="text-center">
								{{ resource.last_updated && $moment(resource.last_updated).format('YYYY-MM-DD') || $t('common.never') }}
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<script>
import { mapActions, mapGetters } from 'vuex';
export default {
	data(){
		return {

		};
	},
	computed: {
		...mapGetters('resources', ['resources', 'fetchingResources']),
		...mapGetters('presets', ['presets', 'fetchingPresets']),
	},
	mounted(){
		this.refreshPage();
	},
	methods: {
		...mapActions('resources',['fetchResources']),
		...mapActions('presets',['fetchPresets', 'dispatchPreset']),
		resourceClicked(resource){
			this.$router.push({
				name: 'resource-page',
				params: {
					resourceId: resource.resource_id
				},
			});
		},
		presetClicked(preset){
			// TODO open preset dialog
			// this.dispatchPreset([preset.preset_id]);
		},
		refreshPage(){
			this.fetchResources();
			this.fetchPresets();			
		},
	},
	onLocaleChange(){
		this.refreshPage();
	}
};
</script>

<style 
	scoped
	lang="postcss">

.resources_grid_wrapper{
	/**
	* User input values.
	*/
	--grid-layout-gap: 50px;
	--grid-column-count: 5;
	--grid-item-width: 200px;
	--wrapper-padding: 50px;

	/**
	* Calculated values.
	*/
	--gap-count: calc(var(--grid-column-count) - 1);
	--total-gap-width: calc(var(--gap-count) * var(--grid-layout-gap));
	--grid-width: calc(var(--grid-item-width) * var(--grid-column-count) + var(--total-gap-width));
	--grid--padding: calc((100% - var(--grid-width) - 2*var(--wrapper-padding)) / 2);
	padding: var(--wrapper-padding);
	width: calc(min(var(--grid-width) + var(--wrapper-padding)*2, 100%));
	/* margin-inline: calc(max(0px, var(--grid--padding))); */
}

.resources_grid{
	width: 100%;
	display: grid;
	grid-template-columns: repeat(auto-fill, minmax(var(--grid-item-width), 1fr));
	grid-gap: var(--grid-layout-gap);
}

.resource_tile{
	@apply text-dimmed-white;
	justify-content: space-between;
	border-radius: 20px;
	background-color: #ffffff10;
	height: auto;
	min-width: 150px;
	display: flex;
	align-items: center;
	justify-content: center;
	flex-direction: column;
	user-select: none;
	cursor: pointer;
}

.presets_grid_wrapper{
	/**
	* User input values.
	*/
	--grid-layout-gap: 50px;
	--grid-column-count: 5;
	--grid-item-width: 200px;
	--wrapper-padding: 50px;

	/**
	* Calculated values.
	*/
	--gap-count: calc(var(--grid-column-count) - 1);
	--total-gap-width: calc(var(--gap-count) * var(--grid-layout-gap));
	--grid-width: calc(var(--grid-item-width) * var(--grid-column-count) + var(--total-gap-width));
	--grid--padding: calc((100% - var(--grid-width) - 2*var(--wrapper-padding)) / 2);
	padding: var(--wrapper-padding);
	width: calc(min(var(--grid-width) + var(--wrapper-padding)*2, 100%));
	/* margin-inline: calc(max(0px, var(--grid--padding))); */
}

.presets_grid{
	width: 100%;
	display: grid;
	grid-template-columns: repeat(auto-fill, minmax(var(--grid-item-width), 1fr));
	grid-gap: var(--grid-layout-gap);
}

.preset_tile{
	@apply text-dimmed-white;
	border-radius: 20px;
	height: auto;
	min-width: 150px;
	display: flex;
	align-items: center;
	justify-content: center;
	flex-direction: column;
	user-select: none;
	cursor: pointer;
	background: linear-gradient(45deg, #134aa7, #2a3881);
	box-shadow: 0 0 30px -15px #00c7ec;
}


</style>