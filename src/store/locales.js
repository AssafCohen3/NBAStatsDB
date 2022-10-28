import axios from 'axios';



const state = {
	localesConfig: null,

	isFetchingLocalesConfig: false,
};


const getters = {
	localesConfig: (state) => state.localesConfig,

	isFetchingLocalesConfig: (state) => state.isFetchingLocalesConfig,

};

const actions = {
	getLocalesConfig({commit}){
		return new Promise((resolve, reject) => {
			commit('getLocalesConfigStart');
			axios.get('/locale/config')
				.then(resp => {
					commit('getLocalesConfigSuccess', resp.data);
					resolve(resp.data);
				})
				.catch(err => {
					console.log(err.toJSON());
				});
		});
	},
};

const mutations = {
	getLocalesConfigStart(state){
		state.localesConfig = null;
		state.isFetchingLocalesConfig = true;
	},
	getLocalesConfigSuccess(state, localesConfig){
		state.localesConfig = localesConfig;
		state.isFetchingLocalesConfig = false;
	},
};


export default {
	namespaced: true,
	state,
	getters,
	actions,
	mutations
};