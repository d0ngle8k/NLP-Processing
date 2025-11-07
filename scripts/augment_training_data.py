"""
Generate additional training data focusing on edge cases
"""
import json
from pathlib import Path

# Edge case patterns to add
edge_cases = [
    # ===== WEEKDAY PATTERNS (t2, t3, t5, cn) =====
    {"input": "t2 8h sáng họp", "expected": {"event": "họp", "time_str": "t2 8h sáng", "location": None, "reminder_minutes": 0}},
    {"input": "t3 10h họp nhóm", "expected": {"event": "họp nhóm", "time_str": "t3 10h", "location": None, "reminder_minutes": 0}},
    {"input": "t5 9h30 đi làm", "expected": {"event": "đi làm", "time_str": "t5 9h30", "location": None, "reminder_minutes": 0}},
    {"input": "t7 chiều đi chơi", "expected": {"event": "đi chơi", "time_str": "t7 chiều", "location": None, "reminder_minutes": 0}},
    {"input": "cn 10h sáng họp gia đình", "expected": {"event": "họp gia đình", "time_str": "cn 10h sáng", "location": None, "reminder_minutes": 0}},
    {"input": "chu nhat 8h chạy bộ", "expected": {"event": "chạy bộ", "time_str": "chu nhat 8h", "location": None, "reminder_minutes": 0}},
    {"input": "thứ 2 14h họp công ty", "expected": {"event": "họp công ty", "time_str": "thứ 2 14h", "location": None, "reminder_minutes": 0}},
    {"input": "thứ hai 9h sáng đi học", "expected": {"event": "đi học", "time_str": "thứ hai 9h sáng", "location": None, "reminder_minutes": 0}},
    {"input": "thứ ba 10h họp", "expected": {"event": "họp", "time_str": "thứ ba 10h", "location": None, "reminder_minutes": 0}},
    {"input": "thứ năm 15h gặp khách", "expected": {"event": "gặp khách", "time_str": "thứ năm 15h", "location": None, "reminder_minutes": 0}},
    
    # ===== "O" INSTEAD OF "Ở" (NO DIACRITICS) =====
    {"input": "hop nhom 10h o phong 302", "expected": {"event": "hop nhom", "time_str": "10h", "location": "phong 302", "reminder_minutes": 0}},
    {"input": "di hoc 8h sang o truong", "expected": {"event": "di hoc", "time_str": "8h sang", "location": "truong", "reminder_minutes": 0}},
    {"input": "gap ban 9h o cafe", "expected": {"event": "gap ban", "time_str": "9h", "location": "cafe", "reminder_minutes": 0}},
    {"input": "hop 14h o van phong", "expected": {"event": "hop", "time_str": "14h", "location": "van phong", "reminder_minutes": 0}},
    {"input": "an com 12h trua o nha hang", "expected": {"event": "an com", "time_str": "12h trua", "location": "nha hang", "reminder_minutes": 0}},
    {"input": "lam viec 9h sang o cong ty", "expected": {"event": "lam viec", "time_str": "9h sang", "location": "cong ty", "reminder_minutes": 0}},
    {"input": "tap gym 18h o phong tap", "expected": {"event": "tap gym", "time_str": "18h", "location": "phong tap", "reminder_minutes": 0}},
    {"input": "5h chieu o truong ham tu di hoc", "expected": {"event": "di hoc", "time_str": "5h chieu", "location": "truong ham tu", "reminder_minutes": 0}},
    {"input": "8h toi o quan an voi ban", "expected": {"event": "an voi ban", "time_str": "8h toi", "location": "quan", "reminder_minutes": 0}},
    {"input": "t5 10h o benh vien kham benh", "expected": {"event": "kham benh", "time_str": "t5 10h", "location": "benh vien", "reminder_minutes": 0}},
    
    # ===== TIME PERIODS (CHIỀU, TỐI, SÁNG) =====
    {"input": "6h chieu hop", "expected": {"event": "hop", "time_str": "6h chieu", "location": None, "reminder_minutes": 0}},
    {"input": "7h toi di an", "expected": {"event": "di an", "time_str": "7h toi", "location": None, "reminder_minutes": 0}},
    {"input": "8h sang tap the duc", "expected": {"event": "tap the duc", "time_str": "8h sang", "location": None, "reminder_minutes": 0}},
    {"input": "12h trua an com", "expected": {"event": "an com", "time_str": "12h trua", "location": None, "reminder_minutes": 0}},
    {"input": "chieu mai di cho", "expected": {"event": "di cho", "time_str": "chieu mai", "location": None, "reminder_minutes": 0}},
    {"input": "sang nay tap yoga", "expected": {"event": "tap yoga", "time_str": "sang nay", "location": None, "reminder_minutes": 0}},
    {"input": "toi mai xem phim", "expected": {"event": "xem phim", "time_str": "toi mai", "location": None, "reminder_minutes": 0}},
    {"input": "sang thu 2 di lam", "expected": {"event": "di lam", "time_str": "sang thu 2", "location": None, "reminder_minutes": 0}},
    {"input": "chieu chu nhat nghi ngoi", "expected": {"event": "nghi ngoi", "time_str": "chieu chu nhat", "location": None, "reminder_minutes": 0}},
    {"input": "5 gio chieu gap khach", "expected": {"event": "gap khach", "time_str": "5 gio chieu", "location": None, "reminder_minutes": 0}},
    
    # ===== LOCATIONS WITHOUT MARKERS =====
    {"input": "10h sang mai hop cong ty ABC", "expected": {"event": "hop", "time_str": "10h sang mai", "location": "cong ty ABC", "reminder_minutes": 0}},
    {"input": "8h hoc truong dai hoc", "expected": {"event": "hoc", "time_str": "8h", "location": "truong dai hoc", "reminder_minutes": 0}},
    {"input": "14h kham benh vien Bach Mai", "expected": {"event": "kham", "time_str": "14h", "location": "benh vien Bach Mai", "reminder_minutes": 0}},
    {"input": "9h lam viec van phong lau 5", "expected": {"event": "lam viec", "time_str": "9h", "location": "van phong lau 5", "reminder_minutes": 0}},
    {"input": "12h an com nha hang Sai Gon", "expected": {"event": "an com", "time_str": "12h", "location": "nha hang Sai Gon", "reminder_minutes": 0}},
    {"input": "15h gap ban quan cafe", "expected": {"event": "gap ban", "time_str": "15h", "location": "quan cafe", "reminder_minutes": 0}},
    {"input": "18h tap gym phong the thao", "expected": {"event": "tap gym", "time_str": "18h", "location": "phong the thao", "reminder_minutes": 0}},
    {"input": "7h chay bo cong vien", "expected": {"event": "chay bo", "time_str": "7h", "location": "cong vien", "reminder_minutes": 0}},
    {"input": "20h xem phim rap chieu phim", "expected": {"event": "xem phim", "time_str": "20h", "location": "rap chieu phim", "reminder_minutes": 0}},
    {"input": "11h mua sam sieu thi", "expected": {"event": "mua sam", "time_str": "11h", "location": "sieu thi", "reminder_minutes": 0}},
    
    # ===== COMBINED PATTERNS =====
    {"input": "t2 8h sang hop o van phong", "expected": {"event": "hop", "time_str": "t2 8h sang", "location": "van phong", "reminder_minutes": 0}},
    {"input": "t5 5h chieu gap khach o cafe", "expected": {"event": "gap khach", "time_str": "t5 5h chieu", "location": "cafe", "reminder_minutes": 0}},
    {"input": "cn 10h sang le nha tho", "expected": {"event": "le", "time_str": "cn 10h sang", "location": "nha tho", "reminder_minutes": 0}},
    {"input": "thu 3 chieu di cho voi me", "expected": {"event": "di cho voi me", "time_str": "thu 3 chieu", "location": None, "reminder_minutes": 0}},
    {"input": "t7 toi xem phim rap CGV", "expected": {"event": "xem phim", "time_str": "t7 toi", "location": "rap CGV", "reminder_minutes": 0}},
    {"input": "thứ 6 sang tap yoga phong gym", "expected": {"event": "tap yoga", "time_str": "thứ 6 sang", "location": "phong gym", "reminder_minutes": 0}},
    {"input": "chu nhat chieu an tiec nha hang", "expected": {"event": "an tiec", "time_str": "chu nhat chieu", "location": "nha hang", "reminder_minutes": 0}},
    {"input": "t2 9h o phong hop tang 3", "expected": {"event": "hop", "time_str": "t2 9h", "location": "phong hop tang 3", "reminder_minutes": 0}},
    {"input": "t4 14h gap doi tac van phong ABC", "expected": {"event": "gap doi tac", "time_str": "t4 14h", "location": "van phong ABC", "reminder_minutes": 0}},
    {"input": "thứ năm 7h toi an com nha", "expected": {"event": "an com", "time_str": "thứ năm 7h toi", "location": "nha", "reminder_minutes": 0}},
    
    # ===== TYPO VARIATIONS =====
    {"input": "thứ bah 10h sang hop", "expected": {"event": "hop", "time_str": "thứ bah 10h sang", "location": None, "reminder_minutes": 0}},
    {"input": "thứ tuh 8h di hoc", "expected": {"event": "di hoc", "time_str": "thứ tuh 8h", "location": None, "reminder_minutes": 0}},
    {"input": "thứ namh 9h lam viec", "expected": {"event": "lam viec", "time_str": "thứ namh 9h", "location": None, "reminder_minutes": 0}},
    {"input": "thứ sauh 10h tap gym", "expected": {"event": "tap gym", "time_str": "thứ sauh 10h", "location": None, "reminder_minutes": 0}},
    {"input": "thứ bayh 11h di choi", "expected": {"event": "di choi", "time_str": "thứ bayh 11h", "location": None, "reminder_minutes": 0}},
    {"input": "chu nhat tamh gio sang le", "expected": {"event": "le", "time_str": "chu nhat tamh gio sang", "location": None, "reminder_minutes": 0}},
    {"input": "t5 muoih gio hop", "expected": {"event": "hop", "time_str": "t5 muoih gio", "location": None, "reminder_minutes": 0}},
    {"input": "thứ haih 9h di lam", "expected": {"event": "di lam", "time_str": "thứ haih 9h", "location": None, "reminder_minutes": 0}},
    {"input": "thứ bonh 8h sang hoc", "expected": {"event": "hoc", "time_str": "thứ bonh 8h sang", "location": None, "reminder_minutes": 0}},
    {"input": "cn chinh gio chieu nghi", "expected": {"event": "nghi", "time_str": "cn chinh gio chieu", "location": None, "reminder_minutes": 0}},
    
    # ===== WITH REMINDERS =====
    {"input": "t2 9h hop o van phong nhac truoc 30 phut", "expected": {"event": "hop", "time_str": "t2 9h", "location": "van phong", "reminder_minutes": 30}},
    {"input": "t5 5h chieu gap khach nhac 1 gio truoc", "expected": {"event": "gap khach", "time_str": "t5 5h chieu", "location": None, "reminder_minutes": 60}},
    {"input": "cn 8h sang le nha tho nhac som hon 15 phut", "expected": {"event": "le", "time_str": "cn 8h sang", "location": "nha tho", "reminder_minutes": 15}},
    {"input": "thu 3 14h kham benh nhac truoc 2 gio", "expected": {"event": "kham benh", "time_str": "thu 3 14h", "location": None, "reminder_minutes": 120}},
    {"input": "6h chieu hop o phong 302 nhac 45 phut truoc", "expected": {"event": "hop", "time_str": "6h chieu", "location": "phong 302", "reminder_minutes": 45}},
]

# Load existing test cases
test_file = Path("tests/extended_test_cases.json")
with open(test_file, 'r', encoding='utf-8') as f:
    existing_cases = json.load(f)

print(f"📊 Existing test cases: {len(existing_cases)}")
print(f"➕ Adding edge cases: {len(edge_cases)}")

# Append new cases
all_cases = existing_cases + edge_cases
total = len(all_cases)

print(f"✅ Total test cases: {total}")

# Save augmented dataset
with open(test_file, 'w', encoding='utf-8') as f:
    json.dump(all_cases, f, indent=2, ensure_ascii=False)

print(f"💾 Saved to: {test_file}")
print(f"\n📈 Data augmentation complete!")
print(f"   - Weekday patterns: ~20 cases")
print(f"   - 'o' instead of 'ở': ~10 cases")
print(f"   - Time periods: ~10 cases")
print(f"   - Locations without markers: ~10 cases")
print(f"   - Combined patterns: ~10 cases")
print(f"   - Typo variations: ~10 cases")
print(f"   - With reminders: ~5 cases")
