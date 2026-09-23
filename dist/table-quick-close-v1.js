// La ficha rápida se cierra sin reconstruir la tabla: conserva filtros, scroll y selección.
document.addEventListener('click', event => {
  const close = event.target.closest('#quickClose');
  if (!close) return;
  event.preventDefault();
  event.stopImmediatePropagation();
  document.querySelector('#quickView')?.remove();
}, true);
