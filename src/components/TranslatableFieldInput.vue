<template>
	<div
		class="p-[10px]">
		<div
			class="pb-[5px] text-dimmed-white">
			{{ fieldTitle }}
		</div>
		<div
			class="flex flex-col h-full text-primary-light">
			<div
				v-for="locale in Object.keys(availableLocales)"
				:key="locale"
				class="pb-[20px]">
				<v-text-field
					:model-value="fieldTranslations[locale]"
					:error-messages="v$.fieldTranslations[locale].$errors.map(m => m.$message)"
					:label="localesLanguageNames[locale]"
					hide-details="auto"
					@update:model-value="updateTranslations(locale, $event)" />
			</div>
		</div>
	</div>
</template>

<script>
import { mapActions, mapGetters } from 'vuex';
import { useVuelidate } from '@vuelidate/core';
import { required } from '@/utils/i18n-validators';

export default {
	props: {
		fieldTitle: {
			type: String,
			required: true,
		},
		fieldTranslations: {
			type: Object,
			default: null,
			required: false,
		},
	},
	emits: ['update:fieldTranslations'],
	setup(){
		const v$ = useVuelidate();
		return { v$ };
	},
	validations(){
		return {
			fieldTranslations: {
				...Object.assign({},
					...Object.keys(this.availableLocales).map(locale => ({[locale]: locale == this.defaultLocale ? { required } : {}}))
				)
			}
		};
	},
	computed: {
		...mapGetters('locales', ['localesConfig', 'isFetchingLocalesConfig']),
		availableLocales(){
			return this.localesConfig ? this.localesConfig.available_locales : {};
		},
		defaultLocale(){
			return this.localesConfig ? this.localesConfig.default_locale : null;
		},
		localesLanguageNames(){
			let languageNames = new Intl.DisplayNames([this.$i18n.locale], {type: 'language'});
			return Object.assign({},
				...Object.keys(this.availableLocales).map(locale => ({[locale]: languageNames.of(locale)}))
			);
		},		
	},
	mounted(){
		this.getLocalesConfig();
	},
	methods: {
		...mapActions('locales', ['getLocalesConfig']),
		updateTranslations(locale, newTranslation){
			this.$emit('update:fieldTranslations', {...(this.fieldTranslations || {}), [locale]: newTranslation});
		}
	},
};
</script>

<style>

</style>