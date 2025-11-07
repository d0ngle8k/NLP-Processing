"""
Generate 100K+ edge case training data for PhoBERT fine-tuning
Focus: Extreme typos, reversed orders, rare patterns, regional variants
"""

import json
import random
from datetime import datetime, timedelta

# Vietnamese word mappings
WEEKDAYS = {
    'full': ['thứ hai', 'thứ ba', 'thứ tư', 'thứ năm', 'thứ sáu', 'thứ bảy', 'chủ nhật'],
    'short': ['t2', 't3', 't4', 't5', 't6', 't7', 'cn'],
    'no_diacritic': ['thu hai', 'thu ba', 'thu tu', 'thu nam', 'thu sau', 'thu bay', 'chu nhat'],
    'typo_h': ['thứ haih', 'thứ bah', 'thứ tuh', 'thứ namh', 'thứ sauh', 'thứ bayh'],
    'extreme_typo': ['thur hai', 'thua ba', 'thuw tu', 'thuu nam', 'thux sau', 'thuy bay'],
}

NUMBERS = {
    'digit': list(range(1, 25)),
    'word': ['một', 'hai', 'ba', 'bốn', 'năm', 'sáu', 'bảy', 'tám', 'chín', 'mười', 'mười một', 'mười hai'],
    'no_diacritic': ['mot', 'hai', 'ba', 'bon', 'nam', 'sau', 'bay', 'tam', 'chin', 'muoi', 'muoi mot', 'muoi hai'],
    'typo_h': ['moth', 'haih', 'bah', 'bonh', 'namh', 'sauh', 'bayh', 'tamh', 'chinh', 'muoih'],
    'extreme_typo': ['moat', 'hhai', 'baa', 'bown', 'naem', 'xau', 'byay', 'taam', 'chien', 'muuoi'],
}

PERIODS = {
    'full': ['sáng', 'trưa', 'chiều', 'tối', 'đêm', 'khuya'],
    'no_diacritic': ['sang', 'trua', 'chieu', 'toi', 'dem', 'khuya'],
    'short': ['s', 'tr', 'ch', 't', 'd'],
}

EVENTS = [
    'họp nhóm', 'họp team', 'họp khách', 'họp ban giám đốc',
    'đi làm', 'đi học', 'đi khám bệnh', 'đi chợ', 'đi cafe', 'đi ăn',
    'gặp bạn', 'gặp khách', 'gặp đối tác',
    'làm báo cáo', 'làm bài tập', 'làm việc',
    'ăn sáng', 'ăn trưa', 'ăn tối', 'ăn nhẹ',
    'chạy bộ', 'tập gym', 'đá bóng', 'bơi lội',
    'xem phim', 'nghe nhạc', 'đọc sách',
    'nộp hồ sơ', 'ký hợp đồng', 'phỏng vấn',
]

LOCATIONS = [
    'văn phòng', 'công ty', 'trường học', 'bệnh viện', 'nhà hàng',
    'quán cafe', 'siêu thị', 'chợ', 'công viên', 'sân bay',
    'tầng 5', 'phòng 302', 'toà A', 'khu B',
    'Hà Nội', 'Sài Gòn', 'Đà Nẵng',
]

RELATIVE_TIME = [
    'hôm nay', 'ngày mai', 'ngày kia', 'mai', 'hôm qua',
    'tuần sau', 'tuần tới', 'tháng sau', 'năm sau',
]

def generate_extreme_typos(word):
    """Generate creative typos"""
    typos = [word]  # Original
    
    # Missing chars
    if len(word) > 3:
        typos.append(word[:2] + word[3:])  # "chieu" → "cheu"
    
    # Double chars
    if len(word) > 2:
        idx = random.randint(1, len(word)-1)
        typos.append(word[:idx] + word[idx] + word[idx:])  # "cafe" → "caafe"
    
    # Swap adjacent
    if len(word) > 2:
        idx = random.randint(0, len(word)-2)
        chars = list(word)
        chars[idx], chars[idx+1] = chars[idx+1], chars[idx]
        typos.append(''.join(chars))  # "hop" → "hpo"
    
    # Add 'h' suffix (common Vietnamese typo)
    if word[-1] in 'aiou':
        typos.append(word + 'h')
    
    return random.choice(typos)

