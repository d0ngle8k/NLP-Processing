"""
PhoBERT Fine-tuning Script
Optimized for event extraction from Vietnamese text

Usage:
    python train_phobert.py --epochs 5 --batch_size 16
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def check_requirements():
    """Check if all required packages are installed"""
    missing = []
    
    try:
        import torch
        print(f"✅ PyTorch {torch.__version__}")
        if torch.cuda.is_available():
            print(f"✅ CUDA available: {torch.cuda.get_device_name(0)}")
        else:
            print("⚠️  CUDA not available - training will use CPU (slower)")
    except ImportError:
        missing.append("torch")
    
    try:
        import transformers
        print(f"✅ Transformers {transformers.__version__}")
    except ImportError:
        missing.append("transformers")
    
    try:
        import underthesea
        print(f"✅ Underthesea {underthesea.__version__}")
    except ImportError:
        missing.append("underthesea")
    
    if missing:
        print(f"\n❌ Missing packages: {', '.join(missing)}")
        print("\n📦 Install with:")
        print("   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")
        print("   pip install transformers underthesea")
        return False
    
    return True


def check_training_data():
    """Check if training data exists"""
    train_file = Path("training_data/phobert_train.json")
    val_file = Path("training_data/phobert_validation.json")
    
    if not train_file.exists():
        print(f"❌ Training data not found: {train_file}")
        return False
    
    if not val_file.exists():
        print(f"❌ Validation data not found: {val_file}")
        return False
    
    # Check file sizes
    train_size = train_file.stat().st_size / (1024 * 1024)  # MB
    val_size = val_file.stat().st_size / (1024 * 1024)  # MB
    
    print(f"✅ Training data: {train_file} ({train_size:.1f} MB)")
    print(f"✅ Validation data: {val_file} ({val_size:.1f} MB)")
    
    return True


def train_model(
    epochs: int = 5,
    batch_size: int = 16,
    learning_rate: float = 2e-5,
    output_dir: str = "./models/phobert_finetuned"
):
    """
    Fine-tune PhoBERT model
    
    Args:
        epochs: Number of training epochs (default: 5)
        batch_size: Batch size (default: 16, reduce if OOM)
        learning_rate: Learning rate (default: 2e-5)
        output_dir: Directory to save model
    """
    print("\n" + "="*60)
    print("🚀 Starting PhoBERT Fine-tuning")
    print("="*60 + "\n")
    
    # Import training function
    from core_nlp.phobert_trainer import train_phobert_from_test_cases
    
    # Training configuration
    print("⚙️  Configuration:")
    print(f"   • Epochs: {epochs}")
    print(f"   • Batch size: {batch_size}")
    print(f"   • Learning rate: {learning_rate}")
    print(f"   • Output: {output_dir}")
    print(f"   • Training data: training_data/phobert_training_augmented.json")
    print()
    
    # Start training
    try:
        train_phobert_from_test_cases(
            test_file="training_data/phobert_training_augmented.json",
            output_dir=output_dir,
            num_epochs=epochs,
            batch_size=batch_size
        )
        
        print("\n" + "="*60)
        print("✅ Training completed successfully!")
        print("="*60)
        print(f"\n📁 Model saved to: {output_dir}")
        print("\n💡 To use the fine-tuned model:")
        print("   1. Update pipeline to use: HybridPipeline(model_path='./models/phobert_finetuned')")
        print("   2. Run tests: python comprehensive_test.py")
        print()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Training interrupted by user")
        print(f"   Partial model may be saved in: {output_dir}")
    except Exception as e:
        print(f"\n\n❌ Training failed: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main training entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Fine-tune PhoBERT for event extraction",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic training (5 epochs)
  python train_phobert.py
  
  # Custom epochs and batch size
  python train_phobert.py --epochs 10 --batch_size 8
  
  # With custom learning rate
  python train_phobert.py --epochs 5 --lr 1e-5
  
  # Save to custom directory
  python train_phobert.py --output ./my_models/phobert_v2
        """
    )
    
    parser.add_argument(
        '--epochs', 
        type=int, 
        default=5,
        help='Number of training epochs (default: 5)'
    )
    parser.add_argument(
        '--batch_size', 
        type=int, 
        default=16,
        help='Batch size (default: 16, reduce to 8 or 4 if GPU OOM)'
    )
    parser.add_argument(
        '--lr', 
        type=float, 
        default=2e-5,
        help='Learning rate (default: 2e-5)'
    )
    parser.add_argument(
        '--output', 
        type=str, 
        default='./models/phobert_finetuned',
        help='Output directory for trained model'
    )
    parser.add_argument(
        '--skip_checks',
        action='store_true',
        help='Skip requirement and data checks'
    )
    
    args = parser.parse_args()
    
    # Print header
    print("\n" + "="*60)
    print("📚 PhoBERT Fine-tuning for Event Extraction")
    print("="*60 + "\n")
    
    # Run checks
    if not args.skip_checks:
        print("🔍 Checking requirements...\n")
        
        if not check_requirements():
            sys.exit(1)
        
        print("\n🔍 Checking training data...\n")
        
        if not check_training_data():
            sys.exit(1)
        
        print()
    
    # Start training
    train_model(
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.lr,
        output_dir=args.output
    )


if __name__ == "__main__":
    main()
