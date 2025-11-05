"""Test NLP parsing bug"""
import sys
sys.path.insert(0, '.')

from core_nlp.pipeline import NLPPipeline

# Test case 1 from test_cases.json
test_input = "Họp nhóm lúc 10h sáng mai ở phòng 302, nhắc trước 15 phút"

print(f"Testing: {test_input}")
print("=" * 60)

nlp = NLPPipeline()

try:
    result = nlp.parse_event(test_input)
    print(f"✅ SUCCESS: {result}")
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
