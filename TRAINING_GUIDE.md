# 🚀 Hướng Dẫn Fine-tune PhoBERT

## 📊 Tổng Quan

File này hướng dẫn fine-tune PhoBERT model để cải thiện event extraction accuracy.

### 📈 Hiệu Suất Hiện Tại
- **Rule-based**: 96.88% Macro F1
- **PhoBERT (base)**: 71.43% Macro F1 ❌
- **Hybrid**: 96.88% Macro F1 (dựa vào rule-based)

### 🎯 Mục Tiêu Sau Fine-tuning
- **PhoBERT (fine-tuned)**: 90%+ Macro F1 ✅
- **Hybrid**: 98%+ Macro F1 ✅

---

## 🛠️ Phương Pháp 1: Google Colab (Khuyến nghị ⭐)

### ✅ Ưu điểm
- **Miễn phí T4 GPU** (15GB VRAM)
- **Nhanh hơn CPU 50x**: ~30-60 phút thay vì 51 giờ
- Không cần cài đặt CUDA local

### 📝 Các Bước

#### 1. Mở Google Colab
- Truy cập: https://colab.research.google.com
- File → Upload notebook → Chọn `colab_training.ipynb`

#### 2. Bật GPU
- Runtime → Change runtime type
- Hardware accelerator → **T4 GPU**
- Save

#### 3. Chạy từng cell
```python
# Cell 1: Clone repo
!git clone https://github.com/d0ngle8k/NLP-Processing.git
%cd NLP-Processing

# Cell 2: Install dependencies
!pip install -q torch transformers underthesea tqdm

# Cell 3: Check GPU
import torch
print(f"GPU: {torch.cuda.get_device_name(0)}")

# Cell 4: Training (30-60 phút)
!python train_phobert.py --epochs 3 --batch_size 16

# Cell 5: Download model
!zip -r phobert_finetuned.zip models/phobert_finetuned
from google.colab import files
files.download('phobert_finetuned.zip')
```

#### 4. Sau khi download
```bash
# Giải nén vào thư mục models/
unzip phobert_finetuned.zip

# Test model
python comprehensive_test.py

# Commit
git add models/phobert_finetuned
git commit -m "v1.1.0: Add fine-tuned PhoBERT model"
git push
```

---

## 💻 Phương Pháp 2: Local Training (Chậm ⚠️)

### ⚙️ Yêu Cầu
- **GPU**: NVIDIA GPU với CUDA support
- **RAM**: 16GB+
- **Storage**: 5GB+ free space

### 📝 Các Bước

#### 1. Cài đặt CUDA (nếu có GPU)
```powershell
# Check GPU
nvidia-smi

# Install PyTorch với CUDA
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

#### 2. Training
```powershell
# Full training (3 epochs)
python train_phobert.py --epochs 3 --batch_size 16

# Hoặc test với dataset nhỏ hơn
python train_phobert.py --epochs 1 --batch_size 8
```

#### 3. Monitor Progress
```powershell
# Terminal khác
python monitor_training.py
```

### ⏱️ Thời Gian Ước Tính
- **CPU**: ~51 giờ (3 epochs) ❌
- **GPU (RTX 3060)**: ~2-3 giờ (3 epochs) ⚡
- **GPU (RTX 4090)**: ~30-60 phút (3 epochs) ⚡⚡

---

## 📊 Training Data

### 📁 Datasets
```
training_data/
├── phobert_training_augmented.json  (95K+ samples) ← Sử dụng file này
├── phobert_train.json               (772K samples, too large)
└── phobert_validation.json          (85K samples)
```

### 📈 Dataset Statistics
- **Training**: 76,266 samples
- **Validation**: 19,067 samples
- **Coverage**: Week/month reminders, location conflicts, edge cases

---

## 🎛️ Training Options

### Command Line Arguments
```bash
python train_phobert.py [OPTIONS]

Options:
  --epochs INT          Number of epochs (default: 5)
  --batch_size INT      Batch size (default: 16, giảm xuống 8 hoặc 4 nếu OOM)
  --lr FLOAT           Learning rate (default: 2e-5)
  --output PATH        Output directory (default: ./models/phobert_finetuned)
  --skip_checks        Skip requirement checks
