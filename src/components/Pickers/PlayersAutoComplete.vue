<template>
	<div
		class="w-[400px]">
		<v-autocomplete
			v-model="selectedPlayerComp"
			v-model:search="search"
			:items="suggestions"
			:loading="isLoadingSuggestions"
			no-filter
			return-object
			variant="underlined"
			prepend-icon="mdi-account-search"
			:item-title="getPlayerTitle"
			item-value="player_id"
			hide-no-data
			:menu-props="{
				contentClass: 'players-autocomplete-select-menu'
			}"
			clearable
			hide-selected
			hide-details="auto"
			:error-messages="v$.$errors.map(m => m.$message)"
			:label="$t('common.player')" />
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
			selectedPlayer: null,
		};
	},
	validations(){
		return {
			inputData: {
				player_id: { required },
			},
		};
	},
	computed: {
		selectedPlayerComp: {
			get(){
				return this.selectedPlayer;
			},
			set(newVal){
				this.selectedPlayer = newVal;
				this.$emit('update:inputData', {
					'player_id': newVal ? newVal.player_id : '',
				});
			}
		}
	},
	watch: {
		search: {
			handler(newVal){
				if(newVal.length >= 3 && !this.isLoadingSuggestions){
					this.isLoadingSuggestions = true;
					this.searchPlayers([newVal]).
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
		...mapActions('suggestions', ['searchPlayers']),
		getPlayerTitle(player){
			return `${player.player_name}(${player.first_season}-${player.last_season})`;
		}
	},
};
</script>

<style
	scoped>


</style>