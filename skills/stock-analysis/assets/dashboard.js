(() => {
  document.querySelectorAll('[data-export-visuals]').forEach(button => button.addEventListener('click', () => {
    const content = document.querySelector('#visual-package').textContent;
    const data = JSON.parse(content);
    if (!data) return;
    const url = URL.createObjectURL(new Blob([content], {type:'application/json'}));
    const a = document.createElement('a'); a.href=url;
    a.download=data.ticker+'-chart-data-'+data.retrieved_at+'.json';
    a.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
  }));
  document.querySelectorAll('.viz-period').forEach(select => {
    const card = select.closest('.viz-card');
    const values = JSON.parse(card.querySelector('.viz-values').textContent);
    select.addEventListener('change', () => {
      const row = values[Number(select.value)];
      if (!row) return;
      card.querySelectorAll('[data-viz-value]').forEach(el => {
        el.textContent = row[Number(el.dataset.vizValue)];
      });
    });
  });
})();
