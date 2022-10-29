import axios from 'axios';
import { toastError } from '../utils/errorToasts';



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
					commit('getLocalesConfigError');
					toastError(err.response);
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
	getLocalesConfigError(state){
		state.isFetchingLocalesConfig = false;
	}
};


export default {
	namespaced: true,
	state,
	getters,
	actions,
	mutations
};