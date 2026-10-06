#!/usr/bin/env node
'use strict';

/* Captura os slides originais e os estados das simulações para montar o vídeo. */
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const { pathToFileURL } = require('node:url');

function loadPlaywright() {
  try { return require('playwright'); } catch (error) {
    if (error.code !== 'MODULE_NOT_FOUND') throw error;
  }
  const bundledModules = path.join(os.homedir(), '.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules');
  try { return require(path.join(bundledModules, 'playwright')); } catch (error) {
    throw new Error(`Playwright indisponível. Configure NODE_PATH com o diretório de pacotes do runtime. ${error.message}`);
  }
}

function parseArguments(argv) {
  if (argv.length !== 2 || argv[0] !== '--output-dir' || !argv[1]) {
    throw new Error('Uso: node records/scripts/render_slides.cjs --output-dir /diretorio/de/imagens');
  }
  return path.resolve(argv[1]);
}

function validatePng(filename) {
  const data = fs.readFileSync(filename);
  const signature = Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]);
  if (!data.subarray(0, 8).equals(signature)) throw new Error(`PNG inválido: ${filename}`);
  const width = data.readUInt32BE(16), height = data.readUInt32BE(20);
  if (width !== 1920 || height !== 1080) throw new Error(`Dimensões inesperadas ${width} × ${height}: ${filename}`);
}

async function validateLayout(page, label) {
  const problems = await page.evaluate(() => {
    const slide = document.querySelector('.slide:not([hidden])');
    const bounds = slide.getBoundingClientRect();
    const footer = slide.querySelector('footer').getBoundingClientRect();
    const selectors = '.content p,.content pre,.content table,.content figure,.content .matrix-wrap,.content ol,.content .process-flow,.content .chart,.content .stripes';
    return [...slide.querySelectorAll(selectors)]
      .filter(element => {
        const r = element.getBoundingClientRect();
        return r.width > 0 && r.height > 0 && (r.left < bounds.left - 1 || r.right > bounds.right + 1 || r.top < bounds.top - 1 || r.bottom > footer.top - 3);
      })
      .map(element => ({ tag: element.tagName, text: element.textContent.trim().slice(0, 100) }));
  });
  if (problems.length) throw new Error(`Conteúdo excede a área do slide em ${label}: ${JSON.stringify(problems)}`);
}

async function main() {
  const outputDir = parseArguments(process.argv.slice(2));
  fs.mkdirSync(outputDir, { recursive: true });
  const root = path.resolve(__dirname, '../..');
  const { chromium } = loadPlaywright();
  const browser = await chromium.launch({
    executablePath: process.env.CHROME || '/usr/bin/google-chrome',
    headless: true,
    args: ['--no-sandbox'],
  });
  const javascriptErrors = [], remoteRequests = [], captures = [];
  try {
    const page = await browser.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1.5 });
    page.on('pageerror', error => javascriptErrors.push(String(error)));
    page.on('request', request => { if (/^https?:/.test(request.url())) remoteRequests.push(request.url()); });
    await page.goto(pathToFileURL(path.join(root, 'slides/apresentacao.html')).href);
    await page.waitForFunction(() => typeof showSlide === 'function');
    await page.evaluate(async () => {
      await document.fonts.ready;
      await Promise.all([...document.images].map(image => image.decode()));
    });
    await page.addStyleTag({ content: `
      .navigation, #notes, .skip { display: none !important; }
      .sim-controls { visibility: hidden !important; pointer-events: none !important; }
      .slide footer > span:first-child { visibility: hidden !important; }
      .video-diagonal { outline: 4px solid #a94d10; outline-offset: -4px; }
    ` });
    const inventory = await page.evaluate(() => ({ slides: slides.length, frames: FRAMES.length }));
    if (inventory.slides !== 14 || inventory.frames !== 10) throw new Error(`Inventário inesperado: ${JSON.stringify(inventory)}`);

    async function capture(filename, slideNumber, simulation, state, highlightDiagonal = false) {
      await page.evaluate(({ slideNumber, simulation, state, highlightDiagonal }) => {
        document.querySelectorAll('.video-diagonal').forEach(cell => cell.classList.remove('video-diagonal'));
        showSlide(slideNumber - 1);
        if (slideNumber === 6) { seqStep = simulation === 'seq' ? state : -1; renderSeq(); }
        if (slideNumber === 10) { mergeStep = simulation === 'merge' ? state : 0; renderMerge(); }
        if (highlightDiagonal) {
          for (const [row, col] of [[2, 2], [3, 3]]) {
            document.querySelector(`#merge-matrix .cell[data-row="${row}"][data-col="${col}"]`).classList.add('video-diagonal');
          }
        }
      }, { slideNumber, simulation, state, highlightDiagonal });
      await validateLayout(page, filename);
      const destination = path.join(outputDir, filename);
      await page.locator('.slide:not([hidden])').screenshot({ path: destination, animations: 'disabled' });
      validatePng(destination);
      captures.push(filename);
    }

    for (let slideNumber = 1; slideNumber <= 14; slideNumber++) {
      await capture(`slide-${String(slideNumber).padStart(2, '0')}.png`, slideNumber);
    }
    for (let state = 0; state < 10; state++) {
      await capture(`slide-06-seq-${state}.png`, 6, 'seq', state);
    }
    const sequentialResult = await page.evaluate(() => ({ objects: document.getElementById('seq-count').textContent, stack: document.getElementById('seq-stack').textContent }));
    if (sequentialResult.objects !== '3' || sequentialResult.stack !== '0') throw new Error(`Resultado sequencial incorreto: ${JSON.stringify(sequentialResult)}`);
    for (let state = 0; state <= 3; state++) {
      await capture(`slide-10-merge-${state}.png`, 10, 'merge', state);
      const count = await page.locator('#merge-count').textContent();
      const expected = state === 0 ? 'Resultado esperado: 4' : state === 1 ? 'Soma local: 2 + 3 = 5' : 'Consolidação: 5 − 1 = 4';
      if (count !== expected) throw new Error(`Consolidação incorreta no estado ${state}: ${count}`);
    }
    await capture('slide-10-merge-1-diagonal.png', 10, 'merge', 1, true);
    const diagonalLabels = await page.evaluate(() => [...document.querySelectorAll('#merge-matrix .video-diagonal')].map(cell => cell.textContent));
    if (diagonalLabels.join(',') !== '10,28') throw new Error(`Contato diagonal incorreto: ${diagonalLabels}`);
    if (javascriptErrors.length || remoteRequests.length) throw new Error(JSON.stringify({ javascriptErrors, remoteRequests }));
    console.log(JSON.stringify({ outputDir, captures: captures.length, width: 1920, height: 1080, sequentialObjects: 3, mergedObjects: 4, javascriptErrors: 0, remoteRequests: 0 }, null, 2));
  } finally {
    await browser.close();
  }
}

main().catch(error => { console.error(error.stack || error.message); process.exitCode = 1; });
