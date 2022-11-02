<template>
	<div
		class="preset-div"
		@dragenter="onMouseEnter"
		@dragleave="onMouseLeave">
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
					<v-tooltip
						:text="$t('common.edit')">
						<template #activator="{ props: tooltipProps }">
							<v-fade-transition>
								<v-btn
									v-show="isHovering"
									v-bind="tooltipProps"
									class="mx-[5px]"
									variant="plain"
									icon="mdi-pencil"
									color="primary-light"
									@click="editingPreset = true" />
							</v-fade-transition>
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
									@click="removePresetMethod" />
							</v-fade-transition>
						</template>
						<p>
							{{ $t('common.delete') }}
						</p>
					</v-tooltip>
				</div>
			</v-hover>
		</div>
		<v-expand-transition>
			<div
				v-show="expanded">
				<!-- TODO change pull to true and allow copy recipes between presets -->
				<draggable
					v-model="recipesList"
					:group="{
						name: `${preset.preset_id}_group`,
						pull: 'clone',
						put: true,
					}"
					item-key="action_recipe_id"
					@change="onChange"
					@move="onMove"
					@start="onDragStart"
					@end="onDragEnd">
					<template #item="{element}">
						<draggable-action-recipe-row
							:action-recipe="element"
							@refresh="$emit('refresh')" />
					</template>
				</draggable>
			</div>
		</v-expand-transition>
		<v-dialog
			v-model="editingPreset"
			persistent>
			<preset-edit-dialog
				:preset="preset"
				@save-preset="savePresetName"
				@cancel="editingPreset = false" />
		</v-dialog>
		<v-dialog
			v-if="actionToAdd"
			v-model="addingAction"
			persistent>
			<action-form-wrapper
				:action-id="actionToAdd.action_id"
				:action-title="actionToAdd.action_title"
				:resource-id="actionToAdd.resource_id"
				:resource-name="actionToAdd.resource_name"
				:submit-text="$t('common.add')"
				@cancel="cancelActionCreation"
				@submit-action="addAction"
			/>
		</v-dialog>
	</div>
</template>

<script>
import DraggableActionRecipeRow from './DraggableActionRecipeRow.vue';
import draggable from 'vuedraggable';
import { mapActions, } from 'vuex';
import PresetEditDialog from './PresetEditDialog.vue';
import ActionFormWrapper from './ActionFormWrapper.vue';
import { toastSuccess } from '../utils/errorToasts';

export default {
	components: { DraggableActionRecipeRow, draggable, PresetEditDialog, ActionFormWrapper},
	props: {
		preset: {
			type: Object,
			required: true,
		},
		draggedActionSourceGroup: {
			type: String,
			default: null,
		},
	},
	emits: ['refresh', 'onDragStart', 'onDragEnd'],
	data(){
		return {
			expanded: false,
			editingPreset: false,
			addingAction: false,
			actionToAdd: null,
			expandTimeout: null,
		};
	},
	computed: {
		recipesList: {
			get(){
				return this.preset.action_recipes;
			},
			set(newList){
			}
		},
		groupId(){
			return this.preset ? `${this.preset.preset_id}_group` : null;
		},
		isDragHoverActive(){
			return this.preset && !this.expanded && this.draggedActionSourceGroup && this.draggedActionSourceGroup != this.groupId;
		},
	},
	methods: {
		...mapActions('presets', ['editPreset', 'removePreset']),
		...mapActions('action_recipes', ['editActionRecipeOrder', 'copyActionRecipe', 'createActionRecipe',]),
		onChange(event){
			if(event.moved){
				this.editActionRecipeOrder([this.preset.preset_id, event.moved.element.action_recipe_id, event.moved.newIndex])
					.then((resp) => {
						this.$emit('refresh');
						toastSuccess(this.$t('messages.actions_order_saved'));
					});
			}
			else if(event.added){
				let newRecipe = event.added.element;
				if(newRecipe.action_recipe_id){
					this.copyActionRecipe([newRecipe.preset_id, newRecipe.action_recipe_id, this.preset.preset_id, event.added.newIndex])
						.then((resp) => {
							this.$emit('refresh');
							toastSuccess(this.$t('messages.action_copied_successfully'));
						});
				}
				else if(newRecipe.action_id){
					this.actionToAdd = {...newRecipe, order: event.added.newIndex};
					this.addingAction = true;
				}
			}
		},
		savePresetName(presetId, presetNameJson){
			this.editPreset([this.preset.preset_id, presetNameJson])
				.then((resp) => {
					this.editingPreset = false;
					this.$emit('refresh');
					toastSuccess(this.$t('messages.preset_saved_successfully'));
				});
		},
		removePresetMethod(){
			this.removePreset([this.preset.preset_id])
				.then((resp) => {
					this.$emit('refresh');
					toastSuccess(this.$t('messages.preset_removed_successfully'));
				});
		},
		onMove(evt){
			if(evt.from != evt.to){
				evt.dragged.classList.add('in-other-list');
				evt.dragged.classList.remove('some-list');
			}
			else{
				evt.dragged.classList.remove('in-other-list');
				evt.dragged.classList.add('some-list');
			}
		},
		cancelActionCreation(){
			this.addingAction = false;
			this.actionToAdd = null;
		},
		addAction(resourceId, actionId, actionParams){
			this.createActionRecipe([this.preset.preset_id, resourceId, actionId, this.actionToAdd.order, actionParams])
				.then((resp) => {
					this.cancelActionCreation();
					this.$emit('refresh');
					toastSuccess(this.$t('messages.action_created_successfully'));
				});
		},
		onDragStart(){
			this.$emit('onDragStart', `preset-${this.preset.preset_id}`);
		},
		onDragEnd(){
			this.$emit('onDragEnd');
		},
		onMouseEnter(){
			if(this.isDragHoverActive){
				this.expandTimeout = setTimeout(() => {
					if(this.isDragHoverActive){
						this.expanded = true;
					}
					this.expandTimeout = null;
				}, 1000);
			}
		},
		onMouseLeave(){
			if(this.expandTimeout){
				clearTimeout(this.expandTimeout);
			}
		},
	}
};
</script>

<style
	lang="postcss"
	scoped>

.preset-div{
	background: linear-gradient(45deg, #13138f, #2b356880);
	/* w-[30%] p-[30px] m-[10px] rounded-lg */
	padding: 5px;
	width: 80%;
	margin-block: 30px;
	border-radius: 10px;
	margin-inline-start: 5px;
	box-shadow: 0px 0px 10px 3px #131434;
}

</style>