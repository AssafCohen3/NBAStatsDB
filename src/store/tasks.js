import axios from 'axios';

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

	// resources to refresh
	resourcesIdsToRefresh: [],
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

	// resources to refresh
	resourcesIdsToRefresh: (state) => state.resourcesIdsToRefresh,
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
	pauseTask({commit}, [taskPath]){
		return new Promise((resolve, reject) => {
			commit('pauseTaskStart');
			axios.post('/tasks/pause_task',
				{
					task_path: taskPath
				})
				.then(resp => {
					commit('pauseTaskSuccess', resp);
					resolve(resp.data);
				});
		});
	},
	resumeTask({commit}, [taskPath]){
		return new Promise((resolve, reject) => {
			commit('resumeTaskStart');
			axios.post('/tasks/resume_task',
				{
					task_path: taskPath
				})
				.then(resp => {
					commit('resumeTaskSuccess', resp);
					resolve(resp.data);
				});
		});
	},
	cancelTask({commit}, [taskPath]){
		return new Promise((resolve, reject) => {
			commit('cancelTaskStart');
			axios.post('/tasks/cancel_task',
				{
					task_path: taskPath
				})
				.then(resp => {
					commit('cancelTaskSuccess', resp);
					resolve(resp.data);
				});
		});
	},
	dismissTask({commit}, [taskPath]){
		return new Promise((resolve, reject) => {
			commit('dismissTaskStart');
			axios.post('/tasks/dismiss_task',
				{
					task_path: taskPath
				})
				.then(resp => {
					commit('dismissTaskSuccess', [resp, taskPath]);
					resolve(resp.data);
				});
		});
	},

};

function getTaskWithId(taskId, tasksList){
	return tasksList.find(t => t.task_id === taskId);
}

function getTaskIndexWithId(taskId, tasksList){
	return tasksList.findIndex(t => t.task_id === taskId);
}

function getTaskParent(initialList, taskPath){
	let dummy = {
		subtasks_messages: initialList
	};

	let taskParent = taskPath.slice(0, -1).reduce(
		(prev, cur) =>{
			if(prev === undefined){
				return undefined;
			}
			return getTaskWithId(cur, prev.subtasks_messages);
		},
		dummy
	);
	return taskParent;
}

const mutations = {
	updateTask(state, [taskPath, taskToUpdate]){
		console.log(taskPath, taskToUpdate);
		if(!taskPath){
			throw 'empty task path';
		}
		let taskParent = getTaskParent(state.currentTasks, taskPath);
		if(taskParent === undefined){
			// TODO maybe throw an error?
			throw `task Path ${taskPath} parent not exist`;
		}
		let currentTask = getTaskWithId(taskPath.at(-1), taskParent.subtasks_messages);
		if(currentTask === undefined){
			taskParent.subtasks_messages.push(taskToUpdate);
		}
		else{
			Object.assign(currentTask, taskToUpdate);
		}
	},
	refreshResources(state, resourcesIdsToRefresh){
		state.resourcesIdsToRefresh = resourcesIdsToRefresh;
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
	dismissTaskSuccess(state, [resp, taskPath]){
		if(!taskPath){
			throw 'empty task path';
		}
		let taskParent = getTaskParent(state.currentTasks, taskPath);
		if(taskParent === undefined){
			// TODO maybe throw an error?
			throw `task Path ${taskPath} parent not exist`;
		}
		let taskIndex = getTaskIndexWithId(taskPath.at(-1), taskParent.subtasks_messages);
		if(taskIndex != -1){
			taskParent.subtasks_messages.splice(taskIndex,1);
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