import axios from 'axios';



const state = {
	// resources
	dbStatus: {},
	initializingDB: false,
};


const getters = {
	// resources
	dbStatus: (state) => state.dbStatus,
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
				});
		});
	},
};

const mutations = {
	// resources
	initDBStart(state){
		state.initializingDB = true;
	},
	initDBSuccess(state, resp){
		state.initializingDB = false;
		state.dbStatus = resp.data;
	},
};


export default {
	namespaced: true,
	state,
	getters,
	actions,
	mutations
};