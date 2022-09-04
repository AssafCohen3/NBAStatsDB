<template>
	<v-card
		class="bg-section-bg">
		<v-card-title>
			<span
				class="text-dimmed-white">
				{{ $t('common.database_not_initialized') }}
			</span>
		</v-card-title>
		<v-card-text>
			<span
				class="text-dimmed-white">
				{{ $t('common.try_again_with_another_settings') }}
			</span>
			<div
				class="pt-[10px]">
				<v-checkbox
					:label="$t('common.create_db')"
					class="text-dimmed-white"
					v-model="createDB"
					hide-details="auto" />
				<v-btn
					:loading="initializingDB"
					@click="submit"
					color="green">
					<span>
						{{ $t('common.try_again') }}
					</span>
				</v-btn>

			</div>
		</v-card-text>
	</v-card>
</template>

<script>
import { mapGetters } from 'vuex';
export default {
	data(){
		return {
			createDB: false
		};
	},
	computed: {
		...mapGetters('db', {
			initializingDB: 'initializingDB',
		})
	},
	methods: {
		submit(){
			this.$emit('initDB', null, this.createDB);
		}
	}
};
</script>

<style>

</style>