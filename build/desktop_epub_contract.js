(async()=>{
 const result={reader:'Neat Reader 9.0.11',spines:[],toc:[],originals:[],fonts:[],images:[]};
 const viewer=NeatEpubViewer.viewer(),initial={...window.userSetting};
 const pause=ms=>new Promise(r=>setTimeout(r,ms));
 const jump=index=>new Promise((resolve,reject)=>{const t=setTimeout(()=>reject(new Error('spine timeout '+index)),7000);viewer.jumpToPositionBySpineIndexAndProgress(index,0,()=>{clearTimeout(t);resolve()})});
 const href=target=>new Promise((resolve,reject)=>{const t=setTimeout(()=>reject(new Error('link timeout '+target)),7000);viewer.jumpToPositionByHref(target,()=>{clearTimeout(t);resolve()})});
 const checkImages=async()=>{const imgs=[...document.querySelectorAll('.nr_spine_section img')];await Promise.all(imgs.map(img=>img.complete?Promise.resolve():new Promise((r,j)=>{img.onload=r;img.onerror=j})));if(imgs.some(img=>!img.naturalWidth))throw new Error('broken image');return imgs.map(img=>({src:img.src.replace(/^.*\/EPUB\//,'EPUB/'),width:img.naturalWidth,height:img.naturalHeight}));};
 try {
  for(const index of [0,...Array.from({length:36},(_,i)=>i+3)]){
   await jump(index);const s=document.querySelector('.nr_spine_section');
   if(!s||Number(s.getAttribute('spineIndex'))!==index)throw new Error('wrong chapter '+index);
   const images=await checkImages();
   const links=[...s.querySelectorAll('a')].filter(a=>a.textContent.includes('原图')||a.textContent.includes('返回正文')).map(a=>({text:a.textContent,href:a.getAttribute('href')}));
   result.spines.push({index,text:s.textContent.length,images,links});
  }
  const flatten=items=>items.flatMap(item=>[item,...flatten(item.children||[])]);
  for(const t of flatten(currentBookTocList).filter(t=>/reader-index|四项验收|两仓身份/.test(t.href))){
   await href(t.href);result.toc.push({title:t.title,position:NeatEpubViewer.getCurrentPositionInfo()});
  }
  // Follow every actual original-page link and its actual return target.
  for(const section of result.spines.filter(s=>s.index>=3&&s.index<=13)){
   for(const link of section.links.filter(l=>l.text.includes('原图'))){
    await jump(section.index);
    const original=[...document.querySelectorAll('.nr_spine_section a')].find(a=>a.getAttribute('href')===link.href);
    original.click();await pause(100);await checkImages();
    const a=[...document.querySelectorAll('.nr_spine_section a')].find(a=>a.textContent.includes('返回正文'));
    if(!a)throw new Error('missing return');const back=a.getAttribute('href');
    a.click();await pause(100);
    if(NeatEpubViewer.getCurrentPositionInfo().spineIndex!==section.index)throw new Error('return click failed');
    result.originals.push({original:link.href,back,position:NeatEpubViewer.getCurrentPositionInfo()});
   }
  }
  for(const size of [16,24]){
   viewer.setBookContentStyle({...initial,fontSize:size});await jump(12);await pause(120);
   const p=document.querySelector('.nr_spine_section p');
   result.fonts.push({requested:size,actual:parseFloat(getComputedStyle(p).fontSize),position:NeatEpubViewer.getCurrentPositionInfo()});
  }
  viewer.setBookContentStyle(initial);await jump(7);
  const before=NeatEpubViewer.getCurrentPositionInfo();viewer.goToNextPages();await pause(650);
  const next=NeatEpubViewer.getCurrentPositionInfo();viewer.goToPrevPages();await pause(650);
  const back=NeatEpubViewer.getCurrentPositionInfo();
  if(next.pageIndex===before.pageIndex||back.pageIndex!==before.pageIndex)throw new Error('page navigation failed');
  result.pagination={before,next,back};
  await jump(0);
  result.passed=true;window.bookAcceptance=result;return result;
 } finally {viewer.setBookContentStyle(initial)}
})()
