# Cập nhật: Nhập JSON từ Test Cases

## Thay đổi

Chức năng "Nhập JSON" giờ đây hỗ trợ **2 định dạng** JSON:

### 1. Định dạng Export (như trước)
```json
[
  {
    "id": 1,
    "event_name": "họp nhóm",
    "start_time": "2025-11-10T18:00:00",
    "location": "phòng 302",
    "reminder_minutes": 15
  }
]
```

### 2. Định dạng Test Case (MỚI)
```json
[
  {
    "input": "Họp nhóm lúc 10h sáng mai ở phòng 302, nhắc trước 15 phút",
    "expected": {
      "event": "họp nhóm",
      "time_str": "10h sáng mai",
      "location": "phòng 302",
      "reminder_minutes": 15
    }
  }
]
```

## Cách hoạt động

- **Định dạng Export**: Nhập trực tiếp các trường `event_name`, `start_time`, `location`, `reminder_minutes`.
- **Định dạng Test Case**: Tự động nhận diện format có field `input` và `expected`, sau đó:
  1. Lấy nội dung từ field `input`
  2. Xử lý qua NLP pipeline (như khi bạn nhập thủ công trong app)
  3. Chuyển đổi thành sự kiện với start_time ISO
  4. Lưu vào database

## Lưu ý

- File test case từ `./tests/` (như `test_cases.json`, `extended_test_cases_10000.json`) giờ có thể nhập trực tiếp.
- Một số sự kiện có thể không được nhập nếu:
  - Thời gian tương đối đã qua (ví dụ: "mai" trong file test cũ)
  - Input không đủ thông tin (thiếu sự kiện hoặc thời gian)
  - Lỗi phân tích cú pháp

## Ví dụ sử dụng

1. Bấm nút **"Nhập JSON"** trong app
2. Chọn file:
   - `schedule_export.json` (export từ app) → nhập trực tiếp
   - `tests/test_cases.json` (test cases) → tự động parse qua NLP
   - `tests/extended_test_cases_10000.json` → tự động parse 10,000 cases
3. App sẽ hiển thị số sự kiện đã nhập thành công

## Test

Chạy test để xác nhận cả 2 định dạng hoạt động:
```powershell
python test_import_formats.py
```

## Files thay đổi

- `services/import_service.py`: Thêm logic phát hiện và xử lý test case format
- `main.py`: Truyền `nlp_pipeline` vào `import_from_json()`
