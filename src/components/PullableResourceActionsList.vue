<template>
	<div
		class="resource-div">
		<div
			class="flex items-center">
			<v-btn
				variant="plain"
				:icon="expanded ? 'mdi-chevron-up' : 'mdi-chevron-down'"
				color="primary-light"
				@click="expanded = !expanded" />
			<div
				class="flex items-center w-full break-all">
				<div
					class="text-primary-light font-bold text-[24px] select-none">
					{{ resource.resource_name }}
				</div>
			</div>
		</div>
		<v-expand-transition>
			<div
				v-show="expanded">
				<draggable
					v-model="actionsList"
					:group="{
						name: `resource_actions`,
						pull: 'clone',
						put: false,
					}"
					:sort="false"
					item-key="action_id"
					:clone="cloneAction"
					@move="onMove">
					<template #item="{element}">
						<draggable-action-row
							:action="element" />
					</template>
				</draggable>
			</div>
		</v-expand-transition>
	</div>
</template>

<script>
import DraggableActionRow from './DraggableActionRow.vue';
import draggable from 'vuedraggable';
export default {
	components: { DraggableActionRow, draggable, },
	props: {
		resource: {
			type: Object,
			required: true,
		},
	},
	data(){
		return {
			expanded: true,
		};
	},
	computed: {
		actionsList: {
			get(){
				return this.resource.actions;
			},
			set(newVal){

			}
		}
	},
	methods: {
		onMove(evt){
			if(evt.from != evt.to){
				evt.dragged.classList.add('in-other-list');
				evt.dragged.classList.remove('some-list');
			}
			else{
				evt.dragged.classList.remove('in-other-list');
				evt.dragged.classList.add('some-list');
			}
		},
		cloneAction(action){
			return {...action, resource_id: this.resource.resource_id, resource_name: this.resource.resource_name};
		}
	},
};
</script>

<style
	scoped
	lang="postcss">

.resource-div{
	padding: 5px;
	margin-block: 30px;
}
</style>