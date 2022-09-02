const LanguagueReloadPlugin = {
	install (Vue, options) {
		Vue.mixin({
			beforeCreate () {				
				if (typeof this.$options.onLocaleChange === 'function') {
					this.$watch('$i18n.locale', this.$options.onLocaleChange);
				}
			}
		});
	}
};

export default LanguagueReloadPlugin;