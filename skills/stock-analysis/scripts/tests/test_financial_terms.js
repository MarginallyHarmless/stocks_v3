// Exercise tooltip lifecycle without a browser dependency.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
class Target {
  constructor(attrs={}) { this.attrs=attrs; this.events={}; this.hidden=true; this.style={}; this.offsetWidth=296; this.offsetHeight=120; }
  addEventListener(name,fn) { (this.events[name] ||= []).push(fn); }
  emit(name,props={}) { const event={target:this,preventDefault(){this.prevented=true},stopPropagation(){this.stopped=true},...props}; for(const fn of this.events[name] || [])fn(event); return event; }
  setAttribute(k,v){ this.attrs[k]=v; }
  getAttribute(k){ return this.attrs[k]; }
  getBoundingClientRect(){ return {left:300,top:700,bottom:720}; }
  closest(){ return this.isTerm ? this : null; }
}
const term=new Target({'aria-describedby':'tip'}); term.isTerm=true;
const tip=new Target(), language=new Target(), dialog=new Target();
const document=new Target(), window=new Target();
document.querySelectorAll=()=>[term];
document.querySelector=s=>s==='#language'?language:dialog;
document.getElementById=id=>{assert.equal(id,'tip');return tip};
let scheduled=null;
const ctx={document,window,innerWidth:320,innerHeight:800,setTimeout:fn=>{scheduled=fn;return 1},clearTimeout:()=>{scheduled=null}};
vm.runInNewContext(fs.readFileSync(path.join(__dirname,'../../assets/financial-terms.js'),'utf8'),ctx);
term.emit('pointerenter',{pointerType:'mouse'});
assert.equal(tip.hidden,false);assert.equal(term.attrs['aria-expanded'],'true');
assert.equal(tip.style.left,'12px');assert.equal(tip.style.top,'572px');
term.emit('pointerleave',{pointerType:'mouse'});assert.ok(scheduled);
tip.emit('pointerenter');assert.equal(scheduled,null);
const escape=document.emit('keydown',{key:'Escape'});
assert.equal(tip.hidden,true);assert.ok(escape.prevented && escape.stopped);
term.emit('focus');assert.equal(tip.hidden,false);
term.emit('blur');assert.equal(tip.hidden,true);
term.emit('click');term.emit('pointerleave',{pointerType:'touch'});
assert.equal(tip.hidden,false);assert.equal(scheduled,null);
document.emit('pointerdown',{target:new Target()});assert.equal(tip.hidden,true);
for(const [target,event] of [[document,'scroll'],[window,'resize'],[language,'change'],[dialog,'close']]){
 term.emit('click');target.emit(event);assert.equal(tip.hidden,true);
}
console.log('Financial terms: hover, focus, touch persistence, Escape, viewport bounds and dismissal passed.');
