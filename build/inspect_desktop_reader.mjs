// Local diagnostic for an explicitly launched desktop reader; no book changes.
import {readFileSync,writeFileSync} from 'node:fs';
const targets = await (await fetch('http://127.0.0.1:19331/json/list')).json();
console.log('Desktop reader connection:', targets.length, 'windows');
const selected = process.argv.indexOf('--target');
const pages=targets.filter(t=>t.type==='page'&&!t.url.includes('#/epubreaderworker'));
const target = selected>=0 ? pages.find(t=>t.url.includes(process.argv[selected+1])) : pages.find(t=>t.url.includes('#/epubreader')) || pages.find(t=>t.url.includes('#/library'));
if (!target) throw new Error('No active reader window');
const ws = new WebSocket(target.webSocketDebuggerUrl);
await new Promise((resolve,reject)=>{ws.onopen=resolve;ws.onerror=reject;});
let next=0;
const pending=new Map();
ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id&&pending.has(m.id)){const {resolve,reject}=pending.get(m.id);pending.delete(m.id);m.error?reject(new Error(JSON.stringify(m.error))):resolve(m.result);}};
function send(method,params={}) {return new Promise((resolve,reject)=>{const id=++next;const timer=setTimeout(()=>{pending.delete(id);reject(new Error(method+' timeout'));},90000);pending.set(id,{resolve:v=>{clearTimeout(timer);resolve(v);},reject:e=>{clearTimeout(timer);reject(e);}});ws.send(JSON.stringify({id,method,params}));});}
const page={
  evaluate:async fn=>{const r=await send('Runtime.evaluate',{expression:`(${fn})()`,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw new Error(JSON.stringify(r.exceptionDetails));return r.result.value;},
  screenshot:async ({path})=>{const r=await send('Page.captureScreenshot',{format:'png'});writeFileSync(path,Buffer.from(r.data,'base64'));},
};
try {
  const file=process.argv.indexOf('--eval-file');
  if(file>=0){
    const r=await send('Runtime.evaluate',{expression:readFileSync(process.argv[file+1],'utf8'),returnByValue:true,awaitPromise:true});
    if(r.result?.value?.reader)writeFileSync('build/tmp/live-acceptance/neat-report.json',JSON.stringify(r.result.value,null,2)+'\n');
    console.log(JSON.stringify(r));
    process.exitCode=r.exceptionDetails?1:0;
  } else {
  const expr=process.argv.indexOf('--eval');
  if(expr>=0){
    const r=await send('Runtime.evaluate',{expression:process.argv[expr+1],returnByValue:true,awaitPromise:true});
    console.log(JSON.stringify(r));
    process.exitCode=r.exceptionDetails?1:0;
  } else {
  if (process.argv.includes('--open') && target.url.includes('#/library')) {
    await page.evaluate(()=>{const el=document.querySelector('.books-image');el?.click();return !!el;}).then(x=>console.log('open',x));
  }
    const result = await page.evaluate(() => ({
      title: document.title, text: document.body.innerText.slice(0, 14000),
      controls: [...document.querySelectorAll('button,[title],input')].slice(0, 100)
        .map(x=>({tag:x.tagName,cls:x.className,title:x.title,text:x.innerText?.slice(0,100),type:x.type})),
      frames: [...document.querySelectorAll('iframe')].map(x=>({src:x.src,title:x.title})),
      globals: Object.keys(window).filter(x=>/book|rend|epub|reader/i.test(x)),
      viewer: window.NeatEpubViewer ? Object.getOwnPropertyNames(window.NeatEpubViewer) : [],
      settings: [...document.querySelectorAll('iframe')].map(x=>({attrs:[...x.attributes].map(a=>[a.name,a.value])})),
      viewerState: window.NeatEpubViewer?.viewer ? Object.getOwnPropertyNames(window.NeatEpubViewer.viewer) : [],
      spine:window.currentBookSpineItems,
    }));
    console.log(JSON.stringify(result,null,2));
    writeFileSync('build/tmp/live-acceptance/neat-inspection.json',JSON.stringify(result,null,2));
    const tree=await send('Page.getFrameTree');
    for(const child of tree.frameTree.childFrames||[]) {
      const {executionContextId}=await send('Page.createIsolatedWorld',{frameId:child.frame.id,worldName:'book-diagnostic'});
      const r=await send('Runtime.evaluate',{contextId:executionContextId,returnByValue:true,expression:`JSON.stringify({url:location.href,text:document.body.innerText.slice(0,1500),images:[...document.images].map(x=>({src:x.src,complete:x.complete,width:x.naturalWidth})),width:innerWidth,scroll:document.documentElement.scrollWidth,html:document.body.innerHTML.slice(0,1500)})`});
      console.log('FRAME',r.result.value);
    }
    await page.screenshot({path:'build/tmp/live-acceptance/screenshots/neat-initial.png'});
  }
  }
} finally { ws.close(); }
