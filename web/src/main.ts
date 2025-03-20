import { createApp } from 'vue'
import PrimeVue from 'primevue/config'
import ToastService from 'primevue/toastservice'
import Aura from '@primeuix/themes/aura'
import './assets/styles.css'
import App from './App.vue'
// import router from './router'
import 'github-markdown-css/github-markdown.css'

const app = createApp(App)
app.use(PrimeVue, {
  theme: {
    preset: Aura,
  },
  ripple: true,
})
app.use(ToastService)
// app.use(router)

app.mount('#app')
