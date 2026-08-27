// Genera, para cada uno de los 3 casos de estudio, una pagina standalone
// del visor de Gaussian Splatting (SuperSplat Viewer / PlayCanvas), con la
// camara inicial calculada por compute_splat_camera.py.
//
// Los splats en si (scene.ply) son los exports crudos de Splatfacto -- SIN
// pasar por limpieza en SuperSplat Editor todavia (floaters incluidos). Es
// el "cableado" funcionando extremo a extremo; cuando la usuaria limpie los
// splats en superspl.at y los vuelva a exportar, alcanza con reemplazar el
// scene.ply de cada carpeta -- no hace falta tocar este script.
import { renderViewerHtml, css, js } from '@playcanvas/supersplat-viewer';
import { defaultSettings } from '@playcanvas/supersplat-viewer/settings';
import { execFileSync } from 'node:child_process';
import { writeFileSync, readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const PUBLIC_DIR = join(__dirname, '..', 'public', 'archivo-digital');
const PYTHON = 'C:\\Users\\mboth\\AppData\\Local\\Programs\\Python\\Python313\\python.exe';

const SITES = [
    { id: 'paraguas', title: 'Los Paraguas — Vicente López' },
    { id: 'templete-central', title: 'Templete Central — Panteón Sexto, Chacarita' },
    { id: 'panteon', title: 'Panteón Asociación Catalana — Chacarita' },
];

for (const site of SITES) {
    const dir = join(PUBLIC_DIR, site.id);
    const plyPath = join(dir, 'scene.ply');

    const camJson = execFileSync(PYTHON, [join(__dirname, 'compute_splat_camera.py'), plyPath], { encoding: 'utf-8' });
    const cam = JSON.parse(camJson);

    const settings = defaultSettings();
    settings.cameras = [{ initial: { position: cam.position, target: cam.target, fov: cam.fov } }];

    writeFileSync(join(dir, 'settings.json'), JSON.stringify(settings, null, 2));

    const html = renderViewerHtml({
        bootstrap: {
            settings,
            contentUrl: 'scene.ply',
        },
        baseHref: `/archivo-digital/${site.id}/`,
        inlineCss: false,
    });

    writeFileSync(join(dir, 'index.html'), html);
    writeFileSync(join(dir, 'index.css'), css);
    writeFileSync(join(dir, 'index.js'), js);
    console.log(`[OK] ${site.id}: camara a distancia ${cam.radius.toFixed(1)}m del centro, index.html + settings.json + bundle escritos`);
}
