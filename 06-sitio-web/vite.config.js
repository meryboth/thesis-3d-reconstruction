import { writeFile } from 'node:fs/promises'
import path from 'node:path'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

const SEGMENTACION_DIR = path.resolve(import.meta.dirname, 'public/segmentacion')
// mismos ids que SITES en PointCloudSegmentor.jsx -- se valida contra esta
// lista (no contra el nombre que mande el cliente) para que el endpoint no
// pueda escribir fuera de la carpeta de segmentacion.
const KNOWN_SITE_IDS = new Set([
  'templete-central-dji',
  'los-paraguas-dron',
  'panteon-asociacion-espanola-dji',
  'templete-central-dji-vlm',
  'los-paraguas-dron-vlm',
  'panteon-asociacion-espanola-dji-vlm',
])

// Plugin dev-only: permite que el visor de segmentacion (/segmentador)
// guarde la nube editada (tras eliminar puntos a mano) directamente sobre el
// .ply servido en public/segmentacion/, en vez de forzar a descargar el
// archivo y reemplazarlo manualmente en disco.
function saveSegmentacionPlugin() {
  return {
    name: 'save-segmentacion',
    configureServer(server) {
      server.middlewares.use('/api/segmentacion', async (req, res, next) => {
        if (req.method !== 'PUT') return next()
        const siteId = req.url.replace(/^\//, '').replace(/\.ply$/, '')
        if (!KNOWN_SITE_IDS.has(siteId)) {
          res.statusCode = 400
          res.end('sitio desconocido')
          return
        }
        try {
          const chunks = []
          for await (const chunk of req) chunks.push(chunk)
          const buffer = Buffer.concat(chunks)
          await writeFile(path.join(SEGMENTACION_DIR, `${siteId}.ply`), buffer)
          res.statusCode = 200
          res.end('ok')
        } catch (err) {
          console.error('[save-segmentacion]', err)
          res.statusCode = 500
          res.end('error al guardar')
        }
      })
    },
  }
}

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), saveSegmentacionPlugin()],
})
