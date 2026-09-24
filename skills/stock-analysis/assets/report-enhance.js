// Presentation only: reading progress and the current section in the navigation.
(() => {
  const root = document.documentElement;
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
    links.forEach(link => link === current ? link.setAttribute('aria-current', 'true') : link.removeAttribute('aria-current'));
  };
  const schedule = () => { if (!queued) { queued = true; requestAnimationFrame(update); } };
  addEventListener('scroll', schedule, {passive: true});
  addEventListener('resize', schedule);
  document.querySelector('#language').addEventListener('change', schedule);
  update();
})();
