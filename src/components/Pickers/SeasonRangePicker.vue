<template>
	<div
		class="custom_date_picker">
		<date-picker 
			v-model="selectedYearRange" 
			range
			year-picker
			format="yyyy"
			dark
			:year-range="[minSeason, maxSeason]"
			:enable-time-picker="false"
			:ignore-time-validation="true"
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
					:label="$t('common.seasons_range')"
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
		minSeason: {
			type: Number,
			required: true,
		},
		maxSeason: {
			type: Number,
			required: true,
		},
		defaultSeason: {
			type: Number,
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
				start_season: { required },
			},
		};
	},
	computed: {
		selectedYearRange: {
			get(){
				return [this.inputData['start_season'], this.inputData['end_season']];
			},
			set(newVal){
				console.log(newVal);
				let startSeason = newVal && newVal[0] ? `${newVal[0]}` : null;
				let endSeason = newVal && newVal[1] ? `${newVal[1]}` : startSeason;
				this.$emit('update:inputData', {
					'start_season': startSeason,
					'end_season': endSeason
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