#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Automated Edge Case Testing
Tests all edge cases from EDGE_CASE_PROMPTS.md automatically
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime
from core_nlp.pipeline import NLPPipeline

class EdgeCaseTester:
    def __init__(self):
        self.base_datetime = datetime(2025, 11, 7, 9, 0)  # Nov 7, 2025, 9:00 AM
        self.nlp = NLPPipeline()
        self.passed = 0
        self.failed = 0
        self.failures = []
    
    def test_case(self, name, input_text, expected):
        """Test a single edge case"""
        print(f"\n{'='*70}")
        print(f"TEST: {name}")
        print(f"Input: {input_text}")
        
        result = self.nlp.process(input_text)
        
        # Compare results
        matches = True
        mismatches = []
        
        for key in ['event', 'start_time', 'location', 'reminder_minutes']:
            expected_val = expected.get(key)
            actual_val = result.get(key)
            
            if expected_val != actual_val:
                matches = False
                mismatches.append(f"  {key}: expected '{expected_val}', got '{actual_val}'")
        
        if matches:
            print("✅ PASS")
            self.passed += 1
        else:
            print("❌ FAIL")
            for mismatch in mismatches:
                print(mismatch)
            self.failed += 1
            self.failures.append({
                'name': name,
                'input': input_text,
                'expected': expected,
                'actual': result,
                'mismatches': mismatches
            })
        
        return matches
    
    def run_all_tests(self):
        """Run all edge case tests"""
        print("="*70)
        print("AUTOMATED EDGE CASE TESTING")
        print("="*70)
        
        # 1. UPPERCASE & MIXED CASE
        print("\n\n📋 CATEGORY 1: UPPERCASE & MIXED CASE")
        
        self.test_case(
            "Uppercase Event",
            "SINH NHẬT 8:30 NGÀY MAI",
            {'event': 'sinh nhat', 'start_time': '2025-11-08 08:30:00', 'location': None, 'reminder_minutes': None}
        )
        
        self.test_case(
            "Mixed Case Complex",
            "HỌp Với KHÁCH 10h SÁng T2",
            {'event': 'hop voi khach', 'start_time': '2025-11-10 10:00:00', 'location': None, 'reminder_minutes': None}
        )
        
        self.test_case(
            "Uppercase with Location",
            "10H SÁNG MAI HỌP CÔNG TY ABC",
            {'event': 'hop', 'start_time': '2025-11-08 10:00:00', 'location': 'cong ty abc', 'reminder_minutes': None}
        )
        
        # 2. TYPOS & NO DIACRITICS
        print("\n\n📋 CATEGORY 2: TYPOS & NO DIACRITICS")
        
        self.test_case(
            "Typo 'sauh'",
            "chu nhat sauh gio chieu di cafe",
            {'event': 'di cafe', 'start_time': '2025-11-09 18:00:00', 'location': None, 'reminder_minutes': None}
        )
        
        self.test_case(
            "No Diacritics",
            "t3 14h hop tai van phong",
            {'event': 'hop', 'start_time': '2025-11-11 14:00:00', 'location': 'van phong', 'reminder_minutes': None}
        )
        
        self.test_case(
            "Period Word 'toi'",
            "20h toi di an",
            {'event': 'di an', 'start_time': '2025-11-07 20:00:00', 'location': None, 'reminder_minutes': None}
        )
        
        self.test_case(
            "Typo 'ngai'",
            "8h30 ngai mai lam viec",
            {'event': 'lam viec', 'start_time': '2025-11-08 08:30:00', 'location': None, 'reminder_minutes': None}
        )
        
        # 3. LOCATION WITHOUT MARKERS
        print("\n\n📋 CATEGORY 3: LOCATION WITHOUT MARKERS")
        
        self.test_case(
            "Location after Event",
            "10h sang mai hop cong ty ABC",
            {'event': 'hop', 'start_time': '2025-11-08 10:00:00', 'location': 'cong ty abc', 'reminder_minutes': None}
        )
        
        self.test_case(
            "Multiple Word Location",
            "14h chieu t4 gap khach nha hang pho co",
            {'event': 'gap khach', 'start_time': '2025-11-12 14:00:00', 'location': 'nha hang pho co', 'reminder_minutes': None}
        )
        
        self.test_case(
            "Two-word Event",
            "chu nhat chieu an tiec nha hang",
            {'event': 'an tiec', 'start_time': '2025-11-09 14:00:00', 'location': 'nha hang', 'reminder_minutes': None}
        )
        
        self.test_case(
            "Short Location",
            "18h toi an com nha",
            {'event': 'an com', 'start_time': '2025-11-07 18:00:00', 'location': 'nha', 'reminder_minutes': None}
        )
        
        # 4. COMPLEX TIME PATTERNS
        print("\n\n📋 CATEGORY 4: COMPLEX TIME PATTERNS")
        
        self.test_case(
            "Weekday + Number Word",
            "thứ năm 7h toi an com nha hang",
            {'event': 'an com', 'start_time': '2025-11-13 19:00:00', 'location': 'nha hang', 'reminder_minutes': None}
        )
        
        self.test_case(
            "Sunday Afternoon",
            "chu nhat chieu 3h tap gym",
            {'event': 'tap gym', 'start_time': '2025-11-09 15:00:00', 'location': None, 'reminder_minutes': None}
        )
        
        self.test_case(
            "Complex Compound",
            "thứ ba tuần sau 8h30 sáng họp",
            {'event': 'hop', 'start_time': '2025-11-18 08:30:00', 'location': None, 'reminder_minutes': None}
        )
        
        self.test_case(
            "Period + Exact Time",
            "toi mai 19h30 xem phim",
            {'event': 'xem phim', 'start_time': '2025-11-08 19:30:00', 'location': None, 'reminder_minutes': None}
        )
        
        # 5. THREE-WORD EVENTS
        print("\n\n📋 CATEGORY 5: THREE-WORD EVENTS")
        
        self.test_case(
            "3-word Event 'gap doi tac'",
            "t4 14h gap doi tac van phong ABC",
            {'event': 'gap doi tac', 'start_time': '2025-11-12 14:00:00', 'location': 'van phong abc', 'reminder_minutes': None}
        )
        
        self.test_case(
            "4+ Words Split",
            "10h sang hop ban giam doc phong hop A",
            {'event': 'hop ban giam', 'start_time': '2025-11-07 10:00:00', 'location': 'doc phong hop a', 'reminder_minutes': None}
        )
        
        # 6. MULTIPLE EVENTS
        print("\n\n📋 CATEGORY 6: MULTIPLE EVENTS")
        
        self.test_case(
            "First Event Extracted",
            "8h sang hop va 14h gap khach",
            {'event': 'hop', 'start_time': '2025-11-07 08:00:00', 'location': None, 'reminder_minutes': None}
        )
        
        self.test_case(
            "Multiple Time Markers",
            "thứ 2 10h lam viec, thứ 3 14h gap doi tac",
            {'event': 'lam viec', 'start_time': '2025-11-10 10:00:00', 'location': None, 'reminder_minutes': None}
        )
        
        # 7. REMINDER MINUTES
        print("\n\n📋 CATEGORY 7: REMINDER MINUTES")
        
        self.test_case(
            "Reminder 30 mins",
            "hop 14h mai nhac truoc 30 phut",
            {'event': 'hop', 'start_time': '2025-11-08 14:00:00', 'location': None, 'reminder_minutes': 30}
        )
        
        self.test_case(
            "Reminder 1 hour",
            "gap khach 10h t3 nhac truoc 1 tieng",
            {'event': 'gap khach', 'start_time': '2025-11-11 10:00:00', 'location': None, 'reminder_minutes': 60}
        )
        
        # 8. EXTREME EDGE CASES
        print("\n\n📋 CATEGORY 8: EXTREME EDGE CASES")
        
        self.test_case(
            "No Time Info",
            "hop quan trong",
            {'event': 'hop quan trong', 'start_time': None, 'location': None, 'reminder_minutes': None}
        )
        
        self.test_case(
            "Time Only",
            "14h30",
            {'event': None, 'start_time': '2025-11-07 14:30:00', 'location': None, 'reminder_minutes': None}
        )
        
        self.test_case(
            "Single Word",
            "hop",
            {'event': 'hop', 'start_time': None, 'location': None, 'reminder_minutes': None}
        )
        
        self.test_case(
            "Very Short",
            "8h an",
            {'event': 'an', 'start_time': '2025-11-07 08:00:00', 'location': None, 'reminder_minutes': None}
        )
        
        # Print summary
        print("\n\n" + "="*70)
        print("SUMMARY")
        print("="*70)
        print(f"Total: {self.passed + self.failed}")
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        
        if self.failed == 0:
            print("\n🎉 ALL TESTS PASSED!")
        else:
            print(f"\n⚠️  {self.failed} test(s) failed:")
            for failure in self.failures:
                print(f"\n  - {failure['name']}")
                print(f"    Input: {failure['input']}")
                for mismatch in failure['mismatches']:
                    print(f"    {mismatch}")
        
        accuracy = (self.passed / (self.passed + self.failed)) * 100 if (self.passed + self.failed) > 0 else 0
        print(f"\n📊 Accuracy: {accuracy:.2f}%")
        
        return self.failed == 0


if __name__ == '__main__':
    tester = EdgeCaseTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
