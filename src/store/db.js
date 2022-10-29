import axios from 'axios';
import { toastError } from '../utils/errorToasts';



const state = {
	dbName: {},
	initializingDB: false,
};


const getters = {
	dbName: (state) => state.dbName,
	initializingDB: (state) => state.initializingDB,
};

const actions = {
	initDB({commit}, [dbName, createDB]){
		return new Promise((resolve, reject) => {
			commit('initDBStart');
			axios.post('/init_db',
				{
					db_name: dbName,
					create_db: createDB 
				})
				.then(resp => {
					commit('initDBSuccess', resp);
					resolve(resp.data);
				})
				.catch(err => {
					commit('initDBError', err.response);
					toastError(err.response);
				});
		});
	},
};

const mutations = {
	// resources
	initDBStart(state){
		state.initializingDB = true;
		state.dbName = null;
	},
	initDBSuccess(state, resp){
		state.initializingDB = false;
		state.dbName = resp.data;
	},
	initDBError(state, err){
		state.initializingDB = false;
	}
};


export default {
	namespaced: true,
	state,
	getters,
	actions,
	mutations
};