def generate_reversed_patterns(count=10000):
    """Reversed word order patterns"""
    samples = []
    base_date = datetime(2025, 11, 7)
    
    for i in range(count):
        # Pattern 1: Period + Number + Weekday (chiều 3h thứ 5)
        weekday = random.choice(WEEKDAYS['full'] + WEEKDAYS['short'])
        period = random.choice(PERIODS['full'] + PERIODS['no_diacritic'])
        hour = random.choice(NUMBERS['digit'][:12])
        event = random.choice(EVENTS)
        location = random.choice(LOCATIONS) if random.random() > 0.5 else None
        
        text_parts = [period, f"{hour}h", weekday, event]
        if location:
            text_parts.append(f"ở {location}")
        
        # Calculate datetime
        days_ahead = WEEKDAYS['full'].index(weekday) + 1 if weekday in WEEKDAYS['full'] else random.randint(1, 7)
        target_date = base_date + timedelta(days=days_ahead)
        hour_24 = hour + (12 if period in ['chiều', 'chieu', 'tối', 'toi'] and hour < 12 else 0)
        
        sample = {
            "text": " ".join(text_parts),
            "event": event,
            "start_time": target_date.replace(hour=hour_24, minute=0).isoformat(),
            "location": location,
            "reminder_minutes": 0
        }
        samples.append(sample)
    
    return samples

def generate_extreme_typo_patterns(count=20000):
    """Extreme typo combinations"""
    samples = []
    base_date = datetime(2025, 11, 7)
    
    for i in range(count):
        # Random typo intensity (20-80% of words have typos)
        typo_rate = random.uniform(0.2, 0.8)
        
        weekday = random.choice(WEEKDAYS['full'] + WEEKDAYS['typo_h'] + WEEKDAYS['extreme_typo'])
        number = random.choice(NUMBERS['word'] + NUMBERS['typo_h'] + NUMBERS['extreme_typo'])
        period = random.choice(PERIODS['full'] + PERIODS['no_diacritic'])
        event = random.choice(EVENTS)
        
        # Apply typos
        if random.random() < typo_rate:
            weekday = generate_extreme_typos(weekday)
        if random.random() < typo_rate:
            number = generate_extreme_typos(number)
        if random.random() < typo_rate:
            period = generate_extreme_typos(period)
        
        text = f"{weekday} {number} gio {period} {event}"
        
        # Calculate datetime (approximate)
        hour = 10  # Default fallback
        try:
            hour_idx = NUMBERS['word'].index(number) if number in NUMBERS['word'] else 10
            hour = hour_idx + 1
        except:
            pass
        
        hour_24 = hour + (12 if 'chieu' in period.lower() or 'toi' in period.lower() else 0)
        target_date = base_date + timedelta(days=random.randint(1, 7))
        
        sample = {
            "text": text,
            "event": event,
            "start_time": target_date.replace(hour=hour_24 % 24, minute=0).isoformat(),
            "location": None,
            "reminder_minutes": 0
        }
        samples.append(sample)
    
    return samples

def generate_triple_combinations(count=20000):
    """Weekday + Period + Number + Location combinations"""
    samples = []
    base_date = datetime(2025, 11, 7)
    
    for i in range(count):
        weekday = random.choice(WEEKDAYS['full'] + WEEKDAYS['short'] + WEEKDAYS['no_diacritic'])
        period = random.choice(PERIODS['full'] + PERIODS['no_diacritic'])
        hour = random.choice(NUMBERS['digit'][:15])
        event = random.choice(EVENTS)
        location = random.choice(LOCATIONS)
        reminder = random.choice([0, 15, 30, 60]) if random.random() > 0.7 else 0
        
        # Vary order randomly
        orders = [
            f"{weekday} {period} {hour}h {event} ở {location}",
            f"{period} {weekday} {hour}h {event} tại {location}",
            f"{hour}h {period} {weekday} {event} o {location}",
            f"{event} {weekday} {hour}h {period} tại {location}",
        ]
        text = random.choice(orders)
        
        if reminder > 0:
            text += f" nhắc {reminder} phút trước"
        
        # Calculate datetime
        days_ahead = random.randint(1, 7)
        target_date = base_date + timedelta(days=days_ahead)
        hour_24 = hour + (12 if period in ['chiều', 'chieu', 'tối', 'toi', 'đêm', 'dem'] and hour < 12 else 0)
        
        sample = {
            "text": text,
            "event": event,
            "start_time": target_date.replace(hour=hour_24 % 24, minute=0).isoformat(),
            "location": location,
            "reminder_minutes": reminder
        }
        samples.append(sample)
    
    return samples

