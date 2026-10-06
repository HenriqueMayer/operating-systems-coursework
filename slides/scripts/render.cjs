/* Renderizacao e verificacao do HTML local com Playwright e Chrome. */
const fs=require('fs');
const path=require('path');
const {pathToFileURL}=require('url');
const {chromium}=require('playwright');
const root=path.resolve(__dirname,'../..');
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.CHROME||'/usr/bin/google-chrome',headless:true,args:['--no-sandbox']});
 const page=await browser.newPage({viewport:{width:1440,height:900},deviceScaleFactor:1});
 let errors=[];page.on('pageerror',e=>errors.push(String(e)));let remote=[];page.on('request',r=>{if(/^https?:/.test(r.url()))remote.push(r.url());});
 await page.goto(pathToFileURL(path.join(root,'slides/apresentacao.html')).href);
 await page.waitForFunction(()=>typeof showSlide==='function');
 fs.mkdirSync(path.join(root,'slides/assets/codigo'),{recursive:true});
 if(!process.argv.includes('--final')){
  for(let i=0;i<14;i++){
   await page.evaluate(i=>showSlide(i),i);
   const code=page.locator('.slide:not([hidden]) .code');
   if(await code.count()){
    const key=await code.getAttribute('data-code');
    await code.screenshot({path:path.join(root,'slides/assets/codigo',key+'.png')});
   }
  }
  console.log('Capturas dos trechos de codigo geradas.');
 }else{
  const shots=path.join('/tmp','sisop-slides-qa');fs.mkdirSync(shots,{recursive:true});
  for(let i=0;i<14;i++){
   await page.evaluate(i=>showSlide(i),i);
   if(i===5)await page.locator('#seq-end').click();
   if(i===9){await page.locator('#merge-next').click();await page.locator('#merge-next').click();}
   await page.locator('.slide:not([hidden])').screenshot({path:path.join(shots,`slide-${String(i+1).padStart(2,'0')}.png`)});
   const overflow=await page.evaluate(()=>{
    const slide=document.querySelector('.slide:not([hidden])'),footer=slide.querySelector('footer').getBoundingClientRect();
    return [...slide.querySelectorAll('.content p,.content pre,.content table,.content figure,.content .matrix-wrap,.content ol')].filter(e=>e.getBoundingClientRect().bottom>footer.top-3).map(e=>e.textContent.slice(0,50));
   });
   if(overflow.length)throw new Error(`Overflow slide ${i+1}: ${overflow}`);
  }
  await page.evaluate(()=>showSlide(0));
  await page.keyboard.press('ArrowRight');if(await page.locator('#progress').textContent()!=='2 / 14')throw new Error('Teclado');
  await page.keyboard.press('r');if(await page.locator('#notes').isHidden())throw new Error('Roteiro');await page.keyboard.press('Escape');
  await page.evaluate(()=>{showSlide(5);seqStep=-1;renderSeq();});await page.locator('#seq-next').click();
  if(await page.locator('#seq-count').textContent()!=='1')throw new Error('Simulacao sequencial');
  await page.locator('#seq-end').click();if(await page.locator('#seq-count').textContent()!=='3')throw new Error('Resultado sequencial');
  await page.evaluate(()=>{showSlide(9);mergeStep=0;renderMerge();});
  await page.locator('#merge-next').click();if(await page.locator('#merge-count').textContent()!=='Soma local: 2 + 3 = 5')throw new Error('Soma local');
  await page.locator('#merge-next').click();await page.locator('#merge-next').click();
  if(await page.locator('#merge-count').textContent()!=='Consolidação: 5 − 1 = 4')throw new Error('Consolidacao');
  await page.pdf({path:path.join(root,'slides/apresentacao.pdf'),printBackground:true,preferCSSPageSize:true});
  await page.setViewportSize({width:390,height:844});
  for(let i=0;i<14;i++){
   await page.evaluate(i=>showSlide(i),i);
   const bad=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth);
   if(bad)throw new Error(`Overflow mobile ${i+1}`);
  }
  await page.evaluate(()=>showSlide(9));await page.screenshot({path:path.join(shots,'mobile.png'),fullPage:true});
  const fallback=await browser.newPage({javaScriptEnabled:false,viewport:{width:1440,height:900}});
  await fallback.goto(pathToFileURL(path.join(root,'slides/apresentacao.html')).href);
  if(await fallback.locator('.slide:visible').count()!==14)throw new Error('Fallback sem JS');
  if(errors.length||remote.length)throw new Error(JSON.stringify({errors,remote}));
  console.log('QA: 14 slides; teclado, roteiro, simulacoes, mobile e fallback sem JS; sem recursos remotos. PDF exportado.');
 }
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1);});
