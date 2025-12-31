/**
 * ADVANCED FEATURES - Tính năng nâng cao cho hệ thống
 * - Copy to clipboard
 * - Bulk actions
 * - Keyboard shortcuts
 * - Quick filters
 * - Export functions
 */

(function() {
  'use strict';

  // ====================================================================
  // COPY TO CLIPBOARD
  // ====================================================================

  function initCopyButtons() {
    // Add copy button to all elements with data-copy attribute
    document.querySelectorAll('[data-copy]').forEach(element => {
      // Check if copy button already exists
      if (element.querySelector('.copy-btn-inline')) return;

      const value = element.getAttribute('data-copy');
      if (!value) return;

      // Create copy button
      const copyBtn = document.createElement('button');
      copyBtn.className = 'copy-btn-inline';
      copyBtn.innerHTML = `
        <svg width="14" height="14" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
        </svg>
      `;
      copyBtn.title = 'Copy';
      copyBtn.style.cssText = `
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 24px;
        height: 24px;
        margin-left: 8px;
        padding: 4px;
        background: var(--primary-100);
        border: 1px solid var(--primary-300);
        border-radius: 4px;
        color: var(--primary-700);
        cursor: pointer;
        opacity: 0;
        transition: all 0.2s;
        vertical-align: middle;
      `;

      // Show button on hover
      element.style.position = 'relative';
      element.addEventListener('mouseenter', () => {
        copyBtn.style.opacity = '1';
      });
      element.addEventListener('mouseleave', () => {
        if (!copyBtn.classList.contains('copied')) {
          copyBtn.style.opacity = '0';
        }
      });

      // Copy functionality
      copyBtn.addEventListener('click', async (e) => {
        e.preventDefault();
        e.stopPropagation();

        try {
          await navigator.clipboard.writeText(value);

          // Success feedback
          copyBtn.innerHTML = `
            <svg width="14" height="14" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
          `;
          copyBtn.style.background = 'var(--secondary-100)';
          copyBtn.style.borderColor = 'var(--secondary-500)';
          copyBtn.style.color = 'var(--secondary-700)';
          copyBtn.classList.add('copied');

          // Reset after 2 seconds
          setTimeout(() => {
            copyBtn.innerHTML = `
              <svg width="14" height="14" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
            `;
            copyBtn.style.background = 'var(--primary-100)';
            copyBtn.style.borderColor = 'var(--primary-300)';
            copyBtn.style.color = 'var(--primary-700)';
            copyBtn.classList.remove('copied');
            copyBtn.style.opacity = '0';
          }, 2000);

          // Show toast notification
          if (window.toast) {
            window.toast.success(`Đã copy: ${value}`);
          }
        } catch (err) {
          console.error('Failed to copy:', err);
          if (window.toast) {
            window.toast.error('Không thể copy');
          }
        }
      });

      element.appendChild(copyBtn);
    });
  }

  // ====================================================================
  // KEYBOARD SHORTCUTS
  // ====================================================================

  function initKeyboardShortcuts() {
    const shortcuts = {
      // Ctrl/Cmd + K: Focus search
      'k': (e) => {
        if (e.ctrlKey || e.metaKey) {
          e.preventDefault();
          const searchInput = document.querySelector('[data-table-search]') || document.querySelector('input[type="search"]');
          if (searchInput) {
            searchInput.focus();
            searchInput.select();
          }
        }
      },
      // Ctrl/Cmd + N: New contract
      'n': (e) => {
        if (e.ctrlKey || e.metaKey) {
          e.preventDefault();
          const newBtn = document.querySelector('a[href*="/contracts/new"]');
          if (newBtn) window.location.href = newBtn.href;
        }
      },
      // Ctrl/Cmd + S: Save form
      's': (e) => {
        if (e.ctrlKey || e.metaKey) {
          e.preventDefault();
          const form = document.querySelector('form[method="post"]');
          if (form) {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) submitBtn.click();
          }
        }
      },
      // Escape: Close modals
      'Escape': (e) => {
        const openModals = document.querySelectorAll('.modal[style*="display: flex"]');
        openModals.forEach(modal => {
          modal.style.display = 'none';
        });
        const openDropdowns = document.querySelectorAll('.dropdown-menu.show');
        openDropdowns.forEach(dropdown => {
          dropdown.classList.remove('show');
        });
      },
      // Ctrl/Cmd + /: Show shortcuts help
      '/': (e) => {
        if (e.ctrlKey || e.metaKey) {
          e.preventDefault();
          showKeyboardShortcutsHelp();
        }
      }
    };

    document.addEventListener('keydown', (e) => {
      const handler = shortcuts[e.key];
      if (handler) {
        handler(e);
      }
    });

    // Show shortcuts indicator
    const shortcutsIndicator = document.createElement('div');
    shortcutsIndicator.innerHTML = `
      <button title="Nhấn Ctrl+/ để xem phím tắt" style="
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 48px;
        height: 48px;
        background: linear-gradient(135deg, var(--primary-500), var(--primary-700));
        border: none;
        border-radius: 50%;
        color: white;
        font-size: 20px;
        cursor: pointer;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
        z-index: 1000;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.3s;
      " onmouseover="this.style.transform='scale(1.1)'" onmouseout="this.style.transform='scale(1)'">
        <svg width="24" height="24" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
      </button>
    `;
    shortcutsIndicator.querySelector('button').addEventListener('click', showKeyboardShortcutsHelp);
    document.body.appendChild(shortcutsIndicator);
  }

  function showKeyboardShortcutsHelp() {
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.style.display = 'flex';
    modal.innerHTML = `
      <div class="modal-backdrop"></div>
      <div class="modal-dialog" style="max-width: 600px;">
        <div class="modal-header">
          <h2 class="modal-title">⚡ Phím tắt</h2>
          <button class="modal-close" onclick="this.closest('.modal').remove()">&times;</button>
        </div>
        <div class="modal-body">
          <div style="display: grid; gap: var(--space-4);">
            <div style="display: flex; justify-content: space-between; align-items: center; padding: var(--space-3); background: var(--bg-secondary); border-radius: var(--radius-md);">
              <span>Tìm kiếm</span>
              <kbd style="padding: 4px 8px; background: white; border: 1px solid var(--border); border-radius: 4px; font-family: monospace;">Ctrl + K</kbd>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; padding: var(--space-3); background: var(--bg-secondary); border-radius: var(--radius-md);">
              <span>Tạo hợp đồng mới</span>
              <kbd style="padding: 4px 8px; background: white; border: 1px solid var(--border); border-radius: 4px; font-family: monospace;">Ctrl + N</kbd>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; padding: var(--space-3); background: var(--bg-secondary); border-radius: var(--radius-md);">
              <span>Lưu form</span>
              <kbd style="padding: 4px 8px; background: white; border: 1px solid var(--border); border-radius: 4px; font-family: monospace;">Ctrl + S</kbd>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; padding: var(--space-3); background: var(--bg-secondary); border-radius: var(--radius-md);">
              <span>Đóng modal/dropdown</span>
              <kbd style="padding: 4px 8px; background: white; border: 1px solid var(--border); border-radius: 4px; font-family: monospace;">ESC</kbd>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; padding: var(--space-3); background: var(--bg-secondary); border-radius: var(--radius-md);">
              <span>Hiện bảng phím tắt</span>
              <kbd style="padding: 4px 8px; background: white; border: 1px solid var(--border); border-radius: 4px; font-family: monospace;">Ctrl + /</kbd>
            </div>
          </div>
        </div>
      </div>
    `;

    modal.querySelector('.modal-backdrop').addEventListener('click', () => {
      modal.remove();
    });

    document.body.appendChild(modal);
  }

  // ====================================================================
  // BULK ACTIONS
  // ====================================================================

  function initBulkActions() {
    const tables = document.querySelectorAll('.table[data-bulk-actions="1"]');

    tables.forEach(table => {
      const tbody = table.querySelector('tbody');
      if (!tbody) return;

      const rows = tbody.querySelectorAll('tr');
      if (rows.length === 0) return;

      // Add checkboxes to rows
      const thead = table.querySelector('thead tr');
      if (!thead) return;

      // Add header checkbox
      const headerCheckTh = document.createElement('th');
      headerCheckTh.style.width = '40px';
      headerCheckTh.innerHTML = `
        <input type="checkbox" class="bulk-select-all" style="cursor: pointer;" title="Chọn tất cả">
      `;
      thead.insertBefore(headerCheckTh, thead.firstChild);

      // Add row checkboxes
      rows.forEach(row => {
        const checkTd = document.createElement('td');
        checkTd.innerHTML = `
          <input type="checkbox" class="bulk-select-row" style="cursor: pointer;">
        `;
        row.insertBefore(checkTd, row.firstChild);
      });

      // Select all functionality
      const selectAllCheckbox = thead.querySelector('.bulk-select-all');
      const rowCheckboxes = tbody.querySelectorAll('.bulk-select-row');

      selectAllCheckbox.addEventListener('change', () => {
        rowCheckboxes.forEach(checkbox => {
          checkbox.checked = selectAllCheckbox.checked;
        });
        updateBulkActionsBar();
      });

      rowCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', updateBulkActionsBar);
      });

      // Create bulk actions bar
      createBulkActionsBar(table);
    });
  }

  function createBulkActionsBar(table) {
    const bar = document.createElement('div');
    bar.className = 'bulk-actions-bar';
    bar.style.cssText = `
      display: none;
      position: fixed;
      bottom: 20px;
      left: 50%;
      transform: translateX(-50%);
      background: white;
      border: 1px solid var(--border);
      border-radius: var(--radius-lg);
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
      padding: var(--space-4) var(--space-6);
      z-index: 1000;
      animation: slideUp 0.3s ease-out;
    `;

    bar.innerHTML = `
      <div style="display: flex; align-items: center; gap: var(--space-4);">
        <span class="selected-count" style="font-weight: 600; color: var(--primary-700);">0 mục được chọn</span>
        <div style="display: flex; gap: var(--space-2);">
          <button class="btn btn-sm btn-secondary bulk-export" title="Export các mục đã chọn">
            <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Export
          </button>
          <button class="btn btn-sm btn-danger bulk-delete" title="Xóa các mục đã chọn">
            <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
            Xóa
          </button>
          <button class="btn btn-sm btn-secondary bulk-cancel" title="Hủy chọn">
            <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>
    `;

    // Cancel button
    bar.querySelector('.bulk-cancel').addEventListener('click', () => {
      table.querySelectorAll('.bulk-select-row, .bulk-select-all').forEach(checkbox => {
        checkbox.checked = false;
      });
      bar.style.display = 'none';
    });

    document.body.appendChild(bar);
    table.bulkActionsBar = bar;
  }

  function updateBulkActionsBar() {
    const tables = document.querySelectorAll('.table[data-bulk-actions="1"]');

    tables.forEach(table => {
      if (!table.bulkActionsBar) return;

      const selectedRows = table.querySelectorAll('.bulk-select-row:checked');
      const count = selectedRows.length;

      const bar = table.bulkActionsBar;
      const countSpan = bar.querySelector('.selected-count');

      if (count > 0) {
        bar.style.display = 'block';
        countSpan.textContent = `${count} mục được chọn`;
      } else {
        bar.style.display = 'none';
      }
    });
  }

  // ====================================================================
  // QUICK STATS
  // ====================================================================

  function initQuickStats() {
    // Add quick stats to tables
    const tables = document.querySelectorAll('.table[data-quick-stats="1"]');

    tables.forEach(table => {
      const container = table.closest('.data-table-container') || table.closest('.card-body');
      if (!container) return;

      const rows = table.querySelectorAll('tbody tr');
      if (rows.length === 0) return;

      // Create stats bar
      const statsBar = document.createElement('div');
      statsBar.className = 'quick-stats-bar';
      statsBar.style.cssText = `
        display: flex;
        gap: var(--space-4);
        padding: var(--space-4);
        background: linear-gradient(135deg, var(--bg-secondary) 0%, white 100%);
        border-radius: var(--radius-md);
        margin-bottom: var(--space-4);
        flex-wrap: wrap;
      `;

      statsBar.innerHTML = `
        <div class="quick-stat">
          <div style="font-size: var(--text-xs); color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.05em;">Tổng số</div>
          <div style="font-size: var(--text-2xl); font-weight: 700; color: var(--primary-700);">${rows.length}</div>
        </div>
      `;

      container.insertBefore(statsBar, container.firstChild);
    });
  }

  // ====================================================================
  // INITIALIZATION
  // ====================================================================

  function init() {
    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', init);
      return;
    }

    initCopyButtons();
    initKeyboardShortcuts();
    initBulkActions();
    initQuickStats();

    console.log('✨ Advanced features initialized');
  }

  init();
})();
