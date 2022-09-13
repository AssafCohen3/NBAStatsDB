import { createStore } from 'vuex';
import resources from './resources';
import db from './db';
import tasks from './tasks';
import presets from './presets';

export default createStore({
	modules: {
		resources,
		db,
		tasks,
		presets,
	}
});
