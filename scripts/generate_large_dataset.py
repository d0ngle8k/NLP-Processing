"""
Generate Large Training Dataset (10,000 samples)
Focus on failure modes and edge cases
"""
import json
import random
from pathlib import Path
from datetime import datetime, timedelta

# Load existing extended dataset
existing_file = Path(__file__).parent.parent / "tests" / "extended_test_cases.json"
with open(existing_file, 'r', encoding='utf-8') as f:
    existing_data = json.load(f)

print(f"📂 Loaded {len(existing_data)} existing samples")

# Template structures
EVENTS = [
    'họp', 'hop', 'họp nhóm', 'hop nhom', 'họp team', 'họp ban giám đốc',
    'đi', 'di', 'đi học', 'di hoc', 'đi làm', 'di lam', 'đi khám bệnh',
    'ăn', 'an', 'ăn tối', 'an toi', 'ăn trưa', 'an trua', 'đi ăn',
    'gặp', 'gap', 'gặp bạn', 'gap ban', 'gặp khách', 'gap khach',
    'học', 'hoc', 'học tiếng Anh', 'hoc tieng Anh', 'học piano',
    'chạy', 'chay', 'chạy bộ', 'chay bo', 'tập gym', 'tap gym',
    'làm', 'lam', 'làm báo cáo', 'lam bao cao', 'làm việc',
    'dự', 'du', 'dự hội nghị', 'du hoi nghi', 'dự tiệc',
    'đọc', 'doc', 'đọc sách', 'doc sach', 'viết', 'viet',
    'nấu', 'nau', 'nấu ăn', 'nau an', 'nấu cơm',
]

LOCATIONS = [
    'phòng 302', 'phong 302', 'phòng 401', 'tầng 5 toà A', 'tang 5 toa A',
    'công ty', 'cong ty', 'công ty ABC', 'văn phòng', 'van phong',
    'trường', 'truong', 'trường ham tu', 'truong ham tu', 'trường đại học',
    'bệnh viện', 'benh vien', 'bệnh viện Bạch Mai', 'bệnh viện Việt Đức',
    'nhà hàng', 'nha hang', 'nhà hàng Sài Gòn', 'quán', 'quan',
    'quán cafe', 'quan cafe', 'cafe', 'café', 'quán ăn',
    'sân bay', 'san bay', 'sân bay Nội Bài', 'bến xe',
    'công viên', 'cong vien', 'công viên Thống Nhất',
    'siêu thị', 'sieu thi', 'chợ', 'cho', 'chợ Bến Thành',
    'nhà', 'nha', 'nhà tôi', 'nhà bạn', 'ký túc xá',
]

WEEKDAYS = ['thứ 2', 'thứ 3', 'thứ 4', 'thứ 5', 'thứ 6', 'thứ 7', 'chủ nhật']
WEEKDAYS_SHORT = ['t2', 't3', 't4', 't5', 't6', 't7', 'cn']
WEEKDAYS_NO_DIACRITICS = ['thu 2', 'thu 3', 'thu 4', 'thu 5', 'thu 6', 'thu 7', 'chu nhat']

NUMBER_WORDS = ['một', 'hai', 'ba', 'bốn', 'năm', 'sáu', 'bảy', 'tám', 'chín', 'mười', 'mười một', 'mười hai']
NUMBER_WORDS_TYPO = ['moth', 'haih', 'bah', 'bonh', 'namh', 'sauh', 'bayh', 'tamh', 'chinh', 'muoih']

PERIODS = ['sáng', 'trưa', 'chiều', 'tối', 'đêm']
PERIODS_NO_DIACRITICS = ['sang', 'trua', 'chieu', 'toi', 'dem']

RELATIVE_DAYS = ['hôm nay', 'ngày mai', 'mai', 'ngày kia']
RELATIVE_DAYS_NO_DIACRITICS = ['hom nay', 'ngay mai', 'mai', 'ngay kia']

LOCATION_MARKERS = ['ở', 'o', 'tại', 'tai']
TIME_CONNECTORS = ['vào', 'vao', 'lúc', 'luc']

def generate_datetime(base=None):
    """Generate random datetime"""
    if base is None:
        base = datetime.now()
    days_ahead = random.randint(0, 7)
    hour = random.randint(6, 22)
    minute = random.choice([0, 15, 30, 45])
    return base + timedelta(days=days_ahead, hours=hour-base.hour, minutes=minute-base.minute)

