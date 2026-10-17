// Dependency-free behavior checks for the inline player. Not a browser/media test.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

class Element {
  constructor() { this.listeners = {}; this.attrs = {}; this.children = []; this.textContent = ''; }
  addEventListener(name, callback) { (this.listeners[name] ??= []).push(callback); }
  emit(name, event = {}) { for (const callback of this.listeners[name] ?? []) callback(event); }
  append(...children) { this.children.push(...children); }
  setAttribute(name, value) { this.attrs[name] = value; }
  closest() { return false; }
  click() { this.emit('click'); }
}

async function main() {
  const page = fs.readFileSync(process.argv[2], 'utf8');
  const script = page.match(/<script>([\s\S]*?)<\/script>/)[1];
  const nodes = Object.fromEntries(['player', 'position', 'spoken', 'status', 'repeat', 'beats', 'previous', 'next', 'speed', 'chapters', 'resume', 'lessonbadge', 'previousslide', 'nextslide', 'captions', 'search', 'searchstatus'].map(id => [id, new Element()]));
  const player = nodes.player;
  Object.assign(player, { currentTime: 0, duration: 6, paused: true, seeking: false,
    play() { this.paused = false; return Promise.resolve(); }, pause() { this.paused = true; } });
  const document = new Element();
  document.querySelector = selector => nodes[selector.slice(1)];
  document.createElement = () => new Element();
  const beats = [0, 2, 4].map((start, i) => ({ start, end: start + 2, text: `Narration ${i}`, purpose: 'teach', effect: 'none', target_text: '<script>not markup</script>' }));
  const track = { kind: 'subtitles', mode: 'showing' };
  player.textTracks = [track]; player.textTracks.addEventListener = () => {};
  const store = new Map();
  vm.runInNewContext(script, { document, localStorage: { getItem: key => store.get(key) || null, setItem: (key, value) => store.set(key, value) }, fetch: async () => ({ ok: true, json: async () => ({ slides: [{ index: 1, title: 'Trung vị', start: 0, end: 4, beats: beats.slice(0,2) }, { index: 2, title: 'Biểu đồ', start: 4, end: 6, beats: beats.slice(2) }] }) }) });
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(nodes.beats.children.length, 3);
  assert.equal(nodes.beats.children[0].children[1].textContent, '<script>not markup</script>');
  nodes.next.click();
  assert.equal(player.currentTime, 2);
  player.emit('timeupdate');
  assert.equal(nodes.beats.children[1].attrs['aria-current'], 'true');
  assert.equal(nodes.spoken.textContent, 'Narration 1');
  nodes.repeat.click();
  assert.equal(nodes.repeat.attrs['aria-pressed'], 'true');
  player.currentTime = 4.1; player.emit('timeupdate');
  assert.equal(player.currentTime, 2);
  nodes.next.click(); player.emit('seeked');
  assert.equal(player.currentTime, 4);
  player.currentTime = 6; player.paused = true; player.emit('ended');
  assert.equal(player.currentTime, 4);
  assert.equal(player.paused, false);
  player.currentTime = 0; player.emit('seeked');
  assert.equal(nodes.repeat.attrs['aria-pressed'], 'false');
  nodes.speed.emit('change', { target: { value: '1.5' } });
  assert.equal(player.playbackRate, 1.5);
  function key(value, target = new Element(), extra = {}) {
    let prevented = false;
    document.emit('keydown', { key: value, target, preventDefault() { prevented = true; }, ...extra });
    return prevented;
  }
  assert.equal(key(' '), true); assert.equal(player.paused, true);
  key(']'); assert.equal(player.currentTime, 2);
  key('['); assert.equal(player.currentTime, 0);
  key('ArrowLeft'); assert.equal(player.currentTime, 0);
  key('ArrowRight'); assert.equal(player.currentTime, 5);
  assert.equal(key(' ', { closest: () => true }), false);
  assert.equal(key(' ', new Element(), { ctrlKey: true }), false);
  nodes.previous.click(); assert.equal(player.currentTime, 4);
  player.play = () => Promise.reject(new Error('blocked'));
  nodes.beats.children[0].click();
  await new Promise(resolve => setImmediate(resolve));
  assert.match(nodes.status.textContent, /Play/);
  player.play = function() { this.paused = false; return Promise.resolve(); };
  player.currentTime = 0;
  nodes.nextslide.click(); assert.equal(player.currentTime, 4);
  nodes.previousslide.click(); assert.equal(player.currentTime, 0);
  nodes.chapters.emit('change', {target: {value: '2'}}); assert.equal(player.currentTime, 4);
  nodes.captions.click(); assert.equal(track.mode, 'disabled');
  nodes.captions.click(); assert.equal(track.mode, 'showing');
  nodes.search.emit('input', { target: { value: 'trung vi' } });
  assert.equal(nodes.beats.children.filter(e => !e.hidden).length, 2);
  nodes.search.emit('input', { target: { value: 'bieu do' } });
  assert.equal(nodes.beats.children.filter(e => !e.hidden).length, 1);
  assert.match(nodes.searchstatus.textContent, /1 \/ 3/);
  nodes.search.emit('input', { target: { value: 'not found' } });
  assert.equal(nodes.beats.children.filter(e => !e.hidden).length, 0);
  nodes.search.emit('input', { target: { value: '' } });
  assert.equal(nodes.beats.children.filter(e => !e.hidden).length, 3);
  player.emit('pause'); assert.ok(store.size > 0);
  player.currentTime = 6; player.ended = true; player.emit('ended');
  assert.match(nodes.position.textContent, /hết bài/);
  assert.equal(JSON.parse([...store.values()][0]).time, 0);
  player.error = { code: 4 }; player.emit('error'); assert.match(nodes.status.textContent, /mã 4/);
}
main().catch(error => { console.error(error); process.exitCode = 1; });