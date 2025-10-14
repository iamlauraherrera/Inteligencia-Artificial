<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Cadenas de Markov – Visualizador</title>
<style>
:root { font-family: system-ui, -apple-system, Segoe UI, Roboto; }
body { margin:0; background:#0f172a; color:#e5e7eb; }
header { display:flex; align-items:center; padding:12px 16px; background:#111827; border-bottom:1px solid #1f2937; }
h1 { margin:0; font-size:1.05rem; color:#fafafa; }
.container{ max-width:1100px; margin:16px auto; padding:0 16px; display:grid; grid-template-columns: 1fr 420px; gap:16px; }
.card{ background:#111827; border:1px solid #1f2937; border-radius:14px; padding:16px; }
.title{ font-weight:600; color:#fafafa; margin-bottom:8px; }
.box{ background:#0b101d; border-radius:10px; padding:12px; border:1px solid #1f2937; white-space:pre-wrap; min-height:180px; }
label{ color:#cbd5e1; display:block; margin-top:8px; font-size:.9rem; }
input,textarea{ width:100%; box-sizing:border-box; background:#1f2937; color:#e5e7eb; border:1px solid #374151; border-radius:8px; padding:8px; }
.btn{ background:#2563eb; color:#e5e7eb; border:1px solid #2563eb; border-radius:10px; padding:10px 14px; margin-right:8px; margin-top:8px; }
.btn.secondary{ background:#374151; border-color:#374151; }
.stat{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size:.92rem; color:#cbd5e1; }
</style>
</head>
<body>
<header><h1>Cadenas de Markov – Visualizador</h1></header>

<div class="container">
  <div class="card">
    <div class="title">Trayectoria simulada</div>
    <div id="trayectoria" class="box"></div>
    <div class="title" style="margin-top:10px;">Distribución actual</div>
    <div id="dist" class="box"></div>
  </div>

  <div class="card">
    <div class="title">Controles</div>
    <label>Estados (separados por coma):</label>
    <input id="estados" placeholder="Ej: A,B,C"/>
    <label>Matriz de transición (filas por línea):</label>
    <textarea id="mat" rows="6" placeholder="Ej:\n0.1 0.9 0.0\n0.5 0.0 0.5\n0.0 1.0 0.0"></textarea>
    <label>Estado inicial:</label>
    <input id="inicio" placeholder="A"/>
    <label>Pasos a simular:</label>
    <input id="pasos" type="number" min="1" value="10"/>
    <div style="margin-top:8px;">
      <button class="btn" id="run">Simular</button>
      <button class="btn secondary" id="reset">Reiniciar</button>
      <a class="btn secondary" href="/">Volver</a>
    </div>
    <div class="title" style="margin-top:10px;">Estado</div>
    <div id="stat" class="stat"></div>
  </div>
</div>

<script>
const name = "markov-algorithm.py";
const boxT = document.getElementById('trayectoria');
const boxD = document.getElementById('dist');
const stat = document.getElementById('stat');

async function j(url, opts={}){ const r = await fetch(url, opts); return r.json(); }
async function getState(){ return j(`/api/${name}/state`); }
async function act(action, payload={}){
  return j(`/api/${name}/act`, {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({action, ...payload})});
}
async function restart(){ return j(`/api/${name}/restart`, {method:'POST'}); }

function render(state){
  // estado esperado (opcional): { trayectoria:[...], dist:{A:0.3,...}, msg:"" }
  const tr = (state.trayectoria || []).join(" → ");
  boxT.textContent = tr || "Sin datos (simula para ver la trayectoria).";
  const dist = state.dist || {};
  const lines = Object.keys(dist).map(k=> `${k}: ${dist[k].toFixed(4)}`);
  boxD.textContent = lines.length ? lines.join("\n") : "—";
  stat.textContent = state.msg || '';
}

async function update(){ const {estado} = await getState(); render(estado||{}); }
document.getElementById('run').onclick = ()=>{
  const estados = (document.getElementById('estados').value||'').trim();
  const mat = (document.getElementById('mat').value||'').trim();
  const inicio = (document.getElementById('inicio').value||'').trim();
  const pasos = parseInt(document.getElementById('pasos').value||'10',10);
  act('simular', {estados, mat, inicio, pasos}).then(update);
};
document.getElementById('reset').onclick = ()=> restart().then(update);

update();
</script>
</body>
</html>
