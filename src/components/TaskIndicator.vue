<template>
	<div
		class="task_indicator select-none"
		:class="{
			active_task: task.status == 'active',
			intermediate_task: task.to_finish == null
		}">
		<div
			class="flex flex-row items-center">
			<!-- task icon -->
			<v-icon
				:color="taskIconColor"
				size="x-large">
				{{ taskIcon }}
			</v-icon>
			<!-- main content -->
			<div
				class="px-[20px] w-full">
				<div
					class="text-dimmed-white font-bold">
					{{ task.resource_name }}
				</div>
				<div
					class="text-dimmed-white font-bold">
					{{ task.action_title }}
				</div>
				<div
					class="text-dimmed-white">
					{{ taskMiniText }}
				</div>
				<div
					v-if="showProgressBar">
					<div
						class="flex flex-row items-center">
						<div
							class="pe-4 w-full">
							<v-progress-linear 
								:model-value="task.to_finish !== null ? task.completed*100.0 / task.to_finish : 0"
								color="green"
								:indeterminate="task.to_finish === null" />
						</div>
						<v-btn
							v-if="task.status == 'active'"
							icon="mdi-pause"
							color="white"
							size="x-small"
							@click="$emit('pauseTask')" />
						<v-btn
							v-else-if="task.status == 'paused'"
							icon="mdi-play"
							color="white"
							size="x-small"
							@click="$emit('resumeTask')" />
						<v-btn
							icon="mdi-close"
							color="white"
							size="x-small"
							@click="$emit('cancelTask')" />
					</div>
					<div
						class="text-dimmed-white text-[14px]">
						<span
							v-if="task.to_finish !== null">
							{{ $t('tasks.progress_line', task) }}
						</span>
						<span
							v-else>
							{{ $t('tasks.progress_line_no_to_finish', task) }}
						</span>
					</div>					
				</div>
			</div>
			<v-spacer />
			<v-btn
				v-if="canDismiss"
				icon="mdi-delete-forever"
				color="white"
				@click="$emit('dismissTask')" />
		</div>
	</div>
</template>

<script>
export default {
	props: {
		task: {
			type: Object,
			required: true,
		}
	},
	emits: [
		'pauseTask',
		'resumeTask',
		'cancelTask',
		'dismissTask',
	],
	computed: {
		taskIcon(){
			switch(this.task.status){
			case 'active':
				return 'mdi-progress-download';
			case 'paused':
				return 'mdi-motion-pause-outline';
			case 'error':
				return 'mdi-progress-alert';
			case 'cancelled':
				return 'mdi-progress-close';
			case 'finished':
				return 'mdi-progress-check';
			default:
				return 'mdi-progress-question';
			}
		},
		taskIconColor(){
			switch(this.task.status){
			case 'active':
				return 'blue';
			case 'paused':
				return 'orange';
			case 'error':
				return 'red';
			case 'cancelled':
				return 'red';
			case 'finished':
				return 'green';
			default:
				return 'blue';
			}
		},
		taskMiniText(){
			switch(this.task.status){
			case 'active':
				return this.task.mini_title;
			case 'paused':
				return this.task.mini_title;
			case 'error':
				return this.$t('tasks.error_occurred');
			case 'cancelled':
				return this.$t('tasks.task_cancelled');
			case 'finished':
				return this.$t('tasks.task_finished');
			default:
				return this.task.mini_title;
			}
		},
		showProgressBar(){
			return ['active', 'paused'].includes(this.task.status);
		},
		canDismiss(){
			return ['error', 'cancelled', 'finished'].includes(this.task.status);
		}
	},
};
</script>

<style
	lang="postcss"
	scoped>

.task_indicator{
	padding-inline: 20px;
	padding-top: 10px;
	padding-bottom: 5px;
	cursor: pointer;
}
.task_indicator:first-child{
	border-top-left-radius: inherit;
	border-top-right-radius: inherit;
}

.task_indicator:last-child{
	border-bottom-left-radius: inherit;
	border-bottom-right-radius: inherit;
}
.task_indicator:not(:last-child){
	border-bottom-width: 1px;
	border-bottom-style: solid;
}
.task_indicator:hover{
	background-color: #21043c;
}

.task_indicator.active_task:not(.intermediate_task) :deep(.v-progress-linear:after){
    animation: progress-bar-shine 2s infinite;
    background: linear-gradient(90deg, white 0%, white 5%, transparent 5%, transparent 100%);
	opacity: 0.5;
    border-radius: 10px;
    content:'';
    height: 100%;
    position: absolute;
    transform:translateX(0);
    width: 100%;
}
@keyframes progress-bar-shine {
    to {
      transform:translateX(100%);
    }
}
</style>