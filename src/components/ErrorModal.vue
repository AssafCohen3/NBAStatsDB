<template>
	<div
		class="bg-section-bg-not-transparent rounded-[10px] w-[50vw] overflow-auto">
		<div
			class="py-[20px]">
			<div
				class="flex items-center mb-[4px]">
				<v-btn
					class="ps-4"
					variant="plain"
					:icon="errorMessageExpanded ? 'mdi-chevron-up' : 'mdi-chevron-down'"
					color="primary-light"
					@click="errorMessageExpanded = !errorMessageExpanded" />
				<div
					class="flex w-full break-all px-[10px]">
					<div
						class="text-primary-light font-bold text-[20px]">
						{{ $t('errors.error_message') }}
					</div>
				</div>
			</div>
			<v-fade-transition>
				<div
					v-show="errorMessageExpanded"
					class="w-full break-all text-primary-light px-[54px] text-[20px] bg-[#0b0d24] py-[20px]">
					{{ error.message }}
				</div>
			</v-fade-transition>
		</div>
		<div
			class="pb-[20px]">
			<div
				class="flex items-center mb-[4px]">
				<v-btn
					class="ps-4"
					variant="plain"
					:icon="errorDescriptionExpanded ? 'mdi-chevron-up' : 'mdi-chevron-down'"
					color="primary-light"
					@click="errorDescriptionExpanded = !errorDescriptionExpanded" />
				<div
					class="flex w-full break-all px-[10px]">
					<div
						class="text-primary-light font-bold text-[20px]">
						{{ $t('errors.error_description') }}
					</div>
				</div>
			</div>
			<v-fade-transition>
				<div
					v-show="errorDescriptionExpanded"
					class="w-full break-all text-primary-light px-[54px] text-[20px] bg-[#0b0d24] py-[20px]">
					{{ error.representation }}
				</div>
			</v-fade-transition>
		</div>
		<div>
			<div
				class="flex items-center mb-[4px]">
				<v-btn
					class="ps-4"
					variant="plain"
					:icon="errorTracebackExpanded ? 'mdi-chevron-up' : 'mdi-chevron-down'"
					color="primary-light"
					@click="errorTracebackExpanded = !errorTracebackExpanded" />
				<div
					class="flex w-full break-all px-[10px]">
					<div
						class="text-primary-light font-bold text-[20px]">
						{{ $t('errors.error_traceback') }}
					</div>
				</div>
			</div>
			<v-fade-transition>
				<div
					v-show="errorTracebackExpanded"
					class="w-full break-all text-primary-light px-[54px] text-[20px] bg-[#0b0d24] py-[20px] whitespace-pre-wrap">
					{{ error.traceback }}
				</div>
			</v-fade-transition>
		</div>
	</div>
</template>

<script>
export default {
	props: {
		error: {
			type: Object,
			required: true,
		},
	},
	data(){
		return {
			errorMessageExpanded: true,
			errorDescriptionExpanded: true,
			errorTracebackExpanded: false,
		};
	},

};
</script>

<style>

</style>