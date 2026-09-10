// Render QA keyframes: one frame per scene -> qa/
// Usage: node scripts/qa-frames.mjs
import puppeteer from 'puppeteer';
import { mkdirSync, rmSync } from 'fs';
import { resolve } from 'path';

const SCENES = [3, 10, 18, 25, 33, 38]; // satu frame per scene (6 scene, DUR=40)
const root = resolve(import.meta.dirname, '..');
rmSync(resolve(root, 'qa'), { recursive: true, force: true });
mkdirSync(resolve(root, 'qa'), { recursive: true });

const browser = await puppeteer.launch({
  headless: true,
  args: ['--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage', '--font-render-hinting=none'],
});
const page = await browser.newPage();
await page.setViewport({ width: 720, height: 1280 });
for (const t of SCENES) {
  await page.goto(`file://${resolve(root, 'video/index.html')}?t=${t}`, { waitUntil: 'load' });
  await page.screenshot({ path: resolve(root, `qa/frame_${String(t).padStart(2, '0')}.png`) });
  console.log('qa frame t=' + t);
}
await browser.close();
