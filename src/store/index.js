import { createStore } from 'vuex';
import resources from './resources';
import db from './db';
import tasks from './tasks';
import presets from './presets';
import suggestions from './suggestions';

export default createStore({
	modules: {
		resources,
		db,
		tasks,
		presets,
		suggestions,
	}
});
