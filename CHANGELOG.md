# TroLyLichTrinh - Release Notes

## Version 0.4 (2025-11-05)

### ✨ New Features
- **Treeview Scrollbars**: Added vertical and horizontal scrollbars
  - Vertical scrollbar: Essential for viewing many events (100s or 1000s)
  - Horizontal scrollbar: Useful when content is wide
  - Professional UI with standard scrollbar behavior

### 🎯 Improvements
- **Grid Layout**: Switched from pack() to grid() for better widget positioning
- **Responsive Design**: Configured grid weights for proper window resizing
- **Better UX**: Can now scroll through large datasets imported from test files

### 📦 Technical
- File size: ~24.76 MB
- Grid-based layout with columnconfigure/rowconfigure weights
- Scrollbar linking via yscrollcommand/xscrollcommand
- Sticky flags for proper widget expansion

---

## Version 0.3 (2025-11-05)

### ✨ New Features
- **Dual-format JSON Import**: Import both export format AND test case format
  - Export format: `{"event_name": "...", "start_time": "2025-11-10T18:00:00", ...}`
  - Test case format: `{"input": "Họp nhóm 10h mai...", "expected": {...}}` - auto-parsed with NLP
  - Can now import files directly from `./tests/` directory
- **10,000 Test Cases Generator**: Enhanced generator with CLI arguments
  - `--count`: Specify number of test cases (default 1000)
  - `--output`: Custom output file path
  - `--seed`: Reproducible random seed
  - Generated `extended_test_cases_10000.json`

### 🎯 Improvements
- NLP pipeline accuracy: **99.6%** on 1000 test cases (up from 93.8%)
- Import service automatically detects and handles both JSON formats
- Better test coverage and validation scripts

### 📝 Documentation
- Added `IMPORT_UPDATE.md` - detailed import feature documentation
- Updated `README.md` with new import capabilities
- Enhanced `BUILD.md` with version history

### 🐛 Bug Fixes
- Fixed import service to properly parse test case inputs through NLP
- Corrected method name from `parse()` to `process()` in NLP pipeline calls

### 📦 Technical
- File size: ~24.8 MB
- Dependencies: Python 3.12, PyInstaller 6.16.0
- Included: babel, underthesea, tkcalendar, ics

---

## Version 0.2 (2025-11-05)

### ✨ New Features
- **Time Period Semantics**: Business rules for Vietnamese time expressions
  - Noon (trưa) = 12:00, Midnight (nửa đêm) = 00:00
  - Morning/Afternoon/Evening/Night proper hour ranges
  - 12 giờ sáng → 00:00, 12 giờ chiều → 12:00
  - 1-5 giờ trưa → 13-17 hours

### 🎯 Improvements
- Increased "Lập lịch" input limit from 100 to **300 characters**
- Time validation test suite (8/8 passed)
- Stable NLP parser with edge case handling

### 📝 Documentation
- Added time period validation tests
- Documented known limitations

---

## Version 0.1 (2025-11-05)

### ✨ Initial Release
- Vietnamese NLP scheduling assistant
- Natural language input processing
- Calendar view with tkcalendar
- Event CRUD operations (Create, Read, Update, Delete)
- Reminder notifications (before + on-time)
- Export to JSON/ICS
- Import from JSON/ICS
- SQLite database backend
- Desktop GUI with Tkinter

### 🎯 Core Features
- Event extraction: Name, time, location, reminder
- Vietnamese time parsing: relative dates, periods, formats
- Search by content, ID, date, location
- Inline editing
- Background notification service

### 📦 Technical
- Python 3.12
- NLP accuracy: ~93.8% on initial test suite
- File size: ~24.7 MB
