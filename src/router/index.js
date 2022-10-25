import { createRouter, createWebHashHistory } from 'vue-router';
import AppBase from '../components/AppBase';
import HomePage from '../components/HomePage';
import ResourcePage from '../components/ResourcePage';
import PresetsPage from '../components/PresetsPage';

const routes = [
	{
		path: '/',
		component: AppBase,
		children: [
			{
				path: '/',
				name: 'home',
				component: HomePage
			},
			{
				path: 'resources/:resourceId',
				name: 'resource-page',
				component: ResourcePage
			},
			{
				path: 'presets',
				name: 'presets-page',
				component: PresetsPage,
			}
		]
	},
];

const router = createRouter({
	history: createWebHashHistory(process.env.BASE_URL),
	routes
});

export default router;
