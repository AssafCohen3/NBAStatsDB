<template>
	<div>
		<input-picker
			v-for="actionInput, index in actionSpec.action_inputs"
			:key="index"
			v-model:inputData="form[actionInput.input_name]"
			:action-input="actionInput" />
		<v-btn 
			class="mt-[20px]"
			color="success"
			@click="submitAction">
			{{ $t('common.submit') }}
		</v-btn>
	</div>
</template>

<script>
import InputPicker from './Pickers/InputPicker.vue';
import { useVuelidate } from '@vuelidate/core';
function createFormFromInputs(actionInputs){
	return Object.assign({}, 
		...actionInputs.map(actionInput => ({
			[actionInput.input_name]: {}
		}))
	);
}

export default {
	components: { InputPicker },
	props: {
		actionSpec: {
			type: Object,
			required: true
		},
	},
	emits: [
		'postAction',
	],
	setup(){
		const v$ = useVuelidate();
		return { v$ };
	},
	data(){
		return {
			form: {},
		};
	},
	watch: {
		actionSpec: {
			handler(newVal){
				this.form = createFormFromInputs(this.actionSpec.action_inputs);
			},
			immediate: true,
		},
	},
	methods: {
		submitAction(){
			this.v$.$touch();
			if(this.v$.$error){
				return;
			}
			let actionForm = Object.assign({},
				...Object.keys(this.form).map(key => this.form[key]));
			this.$emit('postAction', this.actionSpec.action_id, actionForm);
		}
	}
};
</script>

<style>

</style>