<template>
	<div>
		<!-- resources list -->
		<div
			class="flex justify-center">
			<div
				class="resources_grid_wrapper app-section flex flex-col justify-center items-center">
				<div
					class="text-primary-light text-[30px] font-bold pb-[20px]">
					{{ $t('generic.resources') }}
				</div>
				<div
					class="resources_grid">
					<div
						v-ripple="{class: 'white--text'}"
						class="resource_tile rounded-[20px] bg-[#ffffff10]
					h-[150px] min-w-[150px] 
					flex items-center justify-center flex-col
					text-dimmed-white select-none
					cursor-pointer"
						v-for="resource, index in repeated"
						:key="index">
						<div
							class="text-[20px] font-bold p-[20px]">
							{{ resource.resource_name }}
						</div>
						<div
							class="text-[16px] p-[10px]">
							<div>
								{{ $t('generic.last_updated') + ':' }}
							</div>
							<div
								class="text-center">
								{{ resource.last_updated || $t('common.never') }}
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
		...mapGetters({
			resources: 'resources/resources',
			fetchingResources: 'resources/fetchingResources'
		}),
		repeated(){
			if(this.resources && this.resources[0]){
				return [
					this.resources[0],
					this.resources[0],
					this.resources[0],
					this.resources[0],
					this.resources[0],
					this.resources[0],
					this.resources[0],
					this.resources[0],
					this.resources[0],
					this.resources[0],
					this.resources[0],
					this.resources[0],
				];
			}
			return [];
		}
	},
	methods: {
		...mapActions({
			fetchResources: 'resources/fetchResources',
		}),
	},
	mounted(){
		this.fetchResources();
	}
};
</script>

<style scoped>

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

</style>