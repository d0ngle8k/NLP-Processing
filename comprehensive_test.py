#!/usr/bin/env python3
"""
Comprehensive Pipeline Testing Summary
Tests all 3 pipelines on test_cases.json
"""
import json
from datetime import datetime
from core_nlp.pipeline import NLPPipeline
from core_nlp.phobert_model import PhoBERTNLPPipeline
from core_nlp.hybrid_pipeline import HybridNLPPipeline

def calculate_f1(tp, fp, fn):
    """Calculate F1 score"""
    if tp + fp == 0:
        precision = 0
    else:
        precision = tp / (tp + fp)
    
    if tp + fn == 0:
        recall = 0
    else:
        recall = tp / (tp + fn)
    
    if precision + recall == 0:
        return 0
    else:
        return 2 * (precision * recall) / (precision + recall)

def test_pipeline_comprehensive(name, pipeline, test_cases):
    """Test pipeline and calculate detailed metrics"""
    print(f"\n{'='*70}")
    print(f"🧪 {name}")
    print(f"{'='*70}")
    
    metrics = {
        'event': {'tp': 0, 'fp': 0, 'fn': 0},
        'time': {'tp': 0, 'fp': 0, 'fn': 0},
        'location': {'tp': 0, 'fp': 0, 'fn': 0},
        'reminder': {'tp': 0, 'fp': 0, 'fn': 0}
    }
    
    errors = []
    
    for i, case in enumerate(test_cases, 1):
        text = case['input']
        expected = case['expected']
        
        try:
            result = pipeline.process(text)
        except Exception as e:
            errors.append(f"Test #{i}: Exception - {e}")
            continue
        
        # Event name
        exp_event = expected.get('event', '').strip().lower() if expected.get('event') else None
        got_event = result.get('event_name', '').strip().lower() if result.get('event_name') else None
        
        if exp_event and got_event and exp_event == got_event:
            metrics['event']['tp'] += 1
        elif exp_event and not got_event:
            metrics['event']['fn'] += 1
        elif not exp_event and got_event:
            metrics['event']['fp'] += 1
        elif exp_event and got_event and exp_event != got_event:
            metrics['event']['fn'] += 1
            metrics['event']['fp'] += 1
        
        # Time
        exp_time = expected.get('time_str')
        got_time = result.get('start_time')
        
        if exp_time and got_time:
            metrics['time']['tp'] += 1
        elif exp_time and not got_time:
            metrics['time']['fn'] += 1
        elif not exp_time and got_time:
            metrics['time']['fp'] += 1
        
        # Location
        exp_loc = expected.get('location', '').strip().lower() if expected.get('location') else None
        got_loc = result.get('location', '').strip().lower() if result.get('location') else None
        
        if exp_loc and got_loc and exp_loc == got_loc:
            metrics['location']['tp'] += 1
        elif exp_loc and not got_loc:
            metrics['location']['fn'] += 1
        elif not exp_loc and got_loc:
            metrics['location']['fp'] += 1
        elif exp_loc and got_loc and exp_loc != got_loc:
            metrics['location']['fn'] += 1
            metrics['location']['fp'] += 1
        
        # Reminder
        exp_rem = expected.get('reminder_minutes', 0)
        got_rem = result.get('reminder_minutes', 0)
        
        if exp_rem == got_rem and exp_rem > 0:
            metrics['reminder']['tp'] += 1
        elif exp_rem > 0 and got_rem != exp_rem:
            metrics['reminder']['fn'] += 1
        elif exp_rem == 0 and got_rem > 0:
            metrics['reminder']['fp'] += 1
    
    # Calculate F1 scores
    results = {}
    for metric_name, counts in metrics.items():
        f1 = calculate_f1(counts['tp'], counts['fp'], counts['fn'])
        results[metric_name] = {
            'f1': f1,
            'tp': counts['tp'],
            'fp': counts['fp'],
            'fn': counts['fn']
        }
    
    # Calculate macro F1
    macro_f1 = sum(r['f1'] for r in results.values()) / len(results)
    
    # Print results
    print(f"\n📊 Metrics:")
    print(f"{'Metric':<15} {'F1':<8} {'TP':<6} {'FP':<6} {'FN':<6}")
    print("-" * 50)
    for metric_name, data in results.items():
        print(f"{metric_name.capitalize():<15} {data['f1']:.3f}    {data['tp']:<6} {data['fp']:<6} {data['fn']:<6}")
    print("-" * 50)
    print(f"{'Macro F1':<15} {macro_f1:.3f}")
    
    if errors:
        print(f"\n⚠️  {len(errors)} errors occurred")
    
    return macro_f1, results

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧬 COMPREHENSIVE NLP PIPELINE TESTING")
    print("="*70)
    
    # Load test cases
    with open('tests/test_cases.json', encoding='utf-8') as f:
        test_cases = json.load(f)
    
    print(f"\n📋 Loaded {len(test_cases)} test cases from test_cases.json")
    
    results_summary = {}
    
    # Test 1: Rule-based NLP Pipeline
    print("\n" + "="*70)
    print("1️⃣  RULE-BASED NLP PIPELINE")
    print("="*70)
    nlp_rule = NLPPipeline()
    macro_f1_rule, results_rule = test_pipeline_comprehensive("Rule-based NLP", nlp_rule, test_cases)
    results_summary['Rule-based'] = macro_f1_rule
    
    # Test 2: PhoBERT Pipeline
    print("\n" + "="*70)
    print("2️⃣  PHOBERT PIPELINE (Base Model)")
    print("="*70)
    try:
        phobert = PhoBERTNLPPipeline()
        macro_f1_phobert, results_phobert = test_pipeline_comprehensive("PhoBERT", phobert, test_cases)
        results_summary['PhoBERT'] = macro_f1_phobert
    except Exception as e:
        print(f"⚠️  PhoBERT not available: {e}")
        results_summary['PhoBERT'] = 0.0
    
    # Test 3: Hybrid Pipeline
    print("\n" + "="*70)
    print("3️⃣  HYBRID PIPELINE (Rule-based + PhoBERT)")
    print("="*70)
    try:
        hybrid = HybridNLPPipeline()
        macro_f1_hybrid, results_hybrid = test_pipeline_comprehensive("Hybrid", hybrid, test_cases)
        results_summary['Hybrid'] = macro_f1_hybrid
    except Exception as e:
        print(f"⚠️  Hybrid not available: {e}")
        results_summary['Hybrid'] = 0.0
    
    # Final summary
    print("\n" + "="*70)
    print("🏆 FINAL COMPARISON")
    print("="*70)
    print(f"\n{'Pipeline':<20} {'Macro F1':<12} {'Status'}")
    print("-" * 50)
    
    for pipeline_name, score in results_summary.items():
        status = "✅ Excellent" if score > 0.95 else "✅ Good" if score > 0.85 else "⚠️  Fair" if score > 0.70 else "❌ Poor"
        print(f"{pipeline_name:<20} {score:.4f}       {status}")
    
    print("\n" + "="*70)
    print("✅ Testing Complete!")
    print("="*70)
    print(f"\n🎯 Best performing: {max(results_summary.items(), key=lambda x: x[1])[0]}")
    print(f"📊 Test dataset: {len(test_cases)} cases")
    print("\n")
