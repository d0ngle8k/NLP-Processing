from pathlib import Path
from transformers import AutoTokenizer, AutoModel

TARGET_DIR = Path('./models/phobert_base')
TARGET_DIR.mkdir(parents=True, exist_ok=True)

print('🔽 Downloading PhoBERT base (vinai/phobert-base) ...')

# Download from HF and save locally for offline usage
tokenizer = AutoTokenizer.from_pretrained('vinai/phobert-base')
model = AutoModel.from_pretrained('vinai/phobert-base')

print(f'💾 Saving model and tokenizer to {TARGET_DIR.resolve()}')

tokenizer.save_pretrained(TARGET_DIR)
model.save_pretrained(TARGET_DIR)

print('✅ PhoBERT base downloaded and cached locally.')
