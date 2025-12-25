document.addEventListener('DOMContentLoaded', function() {
    initSidebar();
    initAlerts();
    initForms();
});

function initSidebar() {
    const sidebar = document.getElementById('sidebar');
    const toggleBtn = document.getElementById('sidebar-toggle');

    if (!sidebar) return;

    if (toggleBtn) {
        toggleBtn.addEventListener('click', function() {
            sidebar.classList.toggle('mobile-open');
        });
    }

    if (window.innerWidth <= 768) {
        document.addEventListener('click', function(e) {
            if (!sidebar.contains(e.target) && !toggleBtn?.contains(e.target)) {
                sidebar.classList.remove('mobile-open');
            }
        });
    }
}

function initAlerts() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        if (alert.querySelector('.alert-close')) {
            alert.querySelector('.alert-close').addEventListener('click', function() {
                alert.style.opacity = '0';
                alert.style.transform = 'translateY(-10px)';
                setTimeout(() => alert.remove(), 300);
            });
        }

        setTimeout(() => {
            if (alert.classList.contains('alert-success') || alert.classList.contains('alert-info')) {
                alert.style.opacity = '0';
                alert.style.transform = 'translateY(-10px)';
                setTimeout(() => alert.remove(), 300);
            }
        }, 5000);
    });
}

function initForms() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn && !submitBtn.disabled) {
                submitBtn.disabled = true;
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<span class="loading-spinner"></span> Đang xử lý...';

                setTimeout(() => {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalText;
                }, 5000);
            }
        });
    });

    const numberInputs = document.querySelectorAll('input[type="text"][id*="tien"]');
    numberInputs.forEach(input => {
        input.addEventListener('input', function(e) {
            let value = e.target.value.replace(/[^\d]/g, '');
            if (value) {
                value = parseInt(value).toLocaleString('vi-VN');
                e.target.value = value;
            }
        });
    });
}

function showModal(title, content, buttons) {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="modal">
            <div class="modal-header">
                <h3 class="modal-title">${title}</h3>
                <button type="button" class="btn btn-sm btn-outline" onclick="this.closest('.modal-overlay').remove()">
                    <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                    </svg>
                </button>
            </div>
            <div class="modal-body">
                ${content}
            </div>
            ${buttons ? `<div class="modal-footer">${buttons}</div>` : ''}
        </div>
    `;

    document.body.appendChild(modal);

    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            modal.remove();
        }
    });

    return modal;
}

function showLoading(message = 'Đang xử lý...') {
    const loading = document.createElement('div');
    loading.className = 'modal-overlay';
    loading.id = 'loading-overlay';
    loading.innerHTML = `
        <div style="background: var(--bg-primary); padding: 2rem; border-radius: var(--radius-lg); text-align: center;">
            <div class="loading-spinner" style="width: 40px; height: 40px; margin: 0 auto 1rem;"></div>
            <p style="color: var(--text-primary); margin: 0;">${message}</p>
        </div>
    `;
    document.body.appendChild(loading);
    return loading;
}

function hideLoading() {
    const loading = document.getElementById('loading-overlay');
    if (loading) {
        loading.remove();
    }
}

function formatMoney(value) {
    return parseInt(value).toLocaleString('vi-VN') + ' VNĐ';
}

function formatDate(dateString) {
    const date = new Date(dateString);
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();
    return `${day}/${month}/${year}`;
}
