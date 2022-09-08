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
				<!-- <div
					class="flex flex-row text-primary-light font-bold text-[30px] p-[20px] pb-[20px]">
					<v-icon
						class="pe-5">
						mdi-help-circle-outline
					</v-icon>
					{{ $t('common.status') }}
				</div> -->
				<div
					class="w-[80%] min-w-[500px] flex flex-wrap gap-[30px]">
					<div
						v-for="message, index in currentResource.messages"
						:key="index"
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
							class="text-[40px] text-green">
							mdi-check-circle
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
									@post-action="runAction" />
							</div>
						</v-expansion-panel-text>
					</v-expansion-panel>
				</v-expansion-panels>
			</div>
		</div>
	</div>
</template>

<script>
import { mapActions, mapGetters } from 'vuex';
import ActionForm from './ActionForm.vue';
export default {
	components: { ActionForm },
	data(){
		return {
			currentResource: null,
		};
	},
	computed: {
		...mapGetters('resources', ['fetchingResource']),
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
			this.postAction([this.resourceId, actionId, actionParams]);
		},
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