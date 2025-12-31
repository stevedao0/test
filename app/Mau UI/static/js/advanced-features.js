function setupCopyElement(el) {
  if (el.querySelector('.copy-icon')) return;

  el.style.cursor = 'pointer';
  el.style.position = 'relative';

  const copyIcon = document.createElement('span');
  copyIcon.innerHTML = `
    <svg style="width: 14px; height: 14px; margin-left: 6px; opacity: 0.5; transition: opacity 0.2s;" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
    </svg>
  `;
  copyIcon.className = 'copy-icon';
  copyIcon.style.display = 'inline-block';
  copyIcon.style.verticalAlign = 'middle';
  el.appendChild(copyIcon);

  el.addEventListener('mouseenter', () => {
    copyIcon.querySelector('svg').style.opacity = '1';
  });

  el.addEventListener('mouseleave', () => {
    copyIcon.querySelector('svg').style.opacity = '0.5';
  });

  el.addEventListener('click', async function(e) {
    e.preventDefault();
    e.stopPropagation();

    const textToCopy = this.dataset.copy || this.textContent.trim();

    try {
      await navigator.clipboard.writeText(textToCopy);

      const originalHTML = copyIcon.innerHTML;
      copyIcon.innerHTML = `
        <svg style="width: 14px; height: 14px; margin-left: 6px; color: var(--secondary-600);" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
        </svg>
      `;

      if (window.toast) {
        window.toast.success('Đã copy: ' + textToCopy.substring(0, 50) + (textToCopy.length > 50 ? '...' : ''));
      }

      setTimeout(() => {
        copyIcon.innerHTML = originalHTML;
      }, 1500);
    } catch (err) {
      console.error('Copy failed:', err);
      if (window.toast) {
        window.toast.error('Không thể copy');
      }
    }
  });
}

function initCopyToClipboard() {
  const elements = document.querySelectorAll('[data-copy]');
  console.log(`📋 Initializing copy for ${elements.length} elements`);
  elements.forEach(setupCopyElement);
}

function reinitCopyToClipboard(container) {
  if (!container) return;
  const elements = container.querySelectorAll('[data-copy]');
  console.log(`📋 Reinitializing copy for ${elements.length} elements in container`);
  elements.forEach(setupCopyElement);
}

if (typeof window !== 'undefined') {
  window.reinitCopyToClipboard = reinitCopyToClipboard;
}


function initDragDropUpload() {
  const fileInputs = document.querySelectorAll('input[type="file"]');

  fileInputs.forEach(input => {
    const wrapper = input.closest('.form-group') || input.parentElement;

    const dropZone = document.createElement('div');
    dropZone.className = 'drag-drop-zone';
    dropZone.innerHTML = `
      <div class="drag-drop-content">
        <svg class="drag-drop-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
        </svg>
        <div class="drag-drop-text">
          <strong>Kéo thả file vào đây</strong>
          <span>hoặc click để chọn file</span>
        </div>
        <div class="drag-drop-hint">Hỗ trợ: .xlsx, .xls</div>
      </div>
    `;

    input.style.display = 'none';
    wrapper.appendChild(dropZone);

    dropZone.addEventListener('click', () => {
      input.click();
    });

    input.addEventListener('change', function() {
      if (this.files.length > 0) {
        const file = this.files[0];
        dropZone.innerHTML = `
          <div class="drag-drop-content" style="color: var(--secondary-600);">
            <svg class="drag-drop-icon" style="color: var(--secondary-600);" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <div class="drag-drop-text">
              <strong>📄 ${file.name}</strong>
              <span>${formatFileSize(file.size)}</span>
            </div>
            <button type="button" class="btn btn-sm btn-secondary" style="margin-top: var(--space-3);">Chọn file khác</button>
          </div>
        `;

        const changeBtn = dropZone.querySelector('button');
        changeBtn.addEventListener('click', (e) => {
          e.stopPropagation();
          input.value = '';
          resetDropZone(dropZone);
        });
      }
    });

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
      dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
      e.preventDefault();
      e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
      dropZone.addEventListener(eventName, () => {
        dropZone.classList.add('drag-over');
      });
    });

    ['dragleave', 'drop'].forEach(eventName => {
      dropZone.addEventListener(eventName, () => {
        dropZone.classList.remove('drag-over');
      });
    });

    dropZone.addEventListener('drop', function(e) {
      const dt = e.dataTransfer;
      const files = dt.files;

      if (files.length > 0) {
        input.files = files;
        input.dispatchEvent(new Event('change', { bubbles: true }));
      }
    });

    function resetDropZone(zone) {
      zone.innerHTML = `
        <div class="drag-drop-content">
          <svg class="drag-drop-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
          <div class="drag-drop-text">
            <strong>Kéo thả file vào đây</strong>
            <span>hoặc click để chọn file</span>
          </div>
          <div class="drag-drop-hint">Hỗ trợ: .xlsx, .xls</div>
        </div>
      `;

      zone.addEventListener('click', () => {
        input.click();
      });
    }
  });
}

