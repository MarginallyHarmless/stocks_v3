// Terms remain inline; their definitions work with pointer, keyboard and touch.
(() => {
  let active = null, timer;
  const close = () => {
    clearTimeout(timer);
    if (!active) return;
    active.setAttribute('aria-expanded', 'false');
    document.getElementById(active.getAttribute('aria-describedby')).hidden = true;
    active = null;
  };
  const open = button => {
    close(); active = button;
    const tip = document.getElementById(button.getAttribute('aria-describedby'));
    tip.hidden = false; button.setAttribute('aria-expanded', 'true');
    const r = button.getBoundingClientRect();
    const width = tip.offsetWidth, height = tip.offsetHeight;
    tip.style.left = Math.max(12, Math.min(r.left, innerWidth - width - 12)) + 'px';
    tip.style.top = Math.max(12, Math.min(r.bottom + 8 + height <= innerHeight ? r.bottom + 8 : r.top - height - 8, innerHeight - height - 12)) + 'px';
  };
  const later = () => { timer = setTimeout(close, 180); };
  document.querySelectorAll('.finance-term').forEach(button => {
    const tip = document.getElementById(button.getAttribute('aria-describedby'));
    button.addEventListener('pointerenter', e => { if (e.pointerType !== 'touch') open(button); });
    button.addEventListener('pointerleave', e => { if (e.pointerType !== 'touch') later(); });
    button.addEventListener('focus', () => open(button));
    button.addEventListener('blur', close);
    button.addEventListener('click', () => open(button));
    tip.addEventListener('pointerenter', () => clearTimeout(timer));
    tip.addEventListener('pointerleave', later);
  });
  document.addEventListener('pointerdown', e => {
    if (!e.target.closest('.finance-term, .term-definition')) close();
  });
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && active) { close(); e.preventDefault(); e.stopPropagation(); }
  }, true);
  document.addEventListener('scroll', close, true);
  window.addEventListener('resize', close);
  document.querySelector('#language').addEventListener('change', close);
  document.querySelector('#evidence-dialog').addEventListener('close', close);
})();
