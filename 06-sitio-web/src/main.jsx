import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import './presentation.css'
import App from './App.jsx'
import PointCloudSegmentor from './components/PointCloudSegmentor.jsx'
import Presentation from './components/Presentation.jsx'

// sin router: son rutas extra, aparte del sitio principal, alcanza con
// mirar el pathname directamente.
const path = window.location.pathname.replace(/\/+$/, '')
const isSegmentador = path === '/segmentador'
const isPresentacion = path === '/presentacion'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    {isSegmentador ? <PointCloudSegmentor /> : isPresentacion ? <Presentation /> : <App />}
  </StrictMode>,
)
