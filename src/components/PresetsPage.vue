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
			class="flex justify-between">
			<div
				class="presets-div-wrapper w-[60%] flex flex-col px-[30px] overflow-y-auto">
				<div
					class="presets-div h-[85vh] overflow-y-auto px-[40px]">
					<div
						class="flex items-center">
						<div
							class="text-primary-light font-bold text-[30px] select-none">
							{{ $t('generic.presets') }}
						</div>
						
						<v-tooltip :text="$t('common.create_preset')">
							<template #activator="{props}">
								<v-btn
									class="mx-[5px]"
									v-bind="props"
									variant="plain"
									icon="mdi-plus-circle-outline"
									size="x-large"
									color="primary-light"
									@click="creatingPreset = true" />
							</template>
						</v-tooltip>
					</div>
					<div
						class="text-dimmed-white font-bold text-[18px] select-none">
						{{ $t('common.presets_explanation') }}
					</div>
					<div
						v-for="preset in presets"
						:key="preset.preset_id">
						<!-- TODO preset div -->
						<preset-card 
							:dragged-action-source-group="draggedActionSourceGroup"
							:preset="preset"
							@refresh="refreshPage"
							@on-drag-start="onActionDragStart"
							@on-drag-end="onActionDragEnd" />
					</div>
				</div>
			</div>
			<div
				class="flex flex-col h-[85vh] overflow-y-auto px-[30px] rounded-[10px] border-dimmed-white border-[1px] w-[40%]">
				<div
					class="flex items-center">
					<div
						class="text-primary-light font-bold text-[30px] select-none">
						{{ $t('common.available_actions') }}
					</div>
				</div>
				<div
					v-for="resource in resources"
					:key="resource.resource_id">
					<pullable-resource-actions-list 
						:resource="resource"
						@action-drag-end="onActionDragEnd"
						@action-drag-start="onActionDragStart" />
				</div>
			</div>
		</div>
		<v-dialog
			v-model="creatingPreset"
			persistent>
			<preset-edit-dialog
				@save-preset="createPresetMethod"
				@cancel="creatingPreset = false" />
		</v-dialog>
	</div>
</template>

<script>
import { mapActions, mapGetters } from 'vuex';
import { toastSuccess } from '../utils/errorToasts';
import PresetCard from './PresetCard.vue';
import PresetEditDialog from './PresetEditDialog.vue';
import PullableResourceActionsList from './PullableResourceActionsList.vue';
export default {
	components: { PresetCard, PresetEditDialog, PullableResourceActionsList },
	data(){
		return {
			creatingPreset: false,
			draggedActionSourceGroup: null,
		};
	},
	computed: {
		...mapGetters('presets', ['presets', 'fetchingPresets', 'isCreatingPreset', 'isEditingPreset', 'isRemovingPreset']),
		...mapGetters('action_recipes', ['isCreatingActionRecipe', 'isEditingActionRecipeParams', 'isEditingActionRecipeOrder', 'isRemovingActionRecipe', 'isCopyingActionRecipe']),
		...mapGetters('resources', ['fetchingResources', 'resources']),
		isLoading(){
			return this.fetchingPresets || this.isCreatingPreset || this.isEditingPreset || this.isRemovingPreset ||
				this.isCreatingActionRecipe || this.isEditingActionRecipeParams || this.isEditingActionRecipeOrder || this.isRemovingActionRecipe || this.isCopyingActionRecipe;
		}
	},
	mounted(){
		this.refreshPage();
	},
	methods: {
		...mapActions('presets', ['fetchPresets', 'createPreset', ]),
		...mapActions('resources', ['fetchResources']),
		refreshPage(){
			this.fetchPresets();
			this.fetchResources();
		},
		refreshPresets(){
			this.fetchPresets();
		},
		createPresetMethod(presetId, presetNameJson){
			this.createPreset([presetId, presetNameJson])
				.then((resp) => {
					this.refreshPresets();
					this.creatingPreset = false;
					toastSuccess(this.$t('messages.preset_created_successfully'));
				});
		},
		onActionDragStart(groupId){
			this.draggedActionSourceGroup = groupId;
		},
		onActionDragEnd(){
			this.draggedActionSourceGroup = null;
		}
	},
	onLocaleChange(){
		this.refreshPage();
	},
};
</script>

<style
	lang="postcss"
	scoped>
.presets-div-wrapper{
	border-inline-end-width: 1px;
	border-inline-end-style: dashed;
	border-inline-end-color: theme('colors.primary-light');
}
</style>