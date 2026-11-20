// Browser acceptance checks for the exported SVGs and the offline gallery.
import assert from 'node:assert/strict';
import { existsSync } from 'node:fs';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import puppeteer from 'puppeteer';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const output=path.join(root,'build/tmp/artwork-check');
await mkdir(output,{recursive:true});
const executablePath=[process.env.CHROME_PATH,process.env.PUPPETEER_EXECUTABLE_PATH,
 'C:/Program Files/Google/Chrome/Application/chrome.exe',
 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
 '/usr/bin/google-chrome','/usr/bin/chromium'].find(p=>p&&existsSync(p));
assert(executablePath,'Set CHROME_PATH to a Chrome/Edge executable');
console.log("Starting artwork browser");
const browser=await puppeteer.launch({executablePath,headless:true,
 args:process.env.CI?['--no-sandbox']:[]});
console.log("Browser connected");
const report={plates:[],gallery:{}};
const plates=JSON.parse(await readFile(path.join(root,'illustrations/manifest.json'),'utf8'));
assert(plates.length>0&&new Set(plates.map(p=>p.key)).size===plates.length,'unique plate manifest');
try{
 const page=await browser.newPage();
 console.log("Page ready");
 const errors=[];
 page.on('pageerror',error=>errors.push(error.message));
 await page.setOfflineMode(true);
 await page.setViewport({width:1200,height:660});
 for(const {key:name} of plates){
  console.log('Inspect',name);
  await page.goto(pathToFileURL(path.join(root,'illustrations',name+'.svg')).href);
  await page.evaluate(()=>document.fonts.ready);
  const result=await page.evaluate(()=>{
   const boxes=[...document.querySelectorAll('text')].map(el=>({text:el.textContent,box:el.getBoundingClientRect()}));
   const overflow=boxes.filter(({box:b})=>b.x<18||b.y<18||b.right>1182||b.bottom>642).map(b=>b.text);
   const collisions=[];
   for(let i=0;i<boxes.length;i++)for(let j=i+1;j<boxes.length;j++){
    const a=boxes[i].box,b=boxes[j].box;
    if(Math.min(a.right,b.right)-Math.max(a.x,b.x)>3&&Math.min(a.bottom,b.bottom)-Math.max(a.y,b.y)>3)
     collisions.push([boxes[i].text,boxes[j].text]);
   }
   return {overflow,collisions,ink:document.querySelectorAll('[data-ink="pressure"]').length,
    patchCells:document.querySelectorAll('[data-patch-index]').length};
  });
  assert.deepEqual(result.overflow,[],name+' text overflow');
  assert.deepEqual(result.collisions,[],name+' text collisions');
  assert(result.ink>0,name+' has pressure outlines');
  if(name==='ch02')assert.equal(result.patchCells,59);
  await page.screenshot({path:path.join(output,name+'.png')});
  report.plates.push({name,...result});
 }
 await page.setViewport({width:1280,height:900});
 await page.goto(pathToFileURL(path.join(root,'dist/illustrations.html')).href);
 assert.equal(await page.$$eval('.open',nodes=>nodes.length),plates.length);
 assert(await page.$$eval('.open img',nodes=>nodes.every(i=>i.complete&&i.naturalWidth>0)));
 const downloads=await page.$$eval('.download',nodes=>nodes.map(a=>({name:a.download,uri:a.href})));
 for(const {name,uri} of downloads){
  assert.deepEqual(Buffer.from(uri.split(',')[1],'base64'),await readFile(path.join(root,'illustrations',name)),'download matches source');
 }
 await page.screenshot({path:path.join(output,'gallery.png'),fullPage:true});
 await page.click('.open');
 assert(await page.$eval('dialog',d=>d.open));
 await page.click('.actual');
 assert.equal(await page.$eval('output',el=>el.value),'100%');
 await page.click('.zoom-in');
 assert.equal(await page.$eval('output',el=>el.value),'150%');
 const stage=await page.$eval('.stage',el=>{const b=el.getBoundingClientRect();return{x:b.x+100,y:b.y+100,left:el.scrollLeft}});
 await page.mouse.move(stage.x,stage.y);await page.mouse.down();await page.mouse.move(stage.x-60,stage.y,{steps:3});await page.mouse.up();
 assert((await page.$eval('.stage',el=>el.scrollLeft))>stage.left,'drag pans the zoomed image');
 for(let i=0;i<4;i++)await page.keyboard.press('+');
 assert.equal(await page.$eval('output',el=>el.value),'300%');
 assert(await page.$eval('.zoom-in',el=>el.disabled),'zoom stops at 300%');
 await page.keyboard.press('ArrowRight');
 assert.equal(await page.$eval('.counter',el=>el.textContent),`2 / ${plates.length}`);
 await page.keyboard.press('0');
 assert(await page.$eval('.stage',el=>el.scrollWidth<=el.clientWidth+1&&el.scrollHeight<=el.clientHeight+1));
 await page.keyboard.press('Escape');
 await page.waitForFunction(()=>!document.querySelector('dialog').open&&document.body.style.overflow==='');
 assert(await page.$eval('dialog',el=>!el.open));
 assert(await page.$eval('.open',el=>el===document.activeElement),'focus returns to opener');
 assert.equal(await page.evaluate(()=>document.body.style.overflow),'');
 await page.setViewport({width:390,height:844});
 assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'mobile page fits');
 await page.click('.open');
 await page.click('.actual');
 assert(await page.$eval('.stage',el=>el.scrollWidth>el.clientWidth),'mobile original-size image scrolls');
 await page.click('.fit');
 assert(await page.$eval('.stage',el=>el.scrollWidth<=el.clientWidth+1&&el.scrollHeight<=el.clientHeight+1),'mobile fit works');
 for(let i=0;i<plates.length-1;i++)await page.keyboard.press('ArrowRight');
 assert(await page.$eval('.next',el=>el.disabled),'last image has no next');
 await page.keyboard.press('ArrowRight');
 assert.equal(await page.$eval('.counter',el=>el.textContent),`${plates.length} / ${plates.length}`);
 await page.screenshot({path:path.join(output,'mobile-viewer.png')});
 await page.setViewport({width:844,height:390});
 await page.click('.fit');
 assert(await page.$eval('.stage',el=>el.scrollWidth<=el.clientWidth+1&&el.scrollHeight<=el.clientHeight+1),'landscape fit works');
 await page.click('.close');
 assert(await page.$eval('dialog',el=>!el.open));
 assert.deepEqual(errors,[]);
 report.gallery={offline:true,downloadsMatch:true,zoom:true,pan:true,keyboard:true,focusRestore:true,mobile:true,landscape:true,boundaries:true,noScriptErrors:true};
 await writeFile(path.join(output,'report.json'),JSON.stringify(report,null,2));
 console.log(`PASS: ${plates.length} SVG plates; offline gallery, zoom, pan, keyboard, focus restoration, mobile layout and navigation boundaries.`);
}finally{await browser.close()}
