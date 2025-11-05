"""
Quick diagnostic to see what NLP pipeline returns for test input
"""
from core_nlp.pipeline import NLPPipeline

nlp = NLPPipeline()

test_input = "Họp nhóm lúc 10h sáng mai ở phòng 302, nhắc trước 15 phút"
print(f"Input: {test_input}")
print(f"\nParsed result:")
result = nlp.process(test_input)
for key, value in result.items():
    print(f"  {key}: {value}")
