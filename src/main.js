import { createApp } from 'vue';
import App from './components/App.vue';
import router from './router';
import store from './store';
import vuetify from './plugins/vuetify';
import { loadFonts } from './plugins/webfontloader';
import i18n from './i18n';
import '@/assets/styles/main.css';
import axios from 'axios';
// import axiosRetry, { exponentialDelay } from 'axios-retry';
import CountryFlag from 'vue-country-flag-next';
import LanguagueReloadPlugin from './plugins/language_reload_plugin';

loadFonts();
// var aaa = window.process;
const currentLocal = localStorage.getItem('locale') || 'en';
axios.defaults.baseURL = `http://localhost:${window.ipcRenderer.pyPort}/`;
axios.defaults.headers.common['Accept-Language'] = currentLocal;
// solve problems when vue instantiate before flask 
// function customIsNetworkErrorCheck(error){
// 	return error.message === 'Network Error';
// }

// axiosRetry(axios, {
// 	retries: 3,
// 	retryDelay: exponentialDelay,
// 	retryCondition: customIsNetworkErrorCheck
// });
// wait for server to initiate
createApp(App)
	.use(router)
	.use(store)
	.use(vuetify)
	.use(i18n)
	.use(LanguagueReloadPlugin)
	.component('country-flag', CountryFlag)
	.mount('#app');
