// Presentation only: reading progress, current section, display menu and localized option labels.
(() => {
  const root = document.documentElement;
  const language = document.querySelector('#language');
  const bar = document.createElement('div');
  bar.className = 'read-progress';
  bar.setAttribute('aria-hidden', 'true');
  document.body.prepend(bar);
  const links = [...document.querySelectorAll('.sidebar nav a[href^="#"]')];
  let queued = false;
  const update = () => {
    queued = false;
    const max = root.scrollHeight - innerHeight;
    bar.style.transform = `scaleX(${max > 0 ? Math.min(1, scrollY / max) : 0})`;
    let current = null;
    for (const link of links) {
      if (link.closest('[hidden]')) continue;
      const target = document.getElementById(link.getAttribute('href').slice(1));
      if (target && target.offsetParent !== null && target.getBoundingClientRect().top < innerHeight * .3) current = link;
    }
    links.forEach(link => {
      if (link === current) {
        if (link.getAttribute('aria-current') !== 'true') {
          link.setAttribute('aria-current', 'true');
          const strip = link.parentElement;
          if (strip.scrollWidth > strip.clientWidth) strip.scrollTo({left: link.offsetLeft - 16, behavior: 'smooth'});
        }
      } else link.removeAttribute('aria-current');
    });
  };
  const schedule = () => { if (!queued) { queued = true; requestAnimationFrame(update); } };
  const relabel = () => document.querySelectorAll('option[data-en]').forEach(option => {
    option.textContent = option.dataset[language.value] || option.dataset.en;
  });
  addEventListener('scroll', schedule, {passive: true});
  addEventListener('resize', schedule);
  language.addEventListener('change', () => { relabel(); schedule(); });
  relabel();
  update();

  document.querySelectorAll('.display-menu, .about-report').forEach(menu => {
    document.addEventListener('pointerdown', event => { if (menu.open && !menu.contains(event.target)) menu.open = false; });
    menu.addEventListener('keydown', event => {
      if (event.key === 'Escape' && menu.open) { menu.open = false; menu.querySelector('summary').focus(); event.stopPropagation(); }
    });
  });
})();
