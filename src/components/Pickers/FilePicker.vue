<template>
	<div>
		<v-text-field
			:model-value="selectedFilePath"
			class="file_path_text_field"
			readonly
			variant="plain"
			clearable
			:label="$t('common.file_path')"
			:error-messages="v$.$errors.map(m => m.$message)"
			prepend-icon="mdi-paperclip"
			hide-details="auto"
			@click:clear="clearFile"
			@click="onSelectFileClick" />
		<input
			ref="uploader"
			class="hidden"
			type="file"
			@change="onFileChanged"
		>
		<a 
			v-if="exampleFileLink"
			class="text-dimmed-white text-[14px] example-link"
			:href="`${exampleFileLink}`"
			download>
			{{ $t('common.example_file') }}
		</a>
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
		exampleFileLink: {
			type: String,
			default: null,
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
		}
	},
	methods: {
		onSelectFileClick(){
			this.$refs.uploader.click();
		},
		onFileChanged(e){
			let selectedFile = e.target.files[0];
			if(selectedFile){
				this.$emit('update:inputData', {
					'file_path': selectedFile.path
				});
			}
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

.file_path_text_field :deep(.v-field__input){
	cursor: pointer;
}

.example-link{
	text-underline-offset: 3px !important;
	font-weight: 400 !important;
}
</style>