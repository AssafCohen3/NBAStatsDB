<template>
	<v-card
		class="bg-section-bg-not-transparent min-w-[300px]">
		<v-card-title>
			<span
				class="text-dimmed-white">
				{{ preset ? preset.preset_name : $t('common.create_preset') }}
			</span>
		</v-card-title>
		<v-card-text>
			<v-text-field
				v-model="presetForm.presetId"
				class="text-primary-light pb-[20px]"
				:readonly="!!preset"
				:disabled="!!preset"
				hide-details="auto"
				:error-messages="v$.presetForm.presetId.$errors.map(m => m.$message)"
				:label="$t('common.preset_id')" />
			<div
				class="border-[1px] rounded-[10px] border-dimmed-white border-solid">
				<translatable-field-input 
					v-model:field-translations="presetForm.presetNameJson"
					:field-title="$t('common.preset_name')" />
			</div>
			<div
				class="flex justify-between py-[20px]">
				<v-btn
					color="primary"
					@click="savePreset">
					{{ $t('common.save') }}
				</v-btn>
				<v-btn
					color="error"
					@click="cancel">
					{{ $t('common.cancel') }}
				</v-btn>
			</div>
		</v-card-text>
	</v-card>
</template>

<script>
import { useVuelidate } from '@vuelidate/core';
import { required } from '@/utils/i18n-validators';
import TranslatableFieldInput from './TranslatableFieldInput.vue';

function createFormFromPreset(preset){
	return Object.assign({}, {presetId: null, presetNameJson: {}}, (preset && {presetId: preset.preset_id, presetNameJson: preset.preset_name_json}) || {});
}


export default {
	components: { TranslatableFieldInput },
	props: {
		preset: {
			type: Object,
			default: null,
		}
	},
	emits: ['savePreset', 'cancel'],
	setup(){
		const v$ = useVuelidate();
		return { v$ };
	},
	data(){
		return {
			presetForm: createFormFromPreset(this.preset),
		};
	},
	validations(){
		return {
			presetForm: {
				presetId: { required },
			}
		};
	},
	methods: {
		savePreset(){
			this.v$.$touch();
			if(this.v$.$error){
				return;
			}
			this.$emit('savePreset', this.presetForm.presetId, this.presetForm.presetNameJson);
		},
		cancel(){
			this.$emit('cancel');
		}
	},
};
</script>

<style>

</style>