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
			customFileProtocol: './',
			nodeIntegration: false,
			preload: 'src/preload.js',
			builderOptions: {
				// TODO replace
				appId: 'com.assaflgc.nbastatsdb',
				afterSign: './scripts/notarize.js',
				asar: true,
				generateUpdatesFilesForAllChannels: true,
				files: [
					'**/*',
					'!dbmanager/',
					'!build/',
					'!dbmanagerbuild/',
				],
				win: {
					target: 'nsis',
					icon: './src/assets/app-icons/logo.png',
					extraResources: [
						{
							from: './dbmanagerbuild/api.exe',
						}
					]
				},
				mac: {
					target: [
						'dmg',
						'zip'
					],
					icon: './src/assets/app-icons/logo.png',
					extraResources: [
						{
							from: './dbmanagerbuild/api',
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
					icon: './src/assets/app-icons/logo.png',
					extraResources: [
						{
							from: './dbmanagerbuild/api',
						}
					]
				},
				nsis: {
					createDesktopShortcut: 'always',
					oneClick: true,
					deleteAppDataOnUninstall: true,
					installerIcon: './src/assets/app-icons/logo.png'
				},
				// TODO replace
				// publish: {
				// 	provider: 'github',
				// 	repository: 'https://github.com/AssafCohen3/NBAStatsDB.git'
				// }
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
