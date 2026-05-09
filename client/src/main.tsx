import React from 'react'
import ReactDOM from 'react-dom/client'
import { structuralStyles, componentSpecificStyles } from '@a2ui/react/styles'
import App from './App'
import './App.css'

// Inject A2UI structural styles without the aggressive reset layer
const styleEl = document.createElement('style')
styleEl.id = 'a2ui-structural-styles'
styleEl.textContent = structuralStyles + '\n' + componentSpecificStyles
document.head.appendChild(styleEl)

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
