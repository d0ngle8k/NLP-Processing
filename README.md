# Trợ lý Lịch trình Cá nhân (NLP Tiếng Việt)

Ứng dụng desktop (Python + Tkinter) giúp bạn tạo/sửa/xóa sự kiện lịch bằng câu lệnh tiếng Việt tự nhiên, có nhắc nhở pop-up, và hỗ trợ nhập/xuất JSON, ICS.

## Nội dung

- Tính năng chính
- Kiến trúc & luồng xử lý
- Cấu trúc thư mục và tệp chính
- Yêu cầu hệ thống
- Cài đặt và chạy (Windows PowerShell)
- Kiểm thử (F1 macro)
- Cơ sở dữ liệu (SQLite)
- Nhập/Xuất JSON & ICS
- Đóng gói (.exe) bằng PyInstaller
- Sự cố thường gặp (Troubleshooting)

---

## Tính năng chính

- Nhập câu lệnh tiếng Việt để tạo sự kiện: ví dụ “Họp nhóm lúc 10h sáng mai ở phòng 302, nhắc trước 15 phút”.
- Lịch trực quan (tkcalendar) và bảng danh sách sự kiện theo ngày.
- Sửa/xóa sự kiện ngay trong ứng dụng (chỉnh sửa inline).
- Nhắc nhở pop-up trước sự kiện theo số phút cấu hình.
- Nhập từ JSON/ICS và xuất ra JSON/ICS.

## Kiến trúc & luồng xử lý

- Giao diện: `main.py`
    - Ô nhập lệnh → gọi `NLPPipeline.process(text)` → kết quả (event, start_time, location, reminder_minutes) → lưu DB → refresh UI.
    - Lịch (`tkcalendar.Calendar`) chọn ngày → truy vấn DB theo ngày → hiển thị `Treeview`.
    - Chỉnh sửa inline: nạp dữ liệu từ DB, cập nhật và refresh.
    - Import/Export: gọi các hàm trong `services/`.
    - Nhắc nhở: khởi động luồng nền kiểm tra định kỳ (60s) để hiển thị pop-up và cập nhật trạng thái.

- NLP: `core_nlp/pipeline.py`
    - Kết hợp NER địa điểm của `underthesea` (nếu có) với regex.
    - Tách cụm thời gian (giờ:phút, “10h”, “ngày 6 tháng 12”, “hôm nay/mai/ngày mốt…”, “thứ d [tuần sau]”, “UTC+7/múi giờ +07:00”, “trong/sau X”, “X nữa”, sáng/chiều/tối…).
    - Chuẩn hóa phần văn bản còn lại làm tên sự kiện; trích phút nhắc nhở.
    - Gọi `parse_vietnamese_time` để chuyển `time_str` → `datetime` ISO.

- Phân tích thời gian: `core_nlp/time_parser.py`
    - Quy tắc thủ công cho ngày/giờ tường minh và tương đối; mặc định giờ nếu thiếu (ví dụ 09:00 hoặc theo buổi).
    - Timezone chỉ áp dụng khi người dùng nêu rõ (UTC/GMT hoặc “múi giờ +..”).

- CSDL: `database/db_manager.py` + `database/schema.sql`
    - SQLite lưu `events(id, event_name, start_time, end_time, location, reminder_minutes, status)`.
    - CRUD, lấy theo ngày, lấy nhắc nhở “pending” và cập nhật trạng thái `notified` sau khi hiển thị.

- Dịch vụ: `services/`
    - `import_service.py`: đọc JSON/ICS và ghi vào DB.
    - `export_service.py`: xuất toàn bộ DB ra JSON/ICS.
    - `notification_service.py`: luồng kiểm tra nhắc nhở và popup.

- Kiểm thử: `tests/`
    - `tests/test_cases.json`: bộ dữ liệu kỳ vọng.
    - `tests/test_nlp_pipeline.py`: unittest tính macro-F1 cho 4 nhánh (event, time, location, reminder).

## Cấu trúc thư mục và tệp chính

```
.
├── main.py                     # Tkinter GUI, nhập NLP, lịch, chỉnh sửa, import/export, nhắc nhở
├── core_nlp/
│   ├── pipeline.py             # NLPPipeline: NER (underthesea) + regex trích event/time/location/reminder
│   └── time_parser.py          # parse_vietnamese_time: quy tắc thời gian tiếng Việt
├── database/
│   ├── db_manager.py           # SQLite CRUD và các truy vấn tiện ích
│   └── schema.sql              # DDL tạo bảng events
├── services/
│   ├── import_service.py       # Import JSON/ICS → DB
│   ├── export_service.py       # Export DB → JSON/ICS
│   └── notification_service.py # Luồng nền kiểm tra và popup nhắc nhở
├── tests/
│   ├── test_nlp_pipeline.py    # unittest tính macro-F1
│   └── test_cases.json         # dữ liệu kiểm thử
├── requirements.txt
└── README.md
```

## Yêu cầu hệ thống

- Python 3.9+ (đã kiểm thử trên Windows)
- Tkinter (đi kèm CPython chuẩn trên Windows)
- Thư viện trong `requirements.txt`: underthesea, tkcalendar, ics, babel, (dateparser hiện không dùng trong mã, có thể giữ lại nếu muốn thử nghiệm)

