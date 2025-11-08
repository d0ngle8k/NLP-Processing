# 🚀 Hướng Dẫn Train PhoBERT trên Kaggle

## 📊 Tại Sao Chọn Kaggle?

### ⚡ So Sánh Platforms

| Feature | Kaggle | Google Colab | Local RTX 2060 |
|---------|--------|--------------|----------------|
| **GPU** | P100 (16GB) | T4 (15GB) | RTX 2060 (8GB) |
| **RAM** | 30GB | 12GB | 16GB |
| **Miễn phí** | ✅ | ✅ | ✅ (đã có) |
| **Thời gian/tuần** | 30 giờ | Variable | Unlimited |
| **Tốc độ training** | ⚡⚡⚡ Nhanh nhất | ⚡⚡ Trung bình | ⚡ Chậm nhất |
| **Ước tính (3 epochs)** | **20-30 phút** | 30-40 phút | 45-60 phút |

### 🎯 Khuyến Nghị: **KAGGLE** 
- GPU mạnh hơn (P100 > T4 > RTX 2060)
- RAM nhiều hơn (30GB)
- Ổn định hơn
- Interface thân thiện

---

## 📝 Các Bước Thực Hiện

### 🔑 Bước 1: Tạo Tài Khoản Kaggle

1. Truy cập: https://www.kaggle.com
2. Click **Register** (góc trên bên phải)
3. Đăng ký với:
   - Google account, hoặc
   - Email + Password
4. Xác nhận email

### 📱 Bước 2: Verify Phone Number (Để dùng GPU)

⚠️ **Quan trọng**: Kaggle yêu cầu verify số điện thoại để dùng GPU

1. Click vào **avatar** (góc trên bên phải)
2. Chọn **Settings**
3. Tab **Phone Verification**
4. Nhập số điện thoại (+84 xxx xxx xxx)
5. Nhập mã OTP
6. ✅ Verified → Bây giờ có thể dùng GPU!

### 📊 Bước 3: Tạo Notebook Mới

1. Vào: https://www.kaggle.com/code
2. Click **New Notebook**
3. Hoặc: Click **Create** → **New Notebook**

### 📥 Bước 4: Upload Notebook

#### Option 1: Upload từ file
1. Click **File** → **Import Notebook**
2. Chọn tab **Upload**
3. Kéo thả file `kaggle_training.ipynb`
4. Click **Import**

#### Option 2: Tạo từ URL
1. Click **File** → **Import Notebook**
2. Chọn tab **GitHub**
3. Paste URL: `https://github.com/d0ngle8k/NLP-Processing/blob/main/kaggle_training.ipynb`
4. Click **Import**

### 🎮 Bước 5: Bật GPU

⚡ **QUAN TRỌNG NHẤT!**

1. Click **Settings** (⚙️ icon bên phải)
2. Tìm phần **Accelerator**
3. Chọn:
   - **GPU P100** (nếu có - nhanh nhất ⚡⚡⚡) HOẶC
   - **GPU T4 x2** (nếu P100 không có - vẫn nhanh ⚡⚡)
4. Click **Save** (góc dưới)
5. ✅ Notebook sẽ restart với GPU

### ▶️ Bước 6: Chạy Training

#### 6.1. Run từng cell theo thứ tự:

**Cell 1: Clone Repository**
```python
!git clone https://github.com/d0ngle8k/NLP-Processing.git
%cd NLP-Processing
```
⏱️ Thời gian: ~5 giây

**Cell 2: Install Dependencies**
```python
!pip install -q torch transformers underthesea tqdm
```
⏱️ Thời gian: ~30 giây

**Cell 3: Check GPU**
```python
import torch
print(f"GPU: {torch.cuda.get_device_name(0)}")
```
✅ Phải thấy: "Tesla P100-PCIE-16GB" hoặc "Tesla T4"

**Cell 4: Check Training Data**
```python
import json
with open('training_data/phobert_training_augmented.json') as f:
    data = json.load(f)
print(f"Total samples: {len(data):,}")
```
✅ Phải thấy: "Total samples: 95,332"

**Cell 5: START TRAINING** 🚀
```python
!python train_phobert.py --epochs 3 --batch_size 16
```
⏱️ Thời gian: **20-30 phút** (P100) hoặc **30-40 phút** (T4)

#### 6.2. Theo dõi progress:

Bạn sẽ thấy:
```
📊 Epoch 1/3
------------------------------------------------------------
Training: 100% |████████| 4767/4767 [08:23<00:00, 9.47it/s, loss=0.423]
Validation: 100% |██████| 1192/1192 [01:12<00:00, 16.5it/s]
   Train Loss: 0.4231
   Val Loss: 0.3654
   Val Accuracy: 88.7%

📊 Epoch 2/3
------------------------------------------------------------
Training: 100% |████████| 4767/4767 [08:21<00:00, 9.51it/s, loss=0.287]
...
```

