// Render deterministic frames from video/index.html using puppeteer, save PNGs to out/.
// Usage: node scripts/render.mjs [fps]   (fps default 30)
import puppeteer from 'puppeteer';
import { mkdirSync } from 'fs';
import { resolve } from 'path';

const fps = Number(process.argv[2] || 30);
const root = resolve(import.meta.dirname, '..');
// DUR dibaca dari video/index.html (baris "const DUR=...") — timeline mengikuti VO
const htmlSrc = await (await import('fs')).promises.readFile(resolve(root, 'video/index.html'), 'utf8');
const DUR = parseFloat(htmlSrc.match(/const DUR=([\d.]+)/)[1]);
mkdirSync(resolve(root, 'out'), { recursive: true });

const browser = await puppeteer.launch({
  headless: true,
  protocolTimeout: 180000,
  args: ['--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage', '--font-render-hinting=none'],
});
const page = await browser.newPage();
await page.setViewport({ width: 720, height: 1280 });
await page.goto('file://' + resolve(root, 'video/index.html?t=0'), { waitUntil: 'load' });

const total = DUR * fps;
for (let f = 0; f < total; f++) {
  const t = f / fps;
  await page.evaluate((tt) => window.__seek(tt), t);
  await page.screenshot({ path: resolve(root, `out/f_${String(f).padStart(5, '0')}.png`), clip: { x: 0, y: 0, width: 720, height: 1280 } });
}
await browser.close();
console.log('rendered', total, 'frames @', fps, 'fps');
