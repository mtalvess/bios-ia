const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path');

const [, , htmlPath, outPath, durArg, onlyFrame] = process.argv;
const FPS = Number(process.env.FPS || 30), DUR = Number(durArg || 15);

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  const [f, qs] = htmlPath.split('?');
  await page.goto('file://' + path.resolve(f) + (qs ? '?' + qs : ''));
  await page.waitForFunction(() => window.render && window.ready !== false);
  await page.evaluate(() => document.fonts.ready);
  if (onlyFrame) {
    for (const t of onlyFrame.split(',')) {
      await page.evaluate(x => render(x), Number(t));
      await page.screenshot({ path: `${outPath}-${t}.png` });
    }
    return browser.close();
  }
  const ff = spawn('ffmpeg', ['-y', '-f', 'image2pipe', '-framerate', String(FPS), '-i', '-',
    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-preset', 'medium', '-movflags', '+faststart', outPath],
    { stdio: ['pipe', 'ignore', 'inherit'] });
  for (let f = 0; f < FPS * DUR; f++) {
    await page.evaluate(([x, i]) => render(x, i), [f / FPS, f]);
    const buf = await page.screenshot({ type: 'jpeg', quality: 95 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  await browser.close();
})();
