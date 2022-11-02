<template>
	<div
		class="h-full w-full">
		<div
			v-if="fetchingResource || currentResource == null"
			class="flex h-full items-center justify-center">
			<div
				class="app-section p-[30px] w-[fit-content]">
				<v-progress-circular
					class=" text-primary-light "
					indeterminate />
			</div>
		</div>
		<!-- content wrappe -->
		<div
			v-else>
			<!-- title -->
			<div
				class="px-[30px] flex items-center justify-start resource-extra overflow-x-auto">
				<div
					class="text-primary-light text-[50px] font-bold pe-5">
					{{ currentResource.resource_name }}
				</div>
				<div
					class="custom-card flex items-center">
					<v-icon
						class="text-primary-light text-[30px] pe-4">
						mdi-clock-time-five-outline
					</v-icon>
					<div>
						<div
							class="text-dimmed-white whitespace-pre font-bold text-[25px]">
							{{ currentResource.last_updated && $moment(currentResource.last_updated).format('YYYY-MM-DD[\n]HH:mm') || $t('common.never') }}
						</div>
						<div
							class="text-dimmed-white text-[12px]">
							{{ $t('common.last_updated') }}
						</div>
					</div>
				</div>
				<div
					v-for="table in currentResource.related_tables"
					:key="table.name"
					class="custom-card flex items-center">
					<v-icon
						class="text-primary-light text-[30px] pe-4 mb-[15px]">
						mdi-database
					</v-icon>
					<div>
						<div
							class="text-dimmed-white whitespace-pre-wrap font-bold text-[25px]">
							{{ table.name }}
						</div>
						<div
							class="text-dimmed-white text-[12px]">
							{{ $t('common.related_table') }}
						</div>
					</div>
				</div>
			</div>
			<div
				class="text-dimmed-white p-[30px]">
				<v-icon
					color="info"
					class="pb-[5px]"
					size="x-large">
					mdi-information
				</v-icon>
				<span
					class="ms-3 text-[24px] whitespace-pre-wrap">
					{{ descriptionToShow }}
				</span>
				<span
					v-if="showReadMoreButton"
					class="ms-3 text-dimmed-white text-[16px] font-bold cursor-pointer"
					@click="descriptionExpanded = !descriptionExpanded">
					{{ expandCollapseDescriptionButtonText }}
				</span>
			</div>
			<div
				class="resource-extra flex flex-row overflow-x-auto gap-[30px] items-stretch" />
			<!-- messages -->
			<div
				class="select-none ps-4 pt-[40px]">
				<div
					class="flex items-center pb-[20px]">
					<v-icon
						class="text-[40px] font-bold"
						color="primary-light">
						mdi-message-outline
					</v-icon>
					<div
						class="text-[30px] text-primary-light font-bold text-center px-[10px]">
						{{ $t('common.messages') }}
					</div>
				</div>
				<div
					class="w-[80%] min-w-[500px] flex flex-wrap gap-[30px]">
					<!-- bg-[#2c235a] -->
					<div
						v-for="message, index in currentResource.messages"
						:key="`${currentResource.resource_id}-${index}`"
						class="p-[20px] app-section w-[250px] flex flex-row items-center message-card ">
						<div
							class="flex flex-col pe-4">
							<span
								class="text-primary-light block pb-[10px] font-bold">
								{{ message.title }}
							</span>
							<span
								class="text-dimmed-white ">
								{{ message.text }}
							</span>
						</div>
						<v-icon
							class="text-[40px]"
							:color="getStatusColor(message.status)">
							{{ getStatusIcon(message.status) }}
						</v-icon>
					</div>
				</div>
			</div>
			<!-- actions -->
			<div
				class="pt-[40px] select-none">
				<div
					class="flex flex-row text-primary-light font-bold text-[30px] p-[20px] pb-[20px]">
					<v-icon
						class="pe-5">
						mdi-cog-outline
					</v-icon>
					{{ $t('common.actions') }}
				</div>
				<v-expansion-panels
					variant="inset">
					<v-expansion-panel
						v-for="actionSpec, index in currentResource.actions_specs"
						:key="index"
						:title="actionSpec.action_title"
						class="action_panel !bg-section-bg !text-dimmed-white font-bold">
						<v-expansion-panel-text>
							<div
								class="p-[20px]">
								<action-form									
									:action-spec="actionSpec"
									:form-submit-text="$t('common.run')"
									@post-action="runAction" />
							</div>
						</v-expansion-panel-text>
					</v-expansion-panel>
				</v-expansion-panels>
			</div>
		</div>
		<v-dialog
			v-if="isDependenciesModalOpen"
			v-model="isDependenciesModalOpen"
			persistent>
			<action-dependencies-modal 
				:action-id="actionIdForModal"
				:action-params="actionParamsForModal"
				:action-dependencies="actionDependenciesForModal"
				@submit-dependencies="submitDependencies" />
		</v-dialog>
	</div>
</template>

<script>
import { mapActions, mapGetters } from 'vuex';
import { toastSuccess } from '../utils/errorToasts';
import ActionDependenciesModal from './ActionDependenciesModal.vue';
import ActionForm from './ActionForm.vue';
export default {
	components: { ActionForm, ActionDependenciesModal },
	data(){
		return {
			currentResource: null,
			isDependenciesModalOpen: false,
			actionIdForModal: null,
			actionParamsForModal: null,
			actionDependenciesForModal: null,
			descriptionExpanded: false,
			maxCollapsedDescriptionLength: 150,
		};
	},
	computed: {
		...mapGetters('resources', ['fetchingResource']),
		...mapGetters('tasks', ['resourcesIdsToRefresh']),
		resourceId(){
			return this.$route.params.resourceId;
		},
		descriptionToShow(){
			if(!this.currentResource){
				return '';
			}
			if(this.descriptionExpanded){
				return this.currentResource.description;
			}
			if(this.currentResource.description.length <= this.maxCollapsedDescriptionLength){
				return this.currentResource.description;
			}
			return this.currentResource.description.slice(0, this.maxCollapsedDescriptionLength) + '...';
		},
		showReadMoreButton(){
			return this.currentResource && this.currentResource.description.length > this.maxCollapsedDescriptionLength;
		},
		expandCollapseDescriptionButtonText(){
			return this.descriptionExpanded ? this.$t('common.read_less') : this.$t('read_more');
		},
	},
	watch: {
		resourceId: {
			handler(newVal){
				this.refreshPage();
			},
			immediate: true
		},
		resourcesIdsToRefresh(newVal){
			if(this.currentResource && !this.fetchingResource && this.resourcesIdsToRefresh.includes(this.currentResource.resource_id)){
				this.refreshPage();
			}
		}
	},
	methods: {
		...mapActions('resources', ['fetchResource', 'postAction']),
		refreshPage(){
			if(this.resourceId !== undefined){
				this.fetchResource([this.resourceId])
					.then(resource => {
						this.currentResource = resource;
					})
					.catch(err => {
						this.currentResource = null;
					});
			}
		},
		runAction(actionId, actionParams){
			let action = this.currentResource.actions_specs.find((action) => action.action_id == actionId);
			let downloadDependencies = localStorage.getItem('downloadDependencies', null);
			if(action.action_dependencies.length > 0 && downloadDependencies === null){
				this.actionIdForModal = actionId;
				this.actionParamsForModal = actionParams;
				this.actionDependenciesForModal = action.action_dependencies;
				this.isDependenciesModalOpen = true;
				return;
			}
			this.postAction([this.resourceId, actionId, actionParams, !!downloadDependencies])
				.then(resp => {
					toastSuccess(this.$t('messages.action_submited_successfully'));
				});
		},
		closeDependenciesModal(){
			this.isDependenciesModalOpen = false;
			this.actionIdForModal = null;
			this.actionParamsForModal = null;
			this.actionDependenciesForModal = null;
		},
		submitDependencies(actionId, actionParams, downloadDependencies, rememberMyAnswer){
			if(rememberMyAnswer){
				localStorage.setItem('downloadDependencies', downloadDependencies);
			}
			this.postAction([this.resourceId, actionId, actionParams, downloadDependencies])
				.then(resp => {
					toastSuccess(this.$t('messages.action_submited_successfully'));
				});
			this.closeDependenciesModal();
		},
		getStatusColor(status){
			switch (status) {
			case 'OK':
				return 'green';
			case 'MISSING':
				return 'warning';
			case 'ERROR':
				return 'red';
			case 'INFO':
				return 'blue';
			default:
				return 'white';
			}
		},
		getStatusIcon(status){
			switch (status) {
			case 'OK':
				return 'mdi-check-circle';
			case 'MISSING':
				return 'mdi-update';
			case 'ERROR':
				return 'mdi-alert-circle';
			case 'INFO':
				return 'mdi-information';
			default:
				return 'mdi-help-circle';
			}
		}
	},
	onLocaleChange(){
		this.refreshPage();
	}
};
</script>

<style
	lang="postcss"
	scoped>

.v-expansion-panel.action_panel :deep(.v-expansion-panel-title){
	@apply text-[20px]
}
.custom-card{
	/* border-radius: 10px;
	border-color: #ffffff40;
	border-width: 3px;
	border-style: groove; */

	padding: 20px;
	/* box-shadow: 0px 0px 4px 1px #0000002b; */
	/* background: linear-gradient(172deg, #221562 3%, #1d0f959e, #160b4ef2); */
}

.resource-extra{
	align-items: center;
	justify-content: center;
	background: linear-gradient(172deg, #22156250 3%, #1d0f9550, #160b4e50);
}

.message-card{
	/* border-radius: 10px;
	border-color: #181845;
	border-width: 3px;
	border-style: groove; */
	padding: 20px;
	box-shadow: 0px 0px 10px 1px #0b0b2c;
}
</style>