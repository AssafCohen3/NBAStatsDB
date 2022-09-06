<template>
	<v-app-bar
		app
		class="flex justify-items-stretch myappbar"
		color="transparent"
		elevation="0">
		<v-spacer />
		<v-menu
			location="bottom"
			:close-on-content-click="false">
			<template 
				#activator="{ props }">
				<v-btn
					v-if="currentTasks.length > 0"
					stacked
					v-bind="props">
					<v-badge 
						color="error"
						label="common.never"
						:content="currentTasks.length">
						<v-icon
							color="white"
							size="x-large">
							mdi-download
						</v-icon>
					</v-badge>
				</v-btn>
				<v-btn
					v-else
					color="white"
					size="x-large"
					icon="mdi-download"
					v-bind="props" />
			</template>
			<tasks-menu
				:tasks="currentTasks"
				@pause-task="pauseTask"
				@resume-task="resumeTask"
				@dismiss-task="dismissTask"
				@cancel-task="cancelTask" />
		</v-menu>
		<v-btn
			color="white"
			size="x-large"
			icon="mdi-message-text-outline" />
		<locale-selector
			class="pe-8" />
	</v-app-bar>
</template>

<script>
import { mapActions, mapGetters } from 'vuex';
import LocaleSelector from './LocaleSelector.vue';
import TasksMenu from './TasksMenu.vue';

export default {
	components: { LocaleSelector, TasksMenu, },
	computed: {
		...mapGetters('tasks', ['currentTasks']),
	},
	methods: {
		...mapActions('tasks', {
			fetchTasksAction: 'fetchTasks',
			pauseTaskAction: 'pauseTask',
			resumeTaskAction: 'resumeTask',
			dismissTaskAction: 'dismissTask',
			cancelTaskAction: 'cancelTask',
		}),
		pauseTask(taskId){
			this.pauseTaskAction([taskId]);
		},
		resumeTask(taskId){
			this.resumeTaskAction([taskId]);
		},
		dismissTask(taskId){
			this.dismissTaskAction([taskId]);
		},
		cancelTask(taskId){
			this.cancelTaskAction([taskId]);
		},
	},
	onLocaleChange(){
		this.fetchTasksAction();
	}
};
</script>

<style>
</style>
