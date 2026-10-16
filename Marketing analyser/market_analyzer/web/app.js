/* Front-end for the Tier 2/3 Expansion Analyzer. All calculations happen in Python (server.py). */
const $=s=>document.querySelector(s),$$=s=>[...document.querySelectorAll(s)];
const esc=s=>String(s).replace(/[&<>"']/g,c=>'&#'+c.charCodeAt(0)+';');
const M=v=>'₹'+(v/1e6).toFixed(1)+'M',n=v=>Math.round(v).toLocaleString('en-IN'),pc=v=>v.toFixed(1)+'%';
const CT=[['aov','Average order value',500,5000,100,v=>'₹'+n(v)],['conversion_rate','Conversion rate',.05,.6,.01,v=>Math.round(v*100)+'%'],['footfall_rate','Footfall rate',.02,.4,.01,v=>Math.round(v*100)+'%'],['setup_cost','Setup cost',5e6,6e7,1e6,M],['base_rent','Annual base rent',5e5,8e6,1e5,M],['staff_cost','Annual staff cost',1e6,8e6,1e5,M],['fixed_opex','Other fixed costs',5e5,4e6,1e5,M]];
const WT=[['market','Market size'],['income','Income strength'],['competition','Competition'],['rent','Rent affordability'],['infra','Infrastructure']];
const W0={market:25,income:25,competition:20,rent:15,infra:15};
const SCN={conservative:'Conservative',base:'Base',optimistic:'Optimistic'};
const S={inputs:{},cities:[],scen:'base',tier:'all',state:'all',sort:'roi',w:{...W0},open:null,pins:[],picks:[],revealed:false,d:null};
let timer;const dots=new Map();

async function post(u,b){const r=await fetch(u,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(b)});const j=await r.json();if(!r.ok)throw new Error(j.error||'Request failed');return j}
function toast(m){const t=$('#toast');t.textContent=m;t.style.display=m?'block':'none';if(m)setTimeout(()=>t.style.display='none',4000)}
function refresh(){clearTimeout(timer);timer=setTimeout(go,50)}
async function go(extra){try{S.d=await post('/api/analyze',{inputs:S.inputs,cities:S.cities,scenario:S.scen,sort:S.sort,tier:S.tier,state:S.state,weights:S.w,...extra});render();return S.d}catch(e){toast(e.message)}}
const cityRow=nm=>S.cities.find(c=>c.city.toLowerCase()==nm.toLowerCase())||{};

/* ---------- Explore ---------- */
function render(){const d=S.d;
 $('#state').innerHTML='<option value="all">All states</option>'+d.states.map(s=>`<option ${s==S.state?'selected':''}>${esc(s)}</option>`).join('');
 $('#seg').innerHTML=Object.keys(SCN).map(s=>`<button data-s="${s}" aria-pressed="${s==S.scen}">${SCN[s]}</button>`).join('');
 $$('th.s').forEach(t=>t.classList.toggle('on',t.dataset.k==S.sort));
 const R=d.results;
 if(!R.length){$('#rows').innerHTML='<tr><td colspan="8" class="empty">No cities match. Try another tier or state.</td></tr>';$('#kpis').innerHTML='';$('#srows').innerHTML='';chart();dataView();return}
 const s=d.summary,best=R.reduce((a,b)=>b.roi>a.roi?b:a),robust=d.scenarios.filter(x=>x.robust).length;
 $('#kpis').innerHTML=[['Worth opening in',s.profitable+' of '+s.cities_analyzed],['Best ROI',esc(best.name)+' '+pc(best.roi)],['Median ROI',pc(s.median_roi_pct)],['Robust picks',robust]].map(k=>`<div class="kpi"><small>${k[0]}</small><div>${k[1]}</div></div>`).join('');
 const mx=Math.max(...R.map(r=>Math.abs(r.roi)),1);
 $('#rows').innerHTML=R.map(r=>{const neg=r.profit<=0,o=S.open==r.name;
  return`<tr class="row" tabindex="0" data-c="${esc(r.name)}"><td><input class="pn" type="checkbox" data-p="${esc(r.name)}" ${S.pins.includes(r.name)?'checked':''} aria-label="Pin ${esc(r.name)}"></td><td class="rk">${r.rank}</td><td class="city"><b>${esc(r.name)}${neg?'<em class="tag l">Loss-making</em>':''}</b><span>${esc(r.state)}, Tier ${r.tier}</span></td><td>${M(r.revenue)}</td><td class="${neg?'neg':'pos'}">${M(r.profit)}</td><td>${r.payback==null?'Never':r.payback.toFixed(2)+' yrs'}</td><td><div class="roi ${r.roi<0?'neg':''}"><i style="width:${Math.abs(r.roi)/mx*80}px"></i><b>${pc(r.roi)}</b></div></td><td>${r.feas.toFixed(1)}/100</td></tr>`+(o?detail(r):'')}).join('');
 $('#srows').innerHTML=d.scenarios.map(x=>{const ch=x.change;return`<tr><td class="rk">${x.rank[1]}</td><td class="city"><b>${esc(x.city)}</b></td>${x.roi.map(v=>`<td class="${v<0?'neg':''}">${pc(v)}</td>`).join('')}<td>${x.rank.join(' / ')}</td><td>${x.robust?'<span class="tag">Robust</span>':ch?'Rank shifts by '+ch:'Stable'}</td></tr>`}).join('');
 chart();radar();picks();dataView()}
function detail(r){const U=S.d.used,c=cityRow(r.name),f=(a,b)=>`<p class="f">${a}<br><b>${b}</b></p>`;
 return`<tr class="det"><td colspan="8"><div class="dg"><div><h3>How the numbers are built</h3>
 ${f('Addressable population',n(c.population||0)+' x '+(c.target_income_share??'')+' = '+n(r.addr))}${f('Annual visitors',n(r.addr)+' x '+U.footfall_rate.toFixed(3)+' = '+n(r.vis))}
 ${f('Annual revenue',n(r.vis)+' x '+U.conversion_rate.toFixed(3)+' x ₹'+n(U.aov)+' = ₹'+n(r.revenue))}
 ${f('Operating cost','(₹'+n(U.base_rent)+' x '+(c.rent_index??'')+') + ₹'+n(U.staff_cost)+' + ₹'+n(U.fixed_opex)+' = ₹'+n(r.opex))}
 ${f('Net profit','₹'+n(r.revenue)+' - ₹'+n(r.opex)+' = ₹'+n(r.profit))}
 ${f('Payback and ROI',(r.payback==null?'Never (profit is not positive)':'₹'+n(U.setup_cost)+' / ₹'+n(r.profit)+' = '+r.payback.toFixed(2)+' years')+', ROI '+pc(r.roi))}</div>
 <div><h3>Feasibility ${r.feas.toFixed(1)} out of 100</h3>${r.bd.map(l=>`<div class="sc"><div><span>${l[0]}</span><b>${l[1]}/${l[2]}</b></div><u><i style="width:${l[2]?l[1]/l[2]*100:0}%"></i></u><small>${esc(l[3])}</small></div>`).join('')}</div></div></td></tr>`}

/* ---------- Bubble chart (circles are reused so they glide to new positions) ---------- */
function chart(){const R=S.d.results,svg=$('#chart');if(!$('#dots')){svg.innerHTML='<g id="ax"></g><g id="dots"></g>'}
 const g=$('#dots');if(!R.length){g.innerHTML='';dots.clear();return}
 const fx=R.map(r=>r.feas),ro=R.map(r=>r.roi),x0=Math.min(...fx)-4,x1=Math.max(...fx)+4,y0=Math.min(0,...ro)-15,y1=Math.max(...ro)+20,mr=Math.max(...R.map(r=>r.revenue));
 const X=v=>55+(v-x0)/(x1-x0)*565,Y=v=>262-(v-y0)/(y1-y0)*246;let ax='';
 for(let i=0;i<=4;i++){const v=y0+(y1-y0)*i/4;ax+=`<line x1="55" x2="620" y1="${Y(v)}" y2="${Y(v)}" stroke="var(--line)"/><text x="48" y="${Y(v)+4}" text-anchor="end">${Math.round(v)}%</text>`}
 for(let i=0;i<=4;i++){const v=x0+(x1-x0)*i/4;ax+=`<text x="${X(v)}" y="284" text-anchor="middle">${Math.round(v)}</text>`}
 ax+=`<line x1="55" x2="620" y1="${Y(0)}" y2="${Y(0)}" stroke="var(--mute)" stroke-dasharray="4 4"/><text x="620" y="${Y(0)-5}" text-anchor="end">break-even</text><text x="337" y="298" text-anchor="middle">Feasibility score</text>`;
 $('#ax').innerHTML=ax;const names=new Set(R.map(r=>r.name));
 for(const[k,el]of dots)if(!names.has(k)){el.remove();dots.delete(k)}
 R.forEach(r=>{let el=dots.get(r.name);if(!el){el=document.createElementNS('http://www.w3.org/2000/svg','circle');g.appendChild(el);dots.set(r.name,el);
  el.addEventListener('mousemove',e=>tip(e,el.dataset.n));el.addEventListener('mouseleave',()=>$('#tip').style.display='none');
  el.addEventListener('click',()=>{S.open=S.open==el.dataset.n?null:el.dataset.n;render();const row=document.querySelector(`tr.row[data-c="${CSS.escape(el.dataset.n)}"]`);row&&row.scrollIntoView({behavior:'smooth',block:'center'})})}
  el.dataset.n=r.name;el.setAttribute('cx',X(r.feas));el.setAttribute('cy',Y(r.roi));el.setAttribute('r',7+20*Math.sqrt(Math.max(r.revenue,0)/mr));
  el.setAttribute('fill',r.profit>0?'var(--good)':'var(--bad)');el.classList.toggle('sel',S.open==r.name)})}
function tip(e,nm){const r=S.d.results.find(x=>x.name==nm),t=$('#tip');if(!r)return;t.innerHTML=`<b>${esc(r.name)}</b><br>ROI ${pc(r.roi)} · Feasibility ${r.feas.toFixed(1)}<br>Profit ${M(r.profit)} · Rank ${r.rank}`;t.style.display='block';t.style.left=e.clientX+14+'px';t.style.top=e.clientY+14+'px'}

/* ---------- Compare (radar) ---------- */
function radar(){const ps=S.pins.map(nm=>S.d.results.find(r=>r.name==nm)).filter(Boolean),el=$('#radar');
 if(ps.length<2){el.innerHTML='<p class="empty">Tick the Pin box beside 2 or 3 cities in Explore, then come back here.</p>';return}
 const cx=170,cy=150,R=105,K=5,col=['#f2a900','#12805f','#cf3d3d'],pt=(i,v)=>[cx+R*v*Math.sin(2*Math.PI*i/K),cy-R*v*Math.cos(2*Math.PI*i/K)].map(x=>x.toFixed(1)).join(',');
 let s='<svg viewBox="0 0 340 310" style="max-width:420px;width:100%;display:block;margin:auto">';
 [.25,.5,.75,1].forEach(v=>s+=`<polygon points="${[0,1,2,3,4].map(i=>pt(i,v)).join(' ')}" fill="none" stroke="var(--line)"/>`);
 ps[0].bd.forEach((b,i)=>{const[x,y]=pt(i,1.22).split(',');s+=`<line x1="${cx}" y1="${cy}" x2="${pt(i,1).split(',')[0]}" y2="${pt(i,1).split(',')[1]}" stroke="var(--line)"/><text x="${x}" y="${y}" text-anchor="middle" font-size="11" fill="var(--mute)">${b[0]}</text>`});
 ps.forEach((r,j)=>s+=`<polygon points="${r.bd.map((b,i)=>pt(i,b[2]?b[1]/b[2]:0)).join(' ')}" fill="${col[j]}" fill-opacity=".22" stroke="${col[j]}" stroke-width="2"/>`);
 el.innerHTML=s+'</svg><div class="leg">'+ps.map((r,j)=>`<span><i style="background:${col[j]}"></i><b>${esc(r.name)}</b> ROI ${pc(r.roi)}, feasibility ${r.feas.toFixed(1)}, payback ${r.payback==null?'Never':r.payback.toFixed(1)+' yrs'}</span>`).join('')+'</div>'}

/* ---------- Beat the model ---------- */
function picks(){const R=[...S.d.results].sort((a,b)=>a.name.localeCompare(b.name)),top=[...S.d.results].sort((a,b)=>b.roi-a.roi).slice(0,3).map(r=>r.name);
 $('#picks').innerHTML=R.map(r=>{const on=S.picks.includes(r.name),cls=S.revealed?(on?(top.includes(r.name)?'hit':'miss'):(top.includes(r.name)?'hit':'')):(on?'on':'');
  return`<button class="pick ${cls}" data-pk="${esc(r.name)}" ${S.revealed?'disabled':''}><b>${esc(r.name)}</b><span>${esc(r.state)} · pop ${(cityRow(r.name).population/1e6||0).toFixed(2)}M${S.revealed?' · ROI '+pc(r.roi):''}</span></button>`}).join('');
 const b=$('#reveal');b.disabled=S.picks.length!=3;b.hidden=S.revealed;b.textContent=S.picks.length==3?'Reveal the results':'Pick '+(3-S.picks.length)+' more';$('#again').hidden=!S.revealed;
 if(!S.revealed){$('#result').innerHTML='';return}
 const by=nm=>S.d.results.find(r=>r.name==nm),mine=S.picks.map(by).filter(Boolean),hit=mine.filter(r=>top.includes(r.name)).length,avg=a=>a.reduce((s,r)=>s+r.roi,0)/a.length;
 $('#result').innerHTML=`<div class="res"><div><div class="big">${hit} of 3</div><p>${hit==3?'You matched the model exactly.':hit?'You found '+hit+' of the model\'s top 3.':'Your instincts and the numbers disagree.'}</p></div><div><p class="f">Your picks, average ROI<br><b>${pc(avg(mine))}</b></p><p class="f">Model's top 3: ${top.map(esc).join(', ')}<br><b>${pc(avg(top.map(by)))}</b></p></div></div>`}

/* ---------- Your data ---------- */
const FIELDS=[['city','City','text'],['state','State','text'],['tier','Tier','sel'],['population','Population','number'],['target_income_share','Income share (0-1)','number'],['avg_household_income','Avg household income','number'],['rent_index','Rent index','number'],['competition_level','Competition (1-5)','number'],['infrastructure_score','Infrastructure (1-10)','number']];
function dataView(){$('#clist').innerHTML=S.cities.map((c,i)=>`<tr><td class="city"><b>${esc(c.city)}</b><span>${esc(c.state)}</span></td><td>Tier ${c.tier}</td><td>${n(c.population)}</td><td><button class="x" data-rm="${i}" title="Remove">&times;</button></td></tr>`).join('');$('#count').textContent='('+S.cities.length+')';
 $('#warns').innerHTML=(S.d.errors||[]).map(e=>`<p class="warn">${esc(e)}</p>`).join('')+(S.warns||[]).map(e=>`<p class="warn">${esc(e)}</p>`).join('')}
async function loadCsv(file){try{const j=await post('/api/parse-csv',{text:await file.text()});S.cities=j.cities;S.warns=j.warnings;S.open=null;S.pins=[];S.picks=[];S.revealed=false;await go();toast('')}catch(e){toast(e.message)}}
async function download(fmt){const d=await go({export:true});if(!d||!d.export)return;const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([d.export[fmt]],{type:'text/plain'}));a.download='analyzer_report.'+fmt;a.click()}
async function reset(){const d=await (await fetch('/api/defaults')).json();S.cities=d.cities;S.inputs=d.inputs;S.warns=[];S.w={...W0};S.open=null;S.pins=[];S.picks=[];S.revealed=false;buildPanel();await go()}

