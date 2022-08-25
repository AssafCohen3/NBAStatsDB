<template>
	<v-app-bar
		app
		class="flex justify-items-stretch myappbar"
		color="#340444"
		height="100"
		:style="{
			marginInlineStart: currentMargin
		}">
		<v-spacer />
		<v-btn
			icon
			append-icon="notifications"
			class="mx-[4px]">
		</v-btn>
	</v-app-bar>
</template>

<script>

export default {
	data(){
		return {
			observer: null,
			currentMargin: null,
		};	
	},
	mounted(){
		// some gross hack to fix rtl bug. 
		let element = document.querySelector('.v-locale--is-rtl .myappbar');
		if(element){
			let style = window.getComputedStyle(element);
			this.currentMargin = style.getPropertyValue('margin-left');
			this.observer = new MutationObserver((mutations) => {
				mutations.forEach((mutation) => {
					if (mutation) {
						let style = window.getComputedStyle(element);
						this.currentMargin = style.getPropertyValue('margin-left');					           
					}
				});
			});
			this.observer.observe(element, {attributes: true});	
		}
	}
};
</script>

<style>
</style>
