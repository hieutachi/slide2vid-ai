// Real Chromium media smoke test via CDP. No dependencies; Node 22+.
// Headless/muted checks do not establish human listening or native mobile support.
const fs = require('node:fs');
const assert = require('node:assert/strict');
const pause = ms => new Promise(resolve => setTimeout(resolve, ms));

async function main() {
  const [url, out, port = '9226'] = process.argv.slice(2);
  const tabs = await (await fetch(`http://127.0.0.1:${port}/json`)).json();
  const tab = tabs.find(t => t.type === 'page');
  const ws = new WebSocket(tab.webSocketDebuggerUrl);
  await new Promise((resolve, reject) => {ws.onopen=resolve;ws.onerror=reject;});
  let id=0;
  const pending=new Map(), errors=[];
  ws.onmessage = message => {
    const data=JSON.parse(message.data);
    if(data.method==='Runtime.exceptionThrown')errors.push(data.params.exceptionDetails.text);
    if(data.id){const request=pending.get(data.id);pending.delete(data.id);data.error?request.reject(Error(JSON.stringify(data.error))):request.resolve(data.result);}
  };
  const call=(method,params={})=>new Promise((resolve,reject)=>{const key=++id;pending.set(key,{resolve,reject});ws.send(JSON.stringify({id:key,method,params}));});
  const evaluate=async expression=>{
    const result=await call('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});
    if(result.exceptionDetails)throw Error(JSON.stringify(result.exceptionDetails));
    return result.result.value;
  };
  const wait=async expression=>{for(let i=0;i<100;i++){if(await evaluate(expression))return;await pause(200);}throw Error(`Timed out: ${expression}`);};
  try {
    await call('Page.enable');await call('Runtime.enable');
    await call('Emulation.setDeviceMetricsOverride',{width:1440,height:1000,deviceScaleFactor:1,mobile:false});
    await call('Page.navigate',{url});
    await wait("document.querySelectorAll('#chapters option').length===24 && document.querySelector('#player').readyState>=2");
    assert.equal(await evaluate("document.querySelectorAll('#beats button').length"),48);
    assert.ok(await evaluate("[...document.querySelectorAll('#chapters option')].every(o=>o.textContent.split('. ').slice(1).join('. ').trim())"),'missing chapter titles');
    assert.ok(await evaluate("[...document.querySelectorAll('#beats button span')].every(e=>e.textContent.trim())"),'empty beat labels');
    await evaluate("document.querySelector('#search').value='trung vi';document.querySelector('#search').dispatchEvent(new Event('input'));true");
    const matches=await evaluate("[...document.querySelectorAll('#beats button')].filter(b=>!b.hidden).length");
    assert.ok(matches>0&&matches<48);
    await evaluate("document.querySelector('#search').value='';document.querySelector('#search').dispatchEvent(new Event('input'));const v=document.querySelector('#player');v.muted=true;v.playbackRate=2;v.play()");
    await pause(1400);
    assert.ok(await evaluate("document.querySelector('#player').currentTime>1 && !document.querySelector('#player').error"));
    await evaluate("document.querySelector('#player').pause();document.querySelector('#captions').click();true");
    assert.equal(await evaluate("document.querySelector('#player').textTracks[0].mode"),'disabled');
    await evaluate("document.querySelector('#captions').click();document.querySelector('#chapters').value='10';document.querySelector('#chapters').dispatchEvent(new Event('change'));true");
    await pause(600);
    await evaluate("document.querySelector('#player').pause();true");
    assert.equal(await evaluate("document.querySelector('#chapters').value"),'10');
    const savedTime=await evaluate("document.querySelector('#player').currentTime");
    const shot=await call('Page.captureScreenshot',{format:'png',captureBeyondViewport:true});
    fs.writeFileSync(`${out}/browser_desktop.png`,Buffer.from(shot.data,'base64'));
    await call('Page.reload');
    await wait("document.querySelector('#resume') && !document.querySelector('#resume').hidden");
    // Initial update must not erase the previous position before the user accepts it.
    await call('Page.reload');
    await wait("document.querySelector('#resume') && !document.querySelector('#resume').hidden");
    await evaluate("document.querySelector('#player').muted=true;document.querySelector('#resume').click();true");
    await pause(400);
    assert.ok(Math.abs(await evaluate("document.querySelector('#player').currentTime")-savedTime)<2);
    await evaluate("document.querySelector('#player').pause();document.querySelector('#player').currentTime=document.querySelector('#player').duration-0.25;document.querySelector('#player').play()");
    await wait("document.querySelector('#player').ended");
    assert.equal(await evaluate("document.querySelector('#position').textContent"),'Đã hết bài giảng');
    await call('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:1,mobile:true});
    await evaluate("document.querySelector('#player').currentTime=120;true");await pause(700);
    assert.ok(await evaluate("document.documentElement.scrollWidth<=window.innerWidth"),'mobile viewport has horizontal overflow');
    const mobile=await call('Page.captureScreenshot',{format:'png',captureBeyondViewport:true});
    fs.writeFileSync(`${out}/browser_mobile.png`,Buffer.from(mobile.data,'base64'));
    assert.deepEqual(errors,[]);
    fs.writeFileSync(`${out}/browser_validation.json`,JSON.stringify({
      browser:await evaluate('navigator.userAgent'),slides:24,beats:48,search_matches:matches,
      real_media_playback:true,captions_toggle:true,chapter_seek:true,resume_after_two_reloads:true,
      end_of_file:true,mobile_viewport_no_horizontal_overflow:true,javascript_errors:errors,
      human_listening_verified:false,native_mobile_device_tested:false,
    },null,2));
    console.log('Real Chromium media, captions, chapters, search, resume, EOF, mobile viewport: PASS');
  } finally {ws.close();}
}
main().catch(error=>{console.error(error);process.exitCode=1;});