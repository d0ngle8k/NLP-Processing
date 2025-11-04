# Tính năng mới - Duplicate Detection & Auto-Reset ID

## 📋 Tổng quan

Phiên bản này bổ sung 2 tính năng quan trọng theo nghiệp vụ của senior developer:

### 1. ✅ Kiểm tra trùng lặp thời gian (Duplicate Time Detection)
- **Mục đích**: Ngăn chặn xung đột lịch trình khi 2 sự kiện được đặt cùng một thời điểm
- **Độ chính xác**: Kiểm tra trùng lặp đến cấp phút (YYYY-MM-DD HH:MM)
- **Áp dụng cho**: Cả thêm mới (add_event) và chỉnh sửa (update_event)

### 2. 🔄 Tự động reset ID về 1 khi xóa hết sự kiện
- **Mục đích**: Đảm bảo ID luôn bắt đầu từ 1 khi database trống
- **Cơ chế**: Tự động reset `sqlite_sequence` khi sự kiện cuối cùng bị xóa
- **Lợi ích**: Database sạch sẽ, ID không nhảy số khi bắt đầu lại

---

## 🎯 Chi tiết triển khai

### Kiểm tra trùng lặp thời gian

#### API Changes

**database/db_manager.py**
```python
# Phương thức mới
def check_duplicate_time(start_time_iso: str, exclude_id: int = None) -> List[Dict[str, Any]]
```

**main.py - handle_add_event()**
```python
result = self.db_manager.add_event(event_dict)

if not result.get('success'):
    if result.get('error') == 'duplicate_time':
        # Hiển thị danh sách các sự kiện trùng
        duplicates = result.get('duplicates', [])
        # ... show error dialog ...
```

#### Ví dụ sử dụng

```python
from database.db_manager import DatabaseManager

db = DatabaseManager()

# Thêm sự kiện đầu tiên
event1 = {
    'event': 'Họp team',
    'start_time': '2025-11-06T10:00:00',
    'end_time': None,
    'location': 'Phòng 302',
    'reminder_minutes': 15
}
result1 = db.add_event(event1)
# => {'success': True}

# Thử thêm sự kiện trùng giờ
event2 = {
    'event': 'Gặp khách',
    'start_time': '2025-11-06T10:00:00',  # Cùng thời điểm!
    'end_time': None,
    'location': 'Phòng 401',
    'reminder_minutes': 0
}
result2 = db.add_event(event2)
# => {
#     'success': False,
#     'error': 'duplicate_time',
#     'duplicates': [{'id': 1, 'event_name': 'Họp team', ...}]
# }
```

#### UI/UX

Khi người dùng thử thêm sự kiện trùng thời gian:

```
❌ Trùng lặp thời gian

Đã có sự kiện khác vào thời điểm này!

Thời gian: 2025-11-06T10:00

Sự kiện trùng:
  • ID 1: Họp team - 2025-11-06T10:00
  • ID 2: Meeting - 2025-11-06T10:00

Vui lòng chọn thời gian khác.
```

---

### Auto-reset ID khi xóa hết

#### API Changes

**database/db_manager.py - delete_event()**
```python
def delete_event(self, event_id: int) -> None:
    with self._conn() as conn:
        conn.execute("DELETE FROM events WHERE id=?", (event_id,))
        
        # Kiểm tra nếu database trống
        cur = conn.execute("SELECT COUNT(*) FROM events")
        count = cur.fetchone()[0]
        
        if count == 0:
            # Reset AUTOINCREMENT counter
            conn.execute("DELETE FROM sqlite_sequence WHERE name='events'")
```

#### Ví dụ sử dụng

```python
from database.db_manager import DatabaseManager

db = DatabaseManager()

# Thêm 3 sự kiện
db.add_event({'event': 'E1', 'start_time': '2025-11-06T09:00:00', ...})
db.add_event({'event': 'E2', 'start_time': '2025-11-06T10:00:00', ...})
db.add_event({'event': 'E3', 'start_time': '2025-11-06T11:00:00', ...})

all_events = db.get_all_events()
# => [{'id': 1, ...}, {'id': 2, ...}, {'id': 3, ...}]

# Xóa tất cả
db.delete_event(1)
db.delete_event(2)
db.delete_event(3)  # ← Tự động reset sqlite_sequence

# Thêm sự kiện mới
db.add_event({'event': 'New Event', 'start_time': '2025-11-07T09:00:00', ...})

new_events = db.get_all_events()
# => [{'id': 1, ...}]  ← ID bắt đầu lại từ 1!
```

---

## 🧪 Testing

### Test 1: Duplicate Detection

```bash
# Thêm sự kiện 1
Lập lịch: Họp team lúc 10h sáng mai ở phòng 302
→ ✅ Thành công

# Thêm sự kiện 2 (trùng giờ)
Lập lịch: Gặp khách 10h sáng mai tại quán cafe
→ ❌ Trùng lặp thời gian (hiện dialog báo lỗi)

# Thêm sự kiện 3 (khác giờ)
Lập lịch: Ăn trưa 12h sáng mai
→ ✅ Thành công
```

