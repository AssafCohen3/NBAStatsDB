<template>
	<v-app>
		<template
			v-if="!connectedToServer || !dbStatus || !dbStatus.status">
			<div
				class="flex h-full w-full justify-center items-center">
				<v-progress-circular
					class="text-primary-light"
					indeterminate />
			</div>
		</template>
		<template
			v-else-if="connectedToServer && dbStatus && dbStatus.status && dbStatus.status == 'ok'">
			<side-menu  />
			<app-header />
			<v-main>
				<v-container
					fluid
					class="!p-[24px]">
					<router-view />
				</v-container>
			</v-main>
		</template>
		<template
			v-else>
			<v-dialog
				v-model="initDialogOpen"
				persistent>
				<init-db-dialog
					@initDB="initDatabase" />
			</v-dialog>
			<!-- refresh db modal -->
		</template>
	</v-app>

</template>

<script>
import AppHeader from './AppHeader.vue';
import SideMenu from './SideMenu.vue';
import io from 'socket.io-client';
import axios from 'axios';
import { mapActions, mapGetters } from 'vuex';
import InitDbDialog from './InitDBDialog.vue';

export default {
	components: { SideMenu, AppHeader, InitDbDialog },
	data(){
		return {
			connectedToServer: false,
			initDialogOpen: true,
		};
	},
	computed: {
		...mapGetters('db', {
			dbStatus: 'dbStatus',
			initializingDB: 'initializingDB',
		}),
	},
	mounted(){
		this.connectToServer();
	},
	methods: {
		...mapActions('db', {
			initDB: 'initDB',
		}),
		connectToServer(){
			let appUrl = axios.defaults.baseURL;
			var socket = io.connect(appUrl);
			socket.on('connect', () => {
				console.log('connected to server!');
				this.connectedToServer = true; 
				this.firstInitialTry();
				socket.emit('first-connect','A user has connected');
			});
			socket.on('refresh-data', function(){
				console.log('to refresh data');
			});
			socket.on('add-message', function(msg){
				console.log('request to add message', msg);
			});
		},
		firstInitialTry(){
			this.initDatabase(null, false);
		},
		initDatabase(dbName, createDB){
			let currentDBName = dbName;
			if(dbName === null){
				currentDBName = localStorage.getItem('dbName') || 'NBAStatsDB.db';
			}
			this.initDB([currentDBName, createDB]);
		}
	}
};
</script>

<style
	lang="postcss">
.v-application{
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

/* .v-locale--is-rtl .v-navigation-drawer--start{
	left: auto !important;
	right: 0 !important;
} */

.app-section{
	@apply bg-section-bg rounded-lg	
}

.local-changer-select-menu .v-list{
	@apply !bg-section-bg
}
.normal-flag{
	margin: 0 !important
}

</style>