// Exercise the actual archived EPUB through epub.js, plus print-size figure text.
import assert from 'node:assert/strict';
import {existsSync} from 'node:fs';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {createServer} from 'node:http';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import puppeteer from 'puppeteer';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const out=path.join(root,'build/tmp/reading-check');
const figureCount=Object.keys(JSON.parse(await readFile(path.join(root,'build/figure-notes.json'),'utf8'))).length;
await mkdir(out,{recursive:true});
const files={
 '/book.epub':['dist/chaizha.epub','application/epub+zip'],
 '/epub.js':['build/node_modules/epubjs/dist/epub.min.js','text/javascript'],
 '/jszip.js':['build/node_modules/jszip/dist/jszip.min.js','text/javascript']
};
const server=createServer(async(req,res)=>{
 try{
  if(req.url==='/'){
   res.writeHead(200,{'Content-Type':'text/html; charset=utf-8'});
   res.end('<!doctype html><html><head><meta charset="utf-8"><style>html,body{margin:0}#reader{width:100vw;height:100vh}</style></head><body><div id="reader"></div><script src="/jszip.js"></script><script src="/epub.js"></script></body></html>');
  }else if(files[req.url]){
   const [file,type]=files[req.url];res.writeHead(200,{'Content-Type':type});res.end(await readFile(path.join(root,file)));
  }else{res.writeHead(404);res.end()}
 }catch(error){res.writeHead(500);res.end(String(error))}
});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
const origin=`http://127.0.0.1:${server.address().port}`;
const executablePath=[process.env.CHROME_PATH,process.env.PUPPETEER_EXECUTABLE_PATH,
 'C:/Program Files/Google/Chrome/Application/chrome.exe',
 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
 '/usr/bin/google-chrome','/usr/bin/chromium'].find(p=>p&&existsSync(p));