### Test 2: ID Reset

```bash
# Trạng thái ban đầu: 3 events với ID 5, 6, 7
ID: 5, 6, 7

# Xóa tất cả
→ Xóa ID 5... OK
→ Xóa ID 6... OK
→ Xóa ID 7... OK (tự động reset)

# Thêm sự kiện mới
Lập lịch: Họp mới 9h sáng mai
→ ✅ Thành công với ID = 1
```

---

## 🎨 Design Decisions (Senior Developer Approach)

### 1. Return dict instead of raising exceptions
```python
# ❌ Bad: Throwing exceptions
def add_event(event_dict):
    if duplicate:
        raise DuplicateTimeError("...")
    conn.execute(...)

# ✅ Good: Returning result object
def add_event(event_dict) -> Dict[str, Any]:
    if duplicate:
        return {'success': False, 'error': 'duplicate_time', 'duplicates': [...]}
    conn.execute(...)
    return {'success': True}
```

**Lý do**:
- Dễ test hơn (không cần try/except)
- Caller có quyền quyết định cách xử lý
- Có thể return thêm metadata (danh sách duplicates)

### 2. Kiểm tra ở database layer, không phải UI layer
```python
# ❌ Bad: Check in UI
def handle_add_event():
    duplicates = db.check_duplicate_time(time)
    if duplicates:
        show_error()
    else:
        db.add_event()

# ✅ Good: Check in database
def add_event(event_dict):
    duplicates = self.check_duplicate_time(...)
    if duplicates:
        return {'success': False, ...}
    # Insert...
```

**Lý do**:
- Tránh race condition (2 requests cùng lúc)
- Logic nghiệp vụ tập trung ở 1 nơi
- Dễ reuse cho API/CLI/GUI

### 3. Auto-reset ID transaction-safe
```python
def delete_event(event_id):
    with self._conn() as conn:  # ← Transaction context
        conn.execute("DELETE ...")
        count = conn.execute("SELECT COUNT(*)").fetchone()[0]
        if count == 0:
            conn.execute("DELETE FROM sqlite_sequence ...")
```

**Lý do**:
- Đảm bảo atomicity (hoặc xóa + reset, hoặc không làm gì)
- Tránh data corruption nếu crash giữa chừng

### 4. Show max 3 duplicates in error message
```python
dup_info = []
for d in duplicates[:3]:  # ← Limit to 3
    dup_info.append(f"  • ID {d['id']}: ...")
```

**Lý do**:
- Tránh dialog quá dài (nếu có 100 duplicates)
- User chỉ cần biết "có trùng", không cần xem hết
- Better UX

---

## 📊 Database Schema (Unchanged)

```sql
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- ← Auto-increment
    event_name TEXT NOT NULL,
    start_time TEXT NOT NULL,  -- ← Used for duplicate check
    end_time TEXT,
    location TEXT,
    reminder_minutes INTEGER DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'pending'
);

-- SQLite internal table (managed automatically)
CREATE TABLE sqlite_sequence (
    name TEXT,
    seq INTEGER
);
```

---

## ⚡ Performance

- **check_duplicate_time()**: O(1) với index trên start_time
  ```sql
  CREATE INDEX IF NOT EXISTS idx_start_time ON events(start_time);
  ```
- **delete_event()**: +1 SELECT COUNT query (negligible overhead)
- **No impact on get_all_events() và search queries**

---

## 🔒 Edge Cases Handled

1. **Concurrent inserts**: SQLite transaction isolation prevents race conditions
2. **Timezone handling**: Comparison uses full ISO string (preserves timezone)
3. **Null timestamps**: check_duplicate_time() returns empty list if input invalid
4. **Update existing event**: exclude_id parameter prevents self-conflict
5. **Partial deletes**: Only resets when count == 0 (not just deleted last ID)

---

## 📝 Commit Message Format

```
feat(database): add duplicate time checking and auto-reset ID when all events deleted

- Add check_duplicate_time() method to detect same datetime conflicts
- update_event() and add_event() now return result dict with success/error info
- UI shows clear error messages with list of conflicting events
- Auto-reset sqlite_sequence when last event is deleted (ID starts from 1 again)
- Prevents scheduling conflicts at same date+time (down to minute precision)
- Senior dev implementation: comprehensive validation with user-friendly feedback
```

---

## 🚀 Future Enhancements

1. **Soft overlaps**: Detect events that partially overlap (not just exact match)
2. **Conflict resolution**: Suggest alternative times
3. **Batch operations**: Optimize for bulk delete/insert
4. **Audit log**: Track ID resets and duplicate attempts
5. **Config**: Allow users to disable duplicate checking if needed

---

**Version**: 1.1.0  
**Date**: November 5, 2025  
**Author**: Senior Developer Implementation