/* ---------- Wiring ---------- */
function buildPanel(){
 $('#ctls').innerHTML=CT.map(([k,l,a,b,st,f])=>`<div class="ctl"><label for="${k}">${l}<b id="v_${k}">${f(+S.inputs[k])}</b></label><input type="range" id="${k}" min="${a}" max="${b}" step="${st}" value="${S.inputs[k]}"></div>`).join('');
 CT.forEach(([k,,,,,f])=>$('#'+k).addEventListener('input',e=>{S.inputs[k]=+e.target.value;$('#v_'+k).textContent=f(S.inputs[k]);refresh()}));
 const wl=()=>{const t=Object.values(S.w).reduce((a,b)=>a+b,0)||1;WT.forEach(([k])=>$('#wv_'+k).textContent=Math.round(S.w[k]/t*100)+' pts')};
 $('#wts').innerHTML=WT.map(([k,l])=>`<div class="ctl"><label for="w_${k}">${l}<b id="wv_${k}"></b></label><input type="range" id="w_${k}" min="0" max="50" value="${S.w[k]}"></div>`).join('');
 WT.forEach(([k])=>$('#w_'+k).addEventListener('input',e=>{S.w[k]=+e.target.value;wl();refresh()}));wl();
 $('#wreset').onclick=()=>{S.w={...W0};buildPanel();refresh()}}
