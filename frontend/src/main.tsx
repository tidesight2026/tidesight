import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import './i18n/config'
import App from './App.tsx'
import i18n from './i18n/config'

// Set initial HTML dir and lang attributes based on i18n language
const updateHtmlAttributes = () => {
  const lang = i18n.language || 'ar'
  const dir = lang === 'ar' ? 'rtl' : 'ltr'
  document.documentElement.dir = dir
  document.documentElement.lang = lang
}

// Update on language change
i18n.on('languageChanged', updateHtmlAttributes)

// Set initial attributes
updateHtmlAttributes()

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
