#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test time period validation edge cases"""

from core_nlp.pipeline import NLPPipeline

def test_time_periods():
    p = NLPPipeline()
    
    test_cases = [
        # (input, expected_hour, description)
        ("Nộp báo cáo 10 giờ trưa hôm nay", 12, "10 giờ trưa → 12:00 (invalid, fallback to noon)"),
        ("Họp 12 giờ sáng mai", 0, "12 giờ sáng → 00:00 (midnight, 12 AM)"),
        ("Họp 12 giờ chiều hôm nay", 12, "12 giờ chiều → 12:00 (noon, 12 PM)"),
        ("Gặp khách 2 giờ chiều", 14, "2 giờ chiều → 14:00 (2 PM)"),
        ("Ăn tối 8 giờ tối", 20, "8 giờ tối → 20:00 (8 PM)"),
        ("Họp 10 giờ sáng", 10, "10 giờ sáng → 10:00 (10 AM)"),
        ("Họp 12 giờ trưa", 12, "12 giờ trưa → 12:00 (noon)"),
        ("Gặp 1 giờ trưa", 13, "1 giờ trưa → 13:00 (1 PM, early afternoon)"),
    ]
    
    print("\n" + "="*80)
    print("TIME PERIOD VALIDATION TESTS")
    print("="*80)
    
    passed = 0
    failed = 0
    
    for input_text, expected_hour, description in test_cases:
        result = p.process(input_text)
        start_time = result.get('start_time')
        
        if start_time:
            actual_hour = int(start_time.split('T')[1].split(':')[0])
            status = "✅ PASS" if actual_hour == expected_hour else "❌ FAIL"
            if actual_hour == expected_hour:
                passed += 1
            else:
                failed += 1
        else:
            actual_hour = None
            status = "❌ FAIL (no time)"
            failed += 1
        
        print(f"\n{status}")
        print(f"  Input: {input_text}")
        print(f"  Description: {description}")
        print(f"  Expected: {expected_hour:02d}:00")
        print(f"  Actual: {actual_hour:02d}:00 ({start_time})" if actual_hour else f"  Actual: {start_time}")
        print(f"  Event: {result.get('event')}")
    
    print("\n" + "="*80)
    print(f"SUMMARY: {passed} passed, {failed} failed")
    print("="*80 + "\n")

if __name__ == "__main__":
    test_time_periods()
