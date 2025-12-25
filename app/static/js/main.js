document.addEventListener('DOMContentLoaded', function() {
  console.log('Contract Pilot - Initializing...');

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
