import axios from 'axios';
import { toastError } from '../utils/errorToasts';



const state = {
	// resources
	resources: [],
	fetchingResources: false,

	// resource
	fetchingResource: false,

	// action spec
	isFetchingActionSpec: false,

	// post action
	postingAction: false,
};


const getters = {
	// resources
	resources: (state) => state.resources,
	fetchingResources: (state) => state.fetchingResources,

	// resource
	fetchingResource: (state) => state.fetchingResource,

	// action spec
	isFetchingActionSpec: (state) => state.isFetchingActionSpec,

	// post action
	postingAction: (state) => state.postingAction,
};

const actions = {
	fetchResources({commit}){
		return new Promise((resolve, reject) => {
			commit('fetchResourcesStart');
			axios.get('/resources/')
				.then(resp => {
					commit('fetchResourcesSuccess', resp);
					resolve(resp.data);
				})
				.catch(err => {
					toastError(err.response);
					commit('fetchResourcesError');
				});
		});
	},
	fetchResource({commit}, [resourceId]){
		return new Promise((resolve, reject) => {
			commit('fetchResourceStart');
			axios.get(`/resources/${resourceId}`).
				then(resp => {
					commit('fetchResourceSuccess');
					resolve(resp.data);
				})
				.catch(err => {
					toastError(err.response);
					commit('fetchResourceError');
				});
		});
	},
	fetchActionSpec({commit}, [resourceId, actionId]){
		return new Promise((resolve, reject) => {
			commit('fetchActionSpecStart');
			axios.get(`/resources/${resourceId}/actions/${actionId}`).
				then(resp => {
					commit('fetchActionSpecSuccess');
					resolve(resp.data);
				})
				.catch(err => {
					toastError(err.response);
					commit('fetchActionSpecError');
				});
		});
	},
	postAction({commit}, [resourceId, actionId, actionParams]){
		return new Promise((resolve, reject) => {
			commit('postActionStart');
			axios.post(`/resources/${resourceId}/actions/${actionId}/dispatch`,{
				params: actionParams
			}).
				then(resp => {
					commit('postActionSuccess');
					resolve(resp.data);
				})
				.catch(err => {
					toastError(err.response);
					commit('postActionError');
				});
		});
	},
};

const mutations = {
	// resources
	fetchResourcesStart(state){
		state.fetchingResources = true;
	},
	fetchResourcesSuccess(state, resp){
		state.fetchingResources = false;
		state.resources = resp.data;
	},
	fetchResourcesError(state){
		state.fetchingResources = false;
	},

	// resource
	fetchResourceStart(state){
		state.fetchingResource = true;
	},
	fetchResourceSuccess(state, resp){
		state.fetchingResource = false;
	},
	fetchResourceError(state){
		state.fetchingResource = false;
	},

	// action spec
	fetchActionSpecStart(state){
		state.isFetchingActionSpec = true;
	},
	fetchActionSpecSuccess(state){
		state.isFetchingActionSpec = false;
	},
	fetchActionSpecError(state){
		state.isFetchingActionSpec = false;
	},
	
	// post action
	postActionStart(state){
		state.postingAction = true;
	},
	postActionSuccess(state){
		state.postingAction = false;
	},
	postActionError(state){
		state.postingAction = false;
	},
};


export default {
	namespaced: true,
	state,
	getters,
	actions,
	mutations
};