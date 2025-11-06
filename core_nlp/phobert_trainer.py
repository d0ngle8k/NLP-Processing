"""
PhoBERT Fine-tuning Module for Event Extraction
Trains PhoBERT on Vietnamese event extraction task
"""
from __future__ import annotations
import json
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import re
from datetime import datetime

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import Dataset, DataLoader
    from torch.optim import AdamW
    from tqdm import tqdm
    from transformers import AutoTokenizer, AutoModel, get_linear_schedule_with_warmup
    TRANSFORMERS_AVAILABLE = True
except ImportError as e:
    TRANSFORMERS_AVAILABLE = False
    print(f"Warning: Could not import dependencies: {e}")


class EventExtractionDataset(Dataset):
    """
    Dataset for event extraction training
    Converts test cases to training examples
    """
    
    def __init__(self, data: List[Dict[str, Any]], tokenizer, max_length: int = 256):
        """
        Args:
            data: List of dicts with 'input' and 'expected' keys
            tokenizer: PhoBERT tokenizer
            max_length: Maximum sequence length
        """
        self.data = data
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self) -> int:
        return len(self.data)
    
    def __getitem__(self, idx: int) -> Dict[str, Any]:
        """
        Get a training example
        
        Returns:
            Dict with:
                - input_ids: [max_length]
                - attention_mask: [max_length]
                - has_event, has_time, has_location, has_reminder: int labels
        """
        item = self.data[idx]
        text = item['input']
        expected = item.get('expected', {})
        
        # Tokenize input
        encoding = self.tokenizer(
            text,
            padding='max_length',
            truncation=True,
            max_length=self.max_length,
            return_tensors='pt'
        )
        
        # Extract labels - flatten them to avoid collate issues
        has_event = 1 if expected.get('event') else 0
        has_time = 1 if expected.get('start_time') else 0
        has_location = 1 if expected.get('location') else 0
        has_reminder = 1 if expected.get('reminder_minutes', 0) > 0 else 0
        
        return {
            'input_ids': encoding['input_ids'].squeeze(0),
            'attention_mask': encoding['attention_mask'].squeeze(0),
            'has_event': torch.tensor(has_event, dtype=torch.long),
            'has_time': torch.tensor(has_time, dtype=torch.long),
            'has_location': torch.tensor(has_location, dtype=torch.long),
            'has_reminder': torch.tensor(has_reminder, dtype=torch.long),
        }


class PhoBERTEventClassifier(nn.Module):
    """
    PhoBERT-based classifier for event extraction
    Multi-task learning: detect event, time, location, reminder
    """
    
    def __init__(self, phobert_model, hidden_size: int = 768, dropout: float = 0.1):
        """
        Args:
            phobert_model: Pre-trained PhoBERT model
            hidden_size: Hidden dimension size
            dropout: Dropout rate
        """
        super().__init__()
        
        self.phobert = phobert_model
        self.dropout = nn.Dropout(dropout)
        
        # Classification heads for each entity type
        self.event_classifier = nn.Linear(hidden_size, 2)  # Binary: has event or not
        self.time_classifier = nn.Linear(hidden_size, 2)   # Binary: has time or not
        self.location_classifier = nn.Linear(hidden_size, 2)  # Binary: has location or not
        self.reminder_classifier = nn.Linear(hidden_size, 2)  # Binary: has reminder or not
        
    def forward(self, input_ids, attention_mask):
        """
        Forward pass
        
        Returns:
            Dict with logits for each classification task
        """
        # Get PhoBERT embeddings
        outputs = self.phobert(input_ids=input_ids, attention_mask=attention_mask)
        
        # Use CLS token representation
        cls_output = outputs.last_hidden_state[:, 0, :]  # [batch_size, hidden_size]
        cls_output = self.dropout(cls_output)
        
        # Classification heads
        event_logits = self.event_classifier(cls_output)
        time_logits = self.time_classifier(cls_output)
        location_logits = self.location_classifier(cls_output)
        reminder_logits = self.reminder_classifier(cls_output)
        
        return {
            'event': event_logits,
            'time': time_logits,
            'location': location_logits,
            'reminder': reminder_logits,
        }