```

### Examples
```bash
# Basic (recommended)
python train_phobert.py --epochs 3 --batch_size 16

# Custom learning rate
python train_phobert.py --epochs 5 --lr 1e-5

# Small batch for limited GPU
python train_phobert.py --epochs 3 --batch_size 4

# Save to custom location
python train_phobert.py --output ./my_models/phobert_v2
```

---

## 📊 Monitoring Training

### Real-time Progress
```powershell
# Terminal 1: Training
python train_phobert.py --epochs 3 --batch_size 16

# Terminal 2: Monitor
python monitor_training.py
```

### Training Logs
```
models/phobert_finetuned/
├── training.log          # Training progress
├── pytorch_model.bin     # Model weights
├── config.json          # Model config
└── tokenizer files...
```

### Expected Output
```
📊 Epoch 1/3
Training: 100% |████████████| 9534/9534 [30:21, 5.23it/s, loss=0.45]
Validation: 100% |██████████| 2384/2384 [03:12, 12.4it/s]
   Train Loss: 0.4532
   Val Loss: 0.3821
   Val Accuracy: 89.3%
```

---

## ✅ Testing Fine-tuned Model

### Run Tests
```powershell
# Test all pipelines
python comprehensive_test.py
```

### Expected Improvements
| Component | Before (base) | After (fine-tuned) | Improvement |
|-----------|---------------|-------------------|-------------|
| Event     | 0% F1         | 90%+ F1          | +90%        |
| Time      | 0% F1         | 85%+ F1          | +85%        |
| Location  | 0% F1         | 80%+ F1          | +80%        |
| Reminder  | 0% F1         | 85%+ F1          | +85%        |
| **Macro F1** | **71.43%** | **90%+**        | **+18.57%** |

---

## 🐛 Troubleshooting

### Out of Memory (OOM)
```bash
# Giảm batch size
python train_phobert.py --batch_size 4

# Hoặc dùng gradient accumulation (trong code)
```

### CUDA Not Available
```powershell
# Check CUDA
python -c "import torch; print(torch.cuda.is_available())"

# Install CUDA version of PyTorch
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

### Slow Training
```
✅ Sử dụng Google Colab với T4 GPU (miễn phí)
✅ Giảm dataset size cho testing
✅ Increase batch_size nếu có GPU memory
```

### Import Errors
```powershell
# Reinstall dependencies
pip install torch transformers underthesea tqdm
```

---

## 📦 Model Deployment

### 1. Save Model
Model tự động save tại: `./models/phobert_finetuned/`

### 2. Use in Pipeline
```python
from core_nlp.hybrid_pipeline import HybridPipeline

# Load fine-tuned model
pipeline = HybridPipeline(model_path="./models/phobert_finetuned")

# Extract event
result = pipeline.extract("mai 8h họp ở phòng 302")
print(result)
```

### 3. Git Commit
```bash
# Add model files
git add models/phobert_finetuned

# Commit
git commit -m "v1.1.0: Add fine-tuned PhoBERT model

- Trained on 76K+ augmented samples
- Improved Macro F1: 71.43% → 90%+
- Full week/month reminder support"

# Push
git push
```

---

## 📚 Resources

### Documentation
- **PhoBERT Paper**: https://arxiv.org/abs/2003.00744
- **Transformers Docs**: https://huggingface.co/docs/transformers
- **Training Guide**: `core_nlp/phobert_trainer.py`

### Files
- **Training Script**: `train_phobert.py`
- **Colab Notebook**: `colab_training.ipynb`
- **Monitor Script**: `monitor_training.py`
- **Test Script**: `comprehensive_test.py`

### Support
- GitHub Issues: https://github.com/d0ngle8k/NLP-Processing/issues
- Training Logs: `models/phobert_finetuned/training.log`

---

## 🎯 Next Steps

1. ✅ **Bật GPU trên Colab** (nếu dùng Colab)
2. ✅ **Run training** với `train_phobert.py`
3. ✅ **Download model** từ Colab
4. ✅ **Test improvements** với `comprehensive_test.py`
5. ✅ **Commit to Git** và deploy

**Estimated Total Time**: 30-60 phút (Colab GPU) hoặc 2-3 giờ (Local GPU)

Good luck! 🚀
