<template>
	<v-navigation-drawer
		class="bg-[#340444]"
		app
		dark
		permanent>
		<img
			class="h-[80px] w-full object-contain mt-[10px]"
			src="images/logo.png">
		<v-divider />
		<!-- home -->
		<v-list-item
			link
			no-action
			exact
			:to="{name: 'main'}"
			class="w-full mt-[20px]">
			<v-list-item-icon
				class="pe-2">
				mdi-home
			</v-list-item-icon>
			<v-list-item-title>
				{{ $t('generic.home') }}
			</v-list-item-title>
		</v-list-item>
		<v-list-item
			link
			no-action
			exact
			class="w-full">
			<v-list-item-icon
				class="pe-2">
				mdi-database-cog
			</v-list-item-icon>
			<v-list-item-title>
				{{ $t('generic.resources') }}
			</v-list-item-title>
		</v-list-item>
	</v-navigation-drawer>
</template>

<script>

export default {
	computed: {
	}
};
</script>

<style scoped>
.v-locale--is-rtl .v-navigation-drawer--start{
	left: auto !important;
	right: 0 !important;
}
.v-list-item-icon{
	margin-inline-end: 0 !important;
	margin-inline-start: 0 !important
}
.v-list-item .v-list-item-title{
	font-weight: 700;
	letter-spacing: 0;
	font-size: 20px;
	z-index: 1000;
}
a.v-list-item--active *{
	font-weight: bold !important;
}
a {
	text-decoration: none;
}

.v-list-item--variant-text >>> .v-list-item__overlay{
	background-color: #712c72 !important;
}

.v-list-item:hover >>> .v-list-item__overlay{
	opacity: 0.2 !important;
}
.v-list-item--active >>> .v-list-item__overlay{
	opacity: 0.35 !important;
}
.v-list-item{
	color: #dad9e9 !important;
}
</style>