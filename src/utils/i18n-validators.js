// @/utils/i18n-validators.js
import * as validators from '@vuelidate/validators';
import i18n from '@/i18n';
import { createI18nMessage } from '@vuelidate/validators';
// Create your i18n message instance. Used for vue-i18n@9
const withI18nMessage = createI18nMessage({ t: i18n.global.t.bind(i18n) });
// for vue-i18n@8
// const withI18nMessage = createI18nMessage({ t: i18n.t.bind(i18n) })

// wrap each validator.
export const required = withI18nMessage(validators.required);

let idRegexValidator = validators.helpers.regex(/^[a-zA-Z0-9][a-zA-Z0-9_]*$/);
export const idValidator = withI18nMessage(idRegexValidator);