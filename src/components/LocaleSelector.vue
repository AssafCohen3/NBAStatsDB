<template>
	<div class="locale-changer">
		<v-select 
			variant="plain"
			v-model="currentLocale"
			:menu-props="{
				contentClass: 'local-changer-select-menu'
			}"
			:items="$i18n.availableLocales">
			<template
				#item=item>
				<div
					@click="item.props.onClick"
					class="flex flex-row items-center cursor-pointer p-[10px]">
					<country-flag :country="langToCountry[item.item.value]"/>
					<div
						class="text-primary-light font-bold">
						{{ $t('langs.' + item.item.value) }}
					</div>
				</div>
			</template>
			<template
				#selection={item}>
				<div
					class="flex flex-row items-center cursor-pointer">
					<country-flag :country="langToCountry[item.value]"/>
					<div
						class="text-primary-light font-bold">
						{{ $t('langs.' + item.value) }}
					</div>
				</div>
			</template>
		</v-select>
	</div>
</template>
<script>
import {LangToCountry} from '@/consts';
import { setI18nLanguage } from '../i18n';

export default {
	data(){
		return {
			langToCountry: LangToCountry
		};
	},
	computed: {
		currentLocale: {
			get(){
				return this.$i18n.locale;
			},
			set(newLocale){
				setI18nLanguage(this.$i18n, newLocale);
			}
		}
	}
};
</script>

<style
	scoped
	lang="postcss">

.v-select >>> .v-field__append-inner{
	align-items: center !important;
	color: white;
}
</style>