import '@mdi/font/css/materialdesignicons.css'
import Vue from 'vue'
import Vuetify from 'vuetify/lib'

Vue.use(Vuetify)

export default new Vuetify({
  icons: {
    iconfont: 'mdi'
  },
  theme: {
    themes: {
      light: {
        accent: '#CC4000',
        anchor: '#CC4000',
        background: '#FFF',
        disabled: '#BBCAD4',
        error: '#B71C1C',
        'evaluation-row-confirmed': '#EBF8FF',
        'evaluation-row-ignore': '#EBEBEB',
        'evaluation-row-review': '#F2FFF6',
        'evaluation-row-xlisting': '#FFFFDD',
        hovered: '#EEE',
        inactive: '#EEE',
        'inactive-contrast': '#666',
        muted: '#606060',
        primary: '#125074',
        'primary-contrast': '#DAF0FD',
        secondary: '#307AAB',
        success: '#00C853',
        tertiary: '#307AAB',
        title: '#125074'
      },
      dark: {
        accent: '#F04A00',
        anchor: '#F04A00',
        background: '#0D202C',
        disabled: '#BBCAD4',
        error: '#9A0007',
        'evaluation-row-confirmed': '#082231',
        'evaluation-row-ignore': '#2D2D2D',
        'evaluation-row-review': '#0E1F0E',
        'evaluation-row-xlisting': '#2D2800',
        hovered: '#616161',
        inactive: '#AAA',
        'inactive-contrast': '#333',
        muted: '#BDBDBD',
        primary: '#0C354D',
        'primary-contrast': '#94A8B3',
        secondary: '#1C4F72',
        success: '#00953E',
        tertiary: '#80BAE0',
        title: '#1E71A4'
      }
    }
  }
})