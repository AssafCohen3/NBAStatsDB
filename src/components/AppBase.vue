<template>
	<v-app>
		<side-menu  />
		<app-header />
		<v-main
			class="bg-[#7092be4d]">
			<v-container
				fluid
				class="!p-[24px]">
				<router-view />
			</v-container>
		</v-main>
	</v-app>

</template>

<script>
import AppHeader from './AppHeader.vue';
import SideMenu from './SideMenu.vue';
export default {
	components: { SideMenu, AppHeader },

};
</script>

<style>
</style>