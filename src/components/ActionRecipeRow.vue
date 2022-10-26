<template>
	<div>
		{{ actionRecipe.resource_name }} - {{ actionRecipe.action_title }}
	</div>
</template>

<script>
export default {
	props: {
		actionRecipe: {
			type: Object,
			required: true,
		},
	},
};
</script>

<style>

</style>