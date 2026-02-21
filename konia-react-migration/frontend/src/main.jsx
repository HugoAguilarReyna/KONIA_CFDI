import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <div id="app-root" style={{ fontFamily: "'Montserrat', sans-serif" }}>
      <App />
    </div>
  </React.StrictMode>,
)
