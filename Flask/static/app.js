const qEl = document.getElementById('q');
const btn = document.getElementById('btn');
const results = document.getElementById('results');
const statusEl = document.getElementById('status');
let aborter = null;
let debounceTimer = null;

function escapeHtml(s){
  return (s||'').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;','\'':'&#39;'}[c]));
}

function render(items){
  results.innerHTML = '';
  if(!items || !items.length){
    results.innerHTML = '<div class="text-center small-dim">No results</div>';
    return;
  }
  items.forEach(row => {
    const wrap = document.createElement('div');
    wrap.className = 'card p-3 mb-2';
    wrap.innerHTML = `
      <div class="d-flex justify-content-between align-items-start gap-3">
        <div>
          <div class="h5 mb-1">${escapeHtml(row.code)} <span class="badge bg-secondary badge-src">${escapeHtml(row.source)}</span></div>
          <div class="mb-1">${escapeHtml(row.description)}</div>
        </div>
        <button class="btn btn-outline-light btn-sm copy-btn">Copy</button>
      </div>`;
    wrap.querySelector('.copy-btn').addEventListener('click', () => {
      const text = `${row.code} - ${row.description}`;
      navigator.clipboard.writeText(text);
      statusEl.textContent = `Copied: ${text}`;
    });
    results.appendChild(wrap);
  });
}

async function search(){
  const q = qEl.value.trim();
  statusEl.textContent = '';
  if(!q){ results.innerHTML = ''; return; }
  if(aborter) aborter.abort();
  aborter = new AbortController();
  try{
    document.body.classList.add('busy');
    const res = await fetch(`/api/search?q=${encodeURIComponent(q)}&limit=30`, { signal: aborter.signal });
    const data = await res.json();
    render(data.items || []);
    statusEl.textContent = data.items?.length ? `Found ${data.items.length} results for "${q}"` : 'No results';
  }catch(e){
    if(e.name !== 'AbortError'){
      results.innerHTML = '<div class="text-danger">Error fetching results</div>';
      statusEl.textContent = 'Network error';
    }
  }finally{
    document.body.classList.remove('busy');
  }
}

qEl.addEventListener('input', () => {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(search, 250);
});
btn.addEventListener('click', search);

// Shortcuts
document.addEventListener('keydown', (e) => {
  if(e.key === '/' && document.activeElement !== qEl){ e.preventDefault(); qEl.focus(); }
  if(e.key === 'Escape'){ qEl.value=''; results.innerHTML=''; statusEl.textContent=''; qEl.focus(); }
});

// Autofocus on load
qEl.focus();