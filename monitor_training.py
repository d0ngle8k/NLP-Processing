"""
Monitor PhoBERT training progress in real-time
"""

import time
import os
from pathlib import Path

def monitor_training_progress(interval=5):
    """Monitor training log file"""
    log_file = Path("models/phobert_finetuned/training.log")
    
    print("🔍 Monitoring PhoBERT Training Progress")
    print("=" * 60)
    print(f"📁 Log file: {log_file}")
    print("Press Ctrl+C to stop monitoring\n")
    
    last_size = 0
    
    try:
        while True:
            if log_file.exists():
                current_size = log_file.stat().st_size
                
                if current_size > last_size:
                    # Read new content
                    with open(log_file, 'r', encoding='utf-8') as f:
                        f.seek(last_size)
                        new_content = f.read()
                        
                        if new_content.strip():
                            print(new_content, end='')
                    
                    last_size = current_size
            else:
                print("⏳ Waiting for training to start...")
            
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print("\n\n✋ Monitoring stopped")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Monitor PhoBERT training")
    parser.add_argument('--interval', type=int, default=5, help='Check interval in seconds')
    
    args = parser.parse_args()
    
    monitor_training_progress(interval=args.interval)
