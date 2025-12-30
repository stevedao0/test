function initSidebar() {
  const currentPath = window.location.pathname;
  const sidebarLinks = document.querySelectorAll('.sidebar-link');

  sidebarLinks.forEach(link => {
    const href = link.getAttribute('href');
    if (href && currentPath.startsWith(href) && href !== '/') {
      link.classList.add('active');
    } else if (href === '/' && currentPath === '/') {
      link.classList.add('active');
    }
  });
}

document.addEventListener('DOMContentLoaded', function() {
  console.log('Contract Pilot - Initializing...');

  initSidebar();
  console.log('✓ Sidebar initialized');

  if (typeof initValidation === 'function') {
    initValidation();
    console.log('✓ Validation initialized');
  }

  if (typeof initMoneyCalculators === 'function') {
    initMoneyCalculators();
    console.log('✓ Money calculators initialized');
  }

  if (typeof initEnhancedTables === 'function') {
    initEnhancedTables();
    console.log('✓ Enhanced tables initialized');
  }

  if (typeof initDropdowns === 'function') {
    initDropdowns();
    console.log('✓ Dropdowns initialized');
  }

  if (typeof initModals === 'function') {
    initModals();
    console.log('✓ Modals initialized');
  }

  if (typeof initLoadingStates === 'function') {
    initLoadingStates();
    console.log('✓ Loading states initialized');
  }

  if (typeof checkUrlParams === 'function') {
    checkUrlParams();
  }

  console.log('Contract Pilot - Ready!');
});
