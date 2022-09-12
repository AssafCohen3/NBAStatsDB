<template>
	<div>
		<v-text-field
			v-model="selectedFilePath"
			class="file_path_text_field"
			readonly
			variant="plain"
			clearable
			:label="$t('common.file_path')"
			:error-messages="v$.$errors.map(m => m.$message)"
			prepend-icon="mdi-paperclip"
			hide-details="auto"
			@clear="clearFile"
			@click="onSelectFileClick" />
		<input
			ref="uploader"
			class="hidden"
			type="file"
			@change="onFileChanged"
		>			
	</div>
</template>

<script>

import { useVuelidate } from '@vuelidate/core';
import { required } from '@/utils/i18n-validators';

export default {
	props: {
		inputData: {
			type: Object,
			required: true,
		},
	},
	emits: ['update:inputData'],
	setup(){
		const v$ = useVuelidate();
		return { v$ };
	},
	validations(){
		return {
			selectedFilePath: { required },
		};
	},
	computed: {
		selectedFilePath: {
			get(){
				return this.inputData['file_path'];
			},
			set(newVal){
				this.$emit('update:inputData', {
					'season_type_code': newVal.code
				});
			}
		}
	},
	methods: {
		onSelectFileClick(){
			this.$refs.uploader.click();
		},
		onFileChanged(e){
			let selectedFile = e.target.files[0];
			this.$emit('update:inputData', {
				'file_path': selectedFile.path
			});
		},
		clearFile(){
			this.$emit('update:inputData', {
				'file_path': null
			});
		}
	}
};
</script>

<style
	scoped>

.file_path_text_field >>> .v-field__input{
	cursor: pointer;
}

</style>