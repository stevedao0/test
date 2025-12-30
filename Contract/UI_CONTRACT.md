# UI_CONTRACT

Mục tiêu: tách UI thành repo riêng (templates/static). UI team có thể thiết kế/đổi layout/UX độc lập, sau đó copy về backend repo để chạy ngay.

Nguyên tắc: Backend giữ nguyên routes + form field names. UI chỉ thay đổi trình bày.


## 1) Quy ước bàn giao UI repo

UI repo (ví dụ `contract-ui`) nên có:

- `templates/` (Jinja2 HTML)
- `static/` (css/js/img)
- `UI_CONTRACT.md` (file này, copy từ backend sang UI repo để làm spec)

Khi UI hoàn thiện, copy:

- `contract-ui/templates/*` -> `backend/app/ui/templates/*`
- `contract-ui/static/*` -> `backend/app/ui/static/*`


## 2) Quy ước bắt buộc (để không vỡ backend)

- Không đổi URL (route) nếu không có trao đổi với backend.
- Không đổi `name="..."` của các input trong form (vì FastAPI đọc theo key).
- Có thể đổi layout, CSS, JS, chia component, `base.html`, partials,... thoải mái.
- Template phải render được với Jinja2.


## 3) Danh sách màn hình hiện có (GET) và template

### 3.1 /documents/new

- **Route**: `GET /documents/new`
- **Template**: `document_form.html`
- **Query params**:
  - `doc_type` (optional) (giá trị: `contract` | `annex`)
  - `year` (optional)
  - `contract_no` (optional) (dùng khi tạo phụ lục)
  - `error` (optional)
- **Context vars**:
  - `title`: str
  - `doc_type`: str
  - `contracts`: list[dict] (danh sách hợp đồng để chọn)
  - `preview`: dict (prefill khi tạo phụ lục)
  - `year`: int
  - `today`: str (ISO date)
  - `selected_contract_no`: str
  - `error`: str | None
  - `breadcrumbs`: list[dict]


### 3.2 /contracts

- **Route**: `GET /contracts`
- **Template**: `contracts_list.html`
- **Query params**:
  - `year` (optional)
  - `download` (optional) (link download docx)
  - `download2` (optional) (link download excel)
  - `catalogue` (optional) (`all` | `yes` | `no`)
- **Context vars**:
  - `title`: str
  - `year`: int
  - `rows`: list[dict]
  - `stats`: dict
  - `download`: str | None
  - `download2`: str | None
  - `catalogue_filter`: str
  - `breadcrumbs`: list[dict]


### 3.3 /annexes

- **Route**: `GET /annexes`
- **Template**: `annexes_list.html`
- **Query params**:
  - `year` (optional)
  - `download` (optional)
  - `catalogue` (optional) (`all` | `yes` | `no`)
- **Context vars**:
  - `title`: str
  - `year`: int
  - `rows`: list[dict]
  - `stats`: dict
  - `download`: str | None
  - `catalogue_filter`: str
  - `breadcrumbs`: list[dict]


### 3.4 /works/import

- **Route**: `GET /works/import`
- **Template**: `works_import.html`
- **Query params**:
  - `error` (optional)
  - `message` (optional)
- **Context vars**:
  - `title`: str
  - `error`: str | None
  - `message`: str | None
  - `breadcrumbs`: list[dict]


### 3.5 /catalogue/upload

- **Route**: `GET /catalogue/upload`
- **Template**: `catalogue_upload.html`
- **Query params**:
  - `year` (optional)
  - `contract_no` (optional)
  - `annex_no` (optional)
  - `error` (optional)
  - `message` (optional)
- **Context vars**:
  - `title`: str
  - `year`: int
  - `contract_no`: str
  - `annex_no`: str
  - `error`: str | None
  - `message`: str | None
  - `breadcrumbs`: list[dict]


### 3.6 /admin/ops

- **Route**: `GET /admin/ops`
- **Template**: `admin_ops.html`
- **Context vars**:
  - `title`: str
  - `logs`: list[dict] (name, size)
  - `backups`: list[dict] (name, size)
  - `breadcrumbs`: list[dict]


## 4) Danh sách form actions (POST) và field names

### 4.1 POST /documents