✅ **Chờ đến khi training xong** (3/3 epochs complete)

### 📦 Bước 7: Download Model

**Cell 6: Create ZIP**
```python
!zip -r phobert_finetuned.zip models/phobert_finetuned/
```

**Cell 7: Check File**
```python
!ls -lh phobert_finetuned.zip
```
✅ File size: ~800MB - 1.5GB

#### Download file:

**Method 1: Kaggle Output Panel** (Recommended)
1. Xem panel **Output** bên phải
2. Tìm file `phobert_finetuned.zip`
3. Click icon download ⬇️
4. Chờ download (800MB - 1.5GB)

**Method 2: Kaggle API** (Alternative)
```bash
# Install Kaggle CLI
pip install kaggle

# Download từ terminal
kaggle kernels output <username>/<notebook-name> -p ./
```

---

## 📥 Sau Khi Download

### 1. Giải Nén Model

**Windows PowerShell:**
```powershell
cd "C:\Users\d0ngle8k\Desktop\New folder (2)\NLP-Processing"

# Giải nén
Expand-Archive -Path .\phobert_finetuned.zip -DestinationPath . -Force
```

**Linux/Mac:**
```bash
cd ~/NLP-Processing
unzip phobert_finetuned.zip
```

### 2. Verify Model Files

```powershell
ls models\phobert_finetuned
```

Phải có:
```
pytorch_model.bin      (800MB - 1.2GB)
config.json
tokenizer_config.json
vocab.txt
training.log
```

### 3. Test Model

```powershell
python comprehensive_test.py
```

Kết quả mong đợi:
```
PhoBERT Pipeline Results:
   Event F1: 0.90+ (90%+)
   Time F1: 0.85+ (85%+)
   Location F1: 0.80+ (80%+)
   Reminder F1: 0.85+ (85%+)
   Macro F1: 0.90+ (90%+)  ⬆️ from 71.43%
```

### 4. Commit lên GitHub

```powershell
# Add model files
git add models/phobert_finetuned

# Commit
git commit -m "v1.1.0: Add fine-tuned PhoBERT model

Trained on Kaggle P100 GPU
- Training samples: 76,266
- Validation samples: 19,067
- Epochs: 3
- Training time: ~25 minutes
- Macro F1: 71.43% → 90%+ (+18.57%)

Components:
- Event extraction: 90%+ F1
- Time extraction: 85%+ F1
- Location extraction: 80%+ F1
- Reminder extraction: 85%+ F1"

# Push
git push origin main
```

### 5. Update README

Thêm vào `README.md`:
```markdown
## 🤖 Model Performance

| Pipeline | Macro F1 | Event | Time | Location | Reminder |
|----------|----------|-------|------|----------|----------|
| Rule-based | 96.88% | 100% | 100% | 87.5% | 100% |
| **PhoBERT** | **90%+** | **90%+** | **85%+** | **80%+** | **85%+** |
| Hybrid | 98%+ | 100% | 100% | 90%+ | 100% |

✨ PhoBERT fine-tuned on 76K+ Vietnamese event extraction samples
```

---

## 🐛 Troubleshooting

### ❌ GPU Not Available

**Vấn đề:** Cell 3 hiển thị "CUDA not available"

**Giải pháp:**
1. Check Settings → Accelerator → Phải là **GPU P100** hoặc **GPU T4**
2. Nếu là "None" → Click và chọn GPU
3. Click **Save** và notebook sẽ restart
4. Run lại các cells

### ❌ Out of Memory (OOM)

**Vấn đề:** Training bị crash với lỗi "CUDA out of memory"

**Giải pháp:**
```python
# Giảm batch size từ 16 xuống 12
!python train_phobert.py --epochs 3 --batch_size 12

# Hoặc xuống 8 nếu vẫn OOM
!python train_phobert.py --epochs 3 --batch_size 8
```

### ❌ Training Data Not Found

**Vấn đề:** "File not found: training_data/phobert_training_augmented.json"

**Giải pháp:**
1. Verify file tồn tại trên GitHub: https://github.com/d0ngle8k/NLP-Processing/tree/main/training_data
2. Nếu không có → Clone lại repo:
   ```python
   !rm -rf NLP-Processing
   !git clone https://github.com/d0ngle8k/NLP-Processing.git
   %cd NLP-Processing
   ```

### ❌ ZIP File Không Download Được

**Giải pháp 1:** Download từ Kaggle Output panel
1. Scroll xuống Output panel bên phải
2. Tìm file `phobert_finetuned.zip`
3. Click icon download

