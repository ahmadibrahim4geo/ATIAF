// Headless offline browser test; does not control the user's browser or GIS windows.
import {spawn} from 'node:child_process';
import {readFileSync,writeFileSync,mkdirSync,mkdtempSync} from 'node:fs';
import {resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
const root=resolve(import.meta.dirname,'..');
const output=resolve(root,'dist','documentation-check-'+Date.now());mkdirSync(output,{recursive:true});
const chrome=process.env.ATIAF_TEST_CHROME || 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const html=readFileSync(resolve(root,'documentation/index.html'),'utf8').replaceAll('src="assets/','src="'+pathToFileURL(resolve(root,'documentation/assets')).href+'/');
const proof=`<script>window.addEventListener('load',()=>{const result={};result.images=[...document.images].every(i=>i.complete&&i.naturalWidth>0);result.logoBeforeBanner=document.querySelector('.logo').compareDocumentPosition(document.querySelector('.banner'))&Node.DOCUMENT_POSITION_FOLLOWING?true:false;result.initialCards=document.querySelectorAll('#catalog article').length;document.getElementById('language').click();result.english=document.documentElement.lang==='en'&&document.documentElement.dir==='ltr';document.getElementById('search').value='NDWI_MCFEETERS';document.getElementById('search').dispatchEvent(new Event('input'));result.searchCount=document.querySelectorAll('#catalog article').length;document.getElementById('search').value='';document.getElementById('search').dispatchEvent(new Event('input'));document.getElementById('toolFilter').value='thermal_urban';document.getElementById('toolFilter').dispatchEvent(new Event('change'));result.toolFilterCount=document.querySelectorAll('#catalog article').length;document.getElementById('toolFilter').value='';document.getElementById('toolFilter').dispatchEvent(new Event('change'));document.getElementById('language').click();result.arabic=document.documentElement.lang==='ar'&&document.documentElement.dir==='rtl';result.noHorizontalOverflow=document.documentElement.scrollWidth<=window.innerWidth;result.allPass=result.images&&result.logoBeforeBanner&&result.initialCards>30&&result.english&&result.arabic&&result.searchCount===1&&result.toolFilterCount===3&&result.noHorizontalOverflow;const p=document.createElement('pre');p.id='atiaf-proof';p.hidden=true;p.textContent=JSON.stringify(result);document.body.appendChild(p);});</script>`;
const page=resolve(output,'test.html');writeFileSync(page,html.replace('</body>',proof+'</body>'));
let failed=false;
for(const [name,width,height] of [['desktop',1400,1100],['mobile',390,844]]){
 const profile=mkdtempSync(resolve(output,'profile-'));
 const child=spawn(chrome,['--headless=new','--disable-gpu','--no-first-run','--disable-background-networking','--disable-extensions','--no-default-browser-check','--host-resolver-rules=MAP * ~NOTFOUND',`--user-data-dir=${profile}`,'--remote-debugging-port=0','--remote-debugging-address=127.0.0.1','--allow-file-access-from-files','about:blank'],{windowsHide:true,stdio:'ignore'});
 let socket,send,data;
 const delay=ms=>new Promise(r=>setTimeout(r,ms));
 try{
  let portInfo;
  for(let i=0;i<150;i++){try{portInfo=readFileSync(resolve(profile,'DevToolsActivePort'),'utf8').trim().split('\n');break;}catch{}await delay(50);}
  if(!portInfo)throw Error('Headless browser did not expose a local test endpoint');
  socket=new WebSocket(`ws://127.0.0.1:${portInfo[0]}/${portInfo[1].replace(/^\//,'')}`);
  await new Promise((ok,bad)=>{socket.onopen=ok;socket.onerror=bad;});
  let next=0;const pending=new Map();
  socket.onmessage=event=>{const reply=JSON.parse(event.data);if(reply.id&&pending.has(reply.id)){const p=pending.get(reply.id);pending.delete(reply.id);clearTimeout(p.timer);reply.error?p.bad(Error(reply.error.message)):p.ok(reply.result);}};
  send=(method,params={},sessionId)=>new Promise((ok,bad)=>{const id=++next;const timer=setTimeout(()=>{pending.delete(id);bad(Error('CDP timeout: '+method));},10000);pending.set(id,{ok,bad,timer});socket.send(JSON.stringify({id,method,params,...(sessionId?{sessionId}:{})}));});
  const target=await send('Target.createTarget',{url:'about:blank'});
  const {sessionId}=await send('Target.attachToTarget',{targetId:target.targetId,flatten:true});
  await send('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:name==='mobile'},sessionId);
  await send('Page.enable',{},sessionId);
  await send('Page.navigate',{url:pathToFileURL(page).href},sessionId);
  for(let i=0;i<100;i++){
   const result=await send('Runtime.evaluate',{expression:"document.getElementById('atiaf-proof')?.textContent",returnByValue:true},sessionId);
   if(result.result.value){data=JSON.parse(result.result.value);break;}await delay(50);
  }
  if(!data)throw Error('Page JavaScript did not produce test evidence');
  const viewport=await send('Runtime.evaluate',{expression:'JSON.stringify({width:innerWidth,height:innerHeight,scrollWidth:document.documentElement.scrollWidth})',returnByValue:true},sessionId);
  data.viewport=JSON.parse(viewport.result.value);data.allPass&&=data.viewport.width===width&&data.viewport.scrollWidth<=width;
  const presentation=await send('Runtime.evaluate',{expression:"JSON.stringify({hostCards:document.querySelectorAll('.host').length,methodCount:Number(document.getElementById('methodTotal').textContent),hostLinks:[...document.querySelectorAll('.host .guide')].every(a=>a.href.endsWith('/ar/INSTALLATION.html')),localizedSearch:document.getElementById('search').getAttribute('aria-label')==='البحث داخل دليل الحسابات',versionRendered:!document.documentElement.innerHTML.includes('__VERSION__')})",returnByValue:true},sessionId);
  data.presentation=JSON.parse(presentation.result.value);data.allPass&&=data.presentation.hostCards===2&&data.presentation.methodCount===data.initialCards&&data.presentation.hostLinks&&data.presentation.localizedSearch&&data.presentation.versionRendered;
  const shot=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false},sessionId);
  writeFileSync(resolve(output,name+'.png'),Buffer.from(shot.data,'base64'));
  await send('Runtime.evaluate',{expression:"window.scrollTo({top:document.getElementById('installation').offsetTop-24,behavior:'instant'})"},sessionId);
  const installShot=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false},sessionId);
  writeFileSync(resolve(output,name+'-installation.png'),Buffer.from(installShot.data,'base64'));
 }catch(error){data={allPass:false,error:String(error)};}
 finally{if(send)try{await send('Browser.close');}catch{}socket?.close();if(child.exitCode===null)child.kill();}
 writeFileSync(resolve(output,name+'.json'),JSON.stringify(data,null,2));console.log(name,JSON.stringify(data));if(!data.allPass)failed=true;
}
process.exitCode=failed?1:0;
