<template>
	<v-app>
		<side-menu  />
		<app-header />
		<v-main>
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


.v-main{
	/* background-image: linear-gradient(135deg, #242b52, #150d45); */
	background: 
		repeating-linear-gradient(
			135deg,
			transparent,
			#2117640a 50px,
			transparent 10px,
			transparent 20%
			),
		linear-gradient(135deg, #2a1f6d 0%, #150d45 50%);
	background-repeat: no-repeat;
	background-attachment: fixed;
}


.v-navigation-drawer{
	box-shadow: 0px 0px 20px 1px #3e4795 !important;
}

/* TODO check when this fixed on update */
.v-locale--is-rtl .v-main{
	background: 
		repeating-linear-gradient(
			135deg,
			transparent,
			#2117640a 50px,
			transparent 10px,
			transparent 20%
			),
		linear-gradient(45deg, #150d45 50%, #2a1f6d 100%);
	background-repeat: no-repeat;
	background-attachment: fixed;
}

.v-locale--is-rtl .v-navigation-drawer--start{
	left: auto !important;
	right: 0 !important;
}

</style>