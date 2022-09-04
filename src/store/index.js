import { createStore } from 'vuex';
import resources from './resources';
import db from './db';

export default createStore({
	modules: {
		resources,
		db,
	}
});
