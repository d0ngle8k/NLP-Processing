#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Hybrid Pipeline - Verify hybrid model works correctly
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime
from core_nlp.hybrid_pipeline import HybridNLPPipeline


def test_hybrid_pipeline():
    """Test hybrid pipeline on critical prompts"""
    print("="*70)
    print("🔥 TESTING HYBRID NLP PIPELINE")
    print("="*70)
    
    # Initialize hybrid pipeline
    model_path = "./models/phobert_finetuned"
    if os.path.exists(model_path):
        print(f"✅ Fine-tuned model found: {model_path}")
    else:
        print(f"⚠️ Fine-tuned model not found: {model_path}")
    
    print("\n📋 Initializing Hybrid Pipeline...")
    nlp = HybridNLPPipeline(model_path=model_path if os.path.exists(model_path) else None)
    
    # Get model info
    info = nlp.get_model_info()
    print(f"\n📊 Model Information:")
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    # Test prompts
    test_cases = [
        {
            'name': 'Uppercase Event',
            'input': 'SINH NHẬT 8:30 NGÀY MAI',
            'expected': {'event': 'sinh nhật', 'has_time': True}
        },
        {
            'name': 'Typo sauh',
            'input': 'chu nhat sauh gio chieu di cafe',
            'expected': {'event': 'di cafe', 'has_time': True}
        },
        {
            'name': 'Location without marker',
            'input': '10h sang mai hop cong ty ABC',
            'expected': {'event': 'hop', 'has_time': True, 'location': 'cong ty abc'}
        },
        {
            'name': 'Complex time',
            'input': 'thứ năm 7h toi an com nha hang',
            'expected': {'event': 'an com', 'has_time': True, 'location': 'nha hang'}
        },
        {
            'name': '3-word event',
            'input': 't4 14h gap doi tac van phong ABC',
            'expected': {'event': 'gap doi tac', 'has_time': True, 'location': 'van phong abc'}
        },
        {
            'name': 'Reminder',
            'input': 'hop 14h mai nhac truoc 30 phut',
            'expected': {'event': 'hop', 'has_time': True, 'reminder': 30}
        },
        {
            'name': 'Mixed case',
            'input': 'HỌp Với KHÁCH 10h SÁng T2',
            'expected': {'event': 'họp với khách', 'has_time': True}
        },
        {
            'name': 'Period word toi',
            'input': '20h toi di an',
            'expected': {'event': 'di an', 'has_time': True}
        },
        {
            'name': 'Sunday + location',
            'input': 'chu nhat chieu an tiec nha hang',
            'expected': {'event': 'an tiec', 'has_time': True, 'location': 'nha hang'}
        },
        {
            'name': 'Compound time',
            'input': 'thứ ba tuần sau 8h30 sáng họp',
            'expected': {'event': 'họp', 'has_time': True}
        }
    ]
    
    passed = 0
    failed = 0
    
    print("\n" + "="*70)
    print("RUNNING TESTS")
    print("="*70)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*70}")
        print(f"TEST #{i}: {test['name']}")
        print(f"Input: {test['input']}")
        
        # Process
        result = nlp.process(test['input'])
        
        # Display result
        print(f"\n📝 Result:")
        print(f"  Event: {result.get('event', '(none)')}")
        print(f"  Time: {result.get('start_time', '(none)')}")
        print(f"  Location: {result.get('location', '(none)')}")
        print(f"  Reminder: {result.get('reminder_minutes', 0)} mins")
        
        if '_models_used' in result:
            print(f"  Mode: {result['_models_used']}")
        
        if '_agreement_scores' in result:
            scores = result['_agreement_scores']
            avg_score = sum(scores.values()) / len(scores) * 100
            print(f"  Agreement: {avg_score:.1f}%")
        
        # Validate
        errors = []
        
        # Check event
        if 'event' in test['expected']:
            expected_event = test['expected']['event'].lower()
            actual_event = (result.get('event') or '').lower()
            if expected_event not in actual_event and actual_event not in expected_event:
                errors.append(f"Event: expected '{expected_event}', got '{actual_event}'")
        
        # Check time existence
        if test['expected'].get('has_time'):
            if not result.get('start_time'):
                errors.append("Time: expected time but got None")
        
        # Check location
        if 'location' in test['expected']:
            expected_loc = test['expected']['location'].lower()
            actual_loc = (result.get('location') or '').lower()
            if expected_loc not in actual_loc and actual_loc not in expected_loc:
                errors.append(f"Location: expected '{expected_loc}', got '{actual_loc}'")
        
        # Check reminder
        if 'reminder' in test['expected']:
            expected_rem = test['expected']['reminder']
            actual_rem = result.get('reminder_minutes', 0)
            if expected_rem != actual_rem:
                errors.append(f"Reminder: expected {expected_rem}, got {actual_rem}")
        
        # Print result
        if errors:
            print(f"\n❌ FAIL")
            for error in errors:
                print(f"  ⚠️  {error}")
            failed += 1
        else:
            print(f"\n✅ PASS")
            passed += 1
    
    # Summary
    print("\n" + "="*70)
    print("📊 SUMMARY")
    print("="*70)
    print(f"Total: {passed + failed}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED!")
    else:
        print(f"\n⚠️  {failed} test(s) failed")
    
    accuracy = (passed / (passed + failed)) * 100 if (passed + failed) > 0 else 0
    print(f"\n📈 Accuracy: {accuracy:.1f}%")
    print("="*70)
    
    return failed == 0


if __name__ == '__main__':
    success = test_hybrid_pipeline()
    sys.exit(0 if success else 1)
