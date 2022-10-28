import axios from 'axios';



const state = {
	// create action recipe
	isCreatingActionRecipe: false,

	// edit action recipe params
	isEditingActionRecipeParams: false,

	// edit action recipe order
	isEditingActionRecipeOrder: false,

	// copy action recipe
	isCopyingActionRecipe: false,

	// remove action recipe
	isRemovingActionRecipe: false,
};


const getters = {
	// create action recipe
	isCreatingActionRecipe: (state) => state.isCreatingActionRecipe,

	// edit action recipe params
	isEditingActionRecipeParams: (state) => state.isEditingActionRecipeParams,

	// edit action recipe order
	isEditingActionRecipeOrder: (state) => state.isEditingActionRecipeOrder,

	// copy action recipe
	isCopyingActionRecipe: (state) => state.isCopyingActionRecipe,

	// remove action recipe
	isRemovingActionRecipe: (state) => state.isRemovingActionRecipe,
};

const actions = {
	createActionRecipe({commit}, [presetId, resourceId, actionId, order, params]){
		return new Promise((resolve, reject) => {
			commit('createActionRecipeStart');
			axios.post(`/presets/${presetId}/actions_recipes/`, {
				resource_id: resourceId,
				action_id: actionId,
				order: order,
				params: params,
			})
				.then(resp => {
					commit('createActionRecipeSuccess', resp);
					resolve(resp.data);
				})
				.catch(err => {
					console.log(err.toJSON());
				});
			// catch?
		});
	},

	editActionRecipeParams({commit}, [presetId, recipeId, newParams]){
		return new Promise((resolve, reject) => {
			commit('editActionRecipeParamsStart');
			axios.put(`/presets/${presetId}/actions_recipes/${recipeId}/update_params`, {
				params: newParams,
			})
				.then(resp => {
					commit('editActionRecipeParamsSuccess', resp);
					resolve(resp.data);
				})
				.catch(err => {
					console.log(err.toJSON());
				});
			// catch?
		});
	},

	editActionRecipeOrder({commit}, [presetId, recipeId, newOrder]){
		return new Promise((resolve, reject) => {
			commit('editActionRecipeOrderStart');
			axios.put(`/presets/${presetId}/actions_recipes/${recipeId}/update_order`, {
				new_order: newOrder,
			})
				.then(resp => {
					commit('editActionRecipeOrderSuccess', resp);
					resolve(resp.data);
				})
				.catch(err => {
					console.log(err.toJSON());
				});
			// catch?
		});
	},

	copyActionRecipe({commit}, [presetId, recipeId, newPresetId, newOrder]){
		return new Promise((resolve, reject) => {
			commit('copyActionRecipeStart');
			axios.post(`/presets/${presetId}/actions_recipes/${recipeId}/copy`, {
				new_preset_id: newPresetId,
				order_in_new_preset: newOrder
			})
				.then(resp => {
					commit('copyActionRecipeSuccess', resp);
					resolve(resp.data);
				})
				.catch(err => {
					console.log(err.toJSON());
				});
			// catch?
		});
	},

	removeActionRecipe({commit}, [presetId, recipeId]){
		return new Promise((resolve, reject) => {
			commit('removeActionRecipeStart');
			axios.delete(`/presets/${presetId}/actions_recipes/${recipeId}`)
				.then(resp => {
					commit('removeActionRecipeSuccess', resp);
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
	// create action recipe
	createActionRecipeStart(state){
		state.isCreatingActionRecipe = true;
	},
	createActionRecipeSuccess(state){
		state.isCreatingActionRecipe = false;
	},

	// edit action recipe params
	editActionRecipeParamsStart(state){
		state.isEditingActionRecipeParams = true;
	},
	editActionRecipeParamsSuccess(state){
		state.isEditingActionRecipeParams = false;
	},

	// edit action recipe order
	editActionRecipeOrderStart(state){
		state.isEditingActionRecipeOrder = true;
	},
	editActionRecipeOrderSuccess(state){
		state.isEditingActionRecipeOrder = false;
	},

	// copy action recipe
	copyActionRecipeStart(state){
		state.isCopyingActionRecipe = true;
	},
	copyActionRecipeSuccess(state){
		state.isCopyingActionRecipe = false;
	},
	
	// remove action recipe
	removeActionRecipeStart(state){
		state.isRemovingActionRecipe = true;
	},
	removeActionRecipeSuccess(state){
		state.isRemovingActionRecipe = false;
	},
};


export default {
	namespaced: true,
	state,
	getters,
	actions,
	mutations
};