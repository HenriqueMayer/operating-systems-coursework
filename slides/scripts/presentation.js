'use strict';
const slides = Array.from(document.querySelectorAll('.slide'));
const prev = document.getElementById('prev');
const next = document.getElementById('next');
const notes = document.getElementById('notes');
const toggle = document.getElementById('notes-toggle');
let active = 0, seqStep = -1, mergeStep = 0;
document.body.classList.add('enhanced');
function showSlide(index, update=true) {
  active=Math.max(0,Math.min(slides.length-1,index));
  slides.forEach((s,i)=>{s.hidden=i!==active;});
  prev.disabled=active===0;next.disabled=active===slides.length-1;
  document.getElementById('progress').textContent=`${active+1} / ${slides.length}`;
  const n=NOTES[active];
  document.getElementById('notes-title').textContent=`${active+1}. ${n.title} · ${n.who} · ${n.seconds} s`;
  document.getElementById('notes-say').textContent=n.say;
  document.getElementById('notes-how').textContent=n.how;
  document.getElementById('notes-source').textContent=n.source;
  if(update) history.replaceState(null,'',`#slide-${active+1}`);
  window.scrollTo(0,0);
}
function setNotes(open) {notes.hidden=!open;toggle.setAttribute('aria-expanded',String(open));}
prev.addEventListener('click',()=>showSlide(active-1));
next.addEventListener('click',()=>showSlide(active+1));
toggle.addEventListener('click',()=>setNotes(notes.hidden));
document.getElementById('notes-close').addEventListener('click',()=>{setNotes(false);toggle.focus();});
async function fullscreen(){try{if(document.fullscreenElement)await document.exitFullscreen();else await document.documentElement.requestFullscreen();}catch(e){document.getElementById('fullscreen').textContent='Use F11';}}
document.getElementById('fullscreen').addEventListener('click',fullscreen);
document.getElementById('print').addEventListener('click',()=>window.print());
document.addEventListener('keydown',e=>{
 if(e.altKey||e.ctrlKey||e.metaKey||e.target.matches('input,textarea,select,[contenteditable]'))return;
 if(e.key==='ArrowRight'||e.key==='PageDown'){e.preventDefault();showSlide(active+1);}
 else if(e.key==='ArrowLeft'||e.key==='PageUp'){e.preventDefault();showSlide(active-1);}
 else if(e.key==='Home'){e.preventDefault();showSlide(0);}
 else if(e.key==='End'){e.preventDefault();showSlide(slides.length-1);}
 else if(e.key.toLowerCase()==='r')setNotes(notes.hidden);
 else if(e.key.toLowerCase()==='f')fullscreen();
 else if(e.key==='Escape')setNotes(false);
});
function color(label,kind){
 if(!label)return '';
 const mapping=kind==='seq'?{1:'a',14:'b',21:'c'}:{7:'a',10:'b',28:'e',40:'c',41:'d'};
 return `group-${mapping[label]||'a'}`;
}
function draw(id,labels,kind){
 document.querySelectorAll(`#${id} .cell`).forEach(cell=>{
  const value=Number(cell.dataset.value),r=Number(cell.dataset.row),c=Number(cell.dataset.col);
  const label=labels?labels[r][c]:0;
  cell.className=`cell ${value?'filled':'zero'} ${color(label,kind)}`;
  cell.textContent=labels?(label||0):value;
 });
 const grid=document.getElementById(id);
 grid.setAttribute('aria-label',kind==='seq'?(labels?'Rótulos dos três componentes: 1, 14 e 21; acompanhe a contagem ao lado.':'Matriz inicial com três objetos.'):(labels?'Rótulos locais nas faixas: 7, 10, 28, 40 e 41. A união dos rótulos 10 e 28 resulta em quatro objetos.':'Exemplo 2, com quatro objetos e fronteira entre as linhas 3 e 4.'));
}
function renderSeq(){
 const f=FRAMES[seqStep];draw('seq-matrix',f?f.labels:null,'seq');
 document.getElementById('seq-text').textContent=f?f.text:'A matriz ainda não foi percorrida.';
 document.getElementById('seq-count').textContent=f?f.objects:0;
 document.getElementById('seq-stack').textContent=f?f.stack:0;
 document.getElementById('seq-next').disabled=seqStep===FRAMES.length-1;
}
document.getElementById('seq-next').addEventListener('click',()=>{seqStep=Math.min(FRAMES.length-1,seqStep+1);renderSeq();});
document.getElementById('seq-reset').addEventListener('click',()=>{seqStep=-1;renderSeq();});
document.getElementById('seq-end').addEventListener('click',()=>{seqStep=FRAMES.length-1;renderSeq();});
const mergeTexts=['A matriz inteira tem 4 objetos.','Busca local: 2 componentes na faixa superior e 3 na inferior. A soma é 5.','Contato diagonal une os rótulos 10 e 28: os dois são o mesmo objeto. A contagem passa de 5 para 4.','Os demais contatos entre 10 e 28 já têm o mesmo representante. A contagem continua em 4.'];
function renderMerge(){
 draw('merge-matrix',mergeStep===0?null:mergeStep===1?LOCAL:MERGED,'merge');
 document.getElementById('merge-text').textContent=mergeTexts[mergeStep];
 document.getElementById('merge-count').textContent=mergeStep===0?'Resultado esperado: 4':mergeStep===1?'Soma local: 2 + 3 = 5':'Consolidação: 5 − 1 = 4';
 document.getElementById('merge-next').disabled=mergeStep===3;
}
document.getElementById('merge-next').addEventListener('click',()=>{mergeStep=Math.min(3,mergeStep+1);renderMerge();});
document.getElementById('merge-reset').addEventListener('click',()=>{mergeStep=0;renderMerge();});
let savedPrint;
window.addEventListener('beforeprint',()=>{savedPrint=[seqStep,mergeStep];seqStep=FRAMES.length-1;mergeStep=3;renderSeq();renderMerge();});
window.addEventListener('afterprint',()=>{if(savedPrint){[seqStep,mergeStep]=savedPrint;renderSeq();renderMerge();}});
window.addEventListener('hashchange',()=>{const m=location.hash.match(/^#slide-(\d+)$/);if(m)showSlide(Number(m[1])-1,false);});
const initial=location.hash.match(/^#slide-(\d+)$/);showSlide(initial?Number(initial[1])-1:0,false);
renderSeq();renderMerge();
