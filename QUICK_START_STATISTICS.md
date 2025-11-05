# 🚀 Quick Start: Enable Statistics Dashboard

## ⚡ 5-Minute Setup

### Step 1: Check Current Python
```powershell
# Check which Python you're using
python --version
python -c "import sys; print(sys.executable)"

# If it shows C:\msys64\... → You need standard Python
# If it shows C:\Users\...\Python312\... → You're good!
```

### Step 2: Install Standard Python (if needed)
1. Go to https://www.python.org/downloads/
2. Download **Python 3.12.x** (latest stable)
3. Run installer:
   - ✅ **CHECK** "Add Python to PATH"
   - ✅ Install for all users (recommended)
4. Verify: Open new PowerShell
   ```powershell
   python --version  # Should show Python 3.12.x
   ```

### Step 3: Backup & Recreate Environment
```powershell
# Navigate to project
cd C:\Users\d0ngle8k\Desktop\NLP-Processing

# Backup (optional but recommended)
Copy-Item -Recurse . ..\NLP-Processing-backup

# Remove old venv
Remove-Item -Recurse -Force venv

# Create new venv with standard Python
python -m venv venv

# Activate
.\venv\Scripts\Activate.ps1

# Install all dependencies
pip install -r requirements.txt
```

### Step 4: Verify Statistics Libraries
```powershell
python -c "import matplotlib; print('✅ matplotlib:', matplotlib.__version__)"
python -c "import reportlab; print('✅ reportlab:', reportlab.Version)"
python -c "import underthesea; print('✅ underthesea:', underthesea.__version__)"
```

**Expected Output**:
```
✅ matplotlib: 3.10.7
✅ reportlab: 4.4.4
✅ underthesea: 7.0.1
```

### Step 5: Run Application
```powershell
python main.py
```

**Success Indicators**:
- ✅ No warning about matplotlib
- ✅ "📊 Thống kê" button appears on toolbar
- ✅ Can click button and see statistics dialog

---

## 🎯 Test Statistics Dashboard

### 1. Add Sample Events
Use NLP to create test data:
```
Họp team 10h sáng mai ở văn phòng
Ăn trưa 12h với khách hàng ở nhà hàng ABC
Gym 6h chiều ở phòng tập
Học tiếng Anh 8h tối
```

Or import test file:
```powershell
# Use provided test cases
python -c "from services.import_service import *; from database.db_manager import *; import_from_json('./tests/test_cases.json', DatabaseManager('./database/schedule.db'))"
```

### 2. Open Statistics
1. Click **📊 Thống kê** button
2. Wait 2-3 seconds (calculating stats)
3. Dialog opens with 5 tabs

### 3. Explore Tabs
- **📊 Tổng quan**: Overview numbers
- **⏰ Thời gian**: 
  - Theo ngày: Weekday distribution
  - Theo giờ: Hourly distribution
  - Tóm tắt: Peak times
- **📍 Địa điểm**: Top locations bar chart
- **🏷️ Phân loại**: Event categories pie chart
- **📈 Xu hướng**: 4-week trend line

### 4. Test Export
1. Click **📄 Xuất PDF**
   - Save to Desktop
   - Open PDF → verify report
2. Click **📊 Xuất Excel**
   - Save to Desktop
   - Open in Excel → check 4 sheets

---

## 🐛 Troubleshooting

### Issue: "matplotlib not installed" warning still shows

**Check 1**: Verify venv is activated
```powershell
# Should show (venv) at prompt
Get-Command python | Select-Object Source
# Should show: ...\NLP-Processing\venv\Scripts\python.exe
```

**Check 2**: Reinstall packages
```powershell
pip uninstall matplotlib reportlab underthesea -y
pip install matplotlib reportlab underthesea
```

**Check 3**: Try with --no-cache
```powershell
pip install --no-cache-dir matplotlib reportlab underthesea
```

### Issue: Import errors when running main.py

**Error**: `ModuleNotFoundError: No module named 'tkcalendar'`

**Solution**:
```powershell
pip install -r requirements.txt
```

### Issue: Charts don't render

**Error**: `RuntimeError: Failed to create PkgConfig...`

**Solution**: Matplotlib backend issue
```powershell
# Edit main.py, change:
matplotlib.use('TkAgg')  # to
matplotlib.use('Agg')    # if TkAgg fails
```

### Issue: PDF export fails

**Error**: `ImportError: cannot import name 'getSampleStyleSheet'`

**Solution**:
```powershell
pip install --upgrade reportlab
```

### Issue: Excel export fails

**Error**: `ModuleNotFoundError: No module named 'openpyxl'`

**Solution**:
```powershell
pip install openpyxl
```

---

## 📝 Notes

### Performance
- First statistics load: 2-3 seconds
- Subsequent loads: ~1 second (data cached in dialog)
- Large datasets (10k+ events): May take 5-10 seconds

### Limitations
- Statistics calculated on-demand (no persistent cache)
- Charts regenerated each time dialog opens
- Max events tested: 100,000 (works fine but slow)

### Tips
1. **Close dialog before adding events** - No auto-refresh yet
2. **Reopen dialog to see updated stats**
3. **Use date filters** (future feature) for better performance
4. **Export reports regularly** for historical tracking

---

## 🎓 Advanced Usage

### Custom Date Range (Future Feature)
Will allow filtering statistics by date range:
```python
# Not implemented yet
stats = stats_service.get_comprehensive_stats(
    start_date='2025-01-01',
    end_date='2025-12-31'
)
```

### Scheduled Reports (Future Feature)
Will auto-generate monthly reports:
```python
# Not implemented yet
stats_service.schedule_monthly_report(
    email='user@example.com',
    format='pdf'
)
```

---

## ✅ Verification Checklist

Before reporting issues, verify:

- [ ] Standard Python 3.12.x installed (not msys64)
- [ ] Virtual environment activated
- [ ] All requirements.txt packages installed
- [ ] matplotlib import works in Python
- [ ] reportlab import works in Python
- [ ] underthesea import works in Python
- [ ] Application starts without errors
- [ ] "📊 Thống kê" button visible
- [ ] At least 5 events in database
- [ ] Statistics dialog opens
- [ ] All 5 tabs show content
- [ ] Charts render correctly
- [ ] PDF export works
- [ ] Excel export works

---

## 📞 Support

If statistics still don't work after following this guide:

1. Check `STATISTICS_README.md` for detailed documentation
2. Review `V0.6_IMPLEMENTATION_SUMMARY.md` for technical details
3. Ensure no firewalls blocking matplotlib
4. Try running as Administrator (Windows UAC)
5. Check Event Viewer for Python errors

---

**Last Updated**: 2025-11-05  
**Version**: 0.6  
**Estimated Setup Time**: 5-10 minutes
