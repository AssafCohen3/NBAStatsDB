import axios from 'axios';
// {
// 	action_title: 'Action A title',
// 	task_id: 55,
// 	mini_text: 'aaaaa',
// 	completed: 100,
// 	to_finish: 200,
// 	status: 'on-progress',
// },
// {
// 	action_title: 'Action B title',
// 	task_id: 56,
// 	mini_text: 'bbbbbbbbaddadasads dassdads sdasad',
// 	completed: 2,
// 	to_finish: 267,
// 	status: 'paused',
// },
// {
// 	action_title: 'Action C title',
// 	task_id: 599,
// 	mini_text: 'saa adsa asdsa sdasad',
// 	completed: 88,
// 	to_finish: 267,
// 	status: 'error',
// },
// {
// 	action_title: 'Action D title',
// 	task_id: 5991,
// 	mini_text: 'saa adsa asdsa sdasad',
// 	completed: 88,
// 	to_finish: 267,
// 	status: 'finished',
// },
// {
// 	action_title: 'Action E title',
// 	task_id: 5992,
// 	mini_text: 'saa adsa asdsa sdasad',
// 	completed: 88,
// 	to_finish: 267,
// 	status: 'cancelled',
// },
// {
// 	action_title: 'Action F title',
// 	task_id: 5995,
// 	mini_text: 'saa adsa asdsa sdasad',
// 	completed: 88,
// 	to_finish: null,
// 	status: 'on-progress',
// },

const state = {
	// tasks
	currentTasks: [],
	// fetch tasks
	isFetchingTasks: false,

	// pause task
	isPausingTask: false,

	// resume task
	isResumingTask: false,

	// cancel task
	isCancellingTask: false,

	// dismiss task
	isDismissingTask: false,
};


const getters = {
	// tasks
	currentTasks: (state) => state.currentTasks,

	// fetch tasks
	isFetchingTasks: (state) => state.isFetchingTasks,

	// pause task
	isPausingTask: (state) => state.isPausingTask,

	// resume task
	isResumingTask: (state) => state.isResumingTask,

	// cancel task
	isCancellingTask: (state) => state.isCancellingTask,

	// dismiss task
	isDismissingTask: (state) => state.isDismissingTask,
};

const actions = {
	fetchTasks({commit}){
		return new Promise((resolve, reject) => {
			commit('fetchTasksStart');
			axios.get('/tasks')
				.then(resp => {
					commit('fetchTasksSuccess', resp);
					resolve(resp.data);
				});
		});
	},
	pauseTask({commit}, [taskId]){
		return new Promise((resolve, reject) => {
			commit('pauseTaskStart');
			axios.post('/tasks/pause_task',
				{
					task_id: taskId
				})
				.then(resp => {
					commit('pauseTaskSuccess', resp);
					resolve(resp.data);
				});
		});
	},
	resumeTask({commit}, [taskId]){
		return new Promise((resolve, reject) => {
			commit('resumeTaskStart');
			axios.post('/tasks/resume_task',
				{
					task_id: taskId
				})
				.then(resp => {
					commit('resumeTaskSuccess', resp);
					resolve(resp.data);
				});
		});
	},
	cancelTask({commit}, [taskId]){
		return new Promise((resolve, reject) => {
			commit('cancelTaskStart');
			axios.post('/tasks/cancel_task',
				{
					task_id: taskId
				})
				.then(resp => {
					commit('cancelTaskSuccess', resp);
					resolve(resp.data);
				});
		});
	},
	dismissTask({commit}, [taskId]){
		return new Promise((resolve, reject) => {
			commit('dismissTaskStart');
			axios.post('/tasks/dismiss_task',
				{
					task_id: taskId
				})
				.then(resp => {
					commit('dismissTaskSuccess', [resp, taskId]);
					resolve(resp.data);
				});
		});
	},

};

const mutations = {
	updateTask(state, taskToUpdate){
		let currentTask = state.currentTasks.find(t => t.task_id === taskToUpdate.task_id);
		console.log(taskToUpdate);
		if(currentTask === undefined){
			state.currentTasks.push(taskToUpdate);
		}
		else{
			Object.assign(currentTask, taskToUpdate);
		}
	},

	fetchTasksStart(state){
		state.isFetchingTasks = true;
	},
	fetchTasksSuccess(state, resp){
		state.isFetchingTasks = false;
		state.currentTasks = resp.data;
	},
	// pause task
	pauseTaskStart(state){
		state.isPausingTask = true;
	},
	pauseTaskSuccess(state){
		state.isPausingTask = false;
	},
	// resume task
	resumeTaskStart(state){
		state.isResumingTask = true;
	},
	resumeTaskSuccess(state){
		state.isResumingTask = false;
	},
	// cancel task
	cancelTaskStart(state){
		state.isCancellingTask = true;
	},
	cancelTaskSuccess(state){
		state.isCancellingTask = false;
	},
	// dismiss task
	dismissTaskStart(state){
		state.isDismissingTask = true;
	},
	dismissTaskSuccess(state, [resp, taskId]){
		let taskIndex = state.currentTasks.findIndex(t => t.task_id == taskId);
		if(taskIndex != -1){
			state.currentTasks.splice(taskIndex,1);
		}
		state.isDismissingTask = false;
	},
};


export default {
	namespaced: true,
	state,
	getters,
	actions,
	mutations
};