<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>KNN – Visualizador</title>
<style>
    :root { font-family: system-ui, -apple-system, Segoe UI, Roboto; }
    header { display:flex; align-items:center; padding:12px 16px; background:#111827; border-bottom:1px solid #1f2937; }
    body { margin:0; background:#0f172a; color:#e5e7eb; }
h1 { margin:0; font-size:1.05rem; color:#fafafa; }
.container{ max-width:1100px; margin:16px auto; padding:0 16px; display:grid; grid-template-columns: 1fr 360px; gap:16px; }
.card{ background:#111827; border:1px solid #1f2937; border-radius:14px; padding:16px; }
.title{ font-weight:600; color:#fafafa; margin-bottom:8px; }
#board.grid{ display:grid; gap:1px; background:#0b101d; padding:4px; border-radius:10px; }
.cell{ display:flex; align-items:center; justify-content:center; background:#1f2937; border-radius:4px; aspect-ratio:1/1; font-size:.85rem; }
.cell:hover{ filter:brightness(1.08); cursor:pointer; }
.btn{ background:#2563eb; color:#e5e7eb; border:1px solid #2563eb; border-radius:10px; padding:10px 14px; margin-right:8px; }
.btn.secondary{ background:#374151; border-color:#374151; }
label{ color:#cbd5e1; display:block; margin-top:8px; font-size:.9rem; }
input,select{ width:100%; box-sizing:border-box; background:#1f2937; color:#e5e7eb; border:1px solid #374151; border-radius:8px; padding:8px; }
.stat{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size:.92rem; color:#cbd5e1; }
</style>
</head>
<body>
<header><h1>KNN – Visualizador</h1></header>

<div class="container">
  <div class="card">
    <div class="title">Plano (dataset sintético)</div>
    <div id="board" class="grid"></div>
  </div>

  <div class="card">
    <div class="title">Controles</div>
    <label>k</label>
    <input id="k" type="number" min="1" value="3"/>
    <label>Métrica</label>
    <select id="metric">
      <option value="euclid">Euclidiana</option>
      <option value="manhattan">Manhattan</option>
    </select>
    <label style="margin-top:8px;">Punto a clasificar (click en el plano)</label>
    <div style="margin-top:10px;">
      <button class="btn" id="classify">Clasificar</button>
      <button class="btn secondary" id="reset">Reiniciar</button>
      <a class="btn secondary" href="/">Volver</a>
    </div>

    <div class="title" style="margin-top:10px;">Estado</div>
    <div id="stat" class="stat"></div>
  </div>
</div>

<script>
const name = "knn-algorithm.py";
const board = document.getElementById('board');
const stat = document.getElementById('stat');
const N = 25; // cuadriculado N×N (render)

async function j(url, opts={}){ const r = await fetch(url, opts); return r.json(); }
async function getState(){ return j(`/api/${name}/state`); }
async function act(action, payload={}){
  return j(`/api/${name}/act`, {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({action, ...payload})});
}
async function restart(){ return j(`/api/${name}/restart`, {method:'POST'}); }

function drawGrid(state){
  // state esperado (opcional): { puntos: [{i,j,clase}], query:{i,j}, vecinos:[idx...], pred:"A"/"B" }
  board.innerHTML = '';
  board.style.gridTemplateColumns = `repeat(${N},1fr)`;

  const puntos = state.puntos || [];             // dataset
  const query  = state.query || null;            // punto a clasificar
  const vecinos = new Set(state.vecinos || []);  // índices en puntos
  const pred  = state.pred || '';

  // Mapa rápido de ocupación para pintar
  const occ = new Map();
  puntos.forEach((p, idx)=> occ.set(p.i*N + p.j, {clase:p.clase, idx}));
  const qIndex = query ? (query.i*N + query.j) : -1;

  for (let i=0;i<N*N;i++){
    const d = document.createElement('div');
    d.className = 'cell';
    if (occ.has(i)){
      const {clase, idx} = occ.get(i);
      d.style.background = clase === 'A' ? '#60a5fa' : '#f59e0b';
      if (vecinos.has(idx)) d.style.outline = '2px solid #22c55e';
    }
    if (i === qIndex){
      d.style.background = '#a78bfa';
      d.style.outline = '2px dashed #fef08a';
    }
    // click define query
    d.onclick = ()=>{
      const ci = Math.floor(i / N), cj = i % N;
      act('set_query', {i:ci, j:cj}).then(update);
    };
    board.appendChild(d);
  }
  stat.textContent = pred ? `Predicción: ${pred}` : (state.msg || '');
}

async function update(){ const {estado} = await getState(); drawGrid(estado||{}); }
document.getElementById('classify').onclick = ()=>{
  const k = parseInt(document.getElementById('k').value || '3', 10);
  const metric = document.getElementById('metric').value;
  act('classify', {k, metric}).then(update);
};
document.getElementById('reset').onclick = ()=> restart().then(update);

update();
</script>
</body>
</html>
