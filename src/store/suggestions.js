import axios from 'axios';



const state = {

};


const getters = {

};

const actions = {
	searchPlayers({commit}, [search]){
		return new Promise((resolve, reject) => {
			axios.get('/suggestions/players', {params: {
				search: search
			}})
				.then(resp => {
					resolve(resp.data);
				})
				.catch(err => {
					console.log(err.toJSON());
				});
		});
	},
};

const mutations = {

};


export default {
	namespaced: true,
	state,
	getters,
	actions,
	mutations
};