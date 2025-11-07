"""
Test PhoBERT Model Extraction
Run inference on test prompts and compare with expected outputs
"""
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core_nlp.phobert_model import PhoBERTNLPPipeline


def normalize_datetime(dt_str: str) -> str:
    """Normalize datetime string to compare (remove seconds)"""
    if not dt_str:
        return ""
    try:
        dt = datetime.fromisoformat(dt_str)
        return dt.strftime("%Y-%m-%d %H:%M")
    except:
        return dt_str


def compare_results(predicted: Dict[str, Any], expected: Dict[str, Any]) -> Dict[str, bool]:
    """Compare predicted vs expected results"""
    comparison = {
        'event': (predicted.get('event') or '').strip().lower() == (expected.get('event') or '').strip().lower(),
        'start_time': normalize_datetime(predicted.get('start_time')) == normalize_datetime(expected.get('start_time')),
        'location': (predicted.get('location') or '').strip().lower() == (expected.get('location') or '').strip().lower(),
        'reminder_minutes': predicted.get('reminder_minutes', 0) == expected.get('reminder_minutes', 0),
    }
    
    # Check end_time if present in expected
    if 'end_time' in expected and expected['end_time']:
        comparison['end_time'] = normalize_datetime(predicted.get('end_time')) == normalize_datetime(expected['end_time'])
    
    return comparison


def format_result(item: Dict, predicted: Dict, comparison: Dict) -> str:
    """Format test result for display"""
    lines = []
    lines.append(f"\n{'='*80}")
    lines.append(f"Test #{item['id']}: {item['category']}")
    lines.append(f"{'='*80}")
    lines.append(f"Input: \"{item['input']}\"")
    lines.append(f"\n{'Attribute':<20} {'Expected':<30} {'Predicted':<30} {'Match'}")
    lines.append(f"{'-'*80}")
    
    expected = item['expected']
    
    # Event
    exp_event = expected.get('event') or 'None'
    pred_event = predicted.get('event') or 'None'
    match_event = '✅' if comparison['event'] else '❌'
    lines.append(f"{'Event':<20} {exp_event:<30} {pred_event:<30} {match_event}")
    
    # Start time
    exp_time = normalize_datetime(expected.get('start_time')) or 'None'
    pred_time = normalize_datetime(predicted.get('start_time')) or 'None'
    match_time = '✅' if comparison['start_time'] else '❌'
    lines.append(f"{'Start Time':<20} {exp_time:<30} {pred_time:<30} {match_time}")
    
    # End time (if present)
    if 'end_time' in expected and expected.get('end_time'):
        exp_end = normalize_datetime(expected['end_time']) or 'None'
        pred_end = normalize_datetime(predicted.get('end_time')) or 'None'
        match_end = '✅' if comparison.get('end_time', False) else '❌'
        lines.append(f"{'End Time':<20} {exp_end:<30} {pred_end:<30} {match_end}")
    
    # Location
    exp_loc = expected.get('location') or 'None'
    pred_loc = predicted.get('location') or 'None'
    match_loc = '✅' if comparison['location'] else '❌'
    lines.append(f"{'Location':<20} {exp_loc:<30} {pred_loc:<30} {match_loc}")
    
    # Reminder
    exp_rem = str(expected.get('reminder_minutes', 0))
    pred_rem = str(predicted.get('reminder_minutes', 0))
    match_rem = '✅' if comparison['reminder_minutes'] else '❌'
    lines.append(f"{'Reminder (min)':<20} {exp_rem:<30} {pred_rem:<30} {match_rem}")
    
    # Overall
    all_match = all(comparison.values())
    overall = '✅ PASS' if all_match else '❌ FAIL'
    lines.append(f"\n{'Overall':<20} {overall}")
    
    return '\n'.join(lines)


def main():
    """Run PhoBERT extraction tests"""
    print("="*80)
    print("PhoBERT Model Extraction Test")
    print("="*80)
    
    # Load test cases
    test_file = Path(__file__).parent / 'test_phobert_extraction.json'
    print(f"\n📂 Loading test cases from: {test_file}")
    
    with open(test_file, 'r', encoding='utf-8') as f:
        test_cases = json.load(f)
    
    print(f"✅ Loaded {len(test_cases)} test cases\n")
    
    # Initialize PhoBERT pipeline
    print("🔧 Initializing PhoBERT pipeline...")
    pipeline = PhoBERTNLPPipeline(model_path='./models/phobert_finetuned')
    print("✅ Pipeline ready\n")
    
    # Run tests
    results = []
    detailed_output = []
    
    for item in test_cases:
        input_text = item['input']
        expected = item['expected']
        
        # Run prediction
        predicted = pipeline.process(input_text)
        
        # Compare
        comparison = compare_results(predicted, expected)
        all_match = all(comparison.values())
        
        results.append({
            'id': item['id'],
            'category': item['category'],
            'input': input_text,
            'pass': all_match,
            'comparison': comparison,
        })
        
        # Format detailed output
        detailed_output.append(format_result(item, predicted, comparison))
    
    # Print detailed results
    for output in detailed_output:
        print(output)
    
    # Summary
    total = len(results)
    passed = sum(1 for r in results if r['pass'])
    failed = total - passed
    accuracy = (passed / total * 100) if total > 0 else 0
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Total Tests:  {total}")
    print(f"Passed:       {passed} ✅")
    print(f"Failed:       {failed} ❌")
    print(f"Accuracy:     {accuracy:.1f}%")
    print("="*80)
    
    # Breakdown by attribute
    print("\nAccuracy by Attribute:")
    print("-"*80)
    
    attr_stats = {
        'event': {'correct': 0, 'total': 0},
        'start_time': {'correct': 0, 'total': 0},
        'location': {'correct': 0, 'total': 0},
        'reminder_minutes': {'correct': 0, 'total': 0},
    }
    
    for result in results:
        for attr, is_correct in result['comparison'].items():
            if attr in attr_stats:
                attr_stats[attr]['total'] += 1
                if is_correct:
                    attr_stats[attr]['correct'] += 1
    
    for attr, stats in attr_stats.items():
        correct = stats['correct']
        total = stats['total']
        pct = (correct / total * 100) if total > 0 else 0
        print(f"{attr:<20} {correct}/{total} ({pct:.1f}%)")
    
    print("="*80)
    
    # Save results to JSON
    output_file = Path(__file__).parent / 'test_phobert_results.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'summary': {
                'total': total,
                'passed': passed,
                'failed': failed,
                'accuracy': accuracy,
            },
            'attribute_stats': {
                attr: {
                    'correct': stats['correct'],
                    'total': stats['total'],
                    'accuracy': (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
                }
                for attr, stats in attr_stats.items()
            },
            'results': results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n📊 Detailed results saved to: {output_file}")
    
    return 0 if passed == total else 1


if __name__ == '__main__':
    sys.exit(main())
