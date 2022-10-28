<template>
	<v-card
		class="bg-section-bg-not-transparent">
		<v-card-title>
			<span
				class="text-dimmed-white">
				{{ `${resourceName} - ${actionTitle}` }}
			</span>
		</v-card-title>
		<v-card-text>
			<action-form 
				v-if="actionSpec"
				:action-spec="actionSpec"
				:inputs-values="actionParams"
				:form-submit-text="submitText"
				:cancel-option="true"
				class="text-primary-light"
				@cancel="$emit('cancel')"
				@post-action="submitAction" />
			<v-progress-circular
				v-else
				class="text-primary-light"
				indeterminate />
		</v-card-text>
	</v-card>
</template>

<script>
import { mapActions } from 'vuex';
import ActionForm from './ActionForm.vue';
export default {
	components: { ActionForm },
	props: {
		resourceId: {
			type: String,
			required: true,
		},
		resourceName: {
			type: String,
			required: true,
		},
		actionId: {
			type: String,
			required: true,
		},
		actionTitle: {
			type: String,
			required: true,
		},
		actionParams: {
			type: Object,
			default: null
		},
		submitText: {
			type: String,
			required: true,
		},
	},
	emits: ['submitAction', 'cancel'],
	data(){
		return {
			actionSpec: null,
		};
	},
	mounted(){
		this.fetchActionSpec([this.resourceId, this.actionId])
			.then((resp) => {
				this.actionSpec = resp;
			});
	},
	methods: {
		...mapActions('resources', ['fetchActionSpec']),
		submitAction(actionId, actionForm){
			this.$emit('submitAction', this.resourceId, this.actionId, actionForm);
		}
	},
};
</script>

<style>

</style>