## Cài đặt và chạy (Windows PowerShell)

1) Tạo môi trường ảo và kích hoạt

```powershell
python -m venv venv
.\n+venv\Scripts\Activate.ps1  # thông thường trên Windows
# Nếu venv của bạn có cấu trúc dạng bin/ (như repo này), dùng:
# .\venv\bin\Activate.ps1
```

2) Cài đặt phụ thuộc

```powershell
pip install -r requirements.txt
```

3) Chạy ứng dụng

```powershell
python main.py
# hoặc (nếu dùng interpreter trong venv/bin)
# .\venv\bin\python.exe main.py
```

Mẹo dùng nhanh:
- Nhập: “Họp nhóm lúc 10h sáng mai ở phòng 302, nhắc trước 15 phút” → bấm “Thêm sự kiện”.
- Chọn ngày trên lịch để xem danh sách. Chọn một dòng → “Sửa” để chỉnh nhanh.
- “Xuất JSON/ICS” và “Nhập JSON/ICS” ở thanh nút dưới cùng.

## Kiểm thử (F1 macro)

Chạy unittest đo macro-F1 cho pipeline NLP:

```powershell
python -m unittest tests\test_nlp_pipeline.py -v
```

Ví dụ kết quả gần đây: macro-F1 ≈ 0.967 (tùy môi trường/thư viện).

## Cơ sở dữ liệu (SQLite)

- File DB: `database/events.db` tự tạo nếu chưa có.
- Bảng `events` (xem `database/schema.sql`):
    - `id` (PK), `event_name` (TEXT, NOT NULL), `start_time` (TEXT ISO 8601, NOT NULL), `end_time` (TEXT, NULL), `location` (TEXT), `reminder_minutes` (INTEGER, default 0), `status` (TEXT, default 'pending').
- Reset DB (xóa dữ liệu): xoá file `database/events.db` khi ứng dụng đang tắt.

## Nhập/Xuất JSON & ICS

- Xuất mặc định ra gốc dự án: `schedule_export.json`, `schedule_export.ics`.
- Nhập từ tệp do bạn chọn qua hộp thoại.
- **Nhập JSON hỗ trợ 2 định dạng**:
    1. **Export format** (truyền thống): `{"event_name": "...", "start_time": "2025-11-10T18:00:00", ...}`
    2. **Test case format** (MỚI): `{"input": "Họp nhóm 10h mai...", "expected": {...}}` - tự động parse qua NLP
- Mapping chính:
    - JSON export: `event_name`/`event` → `event_name`, `start_time` ISO bắt buộc, `location`, `reminder_minutes`.
    - JSON test case: `input` → parse qua NLP → event + start_time + location + reminder.
    - ICS: đọc `name`, `begin` (tự động chuyển `datetime`/Arrow → ISO), `location`.
- **Lưu ý**: Có thể nhập file test từ `./tests/` (như `test_cases.json`, `extended_test_cases_10000.json`).

## Đóng gói (.exe) bằng PyInstaller

`underthesea` sử dụng mô hình ngoài thư mục người dùng (`~/.underthesea`), cần add-data và đã có hack `_MEIPASS` trong `main.py` để định tuyến `Path.home()` khi chạy bản đóng gói.

```powershell
pyinstaller --onefile --windowed --name "TrinhLyAo" \
    --add-data "C:\Users\<TEN_USER>\.underthesea;.underthesea" \
    --hidden-import "babel.numbers" \
    main.py
```

Ghi chú:
- Sửa `<TEN_USER>` phù hợp máy build.
- `--hidden-import "babel.numbers"` giúp tkcalendar/babel không lỗi khi đóng gói.
- Bản .exe sẽ giải nén tạm và `Path.home()` đã được ghi đè để trỏ tới vùng tạm.

## Sự cố thường gặp (Troubleshooting)

- Lỗi `ModuleNotFoundError: No module named 'tkcalendar'`
    - Đảm bảo bạn đã kích hoạt đúng venv và chạy `pip install -r requirements.txt`.

- underthesea không tải được mô hình/không có NER
    - Ứng dụng vẫn chạy nhờ fallback, nhưng nhận diện địa điểm có thể kém chính xác hơn.
    - Khi đóng gói, nhớ `--add-data ~/.underthesea` như hướng dẫn.

- Vấn đề timezone trong ICS/hiển thị giờ
    - Parser chỉ gán timezone khi bạn nêu rõ (UTC/GMT hoặc “múi giờ +..”). Với dữ liệu không có tz, ứng dụng dùng datetime “naive”.

- Venv có thư mục `bin/` thay vì `Scripts/`
    - Sử dụng đường dẫn `venv/bin/python.exe` và `venv/bin/Activate.ps1` thay thế như ví dụ.

---

Nếu bạn muốn mở rộng: thêm index DB cho `start_time`/`status`, mở rộng mẫu thời gian (ví dụ “tuần tới”, “đầu tuần”, “cuối tháng”), thêm bộ lint/type check (ruff/mypy), hoặc cải thiện UX xuất/nhập với hộp thoại lưu.

