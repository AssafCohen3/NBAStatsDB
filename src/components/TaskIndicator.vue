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
			<v-progress-circular
				v-if="isLoading"
				:color="taskIconColor"
				size="30"
				indeterminate />
			<template
				v-else-if="hasError">
				<v-tooltip
					:text="$t('common.show_error')">
					<template #activator="{props}">
						<v-badge
							v-if="isRecoverMode"
							v-bind="props"
							class="error-badge cursor-pointer"
							icon="mdi-alert-circle"
							color="transparent"
							@click="errorClick">
							<v-icon
								:color="taskIconColor"
								size="x-large">
								{{ taskIcon }}
							</v-icon>
						</v-badge>
						<v-icon
							v-else
							v-bind="props"
							:color="taskIconColor"
							class="cursor-pointer"
							size="x-large"
							@click="errorClick">
							{{ taskIcon }}
						</v-icon>
					</template>
				</v-tooltip>
			</template>
			<v-icon
				v-else
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
		<v-dialog
			v-if="hasError"
			v-model="isErrorModalOpen">
			<error-modal
				:error="task.exception" />
		</v-dialog>
	</div>
</template>

<script>
import ErrorModal from './ErrorModal.vue';
import TransitionHeight from './TransitionHeight.vue';

export default {
	components: {
		TransitionHeight,
		ErrorModal, 
	},
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
			isErrorModalOpen: false,
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
			case 'pending':
				return 'mdi-timer-outline';
			case 'initiating':
				return 'mdi-loading';
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
			case 'pending':
				return 'blue';
			case 'initiating':
				return 'blue';
			default:
				return 'blue';
			}
		},
		taskMiniText(){
			if(this.isRecoverMode){
				return this.recoverText;
			}
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
			case 'pending':
				return this.$t('tasks.waiting_for_execution');
			case 'initiating':
				return this.$t('tasks.loading');
			default:
				return this.task.mini_title;
			}
		},
		showProgressBar(){
			return ['active', 'initiating', 'paused'].includes(this.task.status);
		},
		isLoading(){
			return ['active', 'initiating'].includes(this.task.status);
		},
		canDismiss(){
			return ['error', 'cancelled', 'finished'].includes(this.task.status);
		},
		isRecoverMode(){
			return !!this.task.retry_status;
		},
		hasError(){
			return !!this.task.exception;
		},
		recoverText(){
			if(this.isRecoverMode){
				let toRet = this.task.mini_title;
				if(this.task.retry_status.is_last_retry){
					toRet += ' ' + this.$t('tasks.you_can_try_to_resume');
				}
				else{
					let timestamp = this.task.retry_status.timestamp + this.task.retry_status.seconds_to_wait;
					let formattedDueTime = this.$moment.unix(timestamp).format('HH:mm');
					toRet += ' ' + this.$t('tasks.auto_retrying_in', {time: formattedDueTime});
				}
				return toRet;
			}
			return '';
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
		errorClick(){
			this.isErrorModalOpen = true;
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

.v-badge.error-badge :deep(.v-badge__badge .v-icon){
	color: red;
	font-size: 25px;
	background: white;
	border-radius: 10000px;
	clip-path: circle(38% at 50% 50%);
}

</style>