class PhoBERTTrainer:
    """
    Trainer for fine-tuning PhoBERT on event extraction
    """
    
    def __init__(
        self,
        model_name: str = "vinai/phobert-base",
        device: str = None,
        learning_rate: float = 2e-5,
        batch_size: int = 16,
        num_epochs: int = 10,
        warmup_steps: int = 100,
        gradient_accumulation_steps: int = 1,
    ):
        """
        Initialize trainer
        
        Args:
            model_name: PhoBERT model name or path
            device: 'cpu' or 'cuda' (auto-detect if None)
            learning_rate: Learning rate
            batch_size: Batch size per GPU (effective batch = batch_size * gradient_accumulation_steps)
            num_epochs: Number of training epochs
            warmup_steps: Warmup steps for learning rate scheduler
            gradient_accumulation_steps: Accumulate gradients for larger effective batch size
        """
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError("transformers required. Install: pip install transformers torch")
        
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.learning_rate = learning_rate
        self.batch_size = batch_size
        self.num_epochs = num_epochs
        self.warmup_steps = warmup_steps
        
        # Gradient accumulation for effective larger batch size
        self.gradient_accumulation_steps = gradient_accumulation_steps or 1
        
        # Mixed precision training (FP16) for faster GPU training
        self.use_amp = self.device == "cuda"  # Only use AMP on GPU
        self.scaler = torch.cuda.amp.GradScaler() if self.use_amp else None
        
        print(f"🔧 Initializing PhoBERT Trainer on {self.device}")
        print(f"   Model: {model_name}")
        if self.device == "cuda":
            print(f"   🎮 GPU: {torch.cuda.get_device_name(0)}")
            print(f"   💾 GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
            print(f"   ⚡ Mixed Precision (FP16): Enabled")
        print(f"   📦 Batch Size: {batch_size}")
        print(f"   🔄 Gradient Accumulation: {self.gradient_accumulation_steps} steps")
        print(f"   📈 Effective Batch Size: {batch_size * self.gradient_accumulation_steps}")
        
        # Load tokenizer and base model
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        phobert_base = AutoModel.from_pretrained(model_name)
        
        # Create classifier model
        self.model = PhoBERTEventClassifier(phobert_base).to(self.device)
        
        # Loss function
        self.criterion = nn.CrossEntropyLoss()
        
        print("✅ Trainer initialized")
    
    def load_data_from_test_cases(self, test_file: str) -> Tuple[List[Dict], List[Dict]]:
        """
        Load and split test cases into train/val sets
        
        Args:
            test_file: Path to test cases JSON file
            
        Returns:
            (train_data, val_data)
        """
        print(f"📂 Loading test cases from {test_file}")
        
        with open(test_file, 'r', encoding='utf-8') as f:
            test_cases = json.load(f)
        
        # Shuffle and split 80/20
        import random
        random.shuffle(test_cases)
        split_idx = int(len(test_cases) * 0.8)
        
        train_data = test_cases[:split_idx]
        val_data = test_cases[split_idx:]
        
        print(f"   Training samples: {len(train_data)}")
        print(f"   Validation samples: {len(val_data)}")
        
        return train_data, val_data
    
    def train(
        self,
        train_data: List[Dict],
        val_data: List[Dict],
        save_dir: str = "./models/phobert_finetuned",
    ):
        """
        Train the model
        
        Args:
            train_data: Training examples
            val_data: Validation examples
            save_dir: Directory to save the trained model
        """
        print("\n" + "="*60)
        print("🚀 Starting PhoBERT Fine-tuning")
        print("="*60)
        
        # Create datasets
        train_dataset = EventExtractionDataset(train_data, self.tokenizer)
        val_dataset = EventExtractionDataset(val_data, self.tokenizer)
        
        # Create dataloaders
        train_loader = DataLoader(
            train_dataset,
            batch_size=self.batch_size,
            shuffle=True,
            num_workers=0  # Windows compatibility
        )
        val_loader = DataLoader(
            val_dataset,
            batch_size=self.batch_size,
            shuffle=False,
            num_workers=0
        )
        
        # Optimizer and scheduler
        optimizer = AdamW(self.model.parameters(), lr=self.learning_rate)
        total_steps = len(train_loader) * self.num_epochs
        scheduler = get_linear_schedule_with_warmup(
            optimizer,
            num_warmup_steps=self.warmup_steps,
            num_training_steps=total_steps
        )
        
        # Training loop
        best_val_loss = float('inf')
        
        for epoch in range(self.num_epochs):
            print(f"\n📊 Epoch {epoch + 1}/{self.num_epochs}")
            print("-" * 60)
            
            # Train
            train_loss = self._train_epoch(train_loader, optimizer, scheduler)
            print(f"   Training Loss: {train_loss:.4f}")
            
            # Validate
            val_loss, val_acc = self._validate_epoch(val_loader)
            print(f"   Validation Loss: {val_loss:.4f}")
            print(f"   Validation Accuracy: {val_acc:.2%}")
            
            # Save best model
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                self._save_model(save_dir)
                print(f"   ✅ Best model saved to {save_dir}")
        
        print("\n" + "="*60)
        print("✅ Training completed!")
        print(f"📁 Model saved to: {save_dir}")
        print("="*60)
    
    def _train_epoch(self, dataloader: DataLoader, optimizer, scheduler) -> float:
        """Train for one epoch with mixed precision and gradient accumulation"""
        self.model.train()
        total_loss = 0
        
        progress_bar = tqdm(dataloader, desc="Training")
        optimizer.zero_grad()  # Initialize gradients
        
        for batch_idx, batch in enumerate(progress_bar):
            # Move to device
            input_ids = batch['input_ids'].to(self.device)
            attention_mask = batch['attention_mask'].to(self.device)
            
            # Mixed precision forward pass
            if self.use_amp:
                with torch.cuda.amp.autocast():
                    # Forward pass
                    outputs = self.model(input_ids, attention_mask)
                    
                    # Calculate loss for each task
                    loss = 0
                    for task in ['event', 'time', 'location', 'reminder']:
                        task_labels = batch[f'has_{task}'].to(self.device)
                        task_loss = self.criterion(outputs[task], task_labels)
                        loss += task_loss
                    
                    # Scale loss for gradient accumulation
                    loss = loss / self.gradient_accumulation_steps
                
                # Backward pass with scaled gradients
                self.scaler.scale(loss).backward()
                
                # Update weights every N accumulation steps
                if (batch_idx + 1) % self.gradient_accumulation_steps == 0:
                    self.scaler.unscale_(optimizer)
                    torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
                    self.scaler.step(optimizer)
                    self.scaler.update()
                    scheduler.step()
                    optimizer.zero_grad()
            else:
                # Standard training (CPU or without AMP)
                outputs = self.model(input_ids, attention_mask)
                
                # Calculate loss for each task
                loss = 0
                for task in ['event', 'time', 'location', 'reminder']:
                    task_labels = batch[f'has_{task}'].to(self.device)
                    task_loss = self.criterion(outputs[task], task_labels)
                    loss += task_loss
                
                # Scale loss for gradient accumulation
                loss = loss / self.gradient_accumulation_steps
                loss.backward()
                
                # Update weights every N accumulation steps
                if (batch_idx + 1) % self.gradient_accumulation_steps == 0:
                    torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
                    optimizer.step()
                    scheduler.step()
                    optimizer.zero_grad()
            
            total_loss += loss.item() * self.gradient_accumulation_steps
            progress_bar.set_postfix({'loss': loss.item() * self.gradient_accumulation_steps})
        
        return total_loss / len(dataloader)
    
    def _validate_epoch(self, dataloader: DataLoader) -> Tuple[float, float]:
        """Validate for one epoch"""
        self.model.eval()
        total_loss = 0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for batch in tqdm(dataloader, desc="Validation"):
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                
                # Forward pass
                outputs = self.model(input_ids, attention_mask)
                
                # Calculate loss
                loss = 0
                for task in ['event', 'time', 'location', 'reminder']:
                    task_labels = batch[f'has_{task}'].to(self.device)
                    task_loss = self.criterion(outputs[task], task_labels)
                    loss += task_loss
                    
                    # Calculate accuracy
                    predictions = torch.argmax(outputs[task], dim=1)
                    correct += (predictions == task_labels).sum().item()
                    total += len(task_labels)
                
                total_loss += loss.item()
        
        avg_loss = total_loss / len(dataloader)
        accuracy = correct / total if total > 0 else 0
        
        return avg_loss, accuracy
    
    def _save_model(self, save_dir: str):
        """Save the trained model"""
        save_path = Path(save_dir)
        save_path.mkdir(parents=True, exist_ok=True)
        
        # Save model
        torch.save(self.model.state_dict(), save_path / "model.pt")
        
        # Save tokenizer
        self.tokenizer.save_pretrained(save_path)
        
        # Save config
        config = {
            'model_type': 'phobert_event_extractor',
            'trained_date': datetime.now().isoformat(),
            'num_epochs': self.num_epochs,
            'learning_rate': self.learning_rate,
            'batch_size': self.batch_size,
        }
        with open(save_path / "config.json", 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)


def train_phobert_from_test_cases(
    test_file: str = "./tests/extended_test_cases.json",
    output_dir: str = "./models/phobert_finetuned",
    num_epochs: int = 10,
    batch_size: int = 16,
    gradient_accumulation_steps: int = 1,
):
    """
    Convenience function to train PhoBERT from test cases
    
    Args:
        test_file: Path to test cases JSON
        output_dir: Output directory for trained model
        num_epochs: Number of training epochs
        batch_size: Batch size per GPU
        gradient_accumulation_steps: Gradient accumulation steps
    """
    # Initialize trainer
    trainer = PhoBERTTrainer(
        num_epochs=num_epochs,
        batch_size=batch_size,
        gradient_accumulation_steps=gradient_accumulation_steps,
    )
    
    # Load data
    train_data, val_data = trainer.load_data_from_test_cases(test_file)
    
    # Train
    trainer.train(train_data, val_data, save_dir=output_dir)
    
    print("\n✅ Training completed!")
    print(f"📁 Model saved to: {output_dir}")
    print(f"\n💡 To use the trained model:")
    print(f"   from core_nlp.phobert_model import PhoBERTNLPPipeline")
    print(f"   pipeline = PhoBERTNLPPipeline(model_path='{output_dir}')")


if __name__ == '__main__':
    # Example: Train from extended test cases
    train_phobert_from_test_cases(
        test_file="./tests/extended_test_cases.json",
        output_dir="./models/phobert_finetuned",
        num_epochs=15,
        batch_size=8,
    )
