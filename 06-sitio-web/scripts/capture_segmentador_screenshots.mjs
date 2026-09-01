// Script puntual (no forma parte del pipeline) para capturar screenshots del
// visor /segmentador para el Cap. 6 de la tesis. Usa el Edge ya instalado en
// el sistema via playwright-core, sin descargar un Chromium aparte.
import { chromium } from "playwright-core";
import path from "node:path";

const EDGE_PATH = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";
const OUT_DIR = "C:\\nerfstudio_work\\thesis\\05-tesis\\capitulo6_pipeline_definitivo\\media";
const BASE_URL = "http://localhost:5173/segmentador";

const SITES = [
  { value: "templete-central-dji", file: "segmentacion-templete.png", drag: { dy: -90 }, zoom: -400 },
];

async function main() {
  const browser = await chromium.launch({ executablePath: EDGE_PATH, headless: true });
  const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
  await page.goto(BASE_URL, { waitUntil: "networkidle" });

  for (const site of SITES) {
    await page.selectOption("select", site.value);
    // esperar a que cargue el .ply (el contador de puntos deja de estar vacio)
    await page.waitForFunction(
      () => Array.from(document.querySelectorAll("p")).some((p) => /\d.*puntos$/.test(p.textContent || "")),
      { timeout: 15000 }
    );
    await page.waitForTimeout(800);

    const canvas = await page.$("canvas");
    const box = await canvas.boundingBox();
    const cx = box.x + box.width / 2;
    const cy = box.y + box.height / 2;
    await page.mouse.move(cx, cy);
    await page.mouse.down();
    await page.mouse.move(cx, cy + site.drag.dy, { steps: 20 });
    await page.mouse.up();
    if (site.zoom) {
      await page.mouse.move(cx, cy);
      await page.mouse.wheel(0, site.zoom);
    }
    await page.waitForTimeout(300);

    const outPath = path.join(OUT_DIR, site.file);
    await page.screenshot({ path: outPath });
    console.log(`[OK] ${outPath}`);
  }

  // captura extra: modo seleccion con un rectangulo activo, sobre Templete
  await page.selectOption("select", "templete-central-dji");
  await page.waitForTimeout(500);
  const btn = await page.getByRole("button", { name: "Activar modo selección" });
  await btn.click();
  await page.waitForTimeout(300);
  const canvas = await page.$("canvas");
  const box = await canvas.boundingBox();
  const sx = box.x + box.width * 0.42;
  const sy = box.y + box.height * 0.32;
  await page.mouse.move(sx, sy);
  await page.mouse.down();
  await page.mouse.move(sx + 110, sy + 90, { steps: 15 });
  // no soltar el mouse todavia -- se quiere capturar el rectangulo de seleccion en pantalla
  await page.waitForTimeout(150);
  const selOutPath = path.join(OUT_DIR, "segmentacion-edicion-manual.png");
  await page.screenshot({ path: selOutPath });
  await page.mouse.up();
  console.log(`[OK] ${selOutPath}`);

  await browser.close();
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