function init(){
 $('#form').innerHTML=FIELDS.map(([k,l,t])=>`<div><label for="f_${k}">${l}</label>${t=='sel'?`<select id="f_${k}"><option>2</option><option>3</option></select>`:`<input id="f_${k}" type="${t}" step="any" required>`}</div>`).join('')+'<div style="align-self:end"><button class="btn">Add city</button></div>';
 $('#tabs').onclick=e=>{const v=e.target.dataset.v;if(!v)return;$$('#tabs button').forEach(b=>b.setAttribute('aria-pressed',b.dataset.v==v));$$('.view').forEach(x=>x.classList.toggle('on',x.id=='v-'+v))};
 $('#seg').onclick=e=>{if(e.target.dataset.s){S.scen=e.target.dataset.s;refresh()}};
 $('#tier').onchange=e=>{S.tier=e.target.value;refresh()};$('#state').onchange=e=>{S.state=e.target.value;refresh()};
 $('thead').onclick=e=>{const k=e.target.dataset.k;if(k){S.sort=k;refresh()}};
 const tog=e=>{if(e.target.closest('.pn'))return;const t=e.target.closest('tr.row');if(!t||(e.type=='keydown'&&e.key!='Enter'&&e.key!=' '))return;e.preventDefault();S.open=S.open==t.dataset.c?null:t.dataset.c;render()};
 $('#rows').onclick=tog;$('#rows').onkeydown=tog;
 $('#rows').onchange=e=>{const p=e.target.dataset.p;if(!p)return;S.pins=e.target.checked?[...S.pins,p].slice(-3):S.pins.filter(x=>x!=p);render();if(e.target.checked&&S.pins.length>=2)toast('')};
 $('#picks').onclick=e=>{const b=e.target.closest('.pick');if(!b||S.revealed)return;const p=b.dataset.pk;S.picks=S.picks.includes(p)?S.picks.filter(x=>x!=p):[...S.picks,p].slice(-3);picks()};
 $('#reveal').onclick=()=>{S.revealed=true;picks()};$('#again').onclick=()=>{S.revealed=false;S.picks=[];picks()};
 $('#form').onsubmit=async e=>{e.preventDefault();const row={};FIELDS.forEach(([k])=>row[k]=$('#f_'+k).value);$('#ferr').textContent='';S.cities.push(row);const d=await go();
  const bad=d&&d.errors.find(x=>x.toLowerCase().startsWith(row.city.toLowerCase()+':'));
  if(bad){S.cities.pop();await go();$('#ferr').textContent=bad}else if(d){const c=d.results.find(r=>r.name.toLowerCase()==row.city.trim().toLowerCase());e.target.reset();toast('');if(c){S.open=c.name;render()}}};
 $('#clist').onclick=async e=>{const i=e.target.dataset.rm;if(i!==undefined){S.cities.splice(+i,1);await go()}};
 const dr=$('#drop');dr.onclick=()=>$('#file').click();dr.onkeydown=e=>e.key=='Enter'&&$('#file').click();$('#file').onchange=e=>e.target.files[0]&&loadCsv(e.target.files[0]);
 dr.ondragover=e=>{e.preventDefault();dr.classList.add('over')};dr.ondragleave=()=>dr.classList.remove('over');dr.ondrop=e=>{e.preventDefault();dr.classList.remove('over');e.dataTransfer.files[0]&&loadCsv(e.dataTransfer.files[0])};
 $$('[data-x]').forEach(b=>b.onclick=()=>download(b.dataset.x));$('#reset').onclick=reset;
 $('#theme').onclick=()=>{const r=document.documentElement,dark=r.dataset.theme?r.dataset.theme=='dark':matchMedia('(prefers-color-scheme:dark)').matches;r.dataset.theme=dark?'light':'dark'};
 $('#tip').style.display='none';reset()}
init();
