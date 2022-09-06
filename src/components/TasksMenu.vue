<template>
	<div
		class="task_menu_container bg-[#0e0730] rounded-[20px] min-w-[500px] shadow-2xl drop-shadow"
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
				@cancel-task="$emit('cancelTask', task.task_id)" 
				@dismiss-task="$emit('dismissTask', task.task_id)" 
				@resume-task="$emit('resumeTask', task.task_id)" 
				@pause-task="$emit('pauseTask', task.task_id)" 
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

};
</script>

<style
	scoped
	lang="postcss">

/* .task_menu_container{
	position: absolute;
	align-self: center;
} */
</style>