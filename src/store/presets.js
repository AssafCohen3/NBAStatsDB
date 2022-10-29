import axios from 'axios';
import { toastError } from '../utils/errorToasts';



const state = {
	// presets
	presets: [],
	fetchingPresets: false,

	// preset
	fetchingPreset: false,

	// dispatching
	dispatchingPreset: false,

	// create preset
	isCreatingPreset: false,

	// edit preset
	isEditingPreset: false,

	// remove preset
	isRemovingPreset: false,
};


const getters = {
	// presets
	presets: (state) => state.presets,
	fetchingPresets: (state) => state.fetchingPresets,

	// preset
	fetchingPreset: (state) => state.fetchingPreset,

	// dispatching
	dispatchingPreset: (state) => state.dispatchingPreset,

	// create preset
	isCreatingPreset: (state) => state.isCreatingPreset,

	// edit preset
	isEditingPreset: (state) => state.isEditingPreset,

	// remove preset
	isRemovingPreset: (state) => state.isRemovingPreset,
};

const actions = {
	fetchPresets({commit}){
		return new Promise((resolve, reject) => {
			commit('fetchPresetsStart');
			axios.get('/presets/')
				.then(resp => {
					commit('fetchPresetsSuccess', resp);
					resolve(resp.data);
				})
				.catch(err => {
					toastError(err.response);
					commit('fetchPresetsError');
				});
		});
	},
	fetchPreset({commit}, [presetId]){
		return new Promise((resolve, reject) => {
			commit('fetchPresetStart');
			axios.get(`/presets/${presetId}`).
				then(resp => {
					commit('fetchPresetSuccess');
					resolve(resp.data);
				})
				.catch(err => {
					toastError(err.response);
					commit('fetchPresetError');
				});
		});
	},
	dispatchPreset({commit}, [presetId]){
		return new Promise((resolve, reject) => {
			commit('dispatchPresetStart');
			axios.post(`/presets/${presetId}/dispatch`).
				then(resp => {
					commit('dispatchPresetSuccess');
					resolve(resp.data);
				})
				.catch(err => {
					toastError(err.response);
					commit('dispatchPresetError');
				});
		});
	},
	createPreset({commit}, [presetId, presetNameJson]){
		return new Promise((resolve, reject) => {
			commit('createPresetStart');
			axios.post('/presets/', {
				preset_id: presetId,
				preset_name_json: presetNameJson,
			})
				.then(resp => {
					commit('createPresetSuccess', resp);
					resolve(resp.data);
				})
				.catch(err => {
					toastError(err.response);
					commit('createPresetError');
				});
		});
	},

	editPreset({commit}, [presetId, presetNameJson]){
		return new Promise((resolve, reject) => {
			commit('editPresetStart');
			axios.put(`/presets/${presetId}`, {
				preset_name_json: presetNameJson
			})
				.then(resp => {
					commit('editPresetSuccess', resp);
					resolve(resp.data);
				})
				.catch(err => {
					toastError(err.response);
					commit('editPresetError');
				});
		});
	},

	removePreset({commit}, [presetId]){
		return new Promise((resolve, reject) => {
			commit('removePresetStart');
			axios.delete(`/presets/${presetId}`)
				.then(resp => {
					commit('removePresetSuccess', resp);
					resolve(resp.data);
				})
				.catch(err => {
					toastError(err.response);
					commit('removePresetError');
				});
		});
	},
};

const mutations = {
	// presets
	fetchPresetsStart(state){
		state.fetchingPresets = true;
	},
	fetchPresetsSuccess(state, resp){
		state.fetchingPresets = false;
		state.presets = resp.data;
	},
	fetchPresetsError(state){
		state.fetchingPresets = false;
	},
	
	// preset
	fetchPresetStart(state){
		state.fetchingPreset = true;
	},
	fetchPresetSuccess(state, resp){
		state.fetchingPreset = false;
	},
	fetchPresetError(state){
		state.fetchingPreset = false;
	},
	
	// dispatching
	dispatchPresetStart(state){
		state.dispatchingPreset = true;
	},
	dispatchPresetSuccess(state){
		state.dispatchingPreset = false;
	},
	dispatchPresetError(state){
		state.dispatchingPreset = false;
	},

	// create preset
	createPresetStart(state){
		state.isCreatingPreset = true;
	},
	createPresetSuccess(state){
		state.isCreatingPreset = false;
	},
	createPresetError(state){
		state.isCreatingPreset = false;
	},

	// edit preset
	editPresetStart(state){
		state.isEditingPreset = true;
	},
	editPresetSuccess(state){
		state.isEditingPreset = false;
	},
	editPresetError(state){
		state.isEditingPreset = false;
	},

	// remove preset
	removePresetStart(state){
		state.isRemovingPreset = true;
	},
	removePresetSuccess(state){
		state.isRemovingPreset = false;
	},
	removePresetError(state){
		state.isRemovingPreset = false;
	},
};


export default {
	namespaced: true,
	state,
	getters,
	actions,
	mutations
};