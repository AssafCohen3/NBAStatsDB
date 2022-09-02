import axios from 'axios';



const state = {
	// resources
	resources: [],
	fetchingResources: false,

	// resource
	fetchingResource: false,
};


const getters = {
	// resources
	resources: (state) => state.resources,
	fetchingResources: (state) => state.fetchingResources,

	// resource
	fetchingResource: (state) => state.fetchingResource,
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
					console.log(err.toJSON());
				});
			// catch?
		});
	},
	fetchResource({commit}, [resourceId]){
		return new Promise((resolve, reject) => {
			commit('fetchResourceStart');
			axios.get(`/resources/${resourceId}`).
				then(resp => {
					commit('fetchResourceSuccess');
					resolve(resp.data);
				});
			// catch?
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

	// resource
	fetchResourceStart(state){
		state.fetchingResource = true;
	},
	fetchResourceSuccess(state, resp){
		state.fetchingResource = false;
	},

};


export default {
	namespaced: true,
	state,
	getters,
	actions,
	mutations
};