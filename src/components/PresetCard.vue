<template>
	<div
		class="preset-div">
		<div
			class="flex items-center">
			<v-btn
				variant="plain"
				:icon="expanded ? 'mdi-chevron-up' : 'mdi-chevron-down'"
				color="primary-light"
				elevation="0"
				@click="expanded = !expanded" />
			<v-hover v-slot="{isHovering, props}">
				<div
					class="flex items-center w-full"
					v-bind="props">
					<div
						class="text-primary-light font-bold text-[24px] select-none">
						{{ preset.preset_name }}
					</div>
					<v-fade-transition>
						<v-btn
							v-show="isHovering"
							class="mx-[5px]"
							variant="plain"
							icon="mdi-pencil"
							color="primary-light"
							@click="editingPreset = true" />
					</v-fade-transition>
				</div>
			</v-hover>
		</div>
		<v-expand-transition>
			<div v-show="expanded">
				<draggable
					v-model="recipesList"
					:group="`${preset.preset_id}_group`"
					item-key="action_recipe_id"
					@change="onChange">
					<template #item="{element}">
						<action-recipe-row
							:action-recipe="element"
							@remove-action-recipe="removeActionRecipe" />
					</template>
				</draggable>
			</div>
		</v-expand-transition>
		<v-dialog
			v-model="editingPreset"
			persistent>
			<translatable-field-input
				:field-title="$t('common.preset_name')"
				:field-translations="preset.preset_name_json" />
		</v-dialog>
	</div>
</template>

<script>
import ActionRecipeRow from './ActionRecipeRow.vue';
// import { Sortable } from 'sortablejs-vue3';
import draggable from 'vuedraggable';
import TranslatableFieldInput from './TranslatableFieldInput.vue';

export default {
	components: { ActionRecipeRow, draggable, TranslatableFieldInput},
	props: {
		preset: {
			type: Object,
			required: true,
		},
	},
	emits: ['editActionRecipeOrder', 'removeActionRecipe'],
	data(){
		return {
			expanded: false,
			editingPreset: false,
		};
	},
	computed: {
		recipesList: {
			get(){
				return this.preset.action_recipes;
			},
			set(newList){
			}
		}
	},
	methods: {
		onChange(event){
			console.log('change: ', event);
			if(event.moved){
				this.$emit('editActionRecipeOrder', this.preset.preset_id, event.moved.element.action_recipe_id, event.moved.newIndex);
			}
		},
		removeActionRecipe(actionRecipeId){
			this.$emit('removeActionRecipe', this.preset.preset_id, actionRecipeId);
		}
	}
};
</script>

<style
	lang="postcss"
	scoped>
.preset-div{
	background: linear-gradient(45deg, #13138f, #2b356880);
	/* w-[30%] p-[30px] m-[10px] rounded-lg */
	width: 50%;
	padding: 5px;
	margin: 30px;
	border-radius: 10px;
	box-shadow: 0px 0px 10px 3px #131434;
}
</style>