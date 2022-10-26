<template>
	<div
		class="preset-div">
		<div
			class="flex items-center">
			<v-btn
				variant="plain"
				:icon="expanded ? 'mdi-chevron-up' : 'mdi-chevron-down'"
				color="primary-light"
				elevation="0"
				@click="expanded = !expanded" />
			<v-hover v-slot="{isHovering, props}">
				<div
					class="flex items-center w-full"
					v-bind="props">
					<div
						class="text-primary-light font-bold text-[24px] select-none">
						{{ preset.preset_name }}
					</div>
					<v-fade-transition>
						<v-btn
							v-show="isHovering"
							class="mx-[5px]"
							variant="plain"
							icon="mdi-pencil"
							color="primary-light" />
					</v-fade-transition>
				</div>
			</v-hover>
		</div>
		<!-- <v-expand-transition>
			<div v-show="expanded">
				<action-recipe-row
					v-for="actionRecipe in preset.action_recipes"
					:key="actionRecipe."
			</div>
		</v-expand-transition> -->
	</div>
</template>

<script>
// import ActionRecipeRow from './ActionRecipeRow.vue';
export default {
	// components: { ActionRecipeRow },
	props: {
		preset: {
			type: Object,
			required: true,
		},
	},
	data(){
		return {
			expanded: false,
		};
	},
};
</script>

<style
	lang="postcss"
	scoped>
.preset-div{
	background: linear-gradient(45deg, #13138f, #2b356880);
	/* w-[30%] p-[30px] m-[10px] rounded-lg */
	width: 50%;
	padding: 5px;
	margin: 30px;
	border-radius: 10px;
	box-shadow: 0px 0px 10px 3px #131434;
}
</style>