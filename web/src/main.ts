import { createApp } from 'vue'
import PrimeVue from 'primevue/config'
import { vOnClickOutside } from '@vueuse/components'
import ToastService from 'primevue/toastservice'
import ConfirmationService from 'primevue/confirmationservice'
import Aura from '@primeuix/themes/aura'
import './assets/styles.css'
import 'primeicons/primeicons.css'
import App from './App.vue'
// import router from './router'
import 'github-markdown-css/github-markdown.css'

const app = createApp(App)
app.directive('focus', {
  mounted(el) {
    el.focus()
  },
  updated(el) {
    el.focus();
  }
})
app.use(PrimeVue, {
  theme: {
    preset: Aura,
  },
  ripple: true,
})
app.use(ConfirmationService)
app.use(ToastService)
// app.use(router)

app.mount('#app')
