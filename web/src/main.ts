import { createApp } from 'vue'
import PrimeVue from 'primevue/config'
import { definePreset } from '@primeuix/themes';
import ToastService from 'primevue/toastservice'
import ConfirmationService from 'primevue/confirmationservice'
import DialogService from 'primevue/dialogservice'
import Tooltip from 'primevue/tooltip'
import Aura from '@primeuix/themes/aura'
import './assets/styles.css'
import 'primeicons/primeicons.css'
import App from './App.vue'
// import router from './router'
import 'github-markdown-css/github-markdown.css'

const app = createApp(App)
const preset = definePreset(Aura, {
  semantic: {
    // primary: '#3b82f6',
    primary: {
      50: '{indigo.50}',
      100: '{indigo.100}',
      200: '{indigo.200}',
      300: '{indigo.300}',
      400: '{indigo.400}',
      500: '{indigo.500}',
      600: '{indigo.600}',
      700: '{indigo.700}',
      800: '{indigo.800}',
      900: '{indigo.900}',
      950: '{indigo.950}'
    },
  }
})
app.directive('focus', {
  mounted(el) {
    el.focus()
  },
  updated(el) {
    el.focus();
  }
})
app.directive('tooltip', Tooltip)
app.use(PrimeVue, {
  theme: {
    preset: preset,
    options: {
      darkModeSelector: '.my-app-dark',
    },
  },
  ripple: true,
})
app.use(ConfirmationService)
app.use(ToastService)
app.use(DialogService)
// app.use(router)

app.mount('#app')
