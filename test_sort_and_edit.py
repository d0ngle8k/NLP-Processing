"""
Test sorting and edit functionality
"""
from database.db_manager import DatabaseManager
from datetime import datetime, timedelta

def test_edit_function():
    """Test if edit function works with correct key"""
    db = DatabaseManager()
    
    # Clean test environment
    print("🧹 Cleaning test data...")
    db.delete_all_events()
    
    # Add test event
    print("\n📝 Adding test event...")
    test_event = {
        'event_name': 'Test Meeting Original',
        'start_time': '2025-11-10T10:00:00',
        'end_time': '2025-11-10T11:00:00',
        'location': 'Room 101',
        'reminder_minutes': 15
    }
    
    result = db.add_event(test_event)
    if not result.get('success'):
        print(f"❌ Failed to add test event: {result}")
        return False
    
    print(f"✅ Event added successfully")
    
    # Get the event by querying (since add doesn't return ID)
    all_events = db.get_all_events()
    if not all_events:
        print("❌ No events found after adding")
        return False
    
    event_id = all_events[0]['id']
    print(f"✅ Retrieved event with ID: {event_id}")
    
    # Update event (simulate edit save)
    print(f"\n🔧 Updating event ID {event_id}...")
    update_payload = {
        'event_name': 'Test Meeting UPDATED',  # Must use 'event_name', not 'event'
        'start_time': '2025-11-10T14:00:00',
        'end_time': '2025-11-10T15:00:00',
        'location': 'Room 202',
        'reminder_minutes': 30
    }
    
    update_result = db.update_event(event_id, update_payload)
    
    if not update_result.get('success'):
        print(f"❌ Failed to update event: {update_result}")
        return False
    
    print(f"✅ Update successful!")
    
    # Verify update
    print(f"\n🔍 Verifying update...")
    updated_event = db.get_event_by_id(event_id)
    
    if not updated_event:
        print(f"❌ Could not retrieve updated event ID {event_id}")
        return False
    
    checks = [
        ('Event name', updated_event.get('event_name'), 'Test Meeting UPDATED'),
        ('Start time', updated_event.get('start_time'), '2025-11-10T14:00:00'),
        ('Location', updated_event.get('location'), 'Room 202'),
        ('Reminder', updated_event.get('reminder_minutes'), 30)
    ]
    
    all_pass = True
    for field, actual, expected in checks:
        if actual == expected:
            print(f"  ✅ {field}: {actual}")
        else:
            print(f"  ❌ {field}: Expected '{expected}', Got '{actual}'")
            all_pass = False
    
    return all_pass

def test_sorting_data():
    """Create diverse test data for sorting validation"""
    db = DatabaseManager()
    
    print("\n📊 Creating sorting test data...")
    db.delete_all_events()
    
    now = datetime.now()
    
    # Diverse test events for sorting
    test_events = [
        # ID will auto-increment
        # Mix of numbers, letters, special chars in event names
        {'event_name': '123 Meeting', 'start_time': (now + timedelta(days=1)).isoformat(), 'end_time': (now + timedelta(days=1, hours=1)).isoformat(), 'location': 'Room A', 'reminder_minutes': 0},
        {'event_name': 'Abc Conference', 'start_time': (now + timedelta(days=2)).isoformat(), 'end_time': (now + timedelta(days=2, hours=2)).isoformat(), 'location': '1st Floor', 'reminder_minutes': 15},
        {'event_name': 'abc meeting', 'start_time': (now + timedelta(days=5)).isoformat(), 'end_time': (now + timedelta(days=5, hours=1)).isoformat(), 'location': 'Zoom', 'reminder_minutes': 0},
        {'event_name': 'Zoom Call', 'start_time': (now + timedelta(hours=2)).isoformat(), 'end_time': (now + timedelta(hours=3)).isoformat(), 'location': 'Online', 'reminder_minutes': 30},
        {'event_name': '999 Review', 'start_time': (now + timedelta(days=10)).isoformat(), 'end_time': (now + timedelta(days=10, hours=1)).isoformat(), 'location': '', 'reminder_minutes': 0},
        {'event_name': 'Bbb Workshop', 'start_time': (now + timedelta(hours=1)).isoformat(), 'end_time': (now + timedelta(hours=2)).isoformat(), 'location': 'Room B', 'reminder_minutes': 60},
        {'event_name': 'AAA Priority', 'start_time': (now + timedelta(days=30)).isoformat(), 'end_time': (now + timedelta(days=30, hours=1)).isoformat(), 'location': '2nd Floor', 'reminder_minutes': 0},
        {'event_name': '1on1 Chat', 'start_time': (now + timedelta(hours=5)).isoformat(), 'end_time': (now + timedelta(hours=6)).isoformat(), 'location': 'Coffee Shop', 'reminder_minutes': 10},
    ]
    
    added_count = 0
    for event in test_events:
        result = db.add_event(event)
        if result.get('success'):
            added_count += 1
        else:
            print(f"  ⚠️ Failed to add: {event['event_name']}")
    
    print(f"✅ Added {added_count}/{len(test_events)} test events")
    
    # Display events
    all_events = db.get_all_events()
    print(f"\n📋 Created Events (ID order):")
    for ev in all_events:
        print(f"  ID {ev['id']}: {ev['event_name']} | {ev['start_time'][:16]} | {ev.get('location') or '(no loc)'} | Remind: {ev.get('reminder_minutes', 0)}")
    
    return True

