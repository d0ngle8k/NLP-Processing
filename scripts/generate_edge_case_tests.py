"""
Generate 1000 edge case test prompts for Vietnamese NLP
Focus on tricky cases, ambiguous inputs, and boundary conditions
"""
import json
import random
from datetime import datetime, timedelta

def generate_edge_cases():
    """Generate comprehensive edge case test data"""
    test_cases = []
    
    # === CATEGORY 1: Weekday + Time Variations (100 cases) ===
    print("Generating weekday + time cases...")
    weekdays = [
        ('thứ 2', 'thứ hai', 't2', 'thu 2'),
        ('thứ 3', 'thứ ba', 't3', 'thu 3'),
        ('thứ 4', 'thứ tư', 't4', 'thu 4'),
        ('thứ 5', 'thứ năm', 't5', 'thu 5'),
        ('thứ 6', 'thứ sáu', 't6', 'thu 6'),
        ('thứ 7', 'thứ bảy', 't7', 'thu 7'),
        ('chủ nhật', 'cn', 'chủ nhật', 'chu nhat')
    ]
    
    time_words = ['một', 'hai', 'ba', 'bốn', 'năm', 'sáu', 'bảy', 'tám', 'chín', 'mười', 'mười một', 'mười hai']
    events = ['họp', 'meeting', 'gặp khách', 'phỏng vấn', 'làm việc', 'training', 'review code', 'standup']
    
    for i in range(100):
        wd_variants = random.choice(weekdays)
        wd = random.choice(wd_variants)
        time_word = random.choice(time_words)
        event = random.choice(events)
        
        # Variations
        if i % 4 == 0:
            prompt = f"{wd} {time_word} giờ tôi có {event}"
        elif i % 4 == 1:
            prompt = f"{event} {wd} lúc {time_word} giờ"
        elif i % 4 == 2:
            prompt = f"tôi {event} {wd} {time_word}h"
        else:
            prompt = f"{wd} {time_word}h {event}"
        
        test_cases.append({
            'id': len(test_cases) + 1,
            'input': prompt,
            'category': 'weekday_time',
            'note': f'Weekday with word number: {wd} + {time_word}'
        })
    
    # === CATEGORY 2: Ambiguous "tôi" vs "tối" (50 cases) ===
    print("Generating 'tôi' vs 'tối' ambiguous cases...")
    for i in range(50):
        hour = random.randint(1, 11)
        event = random.choice(events)
        
        if i % 2 == 0:
            # "tôi có" - should NOT treat "tôi" as "tối"
            prompt = f"{hour}h tôi có {event}"
            test_cases.append({
                'id': len(test_cases) + 1,
                'input': prompt,
                'category': 'ambiguous_toi',
                'note': 'Should parse as time + "tôi có" (I have), NOT evening'
            })
        else:
            # "tối" - should treat as evening
            prompt = f"{hour}h tối {event}"
            test_cases.append({
                'id': len(test_cases) + 1,
                'input': prompt,
                'category': 'period_evening',
                'note': 'Should parse as evening time'
            })
    
    # === CATEGORY 3: Date Formats (100 cases) ===
    print("Generating date format cases...")
    date_formats = [
        ('20.10', 'DD.MM'),
        ('15/12', 'DD/MM'),
        ('01-06', 'DD-MM'),
        ('25.12.2025', 'DD.MM.YYYY'),
        ('31/01/2026', 'DD/MM/YYYY'),
        ('15-03-2025', 'DD-MM-YYYY')
    ]
    
    for i in range(100):
        date_str, format_type = random.choice(date_formats)
        hour = random.randint(6, 22)
        event = random.choice(events)
        
        variations = [
            f"{event} {hour}h ngày {date_str}",
            f"{hour}h {date_str} {event}",
            f"{hour}h vào ngày {date_str} {event}",
            f"{event} vào {hour}h ngày {date_str}",
            f"ngày {date_str} lúc {hour}h {event}"
        ]
        
        prompt = random.choice(variations)
        test_cases.append({
            'id': len(test_cases) + 1,
            'input': prompt,
            'category': 'date_format',
            'note': f'Date format: {format_type}'
        })
    
    # === CATEGORY 4: Missing Components (100 cases) ===
    print("Generating missing component cases...")
    
    # Missing time
    for i in range(25):
        event = random.choice(events)
        prompt = f"tôi có {event} ngày mai"
        test_cases.append({
            'id': len(test_cases) + 1,
            'input': prompt,
            'category': 'missing_time',
            'note': 'Has event and date, missing specific time'
        })
    
    # Missing location (should be OK)
    for i in range(25):
        wd = random.choice(random.choice(weekdays))
        hour = random.randint(8, 18)
        event = random.choice(events)
        prompt = f"{wd} {hour}h {event}"
        test_cases.append({
            'id': len(test_cases) + 1,
            'input': prompt,
            'category': 'missing_location',
            'note': 'Has event and time, no location (should be OK)'
        })
    
    # Missing event name
    for i in range(25):
        wd = random.choice(random.choice(weekdays))
        hour = random.randint(8, 18)
        prompt = f"{wd} {hour}h"
        test_cases.append({
            'id': len(test_cases) + 1,
            'input': prompt,
            'category': 'missing_event',
            'note': 'Has time only, missing event name - should FAIL'
        })
    
    # Only event name
    for i in range(25):
        event = random.choice(events)
        prompt = f"tôi có {event}"
        test_cases.append({
            'id': len(test_cases) + 1,
            'input': prompt,
            'category': 'only_event',
            'note': 'Has event only, missing time - should FAIL'
        })
    
    # === CATEGORY 5: Period Markers (100 cases) ===
    print("Generating period marker cases...")
    periods = [
        ('sáng', [6, 7, 8, 9, 10, 11]),
        ('trưa', [12]),
        ('chiều', [1, 2, 3, 4, 5]),
        ('tối', [6, 7, 8, 9, 10, 11]),
        ('đêm', [10, 11, 12])
    ]
    
    for i in range(100):
        period, valid_hours = random.choice(periods)
        hour = random.choice(valid_hours)
        event = random.choice(events)
        wd = random.choice(random.choice(weekdays))
        
        variations = [
            f"{hour}h {period} {event}",
            f"{event} {hour}h {period}",
            f"{wd} {hour}h {period} {event}",
            f"{hour} giờ {period} {event}",
            f"{event} lúc {hour}h {period}"
        ]
        
        prompt = random.choice(variations)
        test_cases.append({
            'id': len(test_cases) + 1,
            'input': prompt,
            'category': 'period_marker',
            'note': f'Period: {period}, hour: {hour}'
        })
    
    # === CATEGORY 6: Relative Dates (100 cases) ===
    print("Generating relative date cases...")
    relative_dates = [
        'hôm nay', 'ngày mai', 'mai', 'ngày kia', 'mai mốt', 
        'tuần sau', 'tuần tới', 'tháng sau', 'tháng tới',
        'cuối tuần', 'cuối tuần này', 'cuối tuần sau'
    ]
    
    for i in range(100):
        rel_date = random.choice(relative_dates)
        hour = random.randint(6, 22)
        event = random.choice(events)
        
        variations = [
            f"{event} {rel_date} lúc {hour}h",
            f"{hour}h {rel_date} {event}",
            f"{rel_date} {hour}h tôi có {event}",
            f"tôi {event} {rel_date} {hour}h"
        ]
        
        prompt = random.choice(variations)
        test_cases.append({
            'id': len(test_cases) + 1,
            'input': prompt,
            'category': 'relative_date',
            'note': f'Relative: {rel_date}'
        })
    
    # === CATEGORY 7: Complex Time Expressions (100 cases) ===
    print("Generating complex time expressions...")
    
    # Time ranges
    for i in range(25):
        start_h = random.randint(8, 14)
        end_h = start_h + random.randint(1, 4)
        event = random.choice(events)
        prompt = f"{event} từ {start_h}h đến {end_h}h"
        test_cases.append({
            'id': len(test_cases) + 1,
            'input': prompt,
            'category': 'time_range',
            'note': f'Range: {start_h}h-{end_h}h'
        })
    
    # Compressed format: 17h30, 8h45
    for i in range(25):
        hour = random.randint(6, 22)
        minute = random.choice([0, 15, 30, 45])
        event = random.choice(events)
        prompt = f"{event} {hour}h{minute:02d}"
        test_cases.append({
            'id': len(test_cases) + 1,
            'input': prompt,
            'category': 'compressed_time',
            'note': f'Format: {hour}h{minute:02d}'
        })
    
    # Duration expressions
    for i in range(25):
        duration = random.randint(1, 7)
        unit = random.choice(['ngày', 'tuần', 'tháng'])
        event = random.choice(events)
        prompt = f"{event} trong {duration} {unit}"
        test_cases.append({
            'id': len(test_cases) + 1,
            'input': prompt,
            'category': 'duration',
            'note': f'Duration: {duration} {unit}'
        })
    
    # Special times: rưỡi, kém
    for i in range(25):
        hour = random.randint(7, 20)
        event = random.choice(events)
        if i % 2 == 0:
            prompt = f"{event} {hour}h rưỡi"
        else:
            kems = random.randint(5, 15)
            prompt = f"{event} {hour}h kém {kems}"
        test_cases.append({
            'id': len(test_cases) + 1,
            'input': prompt,
            'category': 'special_time',
            'note': 'rưỡi or kém format'
        })
    
    # === CATEGORY 8: Location Variations (100 cases) ===
    print("Generating location cases...")
    locations = [
        'phòng 302', 'tầng 5', 'toà A', 'văn phòng', 
        'bệnh viện Bạch Mai', 'công ty', 'nhà hàng ABC',
        'quán cafe', 'trung tâm thương mại', 'sân bay'
    ]
    
    for i in range(100):
        hour = random.randint(8, 20)
        event = random.choice(events)
        location = random.choice(locations)
        wd = random.choice(random.choice(weekdays))
        
        variations = [
            f"{event} {hour}h tại {location}",
            f"{hour}h {event} ở {location}",
            f"{wd} {hour}h {event} tại {location}",
            f"{event} tại {location} lúc {hour}h",
            f"đến {location} {hour}h {event}"
        ]
        
        prompt = random.choice(variations)
        test_cases.append({
            'id': len(test_cases) + 1,
            'input': prompt,
            'category': 'with_location',
            'note': f'Location: {location}'
        })
    
    # === CATEGORY 9: Reminder/Notification (50 cases) ===
    print("Generating reminder cases...")
    reminder_phrases = [
        'nhắc trước 15 phút',
        'nhắc trước 30 phút',
        'nhắc trước 1 giờ',
        'nhắc trước 60 phút',
        'nhắc tôi trước 10 phút'
    ]
    
    for i in range(50):
        hour = random.randint(8, 18)
        event = random.choice(events)
        reminder = random.choice(reminder_phrases)
        prompt = f"{event} {hour}h {reminder}"
        test_cases.append({
            'id': len(test_cases) + 1,
            'input': prompt,
            'category': 'with_reminder',
            'note': f'Reminder: {reminder}'
        })
    
    # === CATEGORY 10: Typos and Variations (100 cases) ===
    print("Generating typo and variation cases...")
    
    # Missing diacritics
    typo_variations = [
        ('hop', 'họp'),
        ('phong van', 'phỏng vấn'),
        ('gap khach', 'gặp khách'),
        ('lam viec', 'làm việc'),
        ('sang', 'sáng'),
        ('chieu', 'chiều'),
        ('toi', 'tối'),
    ]
    
    for i in range(50):
        typo, correct = random.choice(typo_variations)
        hour = random.randint(8, 20)
        wd = random.choice(random.choice(weekdays))
        prompt = f"{wd} {hour}h {typo}"
        test_cases.append({
            'id': len(test_cases) + 1,
            'input': prompt,
            'category': 'typo_no_diacritics',
            'note': f'Typo: {typo} (should be {correct})'
        })
    
    # Mixed case
    for i in range(50):
        hour = random.randint(8, 20)
        event = random.choice(events).upper()
        wd = random.choice(random.choice(weekdays)).upper()
        prompt = f"{wd} {hour}H {event}"
        test_cases.append({
            'id': len(test_cases) + 1,
            'input': prompt,
            'category': 'mixed_case',
            'note': 'UPPERCASE or MixedCase'
        })
    
    # === CATEGORY 11: Edge Cases - Same Day (50 cases) ===
    print("Generating same-day edge cases...")
    
    # Today is Thursday (2025-11-06)
    # Test "thứ 5" - should it be today or next week?
    for i in range(25):
        hour = random.randint(8, 22)
        event = random.choice(events)
        prompt = f"thứ 5 {hour}h {event}"  # Thursday
        test_cases.append({
            'id': len(test_cases) + 1,
            'input': prompt,
            'category': 'same_weekday',
            'note': 'Today is Thursday - should parse as today or next week?'
        })
    
    # "hôm nay" edge cases
    for i in range(25):
        hour = random.randint(8, 22)
        event = random.choice(events)
        prompt = f"hôm nay {hour}h {event}"
        test_cases.append({
            'id': len(test_cases) + 1,
            'input': prompt,
            'category': 'today_explicit',
            'note': 'Explicitly "hôm nay" (today)'
        })
    
    # === CATEGORY 12: Week Navigation (50 cases) ===
    print("Generating week navigation cases...")
    
    for i in range(50):
        wd = random.choice(random.choice(weekdays))
        hour = random.randint(8, 20)
        event = random.choice(events)
        
        if i % 2 == 0:
            prompt = f"{wd} tuần sau {hour}h {event}"
        else:
            prompt = f"{wd} {hour}h tuần sau {event}"
        
        test_cases.append({
            'id': len(test_cases) + 1,
            'input': prompt,
            'category': 'next_week',
            'note': 'Explicit "tuần sau"'
        })
    
    # === CATEGORY 13: Empty/Invalid Inputs (50 cases) ===
    print("Generating invalid input cases...")
    
    invalid_inputs = [
        '',  # Empty
        '   ',  # Whitespace
        'abc',  # Random text
        '12345',  # Just numbers
        'họp',  # Just event name
        '10h',  # Just time
        'tôi',  # Just pronoun
        'ngày mai',  # Just date
        'phòng 302',  # Just location
        'nhắc trước 15 phút',  # Just reminder
    ]
    
    for i in range(50):
        prompt = random.choice(invalid_inputs)
        test_cases.append({
            'id': len(test_cases) + 1,
            'input': prompt,
            'category': 'invalid_input',
            'note': 'Should fail gracefully'
        })
    
    print(f"\nTotal test cases generated: {len(test_cases)}")
    return test_cases

def save_test_cases(test_cases, filename='tests/edge_case_tests_1000.json'):
    """Save test cases to JSON file"""
    output = {
        'metadata': {
            'total_cases': len(test_cases),
            'generated_at': datetime.now().isoformat(),
            'categories': list(set(tc['category'] for tc in test_cases))
        },
        'test_cases': test_cases
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Saved {len(test_cases)} test cases to {filename}")
    
    # Print category breakdown
    print("\nCategory breakdown:")
    category_counts = {}
    for tc in test_cases:
        cat = tc['category']
        category_counts[cat] = category_counts.get(cat, 0) + 1
    
    for cat, count in sorted(category_counts.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count}")

if __name__ == '__main__':
    print("Generating 1000 edge case test prompts...\n")
    test_cases = generate_edge_cases()
    save_test_cases(test_cases)
    print("\n✅ Done!")
