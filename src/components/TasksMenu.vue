<template>
	<div
		class="task_menu_container bg-[#0e0730] rounded-[20px] w-[500px] shadow-2xl drop-shadow border-radius-[20px] border-[1px] border-solid border-primary-light"
		elevation="20">
		<div
			class="text-primary-light font-bold text-[20px] text-center p-[20px]">
			{{ $t('common.tasks') }}
		</div>
		<template
			v-if="tasks.length > 0">
			<task-indicator
				v-for="task in tasks"
				:key="task.task_id"
				:task="task"
				@cancel-task="cancelTask" 
				@dismiss-task="dismissTask" 
				@resume-task="resumeTask" 
				@pause-task="pauseTask" 
			/>
		</template>
	</div>  
</template>

<script>
import TaskIndicator from './TaskIndicator.vue';
export default {
	components: { TaskIndicator },
	props: {
		tasks: {
			type: Array,
			required: true
		},
	},
	emits: [
		'pauseTask',
		'resumeTask',
		'cancelTask',
		'dismissTask',
	],
	methods: {
		pauseTask(taskPath){
			this.$emit('pauseTask', taskPath);
		},
		resumeTask(taskPath){
			this.$emit('resumeTask', taskPath);
		},
		cancelTask(taskPath){
			this.$emit('cancelTask', taskPath);
		},
		dismissTask(taskPath){
			this.$emit('dismissTask', taskPath);
		},
	}

};
</script>

<style
	scoped
	lang="postcss">

.task_menu_container{
	overflow: auto;
}
</style>