import { createRouter, createWebHistory } from 'vue-router';
import AppBase from '../components/AppBase';
import HomePage from '../components/HomePage';

const routes = [
	{
		path: '/',
		component: AppBase,
		children: [
			{
				path: '/',
				name: 'home',
				component: HomePage
			}
		]
	},
];

const router = createRouter({
	history: createWebHistory(process.env.BASE_URL),
	routes
});

export default router;
