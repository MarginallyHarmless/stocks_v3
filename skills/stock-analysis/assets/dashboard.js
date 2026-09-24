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
  document.querySelectorAll('.viz-chart').forEach(chart => {
    const card = chart.closest('.viz-card');
    const {values, periods, series} = JSON.parse(card.querySelector('.viz-values').textContent);
    const latest = periods.length - 1;
    const reset = card.querySelector('[data-viz-reset]');
    const pinnedLabel = card.querySelector('[data-viz-pinned]');
    let selected = latest, shown = latest, pinned = false;
    const updateSelection = index => {
      const row = values[index];
      if (!row) return;
      shown = index;
      const period = periods[index];
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
      chart.setAttribute('aria-valuenow', String(index));
      chart.setAttribute('aria-valuetext', [period, ...row.map((value,i) => `${series[i]}: ${value}`)].join(' · '));
      pinnedLabel.hidden = !pinned || index !== selected;
      reset.hidden = !pinned;
    };
    const hitIndex = event => {
      const target = event.target.closest('[data-viz-hit]');
      return target && chart.contains(target) ? Number(target.dataset.vizHit) : null;
    };
    const pin = index => {
      selected = index;
      pinned = true;
      updateSelection(index);
    };
    const showLatest = () => {
      selected = latest;
      pinned = false;
      updateSelection(latest);
    };
    chart.addEventListener('pointermove', event => {
      if (event.pointerType === 'touch') return;
      const index = hitIndex(event);
      if (index !== null && index !== shown) updateSelection(index);
    });
    chart.addEventListener('pointerleave', () => updateSelection(selected));
    chart.addEventListener('pointercancel', () => updateSelection(selected));
    chart.addEventListener('click', event => {
      const index = hitIndex(event);
      if (index !== null) pin(index);
    });
    chart.addEventListener('focus', () => updateSelection(selected));
    chart.addEventListener('keydown', event => {
      let index;
      switch (event.key) {
        case 'ArrowLeft': case 'ArrowDown': index = Math.max(0, shown - 1); break;
        case 'ArrowRight': case 'ArrowUp': index = Math.min(latest, shown + 1); break;
        case 'Home': index = 0; break;
        case 'End': index = latest; break;
        case 'Enter': case ' ': index = shown; break;
        case 'Escape': event.preventDefault(); showLatest(); return;
        default: return;
      }
      event.preventDefault();
      pin(index);
    });
    reset.addEventListener('click', () => { showLatest(); chart.focus(); });
    updateSelection(selected);
  });
})();
