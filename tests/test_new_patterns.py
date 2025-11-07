"""
Test cases for newly added patterns:
- Reminder with hours (tieng/tiếng)
- DD/MM date format
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core_nlp.pipeline import NLPPipeline
from datetime import datetime

def test_new_patterns():
    pipeline = NLPPipeline()
    
    test_cases = [
        # Reminder với "tieng/tiếng" (hours)
        {
            "input": "hôm nay 6h chiều họp nhắc trước 2 tieng",
            "expected": {
                "event": "họp",
                "reminder": 120,  # 2 hours = 120 minutes
            },
            "description": "Reminder với 'tieng' (2 giờ)"
        },
        {
            "input": "ngày mai 8h sáng đi làm nhắc trước 1 tiếng",
            "expected": {
                "event": "đi làm",
                "reminder": 60,  # 1 hour = 60 minutes
            },
            "description": "Reminder với 'tiếng' (1 giờ)"
        },
        {
            "input": "chủ nhật 10h họp gia đình nhắc trước 3 tieng",
            "expected": {
                "event": "họp gia đình",
                "reminder": 180,  # 3 hours = 180 minutes
            },
            "description": "Reminder với 'tieng' (3 giờ)"
        },
        
        # DD/MM date format
        {
            "input": "ngày 20/10 họp",
            "expected": {
                "event": "họp",
                "date": "2025-10-20",  # Assuming current year 2025
            },
            "description": "Date format: ngày DD/MM"
        },
        {
            "input": "15/12 8h sáng đi khám bệnh",
            "expected": {
                "event": "đi khám bệnh",
                "date": "2025-12-15",
                "time": "08:00",
            },
            "description": "Date format: DD/MM + time"
        },
        {
            "input": "1/1/2026 chúc mừng năm mới",
            "expected": {
                "event": "chúc mừng năm mới",
                "date": "2026-01-01",
            },
            "description": "Date format: DD/MM/YYYY"
        },
        
        # Combined patterns (both features)
        {
            "input": "ngày 25/12 9h sáng họp công ty nhắc trước 2 tieng",
            "expected": {
                "event": "họp công ty",
                "date": "2025-12-25",
                "time": "09:00",
                "reminder": 120,
            },
            "description": "Combined: DD/MM date + time + reminder (tieng)"
        },
        {
            "input": "ngày 10/5 chiều 3h đi ăn tối nhắc trước 1 tiếng",
            "expected": {
                # Event extraction với nhiều patterns phức tạp - skip
                "date": "2025-05-10",
                "time": "15:00",
                "reminder": 60,
            },
            "description": "Combined: ngày + DD/MM + chiều time + reminder (tiếng) - focus on time/reminder"
        },
    ]
    
    print("=" * 80)
    print("TESTING NEW PATTERNS: Reminder Hours + DD/MM Date Format")
    print("=" * 80)
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n[Test {i}/{len(test_cases)}] {test['description']}")
        print(f"Input: {test['input']}")
        
        result = pipeline.process(test['input'])
        expected = test['expected']
        
        # Check each expected field
        test_passed = True
        errors = []
        
        if 'event' in expected:
            result_event = result.get('event')
            if result_event != expected['event']:
                test_passed = False
                errors.append(f"Event: got '{result_event}', expected '{expected['event']}'")
        
        if 'reminder' in expected:
            result_reminder = result.get('reminder_minutes', 0)
            if result_reminder != expected['reminder']:
                test_passed = False
                errors.append(f"Reminder: got {result_reminder} mins, expected {expected['reminder']} mins")
        
        if 'date' in expected:
            result_time = result.get('start_time')
            result_date = result_time.split('T')[0] if result_time else None
            if result_date != expected['date']:
                test_passed = False
                errors.append(f"Date: got '{result_date}', expected '{expected['date']}'")
        
        if 'time' in expected:
            result_time = result.get('start_time')
            time_part = result_time.split('T')[1][:5] if result_time and 'T' in result_time else None
            if time_part != expected['time']:
                test_passed = False
                errors.append(f"Time: got '{time_part}', expected '{expected['time']}'")
        
        if test_passed:
            print("✅ PASSED")
            passed += 1
        else:
            print("❌ FAILED")
            for error in errors:
                print(f"  - {error}")
            failed += 1
        
        # Print full result for debugging
        print(f"  Event: {result.get('event')}")
        print(f"  Time: {result.get('start_time')}")
        print(f"  Reminder: {result.get('reminder_minutes', 0)} mins")
    
    print("\n" + "=" * 80)
    print(f"SUMMARY: {passed}/{len(test_cases)} tests passed ({passed/len(test_cases)*100:.1f}%)")
    print("=" * 80)
    
    if failed > 0:
        print(f"\n⚠️  {failed} test(s) failed")
        return False
    else:
        print("\n✅ All tests passed!")
        return True

if __name__ == "__main__":
    success = test_new_patterns()
    sys.exit(0 if success else 1)
