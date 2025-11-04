# Hệ thống Thông báo Kép (Dual Notification)

## Yêu cầu nghiệp vụ

**Tất cả** sự kiện khi đến giờ (`start_time`) phải hiển thị popup thông báo, bất kể có đặt "nhắc tôi trước" hay không.

### Trước khi cập nhật
- Chỉ popup khi `reminder_minutes > 0`.
- Sự kiện không có "nhắc trước" sẽ không được thông báo → **Thiếu ràng buộc nghiệp vụ**.

### Sau khi cập nhật
- **2 loại thông báo:**
  1. **Thông báo "nhắc trước"** (Pre-reminder): Khi `now >= start_time - reminder_minutes` và `reminder_minutes > 0`.
     - Popup: "Sự kiện sắp diễn ra... (Nhắc trước X phút)"
     - Chuyển `status='pending'` → `'reminded'`.
  2. **Thông báo "đúng giờ"** (On-time): Khi `now >= start_time`.
     - Popup: "Sự kiện đã đến giờ..."
     - Chuyển `status='pending'` hoặc `'reminded'` → `'notified'`.

- **Kết quả:**
  - Sự kiện **có** "nhắc trước": **2 popup** (trước X phút + đúng giờ).
  - Sự kiện **không có** "nhắc trước": **1 popup** (chỉ đúng giờ).

## Thay đổi kỹ thuật

### 1. Database Manager (`database/db_manager.py`)
- `get_pending_reminders(now_iso)`:
  - **Trước:** `WHERE start_time > ? AND status='pending' AND reminder_minutes > 0`
  - **Sau:** `WHERE start_time > ? AND status IN ('pending', 'reminded')`
  - Lý do: Lấy cả sự kiện `status='reminded'` để popup "đúng giờ" sau khi đã popup "nhắc trước".

### 2. Notification Service (`services/notification_service.py`)
- **Thêm 3 trạng thái status:**
  - `'pending'`: Chưa popup lần nào.
  - `'reminded'`: Đã popup "nhắc trước", chờ popup "đúng giờ".
  - `'notified'`: Đã popup "đúng giờ", hoàn tất.

- **Logic trong `check_reminders_loop()`:**
  ```python
  for ev in events:
      status = ev['status']
      rem_min = ev['reminder_minutes']
      
      # Điều kiện 1: Popup "nhắc trước" (nếu có reminder > 0 và status='pending')
      if status == 'pending' and rem_min > 0:
          if now >= (start_time - timedelta(minutes=rem_min)):
              show_popup_pre_reminder(...)
              update_status(ev_id, 'reminded')
              continue
      
      # Điều kiện 2: Popup "đúng giờ" (cho 'pending' và 'reminded')
      if status in ('pending', 'reminded'):
          if now >= start_time:
              show_popup_on_time(...)
              update_status(ev_id, 'notified')
  ```

- **Thêm 2 hàm popup riêng:**
  - `show_popup_pre_reminder(event_name, event_time, reminder_minutes)`: Tiêu đề "Nhắc nhở Sự kiện", nội dung "sắp diễn ra" + "(Nhắc trước X phút)".
  - `show_popup_on_time(event_name, event_time)`: Tiêu đề "Thông báo Sự kiện", nội dung "đã đến giờ".

- **Cả 2 hàm đều:** Phát âm thanh thông báo (`winsound.MessageBeep` hoặc `Tk.bell`).

## Ví dụ minh họa

### Case 1: Sự kiện có "nhắc trước 10 phút"
- Tạo: "Họp nhóm 10h sáng mai nhắc tôi trước 10 phút"
- `start_time = 2025-11-06T10:00:00`, `reminder_minutes = 10`, `status = 'pending'`

**Timeline:**
1. **09:50** (now >= 10:00 - 10 phút):
   - Popup: "Sự kiện sắp diễn ra: Họp nhóm, Lúc: 2025-11-06T10:00 (Nhắc trước 10 phút)"
   - `status → 'reminded'`
2. **10:00** (now >= 10:00):
   - Popup: "Sự kiện đã đến giờ: Họp nhóm, Lúc: 2025-11-06T10:00"
   - `status → 'notified'`

### Case 2: Sự kiện không có "nhắc trước"
- Tạo: "Gặp khách 14h thứ 2 tại văn phòng"
- `start_time = 2025-11-10T14:00:00`, `reminder_minutes = 0`, `status = 'pending'`

**Timeline:**
1. **14:00** (now >= 14:00):
   - Popup: "Sự kiện đã đến giờ: Gặp khách, Lúc: 2025-11-10T14:00"
   - `status → 'notified'`

## Test đơn vị (Logic SQL)

```python
# Tạo 2 sự kiện: (1) có reminder, (2) không có reminder
# Initial: cả 2 status='pending'
events = db.get_pending_reminders('2025-11-05T14:00:00')
# → 2 events

# Sau khi popup "nhắc trước" cho event 1
db.update_event_status(1, 'reminded')
events = db.get_pending_reminders('2025-11-05T14:00:00')
# → 2 events (status: 'reminded' và 'pending')

# Sau khi popup "đúng giờ" cho event 1
db.update_event_status(1, 'notified')
events = db.get_pending_reminders('2025-11-05T14:00:00')
# → 1 event (chỉ còn event 2 status='pending')

# Sau khi popup "đúng giờ" cho event 2
db.update_event_status(2, 'notified')
events = db.get_pending_reminders('2025-11-05T14:00:00')
# → 0 events
```

## Lợi ích
- Đảm bảo **không bỏ sót** bất kỳ sự kiện nào khi đến giờ.
- Người dùng có thể tùy chọn "nhắc trước" để nhận popup sớm hơn, nhưng vẫn nhận popup "đúng giờ".
- Không cần thay đổi schema DB, chỉ cần thêm 1 giá trị status mới (`'reminded'`).

## Ghi chú
- Vòng lặp kiểm tra mỗi 60s → độ chính xác ±1 phút.
- Nếu app bị tắt trong khoảng thời gian giữa 2 popup, khi khởi động lại sẽ kiểm tra lại và popup cho những sự kiện chưa `notified`.
- Có thể thêm log để ghi lại thời điểm popup (audit trail) nếu cần.
