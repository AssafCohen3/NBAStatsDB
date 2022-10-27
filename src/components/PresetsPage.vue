<template>
	<div>
		<!-- content wrappe -->
		<v-overlay
			:model-value="isLoading"
			class="items-center justify-center">
			<v-progress-circular
				indeterminate
				class="text-primary-light"
			/>
		</v-overlay>
		<div
			class="flex flex-col h-full">
			<div
				v-for="preset in presets"
				:key="preset.preset_id">
				<!-- TODO preset div -->
				<preset-card 
					:preset="preset"
					@edit-action-recipe-order="editActionRecipeOrderMethod"
					@remove-action-recipe="removeActionRecipeMethod" />
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
		...mapGetters('presets', ['isCreatingPreset', 'isEditingPreset', 'isRemovingPreset']),
		...mapGetters('action_recipes', ['isCreatingActionRecipe', 'isEditingActionRecipeParams', 'isEditingActionRecipeOrder', 'isRemovingActionRecipe']),
		isLoading(){
			return this.fetchingPresets || this.isCreatingPreset || this.isEditingPreset || this.isRemovingPreset ||
				this.isCreatingActionRecipe || this.isEditingActionRecipeParams || this.isEditingActionRecipeOrder || this.isRemovingActionRecipe;
		}
	},
	mounted(){
		this.refreshPage();
	},
	methods: {
		...mapActions('presets', {
			'fetchPresets': 'fetchExtendedPresets'
		}),
		...mapActions('presets', ['createPreset', 'editPreset', 'removePreset']),
		...mapActions('action_recipes', ['createActionRecipe', 'editActionRecipeParams', 'editActionRecipeOrder', 'removeActionRecipe']),
		refreshPage(){
			this.fetchPresets();
		},
		editActionRecipeOrderMethod(presetId, recipeId, newOrder){
			this.editActionRecipeOrder([presetId, recipeId, newOrder]).
				then((resp) => {
					this.refreshPage();
				});
		},
		removeActionRecipeMethod(presetId, recipeId){
			this.removeActionRecipe([presetId, recipeId]).
				then((resp) => {
					this.refreshPage();
				});
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