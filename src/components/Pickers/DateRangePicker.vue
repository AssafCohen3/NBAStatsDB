<template>
	<div
		class="custom_date_picker">
		<date-picker 
			v-model="selectedDateRange" 
			range
			multi-calendars
			multi-calendars-solo
			:min-date="minDate"
			:max-date="maxDate"
			format="yyyy-MM-dd"
			dark
			:start-date="defaultDate"
			:enable-time-picker="false"
			:ignore-time-validation="true"
			:partial-range="false"
			:locale="$i18n.locale"
			:clearable="false">
			<template #dp-input="{ value, onClear }">
				<v-text-field 
					clearable
					prepend-inner-icon="mdi-calendar"
					density="compact"
					class="custom_date_picker_input !cursor-pointer"
					hide-details="auto"
					:model-value="value"
					:error-messages="v$.$errors.map(m => m.$message)"
					:label="$t('common.date_range')"
					variant="plain"
					readonly
					@click:clear="onClear" />
			</template>
		</date-picker>
	</div>
</template>

<script>
import { useVuelidate } from '@vuelidate/core';
import { required } from '@/utils/i18n-validators';

export default {
	props: {
		inputData: {
			type: Object,
			required: true,
		},
		minDate: {
			type: String,
			required: true,
		},
		maxDate: {
			type: String,
			required: true,
		},
		defaultDate: {
			type: String,
			required: true,
		},
	},
	emits: ['update:inputData'],
	setup(){
		const v$ = useVuelidate();
		return { v$ };
	},
	data(){
		return {
		};
	},
	validations(){
		return {
			inputData: {
				start_date: { required },
			},
		};
	},
	computed: {
		selectedDateRange: {
			get(){
				return [this.inputData['start_date'], this.inputData['end_date']];
			},
			set(newVal){
				this.$emit('update:inputData', {
					'start_date': newVal && newVal[0] ? newVal[0].toISOString().substring(0, 10) : '',
					'end_date': newVal && newVal[1] ? newVal[1].toISOString().substring(0, 10) : ''
				});
			}
		}
	}
};
</script>

<style
	scoped>

.custom_date_picker_input :deep(.v-field__input){
	cursor: pointer;
}

.custom_date_picker{
	width: 300px;
}

.custom_date_picker_input :deep(.v-field__prepend-inner){
	align-items: flex-start;
}

.custom_date_picker_input :deep(.v-field--dirty .v-field__prepend-inner){
	align-items: center;
}

</style>