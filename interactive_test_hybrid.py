#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interactive NLP Testing with Hybrid Model - Simple CLI interface
Uses combined Rule-based + PhoBERT for best accuracy
"""

import sys
from datetime import datetime
from core_nlp.hybrid_pipeline import HybridNLPPipeline
import json
import os


def format_output(result):
    """Format output in readable way"""
    print("\n" + "="*60)
    print("📝 EXTRACTION RESULTS (Hybrid Model):")
    print("="*60)
    
    # Event
    event = result.get('event', '')
    print(f"🎯 Event: {event if event else '(none)'}")
    
    # Time
    start_time = result.get('start_time')
    if start_time:
        # Convert ISO format to readable
        try:
            dt = datetime.fromisoformat(start_time)
            formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S (%A)")
            print(f"⏰ Time: {formatted_time}")
        except:
            print(f"⏰ Time: {start_time}")
    else:
        print("⏰ Time: (none)")
    
    # Location
    location = result.get('location')
    print(f"📍 Location: {location if location else '(none)'}")
    
    # Reminder
    reminder = result.get('reminder_minutes', 0)
    if reminder > 0:
        if reminder >= 60:
            print(f"🔔 Reminder: {reminder} minutes ({reminder//60} hour{'s' if reminder//60 > 1 else ''})")
        else:
            print(f"🔔 Reminder: {reminder} minutes")
    else:
        print("🔔 Reminder: (none)")
    
    # Show model info if available
    if '_models_used' in result:
        print(f"\n🔬 Mode: {result['_models_used']}")
    
    # Show agreement scores if available
    if '_agreement_scores' in result:
        scores = result['_agreement_scores']
        total_agreement = sum(scores.values()) / len(scores) * 100
        print(f"📊 Model agreement: {total_agreement:.1f}%")
    
    print("="*60)


def main():
    """Main interactive test loop"""
    print("="*60)
    print("🔥 NLP INTERACTIVE TESTING - HYBRID MODEL")
    print("="*60)
    print("Using Rule-based + PhoBERT AI (best accuracy)")
    print("\nBase datetime: November 7, 2025, 9:00 AM")
    print("\nCommands:")
    print("  - Type any Vietnamese text to test")
    print("  - Type 'json' to see raw JSON output")
    print("  - Type 'debug' to toggle debug mode")
    print("  - Type 'info' to see model information")
    print("  - Type 'quit' or 'exit' to quit")
    print("  - Type 'prompts' to see suggested edge case prompts")
    print("="*60)
    
    # Initialize Hybrid Pipeline
    model_path = "./models/phobert_finetuned"
    nlp = HybridNLPPipeline(model_path=model_path if os.path.exists(model_path) else None)
    
    # Show model info
    model_info = nlp.get_model_info()
    print(f"\n✅ Hybrid pipeline ready!")
    print(f"📊 Mode: {model_info['mode']}")
    print(f"⚡ Rule-based: {model_info['rule_based']}")
    print(f"🤖 PhoBERT: {model_info['phobert']}")
    
    show_json = False
    show_debug = False
    
    # Sample prompts
    sample_prompts = [
        "SINH NHẬT 8:30 NGÀY MAI",
        "chu nhat sauh gio chieu di cafe",
        "10h sang mai hop cong ty ABC",
        "thứ năm 7h toi an com nha hang",
        "t4 14h gap doi tac van phong ABC",
        "hop 14h mai nhac truoc 30 phut",
        "HỌp Với KHÁCH 10h SÁng T2",
        "20h toi di an",
        "chu nhat chieu an tiec nha hang",
        "thứ ba tuần sau 8h30 sáng họp"
    ]
    
    while True:
        try:
            print("\n" + "-"*60)
            user_input = input("💬 Enter text (or command): ").strip()
            
            if not user_input:
                continue
            
            # Check commands
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            elif user_input.lower() == 'json':
                show_json = not show_json
                print(f"✅ JSON output: {'ENABLED' if show_json else 'DISABLED'}")
                continue
            
            elif user_input.lower() == 'debug':
                show_debug = not show_debug
                print(f"✅ Debug mode: {'ENABLED' if show_debug else 'DISABLED'}")
                continue
            
            elif user_input.lower() == 'info':
                info = nlp.get_model_info()
                print("\n📊 MODEL INFORMATION:")
                print("="*60)
                for key, value in info.items():
                    print(f"  {key}: {value}")
                print("="*60)
                continue
            
            elif user_input.lower() == 'prompts':
                print("\n📋 SUGGESTED EDGE CASE PROMPTS:")
                print("="*60)
                for i, prompt in enumerate(sample_prompts, 1):
                    print(f"{i:2d}. {prompt}")
                print("="*60)
                continue
            
            # Process input with Hybrid
            result = nlp.process(user_input)
            
            # Show results
            if show_json:
                # Remove debug info from JSON if not in debug mode
                display_result = result.copy()
                if not show_debug:
                    display_result.pop('_rule_based', None)
                    display_result.pop('_phobert', None)
                    display_result.pop('_agreement_scores', None)
                    display_result.pop('_models_used', None)
                
                print("\n📄 Raw JSON:")
                print(json.dumps(display_result, indent=2, ensure_ascii=False))
            
            format_output(result)
            
            # Show debug info if enabled
            if show_debug and '_rule_based' in result:
                print("\n🔍 DEBUG INFO:")
                print("="*60)
                print("\n⚡ RULE-BASED OUTPUT:")
                print(json.dumps(result['_rule_based'], indent=2, ensure_ascii=False))
                
                if '_phobert' in result:
                    print("\n🤖 PHOBERT OUTPUT:")
                    print(json.dumps(result['_phobert'], indent=2, ensure_ascii=False))
                
                if '_agreement_scores' in result:
                    print("\n📊 AGREEMENT SCORES:")
                    for key, score in result['_agreement_scores'].items():
                        print(f"  {key}: {score*100:.1f}%")
                print("="*60)
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == '__main__':
    main()
