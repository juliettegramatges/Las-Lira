import React from 'react'
import ReactDOM from 'react-dom/client'
import { HeroUIProvider } from '@heroui/react'
import { AuthProvider } from './contexts/AuthContext'
import App from './App.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <HeroUIProvider>
      <AuthProvider>
        <App />
      </AuthProvider>
    </HeroUIProvider>
  </React.StrictMode>,
)

