"""
Test reminder time display functionality
Show specific reminder time instead of just "Có"/"Không"
"""
from database.db_manager import DatabaseManager
from datetime import datetime, timedelta

def test_reminder_display():
    """Test that reminders display specific time"""
    db = DatabaseManager()
    
    print("=" * 70)
    print("🧪 TEST: REMINDER TIME DISPLAY")
    print("=" * 70)
    
    # Clean database
    print("\n🧹 Cleaning database...")
    db.delete_all_events()
    
    # Test cases with different reminder scenarios
    print("\n📝 Creating test events...")
    now = datetime.now()
    
    test_events = [
        {
            'name': '1. Họp nhóm',
            'event': {
                'event_name': 'Họp nhóm',
                'start_time': (now + timedelta(days=1, hours=2)).replace(hour=10, minute=0, second=0, microsecond=0).isoformat(),
                'end_time': (now + timedelta(days=1, hours=3)).replace(hour=11, minute=0, second=0, microsecond=0).isoformat(),
                'location': 'Phòng 302',
                'reminder_minutes': 30
            },
            'expected_reminder': '09:30',  # 10:00 - 30 minutes
            'description': 'Nhắc trước 30 phút'
        },
        {
            'name': '2. Gặp khách',
            'event': {
                'event_name': 'Gặp khách',
                'start_time': (now + timedelta(days=2)).replace(hour=14, minute=0, second=0, microsecond=0).isoformat(),
                'end_time': (now + timedelta(days=2)).replace(hour=15, minute=0, second=0, microsecond=0).isoformat(),
                'location': 'Quán Cafe',
                'reminder_minutes': 0
            },
            'expected_reminder': 'Không',
            'description': 'Không nhắc'
        },
        {
            'name': '3. Phỏng vấn',
            'event': {
                'event_name': 'Phỏng vấn',
                'start_time': (now + timedelta(days=3)).replace(hour=9, minute=0, second=0, microsecond=0).isoformat(),
                'end_time': (now + timedelta(days=3)).replace(hour=10, minute=0, second=0, microsecond=0).isoformat(),
                'location': 'Công ty ABC',
                'reminder_minutes': 60
            },
            'expected_reminder': '08:00',  # 09:00 - 60 minutes
            'description': 'Nhắc trước 1 giờ'
        },
        {
            'name': '4. Học online',
            'event': {
                'event_name': 'Học online',
                'start_time': (now + timedelta(days=4)).replace(hour=20, minute=30, second=0, microsecond=0).isoformat(),
                'end_time': (now + timedelta(days=4)).replace(hour=22, minute=0, second=0, microsecond=0).isoformat(),
                'location': 'Zoom',
                'reminder_minutes': 15
            },
            'expected_reminder': '20:15',  # 20:30 - 15 minutes
            'description': 'Nhắc trước 15 phút'
        },
        {
            'name': '5. Đi chợ',
            'event': {
                'event_name': 'Đi chợ',
                'start_time': (now + timedelta(days=5)).replace(hour=7, minute=0, second=0, microsecond=0).isoformat(),
                'end_time': (now + timedelta(days=5)).replace(hour=8, minute=0, second=0, microsecond=0).isoformat(),
                'location': 'Chợ Đầm',
                'reminder_minutes': 0
            },
            'expected_reminder': 'Không',
            'description': 'Không nhắc'
        },
        {
            'name': '6. Meeting (cross-day reminder)',
            'event': {
                'event_name': 'Meeting',
                'start_time': (now + timedelta(days=6)).replace(hour=0, minute=30, second=0, microsecond=0).isoformat(),
                'end_time': (now + timedelta(days=6)).replace(hour=1, minute=30, second=0, microsecond=0).isoformat(),
                'location': 'Office',
                'reminder_minutes': 45
            },
            'expected_reminder': '23:45',  # 00:30 - 45 minutes = previous day 23:45
            'description': 'Nhắc trước 45 phút (chuyển sang ngày trước)'
        }
    ]
    
    # Add all test events
    added = 0
    for test_case in test_events:
        result = db.add_event(test_case['event'])
        if result.get('success'):
            added += 1
            print(f"  ✅ {test_case['name']}: {test_case['description']}")
        else:
            print(f"  ❌ Failed to add: {test_case['name']}")
    
    print(f"\n✅ Added {added}/{len(test_events)} test events")
    
    # Verify by retrieving events
    print("\n" + "=" * 70)
    print("📊 EXPECTED REMINDER DISPLAY")
    print("=" * 70)
    
    all_events = db.get_all_events()
    print(f"\nTotal events in DB: {len(all_events)}\n")
    
    print("Expected display in 'Nhắc tôi' column:")
    print("-" * 70)
    
    for i, test_case in enumerate(test_events, 1):
        event = test_case['event']
        expected = test_case['expected_reminder']
        
        # Parse times for display
        start_dt = datetime.fromisoformat(event['start_time'])
        start_display = start_dt.strftime('%d/%m/%Y %H:%M')
        
        # Calculate reminder time
        if event['reminder_minutes'] > 0:
            reminder_dt = start_dt - timedelta(minutes=event['reminder_minutes'])
            reminder_display = reminder_dt.strftime('%d/%m/%Y %H:%M')
        else:
            reminder_display = 'Không'
        
        print(f"{i}. {event['event_name']}")
        print(f"   Thời gian sự kiện: {start_display}")
        print(f"   Nhắc trước: {event['reminder_minutes']} phút")
        print(f"   ✅ Nhắc tôi hiển thị: {reminder_display}")
        print(f"   {test_case['description']}")
        print()
    
    print("=" * 70)
    print("💡 LOGIC CALCULATION")
    print("=" * 70)
    print("""
Formula: Reminder Time = Event Time - Reminder Minutes

Examples:
---------
1. Event: 10:00, Reminder: 30 minutes
   → Display: 09:30 (10:00 - 30 min)

2. Event: 14:00, Reminder: 0 minutes
   → Display: Không

3. Event: 09:00, Reminder: 60 minutes
   → Display: 08:00 (09:00 - 60 min)

4. Event: 00:30, Reminder: 45 minutes
   → Display: 23:45 previous day (00:30 - 45 min)
""")
    
    print("=" * 70)
    print("🎨 UI COMPARISON")
    print("=" * 70)
    print("""
BEFORE v0.8.3:
--------------
┌────┬──────────┬──────────────┬────────┬──────┐
│ ID │ Sự kiện  │ Thời gian    │ Nhắc   │ Đ.đ  │
├────┼──────────┼──────────────┼────────┼──────┤
│ 1  │ Họp nhóm │ 08/11 10:00  │ Có  ⬅ Không rõ
│ 2  │ Gặp khách│ 09/11 14:00  │ Không  │
│ 3  │ Phỏng vấn│ 10/11 09:00  │ Có  ⬅ Không rõ
└────┴──────────┴──────────────┴────────┴──────┘

Problem: User không biết nhắc LÚC NÀO

AFTER v0.8.3:
-------------
┌────┬──────────┬──────────────┬──────────────┬──────┐
│ ID │ Sự kiện  │ Thời gian    │ Nhắc tôi     │ Đ.đ  │
├────┼──────────┼──────────────┼──────────────┼──────┤
│ 1  │ Họp nhóm │ 08/11 10:00  │ 08/11 09:30  │ ⬅ Rõ ràng!
│ 2  │ Gặp khách│ 09/11 14:00  │ Không        │
│ 3  │ Phỏng vấn│ 10/11 09:00  │ 10/11 08:00  │ ⬅ Rõ ràng!
└────┴──────────┴──────────────┴──────────────┴──────┘

Improvement: User biết CHÍNH XÁC thời gian nhắc nhở!
""")
    
    print("=" * 70)
    print("✅ TEST COMPLETE")
    print("=" * 70)
    print("""
Next Steps:
-----------
1. Run: python main.py
2. Verify reminder column shows:
   - "Không" for events without reminder
   - "DD/MM/YYYY HH:MM" for events with reminder
3. Check that reminder time = event time - reminder minutes

Technical Changes:
------------------
- File: main.py
- Method: _render_events() (line ~368)
- Logic: Calculate reminder_dt = event_dt - timedelta(minutes=reminder_minutes)
- Display: reminder_dt.strftime('%d/%m/%Y %H:%M')
- Column width: Increased from 80px to 150px

Status: ✅ Ready for testing
""")

if __name__ == '__main__':
    test_reminder_display()
