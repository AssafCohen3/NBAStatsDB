<template>
	<div>
		<div
			v-if="fetchingResource || currentResource == null"
			class="app-section p-[30px] w-[fit-content]">
			<v-progress-circular
				v-if="fetchingResource || currentResource == null"
				class="text-primary-light"
				indeterminate />
		</div>
		<!-- content wrappe -->
		<div
			v-else>
			<!-- title -->
			<div
				class="flex flex-col w-[fit-content] select-none">
				<div
					class="px-[20px] text-primary-light text-[50px] font-bold">
					{{ currentResource.resource_name }}
				</div>
				<div
					class="flex flex-row items-center p-[30px]">
					<v-icon
						class="text-primary-light text-[30px] pe-4 mb-[15px]">
						mdi-clock-time-five-outline
					</v-icon>
					<div>
						<div
							class="text-dimmed-white font-bold text-[25px]">
							{{ currentResource.last_updated && $moment(currentResource.last_updated).format('YYYY-MM-DD') || $t('common.never') }}
						</div>
						<div
							class="text-dimmed-white text-[12px]">
							{{ $t('common.last_updated') }}
						</div>
					</div>
				</div>
			</div>
			<!-- messages -->
			<div
				class="pt-[40px] select-none">
				<div
					class="w-[80%] min-w-[500px] flex flex-wrap gap-[30px]">
					<div
						v-for="message, index in currentResource.messages"
						:key="`${currentResource.resource_id}-${index}`"
						class="p-[20px] app-section w-[250px] flex flex-row items-center">
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
		};
	},
	computed: {
		...mapGetters('resources', ['fetchingResource']),
		...mapGetters('tasks', ['resourcesIdsToRefresh']),
		resourceId(){
			return this.$route.params.resourceId;
		}
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
					});
			}
		},
		runAction(actionId, actionParams){
			let action = this.currentResource.actions_specs.find((action) => action.action_id == actionId);
			let downloadDependencies = localStorage.getItem('downloadDependencies', null);
			if(action.action_dependencies && downloadDependencies === null){
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

</style>