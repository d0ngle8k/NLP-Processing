"""
Script to generate extended test cases for NLP pipeline
Covers: diacritics, no diacritics, uppercase, lowercase, mixed case, edge cases

Now supports generating an arbitrary number of cases via --count (default 1000)
and custom output via --output. A fixed --seed ensures reproducibility.
"""
import json
import random
import argparse

def _generate_base_test_cases():
    """
    Generate a diverse base pool of test cases across categories.
    Returns a list typically > 1000 items to allow sampling/slicing.
    """
    test_cases = []
    
    # 1. Basic events with diacritics variations (100 cases)
    events_diacritic = [
        ("Họp nhóm", "hop nhom", "HỌP NHÓM", "HoP nHoM"),
        ("Đi khám bệnh", "di kham benh", "ĐI KHÁM BỆNH", "Đi KhÁm BeNh"),
        ("Ăn trưa", "an trua", "ĂN TRƯA", "ĂN tRưA"),
        ("Gặp khách", "gap khach", "GẶP KHÁCH", "gẶp KhÁcH"),
        ("Sinh nhật", "sinh nhat", "SINH NHẬT", "SiNh NhẬt"),
        ("Học tiếng Anh", "hoc tieng anh", "HỌC TIẾNG ANH", "HọC TiẾnG AnH"),
        ("Đá bóng", "da bong", "ĐÁ BÓNG", "đÁ BóNg"),
        ("Phỏng vấn", "phong van", "PHỎNG VẤN", "PhỎnG VấN"),
        ("Nộp báo cáo", "nop bao cao", "NỘP BÁO CÁO", "NộP BáO CáO"),
        ("Mua sắm", "mua sam", "MUA SẮM", "MuA SắM"),
    ]
    
    times = ["10h sáng mai", "8:30 ngày mai", "12 giờ hôm nay", "14h", "tối mai", "18:00 thứ 2 tuần sau"]
    locations = ["phòng 302", "bệnh viện bạch mai", None, "quán cà phê", "nhà", "sân A2"]
    reminders = [0, 15, 30, 60]
    
    for event_tuple in events_diacritic:
        for variant in event_tuple:
            time = random.choice(times)
            location = random.choice(locations)
            reminder = random.choice(reminders)
            
            input_parts = [variant, time]
            expected_event = variant.lower()
            
            if location:
                input_parts.append(f"tại {location}")
            if reminder > 0:
                input_parts.append(f"nhắc trước {reminder} phút")
            
            test_cases.append({
                "input": " ".join(input_parts),
                "expected": {
                    "event": expected_event,
                    "time_str": time,
                    "location": location.lower() if location else None,
                    "reminder_minutes": reminder
                }
            })
    
    # 2. Time expressions with variations (200 cases)
    time_expressions = [
        ("sáng", "sang", "SÁNG", "SÁng"),
        ("trưa", "trua", "TRƯA", "TrƯa"),
        ("chiều", "chieu", "CHIỀU", "ChIềU"),
        ("tối", "toi", "TỐI", "TốI"),
        ("đêm", "dem", "ĐÊM", "ĐêM"),
        ("mai", "mai", "MAI", "MaI"),
        ("hôm nay", "hom nay", "HÔM NAY", "HôM NaY"),
        ("ngày mai", "ngay mai", "NGÀY MAI", "NgÀy MaI"),
        ("thứ 2", "thu 2", "THỨ 2", "ThỨ 2"),
        ("thứ 3", "thu 3", "THỨ 3", "ThỨ 3"),
    ]
    
    base_events = ["Họp", "Gặp mặt", "Làm việc", "Học bài", "Đi chơi"]
    
    for i in range(200):
        event = random.choice(base_events)
        time_variant = random.choice(time_expressions)
        time_str = f"{random.randint(6, 22)}h {random.choice(time_variant)}"
        
        test_cases.append({
            "input": f"{event} {time_str}",
            "expected": {
                "event": event.lower(),
                "time_str": time_str,
                "location": None,
                "reminder_minutes": 0
            }
        })
    
    # 3. Location variations (150 cases)
    location_variations = [
        ("Hà Nội", "ha noi", "HÀ NỘI", "Hà nỘi"),
        ("Sài Gòn", "sai gon", "SÀI GÒN", "SàI GòN"),
        ("Đà Nẵng", "da nang", "ĐÀ NẴNG", "Đà nẴnG"),
        ("phòng họp", "phong hop", "PHÒNG HỌP", "PhÒnG HọP"),
        ("bệnh viện", "benh vien", "BỆNH VIỆN", "BệNh ViệN"),
        ("quán cà phê", "quan ca phe", "QUÁN CÀ PHÊ", "QuÁn Cà PhÊ"),
        ("công viên", "cong vien", "CÔNG VIÊN", "CôNg ViÊn"),
        ("siêu thị", "sieu thi", "SIÊU THỊ", "SiÊu ThỊ"),
        ("trường học", "truong hoc", "TRƯỜNG HỌC", "TrƯờNg HọC"),
        ("văn phòng", "van phong", "VĂN PHÒNG", "VăN PhÒnG"),
    ]
    
    for i in range(150):
        event = random.choice(["Gặp gỡ", "Họp", "Làm việc", "Học"])
        loc_variant = random.choice(location_variations)
        location = random.choice(loc_variant)
        time = f"{random.randint(7, 20)}h"
        
        test_cases.append({
            "input": f"{event} {time} tại {location}",
            "expected": {
                "event": event.lower(),
                "time_str": time,
                "location": location.lower(),
                "reminder_minutes": 0
            }
        })
    
    # 4. Reminder variations (100 cases)
    reminder_texts = [
        ("nhắc trước", "nhac truoc", "NHẮC TRƯỚC"),
        ("nhắc sớm hơn", "nhac som hon", "NHẮC SỚM HƠN"),
        ("nhắc", "nhac", "NHẮC"),
    ]
    
    for i in range(100):
        event = random.choice(["Họp", "Phỏng vấn", "Gặp khách"])
        time = f"{random.randint(8, 18)}h sáng mai"
        reminder_text = random.choice([item for sublist in reminder_texts for item in sublist])
        minutes = random.choice([5, 10, 15, 30, 60, 120])
        unit = "phút" if minutes < 60 else "giờ"
        value = minutes if minutes < 60 else minutes // 60
        
        test_cases.append({
            "input": f"{event} {time} {reminder_text} {value} {unit}",
            "expected": {
                "event": event.lower(),
                "time_str": time,
                "location": None,
                "reminder_minutes": minutes
            }
        })
    
    # 5. Edge cases - special characters and numbers (100 cases)
    special_events = [
        "Họp #team-backend",
        "Review PR #123",
        "Meeting @CEO",
        "Gặp khách VIP-001",
        "Học C++ programming",
        "Training .NET Core",
        "Workshop AI/ML",
        "Seminar IoT & Cloud",
        "Đi khám COVID-19",
        "Tiêm vaccine mũi 3",
    ]
    
    for i in range(100):
        event = random.choice(special_events)
        time = f"{random.randint(8, 20)}h"
        
        test_cases.append({
            "input": f"{event} {time} hôm nay",
            "expected": {
                "event": event.lower(),
                "time_str": f"{time} hôm nay",
                "location": None,
                "reminder_minutes": 0
            }
        })
    
    # 6. Date format variations (100 cases)
    date_formats = [
        "ngày 6 tháng 12",
        "6/12",
        "06-12",
        "6.12",
        "12/6",
        "ngày 6/12",
        "6 tháng 12",
        "thứ 2 tuần sau",
        "thứ hai tuần tới",
        "T2 tuần sau",
    ]
    
    for i in range(100):
        event = random.choice(["Họp", "Gặp", "Làm việc", "Học"])
        time = f"{random.randint(7, 22)}h"
        date = random.choice(date_formats)
        
        test_cases.append({
            "input": f"{event} {time} {date}",
            "expected": {
                "event": event.lower(),
                "time_str": f"{time} {date}",
                "location": None,
                "reminder_minutes": 0
            }
        })
    
    # 7. Mixed diacritics in same sentence (50 cases)
    mixed_inputs = [
        "HỌP nhóm lúc 10h SÁNG mai ở PHÒNG 302",
        "ĐI khám bệnh 8:30 NGÀY mai tại bệnh viện BẠCH Mai",
        "ĂN trưa LÚC 12 giờ HÔM nay",
        "GẶP khách 14h ngày 6 THÁNG 12 tại QUÁN cà phê",
        "SINH nhật mẹ TỐI mai ở NHÀ",
    ]
    
    for _ in range(10):
        for mixed in mixed_inputs:
            test_cases.append({
                "input": mixed,
                "expected": {
                    "event": "event_extracted",  # Will be normalized
                    "time_str": "time_extracted",
                    "location": None,
                    "reminder_minutes": 0
                }
            })
    
    # 8. Very long event names (50 cases)
    long_events = [
        "Họp triển khai dự án xây dựng hệ thống quản lý nhân sự tích hợp AI và Machine Learning",
        "Hội thảo khoa học quốc tế về ứng dụng công nghệ thông tin trong giáo dục đại học",
        "Workshop đào tạo kỹ năng lập trình Python nâng cao cho sinh viên năm cuối",
        "Buổi gặp gỡ trao đổi kinh nghiệm phát triển sản phẩm công nghệ với các chuyên gia",
        "Lễ ký kết hợp tác chiến lược giữa công ty và đối tác nước ngoài",
    ]
    
    for _ in range(10):
        for event in long_events:
            time = f"{random.randint(8, 17)}h sáng mai"
            test_cases.append({
                "input": f"{event} {time}",
                "expected": {
                    "event": event.lower(),
                    "time_str": time,
                    "location": None,
                    "reminder_minutes": 0
                }
            })
    
    # 9. Ambiguous time expressions (50 cases)
    ambiguous = [
        "Họp sáng",  # No specific hour
        "Gặp chiều mai",
        "Làm việc tối nay",
        "Học đêm nay",
        "Đi chơi cuối tuần",
        "Nộp báo cáo tuần sau",
        "Review code tháng này",
        "Meeting quý 4",
        "Training năm sau",
        "Workshop mùa hè",
    ]
    
    for _ in range(5):
        for amb in ambiguous:
            test_cases.append({
                "input": amb,
                "expected": {
                    "event": "event_extracted",
                    "time_str": "time_extracted",
                    "location": None,
                    "reminder_minutes": 0
                }
            })
    
    # 10. Multiple locations mentioned (50 cases)
    multi_location = [
        "Họp ở Hà Nội sau đó bay vào Sài Gòn 10h sáng mai",
        "Gặp khách tại văn phòng rồi đi ăn trưa ở nhà hàng 14h",
        "Học tại trường sau đó về nhà 18h",
        "Training ở phòng 302 chuyển sang phòng 401 lúc 15h",
        "Meeting online từ nhà sau đó ra công ty 9h",
    ]
    
    for _ in range(10):
        for multi in multi_location:
            test_cases.append({
                "input": multi,
                "expected": {
                    "event": "event_extracted",
                    "time_str": "time_extracted",
                    "location": "first_location_extracted",
                    "reminder_minutes": 0
                }
            })
    
    # 11. No time specified (edge case - 50 cases)
    no_time_events = [
        "Họp nhóm dự án",
        "Gặp khách hàng",
        "Đi khám bệnh",
        "Học tiếng Anh",
        "Mua sắm",
        "Nấu ăn",
        "Dọn nhà",
        "Tập thể dục",
        "Đọc sách",
        "Viết báo cáo",
    ]
    
    for _ in range(5):
        for event in no_time_events:
            test_cases.append({
                "input": event,
                "expected": {
                    "event": event.lower(),
                    "time_str": None,
                    "location": None,
                    "reminder_minutes": 0
                }
            })
    
    # 12. Typos and common mistakes (50 cases)
    typos = [
        "Họpp nhómm 10hh sángg maiii",
        "Gặp kháchhh 14hhh",
        "Điii khámm bệnhhh 8:300",
        "Ănnn trưaaa 12 giờơơ",
        "Họccc tiếngg Anhhhh",
    ]
    
    for _ in range(10):
        for typo in typos:
            test_cases.append({
                "input": typo,
                "expected": {
                    "event": "event_with_typo",
                    "time_str": "time_extracted_or_none",
                    "location": None,
                    "reminder_minutes": 0
                }
            })
    
    # 13. Empty and whitespace cases (10 cases)
    edge_empty = [
        "",
        "   ",
        "\t\t",
        "\n\n",
        "     10h     ",
        "mai",
        "tại",
        "nhắc trước",
        "ở",
        "lúc",
    ]
    
    for edge in edge_empty:
        test_cases.append({
            "input": edge,
            "expected": {
                "event": None,
                "time_str": None if edge.strip() not in ["10h", "mai"] else edge.strip(),
                "location": None,
                "reminder_minutes": 0
            }
        })
    
    # 14. Very short inputs (20 cases)
    short_inputs = [
        "Họp 10h", "Gặp 14h", "Học 18h", "Đi 7h",
        "A 10h", "B 15h", "X 20h", "Y 9h",
        "H 11h", "G 16h", "D 8h", "L 19h",
        "Họp", "Gặp", "Học", "Đi",
        "10h", "14h", "18h", "7h"
    ]
    
    for short in short_inputs:
        parts = short.split()
        test_cases.append({
            "input": short,
            "expected": {
                "event": parts[0].lower() if len(parts) > 1 else (parts[0].lower() if not parts[0].endswith('h') else None),
                "time_str": parts[1] if len(parts) > 1 else (parts[0] if parts[0].endswith('h') else None),
                "location": None,
                "reminder_minutes": 0
            }
        })
    
    # 15. Numbers as words (30 cases)
    number_words = [
        "Họp lúc mười giờ sáng",
        "Gặp lúc hai giờ chiều",
        "Học lúc tám giờ tối",
        "Đi lúc bảy giờ sáng",
        "Họp lúc mười một giờ",
        "Gặp lúc năm giờ chiều",
    ]
    
    for _ in range(5):
        for num_word in number_words:
            test_cases.append({
                "input": num_word,
                "expected": {
                    "event": "event_extracted",
                    "time_str": "time_as_words",
                    "location": None,
                    "reminder_minutes": 0
                }
            })
    
    return test_cases


