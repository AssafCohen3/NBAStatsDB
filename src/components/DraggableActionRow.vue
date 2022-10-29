<template>
	<div>
		<div
			class="not-cloned">
			<div
				class="action-row flex items-center p-[20px] my-[4px] rounded-sm cursor-pointer">
				<div
					class="font-bold text-[16px] text-primary-light">
					{{ action.action_title }}
				</div>
			</div>
		</div>
		<div
			class="cloned my-[4px] rounded-sm cursor-pointer min-h-[100px] action-row text-center 
			flex items-center justify-center">
			<p
				class="text-center text-dimmed-white">
				{{ $t('common.drop_to_copy') }}
			</p>
		</div>
	</div>
</template>

<script>
export default {
	props: {
		action: {
			type: Object,
			required: true,
		},
	},
};
</script>

<style
	lang="postcss"
	scoped>
.action-row{
	background-color: #0000004d;
}

.action-row:hover{
	background-color: #0000006d;
}

.cloned{
	display: none;
	outline-width: 5px;
	outline-offset: -15px;
	outline-style: dashed;
	outline-color: theme('colors.dimmed-white');

}

.presets-div .in-other-list.sortable-ghost .cloned{
	display: flex;
}

.presets-div .in-other-list.sortable-ghost .not-cloned{
	display: none;
}
</style>