assert(executablePath,'Set CHROME_PATH');
const browser=await puppeteer.launch({executablePath,headless:'shell',args:process.env.CI?['--no-sandbox']:[]});
const report={reader:'epub.js 0.3.93 / JSZip 3.10.1',browser:await browser.version(),reflow:[],fonts:[],navigation:[],originals:[],printFigures:[]};
try{
 const page=await browser.newPage();
 page.setDefaultTimeout(30000);
 const errors=[],external=[];
 page.on('pageerror',error=>errors.push(error.message));
 await page.setRequestInterception(true);
 page.on('request',request=>{
  if(/^https?:/.test(request.url())&&!request.url().startsWith(origin)){
   external.push(request.url());request.abort();
  }else request.continue();
 });
 for(const width of [320,390])for(const font of [100,150]){
  console.log(`EPUB reflow ${width}px / ${font}%`);
  await page.setViewport({width,height:844});
  await page.goto(origin);
  const hrefs=await page.evaluate(async font=>{
   window.book=ePub(await fetch('/book.epub').then(r=>r.arrayBuffer()));await book.ready;
   window.rendition=book.renderTo('reader',{width:'100%',height:'100%',flow:'scrolled-doc',spread:'none'});
   rendition.themes.fontSize(font+'%');
   return book.spine.spineItems.filter(item=>/ch\d+\.xhtml$/.test(item.href)).map(item=>item.href);
  },font);
  assert.equal(hrefs.length,11);
  for(const href of hrefs){
   const result=await page.evaluate(async href=>{
    await rendition.display(href);
    const content=rendition.getContents()[0],d=content.document,w=content.window;
    await d.fonts.ready;
    await Promise.all([...d.images].map(img=>img.complete?Promise.resolve():new Promise((resolve,reject)=>{img.onload=resolve;img.onerror=reject})));
    const style=el=>w.getComputedStyle(el);
    const cells=[...d.querySelectorAll('td')],paragraphs=[...d.querySelectorAll('p')];
    return {href,width:w.innerWidth,scrollWidth:d.documentElement.scrollWidth,
     bodyFont:parseFloat(style(d.body).fontSize),
     tablesStack:cells.every(cell=>style(cell).display==='block'&&style(cell.querySelector('.cell-label')).display==='block'),
     leftAligned:paragraphs.every(p=>style(p).textAlign==='left'||p.closest('header')),
     images:[...d.images].every(img=>img.complete&&img.naturalWidth>0),
     notes:d.querySelectorAll('.figure-reading').length,
     originalLinks:[...d.querySelectorAll('.figure-original')].map(a=>a.getAttribute('href'))};
   },href);
   assert(result.scrollWidth<=result.width+1,JSON.stringify(result));
   assert(result.tablesStack,href+' stacked table labels');assert(result.leftAligned,href+' paragraph spacing');
   assert(result.images,href+' images decoded');assert(result.bodyFont>=16*font/100-.1,href+' font resize');
   report.reflow.push({viewport:width,font,...result});
  }
  // Capture the command table in the actual reader, with the chosen font size.
  await page.evaluate(()=>rendition.display('text/ch010.xhtml'));
  await page.screenshot({path:path.join(out,`epub-${width}-${font}.png`)});
 }
 console.log('EPUB pagination and anchor navigation');
 await page.setViewport({width:900,height:760});await page.goto(origin);
 const links=await page.evaluate(async()=>{
  window.book=ePub(await fetch('/book.epub').then(r=>r.arrayBuffer()));await book.ready;
  window.rendition=book.renderTo('reader',{width:'100%',height:'100%',flow:'paginated',spread:'none'});
  await rendition.display('text/ch001.xhtml#reader-index');
  return [...rendition.getContents()[0].document.querySelectorAll('a[href]')]
   .filter(a=>a.getAttribute('href').includes('#')).map(a=>a.getAttribute('href'));
 });
 assert(links.length>=30,'reader index has shortcuts and figures');
 for(const href of links){
  const target='text/'+href;
  const result=await page.evaluate(async target=>{
   await rendition.display(target);
   const content=rendition.getContents()[0],id=decodeURIComponent(target.split('#')[1]);
   const element=content.document.getElementById(id);
   const box=element?.getBoundingClientRect();
   const range=content.document.createRange();if(element)range.selectNodeContents(element);
   const rects=element?[...range.getClientRects()]:[];
   return {target,exists:!!element,visible:!!box&&[box,...rects].some(r=>r.right>0&&r.left<content.window.innerWidth&&r.bottom>0&&r.top<content.window.innerHeight),cfi:rendition.currentLocation().start.cfi};
  },target);
  assert(result.exists&&result.visible,JSON.stringify(result));report.navigation.push(result);
 }
 const originals=report.reflow.filter(r=>r.viewport===320&&r.font===100).flatMap(r=>r.originalLinks);
 assert.equal(originals.length,figureCount);
 for(const href of originals){
  const result=await page.evaluate(async target=>{
   await rendition.display(target);
   const d=rendition.getContents()[0].document,img=d.querySelector('img');
   if(!img.complete)await new Promise((resolve,reject)=>{img.onload=resolve;img.onerror=reject});
   const back=d.querySelector('a').getAttribute('href');
   return {target,imageLoaded:img.naturalWidth>0,back,linear:book.spine.get(target).linear};
  },'text/'+href);
  assert(result.imageLoaded&&result.back.includes('#fig-')&&result.linear===false,JSON.stringify(result));
  await page.evaluate(target=>rendition.display(target),'text/'+result.back);
  report.originals.push(result);
 }
 await page.evaluate(()=>rendition.display('text/ch005.xhtml'));
 const before=await page.evaluate(()=>rendition.currentLocation().start.cfi);
 await page.evaluate(()=>rendition.next());
 const after=await page.evaluate(()=>rendition.currentLocation().start.cfi);
 assert.notEqual(after,before,'page turn advances');
 await page.evaluate(()=>rendition.prev());
 assert.equal(await page.evaluate(()=>rendition.currentLocation().start.cfi),before,'page back restores location');
 await page.screenshot({path:path.join(out,'epub-paginated.png')});
 console.log('EPUB font fallback');
 await page.setViewport({width:390,height:844});await page.goto(origin);
 const fontHrefs=await page.evaluate(async()=>{
  window.book=ePub(await fetch('/book.epub').then(r=>r.arrayBuffer()));await book.ready;
  window.rendition=book.renderTo('reader',{width:'100%',height:'100%',flow:'scrolled-doc',spread:'none'});
  rendition.themes.fontSize('150%');
  return book.spine.spineItems.filter(item=>/ch\d+\.xhtml$/.test(item.href)).map(item=>item.href);
 });
 for(const family of ['serif','sans-serif'])for(const href of fontHrefs){
  const result=await page.evaluate(async({family,href})=>{
   rendition.themes.font('BookMissingFontFixture, '+family);
   await rendition.display(href);
   const c=rendition.getContents()[0],d=c.document;await d.fonts.ready;
   return {href,family,font:c.window.getComputedStyle(d.body).fontFamily,
    width:c.window.innerWidth,scrollWidth:d.documentElement.scrollWidth,
    hasChinese:/[\u4e00-\u9fff]/.test(d.body.textContent)};
  },{family,href});
  assert(result.font.includes(family)&&result.hasChinese&&result.scrollWidth<=result.width+1,JSON.stringify(result));
  report.fonts.push(result);
 }
 await page.screenshot({path:path.join(out,'epub-font-fallback.png')});
 assert.deepEqual(external,[],'reader uses only local resources');assert.deepEqual(errors,[],'reader script errors');

 console.log('Print figure labels');
 await page.setViewport({width:673,height:1123});await page.emulateMediaType('print');
 await page.goto(pathToFileURL(path.join(root,'build/tmp/book.html')).href);
 const figures=await page.$$eval('.book-figure',elements=>elements.map(el=>({id:el.id,src:el.querySelector('img').src,width:el.querySelector('img').getBoundingClientRect().width})));
 const svgPage=await browser.newPage();
 for(const figure of figures){
  await svgPage.goto(figure.src);
  const result=await svgPage.evaluate(()=>{
   const svg=document.querySelector('svg'),view=svg.viewBox.baseVal;
   const texts=[...svg.querySelectorAll('text')].filter(el=>/[\u4e00-\u9fff]/.test(el.textContent));
   return {viewWidth:view.width,minFont:Math.min(...texts.map(el=>parseFloat(getComputedStyle(el).fontSize))),labels:texts.length};
  });
  const points=result.minFont*figure.width/result.viewWidth*.75;
  assert(result.labels>0&&points>=8.5,`${figure.id}: ${points.toFixed(2)}pt`);
  report.printFigures.push({id:figure.id,chineseLabels:result.labels,minPoints:Math.round(points*100)/100});
 }
 assert.equal(report.printFigures.length,figureCount);
 await writeFile(path.join(out,'report.json'),JSON.stringify(report,null,2)+'\n');
 console.log(`PASS: ${report.reflow.length} chapter/viewport/font cases; ${report.navigation.length} reader anchors; ${report.originals.length} image pages and return links; forward/back pagination; ${figures.length} print figures >=8.5pt.`);
}finally{await browser.close();await new Promise(resolve=>server.close(resolve))}