def format_time(dt, use_period=True, use_number_words=False, use_typos=False):
    """Format time in various Vietnamese styles"""
    hour = dt.hour
    minute = dt.minute
    
    # Determine period
    if hour < 12:
        period = random.choice(PERIODS[:1]) if use_period else ''  # sáng
    elif hour < 13:
        period = random.choice(PERIODS[1:2]) if use_period else ''  # trưa
    elif hour < 18:
        period = random.choice(PERIODS[2:3]) if use_period else ''  # chiều
    else:
        period = random.choice(PERIODS[3:]) if use_period else ''  # tối/đêm
    
    # Convert to 12-hour if needed
    if hour > 12 and period:
        hour = hour - 12
    elif hour == 0:
        hour = 12
    
    # Format hour
    if use_number_words and hour <= 12:
        if use_typos and random.random() < 0.3:
            # Use typo version
            hour_str = random.choice(NUMBER_WORDS_TYPO[:hour])
        else:
            hour_str = NUMBER_WORDS[hour - 1]
        time_str = f"{hour_str} giờ"
    else:
        time_str = f"{hour}h" if minute == 0 else f"{hour}h{minute:02d}"
    
    if period:
        if random.random() < 0.5:
            return f"{time_str} {period}"
        else:
            return f"{period} {time_str}"  # Reversed order
    return time_str

def generate_sample():
    """Generate one training sample"""
    event = random.choice(EVENTS)
    location = random.choice(LOCATIONS) if random.random() < 0.7 else None
    
    # Generate datetime
    dt = generate_datetime()
    
    # Format time with variations
    use_period = random.random() < 0.7
    use_number_words = random.random() < 0.2
    use_typos = random.random() < 0.1
    time_str = format_time(dt, use_period, use_number_words, use_typos)
    
    # Add weekday (30% chance)
    weekday_str = ''
    if random.random() < 0.3:
        weekday_choice = random.choice(['full', 'short', 'no_diacritics'])
        if weekday_choice == 'full':
            weekday_str = random.choice(WEEKDAYS)
        elif weekday_choice == 'short':
            weekday_str = random.choice(WEEKDAYS_SHORT)
        else:
            weekday_str = random.choice(WEEKDAYS_NO_DIACRITICS)
    
    # Add relative day (40% chance)
    relative_day = ''
    if random.random() < 0.4 and not weekday_str:
        if random.random() < 0.3:
            relative_day = random.choice(RELATIVE_DAYS_NO_DIACRITICS)
        else:
            relative_day = random.choice(RELATIVE_DAYS)
    
    # Reminder (20% chance)
    reminder_minutes = 0
    reminder_str = ''
    if random.random() < 0.2:
        reminder_minutes = random.choice([15, 30, 60])
        if reminder_minutes == 60:
            reminder_str = 'nhắc 1 giờ trước'
        else:
            reminder_str = f'nhắc {reminder_minutes} phút trước'
    
    # Construct sentence with various patterns
    patterns = []
    
    # Pattern 1: [weekday] [time] [period] [event] [location] [reminder]
    if weekday_str:
        patterns.append(f"{weekday_str} {time_str} {event}" + 
                       (f" {random.choice(LOCATION_MARKERS)} {location}" if location else "") +
                       (f" {reminder_str}" if reminder_str else ""))
    
    # Pattern 2: [relative_day] [time] [event] [location] [reminder]
    if relative_day:
        patterns.append(f"{relative_day} {time_str} {event}" + 
                       (f" {random.choice(LOCATION_MARKERS)} {location}" if location else "") +
                       (f" {reminder_str}" if reminder_str else ""))
    
    # Pattern 3: [event] [time] [period] [weekday/relative] [location] [reminder]
    if weekday_str or relative_day:
        day_ref = weekday_str or relative_day
        patterns.append(f"{event} {time_str} {day_ref}" + 
                       (f" {random.choice(LOCATION_MARKERS)} {location}" if location else "") +
                       (f" {reminder_str}" if reminder_str else ""))
    
    # Pattern 4: [time] [event] [location]
    patterns.append(f"{time_str} {event}" + 
                   (f" {random.choice(LOCATION_MARKERS)} {location}" if location else "") +
                   (f" {reminder_str}" if reminder_str else ""))
    
    # Choose random pattern
    if not patterns:
        # Fallback simple pattern
        text = f"{time_str} {event}"
        if location:
            text += f" {random.choice(LOCATION_MARKERS)} {location}"
        if reminder_str:
            text += f" {reminder_str}"
    else:
        text = random.choice(patterns)
    
    return {
        "text": text.strip(),
        "event": event,
        "start_time": dt.isoformat(),
        "location": location,
        "reminder_minutes": reminder_minutes
    }

# Generate new samples
new_samples = []
target_count = 10000

print(f"🔄 Generating {target_count - len(existing_data)} new samples...")

while len(existing_data) + len(new_samples) < target_count:
    sample = generate_sample()
    new_samples.append(sample)
    
    if len(new_samples) % 1000 == 0:
        print(f"  Generated {len(new_samples)} samples...")

# Combine and save
all_samples = existing_data + new_samples
output_file = Path(__file__).parent.parent / "tests" / "extended_test_cases_10000.json"

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(all_samples, f, ensure_ascii=False, indent=2)

print(f"✅ Generated {len(all_samples)} total samples")
print(f"📊 Breakdown:")
print(f"   Existing: {len(existing_data)}")
print(f"   New: {len(new_samples)}")
print(f"💾 Saved to: {output_file}")