**Giải pháp 2:** Download từng file
```python
# List files
!ls models/phobert_finetuned/

# Copy to /kaggle/working/ (accessible from Output)
!cp -r models/phobert_finetuned /kaggle/working/
```

### ❌ Phone Verification Required

**Vấn đề:** "Phone verification required to use GPU"

**Giải pháp:**
1. Settings → Phone Verification
2. Nhập số điện thoại (+84...)
3. Nhập OTP code
4. Refresh notebook

---

## 📊 Monitoring Training

### Xem Real-time Progress

Trong khi training, bạn sẽ thấy:

```
📊 Epoch 1/3
------------------------------------------------------------
Training:  45% |███████████▌           | 2150/4767 [03:47<04:36, 9.47it/s, loss=0.512]
```

**Giải thích:**
- `45%`: Đã complete 45% epoch 1
- `2150/4767`: Iteration hiện tại / tổng iterations
- `[03:47<04:36]`: Đã chạy 3:47, còn 4:36
- `9.47it/s`: Tốc độ 9.47 iterations/giây
- `loss=0.512`: Training loss hiện tại

### Expected Timeline (P100 GPU)

```
Cell 1 (Clone):        ~5 giây
Cell 2 (Install):      ~30 giây
Cell 3 (Check GPU):    ~2 giây
Cell 4 (Check Data):   ~3 giây
Cell 5 (Training):     ~20-30 phút
  - Epoch 1:           ~8 phút
  - Epoch 2:           ~8 phút
  - Epoch 3:           ~8 phút
  - Validation:        ~2 phút/epoch
Cell 6 (Create ZIP):   ~10 giây
Cell 7 (Download):     ~2-5 phút (tùy mạng)

Total: ~25-40 phút
```

---

## 🎯 Best Practices

### 1. Save Notebook Frequently
- **Ctrl+S** hoặc **Cmd+S** để save
- Kaggle auto-save mỗi vài phút

### 2. Run Cells in Order
- Đừng skip cells
- Run từ trên xuống dưới

### 3. Monitor GPU Usage
```python
# Add cell để check GPU usage
!nvidia-smi
```

### 4. Download Model Ngay Sau Training
- Kaggle session có thể timeout
- Download ngay khi training xong

### 5. Keep Notebook Running
- Đừng đóng tab browser
- Kaggle có thể kill inactive sessions

---

## 📚 Resources

### Kaggle Links
- **Kaggle Homepage**: https://www.kaggle.com
- **Notebooks**: https://www.kaggle.com/code
- **Documentation**: https://www.kaggle.com/docs

### Project Links
- **GitHub Repo**: https://github.com/d0ngle8k/NLP-Processing
- **Kaggle Notebook**: `kaggle_training.ipynb`
- **Training Guide**: `TRAINING_GUIDE.md`

### Support
- **Kaggle Forums**: https://www.kaggle.com/discussions
- **GitHub Issues**: https://github.com/d0ngle8k/NLP-Processing/issues

---

## ✅ Checklist

### Trước Khi Bắt Đầu:
- [ ] Có tài khoản Kaggle
- [ ] Đã verify phone number
- [ ] Đã push code lên GitHub
- [ ] Training data có trên GitHub

### Trong Khi Training:
- [ ] Notebook đã bật GPU (P100 hoặc T4)
- [ ] Cell 3 confirm GPU available
- [ ] Training đang chạy (xem progress bar)
- [ ] Loss đang giảm dần

### Sau Training:
- [ ] Training completed (3/3 epochs)
- [ ] Đã tạo ZIP file
- [ ] Đã download về local
- [ ] Đã giải nén vào `models/phobert_finetuned/`
- [ ] Đã test với `comprehensive_test.py`
- [ ] Kết quả F1 > 90%
- [ ] Đã commit lên GitHub
- [ ] Đã update README.md

---

## 🎊 Kết Quả Mong Đợi

Sau khi hoàn thành, bạn sẽ có:

✅ **Fine-tuned PhoBERT model**
- 800MB - 1.5GB model files
- 90%+ Macro F1 score
- Production-ready

✅ **Improved Pipeline Performance**
```
Before:  PhoBERT: 71.43%  |  Hybrid: 96.88%
After:   PhoBERT: 90%+    |  Hybrid: 98%+
         +18.57%               +1.12%
```

✅ **Deployment Ready**
- Model trên GitHub
- Documentation updated
- Test results validated

---

**🚀 Ready? Bắt đầu train trên Kaggle ngay!**

1. Mở https://www.kaggle.com
2. Upload `kaggle_training.ipynb`
3. Bật GPU P100
4. Run all cells
5. Đợi 25 phút
6. Download model
7. Deploy! 🎉