def validate_sorting_logic():
    """Test sorting logic manually"""
    print("\n🧪 Testing Sort Logic:")
    
    # Test alphanumeric sorting
    test_names = ['123 Meeting', 'Abc Conf', 'abc meeting', 'Zoom', '999 Review', 'Bbb Work', 'AAA Priority', '1on1']
    
    def alphanumeric_key(name):
        name = name.strip()
        if not name:
            return (2, '')
        first_char = name[0]
        if first_char.isdigit():
            return (0, name.lower())
        else:
            return (1, name.lower())
    
    sorted_names = sorted(test_names, key=alphanumeric_key)
    print("  Alphanumeric Sort (numbers first):")
    for i, name in enumerate(sorted_names, 1):
        print(f"    {i}. {name}")
    
    # Expected: 123 Meeting, 1on1, 999 Review, AAA Priority, Abc Conf, abc meeting, Bbb Work, Zoom
    expected_order = ['123 Meeting', '1on1', '999 Review', 'AAA Priority', 'Abc Conf', 'abc meeting', 'Bbb Work', 'Zoom']
    
    if sorted_names == expected_order:
        print("  ✅ Alphanumeric sorting correct!")
    else:
        print(f"  ❌ Expected: {expected_order}")
        print(f"  ❌ Got: {sorted_names}")
    
    return sorted_names == expected_order

if __name__ == '__main__':
    print("=" * 60)
    print("🧪 TESTING SORT AND EDIT FUNCTIONALITY")
    print("=" * 60)
    
    # Test 1: Edit function
    print("\n" + "=" * 60)
    print("TEST 1: Edit Function (event_name key)")
    print("=" * 60)
    edit_pass = test_edit_function()
    
    # Test 2: Create sorting test data
    print("\n" + "=" * 60)
    print("TEST 2: Create Sorting Test Data")
    print("=" * 60)
    sort_data_pass = test_sorting_data()
    
    # Test 3: Validate sorting logic
    print("\n" + "=" * 60)
    print("TEST 3: Validate Sorting Logic")
    print("=" * 60)
    sort_logic_pass = validate_sorting_logic()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Edit Function: {'✅ PASS' if edit_pass else '❌ FAIL'}")
    print(f"Sort Data Creation: {'✅ PASS' if sort_data_pass else '❌ FAIL'}")
    print(f"Sort Logic Validation: {'✅ PASS' if sort_logic_pass else '❌ FAIL'}")
    
    overall = edit_pass and sort_data_pass and sort_logic_pass
    print(f"\nOverall: {'✅ ALL TESTS PASSED' if overall else '❌ SOME TESTS FAILED'}")
    
    print("\n💡 Next Steps:")
    print("1. Run 'python main.py' to test UI")
    print("2. Click on column headers to test sorting")
    print("3. Select an event and click 'Sửa' to test edit")
    print("4. Verify sorting behavior:")
    print("   - ID: Low→High, then High→Low")
    print("   - Event: Numbers→A/a→B/b...")
    print("   - Time: Nearest→Farthest")
    print("   - Remind: No→Yes toggle")
    print("   - Location: Numbers→Letters (like Event)")
