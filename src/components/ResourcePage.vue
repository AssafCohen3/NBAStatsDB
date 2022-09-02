<template>
	<div>
		<div
			class="app-section p-[30px] w-[fit-content]"
			v-if="fetchingResource || currentResource == null">
			<v-progress-circular
				class="text-primary-light"
				v-if="fetchingResource || currentResource == null"
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
							{{ currentResource.last_updated || $t('common.never') }}
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
					class="flex flex-row text-primary-light font-bold text-[30px] p-[20px] pb-[20px]">
					<v-icon
						class="pe-5">
						mdi-help-circle-outline
					</v-icon>
					{{ $t('common.status') }}
				</div>
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
			</div>
		</div>
	</div>
</template>

<script>
import { mapActions, mapGetters } from 'vuex';
export default {
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
	methods: {
		...mapActions('resources', ['fetchResource']),
	},
	watch: {
		resourceId: {
			handler(newVal){
				if(newVal !== undefined){
					this.fetchResource([newVal])
						.then(resource => {
							this.currentResource = resource;
						});	
				} 
			},
			immediate: true
		}
	}
};
</script>

<style>

</style>