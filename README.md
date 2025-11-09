# 🗓️ Trợ Lý Lịch Trình - Vietnamese NLP Calendar Assistant# 

Download at: https://open-source-schedule-7tta.bolt.host/



[![Version](https://img.shields.io/badge/version-2-blue.svg)](https://github.com/d0ngle8k/NLP-Processing/releases)

[![Python](https://img.shields.io/badge/python-3.13+-brightgreen.svg)](https://www.python.org/)> Extract events, times, locations, and reminders from Vietnamese text with PhoBERT hybrid NLP pipeline

[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)


---



## ✨ Key Features[![Python](https://img.shields.io/badge/python-3.13%2B-brightgreen.svg)](https://www.python.org/)> **Status:** Production Ready ✅  



### 🤖 **Advanced NLP Processing**[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

- **Hybrid AI Pipeline**: Rule-based (100%) + PhoBERT fine-tuned (95%) with intelligent voting

- **Vietnamese Time Parsing**: 96.4% accuracy on complex expressions ("6h chiều mai", "thứ 3 tuần sau")

- **Smart Location Detection**: NER + regex with context awareness

- **Intelligent Reminders**: Extract "nhắc trước 2 tiếng" patterns---



### 🎨 **Modern UI/UX**

- **CustomTkinter Interface**: Material Design with smooth animations

- **Dark/Light Themes**: System-aware theme switching## ✨ Features

- **Calendar Integration**: Visual monthly calendar with event indicators

- **Real-time Notifications**: Background service with custom sounds# 📅 Trợ Lý Lịch Trình (Vietnamese NLP Calendar Assistant)



### 📊 **Data Management**### 🤖 **Intelligent NLP Processing**

- **SQLite Database**: Efficient local storage with full CRUD operations

- **Import/Export**: JSON, ICS (Google Calendar compatible), Excel, PDF- **Hybrid PhoBERT + Rule-based Pipeline**: 80.67% event extraction accuracy (99.1% real-world)![Version](https://img.shields.io/badge/version-0.8.1-blue.svg) ![Python](https://img.shields.io/badge/python-3.9%2B-green.svg) ![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)

- **Statistics Dashboard**: Event analytics, trends, and visualizations

- **Backup & Restore**: Easy data migration- **Advanced Time Parsing**: Supports complex Vietnamese time expressions (1h50p, 14h30, ngày mai, tuần sau...)



---- **Smart Location Detection**: Automatic location extraction with heuristic validationỨng dụng giúp tạo & quản lý lịch hẹn bằng tiếng Việt tự nhiên. Bạn nhập câu giống như trò chuyện: hệ thống tự động trích xuất sự kiện, thời gian, địa điểm, nhắc nhở. Kết hợp mô hình **Hybrid NLP** (Rule-based 100% + PhoBERT fine-tuned ≥95%).



## 🚀 Quick Start- **Context-Aware Reminders**: Extract reminder times from natural language



### **Option 1: Standalone EXE (Recommended)**---

```powershell

# Download and run immediately - no installation needed!### 🎨 **Modern UI/UX**## ✨ Tính năng chính

# File: trolylichtrinhV2.exe (3.6 GB)

# Includes: Python 3.13, PyTorch, PhoBERT models, all dependencies- **CustomTkinter Interface**: Material Design-inspired modern GUI



.\trolylichtrinhV2.exe- **Smooth Animations**: Fade effects on event updates (300ms transitions)- 🔍 Nhận dạng thời gian phức tạp: "6h chiều mai", "thứ 7 tuần sau 7h tối", "trong 2 ngày nữa".

```

- **Dark/Light Themes**: System-aware theme switching- 🗓️ Hỗ trợ nhiều định dạng ngày: `DD/MM`, `DD/MM/YYYY`, "ngày X tháng Y", tên thứ + số.

### **Option 2: Run from Source**

```powershell- **Calendar Widget**: Visual monthly calendar with event indicators- 🧠 Hybrid NLP: So sánh kết quả Rule-based & PhoBERT, tính điểm agreement.

# 1. Clone repository

git clone https://github.com/d0ngle8k/NLP-Processing.git- **Real-time Notifications**: Background service with custom sounds- 📍 Trích xuất địa điểm từ câu (NER + regex).

cd NLP-Processing

- 🔔 Nhắc nhở linh hoạt: phút / giờ / ngày ("nhắc trước 2 tiếng", "15 phút").

# 2. Create virtual environment

python -m venv .venv### 📊 **Data Management**- 📤 Export: Google Calendar / Outlook / Apple (ICS + JSON).

.\.venv\Scripts\Activate.ps1

- **SQLite Database**: Efficient local storage with full CRUD operations- 📥 Import: Đọc file export & test case format.

# 3. Install dependencies

pip install -r requirements.txt- **Import/Export**: JSON and ICS format support- 📊 Dashboard thống kê: phân bố thời gian, xu hướng 4 tuần, top địa điểm.



# 4. Run application- **Statistics Dashboard**: Event analytics and insights- 🛡️ Bảo vệ dữ liệu: xác nhận 2 lớp khi xóa toàn bộ.

python main_ctk.py

```- **Backup & Restore**: Easy data migration- 🎛️ Settings riêng + chế độ im lặng (tắt debug với `VERBOSE_LOG=False`).



---



## 📖 Usage Examples------



### **Natural Language Input**## 🧱 Kiến trúc tổng quan

```

Input: "Họp nhóm lúc 10h sáng mai ở phòng 302, nhắc trước 30 phút"## 🚀 Quick Start

Output:

  ✅ Event: "Họp nhóm"```

  ✅ Time: Tomorrow 10:00 AM

  ✅ Location: "phòng 302"### **Option 1: Run Executable (Windows)**┌─────────────────────────────────────────┐

  ✅ Reminder: 30 minutes before

```│            Hybrid NLP Pipeline          │



### **Complex Time Patterns**1. Download the latest release from [Releases](https://github.com/d0ngle8k/NLP-Processing/releases)├─────────────────────────────────────────┤

```

✅ "6h chiều mai" → Tomorrow 6:00 PM2. Extract `TroLyLichTrinh_v1.0.4_Improved.exe` (987 MB)│  Rule-based Parser  │  PhoBERT Fine-tuned │

✅ "thứ 3 tuần sau 2h" → Next Wednesday 2:00 PM

✅ "15/12 lúc 14h30" → December 15, 2:30 PM3. Double-click to run - no installation needed!│  100% edge cases    │  Contextual          │

✅ "tuần sau thứ 5" → Next Friday

```└──────────┬──────────┴──────────┬─────────┘



### **Reminder Patterns****System Requirements:**                ▼                     ▼

```

✅ "nhắc trước 2 tiếng" → 120 minutes before- Windows 10/11 (64-bit)            Voting / Merge Engine  (Agreement Score)

✅ "nhắc 30 phút" → 30 minutes before

✅ "nhắc trước 1 ngày" → 24 hours before- 2 GB RAM minimum                              ▼

```

- 1.5 GB disk space                  Chuẩn hoá kết quả cuối

---

```

## 🏗️ Architecture

### **Option 2: Run from Source**

```

┌─────────────────────────────────────────────────────────────┐Thành phần chính:

│                     User Interface (CTk)                     │

│  ┌──────────────┬──────────────┬──────────────────────────┐ │```powershell- `core_nlp/pipeline.py`: Rule-based phân tích thời gian / ngày.

│  │ Event Input  │   Calendar   │   Statistics Dashboard   │ │

│  └──────────────┴──────────────┴──────────────────────────┘ │# 1. Clone repository- `core_nlp/hybrid_pipeline.py`: Kết hợp PhoBERT + Rule-based.

└────────────────────────┬────────────────────────────────────┘

                         │git clone https://github.com/d0ngle8k/NLP-Processing.git- `database/db_manager.py`: SQLite + schema + kết nối.

         ┌───────────────┴───────────────┐

         │     NLP Pipeline (Hybrid)     │cd NLP-Processing- `services/*`: Export/Import/Notification/Statistics.

         │  ┌──────────┬──────────────┐  │

         │  │ PhoBERT  │  Rule-based  │  │- `widgets/`: Thành phần giao diện CustomTkinter.

         │  │   NER    │   Patterns   │  │

         │  └──────────┴──────────────┘  │# 2. Create virtual environment (Python 3.13+ recommended)

         └───────────────┬───────────────┘

                         │python -m venv .venv---

         ┌───────────────┴───────────────┐

         │      Services Layer           │.\.venv\Scripts\Activate.ps1## 📦 Cài đặt

         │  • Time Parser               │

         │  • Location Extractor        │

         │  • Notification Service      │

         │  • Import/Export Service     │# 3. Install dependencies### Yêu cầu

         └───────────────┬───────────────┘

                         │pip install -r requirements.txt- Python 3.9+ (khuyên dùng 3.12)

         ┌───────────────┴───────────────┐

         │     Database (SQLite)         │- Windows 10+ 64-bit

         │  • Events, Reminders, Sounds │

         └───────────────────────────────┘# 4. Run application- RAM 2GB+, Disk trống ≥1GB (bundle exe lớn do model + PyTorch)

```

python main_ctk.py

### **Core Components**

```### Clone & môi trường

| Component | Purpose | Accuracy |

|-----------|---------|----------|```powershell

| **Hybrid Pipeline** | Combines AI + rules for best results | 99.7% |

| **Time Parser** | Vietnamese time expression parsing | 96.4% |---git clone https://github.com/d0ngle8k/NLP-Processing.git

| **Location Extractor** | Smart location detection | 25.3% |

| **Notification Service** | Background reminders | 100% |cd NLP-Processing



---## 📖 Usage Examplespython -m venv .venv



## 📊 Performance Metrics.\.venv\Scripts\Activate.ps1



### **NLP Accuracy (1000 test prompts)**### **Basic Event Creation**pip install -r requirements.txt

| Metric | Before (v0.5) | After (v0.6.1) | Improvement |

|--------|----------------|----------------|-------------|```

| **Time Extraction** | 15.7% | **96.4%** | +80.7% |

| **Location Detection** | 24.8% | 25.3% | +0.5% |```

| **Event Extraction** | 87.5% | **99.7%** | +12.2% |

| **PhoBERT Errors** | 2 errors | **0 errors** | Fixed |Input: "Họp nhóm ngày mai lúc 2 giờ chiều tại phòng A301"---



### **Processing Performance**Output:## 🚀 Chạy ứng dụng

- **Speed**: 202.4 prompts/second

- **Memory**: ~4GB RAM during operation  - Event: Họp nhóm

- **Startup**: ~3 seconds (PhoBERT model loading)

- **Reliability**: 0 crashes on 1000+ test cases  - Time: Tomorrow 14:00### GUI (CustomTkinter)



---  - Location: phòng A301```powershell



## 📁 Project Structure```python main_ctk.py



``````

NLP-Processing/

├── main_ctk.py                    # Main GUI application### **Complex Time Patterns**

├── main.py                        # Legacy Tkinter version

├── requirements.txt               # Python dependencies### CLI thử nghiệm (Hybrid Debug)

├── trolylichtrinhV2.spec         # PyInstaller build config

├── README.md                      # This documentation``````powershell

├── CHANGELOG.md                   # Version history

│Input: "Đi gym 1h50p sáng mai"python version_document/interactive_test_hybrid.py

├── core_nlp/                      # NLP Processing Engine

│   ├── pipeline.py               # Rule-based extraction logicOutput:```

│   ├── hybrid_pipeline.py        # Hybrid AI + Rule-based

│   ├── time_parser.py            # Vietnamese time parsing  - Event: Đi gym

│   └── phobert_model.py          # PhoBERT integration

│  - Time: Tomorrow 01:50### Tắt / bật debug

├── database/                      # Data Layer

│   ├── db_manager.py             # SQLite operationsTrong `main_ctk.py` đổi:

│   ├── schema.sql                # Database schema

│   └── events.db                 # SQLite database (auto-created)Input: "Họp team 14h30 ngày 15/12"```python

│

├── services/                      # Business LogicOutput:VERBOSE_LOG = False  # True để xem log chi tiết

│   ├── notification_service.py   # Background reminders

│   ├── export_service.py         # JSON/ICS export  - Event: Họp team```

│   ├── import_service.py         # JSON/ICS import

│   ├── statistics_service.py     # Analytics & reporting  - Time: 2025-12-15 14:30

│   └── sound_service.py          # Audio notifications

│```---

├── widgets/                       # UI Components

│   ├── event_card.py             # Event display cards## 🛠 Build file EXE (PyInstaller)

│   └── calendar_widget.py        # Calendar integration

│### **Reminder Support**

├── models/                        # AI Models (~1GB)

│   ├── phobert_base/             # Pre-trained PhoBERTSử dụng spec tối ưu: `build_main_ctk.spec` (đã loại bỏ thư mục rỗng, thêm hidden imports). 

│   └── phobert_finetuned/        # Fine-tuned for calendar

│```

├── tests/                         # Test Suite

│   ├── test_nlp_pipeline.py      # Unit testsInput: "Nộp báo cáo ngày 20/12 nhắc trước 1 ngày"```powershell

│   ├── test_cases.json           # Test data

│   ├── run_extended_tests.py     # Test runnerOutput:.\.venv\Scripts\python.exe -m PyInstaller --clean build_main_ctk.spec

│   └── full_test_results_v0.6.1.json  # Latest results

│  - Event: Nộp báo cáo```

├── dist/                          # Distribution

│   ├── trolylichtrinhV2.exe      # Standalone executable (3.6GB)  - Time: 2025-12-20Kết quả: `dist/TroLyLichTrinhV2.exe`

│   └── README_EXE.txt            # EXE usage guide

│  - Reminder: 2025-12-19 (1 day before)

└── scripts/                       # Utilities

    └── generate_report.py        # Report generation```Nếu lỗi Permission Denied khi update checksum: đóng mọi phiên bản đang chạy rồi build lại.

```



---

------

## 🧪 Testing

## 🧪 Kiểm thử

### **Run Tests**

```powershell## 🏗️ Architecture

# Unit tests

python -m unittest tests/test_nlp_pipeline.py -v| Suite | Số test | Trạng thái |



# Extended test suite (1000 prompts)```|-------|---------|------------|

python tests/run_extended_tests.py

┌─────────────────────────────────────────────────────────────┐| NLP Pipeline | 42 | ✅ |

# Performance benchmark

python -c "│                     User Interface (CTk)                     │| Hybrid Voting | 10 | ✅ |

from core_nlp.hybrid_pipeline import HybridNLPPipeline

import time│  ┌──────────────┬──────────────┬──────────────────────────┐ │| New Patterns | 8 | ✅ |



pipeline = HybridNLPPipeline()│  │ Event Input  │   Calendar   │   Statistics Dashboard   │ │| Extended Edge Cases | 1065 | ✅ |

start = time.time()

results = [pipeline.process('Họp nhóm 10h mai') for _ in range(100)]│  └──────────────┴──────────────┴──────────────────────────┘ │

elapsed = time.time() - start

print(f'100 prompts: {elapsed:.2f}s ({100/elapsed:.1f} prompts/sec)')└────────────────────────┬────────────────────────────────────┘Chạy nhanh:

"

```                         │```powershell



### **Test Results**         ┌───────────────┴───────────────┐python tests/test_nlp_pipeline.py

```

✅ Events: 997/1000 (99.7%)         │     NLP Pipeline (Hybrid)     │python tests/run_extended_tests.py

✅ Times: 964/1000 (96.4%)

✅ Locations: 253/1000 (25.3%)         │  ┌──────────┬──────────────┐  │```

✅ Errors: 0/1000 (0.0%)

✅ Processing: 4.9s (202.4 prompts/sec)         │  │ PhoBERT  │  Rule-based  │  │

```

         │  │   NER    │   Patterns   │  │---

---

         │  └──────────┴──────────────┘  │## 📂 Cấu trúc dự án (rút gọn)

## 📦 Build Standalone EXE

         └───────────────┬───────────────┘```

### **Using PyInstaller**

```powershell                         │NLP-Processing/

# Install PyInstaller

pip install pyinstaller         ┌───────────────┴───────────────┐├── main_ctk.py                # Entry GUI



# Build executable (includes all models & dependencies)         │      Services Layer           │├── build_main_ctk.spec        # PyInstaller spec chuẩn

pyinstaller --clean trolylichtrinhV2.spec

         │  • Time Parser               │├── core_nlp/                  # NLP logic & hybrid

# Result: dist/trolylichtrinhV2.exe (3.6GB)

```         │  • Location Extractor        │├── services/                  # Export / Import / Notification / Stats



### **EXE Features**         │  • Notification Service      │├── widgets/                   # CustomTkinter components

- ✅ **Self-contained**: No Python installation required

- ✅ **All dependencies**: PyTorch, transformers, underthesea included         │  • Import/Export Service     │├── database/                  # SQLite schema & manager

- ✅ **PhoBERT models**: Fine-tuned Vietnamese NLP models

- ✅ **Database**: SQLite with schema         └───────────────┬───────────────┘├── models/                    # PhoBERT (fine-tuned)

- ✅ **Sounds**: Notification audio files

- ✅ **Cross-platform**: Windows 10/11 compatible                         │├── training_data/             # Dữ liệu huấn luyện/validation



### **Distribution**         ┌───────────────┴───────────────┐├── tests/                     # Bộ test tự động

```powershell

# The exe is completely standalone         │     Database (SQLite)         │└── version_document/          # Tài liệu archive (changelog, design, guides)

# Just share trolylichtrinhV2.exe - users can run it immediately

.\trolylichtrinhV2.exe         │  • Events, Reminders, Sounds │```

```

         └───────────────────────────────┘

---

```---

## 🔧 Configuration

## 📥📤 Import / Export

### **Model Selection**

Edit `main_ctk.py` to choose NLP pipeline:---- JSON: Backup & restore sự kiện.



```python- ICS: Đồng bộ Google / Outlook / Apple.

# Option 1: Hybrid (Recommended)

from core_nlp.hybrid_pipeline import HybridNLPPipeline## 📂 Project Structure- Export báo cáo: scripts/generate_report.py (PDF/Excel).

nlp = HybridNLPPipeline()



# Option 2: Rule-based only (Fast, 100% accurate)

from core_nlp.pipeline import NLPPipeline```---

nlp = NLPPipeline()

NLP-Processing/## 🔔 Nhắc nhở

# Option 3: PhoBERT only (Experimental)

from core_nlp.phobert_model import PhoBERTNLPPipeline├── main_ctk.py                    # Main application (CustomTkinter GUI)- Thread nền kiểm tra mỗi 60s (`notification_service.py`).

nlp = PhoBERTNLPPipeline()

```├── main.py                        # Legacy Tkinter version- Tránh spam: đánh dấu đã thông báo.



### **Debug Mode**├── requirements.txt               # Python dependencies- Hỗ trợ trước X phút/giờ/ngày.

```python

# Enable verbose logging├── build_main_ctk.spec           # PyInstaller build configuration

VERBOSE_LOG = True  # Shows model loading, processing steps

```├── .gitignore                    # Git ignore patterns---



---│## 🧠 NLP Highlights



## 🐛 Troubleshooting├── core_nlp/                      # NLP Processing Engine- Xử lý lỗi gõ phổ biến: "támh", "mườih".



### **Common Issues**│   ├── pipeline.py               # Hybrid PhoBERT + Rule-based pipeline- Chuẩn hoá buổi: sáng / chiều / tối / trưa.



| Issue | Solution |│   └── time_parser.py            # Vietnamese time expression parser- Tương đối: "trong 2 ngày", "tuần sau", "tháng sau".

|-------|----------|

| **Module not found** | `pip install -r requirements.txt` |│- Múi giờ: hỗ trợ chuẩn hoá + nội suy nếu thiếu năm.

| **EXE won't start** | Check antivirus, run as administrator |

| **Slow startup** | Normal - PhoBERT model loading (~3s) |├── database/                      # Data Layer

| **Time parsing errors** | Use explicit formats: "10h sáng mai" |

| **Database locked** | Close all app instances, restart |│   ├── db_manager.py             # SQLite operations---

| **Sound not working** | Check Windows audio settings |

│   └── schema.sql                # Database schema## 🛡️ Bảo trì & đóng góp

### **Performance Tips**

- **For speed**: Use rule-based pipeline│Pull Request được chào đón. Vui lòng kèm test cho logic NLP mới.

- **For accuracy**: Use hybrid pipeline

- **For large datasets**: Enable database indexes├── services/                      # Business Logic

- **For low memory**: Reduce batch processing size

│   ├── notification_service.py   # Background reminders---

---

│   ├── import_service.py         # JSON/ICS import## 📝 Tài liệu mở rộng

## 📝 Changelog

│   ├── export_service.py         # JSON/ICS exportXem thư mục `version_document/` (được ignore trong Git để giảm noise) chứa: 

### **v0.6.1 (2025-11-09)** 🔥 LATEST

- ✅ **Massive improvement**: Time extraction 15.7% → 96.4% (+80.7%)│   └── statistics_service.py     # Analytics & reporting- Changelog & Hotfix (`V0.*.md`)

- ✅ **Fixed PhoBERT errors**: 0 errors on 1000 test prompts

- ✅ **Enhanced location detection**: 50+ new Vietnamese patterns│- UI redesign (`BA_GOOGLE_CALENDAR_UI_REDESIGN.md`)

- ✅ **Standalone EXE**: trolylichtrinhV2.exe (3.6GB) with all dependencies

- ✅ **Production ready**: 202.4 prompts/sec processing speed├── widgets/                       # UI Components- Training guides (Colab, GPU)



### **v0.6.0 (2025-11-05)**│   ├── calendar_widget.py        # Monthly calendar view- Sound system & Theme updates

- ✅ Statistics dashboard with charts

- ✅ PDF/Excel export capabilities│   ├── event_list_widget.py      # Event list with animations

- ✅ Enhanced UI with CustomTkinter

- ✅ Background notification service│   └── settings_widget.py        # Settings dialog---



### **v0.5.0 (2025-11-04)**│## ⚠️ Troubleshooting

- ✅ Initial hybrid NLP pipeline

- ✅ Basic Vietnamese time parsing├── models/                        # AI Models (~1 GB)| Vấn đề | Nguyên nhân | Cách xử lý |

- ✅ SQLite database integration

- ✅ JSON/ICS import/export│   ├── phobert_base/             # Pre-trained PhoBERT|--------|-------------|------------|



---│   └── phobert_finetuned/        # Fine-tuned for calendar tasks| PhoBERT load chậm | Kích thước model | Kiên nhẫn (~vài giây) / preload |



## 📄 License│| EXE >900MB | PyTorch + model | Dùng zip phân phối / build lại khi tối ưu |



**MIT License** - Free for personal and commercial use├── sounds/                        # Notification Sounds| Lỗi checksum khi build | File exe đang mở | Tắt ứng dụng rồi build lại |



```│   └── sound1-4.wav              # Default notification tones| Không hiện âm thanh | Thiếu preset | Tạo file .wav trong `sounds/` |

Copyright (c) 2025 d0ngle8k

│

Permission is hereby granted, free of charge, to any person obtaining a copy

of this software and associated documentation files (the "Software"), to deal├── training_data/                 # Training Datasets---

in the Software without restriction, including without limitation the rights

to use, copy, modify, merge, publish, distribute, sublicense, and/or sell│   └── ...                       # Labeled training examples## 📄 License

copies of the Software...

```│Chưa khai báo – bổ sung sau (MIT khuyến nghị).



---├── tests/                         # Test Suite



## 👨‍💻 Author│   ├── test_nlp_pipeline.py      # NLP unit tests---



**Trường Gia Thành (d0ngle8k)**│   ├── test_cases.json           # Baseline test dataset## ✅ Trạng thái hiện tại

- **GitHub**: [@d0ngle8k](https://github.com/d0ngle8k)

- **Repository**: [NLP-Processing](https://github.com/d0ngle8k/NLP-Processing)│   ├── extended_test_cases*.json # Extended test suites- Production GUI ✅

- **Email**: Contact via GitHub

│   └── test_date_parsing_results.json- Silent startup ✅

---

│- EXE build verified ✅

## 🙏 Acknowledgments

├── scripts/                       # Utility Scripts- NLP >1000 edge cases ✅

- **PhoBERT** - Vietnamese BERT model by VinAI Research

- **underthesea** - Vietnamese NLP toolkit│   └── generate_report.py        # Report generation

- **CustomTkinter** - Modern tkinter UI library

- **PyTorch** - Deep learning framework│---

- **Transformers** - Hugging Face library

├── version_document/              # Version History & Documentation*README được viết lại gọn gàng từ bản cũ bị trộn nội dung. Nếu cần thêm English section, thông báo để bổ sung.*

---

│   ├── INDEX.md                  # Documentation index```

## 📞 Support

│   ├── RELEASE_v1.0.3.md        # Release notes

**Need help?**

1. Check [Troubleshooting](#-troubleshooting) section│   └── ...                       # 30+ technical documents

2. Review [CHANGELOG.md](CHANGELOG.md) for updates

3. Create an issue on GitHub│

4. Check the [Wiki](https://github.com/d0ngle8k/NLP-Processing/wiki) for guides

├── build/                         # Build artifacts (gitignored)## 🔧 Configuration

---

│   └── build_main_ctk/           # Latest build cache

## 🎯 Roadmap

│#### 3. Sửa Sự Kiện- [Troubleshooting](#-troubleshooting)

### **✅ Completed**

- [x] Hybrid NLP pipeline with 96.4% accuracy└── dist/                          # Distribution folder

- [x] Modern CustomTkinter UI

- [x] Standalone EXE distribution    └── TroLyLichTrinh_v1.0.4_Improved.exe  # Standalone executable### Model Selection

- [x] Vietnamese time parsing

- [x] Statistics and reporting```

- [x] Import/export functionality

- Double-click vào sự kiện trong danh sách

### **🚧 In Progress**

- [ ] Google Calendar sync---

- [ ] Mobile app (Flutter)

- [ ] Voice input integrationEdit `main.py` to change model:

- [ ] Multi-language support

## 🧠 NLP Pipeline Details

### **💡 Planned**

- [ ] Recurring events- Chỉnh sửa thông tin trong form- [Changelog](#-changelog)- Phân tích thời gian: `core_nlp/time_parser.py`

- [ ] Team collaboration

- [ ] Smart suggestions### **Event Extraction Accuracy**

- [ ] Advanced analytics

```python

---

| Metric | Test Cases | Baseline | Extended | Real-World |

<p align="center">

  <strong>⭐ Star this repo if you find it useful!</strong>|--------|-----------|----------|----------|------------|# Option 1: Hybrid (Recommended)- Bấm **"Sửa"** để lưu

  <br>

  Made with ❤️ for Vietnamese NLP processing| **Event Name** | 1,107 | 100% | 80.67% | **99.1%** |

  <br>

  <em>Version 0.6.1 - Production Ready</em>| **Time Parsing** | 1,107 | 98.5% | 95.2% | 97.8% |from core_nlp.hybrid_pipeline import HybridNLPPipeline

</p>
| **Location** | 543 | 96.7% | 92.3% | 95.1% |

nlp = HybridNLPPipeline()- [License](#-license)    - Quy tắc thủ công cho ngày/giờ tường minh và tương đối; mặc định giờ nếu thiếu (ví dụ 09:00 hoặc theo buổi).

*Real-world accuracy excludes 210 meta-test artifacts*



### **Supported Time Patterns**

# Option 2: Rule-based only (Faster, 100% accurate)#### 4. Xóa Sự Kiện

```python

# Specific timesfrom core_nlp.pipeline import NLPPipeline

"14h30", "2 giờ chiều", "1h50p", "9h15 sáng"

nlp = NLPPipeline()- Chọn sự kiện → Bấm **"Xóa"** (xóa 1 sự kiện)    - Timezone chỉ áp dụng khi người dùng nêu rõ (UTC/GMT hoặc “múi giờ +..”).

# Relative dates

"hôm nay", "ngày mai", "tuần sau", "tháng tới"



# Complex expressions# Option 3: PhoBERT only (Experimental)- Hoặc bấm **"Xóa tất cả"** → Xác nhận 2 lần

"thứ 3 tuần sau", "ngày 15/12", "cuối tháng này"

from core_nlp.phobert_model import PhoBERTModel

# Reminders

"nhắc trước 1 ngày", "nhắc trước 2 giờ", "nhắc 30 phút trước"nlp = PhoBERTModel(model_path='./models/phobert_finetuned')---

```

```

### **Location Patterns**

#### 5. Import/Export

```python

# Explicit locations## 📝 Pattern Support

"tại phòng A301", "ở Hà Nội", "tại công ty"

- Bấm **"⚙️ Cài đặt"** (góc dưới bên trái)- CSDL: `database/db_manager.py` + `database/schema.sql`

# Smart extraction

"họp công ty"        → Location: "công ty"### Thời gian (Time)

"đi siêu thị"        → Location: "siêu thị"

"cafe quán góc phố"  → Location: "quán góc phố"- ✅ "6h sáng", "3h chiều", "9h tối"- **Xuất JSON/ICS**: Lưu toàn bộ dữ liệu

```

- ✅ "6:30", "15:45"

---

- ✅ "6 rưỡi", "7h30"- **Nhập JSON/ICS**: Khôi phục hoặc import từ nguồn khác## 💻 Yêu Cầu Hệ Thống    - SQLite lưu `events(id, event_name, start_time, end_time, location, reminder_minutes, status)`.

## 🔧 Development



### **Setup Development Environment**

### Ngày (Date)

```powershell

# Install development dependencies- ✅ "hôm nay", "ngày mai", "ngày kia"

pip install -r requirements.txt

pip install pytest black flake8- ✅ "thứ 2", "thứ ba", "chủ nhật"---    - CRUD, lấy theo ngày, lấy nhắc nhở “pending” và cập nhật trạng thái `notified` sau khi hiển thị.



# Run tests- ✅ "tuần sau", "tháng sau"

python -m pytest tests/

- ✅ "ngày 20 tháng 10"

# Format code

python -m black .- ✅ **NEW:** "20/10", "25/12", "1/1/2026"



# Lint- ✅ **NEW:** "ngày 20/10"## 🏗️ Kiến Trúc Hệ Thống### Minimum Requirements

python -m flake8 --max-line-length=100

```



### **Build Standalone Executable**### Nhắc nhở (Reminder)



```powershell- ✅ "nhắc trước 30 phút"

# Activate virtual environment

.\.venv\Scripts\Activate.ps1- ✅ "nhắc trước 2 giờ"### Cấu Trúc Thư Mục- **OS**: Windows 10+ (64-bit)- Dịch vụ: `services/`



# Build with PyInstaller- ✅ **NEW:** "nhắc trước 2 tieng"

python -m PyInstaller --clean build_main_ctk.spec

- ✅ **NEW:** "nhắc trước 1 tiếng"```

# Output: dist/TroLyLichTrinh_v1.0.4_Improved.exe (~987 MB)

```



**Build includes:**### Khoảng thời gian (Duration)NLP-Processing/- **Python**: 3.9+ (recommended: 3.12.0)    - `import_service.py`: đọc JSON/ICS và ghi vào DB.

- Python 3.13 runtime

- PhoBERT models (1 GB)- ✅ "từ 2h đến 4h"

- PyTorch libraries (428 MB)

- All dependencies bundled- ✅ "2h-4h"├── main.py                      # GUI chính (Tkinter)



### **Run Tests**- ✅ "khoảng 2 tiếng"



```powershell├── requirements.txt             # Python dependencies- **RAM**: 4GB+    - `export_service.py`: xuất toàn bộ DB ra JSON/ICS.

# Unit tests

python tests/test_nlp_pipeline.py## 🆕 What's New in V0.6.2



# Extended test suite (1,107 cases)├── README.md                    # Tài liệu này

python tests/run_extended_tests.py

### Bug Fixes

# Performance benchmarks

python tests/test_cases.json  # Baseline accuracy1. **Reminder Hours Support** - Thêm hỗ trợ "tieng/tiếng" cho reminder├── CHANGELOG.md                 # Lịch sử phiên bản- **Disk**: 500MB free space    - `notification_service.py`: luồng kiểm tra nhắc nhở và popup.

```

   - Before: "nhắc trước 2 tieng" → 0 mins ❌

---

   - After: "nhắc trước 2 tieng" → 120 mins ✅│

## 📊 Performance Metrics



### **v1.0.4 Optimizations**

2. **DD/MM Date Format** - Hỗ trợ định dạng ngày DD/MM├── core_nlp/                    # Module xử lý NLP

| Component | Before | After | Improvement |

|-----------|--------|-------|-------------|   - Before: "ngày 20/10" → None ❌

| Event Extraction | 76.96% | 80.67% | +3.71% |

| Complex Events (4-15 words) | 65% | 95% | +30% |   - After: "ngày 20/10" → 2025-10-20 ✅│   ├── pipeline.py              # Pipeline chính (NER + Time + Location)

| Priority Matching | Random | Optimized | Smart 3→2→1 word |

| Time Parsing (1h50p) | ❌ | ✅ | New pattern |



### **Real-world Performance**### Files Changed│   └── time_parser.py           # Parser thời gian tiếng Việt### Dependencies- Kiểm thử: `tests/`



```- `core_nlp/pipeline.py` - Added "tieng|tiếng" to reminder patterns

Total Tests: 1,107

├── Real Events: 897 (81%)- `core_nlp/time_parser.py` - Fixed DD/MM parsing with "ngày" prefix│

│   ├── Passed: ~889 (99.1%)

│   └── Failed: ~8 (0.9%)

└── Meta Tests: 210 (19%) - excluded from metrics

```### Test Results├── database/                    # Lớp database```plaintext    - `tests/test_cases.json`: bộ dữ liệu kỳ vọng.



---- ✅ All 1065 extended tests passed



## 🎯 Features Roadmap- ✅ 8/8 new pattern tests passed│   ├── db_manager.py            # SQLite CRUD operations



### **✅ Completed**- ✅ No regressions detected

- [x] CustomTkinter modern UI

- [x] PhoBERT hybrid NLP pipeline│   ├── schema.sql               # Database schema# Core NLP    - `tests/test_nlp_pipeline.py`: unittest tính macro-F1 cho 4 nhánh (event, time, location, reminder).

- [x] Fade animations (300ms)

- [x] Sound persistence to database## 📊 Performance

- [x] Time pattern 1h50p support

- [x] Calendar widget integration│   └── events.db                # SQLite database (auto-created)

- [x] Import/Export JSON/ICS

| Metric | Value |

### **🚧 In Progress**

- [ ] Google Calendar sync|--------|-------|│underthesea>=6.7.0        # Vietnamese NLP (NER, word segmentation)

- [ ] Mobile app (Flutter)

- [ ] Multi-language support| Accuracy (Rule-based) | 100% |



### **💡 Planned**| Accuracy (PhoBERT) | 95% |├── services/                    # Business logic services

- [ ] Voice input integration

- [ ] Smart suggestions| Accuracy (Hybrid) | ~100% |

- [ ] Recurring events

- [ ] Team collaboration| Avg Processing Time | <100ms |│   ├── import_service.py        # Import JSON/ICS → DBpython-dateutil>=2.8.2    # Date parsing utilities## Cấu trúc thư mục và tệp chính



---| Agreement Score | 84.3% avg |



## 🐛 Troubleshooting│   ├── export_service.py        # Export DB → JSON/ICS



### **Common Issues**## 🐛 Known Issues



#### **1. Exe file won't start**│   └── notification_service.py  # Background reminder thread

```

Problem: ModuleNotFoundError- Event extraction may fail with very complex multi-pattern inputs

Solution: Download from Releases, don't rename/move files

```- PhoBERT model requires ~500MB RAM│



#### **2. NLP extraction errors**- First run loads PhoBERT model (~3s startup time)

```

Problem: Event not detected├── scripts/                     # Utility scripts# GUI Components```

Solution: Use explicit patterns like "Họp [event] lúc [time] tại [location]"

```## 🤝 Contributing



#### **3. Database locked**│   ├── generate_edge_case_tests.py  # Tạo test cases

```

Problem: Database is locked### Development Setup

Solution: Close all app instances, delete events.db-wal

```│   └── generate_report.py           # Tạo báo cáotkcalendar>=1.6.1         # Calendar widget.



#### **4. Models not found**```bash

```

Problem: PhoBERT models missing# Install dev dependencies│

Solution: Ensure models/ folder exists with phobert_base/ and phobert_finetuned/

```pip install -r requirements.txt



---└── tests/                       # Testing suitetkinter                    # Standard library (included with Python)├── main.py                     # Tkinter GUI, nhập NLP, lịch, chỉnh sửa, import/export, nhắc nhở



## 📚 Documentation# Run tests before commit



### **Core Documentation**python tests/run_extended_tests.py    ├── test_nlp_pipeline.py     # Unit tests

- [Version Index](version_document/INDEX.md) - All version documents

- [Release v1.0.3](version_document/RELEASE_v1.0.3.md) - Latest release notespython tests/test_hybrid_pipeline.py

- [Build Guide](version_document/BUILD_SUCCESS_v1.0.3.md) - Build instructions

- [Deployment](version_document/DEPLOYMENT_v1.0.3.md) - Deployment checklist```    ├── run_edge_case_tests.py   # Edge case test runner├── core_nlp/



### **Technical Docs**

- [UI Redesign](version_document/BA_GOOGLE_CALENDAR_UI_REDESIGN.md)

- [Sound System](version_document/SOUND_SYSTEM_V2.md)### Adding New Patterns    ├── test_cases.json          # Test dataset

- [NLP Training](version_document/GPU_TRAINING_GUIDE.md)

- [Testing Guide](version_document/TEST_GUIDE_v0.8.1.md)



---1. Update regex patterns in `core_nlp/pipeline.py`    └── edge_case_tests_1000.json  # 1050 edge cases# Data Processing│   ├── pipeline.py             # NLPPipeline: NER (underthesea) + regex trích event/time/location/reminder



## 🤝 Contributing2. Update parsing logic in `core_nlp/time_parser.py`



We welcome contributions! Please follow these guidelines:3. Add test cases in `tests/test_cases.json````



1. **Fork** the repository4. Run full test suite

2. **Create** a feature branch (`git checkout -b feature/AmazingFeature`)

3. **Commit** your changes (`git commit -m 'Add some AmazingFeature'`)5. Update documentationbabel>=2.13.1             # Locale and timezone support│   └── time_parser.py          # parse_vietnamese_time: quy tắc thời gian tiếng Việt

4. **Push** to the branch (`git push origin feature/AmazingFeature`)

5. **Open** a Pull Request



### **Development Standards**## 📄 License### Luồng Xử Lý NLP

- Follow PEP 8 style guide

- Write unit tests for new features

- Update documentation

- Add examples to READMEThis project is licensed under the MIT License.├── database/



---



## 📄 License## 👨‍💻 Author```



This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.



---**d0ngle8k**Input: "thứ 3 mười giờ tôi có lịch phỏng vấn ở tầng 5, nhắc trước 30 phút"# Import/Export│   ├── db_manager.py           # SQLite CRUD và các truy vấn tiện ích



## 🙏 Acknowledgments- Repository: [NLP-Processing](https://github.com/d0ngle8k/NLP-Processing)



- **PhoBERT** - Vietnamese BERT model by VinAI Research   │

- **CustomTkinter** - Modern tkinter UI library

- **underthesea** - Vietnamese NLP toolkit## 🙏 Acknowledgments

- **PyInstaller** - Executable packaging

   ▼ics>=0.7.2                # iCalendar format support│   └── schema.sql              # DDL tạo bảng events

---

- **PhoBERT** - Pre-trained Vietnamese BERT model

## 📞 Contact

- **VNCoreNLP** - Vietnamese NLP toolkit┌─────────────────────────────────────────┐

**Author:** d0ngle8k  

**GitHub:** [@d0ngle8k](https://github.com/d0ngle8k)  - Test data contributors

**Repository:** [NLP-Processing](https://github.com/d0ngle8k/NLP-Processing)

│ 1. Normalize & Extract Time Patterns   │├── services/

---

---

## 📈 Statistics

│    → "thứ 3 mười giờ"                  │

```

📊 Project Stats**Made with ❤️ for Vietnamese NLP**

├── Lines of Code: ~4,500

├── Test Coverage: 85%+└─────────────────────────────────────────┘# Statistics & Reporting (v0.6+)│   ├── import_service.py       # Import JSON/ICS → DB

├── Documentation: 35+ files

├── Versions Released: 12+   │

└── Accuracy: 99.1% (real-world)

   ▼matplotlib>=3.8.0         # Charts and visualizations│   ├── export_service.py       # Export DB → JSON/ICS

🎯 NLP Performance

├── Event Extraction: 80.67%┌─────────────────────────────────────────┐

├── Time Parsing: 95.2%

├── Location Detection: 92.3%│ 2. Parse Vietnamese Time                │reportlab>=4.0.7          # PDF report generation│   └── notification_service.py # Luồng nền kiểm tra và popup nhắc nhở

└── Processing Speed: <100ms/query

│    → datetime: 2025-11-11T10:00:00     │

💾 Build Size

├── Exe File: 987 MB└─────────────────────────────────────────┘openpyxl>=3.1.2          # Excel file generation├── tests/

├── Models: 1,034 MB

├── PyTorch: 428 MB   │

└── Dependencies: ~250 MB

```   ▼scikit-learn>=1.3.0      # Machine learning utilities│   ├── test_nlp_pipeline.py    # unittest tính macro-F1



---┌─────────────────────────────────────────┐



<div align="center">│ 3. Extract Location (NER + Regex)      │```│   └── test_cases.json         # dữ liệu kiểm thử



**⭐ Star this repo if you find it useful!**│    → "tầng 5"                           │



Made with ❤️ by d0ngle8k└─────────────────────────────────────────┘├── requirements.txt



</div>   │


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
