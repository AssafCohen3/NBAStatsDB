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
				class="pt-[10px] text-dimmed-white">
				<v-text-field
					v-model="filename"
					variant="plain"
					clearable
					:label="$t('common.file_name')"
					prepend-icon="mdi-paperclip"
					hide-details="auto"
					@click:clear="clearFile" />
				<v-checkbox
					v-model="createDB"
					:label="$t('common.create_db')"
					hide-details="auto" />
				<v-btn
					:loading="initializingDB"
					class="my-[10px]"
					color="primary"
					@click="submit">
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
	emits: ['initDb'],
	data(){
		return {
			createDB: false,
			filename: localStorage.getItem('dbName') || 'NBAStatsDB.db',
		};
	},
	computed: {
		...mapGetters('db', {
			initializingDB: 'initializingDB',
		})
	},
	methods: {
		submit(){
			this.$emit('initDb', this.filename, this.createDB);
		},
		clearFile(){
			this.filename = localStorage.getItem('dbName') || 'NBAStatsDB.db';
		}
	},
};
</script>

<style
	scoped>

.file_path_text_field :deep(.v-field__input){
	cursor: pointer;
}
.hidden{
	display: none;
}
</style>