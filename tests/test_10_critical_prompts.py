#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test 10 Critical Edge Case Prompts
Validates the most important edge cases from QUICK_START.md
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime
from core_nlp.pipeline import NLPPipeline


def normalize_text(text):
    """Normalize text for comparison"""
    if text is None:
        return None
    return text.lower().strip()


class CriticalPromptTester:
    def __init__(self):
        self.base_datetime = datetime(2025, 11, 7, 9, 0)  # Nov 7, 2025, 9:00 AM (Friday)
        self.nlp = NLPPipeline()
        self.passed = 0
        self.failed = 0
        self.failures = []
    
    def test_case(self, num, name, input_text, expected_event=None, expected_has_time=None, 
                  expected_location=None, expected_reminder=None, notes=""):
        """Test a single critical prompt"""
        print(f"\n{'='*70}")
        print(f"TEST #{num}: {name}")
        print(f"Input: {input_text}")
        if notes:
            print(f"Notes: {notes}")
        
        result = self.nlp.process(input_text)
        
        # Display actual results
        print(f"\n📝 ACTUAL RESULTS:")
        print(f"  Event: {result.get('event', '(none)')}")
        print(f"  Time: {result.get('start_time', '(none)')}")
        print(f"  Location: {result.get('location', '(none)')}")
        print(f"  Reminder: {result.get('reminder_minutes', 0)} minutes")
        
        # Validate results
        errors = []
        
        # Check event (lenient matching)
        if expected_event is not None:
            actual_event = normalize_text(result.get('event'))
            expected_event_norm = normalize_text(expected_event)
            
            if expected_event_norm and actual_event:
                # Allow partial match - check if one contains the other
                if not (expected_event_norm in actual_event or actual_event in expected_event_norm):
                    errors.append(f"Event mismatch: expected '{expected_event_norm}', got '{actual_event}'")
            elif expected_event_norm != actual_event:
                errors.append(f"Event mismatch: expected '{expected_event_norm}', got '{actual_event}'")
        
        # Check if time exists (not exact match, just presence)
        if expected_has_time is not None:
            actual_has_time = result.get('start_time') is not None
            if expected_has_time != actual_has_time:
                errors.append(f"Time presence mismatch: expected {'time' if expected_has_time else 'no time'}, got {'time' if actual_has_time else 'no time'}")
        
        # Check location (lenient matching)
        if expected_location is not None:
            actual_location = normalize_text(result.get('location'))
            expected_location_norm = normalize_text(expected_location)
            
            if expected_location_norm and actual_location:
                # Allow partial match
                if not (expected_location_norm in actual_location or actual_location in expected_location_norm):
                    errors.append(f"Location mismatch: expected '{expected_location_norm}', got '{actual_location}'")
            elif expected_location_norm != actual_location:
                errors.append(f"Location mismatch: expected '{expected_location_norm}', got '{actual_location}'")
        
        # Check reminder
        if expected_reminder is not None:
            actual_reminder = result.get('reminder_minutes', 0)
            if expected_reminder != actual_reminder:
                errors.append(f"Reminder mismatch: expected {expected_reminder} mins, got {actual_reminder} mins")
        
        # Print validation results
        if errors:
            print(f"\n❌ FAIL")
            for error in errors:
                print(f"  ⚠️  {error}")
            self.failed += 1
            self.failures.append({
                'num': num,
                'name': name,
                'input': input_text,
                'errors': errors,
                'actual': result
            })
        else:
            print(f"\n✅ PASS")
            self.passed += 1
        
        return len(errors) == 0
    
    def run_all_tests(self):
        """Run all 10 critical prompts"""
        print("="*70)
        print("🔥 TESTING 10 CRITICAL EDGE CASE PROMPTS")
        print("="*70)
        print(f"Base datetime: {self.base_datetime.strftime('%Y-%m-%d %H:%M:%S')} (Friday)")
        print("="*70)
        
        # Test #1: Uppercase
        self.test_case(
            num=1,
            name="Uppercase Event",
            input_text="SINH NHẬT 8:30 NGÀY MAI",
            expected_event="sinh nhật",  # App preserves diacritics
            expected_has_time=True,
            expected_location=None,
            expected_reminder=0,
            notes="Should handle uppercase and extract event + time"
        )
        
        # Test #2: Typo "sauh"
        self.test_case(
            num=2,
            name="Typo 'sauh'",
            input_text="chu nhat sauh gio chieu di cafe",
            expected_event="di cafe",
            expected_has_time=True,
            expected_location=None,
            expected_reminder=0,
            notes="Should recognize 'sauh' as 'sau' (6) and 'gio chieu' as afternoon time"
        )
        
        # Test #3: Location without marker
        self.test_case(
            num=3,
            name="Location Without Marker",
            input_text="10h sang mai hop cong ty ABC",
            expected_event="hop",
            expected_has_time=True,
            expected_location="cong ty abc",
            expected_reminder=0,
            notes="Should extract location 'cong ty ABC' without 'tai/o' marker"
        )
        
        # Test #4: Complex time pattern
        self.test_case(
            num=4,
            name="Complex Time: Weekday + Period",
            input_text="thứ năm 7h toi an com nha hang",
            expected_event="an com",
            expected_has_time=True,
            expected_location="nha hang",
            expected_reminder=0,
            notes="Should parse 'thứ năm' (Thursday) + '7h toi' (7PM evening)"
        )
        
        # Test #5: Three-word event
        self.test_case(
            num=5,
            name="3-Word Event",
            input_text="t4 14h gap doi tac van phong ABC",
            expected_event="gap doi tac",
            expected_has_time=True,
            expected_location="van phong abc",
            expected_reminder=0,
            notes="Should keep 'gap doi tac' as complete event, 'van phong ABC' as location"
        )
        
        # Test #6: Reminder
        self.test_case(
            num=6,
            name="Reminder Extraction",
            input_text="hop 14h mai nhac truoc 30 phut",
            expected_event="hop",
            expected_has_time=True,
            expected_location=None,
            expected_reminder=30,
            notes="Should extract 30-minute reminder"
        )
        
        # Test #7: Mixed case
        self.test_case(
            num=7,
            name="Mixed Case",
            input_text="HỌp Với KHÁCH 10h SÁng T2",
            expected_event="họp với khách",  # App preserves diacritics
            expected_has_time=True,
            expected_location=None,
            expected_reminder=0,
            notes="Should handle mixed case properly"
        )
        
        # Test #8: Period word "toi"
        self.test_case(
            num=8,
            name="Period Word 'toi'",
            input_text="20h toi di an",
            expected_event="di an",
            expected_has_time=True,
            expected_location=None,
            expected_reminder=0,
            notes="Should recognize 'toi' as evening period word, not part of event"
        )
        
        # Test #9: Sunday + location
        self.test_case(
            num=9,
            name="Sunday + Location",
            input_text="chu nhat chieu an tiec nha hang",
            expected_event="an tiec",
            expected_has_time=True,
            expected_location="nha hang",
            expected_reminder=0,
            notes="Should parse 'chu nhat chieu' (Sunday afternoon) + extract location"
        )
        
        # Test #10: Compound time
        self.test_case(
            num=10,
            name="Compound Time Expression",
            input_text="thứ ba tuần sau 8h30 sáng họp",
            expected_event="họp",  # App preserves diacritics
            expected_has_time=True,
            expected_location=None,
            expected_reminder=0,
            notes="Should parse 'thứ ba tuần sau' (Tuesday next week) + '8h30 sáng'"
        )
        
        # Print summary
        print("\n\n" + "="*70)
        print("📊 SUMMARY")
        print("="*70)
        print(f"Total: {self.passed + self.failed}")
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        
        if self.failed == 0:
            print("\n🎉 ALL 10 CRITICAL PROMPTS PASSED!")
        else:
            print(f"\n⚠️  {self.failed} test(s) failed:")
            print("\n" + "="*70)
            print("FAILED TESTS DETAIL:")
            print("="*70)
            for failure in self.failures:
                print(f"\n❌ Test #{failure['num']}: {failure['name']}")
                print(f"   Input: {failure['input']}")
                print(f"   Actual Results:")
                print(f"     Event: {failure['actual'].get('event')}")
                print(f"     Time: {failure['actual'].get('start_time')}")
                print(f"     Location: {failure['actual'].get('location')}")
                print(f"     Reminder: {failure['actual'].get('reminder_minutes', 0)} mins")
                print(f"   Errors:")
                for error in failure['errors']:
                    print(f"     • {error}")
        
        accuracy = (self.passed / (self.passed + self.failed)) * 100 if (self.passed + self.failed) > 0 else 0
        print(f"\n📈 Accuracy: {accuracy:.1f}%")
        print("="*70)
        
        return self.failed == 0


if __name__ == '__main__':
    tester = CriticalPromptTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
