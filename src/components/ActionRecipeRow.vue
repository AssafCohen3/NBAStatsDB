<template>
	<div>
		<div
			class="action-recipe-row flex items-center p-[20px] my-[4px] rounded-sm">
			<div
				class="font-bold text-[16px] text-primary-light w-[70%]">
				{{ `${actionRecipe.order + 1}. ${actionRecipe.resource_name} - ${actionRecipe.action_title}` }}
			</div>
			<v-tooltip>
				<template #activator="{ props: tooltipProps }">
					<div
						v-bind="tooltipProps">
						<v-btn
							disabled
							class="ms-2"
							variant="plain"
							icon="mdi-form-select"
							color="primary-light" />
					</div>
				</template>
				<p
					v-if="!hasParams">
					{{ $t('common.no_params') }}
				</p>
				<template
					v-else>
					<p
						v-for="(value, key, index) in actionRecipe.params"
						:key="index">
						{{ `${key}: ${value}` }}
					</p>
				</template>
			</v-tooltip>
		</div>
	</div>
</template>

<script>
export default {
	props: {
		actionRecipe: {
			type: Object,
			required: true,
		},
	},
	computed: {
		hasParams(){
			return Object.keys(this.actionRecipe.params).length > 0;
		}
	},	
};
</script>

<style
	lang="postcss"
	scoped>
.action-recipe-row{
	background-color: #0000004d;
}

.action-recipe-row:hover{
	background-color: #0000006d;
}

</style>