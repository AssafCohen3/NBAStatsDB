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
			<side-menu />
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
					@init-db="initDatabase" />
			</v-dialog>
			<!-- refresh db modal -->
		</template>
	</v-app>
</template>

<script>
import AppHeader from './AppHeader.vue';
import SideMenu from './SideMenu.vue';
import axios from 'axios';
import { mapActions, mapGetters, mapMutations } from 'vuex';
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
		...mapMutations('tasks', ['updateTask', 'refreshResources']),
		connectToServer(){
			let appUrl = axios.defaults.baseURL;
			let source = new EventSource(appUrl + '/tasks/listen');
			source.addEventListener('open', () => {
				console.log('connected to server!');
				this.connectedToServer = true; 
				this.firstInitialTry();
			});
			source.addEventListener('task-update-start', (event) => {
				let taskData = JSON.parse(event.data);
				this.updateTask([taskData.task_path, taskData.task_message]);
			});
			source.addEventListener('task-update-finish', (event) => {
				let taskData = JSON.parse(event.data);
				this.updateTask([taskData.task_path, taskData.task_message]);
			});
			source.addEventListener('task-update-sub-finish', (event) => {
				let taskData = JSON.parse(event.data);
				this.updateTask([taskData.task_path, taskData.task_message]);
			});
			source.addEventListener('task-update-paused', (event) => {
				let taskData = JSON.parse(event.data);
				this.updateTask([taskData.task_path, taskData.task_message]);
			});
			source.addEventListener('task-update-resume', (event) => {
				let taskData = JSON.parse(event.data);
				this.updateTask([taskData.task_path, taskData.task_message]);
			});
			source.addEventListener('task-update-error', (event) => {
				let taskData = JSON.parse(event.data);
				console.error(taskData.task_message.mini_title);
				this.updateTask([taskData.task_path, taskData.task_message]);
			});
			source.addEventListener('task-update-cancel', (event) => {
				let taskData = JSON.parse(event.data);
				this.updateTask([taskData.task_path, taskData.task_message]);
			});
			source.addEventListener('refresh-resources', (event) => {
				let resourcesIdsToRefresh = JSON.parse(event.data);
				this.refreshResources(resourcesIdsToRefresh);
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

.app-section{
	@apply bg-section-bg rounded-lg	
}

.local-changer-select-menu .v-list{
	background-color: #1c1947 !important;
}
.normal-flag{
	margin: 0 !important
}

.autocomplete-select-menu .v-list{
	background-color: #1c1947 !important;
}
.autocomplete-select-menu .v-list .v-list-item .v-list-item-title{
	@apply text-primary-light !font-bold
}





</style>