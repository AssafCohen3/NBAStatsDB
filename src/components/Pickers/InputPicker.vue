<template>
	<div
		class="py-[10px]">
		<season-type-picker
			v-if="actionInput.input_name == 'SeasonTypeSelector'"
			v-model:inputData="inputDataModel" />
		<date-range-picker
			v-if="actionInput.input_name == 'DateRangeSelector'"
			v-model:inputData="inputDataModel"
			:default-date="actionInput.default_date"
			:min-date="actionInput.min_date"
			:max-date="actionInput.max_date" />
		<season-range-picker
			v-if="actionInput.input_name == 'SeasonRangeSelector'"
			v-model:inputData="inputDataModel"
			:default-season="actionInput.default_season"
			:min-season="actionInput.min_season"
			:max-season="actionInput.max_season" />
	</div>
</template>

<script>
import DateRangePicker from './DateRangePicker.vue';
import SeasonRangePicker from './SeasonRangePicker.vue';
import SeasonTypePicker from './SeasonTypePicker.vue';
export default {
	components: { SeasonTypePicker, DateRangePicker, SeasonRangePicker, },
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
	emits: ['update:inputData'],
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