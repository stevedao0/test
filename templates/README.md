# Templates Directory

## Yêu cầu

Để ứng dụng hoạt động, bạn cần đặt các file template DOCX vào thư mục này:

### 1. Hợp đồng chính
**File:** `HDQTGAN_PN_MR_template.docx`

Template hợp đồng chính với các placeholder:
- `{{contract_no}}` - Số hợp đồng
- `{{ngay}}`, `{{thang}}`, `{{nam}}` - Ngày ký
- `{{don_vi_ten}}` - Tên đơn vị (Bên B)
- `{{don_vi_dia_chi}}` - Địa chỉ
- `{{don_vi_dien_thoai}}` - Điện thoại
- `{{don_vi_nguoi_dai_dien}}` - Người đại diện
- `{{don_vi_chuc_vu}}` - Chức vụ
- `{{don_vi_mst}}` - Mã số thuế
- `{{don_vi_email}}` - Email
- `{{kenh_ten}}` - Tên kênh YouTube
- `{{kenh_id}}` - ID kênh YouTube
- `{{so_tien_nhuan_but}}` - Số tiền
- `{{so_tien_bang_chu}}` - Số tiền bằng chữ
- `{{linh_vuc}}` - Lĩnh vực

### 2. Phụ lục hợp đồng
**File:** `HDQTGAN_PN_MR_annex_template.docx`

Template phụ lục với các placeholder tương tự, thêm:
- `{{so_phu_luc}}` - Số phụ lục
- `{{so_hop_dong_day_du}}` - Số hợp đồng gốc
- `{{ngay_ky_hop_dong}}`, `{{thang_ky_hop_dong}}`, `{{nam_ky_hop_dong}}` - Ngày ký hợp đồng gốc
- `{{ngay_ky_phu_luc}}`, `{{thang_ky_phu_luc}}`, `{{nam_ky_phu_luc}}` - Ngày ký phụ lục

## Cách tạo template từ file Word mẫu

Nếu bạn có file Word mẫu (chưa có placeholder), bạn có thể:

### Option 1: Tự chỉnh sửa
1. Mở file Word mẫu
2. Thay các giá trị cụ thể bằng placeholder (ví dụ: thay "0001/2025/HĐQTGAN-PN/MR" thành `{{contract_no}}`)
3. Lưu với tên `HDQTGAN_PN_MR_template.docx` vào thư mục này

### Option 2: Dùng script tự động
1. Đặt file DOCX mẫu vào thư mục `Mau hop dong/`
   - Hợp đồng: `Nam_SHD_SCTT_Ten kenh_MR.docx`
   - Phụ lục: `Nam_SHD_SPL_SCTT_Ten kenh_MR.docx`
2. Sửa đường dẫn trong `scripts/make_template.py` (dòng 651-662)
3. Chạy: `python scripts/make_template.py`

Script sẽ tự động convert các giá trị cụ thể thành placeholder.

## Kiểm tra

Sau khi đặt template, kiểm tra:
```bash
ls -l templates/
# Phải có 2 file:
# - HDQTGAN_PN_MR_template.docx
# - HDQTGAN_PN_MR_annex_template.docx
```

## Lưu ý

- Template phải là file DOCX (không phải DOC, PDF)
- Placeholder phải dùng cú pháp Jinja2: `{{variable_name}}`
- Giữ nguyên format/style của Word (font, màu, căn lề, v.v.)
