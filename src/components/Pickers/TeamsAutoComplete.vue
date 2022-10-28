<template>
	<div
		class="w-[400px]">
		<v-autocomplete
			v-model="selectedTeamComp"
			v-model:search="search"
			:items="suggestions"
			:loading="isLoadingSuggestions"
			no-filter
			return-object
			variant="underlined"
			prepend-icon="mdi-account-search"
			:item-title="getTeamTitle"
			item-value="team_id"
			hide-no-data
			:menu-props="{
				contentClass: 'autocomplete-select-menu'
			}"
			clearable
			hide-selected
			hide-details="auto"
			:error-messages="v$.$errors.map(m => m.$message)"
			:label="$t('common.team')" />
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
			search: '',
			suggestions: [],
			isLoadingSuggestions: false,
			selectedTeam: null,
		};
	},
	validations(){
		return {
			inputData: {
				team_id: { required },
			},
		};
	},
	computed: {
		selectedTeamComp: {
			get(){
				return this.selectedTeam;
			},
			set(newVal){
				this.selectedTeam = newVal;
				this.$emit('update:inputData', {
					'team_id': newVal ? `${newVal.team_id}` : '',
				});
			}
		}
	},
	watch: {
		search: {
			handler(newVal){
				if(newVal.length >= 3 && !this.isLoadingSuggestions){
					this.isLoadingSuggestions = true;
					this.searchTeams([newVal]).
						then(resp => {
							this.suggestions = resp;
							this.isLoadingSuggestions = false;
						});
				}
			},
			immediate: true,
		}
	},
	methods: {
		...mapActions('suggestions', ['searchTeams']),
		getTeamTitle(team){
			return `${team.team_name}(${team.first_season}-${team.last_season})`;
		}
	},
};
</script>

<style
	scoped>


</style>