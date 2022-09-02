<template>
	<season-type-picker
		v-if="actionInput.input_name == 'SeasonTypeSelector'"
		v-model:inputData="inputDataModel" />
</template>

<script>
import SeasonTypePicker from './SeasonTypePicker.vue';
export default {
	components: { SeasonTypePicker },
	props: {
		actionInput: {
			type: Object,
			required: true,
		},
		inputData: {
			type: Object,
			required: true
		},
	},
	computed: {
		inputDataModel: {
			get(){
				return this.inputData;
			},
			set(newVal){
				this.$emit('update:inputData', newVal);
			}
		}
	}

};
</script>

<style>

</style>