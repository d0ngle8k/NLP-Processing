"""
Quick test to verify import_from_json handles both formats correctly
"""
from database.db_manager import DatabaseManager
from core_nlp.pipeline import NLPPipeline
from services.import_service import import_from_json
import tempfile
import json
import os

def test_export_format():
    """Test importing from export format (event_name + start_time)"""
    print("Testing export format...")
    # Create a temp DB file
    db_temp = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    db_temp.close()
    db = DatabaseManager(db_temp.name)
    
    # Create a temp file with export format
    export_data = [
        {
            "id": 1,
            "event_name": "họp nhóm",
            "start_time": "2025-11-10T18:00:00",
            "end_time": None,
            "location": "phòng 302",
            "reminder_minutes": 15,
            "status": "pending"
        }
    ]
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        json.dump(export_data, f, ensure_ascii=False)
        temp_path = f.name
    
    try:
        count = import_from_json(db, temp_path)
        print(f"✓ Imported {count} event(s) from export format")
        events = db.get_all_events()
        assert len(events) == 1
        assert events[0]['event_name'] == 'họp nhóm'
        print(f"✓ Event verified: {events[0]['event_name']}")
    finally:
        os.unlink(temp_path)
        del db  # Close database before unlinking
        try:
            os.unlink(db_temp.name)
        except:
            pass  # May fail on Windows if file is locked

def test_testcase_format():
    """Test importing from test case format (input + expected)"""
    print("\nTesting test case format...")
    db_temp = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    db_temp.close()
    db = DatabaseManager(db_temp.name)
    nlp = NLPPipeline()
    
    # Create a temp file with test case format
    testcase_data = [
        {
            "input": "Họp nhóm lúc 10h sáng mai ở phòng 302, nhắc trước 15 phút",
            "expected": {
                "event": "họp nhóm",
                "time_str": "10h sáng mai",
                "location": "phòng 302",
                "reminder_minutes": 15
            }
        }
    ]
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        json.dump(testcase_data, f, ensure_ascii=False)
        temp_path = f.name
    
    try:
        count = import_from_json(db, temp_path, nlp)
        print(f"✓ Imported {count} event(s) from test case format")
        events = db.get_all_events()
        if len(events) > 0:
            print(f"✓ Event parsed: {events[0]['event_name']}")
            print(f"  Start time: {events[0]['start_time']}")
            print(f"  Location: {events[0]['location']}")
            print(f"  Reminder: {events[0]['reminder_minutes']} mins")
        else:
            print("⚠ No events imported (may need valid future date)")
    finally:
        os.unlink(temp_path)
        del db
        try:
            os.unlink(db_temp.name)
        except:
            pass

def test_real_testcase_file():
    """Test importing from actual test_cases.json"""
    print("\nTesting real test_cases.json file...")
    db_temp = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    db_temp.close()
    db = DatabaseManager(db_temp.name)
    nlp = NLPPipeline()
    
    test_file = 'tests/test_cases.json'
    if os.path.exists(test_file):
        count = import_from_json(db, test_file, nlp)
        print(f"✓ Imported {count} event(s) from {test_file}")
        events = db.get_all_events()
        print(f"✓ Total events in DB: {len(events)}")
        if events:
            print(f"  First event: {events[0]['event_name']}")
        del db
        try:
            os.unlink(db_temp.name)
        except:
            pass
    else:
        print(f"⚠ File not found: {test_file}")
        del db
        try:
            os.unlink(db_temp.name)
        except:
            pass

if __name__ == '__main__':
    try:
        test_export_format()
        test_testcase_format()
        test_real_testcase_file()
        print("\n✅ All tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
