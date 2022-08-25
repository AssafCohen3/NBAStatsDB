import { createRouter, createWebHistory } from 'vue-router';
import AppBase from '../components/AppBase';

const routes = [
	{
		path: '/',
		name: 'main',
		component: AppBase
	},
];

const router = createRouter({
	history: createWebHistory(process.env.BASE_URL),
	routes
});

export default router;
