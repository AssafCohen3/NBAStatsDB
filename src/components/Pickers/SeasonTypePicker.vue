<template>
	<div>
		<v-select
			v-model="selectedSeason"
			class="w-[200px]"
			variant="plain"
			item-value="code"
			item-title="name"
			:label="$t('common.season_type')"
			:items="seasonTypes"
			:error-messages="v$.$errors.map(m => m.$message)"
			return-object
			hide-details="auto" />
	</div>
</template>

<script>

import {SeasonTypes} from '../../consts';
import { useVuelidate } from '@vuelidate/core';
import { required } from '@/utils/i18n-validators';

export default {
	props: {
		inputData: {
			type: Object,
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
			seasonTypes: SeasonTypes
		};
	},
	validations(){
		return {
			selectedSeason: { required },
		};
	},
	computed: {
		selectedSeason: {
			get(){
				return this.inputData['season_type_code'];
			},
			set(newVal){
				this.$emit('update:inputData', {
					'season_type_code': newVal.code
				});
			}
		}
	}
};
</script>

<style>

</style>