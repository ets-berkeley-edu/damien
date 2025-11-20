import axios from 'axios'
import linkifyHtml from 'linkify-html'
import {createApp} from 'vue'
import {createPinia} from 'pinia'
import {setupCalendar} from 'v-calendar'
import {trim} from 'lodash'
import {appErrorHandler, initializeAxios} from '@/utils'
import vuetify from '@/plugins/vuetify'
import router from '@/router'
import axiosPlugin from '@/plugins/axios'
import App from '@/App.vue'
import {useContextStore} from '@/stores/context'

const apiBaseUrl: string = import.meta.env.VITE_APP_API_BASE_URL
const isVueAppDebugMode: boolean = trim(import.meta.env.VITE_APP_DEBUG).toLowerCase() === 'true'

const app = createApp(App)
  .use(axiosPlugin, {baseUrl: apiBaseUrl})
  .use(createPinia())
  .use(setupCalendar, {})
  .use(vuetify)
  .directive('linkified', {
    // See https://github.com/Hypercontext/linkifyjs?tab=readme-ov-file#installation-and-usage
    beforeMount: el => el.innerHTML = linkifyHtml(el.innerHTML, {defaultProtocol: 'https', target: '_blank'})
  })

app.config.errorHandler = appErrorHandler

initializeAxios(axios)

axios.get(`${apiBaseUrl}/api/user/my_profile`).then(response => {
  useContextStore().setCurrentUser(response.data)

  axios.get(`${apiBaseUrl}/api/config`).then(response => {
    const config = {...response.data, ...{apiBaseUrl, isVueAppDebugMode}}
    useContextStore().setConfig(config)
    app.use(router).mount('#app')
  })
})
