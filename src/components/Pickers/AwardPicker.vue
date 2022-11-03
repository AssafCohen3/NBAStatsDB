<template>
	<div>
		<v-select
			v-model="selectedAward"
			class="w-[200px]"
			variant="plain"
			item-value="award_id"
			item-title="award_name"
			:label="$t('common.award')"
			:items="awards"
			:error-messages="v$.$errors.map(m => m.$message)"
			return-object
			hide-details="auto" />
	</div>
</template>

<script>

import { useVuelidate } from '@vuelidate/core';
import { required } from '@/utils/i18n-validators';
import { mapActions } from 'vuex';

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
			awards: [],
		};
	},
	validations(){
		return {
			selectedAward: { required },
		};
	},
	computed: {
		selectedAward: {
			get(){
				return this.inputData['award_id'];
			},
			set(newVal){
				this.$emit('update:inputData', {
					'award_id': newVal.award_id
				});
			}
		}
	},
	mounted(){
		this.getAwards()
			.then(awards => {
				this.awards = awards;
			});
	},
	methods: {
		...mapActions('suggestions', ['getAwards']),
	},
};
</script>

<style>

</style>