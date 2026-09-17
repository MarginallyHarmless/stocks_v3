(() => {
  const body = document.body;
  const get = (key, fallback) => { try { return localStorage.getItem('stock-v3-' + key) || fallback; } catch { return fallback; } };
  const save = (key, value) => { try { localStorage.setItem('stock-v3-' + key, value); } catch {} };
  const language = document.querySelector('#language');
  const reading = document.querySelector('#reading');
  const theme = document.querySelector('#theme');
  const dialog = document.querySelector('#evidence-dialog');
  const setLanguage = value => {
    if (![...language.options].some(o => o.value === value)) value = language.value;
    language.value = value; document.documentElement.lang = value;
    document.querySelectorAll('[data-lang]').forEach(el => el.hidden = el.dataset.lang !== value);
    save('language', value);
  };
  const setReading = value => {
    if (!['beginner', 'experienced'].includes(value)) value = 'beginner';
    body.dataset.reading = value; reading.value = value; save('guided-reading', value);
    document.querySelectorAll('.deep-data').forEach(el => el.open = value === 'experienced');
  };
  const setTheme = value => { body.dataset.theme = value; theme.value = value; save('theme', value); };
  setLanguage(get('language', language.value));
  setReading(get('guided-reading', 'beginner'));
  setTheme(get('theme', 'dark'));
  language.addEventListener('change', () => setLanguage(language.value));
  reading.addEventListener('change', () => setReading(reading.value));
  theme.addEventListener('change', () => setTheme(theme.value));
  document.querySelector('#expand-lessons').addEventListener('click', e => {
    const open = e.currentTarget.getAttribute('aria-expanded') !== 'true';
    setReading('beginner');
    document.querySelectorAll('.lesson').forEach(d => d.open = open);
    e.currentTarget.setAttribute('aria-expanded', String(open));
  });
  document.querySelectorAll('[data-evidence]').forEach(button => button.addEventListener('click', () => {
    if (!dialog.open) dialog.showModal();
    const search = document.querySelector('#evidence-search'); search.value = '';
    const selected = new Set(JSON.parse(button.dataset.evidenceIds));
    const cards = [...document.querySelectorAll('.evidence-card')];
    const byId = new Map(cards.filter(c => c.parentElement.dataset.lang === document.documentElement.lang).map(c => [c.dataset.evidenceKey,c]));
    const pending = [...selected];
    while (pending.length) {
      const card = byId.get(pending.pop());
      if (!card) continue;
      JSON.parse(card.dataset.inputs).forEach(id => { if (!selected.has(id)) { selected.add(id); pending.push(id); } });
    }
    cards.forEach(e => e.hidden = !selected.has(e.dataset.evidenceKey));
    const target = document.getElementById('ev-' + document.documentElement.lang + '-' + button.dataset.evidence);
    if (target) target.scrollIntoView({block: 'start'});
  }));
  document.querySelector('#open-sources').addEventListener('click', () => {
    document.querySelector('#evidence-search').value = '';
    document.querySelectorAll('.evidence-card').forEach(e => e.hidden = false);
    if (!dialog.open) dialog.showModal();
  });
  document.querySelector('#close-sources').addEventListener('click', () => dialog.close());
  document.querySelector('#evidence-search').addEventListener('input', e => {
    const q = e.target.value.toLocaleLowerCase();
    document.querySelectorAll('.evidence-card').forEach(el => el.hidden = !el.textContent.toLocaleLowerCase().includes(q));
  });
  document.querySelectorAll('[data-copy]').forEach(button => button.addEventListener('click', async () => {
    const box = document.getElementById(button.dataset.copy);
    const status = button.parentElement.nextElementSibling;
    box.focus(); box.select();
    try { await navigator.clipboard.writeText(box.value); status.textContent = document.documentElement.lang === 'ro' ? 'Text copiat.' : 'Prompt copied.'; }
    catch { status.textContent = document.documentElement.lang === 'ro' ? 'Text selectat. Copiază-l pentru sesiunea nouă.' : 'Text selected. Copy it for your new session.'; }
  }));
  document.querySelectorAll('[data-export]').forEach(button => button.addEventListener('click', () => {
    const data = document.querySelector('#research-package').textContent;
    const url = URL.createObjectURL(new Blob([data], {type:'application/json'}));
    const a = document.createElement('a'); a.href = url; a.download = button.dataset.export;
    a.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
  }));
})();
