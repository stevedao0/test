function initDropdowns() {
  document.querySelectorAll('[data-dropdown]').forEach(dropdown => {
    const trigger = dropdown.querySelector('[data-dropdown-trigger]');
    const menu = dropdown.querySelector('[data-dropdown-menu]');

    if (!trigger || !menu) return;

    trigger.addEventListener('click', (e) => {
      e.stopPropagation();
      const isOpen = dropdown.classList.contains('show');

      document.querySelectorAll('[data-dropdown]').forEach(d => {
        d.classList.remove('show');
      });

      if (!isOpen) {
        dropdown.classList.add('show');
      }
    });
  });

  document.addEventListener('click', () => {
    document.querySelectorAll('[data-dropdown]').forEach(dropdown => {
      dropdown.classList.remove('show');
    });
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      document.querySelectorAll('[data-dropdown]').forEach(dropdown => {
        dropdown.classList.remove('show');
      });
    }
  });
}

function initModals() {
  document.querySelectorAll('[data-modal-trigger]').forEach(trigger => {
    trigger.addEventListener('click', (e) => {
      e.preventDefault();
      const modalId = trigger.getAttribute('data-modal-trigger');
      const modal = document.getElementById(modalId);
      if (modal) {
        openModal(modal);
      }
    });
  });

  document.querySelectorAll('[data-modal-close]').forEach(closeBtn => {
    closeBtn.addEventListener('click', (e) => {
      const modal = closeBtn.closest('.modal');
      if (modal) {
        closeModal(modal);
      }
    });
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      const openModal = document.querySelector('.modal.show');
      if (openModal) {
        closeModal(openModal);
      }
    }
  });
}

function openModal(modal) {
  modal.classList.add('show');
  document.body.style.overflow = 'hidden';

  const firstFocusable = modal.querySelector('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
  if (firstFocusable) {
    firstFocusable.focus();
  }
}

function closeModal(modal) {
  modal.classList.remove('show');
  document.body.style.overflow = '';
}

function initLoadingStates() {
  document.querySelectorAll('form[data-loading]').forEach(form => {
    form.addEventListener('submit', (e) => {
      const btn = form.querySelector('[data-submit-btn]');
      if (btn) {
        const spinner = btn.querySelector('.btn-spinner');
        const text = btn.querySelector('.btn-text');

        btn.disabled = true;
        if (spinner) spinner.style.display = 'inline-block';
        if (text) text.textContent = 'Đang xử lý...';
      }

      const pageLoader = document.querySelector('[data-page-loader]');
      if (pageLoader) {
        pageLoader.classList.add('show');
      }
    });
  });
}

function checkUrlParams() {
  const url = new URL(window.location.href);
  const success = url.searchParams.get('success');
  const error = url.searchParams.get('error');

  if (success === '1' && window.toast) {
    window.toast.success('Thao tác đã được thực hiện thành công');
  }

  if (error && window.toast) {
    window.toast.error(decodeURIComponent(error));
  }
}

function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

function formatDate(dateString) {
  const date = new Date(dateString);
  const day = String(date.getDate()).padStart(2, '0');
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const year = date.getFullYear();
  return `${day}/${month}/${year}`;
}

if (typeof window !== 'undefined') {
  window.initDropdowns = initDropdowns;
  window.initModals = initModals;
  window.initLoadingStates = initLoadingStates;
  window.openModal = openModal;
  window.closeModal = closeModal;
  window.checkUrlParams = checkUrlParams;
  window.debounce = debounce;
  window.formatDate = formatDate;
}
