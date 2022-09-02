import { createRouter, createWebHashHistory } from 'vue-router';
import AppBase from '../components/AppBase';
import HomePage from '../components/HomePage';
import ResourcePage from '../components/ResourcePage';

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
			}
		]
	},
];

const router = createRouter({
	history: createWebHashHistory(process.env.BASE_URL),
	routes
});

export default router;