function formatFileSize(bytes) {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function initKeyboardShortcuts() {
  document.addEventListener('keydown', function(e) {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
      return;
    }

    if (e.ctrlKey || e.metaKey) {
      switch(e.key.toLowerCase()) {
        case 'n':
          e.preventDefault();
          const newBtn = document.querySelector('a[href*="/new"]');
          if (newBtn) newBtn.click();
          break;

        case 'f':
          e.preventDefault();
          const searchInput = document.querySelector('[data-table-search]');
          if (searchInput) searchInput.focus();
          break;

        case 'e':
          e.preventDefault();
          const exportBtn = document.querySelector('a[href*="/download"]');
          if (exportBtn) exportBtn.click();
          break;
      }
    }

    if (e.key === 'Escape') {
      document.querySelectorAll('.modal').forEach(modal => {
        if (modal.style.display !== 'none') {
          modal.style.display = 'none';
        }
      });

      document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
        menu.classList.remove('show');
      });
    }
  });
}

function initContextMenu() {
  document.querySelectorAll('.contract-row, .annex-row').forEach(row => {
    row.addEventListener('contextmenu', function(e) {
      e.preventDefault();

      const contractNo = this.dataset.contractNo;
      const year = this.dataset.year || new Date().getFullYear();

      const existingMenu = document.querySelector('.context-menu-custom');
      if (existingMenu) {
        existingMenu.remove();
      }

      const contextMenu = document.createElement('div');
      contextMenu.className = 'context-menu-custom';
      contextMenu.style.left = e.pageX + 'px';
      contextMenu.style.top = e.pageY + 'px';

      const actions = [
        {
          icon: '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" /></svg>',
          label: 'Copy số HĐ',
          action: () => {
            navigator.clipboard.writeText(contractNo);
            if (window.toast) window.toast.success('Đã copy số HĐ');
          }
        },
        {
          icon: '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>',
          label: 'Xem chi tiết',
          action: () => {
            if (typeof viewContract === 'function') {
              viewContract(year, contractNo);
            }
          }
        },
        {
          icon: '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>',
          label: 'Chỉnh sửa',
          action: () => {
            window.location.href = `/contracts/${year}/edit?contract_no=${encodeURIComponent(contractNo)}`;
          }
        },
        {
          divider: true
        },
        {
          icon: '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" /></svg>',
          label: 'Tạo phụ lục',
          action: () => {
            window.location.href = `/annexes/new?year=${year}&contract_no=${encodeURIComponent(contractNo)}`;
          }
        }
      ];

      actions.forEach(action => {
        if (action.divider) {
          const divider = document.createElement('div');
          divider.className = 'context-menu-divider';
          contextMenu.appendChild(divider);
        } else {
          const item = document.createElement('button');
          item.className = 'context-menu-item';
          item.innerHTML = `${action.icon} ${action.label}`;
          item.addEventListener('click', () => {
            action.action();
            contextMenu.remove();
          });
          contextMenu.appendChild(item);
        }
      });

      document.body.appendChild(contextMenu);

      const menuRect = contextMenu.getBoundingClientRect();
      if (menuRect.right > window.innerWidth) {
        contextMenu.style.left = (e.pageX - menuRect.width) + 'px';
      }
      if (menuRect.bottom > window.innerHeight) {
        contextMenu.style.top = (e.pageY - menuRect.height) + 'px';
      }

      const closeMenu = () => {
        contextMenu.remove();
        document.removeEventListener('click', closeMenu);
      };

      setTimeout(() => {
        document.addEventListener('click', closeMenu);
      }, 10);
    });
  });
}

document.addEventListener('DOMContentLoaded', function() {
  console.log('✨ Initializing Advanced Features...');

  initCopyToClipboard();
  console.log('✓ Copy to Clipboard initialized');

  console.log('✓ Smart Search disabled (using EnhancedTable)');

  initDragDropUpload();
  console.log('✓ Drag & Drop Upload initialized');

  initKeyboardShortcuts();
  console.log('✓ Keyboard Shortcuts initialized');

  initContextMenu();
  console.log('✓ Context Menu initialized');

  console.log('🎉 All Advanced Features Ready!');
});