- **Route**: `POST /documents`
- **Ghi chú**: dispatcher gọi sang `POST /contracts` hoặc `POST /annexes`
- **Fields**:
  - `doc_type` (required)
  - `ngay_lap_hop_dong`
  - `so_hop_dong_4`
  - `contract_no`
  - `annex_no`
  - `ngay_ky_hop_dong`
  - `ngay_ky_phu_luc`
  - `linh_vuc`
  - `don_vi_ten`
  - `don_vi_dia_chi`
  - `don_vi_dien_thoai`
  - `don_vi_nguoi_dai_dien`
  - `don_vi_chuc_vu`
  - `don_vi_mst`
  - `don_vi_email`
  - `so_CCCD`
  - `ngay_cap_CCCD`
  - `nguoi_thuc_hien_email`
  - `kenh_ten`
  - `kenh_id`
  - `so_tien_chua_GTGT`
  - `thue_percent`


### 4.2 POST /contracts

- **Route**: `POST /contracts`
- **Fields**:
  - `ngay_lap_hop_dong` (required)
  - `so_hop_dong_4` (required)
  - `linh_vuc`
  - `don_vi_ten`
  - `don_vi_dia_chi`
  - `don_vi_dien_thoai`
  - `don_vi_nguoi_dai_dien`
  - `don_vi_chuc_vu`
  - `don_vi_mst`
  - `don_vi_email`
  - `so_CCCD`
  - `ngay_cap_CCCD`
  - `nguoi_thuc_hien_email`
  - `kenh_ten`
  - `kenh_id`
  - `so_tien_chua_GTGT`
  - `thue_percent`


### 4.3 POST /contracts/{year}/update

- **Route**: `POST /contracts/{year}/update`
- **Fields**:
  - `contract_no` (required)
  - `ngay_lap_hop_dong` (required)
  - `don_vi_ten`
  - `don_vi_dia_chi`
  - `don_vi_dien_thoai`
  - `don_vi_nguoi_dai_dien`
  - `don_vi_chuc_vu`
  - `don_vi_mst`
  - `don_vi_email`
  - `kenh_ten`
  - `kenh_id`
  - `so_tien_chua_GTGT`
  - `thue_percent`


### 4.4 POST /annexes

- **Route**: `POST /annexes`
- **Fields**:
  - `contract_no` (required)
  - `annex_no`
  - `ngay_ky_hop_dong`
  - `ngay_ky_phu_luc` (required)
  - `linh_vuc`
  - `don_vi_ten`
  - `don_vi_dia_chi`
  - `don_vi_dien_thoai`
  - `don_vi_nguoi_dai_dien`
  - `don_vi_chuc_vu`
  - `don_vi_mst`
  - `don_vi_email`
  - `so_CCCD`
  - `ngay_cap_CCCD`
  - `kenh_ten`
  - `kenh_id`
  - `nguoi_thuc_hien_email`
  - `so_tien_chua_GTGT`
  - `thue_percent`


### 4.5 POST /works/import

- **Route**: `POST /works/import`
- **Fields**:
  - `import_file` (file)
  - `nguoi_thuc_hien`


### 4.6 POST /catalogue/upload

- **Route**: `POST /catalogue/upload`
- **Fields**:
  - `year` (required)
  - `contract_no` (required)
  - `annex_no`
  - `catalogue_file` (file)


## 5) Download/static URLs (để UI đặt link đúng)

- Static:
  - `GET /static/...`

- File downloads (được dùng trong list pages):
  - `GET /download/{year}/{filename}` (docx)
  - `GET /download_excel/{year}/{filename}` (excel)

- Storage API (JSON/download):
  - `GET /storage/files/{year}`
  - `GET /storage/docx/{year}/{filename}`
  - `GET /storage/excel/{year}/{filename}`
  - `GET /storage/excel/download/{year}`
  - `GET /storage/excel/works/download/{year}`


## 6) Checklist khi UI bàn giao

- [ ] Có đủ templates mapping đúng tên file backend đang render
- [ ] Không đổi `name=` của form fields
- [ ] Không đổi routes nếu không báo backend
- [ ] Có `css/main.css` và asset cần thiết
- [ ] Test nhanh các màn hình: `/documents/new`, `/contracts`, `/annexes`, `/works/import`, `/catalogue/upload`, `/admin/ops`
