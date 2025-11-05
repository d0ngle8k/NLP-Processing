# Hướng dẫn Build EXE

## Yêu cầu
- **Python 3.12.0** from python.org (KHÔNG dùng msys64 Python)
- Virtual environment với dependencies từ `requirements.txt`
- PyInstaller 6.16.0+ trong venv

## ⚠️ Quan trọng: Python Environment

**PHẢI dùng Standard Windows Python:**
```powershell
# Download từ: https://www.python.org/downloads/
# Cài đặt với options:
# ✅ Add to PATH
# ✅ Include tcl/tk (tkinter)
# ✅ Include pip
```

**KHÔNG dùng:**
- ❌ msys64 Python (SSL certificate issues)
- ❌ Python embeddable (thiếu tkinter)
- ❌ Anaconda/Miniconda (package conflicts)

## Phiên bản hiện tại

**v0.6** (Latest) ✅ PRODUCTION - Build: 2025-11-05
- **Statistics Dashboard ENABLED**: matplotlib, reportlab, underthesea
- 5 tabs analytics: Overview, Time, Location, Event Type, Trend
- PDF/Excel export với Vietnamese support
- 111.91 MB (tăng từ 24.76 MB do scientific packages)
- 99.61% NLP accuracy maintained
- Environment fixed: Standard Windows Python 3.12.0

**v0.5** - Build: 2025-11-05
- Nút "Xóa tất cả lịch" với xác nhận 2 lớp bảo mật
- 99.61% accuracy trên 100,000 test cases
- Database reset với ID counter restart
- 24.76 MB (no matplotlib)

## Setup Environment (First Time)

### 1. Install Standard Python
```powershell
# Download Python 3.12.0 installer
Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe" -OutFile "$env:TEMP\python-installer.exe"

# Install silently
& "$env:TEMP\python-installer.exe" /quiet InstallAllUsers=0 PrependPath=1 Include_tcltk=1 Include_launcher=1

# Verify installation
python --version  # Should show: Python 3.12.0
```

### 2. Create Virtual Environment
```powershell
# Navigate to project
cd C:\Users\d0ngle8k\Desktop\NLP-Processing

# Create venv with standard Python
python -m venv venv

# Activate venv (NOTE: Scripts\ not bin\)
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```powershell
# Upgrade pip first
python -m pip install --upgrade pip

# Install all packages (pre-built wheels)
pip install -r requirements.txt

# Verify critical packages
python -c "import matplotlib; print('matplotlib:', matplotlib.__version__)"
python -c "import reportlab; print('reportlab:', reportlab.Version)"
python -c "import underthesea; print('underthesea:', underthesea.__version__)"
```

## Build file .exe

### Cách 1: Sử dụng file spec (RECOMMENDED cho v0.6)

```powershell
# Kích hoạt virtual environment
.\venv\Scripts\Activate.ps1

# Build từ file spec (version 0.6 - latest with statistics)
python -m PyInstaller TroLyLichTrinh0.6.spec --clean --noconfirm

# Hoặc version 0.5 (without statistics)
python -m PyInstaller TroLyLichTrinh0.5.spec
```

### Cách 2: PyInstaller command line (v0.6)

```powershell
.\venv\Scripts\Activate.ps1

python -m PyInstaller --name="TroLyLichTrinh0.6" ^
  --onefile --windowed --noconfirm --clean ^
  --add-data "database/schema.sql;database" ^
  --hidden-import="babel.numbers" ^
  --hidden-import="underthesea" ^
  --hidden-import="tkcalendar" ^
  --hidden-import="matplotlib" ^
  --hidden-import="matplotlib.backends.backend_tkagg" ^
  --hidden-import="reportlab" ^
  --hidden-import="openpyxl" ^
  --hidden-import="scipy" ^
  --hidden-import="sklearn" ^
  --collect-data="underthesea" ^
  --collect-data="tkcalendar" ^
  --collect-data="matplotlib" ^
  main.py
```

## Kết quả

File executable sẽ được tạo tại:
- `dist/TroLyLichTrinh0.6.exe` - **111.91 MB** (with statistics dashboard)
- `dist/TroLyLichTrinh0.5.exe` - 24.76 MB (without statistics)

## Build Time

- **v0.6**: ~2 phút (do nhiều packages: matplotlib, scipy, sklearn)
- **v0.5**: ~30 giây (chỉ basic packages)

## Version History

- **v0.6** (2025-11-05): Statistics dashboard ENABLED + matplotlib + PDF/Excel export + 111.91 MB
- **v0.5** (2025-11-05): "Xóa tất cả" button + 99.61% accuracy on 100k tests + database reset + 24.76 MB
- **v0.4** (2025-11-05): Vertical & horizontal scrollbars + responsive grid layout
- **v0.3** (2025-11-05): Import test case format + 10k test generator + 99.6% NLP accuracy
- **v0.2** (2025-11-05): Time period semantics + UI input limit 300 chars
- **v0.1** (2025-11-05): Initial release with basic NLP + calendar + reminders

## Chạy ứng dụng

Chỉ cần double-click vào file .exe trong thư mục `dist/`:
- **TroLyLichTrinh0.6.exe** - Full version với statistics dashboard
- **TroLyLichTrinh0.5.exe** - Lightweight version

## Lưu ý

### General
- File .exe là standalone, có thể chạy trên máy Windows khác mà không cần cài Python
- Database sẽ được tạo tự động khi chạy lần đầu
- File schema.sql đã được embed vào trong .exe
- Các thư viện NLP (underthesea, babel) đã được bao gồm

### Version 0.6 Specific
- **Kích thước lớn** (111.91 MB) do bao gồm:
  - matplotlib (~30 MB): Chart generation
  - scipy (~25 MB): Scientific computing
  - scikit-learn (~20 MB): Machine learning
  - numpy (~15 MB): Numerical operations
  - Plus: reportlab, openpyxl, pillow, fonttools
- **Lần đầu mở**: Có thể mất 5-10 giây để decompress
- **Statistics tab**: Tính toán có thể mất 2-3 giây với nhiều events
- **Export PDF/Excel**: Yêu cầu write permission trong thư mục

### Troubleshooting

**Nếu "📊 Thống kê" button không hiện:**
```powershell
# Verify build includes matplotlib
python -c "import PyInstaller.utils.hooks as hooks; print(hooks.collect_data_files('matplotlib'))"
```

**Nếu build fails với hidden imports:**
- Kiểm tra `TroLyLichTrinh0.6.spec` có đầy đủ hiddenimports
- Chạy với `--debug=imports` để xem missing modules

**Nếu EXE crash khi mở statistics:**
- Check Windows Event Viewer → Application logs
- Run từ terminal để xem error messages:
  ```powershell
  .\dist\TroLyLichTrinh0.6.exe
  ```
