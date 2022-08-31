<template>
	<div>
		<!-- resources list -->
		<div
			class="resources_grid_wrapper flex flex-col justify-center bg-[#1d1548] rounded-lg items-center">
			<div
				class="text-[#d4e1ff] text-[30px] font-bold pb-[20px]">
				{{ $t('generic.resources') }}
			</div>
			<div
				class="resources_grid">
				<div
					v-ripple="{class: 'white--text'}"
					class="rounded-[20px] bg-[#ffffff10]
					h-[150px] min-w-[150px] 
					flex items-center justify-center flex-col
					text-[#a8adc9]
					cursor-pointer"
					v-for="resource, index in resources"
					:key="index">
					<div
						class="text-[20px] font-bold p-[20px]">
						{{ resource.name }}
					</div>
					<div
						class="text-[16px] p-[10px]">
						<div>
							{{ $t('generic.last_updated') }}
						</div>
						<div>
							{{ resource.last_updated }}
						</div>
					</div>
				</div>
			</div>

		</div>
	</div>
</template>

<script>
export default {
	data(){
		return {
			resources: [
				{
					'name': 'PlayerBoxScore',
					'last_updated': '2022-08-30'
				},
				{
					'name': 'TeamBoxScore',
					'last_updated': '2022-08-30'
				},
				{
					'name': 'Player',
					'last_updated': '2022-08-30'
				},
				{
					'name': 'Transactions',
					'last_updated': '2022-08-30'
				},
				{
					'name': 'Event',
					'last_updated': '2022-08-30'
				},
				{
					'name': 'Awards',
					'last_updated': '2022-08-30'
				},
				{
					'name': 'Honours',
					'last_updated': '2022-08-30'
				},
				{
					'name': 'BREFPlayer',
					'last_updated': '2022-08-30'
				},
				{
					'name': 'PlayerMapping',
					'last_updated': '2022-08-30'
				},
				{
					'name': 'PlayoffSeries',
					'last_updated': '2022-08-30'
				},
				{
					'name': 'Odds',
					'last_updated': '2022-08-30'
				},
			]
		};
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
	margin-inline: calc(max(0px, var(--grid--padding)));
}

.resources_grid{
	width: 100%;
	display: grid;
	grid-template-columns: repeat(auto-fill, minmax(var(--grid-item-width), 1fr));
	grid-gap: var(--grid-layout-gap);
}

</style>