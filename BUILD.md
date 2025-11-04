# Hướng dẫn Build EXE

## Yêu cầu
- Python 3.12+ với venv đã cài đặt dependencies từ `requirements.txt`
- PyInstaller đã được cài đặt trong venv

## Build file .exe

### Cách 1: Sử dụng lệnh PyInstaller trực tiếp

```powershell
# Kích hoạt virtual environment
& C:/Users/d0ngle8k/Desktop/NLP-Processing/venv/bin/Activate.ps1

# Build file .exe
python -m PyInstaller --name="TroLyLichTrinh" --onefile --windowed --add-data "database/schema.sql;database" --hidden-import="babel.numbers" --hidden-import="underthesea" --hidden-import="tkcalendar" main.py
```

### Cách 2: Sử dụng file spec có sẵn (nếu đã được tạo)

```powershell
# Kích hoạt virtual environment
& C:/Users/d0ngle8k/Desktop/NLP-Processing/venv/bin/Activate.ps1

# Build từ file spec
python -m PyInstaller TroLyLichTrinh.spec
```

## Kết quả

File executable sẽ được tạo tại: `dist/TroLyLichTrinh.exe`

Kích thước: ~25 MB

## Chạy ứng dụng

Chỉ cần double-click vào `TroLyLichTrinh.exe` trong thư mục `dist/`

## Lưu ý

- File .exe là standalone, có thể chạy trên máy Windows khác mà không cần cài Python
- Database sẽ được tạo tự động khi chạy lần đầu
- File schema.sql đã được embed vào trong .exe
- Các thư viện NLP (underthesea, babel) đã được bao gồm
