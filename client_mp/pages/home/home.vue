<template>
	<view class="wrap">
		<u-swiper @change="change" :height="250" :list="swiper_list" :title="title" :effect3d="effect3d"
		:indicator-pos="indicatorPos" :mode="mode" :interval="3000" @click="click"></u-swiper>
		<view>{{test}}</view>
	</view>
</template>

<script>
	export default {
		data() {
			return {
				swiper_list: [{
						image: 'https://cdn.uviewui.com/uview/swiper/1.jpg',
						title: '昨夜星辰昨夜风，画楼西畔桂堂东'
					},
					{
						image: 'https://cdn.uviewui.com/uview/swiper/2.jpg',
						title: '身无彩凤双飞翼，心有灵犀一点通'
					},
					{
						image: 'https://cdn.uviewui.com/uview/swiper/3.jpg',
						title: '谁念西风独自凉，萧萧黄叶闭疏窗，沉思往事立残阳'
					}
				],
				title: false,
				mode: 'round',
				indicatorPos: 'bottomCenter',
				effect3d: false,
				test:''
			}
		},
		onLoad() {
			this.gettest();
		},
		methods: {
			gettest(){
				this.$u.api.gettest().then(res=>{
					this.test = res.data
				})
			},
			change(){
				
			},
			click() {
				
			}
		}
	}
</script>

<style>

</style>
