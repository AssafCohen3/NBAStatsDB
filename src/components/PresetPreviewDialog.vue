<template>
	<div
		class="preset-div">
		<div
			class="text-primary-light font-bold text-[24px] select-none py-[10px]">
			{{ preset.preset_name }}
		</div>
		<div
			class="text-dimmed-white font-bold text-[16px] select-none py-[10px]">
			{{ $t('common.presets_preview_explain') }}
		</div>
		<action-recipe-row
			v-for="actionRecipe in preset.action_recipes"
			:key="actionRecipe.action_recipe_id"
			:action-recipe="actionRecipe" />			
		<div
			class="flex items-center py-[20px]">
			<v-btn
				color="primary"
				:loading="dispatchingPreset"
				class="me-5"
				@click="$emit('dispatchPreset', preset)">
				{{ $t('common.run') }}
			</v-btn>
			<v-btn
				color="error"
				:loading="dispatchingPreset"
				@click="$emit('cancel')">
				{{ $t('common.cancel') }}
			</v-btn>
		</div>
	</div>
</template>

<script>
import { mapGetters } from 'vuex';
import ActionRecipeRow from './ActionRecipeRow.vue';

export default {
	components: { ActionRecipeRow, },
	props: {
		preset: {
			type: Object,
			required: true,
		},
	},
	emits: ['cancel', 'dispatchPreset'],
	computed: {
		...mapGetters('presets', ['dispatchingPreset']),
	},
};
</script>

<style
	lang="postcss"
	scoped>

.preset-div{
	background: theme('colors.section-bg-not-transparent');
	padding: 5px;
	width: 80%;
	margin-block: 30px;
	padding-inline: 20px;
	border-radius: 10px;
	margin-inline-start: 5px;
	box-shadow: 0px 0px 10px 3px #131434;
}

</style>