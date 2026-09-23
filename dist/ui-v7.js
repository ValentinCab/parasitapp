// Capa de interfaz: no modifica datos ni taxonomía.
(() => {
  let firstViewApplied = false;
  let pendingQuickScroll = false;

  function removeLevelColumn() {
    document.querySelectorAll('#table .taxonomy-table').forEach(table => {
      const header = table.querySelector('th[data-sort="level"]');
      if (!header) return;
      const index = [...header.parentElement.children].indexOf(header);
      table.querySelectorAll('tr').forEach(row => row.children[index]?.remove());
    });
  }

  function wireQuickTitle() {
    const heading = document.querySelector('#quickView .quick-head h2');
    if (!heading || heading.dataset.fullLink) return;
    heading.dataset.fullLink = 'true';
    heading.classList.add('quick-title-open');
    heading.tabIndex = 0;
    heading.title = 'Abrir ficha completa';
    const openFull = () => document.querySelector('#quickComplete')?.click();
    heading.addEventListener('click', openFull);
    heading.addEventListener('keydown', event => {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        openFull();
      }
    });
  }

  function applyInitialTableView() {
    if (firstViewApplied || document.querySelector('#sidebarCount')?.textContent.trim() === '—') return;
    const tableButton = document.querySelector('.nav-link[data-view="table"]');
    if (!tableButton) return;
    firstViewApplied = true;
    tableButton.click();
  }

  function refreshPresentation() {
    removeLevelColumn();
    wireQuickTitle();
    applyInitialTableView();
    if (pendingQuickScroll && document.querySelector('#quickView')) {
      pendingQuickScroll = false;
      requestAnimationFrame(() => document.querySelector('#quickView')?.scrollIntoView({behavior: 'smooth', block: 'start'}));
    }
  }

  document.addEventListener('click', event => {
    if (event.target.closest('[data-quick-open], tr[data-row] td')) pendingQuickScroll = true;
  }, true);

  new MutationObserver(refreshPresentation).observe(document.body, {childList: true, subtree: true});
  window.addEventListener('load', refreshPresentation);
  refreshPresentation();
})();