def generate_rare_patterns(count=20000):
    """Rare/unusual patterns"""
    samples = []
    base_date = datetime(2025, 11, 7)
    
    rare_templates = [
        # Range times
        lambda: f"họp từ {random.randint(8,11)}h đến {random.randint(12,15)}h {random.choice(RELATIVE_TIME)}",
        # No explicit time
        lambda: f"{random.choice(PERIODS['full'])} {random.choice(RELATIVE_TIME)} {random.choice(EVENTS)}",
        # Multiple events
        lambda: f"{random.randint(8,10)}h {random.choice(EVENTS)} và {random.choice(EVENTS)}",
        # Complex location
        lambda: f"{random.randint(8,17)}h {random.choice(EVENTS)} tại {random.choice(LOCATIONS)} khu {random.choice(['A', 'B', 'C'])} phòng {random.randint(101,501)}",
        # Reminder without time
        lambda: f"{random.choice(EVENTS)} nhắc trước 1 giờ",
    ]
    
    for i in range(count):
        template = random.choice(rare_templates)
        text = template()
        
        sample = {
            "text": text,
            "event": random.choice(EVENTS),
            "start_time": (base_date + timedelta(days=1, hours=10)).isoformat(),
            "location": random.choice([None, random.choice(LOCATIONS)]),
            "reminder_minutes": random.choice([0, 15, 30, 60])
        }
        samples.append(sample)
    
    return samples

def generate_regional_variants(count=20000):
    """Regional pronunciation variants"""
    samples = []
    base_date = datetime(2025, 11, 7)
    
    # Southern Vietnamese variants
    southern_mappings = {
        'thứ': 'thớ', 'giờ': 'zờ', 'trưa': 'chưa',
        'sáng': 'xáng', 'chiều': 'giều',
    }
    
    for i in range(count):
        text = f"{random.choice(WEEKDAYS['full'])} {random.randint(7,18)}h {random.choice(PERIODS['full'])} {random.choice(EVENTS)}"
        
        # Apply regional variants
        for std, regional in southern_mappings.items():
            if random.random() > 0.5:
                text = text.replace(std, regional)
        
        sample = {
            "text": text,
            "event": random.choice(EVENTS),
            "start_time": (base_date + timedelta(days=random.randint(1, 7), hours=10)).isoformat(),
            "location": None,
            "reminder_minutes": 0
        }
        samples.append(sample)
    
    return samples

def main():
    print("🚀 Generating 100K+ edge case training data...")
    
    all_samples = []
    
    print("📝 Generating reversed patterns (10K)...")
    all_samples.extend(generate_reversed_patterns(10000))
    
    print("📝 Generating extreme typo patterns (20K)...")
    all_samples.extend(generate_extreme_typo_patterns(20000))
    
    print("📝 Generating triple combinations (20K)...")
    all_samples.extend(generate_triple_combinations(20000))
    
    print("📝 Generating rare patterns (20K)...")
    all_samples.extend(generate_rare_patterns(20000))
    
    print("📝 Generating regional variants (20K)...")
    all_samples.extend(generate_regional_variants(20000))
    
    # Shuffle
    random.shuffle(all_samples)
    
    # Add IDs
    for i, sample in enumerate(all_samples):
        sample['id'] = i + 1
    
    # Save
    output_file = "tests/extended_test_cases_100k.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_samples, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Generated {len(all_samples)} samples")
    print(f"💾 Saved to {output_file}")
    print(f"📊 File size: {len(json.dumps(all_samples, ensure_ascii=False)) / 1024 / 1024:.2f} MB")
    
    # Sample preview
    print("\n📋 Sample preview (first 3):")
    for sample in all_samples[:3]:
        print(f"  - {sample['text']}")

if __name__ == "__main__":
    main()
