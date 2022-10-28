<template>
	<div>
		<input-picker
			v-for="actionInput, index in actionSpec.action_inputs"
			:key="index"
			v-model:inputData="form"
			:action-input="actionInput" />

		<div
			class="flex justify-between mt-[20px]">
			<v-btn 
				color="success"
				@click="submitAction">
				{{ formSubmitText }}
			</v-btn>
			<v-btn 
				v-if="cancelOption"
				color="error"
				@click="$emit('cancel')">
				{{ $t('common.cancel') }}
			</v-btn>
		</div>
	</div>
</template>

<script>
import InputPicker from './Pickers/InputPicker.vue';
import { useVuelidate } from '@vuelidate/core';
function createFormFromInputs(actionInputs, inputsValues){
	console.log('ii', actionInputs, 'iv', inputsValues);
	//[[p1, p2], [p1, p2]]
	let expectedParams = actionInputs.map(actionInput => {
		return actionInput.expected_params.map(p => p.parameter_name);
	}).flat();
	console.log(expectedParams);
	return Object.assign({}, 
		...expectedParams.map(p => ({[p]: (inputsValues && inputsValues[p]) || null})));
}

export default {
	components: { InputPicker },
	props: {
		actionSpec: {
			type: Object,
			required: true
		},
		inputsValues: {
			type: Object,
			default: null
		},
		formSubmitText: {
			type: String,
			required: true,
		},
		cancelOption: {
			type: Boolean,
			default: false,
		},
	},
	emits: [
		'postAction', 'cancel',
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
				this.form = createFormFromInputs(this.actionSpec.action_inputs, this.inputsValues);
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
			this.$emit('postAction', this.actionSpec.action_id, this.form);
		}
	}
};
</script>

<style>

</style>