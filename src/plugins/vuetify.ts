import './main.scss'
import '@mdi/font/css/materialdesignicons.css'
import {aliases, mdi} from 'vuetify/iconsets/mdi-svg'
import {createVuetify} from 'vuetify'
import {Resize} from 'vuetify/directives/resize'
import {Scroll} from 'vuetify/directives/scroll'
import {VAlert} from 'vuetify/components/VAlert'
import {VAppBar} from 'vuetify/components/VAppBar'
import {VApp} from 'vuetify/components/VApp'
import {VAutocomplete} from 'vuetify/components/VAutocomplete'
import {VBadge} from 'vuetify/components/VBadge'
import {VBanner} from 'vuetify/components/VBanner'
import {VBtn} from 'vuetify/components/VBtn'
import {VBtnToggle} from 'vuetify/components/VBtnToggle'
import {VCard, VCardActions, VCardSubtitle, VCardText, VCardTitle} from 'vuetify/components/VCard'
import {VCheckbox} from 'vuetify/components/VCheckbox'
import {VChip} from 'vuetify/components/VChip'
import {VCol, VContainer, VRow, VSpacer} from 'vuetify/components/VGrid'
import {VCombobox} from 'vuetify/components/VCombobox'
import {VDataTable, VDataTableVirtual} from 'vuetify/components/VDataTable'
import {VDialog} from 'vuetify/components/VDialog'
import {VDivider} from 'vuetify/components/VDivider'
import {VExpansionPanel, VExpansionPanelText, VExpansionPanelTitle, VExpansionPanels} from 'vuetify/components/VExpansionPanel'
import {VFooter} from 'vuetify/components/VFooter'
import {VForm} from 'vuetify/components/VForm'
import {VIcon} from 'vuetify/components/VIcon'
import {VImg} from 'vuetify/components/VImg'
import {VLayout} from 'vuetify/components/VLayout'
import {VList, VListItem, VListItemAction, VListItemTitle} from 'vuetify/components/VList'
import {VMain} from 'vuetify/components/VMain'
import {VMenu} from 'vuetify/components/VMenu'
import {VNavigationDrawer} from 'vuetify/components/VNavigationDrawer'
import {VProgressCircular} from 'vuetify/components/VProgressCircular'
import {VRadio} from 'vuetify/components/VRadio'
import {VRadioGroup} from 'vuetify/components/VRadioGroup'
import {VSlideXReverseTransition, VSlideYTransition, VSnackbar, VSwitch, VToolbar} from 'vuetify/components'
import {VTable} from 'vuetify/components/VTable'
import {VTextarea} from 'vuetify/components/VTextarea'
import {VTextField} from 'vuetify/components/VTextField'

export default createVuetify({
  components: {
    VAlert,
    VApp,
    VAppBar,
    VAutocomplete,
    VBadge,
    VBanner,
    VBtn,
    VBtnToggle,
    VCard,
    VCardActions,
    VCardSubtitle,
    VCardText,
    VCardTitle,
    VCheckbox,
    VChip,
    VCol,
    VCombobox,
    VContainer,
    VDataTable,
    VDataTableVirtual,
    VDialog,
    VDivider,
    VExpansionPanel,
    VExpansionPanels,
    VExpansionPanelText,
    VExpansionPanelTitle,
    VFooter,
    VForm,
    VIcon,
    VImg,
    VLayout,
    VList,
    VListItem,
    VListItemAction,
    VListItemTitle,
    VMain,
    VMenu,
    VNavigationDrawer,
    VProgressCircular,
    VRadio,
    VRadioGroup,
    VRow,
    VSlideYTransition,
    VSlideXReverseTransition,
    VSnackbar,
    VSpacer,
    VSwitch,
    VTable,
    VTextarea,
    VTextField,
    VToolbar
  },
  defaults: {
    VBtn: {
      flat: true,
      style: 'text-transform: none;',
    },
    VTextField: {
      density: 'compact',
      variant: 'outlined'
    }
  },
  directives: {
    Resize,
    Scroll
  },
  icons: {
    defaultSet: 'mdi',
    aliases,
    sets: {
      mdi
    }
  },
  theme: {
    variations: {
      colors: ['anchor', 'error'],
      lighten: 2,
      darken: 2
    },
    themes: {
      light: {
        colors: {
          accent: '#CC4000',
          alert: '#FA9301',
          anchor: '#CC4000',
          background: '#FFF',
          disabled: '#BBCAD4',
          error: '#B71C1C',
          'evaluation-active': '#DAF0FD',
          'evaluation-done': '#EBF8FF',
          'evaluation-done-label': '#176190',
          'evaluation-ignore': '#EBEBEB',
          'evaluation-ignore-label': '#666',
          'evaluation-to-do': '#F2FFF6',
          'evaluation-to-do-label': '#478047',
          'evaluation-xlisting': '#FFFFDD',
          hovered: '#EEE',
          muted: '#606060',
          'on-surface-variant': '#000',
          primary: '#0D364E',
          'on-tertiary': '#E2E8E9',
          secondary: '#005C8A',
          success: '#009C41',
          'surface-variant': '#F8F8F8',
          tertiary: '#2B6C97',
          title: '#125074',
          topbar: '#125074'
        }
      },
      dark: {
        colors: {
          accent: '#F54E00',
          alert: '#BB8009',
          anchor: '#F54E00',
          background: '#0D202C',
          disabled: '#BBCAD4',
          error: '#FF1A1A',
          'evaluation-active': '#B5E2FD',
          'evaluation-done': '#001C2C',
          'evaluation-done-label': '#004A75',
          'evaluation-ignore': '#2D2D2D',
          'evaluation-ignore-label': '#666666',
          'evaluation-to-do': '#001E00',
          'evaluation-to-do-label': '#005400',
          'evaluation-xlisting': '#2B2600',
          hovered: '#262626',
          muted: '#BDBDBD',
          'on-error': '#240000',
          'on-primary': '#07324A',
          'on-secondary': '#072636',
          'on-surface-variant': '#FFF',
          'on-tertiary': '#E2E8E9',
          primary: '#86C8F3',
          secondary: '#4298D1',
          success: '#00BA4D',
          'surface-bright': '#B0B0B0',
          'surface-variant': '#171717',
          tertiary: '#195F8A',
          title: '#1E71A4',
          topbar: '#0C354D'
        }
      }
    }
  }
})
