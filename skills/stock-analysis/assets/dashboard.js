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
    const chart = card.querySelector('.viz-chart');
    const chartLabel = chart.getAttribute('aria-label');
    const updateSelection = () => {
      const index = Number(select.value);
      const row = values[index];
      if (!row) return;
      const period = select.selectedOptions[0].textContent;
      card.querySelector('[data-viz-period-label]').textContent = period;
      card.querySelectorAll('[data-viz-value]').forEach(el => {
        el.textContent = row[Number(el.dataset.vizValue)];
      });
      card.querySelectorAll('[data-viz-point], [data-viz-row]').forEach(el => {
        el.setAttribute('data-selected', String(Number(el.dataset.vizPoint ?? el.dataset.vizRow) === index));
      });
      const focus = card.querySelector('[data-viz-focus]');
      const x = Number(focus.dataset.start) + Number(focus.dataset.step) * (index + .5);
      focus.setAttribute('transform', `translate(${x},0)`);
      chart.setAttribute('aria-label', `${chartLabel} — ${period}`);
    };
    select.addEventListener('change', updateSelection);
    updateSelection();
  });
})();
