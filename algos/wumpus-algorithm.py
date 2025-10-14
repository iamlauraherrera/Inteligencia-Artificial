<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Wumpus – Visualizador</title>
<style>
:root { font-family: system-ui, -apple-system, Segoe UI, Roboto; }
body { margin:0; background:#0f172a; color:#e5e7eb; }
header { display:flex; align-items:center; padding:12px 16px; background:#111827; border-bottom:1px solid #1f2937; }
h1 { margin:0; font-size:1.05rem; color:#fafafa; }
.container{ max-width:1100px; margin:16px auto; padding:0 16px; display:grid; grid-template-columns: 1fr 360px; gap:16px; }
.card{ background:#111827; border:1px solid #1f2937; border-radius:14px; padding:16px; }
.title{ font-weight:600; color:#fafafa; margin-bottom:8px; }
#board.grid{ display:grid; gap:1px; background:#0b101d; padding:4px; border-radius:10px; }
.cell{ display:flex; align-items:center; justify-content:center; background:#1f2937; border-radius:4px; aspect-ratio:1/1; font-size:.85rem; }
.cell:hover{ filter:brightness(1.08); cursor:pointer; }
.btn{ background:#2563eb; color:#e5e7eb; border:1px solid #2563eb; border-radius:10px; padding:10px 14px; margin-right:8px; }
.btn.secondary{ background:#374151; border-color:#374151; }
.stat{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size:.92rem; color:#cbd5e1; }
.badge{ display:inline-block; padding:2px 6px; border-radius:6px; border:1px solid #374151; margin-right:4px; }
</style>
</head>
<body>
<header><h1>Wumpus – Visualizador</h1></header>

<div class="container">
  <div class="card">
    <div class="title">Mundo</div>
    <div id="board" class="grid"></div>
    <div style="margin-top:8px; color:#cbd5e1;">
      <span class="badge">A: Agente</span>
      <span class="badge">W: Wumpus</span>
      <span class="badge">P: Pozo</span>
      <span class="badge">G: Oro</span>
      <span class="badge">? : Desconocido</span>
    </div>
  </div>

  <div class="card">
    <div class="title">Controles</div>
    <div>
      <button class="btn" id="step">Paso</button>
      <button class="btn secondary" id="auto">Auto</button>
      <button class="btn secondary" id="reset">Reiniciar</button>
      <a class="btn secondary" href="/">Volver</a>
    </div>
    <div class="title" style="margin-top:10px;">Percepciones</div>
    <div id="percep" class="stat"></div>
    <div class="title" style="margin-top:10px;">Estado</div>
    <div id="stat" class="stat"></div>
  </div>
</div>

<script>
const name = "wumpus-algorithm.py";
const board = document.getElementById('board');
const stat = document.getElementById('stat');
const percep = document.getElementById('percep');
const N = 6; // tamaño por defecto de la grilla (render)

let autoTimer = null;

async function j(url, opts={}){ const r = await fetch(url, opts); return r.json(); }
async function getState(){ return j(`/api/${name}/state`); }
async function act(action, payload={}){
  return j(`/api/${name}/act`, {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({action, ...payload})});
}
async function restart(){ return j(`/api/${name}/restart`, {method:'POST'}); }

function draw(state){
  // estado esperado (opcional):
  // { n, celdas:[code por celda], agente:{i,j,orient}, percepciones:['brisa','hedor'...], msg:'' }
  const n = state.n || N;
  board.innerHTML = '';
  board.style.gridTemplateColumns = `repeat(${n},1fr)`;

  for (let i=0;i<n*n;i++){
    const d = document.createElement('div');
    d.className = 'cell';
    const code = (state.celdas && state.celdas[i]) || 0;
    // 0: ?, 1: libre, 2: pozo, 3: wumpus, 4: oro, 5: agente
    if (code===2) d.textContent='P';
    if (code===3) d.textContent='W';
    if (code===4) d.textContent='G';
    if (code===5) d.textContent='A';
    board.appendChild(d);
  }
  percep.textContent = (state.percepciones || []).join(', ') || '—';
  stat.textContent = state.msg || '';
}

async function update(){ const {estado} = await getState(); draw(estado || {}); }

document.getElementById('step').onclick = ()=> act('step').then(update);
document.getElementById('auto').onclick = ()=>{
  if (autoTimer){ clearInterval(autoTimer); autoTimer=null; return; }
  autoTimer = setInterval(()=> act('step').then(update), 500);
};
document.getElementById('reset').onclick = ()=> restart().then(update);

update();
</script>
</body>
</html>
