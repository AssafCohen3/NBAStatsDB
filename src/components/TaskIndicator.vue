<template>
	<div
		class="task_indicator select-none"
		:class="{
			active_task: task.status == 'active',
			intermediate_task: task.to_finish == null
		}">
		<div
			class="task_body flex flex-row items-center">
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
						<v-spacer />
						<v-btn
							v-if="task.status == 'active'"
							icon="mdi-pause"
							color="white"
							size="x-small"
							@click="pauseTask([])" />
						<v-btn
							v-else-if="task.status == 'paused'"
							icon="mdi-play"
							color="white"
							size="x-small"
							@click="resumeTask([])" />
						<v-btn
							icon="mdi-close"
							color="white"
							size="x-small"
							@click="cancelTask([])" />
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
				@click="dismissTask([])" />
		</div>
		<template
			v-if="task.subtasks_messages.length > 0">
			<div
				class="flex justify-center items-center">
				<v-btn
					block
					color="white"
					@click="expanded=!expanded">
					<v-icon
						color="white">
						{{ expanded ? 'mdi-menu-up' : 'mdi-menu-down' }}
					</v-icon>
				</v-btn>
			</div>
			<TransitionHeight>
				<div
					v-if="expanded">
					<task-indicator
						v-for="subTask in task.subtasks_messages"
						:key="subTask.task_id"
						:task="subTask"
						class="child_task"
						@cancel-task="cancelTask" 
						@dismiss-task="dismissTask" 
						@resume-task="resumeTask" 
						@pause-task="pauseTask" 
					/>
				</div>
			</TransitionHeight>
		</template>
	</div>
</template>

<script>
import TransitionHeight from './TransitionHeight.vue';

export default {
	components: {TransitionHeight},
	props: {
		task: {
			type: Object,
			required: true,
		},
	},
	emits: [
		'pauseTask',
		'resumeTask',
		'cancelTask',
		'dismissTask',
	],
	data(){
		return {
			expanded: false,
		};
	},
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
	methods: {
		pauseTask(taskPath=[]){
			this.$emit('pauseTask', [this.task.task_id, ...taskPath]);
		},
		resumeTask(taskPath=[]){
			this.$emit('resumeTask', [this.task.task_id, ...taskPath]);
		},
		cancelTask(taskPath=[]){
			this.$emit('cancelTask', [this.task.task_id, ...taskPath]);
		},
		dismissTask(taskPath=[]){
			this.$emit('dismissTask', [this.task.task_id, ...taskPath]);
		},
	}
};
</script>

<style
	lang="postcss"
	scoped>

.task_body{
	padding-inline: 20px;
	padding-top: 10px;
	padding-bottom: 5px;
	cursor: pointer;
}

.child_task .task_body{
	padding-inline: 40px;
}

.task_indicator:not(.child_task):first-child{
	border-top-left-radius: inherit;
	border-top-right-radius: inherit;
}

.task_indicator:not(.child_task):last-child{
	border-bottom-left-radius: inherit;
	border-bottom-right-radius: inherit;
}
.task_indicator:not(:last-child):not(.child_task){
	border-bottom-width: 1px;
	border-bottom-style: solid;
}
.task_body:hover{
	background-color: #21043c;
}

.task_indicator.active_task:not(.intermediate_task) :deep(> .task_body .v-progress-linear:after){
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