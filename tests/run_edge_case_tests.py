"""
Test runner for edge case tests
Runs all 1000+ edge case tests and generates detailed report
"""
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core_nlp.phobert_model import PhoBERTNLPPipeline

class EdgeCaseTestRunner:
    def __init__(self, test_file: str):
        self.test_file = test_file
        self.nlp = PhoBERTNLPPipeline()
        self.results = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'by_category': {},
            'failures': []
        }
    
    def run_tests(self):
        """Run all tests from JSON file"""
        print(f"Loading tests from {self.test_file}...")
        
        with open(self.test_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        test_cases = data['test_cases']
        total = len(test_cases)
        
        print(f"Running {total} test cases...\n")
        print("=" * 80)
        
        for i, test_case in enumerate(test_cases, 1):
            if i % 50 == 0:
                print(f"Progress: {i}/{total} ({i*100//total}%)")
            
            result = self.run_single_test(test_case)
            
            # Update results
            self.results['total'] += 1
            category = test_case['category']
            
            if category not in self.results['by_category']:
                self.results['by_category'][category] = {
                    'total': 0,
                    'passed': 0,
                    'failed': 0
                }
            
            self.results['by_category'][category]['total'] += 1
            
            if result['success']:
                self.results['passed'] += 1
                self.results['by_category'][category]['passed'] += 1
            else:
                self.results['failed'] += 1
                self.results['by_category'][category]['failed'] += 1
                self.results['failures'].append({
                    'test_id': test_case['id'],
                    'input': test_case['input'],
                    'category': category,
                    'note': test_case.get('note', ''),
                    'error': result['error'],
                    'parsed_data': result.get('parsed_data')
                })
        
        print(f"Progress: {total}/{total} (100%)")
        print("=" * 80)
    
    def run_single_test(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single test case"""
        input_text = test_case['input']
        category = test_case['category']
        
        # Special handling for invalid inputs
        if category == 'invalid_input':
            # These SHOULD fail - test that they fail gracefully
            try:
                result = self.nlp.process(input_text)
                # Check if properly rejected
                if not result.get('event') or not result.get('start_time'):
                    return {'success': True, 'error': None}
                else:
                    return {
                        'success': False,
                        'error': 'Invalid input accepted when it should be rejected',
                        'parsed_data': result
                    }
            except Exception as e:
                # Exception is OK for invalid input
                return {'success': True, 'error': None}
        
        # Normal test cases
        try:
            result = self.nlp.process(input_text)
            
            # Validate result
            errors = []
            
            # Check for required fields based on category
            if category in ['missing_event', 'only_event']:
                # These should fail (no event or no time)
                if result.get('event') and result.get('start_time'):
                    errors.append('Should have failed but passed')
            elif category == 'missing_location':
                # Location is optional - should pass
                if not result.get('event') or not result.get('start_time'):
                    errors.append('Missing event or time')
            else:
                # Normal cases - should have event and time
                if not result.get('event'):
                    errors.append('Missing event name')
                if not result.get('start_time'):
                    errors.append('Missing start time')
            
            if errors:
                return {
                    'success': False,
                    'error': '; '.join(errors),
                    'parsed_data': result
                }
            
            return {'success': True, 'error': None, 'parsed_data': result}
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Exception: {str(e)}',
                'parsed_data': None
            }
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print()
        
        total = self.results['total']
        passed = self.results['passed']
        failed = self.results['failed']
        pass_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"Total Tests: {total}")
        print(f"✅ Passed: {passed} ({pass_rate:.1f}%)")
        print(f"❌ Failed: {failed} ({100-pass_rate:.1f}%)")
        print()
        
        # Category breakdown
        print("Results by Category:")
        print("-" * 80)
        
        for category, stats in sorted(self.results['by_category'].items()):
            cat_total = stats['total']
            cat_passed = stats['passed']
            cat_rate = (cat_passed / cat_total * 100) if cat_total > 0 else 0
            status = "✅" if cat_rate >= 90 else "⚠️" if cat_rate >= 70 else "❌"
            
            print(f"{status} {category:30s}: {cat_passed:3d}/{cat_total:3d} ({cat_rate:5.1f}%)")
        
        print()
        
        # Show failures
        if self.results['failures']:
            print(f"\n⚠️  Total Failed Cases: {len(self.results['failures'])}")
            print("Showing first 20 failures:\n")
            
            for failure in self.results['failures'][:20]:
                print(f"Test #{failure['test_id']} [{failure['category']}]:")
                print(f"  Input: {failure['input']}")
                print(f"  Note: {failure['note']}")
                print(f"  Error: {failure['error']}")
                if failure.get('parsed_data'):
                    print(f"  Parsed: {failure['parsed_data']}")
                print()
    
    def save_report(self, output_file='tests/edge_case_test_report.json'):
        """Save detailed report to JSON"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total': self.results['total'],
                'passed': self.results['passed'],
                'failed': self.results['failed'],
                'pass_rate': (self.results['passed'] / self.results['total'] * 100) 
                            if self.results['total'] > 0 else 0
            },
            'by_category': self.results['by_category'],
            'failures': self.results['failures']
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 Detailed report saved to: {output_file}")

def main():
    test_file = 'tests/edge_case_tests_1000.json'
    
    if not Path(test_file).exists():
        print(f"❌ Test file not found: {test_file}")
        print("Please run: python scripts/generate_edge_case_tests.py")
        return
    
    runner = EdgeCaseTestRunner(test_file)
    
    print("=" * 80)
    print("EDGE CASE TEST RUNNER")
    print("=" * 80)
    print()
    
    try:
        runner.run_tests()
        runner.print_summary()
        runner.save_report()
        
        print("\n✅ Testing complete!")
        
        # Exit code based on pass rate
        pass_rate = (runner.results['passed'] / runner.results['total'] * 100) 
        if pass_rate < 80:
            print(f"\n⚠️  Warning: Pass rate is below 80% ({pass_rate:.1f}%)")
            sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Testing interrupted by user")
        runner.print_summary()
        runner.save_report()
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