def generate_extended_test_cases(count: int, seed: int | None = 42):
    """
    Generate 'count' test cases. If the base pool is smaller than 'count',
    top up by sampling from the base pool (duplicates allowed) to reach the target size.
    """
    if seed is not None:
        random.seed(seed)

    base = _generate_base_test_cases()
    if count <= len(base):
        return base[:count]

    # Need more: sample additional items from the base to reach desired size
    extra = []
    need = count - len(base)
    for _ in range(need):
        extra.append(random.choice(base))
    return base + extra


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate extended NLP test cases")
    parser.add_argument("--count", type=int, default=1000, help="Number of test cases to generate (default: 1000)")
    parser.add_argument("--output", type=str, default="tests/extended_test_cases.json", help="Output JSON file path")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility (default: 42)")
    args = parser.parse_args()

    test_cases = generate_extended_test_cases(args.count, args.seed)

    output_file = args.output
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(test_cases, f, ensure_ascii=False, indent=2)

    print(f"Generated {len(test_cases)} test cases")
    print(f"Saved to: {output_file}")

    # Statistics
    with_location = sum(1 for tc in test_cases if tc["expected"]["location"] is not None)
    with_reminder = sum(1 for tc in test_cases if tc["expected"]["reminder_minutes"] > 0)
    with_time = sum(1 for tc in test_cases if tc["expected"]["time_str"] is not None)

    print(f"\nStatistics:")
    print(f"  - Cases with location: {with_location}")
    print(f"  - Cases with reminder: {with_reminder}")
    print(f"  - Cases with time: {with_time}")
    print(f"  - Cases without time: {len(test_cases) - with_time}")
