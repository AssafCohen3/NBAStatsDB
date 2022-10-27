import axios from 'axios';



const state = {
	// create action recipe
	isCreatingActionRecipe: false,

	// edit action recipe params
	isEditingActionRecipeParams: false,

	// edit action recipe order
	isEditingActionRecipeOrder: false,

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

	// remove action recipe
	isRemovingActionRecipe: (state) => state.isRemovingActionRecipe,
};

const actions = {
	createActionRecipe({commit}, [newActionRecipeData]){
		return new Promise((resolve, reject) => {
			commit('createActionRecipeStart');
			axios.post('/presets/actions_recipes/create', newActionRecipeData)
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
			axios.post('/presets/actions_recipes/update_params', {
				preset_id: presetId,
				recipe_id: recipeId,
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
			axios.post('/presets/actions_recipes/update_order', {
				preset_id: presetId,
				recipe_id: recipeId,
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

	removeActionRecipe({commit}, [presetId, recipeId]){
		return new Promise((resolve, reject) => {
			commit('removeActionRecipeStart');
			axios.post('/presets/actions_recipes/delete', {
				preset_id: presetId,
				recipe_id: recipeId,
			})
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