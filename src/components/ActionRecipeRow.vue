<template>
	<div>
		<div
			class="not-cloned">
			<v-hover v-slot="{isHovering: isHovering, props: hoverProps}">
				<div
					class="action-recipe-row flex items-center px-[20px] py-[20px] my-[4px] rounded-sm cursor-pointer min-h-[100px]"
					v-bind="hoverProps">
					<div
						class="font-bold text-[16px] text-primary-light max-w-[70%]">
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
										color="primary-light"
										@click="editingParams=true" />
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
									icon="mdi-delete"
									color="primary-light"
									@click="removeActionRecipeMethod" />
							</v-fade-transition>
						</template>
						<p>
							{{ $t('common.delete') }}
						</p>
					</v-tooltip>
				</div>
			</v-hover>
			<v-dialog
				v-model="editingParams"
				persistent>
				<action-form-wrapper
					:action-id="actionRecipe.action_id"
					:action-title="actionRecipe.action_title"
					:resource-id="actionRecipe.resource_id"
					:resource-name="actionRecipe.resource_name"
					:action-params="actionRecipe.params"
					:submit-text="$t('common.save')"
					@cancel="editingParams = false"
					@submit-action="editActionRecipeParamsMethod" />
			</v-dialog>
		</div>
		<div
			class="cloned my-[4px] rounded-sm cursor-pointer min-h-[100px] action-recipe-row text-center 
			flex items-center justify-center">
			<p
				class="text-center text-dimmed-white">
				{{ $t('common.drop_to_copy') }}
			</p>
		</div>
	</div>
</template>

<script>
import { mapActions } from 'vuex';
import ActionFormWrapper from './ActionFormWrapper.vue';
export default {
	components: { ActionFormWrapper, },
	props: {
		actionRecipe: {
			type: Object,
			required: true,
		},
	},
	emits: ['refresh'],
	data(){
		return {
			editingParams: false,
		};
	},
	computed: {
		hasParams(){
			return Object.keys(this.actionRecipe.params).length > 0;
		}
	},	
	methods: {
		...mapActions('action_recipes', ['removeActionRecipe', 'editActionRecipeParams']),
		removeActionRecipeMethod(){
			this.removeActionRecipe([this.actionRecipe.preset_id, this.actionRecipe.action_recipe_id]).
				then((resp) => {
					this.$emit('refresh');
				});
		},
		editActionRecipeParamsMethod(resourceId, actionId, actionParams){
			this.editActionRecipeParams([this.actionRecipe.preset_id, this.actionRecipe.action_recipe_id, actionParams]).
				then((resp) => {
					this.$emit('refresh');
					this.editingParams = false;
				});
		},
	}
};
</script>

<style
	lang="postcss"
	scoped>
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

.cloned{
	display: none;
	outline-width: 5px;
	outline-offset: -15px;
	outline-style: dashed;
	outline-color: theme('colors.dimmed-white');

}

.in-other-list.sortable-ghost .cloned{
	display: flex;
}

.in-other-list.sortable-ghost .not-cloned{
	display: none;
}
</style>