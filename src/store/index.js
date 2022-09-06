import { createStore } from 'vuex';
import resources from './resources';
import db from './db';
import tasks from './tasks';

export default createStore({
	modules: {
		resources,
		db,
		tasks,
	}
});
