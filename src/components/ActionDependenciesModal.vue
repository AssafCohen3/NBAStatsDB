<template>
	<div
		class="border-radius-[8px] bg-section-bg-not-transparent w-[50vw] p-[10px]">
		<div
			class="pt-[20px] px-[10px] font-bold text-primary-light text-[30px]">
			{{ $t('messages.run_dependent_action') }}
		</div>
		<div
			class="pt-[20px] px-[20px]">
			<div
				class="flex">
				<v-icon
					class="me-3"
					color="info"					
					size="x-large">
					mdi-information
				</v-icon>
				<div
					class="text-dimmed-white text-[16px] pb-[10px]">
					{{ $t('messages.action_dependencies_description') }}
				</div>
			</div>
			<div
				class="overflow-y-auto max-h-[50vh] py-[20px]">
				<div
					v-for="action, i in actionDependencies"
					:key="i">
					<div
						class="action-row flex items-center p-[20px] my-[4px] rounded-sm cursor-pointer">
						<div
							class="font-bold text-[16px] text-primary-light">
							{{ `${action.resource_name} - ${action.action_title}` }}
						</div>
					</div>
				</div>
			</div>
			<div
				class="flex flex-col items-center pt-[10px] text-dimmed-white">
				<div
					class="flex items-center">
					<v-btn
						class="me-4"
						color="primary"
						@click="submit(true)">
						{{ $t('common.yes') }}
					</v-btn>
					<v-btn
						color="error"
						@click="submit(false)">
						{{ $t('common.no') }}
					</v-btn>
				</div>
				<v-checkbox 
					v-model="rememberMyAnswer"
					:label="$t('common.remember_my_answer')" />
			</div>
		</div>
	</div>
</template>

<script>
export default {
	props: {
		actionId: {
			type: String,
			required: true,
		},
		actionParams: {
			type: Object,
			required: true,
		},
		actionDependencies: {
			type: Array,
			required: true,
		},
	},
	emits: ['submitDependencies'],
	data(){
		return {
			rememberMyAnswer: false,
		};
	},
	methods: {
		submit(val){
			this.$emit('submitDependencies', this.actionId, this.actionParams, val, this.rememberMyAnswer);
		},
	},
};
</script>

<style
	scoped>

.action-row{
	background-color: #0000004d;
}

.action-row:hover{
	background-color: #0000006d;
}

</style>