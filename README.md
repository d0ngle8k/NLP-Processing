# 📅 Trợ Lý Lịch Trình - Vietnamese NLP Calendar Assistant



> **Version:** 1.0.2  

> **Status:** Production Ready ✅  

> **Download:** https://open-source-schedule-7tta.bolt.host/



# 📅 Trợ Lý Lịch Trình (Vietnamese NLP Calendar Assistant)

![Version](https://img.shields.io/badge/version-0.8.1-blue.svg) ![Python](https://img.shields.io/badge/python-3.9%2B-green.svg) ![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)

Ứng dụng giúp tạo & quản lý lịch hẹn bằng tiếng Việt tự nhiên. Bạn nhập câu giống như trò chuyện: hệ thống tự động trích xuất sự kiện, thời gian, địa điểm, nhắc nhở. Kết hợp mô hình **Hybrid NLP** (Rule-based 100% + PhoBERT fine-tuned ≥95%).

---
## ✨ Tính năng chính

- 🔍 Nhận dạng thời gian phức tạp: "6h chiều mai", "thứ 7 tuần sau 7h tối", "trong 2 ngày nữa".
- 🗓️ Hỗ trợ nhiều định dạng ngày: `DD/MM`, `DD/MM/YYYY`, "ngày X tháng Y", tên thứ + số.
- 🧠 Hybrid NLP: So sánh kết quả Rule-based & PhoBERT, tính điểm agreement.
- 📍 Trích xuất địa điểm từ câu (NER + regex).
- 🔔 Nhắc nhở linh hoạt: phút / giờ / ngày ("nhắc trước 2 tiếng", "15 phút").
- 📤 Export: Google Calendar / Outlook / Apple (ICS + JSON).
- 📥 Import: Đọc file export & test case format.
- 📊 Dashboard thống kê: phân bố thời gian, xu hướng 4 tuần, top địa điểm.
- 🛡️ Bảo vệ dữ liệu: xác nhận 2 lớp khi xóa toàn bộ.
- 🎛️ Settings riêng + chế độ im lặng (tắt debug với `VERBOSE_LOG=False`).

---
## 🧱 Kiến trúc tổng quan

```
┌─────────────────────────────────────────┐
│            Hybrid NLP Pipeline          │
├─────────────────────────────────────────┤
│  Rule-based Parser  │  PhoBERT Fine-tuned │
│  100% edge cases    │  Contextual          │
└──────────┬──────────┴──────────┬─────────┘
                ▼                     ▼
            Voting / Merge Engine  (Agreement Score)
                              ▼
                  Chuẩn hoá kết quả cuối
```

Thành phần chính:
- `core_nlp/pipeline.py`: Rule-based phân tích thời gian / ngày.
- `core_nlp/hybrid_pipeline.py`: Kết hợp PhoBERT + Rule-based.
- `database/db_manager.py`: SQLite + schema + kết nối.
- `services/*`: Export/Import/Notification/Statistics.
- `widgets/`: Thành phần giao diện CustomTkinter.

---
## 📦 Cài đặt

### Yêu cầu
- Python 3.9+ (khuyên dùng 3.12)
- Windows 10+ 64-bit
- RAM 2GB+, Disk trống ≥1GB (bundle exe lớn do model + PyTorch)

### Clone & môi trường
```powershell
git clone https://github.com/d0ngle8k/NLP-Processing.git
cd NLP-Processing
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---
## 🚀 Chạy ứng dụng

### GUI (CustomTkinter)
```powershell
python main_ctk.py
```

### CLI thử nghiệm (Hybrid Debug)
```powershell
python version_document/interactive_test_hybrid.py
```

### Tắt / bật debug
Trong `main_ctk.py` đổi:
```python
VERBOSE_LOG = False  # True để xem log chi tiết
```

---
## 🛠 Build file EXE (PyInstaller)

Sử dụng spec tối ưu: `build_main_ctk.spec` (đã loại bỏ thư mục rỗng, thêm hidden imports). 

```powershell
.\.venv\Scripts\python.exe -m PyInstaller --clean build_main_ctk.spec
```
Kết quả: `dist/TroLyLichTrinhV2.exe`

Nếu lỗi Permission Denied khi update checksum: đóng mọi phiên bản đang chạy rồi build lại.

---
## 🧪 Kiểm thử

| Suite | Số test | Trạng thái |
|-------|---------|------------|
| NLP Pipeline | 42 | ✅ |
| Hybrid Voting | 10 | ✅ |
| New Patterns | 8 | ✅ |
| Extended Edge Cases | 1065 | ✅ |

Chạy nhanh:
```powershell
python tests/test_nlp_pipeline.py
python tests/run_extended_tests.py
```

---
## 📂 Cấu trúc dự án (rút gọn)
```
NLP-Processing/
├── main_ctk.py                # Entry GUI
├── build_main_ctk.spec        # PyInstaller spec chuẩn
├── core_nlp/                  # NLP logic & hybrid
├── services/                  # Export / Import / Notification / Stats
├── widgets/                   # CustomTkinter components
├── database/                  # SQLite schema & manager
├── models/                    # PhoBERT (fine-tuned)
├── training_data/             # Dữ liệu huấn luyện/validation
├── tests/                     # Bộ test tự động
└── version_document/          # Tài liệu archive (changelog, design, guides)
```

---
## 📥📤 Import / Export
- JSON: Backup & restore sự kiện.
- ICS: Đồng bộ Google / Outlook / Apple.
- Export báo cáo: scripts/generate_report.py (PDF/Excel).

---
## 🔔 Nhắc nhở
- Thread nền kiểm tra mỗi 60s (`notification_service.py`).
- Tránh spam: đánh dấu đã thông báo.
- Hỗ trợ trước X phút/giờ/ngày.

---
## 🧠 NLP Highlights
- Xử lý lỗi gõ phổ biến: "támh", "mườih".
- Chuẩn hoá buổi: sáng / chiều / tối / trưa.
- Tương đối: "trong 2 ngày", "tuần sau", "tháng sau".
- Múi giờ: hỗ trợ chuẩn hoá + nội suy nếu thiếu năm.

---
## 🛡️ Bảo trì & đóng góp
Pull Request được chào đón. Vui lòng kèm test cho logic NLP mới.

---
## 📝 Tài liệu mở rộng
Xem thư mục `version_document/` (được ignore trong Git để giảm noise) chứa: 
- Changelog & Hotfix (`V0.*.md`)
- UI redesign (`BA_GOOGLE_CALENDAR_UI_REDESIGN.md`)
- Training guides (Colab, GPU)
- Sound system & Theme updates

---
## ⚠️ Troubleshooting
| Vấn đề | Nguyên nhân | Cách xử lý |
|--------|-------------|------------|
| PhoBERT load chậm | Kích thước model | Kiên nhẫn (~vài giây) / preload |
| EXE >900MB | PyTorch + model | Dùng zip phân phối / build lại khi tối ưu |
| Lỗi checksum khi build | File exe đang mở | Tắt ứng dụng rồi build lại |
| Không hiện âm thanh | Thiếu preset | Tạo file .wav trong `sounds/` |

---
## 📄 License
Chưa khai báo – bổ sung sau (MIT khuyến nghị).

---
## ✅ Trạng thái hiện tại
- Production GUI ✅
- Silent startup ✅
- EXE build verified ✅
- NLP >1000 edge cases ✅

---
*README được viết lại gọn gàng từ bản cũ bị trộn nội dung. Nếu cần thêm English section, thông báo để bổ sung.*
```



## 🔧 Configuration

#### 3. Sửa Sự Kiện- [Troubleshooting](#-troubleshooting)

### Model Selection

- Double-click vào sự kiện trong danh sách

Edit `main.py` to change model:

- Chỉnh sửa thông tin trong form- [Changelog](#-changelog)- Phân tích thời gian: `core_nlp/time_parser.py`

```python

# Option 1: Hybrid (Recommended)- Bấm **"Sửa"** để lưu

from core_nlp.hybrid_pipeline import HybridNLPPipeline

nlp = HybridNLPPipeline()- [License](#-license)    - Quy tắc thủ công cho ngày/giờ tường minh và tương đối; mặc định giờ nếu thiếu (ví dụ 09:00 hoặc theo buổi).



# Option 2: Rule-based only (Faster, 100% accurate)#### 4. Xóa Sự Kiện

from core_nlp.pipeline import NLPPipeline

nlp = NLPPipeline()- Chọn sự kiện → Bấm **"Xóa"** (xóa 1 sự kiện)    - Timezone chỉ áp dụng khi người dùng nêu rõ (UTC/GMT hoặc “múi giờ +..”).



# Option 3: PhoBERT only (Experimental)- Hoặc bấm **"Xóa tất cả"** → Xác nhận 2 lần

from core_nlp.phobert_model import PhoBERTModel

nlp = PhoBERTModel(model_path='./models/phobert_finetuned')---

```

#### 5. Import/Export

## 📝 Pattern Support

- Bấm **"⚙️ Cài đặt"** (góc dưới bên trái)- CSDL: `database/db_manager.py` + `database/schema.sql`

### Thời gian (Time)

- ✅ "6h sáng", "3h chiều", "9h tối"- **Xuất JSON/ICS**: Lưu toàn bộ dữ liệu

- ✅ "6:30", "15:45"

- ✅ "6 rưỡi", "7h30"- **Nhập JSON/ICS**: Khôi phục hoặc import từ nguồn khác## 💻 Yêu Cầu Hệ Thống    - SQLite lưu `events(id, event_name, start_time, end_time, location, reminder_minutes, status)`.



### Ngày (Date)

- ✅ "hôm nay", "ngày mai", "ngày kia"

- ✅ "thứ 2", "thứ ba", "chủ nhật"---    - CRUD, lấy theo ngày, lấy nhắc nhở “pending” và cập nhật trạng thái `notified` sau khi hiển thị.

- ✅ "tuần sau", "tháng sau"

- ✅ "ngày 20 tháng 10"

- ✅ **NEW:** "20/10", "25/12", "1/1/2026"

- ✅ **NEW:** "ngày 20/10"## 🏗️ Kiến Trúc Hệ Thống### Minimum Requirements



### Nhắc nhở (Reminder)

- ✅ "nhắc trước 30 phút"

- ✅ "nhắc trước 2 giờ"### Cấu Trúc Thư Mục- **OS**: Windows 10+ (64-bit)- Dịch vụ: `services/`

- ✅ **NEW:** "nhắc trước 2 tieng"

- ✅ **NEW:** "nhắc trước 1 tiếng"```



### Khoảng thời gian (Duration)NLP-Processing/- **Python**: 3.9+ (recommended: 3.12.0)    - `import_service.py`: đọc JSON/ICS và ghi vào DB.

- ✅ "từ 2h đến 4h"

- ✅ "2h-4h"├── main.py                      # GUI chính (Tkinter)

- ✅ "khoảng 2 tiếng"

├── requirements.txt             # Python dependencies- **RAM**: 4GB+    - `export_service.py`: xuất toàn bộ DB ra JSON/ICS.

## 🆕 What's New in V0.6.2

├── README.md                    # Tài liệu này

### Bug Fixes

1. **Reminder Hours Support** - Thêm hỗ trợ "tieng/tiếng" cho reminder├── CHANGELOG.md                 # Lịch sử phiên bản- **Disk**: 500MB free space    - `notification_service.py`: luồng kiểm tra nhắc nhở và popup.

   - Before: "nhắc trước 2 tieng" → 0 mins ❌

   - After: "nhắc trước 2 tieng" → 120 mins ✅│



2. **DD/MM Date Format** - Hỗ trợ định dạng ngày DD/MM├── core_nlp/                    # Module xử lý NLP

   - Before: "ngày 20/10" → None ❌

   - After: "ngày 20/10" → 2025-10-20 ✅│   ├── pipeline.py              # Pipeline chính (NER + Time + Location)



### Files Changed│   └── time_parser.py           # Parser thời gian tiếng Việt### Dependencies- Kiểm thử: `tests/`

- `core_nlp/pipeline.py` - Added "tieng|tiếng" to reminder patterns

- `core_nlp/time_parser.py` - Fixed DD/MM parsing with "ngày" prefix│



### Test Results├── database/                    # Lớp database```plaintext    - `tests/test_cases.json`: bộ dữ liệu kỳ vọng.

- ✅ All 1065 extended tests passed

- ✅ 8/8 new pattern tests passed│   ├── db_manager.py            # SQLite CRUD operations

- ✅ No regressions detected

│   ├── schema.sql               # Database schema# Core NLP    - `tests/test_nlp_pipeline.py`: unittest tính macro-F1 cho 4 nhánh (event, time, location, reminder).

## 📊 Performance

│   └── events.db                # SQLite database (auto-created)

| Metric | Value |

|--------|-------|│underthesea>=6.7.0        # Vietnamese NLP (NER, word segmentation)

| Accuracy (Rule-based) | 100% |

| Accuracy (PhoBERT) | 95% |├── services/                    # Business logic services

| Accuracy (Hybrid) | ~100% |

| Avg Processing Time | <100ms |│   ├── import_service.py        # Import JSON/ICS → DBpython-dateutil>=2.8.2    # Date parsing utilities## Cấu trúc thư mục và tệp chính

| Agreement Score | 84.3% avg |

│   ├── export_service.py        # Export DB → JSON/ICS

## 🐛 Known Issues

│   └── notification_service.py  # Background reminder thread

- Event extraction may fail with very complex multi-pattern inputs

- PhoBERT model requires ~500MB RAM│

- First run loads PhoBERT model (~3s startup time)

├── scripts/                     # Utility scripts# GUI Components```

## 🤝 Contributing

│   ├── generate_edge_case_tests.py  # Tạo test cases

### Development Setup

│   └── generate_report.py           # Tạo báo cáotkcalendar>=1.6.1         # Calendar widget.

```bash

# Install dev dependencies│

pip install -r requirements.txt

└── tests/                       # Testing suitetkinter                    # Standard library (included with Python)├── main.py                     # Tkinter GUI, nhập NLP, lịch, chỉnh sửa, import/export, nhắc nhở

# Run tests before commit

python tests/run_extended_tests.py    ├── test_nlp_pipeline.py     # Unit tests

python tests/test_hybrid_pipeline.py

```    ├── run_edge_case_tests.py   # Edge case test runner├── core_nlp/



### Adding New Patterns    ├── test_cases.json          # Test dataset



1. Update regex patterns in `core_nlp/pipeline.py`    └── edge_case_tests_1000.json  # 1050 edge cases# Data Processing│   ├── pipeline.py             # NLPPipeline: NER (underthesea) + regex trích event/time/location/reminder

2. Update parsing logic in `core_nlp/time_parser.py`

3. Add test cases in `tests/test_cases.json````

4. Run full test suite

5. Update documentationbabel>=2.13.1             # Locale and timezone support│   └── time_parser.py          # parse_vietnamese_time: quy tắc thời gian tiếng Việt



## 📄 License### Luồng Xử Lý NLP



This project is licensed under the MIT License.├── database/



## 👨‍💻 Author```



**d0ngle8k**Input: "thứ 3 mười giờ tôi có lịch phỏng vấn ở tầng 5, nhắc trước 30 phút"# Import/Export│   ├── db_manager.py           # SQLite CRUD và các truy vấn tiện ích

- Repository: [NLP-Processing](https://github.com/d0ngle8k/NLP-Processing)

   │

## 🙏 Acknowledgments

   ▼ics>=0.7.2                # iCalendar format support│   └── schema.sql              # DDL tạo bảng events

- **PhoBERT** - Pre-trained Vietnamese BERT model

- **VNCoreNLP** - Vietnamese NLP toolkit┌─────────────────────────────────────────┐

- Test data contributors

│ 1. Normalize & Extract Time Patterns   │├── services/

---

│    → "thứ 3 mười giờ"                  │

**Made with ❤️ for Vietnamese NLP**

└─────────────────────────────────────────┘# Statistics & Reporting (v0.6+)│   ├── import_service.py       # Import JSON/ICS → DB

   │

   ▼matplotlib>=3.8.0         # Charts and visualizations│   ├── export_service.py       # Export DB → JSON/ICS

┌─────────────────────────────────────────┐

│ 2. Parse Vietnamese Time                │reportlab>=4.0.7          # PDF report generation│   └── notification_service.py # Luồng nền kiểm tra và popup nhắc nhở

│    → datetime: 2025-11-11T10:00:00     │

└─────────────────────────────────────────┘openpyxl>=3.1.2          # Excel file generation├── tests/

   │

   ▼scikit-learn>=1.3.0      # Machine learning utilities│   ├── test_nlp_pipeline.py    # unittest tính macro-F1

┌─────────────────────────────────────────┐

│ 3. Extract Location (NER + Regex)      │```│   └── test_cases.json         # dữ liệu kiểm thử

│    → "tầng 5"                           │

└─────────────────────────────────────────┘├── requirements.txt

   │

   ▼---└── README.md

┌─────────────────────────────────────────┐

│ 4. Extract Reminder                     │```

│    → reminder_minutes: 30               │

└─────────────────────────────────────────┘## 🚀 Cài Đặt Nhanh

   │

   ▼## Yêu cầu hệ thống

┌─────────────────────────────────────────┐

│ 5. Extract Event Name (Remaining Text) │### 1. Clone Repository

│    → "phỏng vấn"                        │

└─────────────────────────────────────────┘```powershell- Python 3.9+ (đã kiểm thử trên Windows)

   │

   ▼git clone https://github.com/d0ngle8k/NLP-Processing.git- Tkinter (đi kèm CPython chuẩn trên Windows)

Result: {

  "event": "phỏng vấn",cd NLP-Processing- Thư viện trong `requirements.txt`: underthesea, tkcalendar, ics, babel, (dateparser hiện không dùng trong mã, có thể giữ lại nếu muốn thử nghiệm)

  "start_time": "2025-11-11T10:00:00",

  "location": "tầng 5",```

  "reminder_minutes": 30

}## Cài đặt và chạy (Windows PowerShell)

```

### 2. Tạo Virtual Environment

### Database Schema

```powershell1) Tạo môi trường ảo và kích hoạt

```sql

CREATE TABLE IF NOT EXISTS events (python -m venv venv

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    event_name TEXT NOT NULL,.\venv\Scripts\Activate.ps1```powershell

    start_time TEXT NOT NULL,      -- ISO 8601 format

    end_time TEXT,                  -- ISO 8601 (optional)```python -m venv venv

    location TEXT,

    reminder_minutes INTEGER DEFAULT 0,.\n+venv\Scripts\Activate.ps1  # thông thường trên Windows

    status TEXT DEFAULT 'pending'   -- 'pending' or 'notified'

);### 3. Cài Đặt Dependencies# Nếu venv của bạn có cấu trúc dạng bin/ (như repo này), dùng:

```

```powershell# .\venv\bin\Activate.ps1

---

pip install -r requirements.txt```

## 🧪 Kiểm Thử

```

### Edge Case Testing

2) Cài đặt phụ thuộc

Ứng dụng đã được kiểm thử với **1050 edge cases** bao gồm:

### 4. Chạy Ứng Dụng

- ✅ **weekday_time** (100 cases): "t5 támh", "thứ 2 bah", "chu nhat mườih" - **100% pass**

- ✅ **date_format** (100 cases): "20.10", "15/12", "ngày 6 tháng 11" - **100% pass**```powershell```powershell

- ✅ **period_marker** (100 cases): "sáng", "chiều", "tối", "đêm" - **100% pass**

- ✅ **typo_no_diacritics** (50 cases): "hom nay", "ngay mai", "toi" - **100% pass**python main.pypip install -r requirements.txt

- ✅ **duration** (25 cases): "trong 2 ngày", "sau 3 giờ" - **100% pass**

- ✅ **next_week** (50 cases): "tuần sau", "thứ 2 tuần sau" - **100% pass**``````

- ✅ **today_explicit** (25 cases): "hôm nay 10h" - **100% pass**



**Tổng kết**: **96.6%** pass rate (1014/1050)

### 5. (Optional) Build EXE3) Chạy ứng dụng

### Chạy Tests

```powershell

```powershell

# Tạo edge case testspython -m PyInstaller TroLyLichTrinh0.6.1.spec --clean --noconfirm```powershell

python scripts\generate_edge_case_tests.py

```python main.py

# Chạy edge case tests

python tests\run_edge_case_tests.pyFile EXE sẽ có tại: `dist\TroLyLichTrinh0.6.1.exe` (111.91 MB)# hoặc (nếu dùng interpreter trong venv/bin)



# Kết quả# .\venv\bin\python.exe main.py

# Total Tests: 1050

# ✅ Passed: 1014 (96.6%)---```

# ❌ Failed: 36 (3.4%)

```



### Test Cases Đặc Biệt## 📖 Sử DụngMẹo dùng nhanh:



```python- Nhập: “Họp nhóm lúc 10h sáng mai ở phòng 302, nhắc trước 15 phút” → bấm “Thêm sự kiện”.

# Compact weekday format với typos

"t5 támh phỏng vấn"           → Thứ 5, 8:00, "phỏng vấn"### Thêm Sự Kiện- Chọn ngày trên lịch để xem danh sách. Chọn một dòng → “Sửa” để chỉnh nhanh.

"t2 bah họp"                  → Thứ 2, 3:00, "họp"

"chu nhat mườih đi chơi"      → Chủ nhật, 10:00, "đi chơi"Nhập câu lệnh tự nhiên vào ô text, ví dụ:- “Xuất JSON/ICS” và “Nhập JSON/ICS” ở thanh nút dưới cùng.



# Date formats```

"họp 20.10"                   → 20/10/2025, "họp"

"khám bệnh 15/12"             → 15/12/2025, "khám bệnh"Họp nhóm lúc 10h sáng mai ở phòng 302, nhắc trước 15 phút## Kiểm thử (F1 macro)



# Period markers  ```

"6h chiều họp"                → 18:00 (không phải 6:00)

"10h tối"                     → 22:00Bấm **"Thêm sự kiện"** → Hệ thống tự động:Chạy unittest đo macro-F1 cho pipeline NLP:



# Relative dates- Trích xuất tên sự kiện: "Họp nhóm"

"tuần sau thứ 3"              → Thứ 3 tuần sau

"tháng sau ngày 15"           → Ngày 15 tháng sau- Parse thời gian: 10:00 AM ngày mai```powershell

```

- Địa điểm: "phòng 302"python -m unittest tests\test_nlp_pipeline.py -v

---

- Nhắc nhở: 15 phút trước```

## 📦 Dependencies



### Core Libraries

```### Xem & Sửa Sự KiệnVí dụ kết quả gần đây: macro-F1 ≈ 0.967 (tùy môi trường/thư viện).

underthesea>=6.7.0          # Vietnamese NLP (NER)

python-dateutil>=2.8.2      # Date parsing1. Click vào ngày trên **Calendar**

tkcalendar>=1.6.1           # Calendar widget

babel>=2.13.1               # Timezone support2. Danh sách sự kiện hiển thị bên dưới## Cơ sở dữ liệu (SQLite)

ics>=0.7.2                  # iCalendar format

```3. Double-click vào sự kiện → Chỉnh sửa inline



### Optional (Statistics - chưa dùng)4. Bấm **"Sửa"** để lưu thay đổi- File DB: `database/events.db` tự tạo nếu chưa có.

```

matplotlib>=3.8.0           # Charts- Bảng `events` (xem `database/schema.sql`):

reportlab>=4.0.7            # PDF reports

openpyxl>=3.1.2            # Excel export### Xóa Sự Kiện    - `id` (PK), `event_name` (TEXT, NOT NULL), `start_time` (TEXT ISO 8601, NOT NULL), `end_time` (TEXT, NULL), `location` (TEXT), `reminder_minutes` (INTEGER, default 0), `status` (TEXT, default 'pending').

```

- **Xóa 1 sự kiện**: Chọn sự kiện → Bấm **"Xóa"**- Reset DB (xóa dữ liệu): xoá file `database/events.db` khi ứng dụng đang tắt.

---

- **Xóa tất cả**: Bấm **"Xóa tất cả"** → Xác nhận 2 lần

## 🔧 Troubleshooting

## Nhập/Xuất JSON & ICS

### Lỗi Thường Gặp

### Xem Thống Kê

#### 1. `ModuleNotFoundError: No module named 'tkcalendar'`

```powershell1. Bấm **"📊 Xem thống kê"**- Xuất mặc định ra gốc dự án: `schedule_export.json`, `schedule_export.ics`.

# Kích hoạt venv và cài đặt lại

.\venv\Scripts\Activate.ps12. Chọn tab phân tích:- Nhập từ tệp do bạn chọn qua hộp thoại.

pip install -r requirements.txt

```   - 📊 Tổng quan- **Nhập JSON hỗ trợ 2 định dạng**:



#### 2. Database không tạo được   - ⏰ Thời gian    1. **Export format** (truyền thống): `{"event_name": "...", "start_time": "2025-11-10T18:00:00", ...}`

```powershell

# Kiểm tra quyền ghi trong thư mục database/   - 📍 Địa điểm    2. **Test case format** (MỚI): `{"input": "Họp nhóm 10h mai...", "expected": {...}}` - tự động parse qua NLP

# Xóa file events.db cũ nếu bị corrupt

Remove-Item database\events.db -Force   - 🏷️ Phân loại- Mapping chính:

python main.py  # Sẽ tạo lại tự động

```   - 📉 Xu hướng    - JSON export: `event_name`/`event` → `event_name`, `start_time` ISO bắt buộc, `location`, `reminder_minutes`.



#### 3. Underthesea NER không hoạt động3. Bấm **"📄 Xuất PDF"** hoặc **"📊 Xuất Excel"**    - JSON test case: `input` → parse qua NLP → event + start_time + location + reminder.

```

⚠️ WARNING: underthesea NER failed, using fallback regex    - ICS: đọc `name`, `begin` (tự động chuyển `datetime`/Arrow → ISO), `location`.

```

→ Không ảnh hưởng chức năng, app vẫn chạy với regex location detection### Import/Export- **Lưu ý**: Có thể nhập file test từ `./tests/` (như `test_cases.json`, `extended_test_cases_10000.json`).



#### 4. Venv có cấu trúc `bin/` thay vì `Scripts/`- **Export JSON**: Bấm **"Xuất JSON"** → `schedule_export.json`

```powershell

# Sử dụng đường dẫn bin/- **Export ICS**: Bấm **"Xuất ICS"** → `schedule_export.ics` (Google Calendar compatible)## Đóng gói (.exe) bằng PyInstaller

.\venv\bin\Activate.ps1

.\venv\bin\python.exe main.py- **Import**: Bấm **"Nhập JSON/ICS"** → Chọn file

```

`underthesea` sử dụng mô hình ngoài thư mục người dùng (`~/.underthesea`), cần add-data và đã có hack `_MEIPASS` trong `main.py` để định tuyến `Path.home()` khi chạy bản đóng gói.

---

---

## 📝 Changelog

```powershell

### Version 0.8.1 (2025-11-06) - Current

**Edge Case Improvements:**## 🏗️ Kiến Trúc & Luồng Xử Lýpyinstaller --onefile --windowed --name "TrinhLyAo" \

- ✅ Fixed compact weekday format: "t5 támh", "t2 bah", "t7 sáuh"

- ✅ Added word boundaries to prevent partial matches    --add-data "C:\Users\<TEN_USER>\.underthesea;.underthesea" \

- ✅ Enhanced pipeline patterns for number words with diacritics

- ✅ Fixed "chu nhat" (chủ nhật) parsing### Architecture Overview    --hidden-import "babel.numbers" \

- 📊 Edge case pass rate: **96.6%** (1014/1050)

```    main.py

**Improvements:**

- ✨ Added Settings window (⚙️ button)┌─────────────────────────────────────────────────────────────┐```

- 🎨 Reorganized Import/Export to Settings

- 📦 Added app info section│                        main.py (GUI)                         │

- 🧹 Code cleanup and optimization

│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │Ghi chú:

### Version 0.7.0 (2025-11-05)

**Major Fixes:**│  │ Input Field  │  │   Calendar   │  │  Statistics  │      │- Sửa `<TEN_USER>` phù hợp máy build.

- ✅ Fixed "thứ 3 mười giờ" parsing (weekday + number words)

- ✅ Fixed "tôi" vs "tối" ambiguity│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │- `--hidden-import "babel.numbers"` giúp tkcalendar/babel không lỗi khi đóng gói.

- ✅ Fixed "hôm nay" parsing (0% → 100%)

- ✅ Fixed "tuần sau" parsing (64% → 100%)└─────────┼──────────────────┼──────────────────┼─────────────┘- Bản .exe sẽ giải nén tạm và `Path.home()` đã được ghi đè để trỏ tới vùng tạm.

- ✅ Fixed duration expressions (64% → 100%)

- 📊 Generated 1050 edge case tests          │                  │                  │



### Version 0.6.1 (2025-11-04)          ▼                  ▼                  ▼## Sự cố thường gặp (Troubleshooting)

**Critical Fixes:**

- ✅ Fixed date format parsing: "20.10", "15/12", "6-11"┌─────────────────────────────────────────────────────────────┐

- ✅ Fixed "6h chiều" parsed as 06:00 (now correctly 18:00)

- ✅ Enhanced period detection logic│                     Core Components                          │- Lỗi `ModuleNotFoundError: No module named 'tkcalendar'`



### Version 0.6.0 (2025-11-03)│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │    - Đảm bảo bạn đã kích hoạt đúng venv và chạy `pip install -r requirements.txt`.

**Initial Release:**

- ✨ Basic NLP pipeline for Vietnamese│  │ NLP Pipeline │  │  DB Manager  │  │  Statistics  │      │

- 📅 Calendar UI with tkcalendar

- 🔔 Reminder notifications│  │ (core_nlp)   │  │  (database)  │  │  Service     │      │- underthesea không tải được mô hình/không có NER

- 📥📤 JSON/ICS import/export

│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │    - Ứng dụng vẫn chạy nhờ fallback, nhưng nhận diện địa điểm có thể kém chính xác hơn.

---

└─────────┼──────────────────┼──────────────────┼─────────────┘    - Khi đóng gói, nhớ `--add-data ~/.underthesea` như hướng dẫn.

## 📄 License

          │                  │                  │

MIT License

          ▼                  ▼                  ▼- Vấn đề timezone trong ICS/hiển thị giờ

Copyright (c) 2025 Trường Gia Thành (d0ngle8k)

┌─────────────────────────────────────────────────────────────┐    - Parser chỉ gán timezone khi bạn nêu rõ (UTC/GMT hoặc “múi giờ +..”). Với dữ liệu không có tz, ứng dụng dùng datetime “naive”.

---

│                      Data Layer                              │

## 👨‍💻 Tác Giả

│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │- Venv có thư mục `bin/` thay vì `Scripts/`

**Trường Gia Thành (d0ngle8k)**

- GitHub: [@d0ngle8k](https://github.com/d0ngle8k)│  │ Time Parser  │  │SQLite (events│  │ Export/Import│      │    - Sử dụng đường dẫn `venv/bin/python.exe` và `venv/bin/Activate.ps1` thay thế như ví dụ.

- Repository: [NLP-Processing](https://github.com/d0ngle8k/NLP-Processing)

│  │ (Vietnamese) │  │    table)    │  │   Services   │      │

---

│  └──────────────┘  └──────────────┘  └──────────────┘      │---

## 🙏 Cảm Ơn

└─────────────────────────────────────────────────────────────┘

- **underthesea**: Vietnamese NLP library

- **tkcalendar**: Calendar widget for Tkinter```Nếu bạn muốn mở rộng: thêm index DB cho `start_time`/`status`, mở rộng mẫu thời gian (ví dụ “tuần tới”, “đầu tuần”, “cuối tháng”), thêm bộ lint/type check (ruff/mypy), hoặc cải thiện UX xuất/nhập với hộp thoại lưu.

- **python-dateutil**: Powerful date parsing

- **ics**: iCalendar format support



---### NLP Pipeline Flow

```

## 📞 Hỗ TrợUser Input: "Họp nhóm lúc 10h sáng mai ở phòng 302, nhắc trước 15 phút"

     │

Nếu gặp vấn đề hoặc có câu hỏi:     ▼

1. Kiểm tra [Troubleshooting](#-troubleshooting)┌─────────────────────────────────────────────────────────────┐

2. Xem [CHANGELOG.md](CHANGELOG.md)│ 1. NER (underthesea) + Regex Location Extraction            │

3. Tạo issue trên GitHub│    → location = "phòng 302"                                 │

└─────────────────────────────────────────────────────────────┘

---     │

     ▼

<p align="center">┌─────────────────────────────────────────────────────────────┐

  <strong>🎯 Version 0.8.1 - Production Ready</strong>│ 2. Time Expression Detection & Extraction                   │

  <br>│    → time_str = "10h sáng mai"                              │

  Made with ❤️ by d0ngle8k│    → parse_vietnamese_time() → datetime                     │

</p>└─────────────────────────────────────────────────────────────┘

     │
     ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. Reminder Extraction (regex "nhắc [trước] X [phút/giờ]")  │
│    → reminder_minutes = 15                                  │
└─────────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. Event Name Normalization (remaining text)                │
│    → event_name = "Họp nhóm"                                │
└─────────────────────────────────────────────────────────────┘
     │
     ▼
  Result: {
    "event": "Họp nhóm",
    "start_time": "2025-11-06T10:00:00",
    "location": "phòng 302",
    "reminder_minutes": 15
  }
```

### Database Operations
```
┌─────────────────────────────────────────────────────────────┐
│                      db_manager.py                           │
├─────────────────────────────────────────────────────────────┤
│ CRUD Operations:                                             │
│  • create_event(name, start, end, location, reminder)       │
│  • get_events_by_date(date)                                 │
│  • update_event(id, name, start, end, location, reminder)   │
│  • delete_event(id)                                          │
│  • delete_all_events()                                       │
│                                                              │
│ Reminder Operations:                                         │
│  • get_pending_reminders(now)                               │
│  • mark_as_notified(event_ids)                              │
│                                                              │
│ Statistics Queries:                                          │
│  • get_all_events_for_stats()                               │
│  • get_events_count()                                        │
└─────────────────────────────────────────────────────────────┘
```

### Notification Service
```
Background Thread (checks every 60 seconds):
  1. Query pending reminders (status='pending')
  2. Check if event_time - reminder_minutes <= now
  3. Show popup notification (Tkinter Toplevel)
  4. Mark as notified (status='notified')
  5. Sleep 60 seconds, repeat
```

---

## 📁 Cấu Trúc Dự Án

```
NLP-Processing/
├── main.py                          # Entry point - Tkinter GUI
├── requirements.txt                 # Python dependencies
├── TroLyLichTrinh0.6.1.spec        # PyInstaller build config
├── README.md                        # This file
├── CHANGELOG.md                     # Version history
│
├── core_nlp/                        # NLP Processing Module
│   ├── pipeline.py                  # Main NLP pipeline (NER + Time + Location)
│   ├── time_parser.py               # Vietnamese time expression parser
│   └── __pycache__/
│
├── database/                        # Database Layer
│   ├── db_manager.py                # SQLite CRUD operations
│   ├── schema.sql                   # Database schema definition
│   ├── events.db                    # SQLite database file (auto-created)
│   └── __pycache__/
│
├── services/                        # Business Logic Services
│   ├── import_service.py            # Import JSON/ICS to database
│   ├── export_service.py            # Export database to JSON/ICS
│   ├── notification_service.py      # Background reminder notifications
│   ├── statistics_service.py        # Statistics analysis & reporting
│   └── __pycache__/
│
├── scripts/                         # Utility Scripts
│   └── generate_report.py           # Report generation utilities
│
├── tests/                           # Testing Suite
│   ├── test_nlp_pipeline.py         # Unit tests (macro-F1 calculation)
│   ├── test_cases.json              # Test dataset (baseline)
│   ├── extended_test_cases.json     # Extended tests (10K)
│   ├── extended_test_cases_10000.json    # 10,000 test cases
│   ├── extended_test_cases_100000.json   # 100,000 test cases
│   ├── generate_extended_tests.py   # Test case generator
│   ├── run_extended_tests.py        # Test runner
│   └── test_report.json             # Test results
│
├── build/                           # PyInstaller build artifacts
│   ├── TroLyLichTrinh0.6/
│   └── TroLyLichTrinh0.6.1/
│
└── dist/                            # Distribution folder
    ├── TroLyLichTrinh0.6.exe        # ❌ BROKEN (missing schema.sql)
    └── TroLyLichTrinh0.6.1.exe      # ✅ WORKING (111.91 MB)
```

### Key Files Explained

| File | Purpose | Lines of Code |
|------|---------|---------------|
| `main.py` | GUI application with Tkinter | ~800 |
| `core_nlp/pipeline.py` | NLP processing logic | ~300 |
| `core_nlp/time_parser.py` | Vietnamese time parsing | ~400 |
| `database/db_manager.py` | Database operations | ~200 |
| `services/statistics_service.py` | Statistics & reporting | ~650 |
| `services/notification_service.py` | Reminder notifications | ~100 |
| `services/import_service.py` | Import JSON/ICS | ~150 |
| `services/export_service.py` | Export JSON/ICS | ~100 |

---

## 🗄️ Database Schema

### Table: `events`

```sql
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_name TEXT NOT NULL,
    start_time TEXT NOT NULL,        -- ISO 8601 format
    end_time TEXT,                    -- ISO 8601 format (optional)
    location TEXT,
    reminder_minutes INTEGER DEFAULT 0,
    status TEXT DEFAULT 'pending'     -- 'pending' or 'notified'
);
```

### Indexes (Recommended)
```sql
CREATE INDEX idx_start_time ON events(start_time);
CREATE INDEX idx_status ON events(status);
```

### Sample Data
```json
{
  "id": 1,
  "event_name": "Họp nhóm",
  "start_time": "2025-11-06T10:00:00",
  "end_time": null,
  "location": "phòng 302",
  "reminder_minutes": 15,
  "status": "pending"
}
```

---

## 📥📤 Import/Export

### Export Formats

#### JSON Format
```json
[
  {
    "event_name": "Họp nhóm",
    "start_time": "2025-11-06T10:00:00",
    "end_time": null,
    "location": "phòng 302",
    "reminder_minutes": 15,
    "status": "pending"
  }
]
```

#### ICS Format (iCalendar)
```ics
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//TroLyLichTrinh//NONSGML v0.6.1//EN
BEGIN:VEVENT
UID:1@trolylichtrinh
DTSTART:20251106T100000
SUMMARY:Họp nhóm
LOCATION:phòng 302
BEGIN:VALARM
TRIGGER:-PT15M
ACTION:DISPLAY
END:VALARM
END:VEVENT
END:VCALENDAR
```

### Import Support

**Supported Formats:**
1. **Export format** (standard):
   ```json
   {"event_name": "...", "start_time": "2025-11-10T18:00:00", ...}
   ```

2. **Test case format** (NLP parsing):
   ```json
   {"input": "Họp nhóm 10h mai...", "expected": {...}}
   ```
   Automatically parsed through NLP pipeline

3. **ICS format**: Google Calendar, Outlook, Apple Calendar compatible

---

## 🧪 Kiểm Thử

### Run Unit Tests
```powershell
# Run all tests
python -m unittest tests\test_nlp_pipeline.py -v

# Run specific test
python -m unittest tests.test_nlp_pipeline.TestNLPPipeline.test_macro_f1 -v
```

### Test Coverage
- **Test cases**: 100,000+ scenarios
- **Macro-F1 Score**: 99.61%
- **Components tested**:
  - Event name extraction
  - Time parsing (Vietnamese)
  - Location detection (NER + regex)
  - Reminder extraction

### Generate Extended Tests
```powershell
# Generate 10,000 test cases
python tests/generate_extended_tests.py --count 10000

# Generate 100,000 test cases
python tests/generate_extended_tests.py --count 100000
```

### Run Extended Tests
```powershell
# Run with 100,000 test cases
python tests/run_extended_tests.py --max 100000 --file tests/extended_test_cases_100000.json
```

### Test Results
```
Macro-F1 Score: 0.9961
Precision: 0.9965
Recall: 0.9957

Component Breakdown:
- Event Name: 0.9980
- Time Parsing: 0.9970
- Location: 0.9945
- Reminder: 0.9950
```

---

## 📦 Đóng Gói EXE

### Using PyInstaller

#### Quick Build (Recommended)
```powershell
python -m PyInstaller TroLyLichTrinh0.6.1.spec --clean --noconfirm
```

#### Manual Build (Advanced)
```powershell
pyinstaller --onefile --windowed ^
  --name "TroLyLichTrinh0.6.1" ^
  --icon=icon.ico ^
  --add-data "database/schema.sql;database" ^
  --collect-data underthesea ^
  --collect-data tkcalendar ^
  --collect-data matplotlib ^
  --hidden-import babel.numbers ^
  --hidden-import sklearn.utils._weight_vector ^
  --hidden-import reportlab.graphics.barcode ^
  --exclude-module pytest ^
  --exclude-module unittest ^
  main.py
```

### Build Configuration (TroLyLichTrinh0.6.1.spec)

**Key Settings:**
```python
# Data files (CRITICAL!)
datas = []
datas += collect_data_files('underthesea')
datas += collect_data_files('tkcalendar')
datas += collect_data_files('matplotlib')
datas += [('database/schema.sql', 'database')]  # Fixed in v0.6.1

# Hidden imports
hiddenimports = [
    'babel.numbers',
    'sklearn.utils._weight_vector',
    'reportlab.graphics.barcode.common',
    'openpyxl.cell._writer',
    # ... (400+ sklearn imports)
]

# Exclusions (reduce size)
excludes = ['pytest', 'unittest', 'test', 'setuptools']
```

### Build Output
```
dist/
└── TroLyLichTrinh0.6.1.exe    # 111.91 MB
```

### Build Warnings (Safe to Ignore)
```
WARNING: lib not found: torch.dll
WARNING: lib not found: api-ms-win-core-path-l1-1-0.dll
WARNING: Hidden import "scipy._distributor_init" not found
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. ModuleNotFoundError: No module named 'tkcalendar'
**Solution:**
```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

#### 2. EXE Crashes on Launch (v0.6)
**Problem:** Missing `schema.sql` in PyInstaller bundle

**Solution:** Use v0.6.1 instead
```powershell
# Download from dist/
.\dist\TroLyLichTrinh0.6.1.exe
```

#### 3. Underthesea NER Not Working
**Cause:** Model files not found

**Solution:**
```powershell
# Download models manually
python -c "import underthesea; print(underthesea.__version__)"

# For EXE build:
pyinstaller --add-data "C:\Users\<USER>\.underthesea;.underthesea" ...
```

#### 4. Statistics Dashboard Error
**Problem:** Missing matplotlib/reportlab

**Solution:**
```powershell
pip install matplotlib reportlab openpyxl
```

#### 5. Timezone Issues
**Behavior:** Parser only applies timezone when explicitly stated

**Examples:**
```
"Họp 10h UTC+7"        → Applies UTC+7
"Họp 10h sáng mai"     → No timezone (naive datetime)
"Họp múi giờ +07:00"   → Applies +07:00
```

#### 6. Import JSON Fails
**Check format:**
```json
// Valid export format
{"event_name": "...", "start_time": "2025-11-10T18:00:00"}

// Valid test case format
{"input": "Họp 10h mai", "expected": {...}}
```

#### 7. Virtual Environment Path Issues
**If venv has `bin/` instead of `Scripts/`:**
```powershell
.\venv\bin\Activate.ps1
.\venv\bin\python.exe main.py
```

---

## 📝 Changelog

### Version 0.6.1 (2025-11-05) 🔥 HOTFIX
**Critical Bug Fix:**
- ✅ Fixed: EXE crash on launch (FileNotFoundError: schema.sql)
- ✅ Added: `database/schema.sql` to PyInstaller bundle
- ✅ Enhanced: Better error messages with frozen state info
- 📦 Build: 111.91 MB (same size as v0.6)
- ⏱️ Fix time: 20 minutes

**Status:** ✅ Production ready, fully functional

---

### Version 0.6 (2025-11-05) ❌ DEPRECATED
**Known Issue:** EXE crashes on launch (use v0.6.1 instead)

**Features Added:**
- 📊 Statistics Dashboard (5 tabs)
- 📄 PDF report generation (reportlab)
- 📊 Excel export (multi-sheet)
- 📈 Charts & visualizations (matplotlib)
- 🏷️ Event classification (6 categories)
- 📉 Trend analysis (4-week rolling)

**Dependencies:**
- matplotlib>=3.8.0
- reportlab>=4.0.7
- openpyxl>=3.1.2
- scikit-learn>=1.3.0

---

## 📄 License

MIT License

Copyright (c) 2025 d0ngle8k

---

## 👨‍💻 Author

**d0ngle8k**
- GitHub: [@d0ngle8k](https://github.com/d0ngle8k)
- Repository: [NLP-Processing](https://github.com/d0ngle8k/NLP-Processing)

---

## 🙏 Acknowledgments

- **underthesea**: Vietnamese NLP library
- **tkcalendar**: Calendar widget for Tkinter
- **matplotlib**: Visualization library
- **reportlab**: PDF generation
- **PyInstaller**: Python to EXE packaging

---

## 📞 Support

Nếu bạn gặp vấn đề hoặc có câu hỏi:
1. Kiểm tra [Troubleshooting](#-troubleshooting)
2. Xem [CHANGELOG.md](CHANGELOG.md) cho lịch sử phiên bản
3. Tạo issue trên GitHub

---

**⚡ Quick Start:**
```powershell
git clone https://github.com/d0ngle8k/NLP-Processing.git
cd NLP-Processing
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

**🎯 Current Version:** v0.6.1 (Stable - Production Ready)

---

<p align="center">Made with ❤️ by d0ngle8k</p>

## 🛠 Hybrid Model EXE Build (v0.8+)

Bạn có thể đóng gói ứng dụng (bao gồm mô hình PhoBERT fine-tuned hybrid) thành file `.exe` bằng script tự động.

### 1. Chuẩn bị
```powershell
git clone https://github.com/d0ngle8k/NLP-Processing.git
cd NLP-Processing
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Kiểm tra mô hình
Thư mục bắt buộc: `models/phobert_finetuned/` (nếu thiếu sẽ fallback rule-based).
Tuỳ chọn: `models/phobert_base/`.

### 3. Build ONEDIR (khuyên dùng cho mô hình lớn)
```powershell
python scripts/build_exe.py --name TroLyLichTrinhHybrid
```
Kết quả: `dist/TroLyLichTrinhHybrid/` chứa `.exe` và các file phụ.

### 4. Build ONEFILE (dung lượng lớn, khởi động chậm hơn)
```powershell
python scripts/build_exe.py --name TroLyLichTrinhHybrid --onefile
```
Kết quả: `dist/TroLyLichTrinhHybrid.exe`

### 5. Thêm underthesea cache (nếu cần)
Nếu bạn có thư mục `~/.underthesea` đã tải mô hình, copy hoặc dùng trực tiếp:
```powershell
python scripts/build_exe.py --name TroLyLichTrinhHybrid --underthesea-cache "$env:USERPROFILE\.underthesea"
```

### 6. Xác thực sau build
```powershell
dist/TroLyLichTrinhHybrid/TroLyLichTrinhHybrid.exe  # hoặc .exe onefile
```
Console log (khi chạy lần đầu nên thấy):
- `⚡ Initializing Rule-based NLP...`
- `🤖 Loading base PhoBERT...` hoặc `🤖 Loading fine-tuned PhoBERT from ...`
- `🔥 HYBRID MODE: Rule-based + PhoBERT`

Nếu không thấy dòng HYBRID MODE: kiểm tra lại mô hình đã thêm vào build (thư mục `models/phobert_finetuned`).

### 7. Tuỳ chọn loại bỏ mô hình (chỉ rule-based)
```powershell
python scripts/build_exe.py --name TroLyLichTrinhLite --no-model
```
Dung lượng nhỏ hơn đáng kể.

### 8. Mẹo tối ưu dung lượng
- Tránh --onefile nếu không cần, ONEDIR dễ nạp torch/transformers.
- Loại bỏ không dùng: sửa script thêm `excludes=['matplotlib','reportlab']` nếu không cần thống kê/PDF/Excel.
- Đảm bảo `upx` không làm hỏng DLL (mặc định PyInstaller dùng nếu có). Nếu lỗi runtime, rebuild với `--noupx` (sửa spec).

### 9. Lỗi thường gặp
| Lỗi | Nguyên nhân | Khắc phục |
|-----|-------------|-----------|
| PhoBERT failed to load | Thiếu file mô hình | Kiểm tra `models/phobert_finetuned` đầy đủ |
| ModuleNotFoundError (underthesea) | Cache không đóng gói | Thêm `--underthesea-cache` hoặc để fallback regex |
| EXE khởi động chậm | ONEFILE + torch lớn | Dùng ONEDIR |
| schema.sql missing | Data không thêm | Script đã thêm, kiểm tra log `[WARN] database/schema.sql not found` |

### 10. Cấu trúc sau khi build (ONEDIR)
```
dist/
   TroLyLichTrinhHybrid/
      TroLyLichTrinhHybrid.exe
      database/schema.sql
      models/phobert_finetuned/... (weights, tokenizer, config)
      lib/... (Python stdlib + deps)
```

### 11. Phân phối
Chỉ cần gửi nguyên folder `TroLyLichTrinhHybrid/` cho người dùng; họ double-click `.exe` để chạy (không cần Python cài đặt).

### 12. Kiểm tra fallback
Thử rename tạm `models/phobert_finetuned` bên trong dist và chạy lại – nếu thấy `⚡ RULE-BASED MODE`, nghĩa là fallback hoạt động.

---
*(Mục này được thêm ở phiên bản v0.8 hướng dẫn đóng gói hybrid model dễ dàng hơn.)*
