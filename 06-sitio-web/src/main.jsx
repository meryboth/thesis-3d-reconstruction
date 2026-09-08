import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import './presentation.css'
import App from './App.jsx'
import PointCloudSegmentor from './components/PointCloudSegmentor.jsx'
import Presentation from './components/Presentation.jsx'
import ModeladoViewer from './components/ModeladoViewer.jsx'
import ArchivoDigitalPage from './components/ArchivoDigitalPage.jsx'

// sin router: son rutas extra, aparte del sitio principal, alcanza con
// mirar el pathname directamente.
const path = window.location.pathname.replace(/\/+$/, '')
const isSegmentador = path === '/segmentador'
const isPresentacion = path === '/presentacion'
const isModelado = path === '/modelado'
const isArchivoDigital = path === '/archivo-digital'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    {isSegmentador ? <PointCloudSegmentor /> : isPresentacion ? <Presentation /> : isModelado ? <ModeladoViewer /> : isArchivoDigital ? <ArchivoDigitalPage /> : <App />}
  </StrictMode>,
)
