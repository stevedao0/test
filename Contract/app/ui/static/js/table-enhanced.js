class EnhancedTable {
  constructor(container) {
    this.container = container;
    this.data = [];
    this.filteredData = [];
    this.currentPage = 1;
    this.perPage = 10;
    this.sortColumn = null;
    this.sortDirection = 'asc';
    this.searchQuery = '';

    const tableId = container.getAttribute('data-enhanced-table');
    console.log(`🔧 Setting up EnhancedTable for: ${tableId}`);

    this.searchInput = document.querySelector(`[data-table-search="${tableId}"]`);
    console.log(`  - Search input selector: [data-table-search="${tableId}"]`, this.searchInput);

    this.tableBody = container.querySelector('[data-table-body]');
    this.table = container.querySelector('[data-sortable-table]');
    this.perPageSelect = container.querySelector('[data-per-page]');

    this.paginationContainer = document.querySelector(`[data-pagination-for="${tableId}"]`);
    if (this.paginationContainer) {
      if (!this.paginationContainer.querySelector('.pagination-wrapper')) {
        const wrapper = document.createElement('div');
        wrapper.className = 'pagination-wrapper';
        wrapper.style.cssText = 'display: flex; justify-content: space-between; align-items: center; padding: var(--space-4); border-top: 1px solid var(--border-color);';
        wrapper.innerHTML = `
          <div class="pagination-info" style="color: var(--text-secondary); font-size: var(--text-sm);"></div>
          <div class="pagination-controls" style="display: flex; gap: var(--space-2);"></div>
        `;
        this.paginationContainer.appendChild(wrapper);
      }
      this.paginationInfo = this.paginationContainer.querySelector('.pagination-info');
      this.paginationControls = this.paginationContainer.querySelector('.pagination-controls');
    }

    if (this.table) {
      this.init();
    }
  }

  init() {
    console.log('🔍 Initializing EnhancedTable:', {
      searchInput: this.searchInput ? 'Found' : 'NOT FOUND',
      tableBody: this.tableBody ? 'Found' : 'NOT FOUND',
      table: this.table ? 'Found' : 'NOT FOUND',
      paginationInfo: this.paginationInfo ? 'Found' : 'NOT FOUND',
      paginationControls: this.paginationControls ? 'Found' : 'NOT FOUND'
    });

    this.extractDataFromTable();

    if (this.searchInput) {
      this.searchInput.addEventListener('input', (e) => {
        console.log('🔍 Search input:', e.target.value);
        this.searchQuery = e.target.value.toLowerCase();
        this.applyFilters();
      });
      console.log('✓ Search listener attached');
    } else {
      console.warn('⚠️ Search input not found!');
    }

    if (this.table) {
      this.table.querySelectorAll('th[data-sort]').forEach(th => {
        th.addEventListener('click', () => {
          const column = th.getAttribute('data-sort');
          this.toggleSort(column);
        });
      });
    }

    if (this.perPageSelect) {
      this.perPageSelect.addEventListener('change', (e) => {
        this.perPage = parseInt(e.target.value);
        this.currentPage = 1;
        this.renderTable();
      });
    }

    this.renderTable();
  }

  extractDataFromTable() {
    if (!this.tableBody) {
      console.error('❌ tableBody is null!');
      return;
    }

    const rows = this.tableBody.querySelectorAll('tr');
    console.log(`  - Found ${rows.length} rows in tbody`);

    this.data = Array.from(rows).map((row, idx) => {
      const rowClone = row.cloneNode(true);

      rowClone.querySelectorAll('.copy-icon').forEach(icon => icon.remove());

      const cells = row.querySelectorAll('td');
      const allCellText = [];

      const rowData = {
        _html: rowClone.innerHTML,
        _element: row,
        _attributes: {}
      };

      Array.from(row.attributes).forEach(attr => {
        rowData._attributes[attr.name] = attr.value;
      });

      cells.forEach((cell, index) => {
        const th = this.table.querySelectorAll('th')[index];
        const cellText = cell.textContent.trim();
        allCellText.push(cellText);

        const columnName = th ? th.getAttribute('data-sort') : `col_${index}`;
        if (columnName) {
          if (!rowData[columnName]) {
            rowData[columnName] = cellText;
          } else {
            rowData[`${columnName}_${index}`] = cellText;
          }
        }
      });

      rowData._searchText = allCellText.join(' ').toLowerCase();

      if (idx === 0) {
        console.log('  - Sample row data:', rowData);
      }

      return rowData;
    });

    this.filteredData = [...this.data];
    console.log(`  - Extracted ${this.data.length} rows from table`);
  }

  applyFilters() {
    console.log(`🔍 Applying filters: "${this.searchQuery}"`);
    console.log(`  - Total data rows: ${this.data.length}`);

    this.filteredData = this.data.filter(row => {
      if (!this.searchQuery) return true;

      if (row._searchText) {
        return row._searchText.includes(this.searchQuery);
      }

      return Object.keys(row).some(key => {
        if (key.startsWith('_')) return false;
        const value = String(row[key]).toLowerCase();
        return value.includes(this.searchQuery);
      });
    });

    console.log(`  - Filtered rows: ${this.filteredData.length}`);
    this.currentPage = 1;
    this.renderTable();
  }

  toggleSort(column) {
    if (this.sortColumn === column) {
      this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
      this.sortColumn = column;
      this.sortDirection = 'asc';
    }

    this.filteredData.sort((a, b) => {
      let valA = a[column] || '';
      let valB = b[column] || '';

      const numA = parseFloat(valA.replace(/[^\d.-]/g, ''));
      const numB = parseFloat(valB.replace(/[^\d.-]/g, ''));

      if (!isNaN(numA) && !isNaN(numB)) {
        valA = numA;
        valB = numB;
      }

      if (valA < valB) return this.sortDirection === 'asc' ? -1 : 1;
      if (valA > valB) return this.sortDirection === 'asc' ? 1 : -1;
      return 0;
    });

    this.updateSortIndicators();
    this.renderTable();
  }

  updateSortIndicators() {
    this.table.querySelectorAll('th[data-sort]').forEach(th => {
      th.classList.remove('sort-asc', 'sort-desc');
      const column = th.getAttribute('data-sort');
      if (column === this.sortColumn) {
        th.classList.add(`sort-${this.sortDirection}`);
      }
    });
  }

  renderTable() {
    const start = (this.currentPage - 1) * this.perPage;
    const end = start + this.perPage;
    const pageData = this.filteredData.slice(start, end);

    if (this.tableBody) {
      this.tableBody.innerHTML = '';

      if (pageData.length === 0) {
        const colspan = this.table.querySelectorAll('th').length;
        this.tableBody.innerHTML = `
          <tr>
            <td colspan="${colspan}" style="text-align: center; padding: 2rem; color: var(--text-tertiary);">
              ${this.searchQuery ? 'Không tìm thấy kết quả phù hợp' : 'Không có dữ liệu'}
            </td>
          </tr>
        `;
      } else {
        pageData.forEach(rowData => {
          const tr = document.createElement('tr');
          tr.innerHTML = rowData._html;

          if (rowData._attributes) {
            Object.keys(rowData._attributes).forEach(attrName => {
              tr.setAttribute(attrName, rowData._attributes[attrName]);
            });
          }

          this.tableBody.appendChild(tr);
        });
      }
    }

    this.renderPagination();

    if (typeof window.reinitCopyToClipboard === 'function') {
      window.reinitCopyToClipboard(this.tableBody);
    }
  }

  renderPagination() {
    const totalItems = this.filteredData.length;
    const totalPages = Math.ceil(totalItems / this.perPage);
    const start = totalItems === 0 ? 0 : (this.currentPage - 1) * this.perPage + 1;
    const end = Math.min(start + this.perPage - 1, totalItems);

    if (this.paginationInfo) {
      this.paginationInfo.innerHTML = `
        Hiển thị <strong>${start}-${end}</strong> trong <strong>${totalItems}</strong> bản ghi
      `;
    }

    if (this.paginationControls) {
      this.paginationControls.innerHTML = '';

      const prevBtn = document.createElement('button');
      prevBtn.className = 'pagination-btn';
      prevBtn.innerHTML = '‹';
      prevBtn.disabled = this.currentPage === 1;
      prevBtn.addEventListener('click', () => this.goToPage(this.currentPage - 1));
      this.paginationControls.appendChild(prevBtn);

      const maxButtons = 5;
      let startPage = Math.max(1, this.currentPage - Math.floor(maxButtons / 2));
      let endPage = Math.min(totalPages, startPage + maxButtons - 1);

      if (endPage - startPage < maxButtons - 1) {
        startPage = Math.max(1, endPage - maxButtons + 1);
      }

      if (startPage > 1) {
        const firstBtn = document.createElement('button');
        firstBtn.className = 'pagination-btn';
        firstBtn.textContent = '1';
        firstBtn.addEventListener('click', () => this.goToPage(1));
        this.paginationControls.appendChild(firstBtn);

        if (startPage > 2) {
          const ellipsis = document.createElement('span');
          ellipsis.textContent = '...';
          ellipsis.style.padding = '0.5rem';
          this.paginationControls.appendChild(ellipsis);
        }
      }

      for (let i = startPage; i <= endPage; i++) {
        const btn = document.createElement('button');
        btn.className = 'pagination-btn';
        if (i === this.currentPage) {
          btn.classList.add('active');
        }
        btn.textContent = i;
        btn.addEventListener('click', () => this.goToPage(i));
        this.paginationControls.appendChild(btn);
      }

      if (endPage < totalPages) {
        if (endPage < totalPages - 1) {
          const ellipsis = document.createElement('span');
          ellipsis.textContent = '...';
          ellipsis.style.padding = '0.5rem';
          this.paginationControls.appendChild(ellipsis);
        }

        const lastBtn = document.createElement('button');
        lastBtn.className = 'pagination-btn';
        lastBtn.textContent = totalPages;
        lastBtn.addEventListener('click', () => this.goToPage(totalPages));
        this.paginationControls.appendChild(lastBtn);
      }

      const nextBtn = document.createElement('button');
      nextBtn.className = 'pagination-btn';
      nextBtn.innerHTML = '›';
      nextBtn.disabled = this.currentPage === totalPages || totalPages === 0;
      nextBtn.addEventListener('click', () => this.goToPage(this.currentPage + 1));
      this.paginationControls.appendChild(nextBtn);
    }
  }

  goToPage(page) {
    const totalPages = Math.ceil(this.filteredData.length / this.perPage);
    if (page < 1 || page > totalPages) return;

    this.currentPage = page;
    this.renderTable();

    this.container.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
}

function initEnhancedTables() {
  const containers = document.querySelectorAll('.data-table-container');
  console.log(`📊 Initializing ${containers.length} enhanced tables`);
  containers.forEach(container => {
    new EnhancedTable(container);
  });
}

if (typeof window !== 'undefined') {
  window.EnhancedTable = EnhancedTable;
  window.initEnhancedTables = initEnhancedTables;
}
