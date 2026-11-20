// Compatibility images for readers that serve SVG with an incorrect MIME type.
// The EPUB also retains every vector original without changing its bytes.
import {readFile,writeFile} from 'node:fs/promises';
import {existsSync} from 'node:fs';
import {pathToFileURL} from 'node:url';
import puppeteer from 'puppeteer';

const manifestPath=process.argv[2];
const jobs=JSON.parse(await readFile(manifestPath,'utf8'));
const executablePath=[process.env.CHROME_PATH,process.env.PUPPETEER_EXECUTABLE_PATH,
  'C:/Program Files/Google/Chrome/Application/chrome.exe',
  'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
  '/usr/bin/google-chrome','/usr/bin/chromium'].find(p=>p&&existsSync(p));
if(!executablePath)throw new Error('Set CHROME_PATH');
const browser=await puppeteer.launch({executablePath,headless:true,
  args:process.env.CI?['--no-sandbox']:[]});
try {
 const page=await browser.newPage();
 for(const job of jobs){
  const scale=Math.min(3,4800/Math.max(job.width,job.height));
  await page.setViewport({width:Math.ceil(job.width),height:Math.ceil(job.height),deviceScaleFactor:scale});
  await page.goto(pathToFileURL(job.source).href);
  await page.evaluate(()=>document.fonts.ready);
  const svg=await page.$('svg');
  if(!svg)throw new Error('Missing SVG: '+job.source);
  await svg.screenshot({path:job.target,type:'png',omitBackground:false});
  job.scale=scale;
 }
 await writeFile(manifestPath,JSON.stringify(jobs,null,2)+'\n');
 console.log(`EPUB compatibility images: ${jobs.length}; vectors retained`);
} finally {await browser.close();}
