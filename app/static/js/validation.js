const validators = {
  so_hop_dong_4: (value) => {
    if (!/^\d{4}$/.test(value)) {
      return 'Số hợp đồng phải là 4 chữ số (ví dụ: 0001)';
    }
    return null;
  },

  don_vi_mst: (value) => {
    if (!value) return null;
    if (!/^\d{10,14}$/.test(value.replace(/[^0-9]/g, ''))) {
      return 'Mã số thuế phải là 10-14 chữ số';
    }
    return null;
  },

  don_vi_email: (value) => {
    if (!value) return null;
    const normalized = value.replace(/\r\n/g, '\n').replace(/\r/g, '\n').replace(/,/g, ';').replace(/\n/g, ';');
    const parts = normalized.split(';').map(s => s.trim()).filter(Boolean);
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    for (const p of parts) {
      if (!emailRegex.test(p)) {
        return 'Email không hợp lệ';
      }
    }
    return null;
  },

  don_vi_dien_thoai: (value) => {
    if (!value) return null;
    const normalized = value.replace(/\r\n/g, '\n').replace(/\r/g, '\n').replace(/,/g, ';').replace(/\n/g, ';');
    const parts = normalized.split(';').map(s => s.trim()).filter(Boolean);
    for (const p of parts) {
      const digits = p.replace(/[^0-9]/g, '');
      const hasLetters = /[A-Za-zÀ-ỹ]/.test(p);
      const looksNumeric = !hasLetters && /^[0-9\s().+-]+$/.test(p);

      if (looksNumeric) {
        if (!/^0\d{9,10}$/.test(digits)) {
          return 'Số điện thoại phải bắt đầu bằng 0 và có 10-11 chữ số';
        }
      } else {
        if (!digits) {
          return 'Số điện thoại không hợp lệ';
        }
      }
    }
    return null;
  },

  kenh_id: (value) => {
    if (!value || value.trim() === '') return null;
    if (!/^UC[0-9A-Za-z_-]{10,}/.test(value) &&
        !value.includes('youtube.com/channel/') &&
        !value.includes('youtube.com/@')) {
      return 'ID kênh phải bắt đầu bằng UC... hoặc là URL YouTube hợp lệ';
    }
    return null;
  },

  required: (value) => {
    if (!value || value.trim() === '') {
      return 'Trường này là bắt buộc';
    }
    return null;
  }
};

function validateField(input) {
  const name = input.name || input.getAttribute('data-validate-name');
  const value = input.value.trim();
  const validator = validators[name];

  let error = null;

  if (input.hasAttribute('required') || input.required) {
    error = validators.required(value);
  }

  if (!error && validator) {
    error = validator(value);
  }

  const formGroup = input.closest('.form-group');
  if (!formGroup) return !error;

  const errorElement = formGroup.querySelector('.input-error-text');

  if (error) {
    input.classList.add('input-error');
    if (errorElement) {
      errorElement.textContent = error;
      errorElement.style.display = 'block';
    }
    return false;
  } else {
    input.classList.remove('input-error');
    if (errorElement) {
      errorElement.style.display = 'none';
    }
    return true;
  }
}

function validateForm(form) {
  const inputs = form.querySelectorAll('[data-validate]');
  let isValid = true;

  inputs.forEach(input => {
    if (!validateField(input)) {
      isValid = false;
    }
  });

  return isValid;
}

function initValidation() {
  document.querySelectorAll('[data-validate]').forEach(input => {
    input.addEventListener('blur', () => {
      validateField(input);
    });

    input.addEventListener('input', () => {
      if (input.classList.contains('input-error')) {
        validateField(input);
      }
    });
  });

  document.querySelectorAll('form[data-validate-form]').forEach(form => {
    form.addEventListener('submit', (e) => {
      if (!validateForm(form)) {
        e.preventDefault();

        const firstError = form.querySelector('.input-error');
        if (firstError) {
          firstError.focus();
          firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }

        if (window.toast) {
          window.toast.show('Vui lòng kiểm tra lại thông tin nhập vào', 'error', 'Lỗi nhập liệu');
        }
      }
    });
  });
}

if (typeof window !== 'undefined') {
  window.validateField = validateField;
  window.validateForm = validateForm;
  window.initValidation = initValidation;
}
