# UI Handover (for Design Team)

## 1) Product scope
A web portal for:
- Managing contracts (Hợp đồng) and annexes (Phụ lục)
- Managing works catalogue (Danh mục tác phẩm)
- Uploading/attaching Excel catalogues to contracts/annexes
- Importing works from Excel
- Reports and exports
- Admin user management and permission matrix

Tech:
- Backend: FastAPI (server-rendered HTML via Jinja2)
- Frontend: Jinja templates + custom CSS/JS (no SPA)

---

## 2) Navigation / Layout
**Base layout**: `app/ui/templates/base.html`

### Sidebar (visibility is permission-based)
Menu items:
- Dashboard: `/dashboard` (portal.access)
- Hợp đồng: `/contracts` (contracts.read)
- Tạo tài liệu: `/documents/new` (contracts.create OR annexes.create)
- Tác phẩm: `/works` (works.read)
- Import danh mục: `/works/import` (works.import)
- Báo cáo: `/reports` (reports.view)
- Tìm kiếm: `/search` (portal.access)

Quick actions:
- Tạo hợp đồng: `/contracts/new` (contracts.create)
- Tạo phụ lục: `/annexes/new` (annexes.create)

Admin section:
- Quản lý tài khoản: `/admin/users` (admin.users.manage)
- Phân quyền: `/admin/permissions` (admin.users.manage)
- Admin Ops: `/admin/ops` (admin.ops.view)

Account:
- Đổi mật khẩu: `/account/password` (logged-in)
- Đăng xuất: `/logout`

### Shared UI patterns
- **Card layout**: header/body/footer with accent border-left color
- **Enhanced tables**: search, sort, pagination
  - JS: `app/ui/static/js/table-enhanced.js`
  - Markup: `data-enhanced-table`, `data-table-search`, `data-pagination-for`, `data-sortable-table`
- **Dropdown action menu** for table rows (contracts/annexes)
- **Modal**: used in contracts list (saved files modal, contract detail modal)
- **Alerts**: success/error banners

---

## 3) Permissions model (drives both UI visibility and backend enforcement)
Defined in: `app/auth.py`

### Permission groups
- Portal: `portal.access`
- Contracts: `contracts.read`, `contracts.create`, `contracts.update`, `contracts.delete`
- Annexes: `annexes.read`, `annexes.create`, `annexes.update`, `annexes.delete`
- Catalogue: `catalogue.upload`
- Works: `works.read`, `works.import`
- Reports: `reports.view`, `reports.export`
- Admin: `admin.users.manage`, `admin.system.manage`, `admin.ops.view`

### UI permission helper
Jinja global: `has_permission(request, 'perm')`
- Used widely to hide/show menu items and buttons.

---

## 4) Screen inventory (routes -> template -> primary purpose)

### Auth
- **Login**: `GET /login` -> `login.html`

### Dashboard
- **Dashboard**: `GET /dashboard` -> `dashboard.html`
  - KPIs for current year; owner-filtered for non-admin/mod

### Contracts
- **Contracts list**: `GET /contracts` -> `contracts_list.html`
  - Filters: year, catalogue status
  - Search/sort/pagination: EnhancedTable
  - Actions per row (permission-gated):
    - View detail (modal)
    - Edit (contracts.update)
    - Download docx
    - Download catalogue xlsx
    - Upload catalogue (catalogue.upload)
    - Create annex (annexes.create)
    - Delete (contracts.delete)
  - Inline catalogue upload panel at top (catalogue.upload)
  - Footer actions (permission-gated): create contract/annex

- **Create contract**: `GET /contracts/new` -> `contract_form.html`
- **Edit contract**: `GET /contracts/{year}/edit` -> `contract_edit.html`

### Annexes
- **Annexes list**: `GET /annexes` -> `annexes_list.html`
  - Filters: year, catalogue status
  - Actions per row (permission-gated):
    - Download docx
    - Download catalogue xlsx
    - Upload catalogue (catalogue.upload)
    - Delete (annexes.delete)
  - Inline catalogue upload panel at top (catalogue.upload)
  - Footer actions (permission-gated):
    - Create annex (annexes.create)
    - Download works catalogue file (works.read)

- **Create annex**: `GET /annexes/new` -> `annex_form.html`

### Unified document creation
- **Create document (unified)**: `GET /documents/new` -> `document_form.html`
  - Toggles between contract/annex sections

### Catalogue upload
- **Catalogue upload screen**: `GET /catalogue/upload` -> `catalogue_upload.html`
  - Used as fallback screen; list pages now have inline upload panels

### Works
- **Works list**: `GET /works` -> `works_list.html`
  - Filters: year, contract_no, annex_no
  - Download works excel (works.read)
  - Import panel (works.import)
  - Import templates (catalogue.upload)

- **Works import screen**: `GET /works/import` -> `works_import.html`
  - Download works excel (works.read)
  - Template links (catalogue.upload)
  - Import submit (works.import)

### Reports
- **Reports**: `GET /reports` -> `reports.html`
  - Export button (reports.export)

### Search
- **Search**: `GET /search` -> `search.html`
  - Owner-filtered results for non-admin/mod

### Admin
- **Admin users**: `GET /admin/users` -> `admin_users.html`
  - Create user, reset user password
  - “My account” card links to `/account/password`
  - System account recovery (admin.system.manage)

- **Admin permission matrix**: `GET /admin/permissions` -> `admin_permissions.html`

- **Admin ops**: `GET /admin/ops` -> `admin_ops.html`

---

## 5) File/template download endpoints (UI relevant)
- Export templates:
  - `/templates/export/contract/docx`
  - `/templates/export/contract/xlsx`
  - `/templates/export/annex/docx`
  - `/templates/export/annex/xlsx`

- Import templates:
  - `/templates/import/contract/xlsx`
  - `/templates/import/annex/xlsx`

- Storage downloads:
  - `/storage/excel/download/{year}` (contracts excel)
  - `/storage/excel/works/download/{year}` (works excel)
  - `/download/{year}/{filename}` (legacy docx)
  - `/download_excel/{year}/{filename}` (legacy xlsx)

---

## 6) UI component checklist (for redesign)
### Global
- Sidebar + active state
- Breadcrumbs
- Page loader
- Toast notifications

### Forms
- Consistent form-group spacing, labels, placeholder
- Validation message pattern

### Tables
- Consistent table headers + icons
- Search input pattern
- Pagination footer
- Dropdown actions pattern

### Modals
- Contract detail modal
- Saved files modal

---

## 7) Key UX notes / pain points observed
- Many pages are “dense”: consider consolidating repeated actions into consistent toolbar pattern.
- Permission-based visibility is important: design should specify how to visually communicate missing permissions (hide vs disabled).
- Admin/users vs account password: should remain clearly separated.

---

## 8) Source of truth
Templates directory:
- `app/ui/templates/*`

Static assets:
- `app/ui/static/css/*`
- `app/ui/static/js/*`

Permissions:
- `app/auth.py`

