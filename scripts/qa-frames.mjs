// Render QA keyframes: one frame per scene -> qa/
// Usage: node scripts/qa-frames.mjs
import puppeteer from 'puppeteer';
import { mkdirSync, rmSync } from 'fs';
import { resolve } from 'path';
import { readFileSync } from 'fs';

const htmlSrc = readFileSync(resolve(import.meta.dirname, '..', 'video/index.html'), 'utf8');
const DUR = parseFloat(htmlSrc.match(/const DUR=([\d.]+)/)[1]);

// 1 keyframe per caption segment (14 segmen dari VO) + beberapa transisi
const SCENES = [1.5, 3.4, 5.2, 7.5, 10.5, 14, 18, 20.5, 24.5, 28, 30.5, 33.5, 36.2, 38.8, 41];
const root = resolve(import.meta.dirname, '..');
rmSync(resolve(root, 'qa'), { recursive: true, force: true });
mkdirSync(resolve(root, 'qa'), { recursive: true });

const browser = await puppeteer.launch({
  headless: true,
  protocolTimeout: 180000,
  executablePath: process.env.PUPPETEER_EXECUTABLE_PATH || undefined,
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
