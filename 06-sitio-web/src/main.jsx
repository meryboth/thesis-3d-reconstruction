import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import PointCloudSegmentor from './components/PointCloudSegmentor.jsx'

// sin router: es una sola ruta extra, aparte del sitio principal, alcanza
// con mirar el pathname directamente.
const isSegmentador = window.location.pathname.replace(/\/+$/, '') === '/segmentador'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    {isSegmentador ? <PointCloudSegmentor /> : <App />}
  </StrictMode>,
)
