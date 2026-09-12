import { createApp } from 'vue'
import 'katex/dist/katex.min.css'
import './style.css'
import App from './App.vue'
import router from './router'

createApp(App).use(router).mount('#app')
