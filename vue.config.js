module.exports = {
	configureWebpack: {
		module: {
			rules: [
				{
					test: /\.scss$/,
					use: [
						'vue-style-loader',
						'css-loader',
						'sass-loader'
					]
				}
			]
		},	  
	},
	pluginOptions: {
		electronBuilder: {
			externals: [
				'electron-log'
			],
			nodeIntegration: false,
			preload: 'src/preload.js',
			builderOptions: {
				// TODO replace
				appId: 'com.megasanjay.electronvueflask',
				afterSign: './scripts/notarize.js',
				asar: true,
				generateUpdatesFilesForAllChannels: true,
				files: [
					'**/*',
					'!dbmanager/',
					'!build/',
					'!api.spec'
				],
				win: {
					target: 'nsis',
					icon: './src/assets/app-icons/windowsAppIcon.ico',
					extraResources: [
						{
							from: './src/pyflaskdist/api.exe'
						}
					]
				},
				mac: {
					target: [
						'dmg',
						'zip'
					],
					icon: './src/assets/app-icons/macAppIcon.png',
					extraResources: [
						{
							from: './src/pyflaskdist/api'
						}
					],
					darkModeSupport: false,
					hardenedRuntime: true,
					gatekeeperAssess: false,
					entitlements: './entitlements.mac.inherit.plist',
					entitlementsInherit: './entitlements.mac.inherit.plist'
				},
				linux: {
					target: 'AppImage',
					icon: './src/assets/app-icons/linuxAppIcon.png',
					extraResources: [
						{
							from: './src/pyflaskdist/api'
						}
					]
				},
				nsis: {
					createDesktopShortcut: 'always',
					oneClick: true,
					deleteAppDataOnUninstall: true,
					installerIcon: './src/assets/app-icons/windowsAppIcon.ico'
				},
				// TODO replace
				publish: {
					provider: 'github',
					repository: 'https://github.com/megasanjay/electron-vue3-flask.git'
				}
			}
		},
		i18n: {
			locale: 'en',
			fallbackLocale: 'en',
			localeDir: 'locales',
			enableLegacy: false,
			runtimeOnly: false,
			compositionOnly: false,
			fullInstall: true
		},
		vuetify: {
			// https://github.com/vuetifyjs/vuetify-loader/tree/next/packages/vuetify-loader
		}
	},
};
