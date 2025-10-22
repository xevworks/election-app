import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import '@mdi/font/css/materialdesignicons.css' // Add this line

export default createVuetify({
  components,
  directives,
  icons: {
    defaultSet: 'mdi', // Add this icons config
  },
  theme: {
    defaultTheme: 'light',
    themes: {
      light: {
        colors: { primary: '#1E88E5', secondary: '#424242', accent: '#82B1FF' },
      },
    },
  },
})
