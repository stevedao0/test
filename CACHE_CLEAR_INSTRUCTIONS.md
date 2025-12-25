# Hướng dẫn xem thay đổi giao diện mới

## Vấn đề: Không thấy thay đổi giao diện

CSS đã được cập nhật nhưng trình duyệt đang cache bản cũ.

## Giải pháp: Hard Refresh (Xóa cache trình duyệt)

### Windows/Linux:
```
Ctrl + Shift + R
hoặc
Ctrl + F5
hoặc
Shift + F5
```

### Mac:
```
Cmd + Shift + R
hoặc
Cmd + Option + R
```

### Hoặc xóa cache thủ công:

**Chrome:**
1. Mở DevTools (F12)
2. Click chuột phải vào nút Refresh
3. Chọn "Empty Cache and Hard Reload"

**Firefox:**
1. Mở DevTools (F12)
2. Click chuột phải vào nút Refresh
3. Chọn "Empty Cache and Hard Reload"

**Edge:**
1. Mở DevTools (F12)
2. Click chuột phải vào nút Refresh
3. Chọn "Empty cache and hard refresh"

## Xác nhận CSS mới đã load:

1. Mở DevTools (F12)
2. Vào tab Network
3. Reload trang
4. Tìm file `main.css` hoặc `variables.css`
5. Check xem file có size mới không:
   - `variables.css`: ~4.7KB
   - `components.css`: ~25KB
   - `enhancements.css`: ~8.7KB
   - `form-enhancements.css`: ~7.2KB (file mới)

## Các thay đổi bạn sẽ thấy:

### 1. Màu sắc
- Màu chính: Xanh dương (#2563EB) thay vì tím
- Background: Gradient nhẹ từ #F8FAFC sang #EFF6FF

### 2. Buttons
- Hover: Nút sẽ "bay lên" một chút (translateY)
- Shadow mượt mà hơn

### 3. Cards
- Border radius lớn hơn (16px)
- Shadow nhẹ hơn
- Hover effect: Card sẽ nâng lên

### 4. Forms
- Input có shadow nhẹ
- Focus state: Ring màu xanh dương
- Money calculator: Gradient background

### 5. Tables
- Header có gradient
- Row hover: Scale nhẹ + background màu xanh nhạt

### 6. Animations
- Cards xuất hiện với fadeSlideUp
- Smooth transitions everywhere

## Nếu vẫn không thấy:

1. **Kiểm tra console (F12 > Console)**:
   - Xem có lỗi CSS nào không?

2. **Kiểm tra file được load**:
   - DevTools > Network > Filter: CSS
   - Xem có `form-enhancements.css` không?

3. **Restart server** (nếu đang chạy local):
   ```bash
   # Tắt server (Ctrl+C)
   # Chạy lại
   ./start_server.sh  # hoặc start_server.bat trên Windows
   ```

4. **Xóa toàn bộ cache trình duyệt**:
   - Chrome: Settings > Privacy > Clear browsing data
   - Chọn "Cached images and files"
   - Time range: "All time"
   - Click "Clear data"

## Test nhanh:

Mở Developer Console (F12) và chạy:
```javascript
console.log(getComputedStyle(document.body).background);
```

Nếu thấy gradient `linear-gradient(...)` thì CSS mới đã load thành công!
