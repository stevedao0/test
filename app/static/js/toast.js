class ToastManager {
  constructor() {
    this.container = document.querySelector('[data-toast-container]');
    if (!this.container) {
      this.container = document.createElement('div');
      this.container.className = 'toast-container';
      this.container.setAttribute('data-toast-container', '');
      document.body.appendChild(this.container);
    }
  }

  show(message, type = 'info', title = null, duration = 5000) {
    const toast = this.createToast(message, type, title);
    this.container.appendChild(toast);

    setTimeout(() => toast.classList.add('toast-show'), 10);

    if (duration > 0) {
      setTimeout(() => this.dismiss(toast), duration);
    }

    return toast;
  }

  success(message, title = 'Thành công') {
    return this.show(message, 'success', title);
  }

  error(message, title = 'Có lỗi') {
    return this.show(message, 'error', title);
  }

  warning(message, title = 'Cảnh báo') {
    return this.show(message, 'warning', title);
  }

  info(message, title = 'Thông báo') {
    return this.show(message, 'info', title);
  }

  createToast(message, type, title) {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;

    const icons = {
      success: '✓',
      error: '✕',
      warning: '⚠',
      info: 'ℹ'
    };

    const titles = {
      success: 'Thành công',
      error: 'Có lỗi',
      warning: 'Cảnh báo',
      info: 'Thông báo'
    };

    toast.innerHTML = `
      <div class="toast-icon">${icons[type]}</div>
      <div class="toast-content">
        <div class="toast-title">${title || titles[type]}</div>
        <div class="toast-message">${message}</div>
      </div>
      <button class="toast-close" aria-label="Đóng">✕</button>
    `;

    toast.querySelector('.toast-close').addEventListener('click', () => {
      this.dismiss(toast);
    });

    return toast;
  }

  dismiss(toast) {
    toast.classList.remove('toast-show');
    setTimeout(() => {
      if (toast.parentNode) {
        toast.parentNode.removeChild(toast);
      }
    }, 300);
  }

  dismissAll() {
    const toasts = this.container.querySelectorAll('.toast');
    toasts.forEach(toast => this.dismiss(toast));
  }
}

if (typeof window !== 'undefined') {
  window.toast = new ToastManager();
  window.ToastManager = ToastManager;
}
