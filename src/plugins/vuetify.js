// Styles
import '@mdi/font/css/materialdesignicons.css';
import 'vuetify/styles';
import i18n from '@/i18n';
import { useI18n } from 'vue-i18n';
import { createVuetify } from 'vuetify';
import { computed, watch } from 'vue';

function wrapScope (scope) {
	return {
		current: scope.locale,
		fallback: computed(() => {
			// TODO: Handle this better?
			return typeof scope.fallbackLocale.value !== 'string' ? 'en'
				: scope.fallbackLocale.value;
		}),
		// TODO: Can this be fixed?
		messages: scope.messages,
		t: scope.t,
		n: scope.n,
	};
}

export function createVueI18nAdapter ({ i18n, useI18n, ...rest }){
	return {
		createRoot: () => {
			return wrapScope(i18n.global);
		},
		getScope: () => {
			const scope = useI18n({ legacy: false, useScope: 'global' });

			return wrapScope(scope);
		},
		createScope: (props = {}) => {
			const scope = useI18n({
				legacy: false,
				useScope: 'global',
				messages: (props.messages ?? i18n.global.messages), // TODO: Fix this
				locale: props.locale,
				fallbackLocale: props.fallbackLocale,
				inheritLocale: !props.locale,
			});

			watch(() => props.locale, () => {
				if (props.locale) {
					scope.locale.value = props.locale;
				} else {
					scope.inheritLocale = true;
				}
			});

			watch(() => props.fallbackLocale, () => {
				if (props.fallbackLocale) {
					scope.fallbackLocale.value = props.fallbackLocale;
				}
			});

			return wrapScope(scope);
		},
		...rest,
	};
}

export default createVuetify({
	// locale: currentLocale
	// for testing hebrew
	// locale: {
	// 	defaultLocale: currentLocale
	// }
	
	locale: createVueI18nAdapter({ i18n, useI18n })
});
