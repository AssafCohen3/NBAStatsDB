<template>
	<v-navigation-drawer
		class="bg-[#0e0730]"
		app
		dark
		permanent>
		<img
			class="h-[160px] w-full object-contain mt-[10px]"
			src="images/logo.png">
		<v-divider />
		<!-- home -->
		<v-list-item
			link
			no-action
			exact
			:to="{name: 'home'}"
			prepend-icon="mdi-home"
			:title="$t('generic.home')" />
		<v-list-item
			link
			no-action
			exact
			:to="{name: 'presets-page'}"
			prepend-icon="mdi-script-text-outline"
			:title="$t('generic.presets')" />
		<v-list
			v-model:opened="open"
			bg-color="transparent">
			<v-list-group
				value="resources">
				<template #activator="{props}">
					<v-list-item
						v-bind="props"
						prepend-icon="mdi-database-cog"
						:title="$t('generic.resources')" />
				</template>
				<v-list-item
					v-for="resource, index in resources"
					:key="index"
					:title="resource.resource_name"
					exact
					:to="{name: 'resource-page', params: {
						resourceId: resource.resource_id
					}}"
					link />
			</v-list-group>
		</v-list>
		<v-list-item
			no-action
			prepend-icon="mdi-help-circle"
			:title="$t('common.help')"
			@click="openHelp" />		
		<template #append>
			<div
				class="py-[50px] flex flex-col items-center justify-center">
				<v-btn
					class="!text-[40px] text-primary-light"
					variant="plain"
					icon="mdi-github"
					@click="openGithub" />
				<div
					class="pt-[20px] font-bold text-dimmed-white">
					{{ `NBAStatsDB` }}
				</div>
			</div>
		</template>
	</v-navigation-drawer>
</template>

<script>
import { mapActions, mapGetters } from 'vuex';

export default {
	data: () => ({
		open: [],
	}),
	computed: {
		...mapGetters({
			resources: 'resources/resources',
			fetchingResources: 'resources/fetchingResources'
		}),
	},
	mounted(){
		this.fetchResources();
	},
	methods: {
		...mapActions('resources', ['fetchResources']),
		resourceClicked(resource){
			this.$router.push({
				name: 'resource-page',
				params: {
					resourceId: resource.resourceId
				},
			});
		},
		openHelp(){
			window.open('https://github.com/AssafCohen3/NBAStatsDB/wiki', '_blank');
		},
		openGithub(){
			window.open('https://github.com/AssafCohen3/NBAStatsDB', '_blank');
		}
	},
	onLocaleChange(){
		this.fetchResources();
	}
};
</script>

<style scoped>

.v-list-item--active :deep(.v-list-item-title){
	font-weight: 500;
	z-index: 1000;
}

.v-list-item :deep(.v-list-item__overlay){
	background-color: #120d3a !important;
	z-index: 0;
}

.v-list-item :deep(.v-list-item__content) {
	z-index: 1;
}

.v-list-item--active :deep(.v-list-item__overlay){
	opacity: 1.0 !important;
}

.v-list-item:hover :deep(.v-list-item__overlay){
	opacity: 0.8 !important;
}


.v-list-item:not(.v-list-item--active) :deep(.v-list-item-icon), 
.v-list-item:not(.v-list-item--active) :deep(.v-list-item-title){
	opacity: 0.35 !important;
}


.v-list-item{
	color: #d9e1ff !important;
}


</style>

<style>
.v-navigation-drawer{
	overflow-y: auto;
}

.v-navigation-drawer__content{
	overflow-x: unset;
	overflow-y: unset;
	height: unset;
}
</style>