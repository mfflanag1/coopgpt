(() => {
  const $ = id => document.getElementById(id);
  document.body.classList.add("js");
  if(location.protocol==='file:')document.querySelectorAll('a[href="coopgpt-mega-handoff.zip"]').forEach(a=>{const note=document.createElement('span');note.textContent='Offline bundle already extracted';a.replaceWith(note);});
  $("menu-toggle").addEventListener("click",()=>{const rail=document.querySelector(".rail");rail.classList.toggle("menu-open");$("menu-toggle").setAttribute("aria-expanded",String(rail.classList.contains("menu-open")));});
  const details = [...document.querySelectorAll('details')];
  details.forEach((d,i) => { if (!d.id) d.id = 'detail-'+i; });
  function reveal(node) {
    for (let p=node; p; p=p.parentElement) if(p.tagName==='DETAILS') p.open=true;
    node.scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth',block:'start'});
  }
  function followHash() {
    if(!location.hash) return;
    const node=$(decodeURIComponent(location.hash.slice(1)));
    if(node) reveal(node);
  }
  window.addEventListener('hashchange',followHash);
  if(location.hash) requestAnimationFrame(followHash);
  $('open-all').addEventListener('click',()=>details.forEach(d=>d.open=true));
  $('close-all').addEventListener('click',()=>details.forEach(d=>d.open=false));
  $('print').addEventListener('click',()=>window.print());
  let saved=[];
  window.addEventListener('beforeprint',()=>{saved=details.map(d=>[d,d.open]);details.forEach(d=>d.open=true);});
  window.addEventListener('afterprint',()=>saved.forEach(([d,open])=>d.open=open));
  const normal = s => s.normalize('NFKC').toLocaleLowerCase().replace(/\s+/g,' ').trim();
  const units=[...document.querySelectorAll('section.chapter,details.paper,details.audit-report,.inherited-section')];
  const index=units.map((node,i)=>{
    if(!node.id)node.id='search-section-'+i;
    const heading=node.querySelector('summary,h2,h3,h4');
    return {node,title:(heading?.textContent||'Research record').trim(),text:node.textContent.replace(/\s+/g,' ').trim(),norm:normal(node.textContent)};
  });
  $('book-search').addEventListener('input',()=>{
    const q=normal($('book-search').value);const list=$('search-results');list.replaceChildren();
    if(!q){list.hidden=true;$('search-status').textContent='Search includes folded chapters and historical records.';return;}
    const terms=q.split(' '), matches=index.filter(x=>terms.every(t=>x.norm.includes(t)));
    list.hidden=false;$('search-status').textContent=matches.length?`${matches.length} matching sections. Showing ${Math.min(matches.length,30)}; select one to open it.`:'No matching sections. Try fewer words.';
    matches.slice(0,30).forEach(x=>{
      const li=document.createElement('li'),button=document.createElement('button'),p=document.createElement('p');
      button.type='button';button.textContent=x.title;button.addEventListener('click',()=>{location.hash=x.node.id;reveal(x.node);});
      const at=normal(x.text).indexOf(terms[0]);const start=Math.max(0,at-80);p.textContent=(start?'…':'')+x.text.slice(start,start+250)+'…';
      li.append(button,p);list.append(li);
    });
  });
  function ideal(){const a=Number($('ideal-share').value)/100;$('ideal-label').textContent=a.toFixed(2);$('ideal-result').textContent=`Total funding ${Math.max(1,2*a).toFixed(2)}; extra subsidy ${Math.max(0,2*a-1).toFixed(2)}.`;}
  $('ideal-share').addEventListener('input',ideal);ideal();
  function gains(){const s=Number($('standalone').value),g=Number($('gain').value),cap=.5430633898250876*(s+g);$('standalone-label').textContent=s;$('gain-label').textContent=g;$('gain-result').textContent=`Extra-funding cap ${cap.toFixed(2)}; cap / cooperation gain ${(cap/g).toFixed(2)}×.`;}
  $('standalone').addEventListener('input',gains);$('gain').addEventListener('input',gains);gains();
  const oldTheta=$('old-energy-theta');
  if(oldTheta){const update=()=>{const t=Number(oldTheta.value)/100;$('old-energy-theta-formula').textContent=t.toFixed(2);$('old-energy-theta-value').textContent=`${Math.round(t*100)}%`;$('old-energy-funding').textContent=(1+t/4).toFixed(4)+'×';$('old-energy-subsidy').textContent=(t*25).toFixed(2)+'%';};oldTheta.addEventListener('input',update);update();}
  if($('old-overnight-s-range')){const update=()=>{const s=+$('old-overnight-s-range').value,g=+$('old-overnight-g-range').value,c=.5430633898250876;$('old-overnight-s-label').textContent=s;$('old-overnight-g-label').textContent=g;$('old-overnight-fund-cap').textContent=(c*(s+g)).toFixed(2);$('old-overnight-fund-ratio').textContent=(c*(s+g)/g).toFixed(2)+'×';};$('old-overnight-s-range').addEventListener('input',update);$('old-overnight-g-range').addEventListener('input',update);update();}
  const ladderSize=$('ladder-size'),ladderStage=$('ladder-stage');
  if(ladderSize && ladderStage){
    const svgNS='http://www.w3.org/2000/svg';
    function updateLadder(){
      const s=Number(ladderSize.value),last=2*s;
      ladderStage.max=String(last);
      if(Number(ladderStage.value)>last)ladderStage.value=String(last);
      const M=Number(ladderStage.value);let q=1/3;const values=[];
      for(let m=1;m<=last;m++){
        if(m>1){const k=Math.min(s-1,2*m-2);q*=k/(k+1);}
        values.push(1+2*(m-1)*q);
      }
      const val=values[M-1],peak=values[s-1];
      $('ladder-size-label').textContent=s;$('ladder-stage-label').textContent=M;
      $('ladder-result').textContent=`Forced total funding: ${val.toFixed(6)} × output. This ladder peaks at M=${s} or ${s+1}, at ${peak.toFixed(6)} ×.`;
      $('ladder-institution').textContent=`At M=${M}: ${2*M+1} fully eligible actual owners and ${(2**(M+1)-1).toLocaleString('en-US')} resource rows.`;
      $('ladder-chart-desc').textContent=`For protected size ${s}, the bound peaks at ${s} and ${s+1} branches, at ${peak.toFixed(6)} times output. Selected branch count ${M} forces ${val.toFixed(6)} times output.`;
      const layer=$('ladder-chart-marks');layer.replaceChildren();
      const x=m=>48+548*(m-1)/(last-1),y=v=>188-150*(v-1)/(peak*1.12-1);
      function mark(tag,attrs,text){const el=document.createElementNS(svgNS,tag);for(const [k,v] of Object.entries(attrs))el.setAttribute(k,v);if(text!==undefined)el.textContent=text;layer.append(el);return el;}
      mark('line',{x1:48,y1:188,x2:596,y2:188,stroke:'#a9b9c9'});
      mark('line',{x1:48,y1:25,x2:48,y2:188,stroke:'#a9b9c9'});
      mark('line',{x1:48,y1:y(peak),x2:596,y2:y(peak),stroke:'#a9b9c9','stroke-dasharray':'3 5'});
      mark('polyline',{points:values.map((v,i)=>`${x(i+1)},${y(v)}`).join(' '),fill:'none',stroke:'#236291','stroke-width':3,'stroke-linejoin':'round'});
      mark('circle',{cx:x(M),cy:y(val),r:6,fill:'#975416',stroke:'#fff','stroke-width':2});
      mark('text',{x:38,y:192,'text-anchor':'end'},'1×');
      mark('text',{x:38,y:y(peak)+5,'text-anchor':'end'},peak.toFixed(2)+'×');
      mark('text',{x:48,y:211,'text-anchor':'middle'},'1');
      mark('text',{x:x(s),y:211,'text-anchor':'middle'},String(s));
      mark('text',{x:596,y:211,'text-anchor':'middle'},String(last));
      mark('text',{x:322,y:229,'text-anchor':'middle'},'Number of branches M');
    }
    ladderSize.addEventListener('input',updateLadder);ladderStage.addEventListener('input',updateLadder);updateLadder();
  }
  if('IntersectionObserver' in window){const observer=new IntersectionObserver(entries=>{for(const e of entries)if(e.isIntersecting){document.querySelectorAll('.rail nav a').forEach(a=>a.removeAttribute('aria-current'));document.querySelector(`.rail nav a[href="#${e.target.id}"]`)?.setAttribute('aria-current','location');}},{rootMargin:'-5% 0px -75% 0px'});document.querySelectorAll('section.chapter').forEach(s=>observer.observe(s));}
})();
