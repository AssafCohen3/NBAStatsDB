import axios from 'axios';
import { toastError } from '../utils/errorToasts';



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
					toastError(err.response);
				});
		});
	},
	searchTeams({commit}, [search]){
		return new Promise((resolve, reject) => {
			axios.get('/suggestions/teams', {params: {
				search: search
			}})
				.then(resp => {
					resolve(resp.data);
				})
				.catch(err => {
					toastError(err.response);
				});
		});
	},
	getAwards({commit}){
		return new Promise((resolve, reject) => {
			axios.get('/suggestions/awards')
				.then(resp => {
					resolve(resp.data);
				})
				.catch(err => {
					toastError(err.response);
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