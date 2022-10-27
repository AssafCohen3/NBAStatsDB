import axios from 'axios';



const state = {
	// presets
	presets: [],
	fetchingPresets: false,

	// extended presets
	extendedPresets: [],
	fetchingExtendedPresets: false,
	
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

	// extended presets
	extendedPresets: (state) => state.extendedPresets,
	fetchingExtendedPresets: (state) => state.fetchingExtendedPresets,
	
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
					console.log(err.toJSON());
				});
			// catch?
		});
	},
	fetchPreset({commit}, [presetId]){
		return new Promise((resolve, reject) => {
			commit('fetchPresetStart');
			axios.get(`/presets/details/${presetId}`).
				then(resp => {
					commit('fetchPresetSuccess');
					resolve(resp.data);
				});
			// catch?
		});
	},
	dispatchPreset({commit}, [presetId]){
		return new Promise((resolve, reject) => {
			commit('dispatchPresetStart');
			axios.post(`/presets/dispatch/${presetId}`).
				then(resp => {
					commit('dispatchPresetSuccess');
					resolve(resp.data);
				});
			// catch?
		});
	},
	fetchExtendedPresets({commit}){
		return new Promise((resolve, reject) => {
			commit('fetchExtendedPresetsStart');
			axios.get('/presets/extended')
				.then(resp => {
					commit('fetchExtendedPresetsSuccess', resp);
					resolve(resp.data);
				})
				.catch(err => {
					console.log(err.toJSON());
				});
			// catch?
		});
	},

	createPreset({commit}, [newPreset]){
		return new Promise((resolve, reject) => {
			commit('createPresetStart');
			axios.post('/presets/create', newPreset)
				.then(resp => {
					commit('createPresetSuccess', resp);
					resolve(resp.data);
				})
				.catch(err => {
					console.log(err.toJSON());
				});
			// catch?
		});
	},

	editPreset({commit}, [updatedPreset]){
		return new Promise((resolve, reject) => {
			commit('editPresetStart');
			axios.post('/presets/update', updatedPreset)
				.then(resp => {
					commit('editPresetSuccess', resp);
					resolve(resp.data);
				})
				.catch(err => {
					console.log(err.toJSON());
				});
			// catch?
		});
	},

	removePreset({commit}, [presetId]){
		return new Promise((resolve, reject) => {
			commit('removePresetStart');
			axios.post('/presets/delete', {preset_id: presetId})
				.then(resp => {
					commit('removePresetSuccess', resp);
					resolve(resp.data);
				})
				.catch(err => {
					console.log(err.toJSON());
				});
			// catch?
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

	// extended presets
	fetchExtendedPresetsStart(state){
		state.fetchingExtendedPresets = true;
	},
	fetchExtendedPresetsSuccess(state, resp){
		state.fetchingExtendedPresets = false;
		state.extendedPresets = resp.data;
	},
	
	// preset
	fetchPresetStart(state){
		state.fetchingPreset = true;
	},
	fetchPresetSuccess(state, resp){
		state.fetchingPreset = false;
	},
	
	// dispatching
	dispatchPresetStart(state){
		state.dispatchingPreset = true;
	},
	dispatchPresetSuccess(state){
		state.dispatchingPreset = false;
	},

	// create preset
	createPresetStart(state){
		state.isCreatingPreset = true;
	},
	createPresetSuccess(state){
		state.isCreatingPreset = false;
	},

	// edit preset
	editPresetStart(state){
		state.isEditingPreset = true;
	},
	editPresetSuccess(state){
		state.isEditingPreset = false;
	},

	// remove preset
	removePresetStart(state){
		state.isRemovingPreset = true;
	},
	removePresetSuccess(state){
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