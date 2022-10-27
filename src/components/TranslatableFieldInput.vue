<template>
	<v-card
		class="bg-section-bg-not-transparent">
		<v-card-title>
			<span
				class="text-dimmed-white">
				{{ fieldTitle }}
			</span>
		</v-card-title>
		<v-card-text>
			<!-- <div>
				<v-overlay
					:model-value="false"
					class="items-center justify-center">
					<v-progress-circular
						indeterminate
						class="text-primary-light"
					/>
				</v-overlay>
			</div> -->
			<div
				class="pt-[10px]">
				<div
					class="flex flex-col h-full text-primary-light">
					<div
						v-for="locale in Object.keys(translationsForm)"
						:key="locale">
						<v-text-field
							v-model="translationsForm[locale]"
							:label="localesLanguageNames[locale]" />
					</div>
				</div>
			</div>
		</v-card-text>
	</v-card>
</template>

<script>
import { mapActions, mapGetters } from 'vuex';

function createFormFromTranslations(availableLocales, translations){
	return Object.assign({}, 
		...Object.keys(availableLocales).map(locale => ({
			[locale]: (translations && translations[locale]) || null
		}))
	);
}

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
	data(){
		return {
			translationsForm: {},
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
		}
	},
	mounted(){
		this.getLocalesConfig().
			then((resp) => {
				console.log(this.localesConfig, resp);
				this.translationsForm = createFormFromTranslations(this.localesConfig.available_locales, this.fieldTranslations);
			});
	},
	methods: {
		...mapActions('locales', ['getLocalesConfig']),
	},
};
</script>

<style>

</style>