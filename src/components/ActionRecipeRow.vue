<template>
	<div>
		<v-hover v-slot="{isHovering: isHovering, props: hoverProps}">
			<div
				class="action-recipe-row flex items-center px-[20px] py-[20px] my-[4px] rounded-sm cursor-pointer min-h-[100px]"
				v-bind="hoverProps">
				<div
					class="font-bold text-[16px] text-primary-light">
					{{ actionRecipe.resource_name }} - {{ actionRecipe.action_title }}
				</div>
				<v-tooltip>
					<template #activator="{ props: tooltipProps }">
						<v-fade-transition>
							<div
								v-show="isHovering"
								v-bind="tooltipProps">
								<v-btn
									:disabled="!hasParams"
									class="ms-2"
									variant="plain"
									icon="mdi-pencil"
									color="primary-light" />
							</div>
						</v-fade-transition>
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
				<v-tooltip>
					<template #activator="{ props: tooltipProps }">
						<v-fade-transition>
							<v-btn
								v-show="isHovering"
								v-bind="tooltipProps"
								variant="plain"
								icon="mdi-close"
								color="primary-light"
								@click="removeActionRecipe" />
						</v-fade-transition>
					</template>
					<p>
						{{ $t('common.delete') }}
					</p>
				</v-tooltip>
			</div>
		</v-hover>
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
	emits: ['removeActionRecipe'],
	computed: {
		paramsRepresantation(){
			let test = Object.keys(this.actionRecipe.params).map(k => `${k}: ${this.actionRecipe.params[k]}`);
			let test2 = [test[0],test[0],test[0],test[0],test[0],test[0],test[0],test[0],test[0],test[0],test[0],test[0],test[0]];
			// let toRet = Object.keys(this.actionRecipe.params).map(k => `${k}: ${this.actionRecipe.params[k]}`).join('\n');
			let toRet = test2.join('\n');
			return toRet || this.$t('common.no_params');
		},
		hasParams(){
			return Object.keys(this.actionRecipe.params).length > 0;
		}
	},
	methods: {
		removeActionRecipe(){
			this.$emit('removeActionRecipe', this.actionRecipe.action_recipe_id);
		}
	}
};
</script>

<style>
.action-recipe-row{
	background-color: #0000004d;
	/* background-color: #442b2b2e; */
	/* background-color: #262662; */
}

.action-recipe-row:hover{
	background-color: #0000006d;
	/* background-color: #442b2b3e; */
	/* background-color: #262662; */
}
</style>