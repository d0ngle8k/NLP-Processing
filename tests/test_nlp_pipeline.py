import json
import unittest
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core_nlp.pipeline import NLPPipeline
from core_nlp.time_parser import parse_vietnamese_time

TEST_BASE = datetime(2025, 11, 5, 9, 0, 0)  # Cố định mốc thời gian để test ổn định


def load_cases():
    p = Path(__file__).with_name('test_cases.json')
    with p.open('r', encoding='utf-8') as f:
        return json.load(f)


def normalize(s):
    return (s or '').strip().lower()


class TestNLPPipeline(unittest.TestCase):
    def setUp(self):
        self.pipeline = NLPPipeline(relative_base=TEST_BASE)

    def _compare_time(self, pred_iso: str | None, gold_time_str: str | None) -> bool:
        if not gold_time_str:
            return pred_iso is None
        gold_dt = parse_vietnamese_time(gold_time_str, relative_base=TEST_BASE)
        if not gold_dt or not pred_iso:
            return False
        # So sánh đến phút
        pred = pred_iso[:16]
        gold = gold_dt.isoformat()[:16]
        return pred == gold

    def test_macro_f1(self):
        cases = load_cases()
        tp = {k: 0 for k in ['event', 'start_time', 'location', 'reminder_minutes']}
        fp = {k: 0 for k in tp}
        fn = {k: 0 for k in tp}

        for item in cases:
            text = item['input']
            gold = item['expected']
            pred = self.pipeline.process(text)

            # event
            if normalize(pred['event']) == normalize(gold['event']):
                tp['event'] += 1
            else:
                fp['event'] += 1
                fn['event'] += 1

            # start_time
            if self._compare_time(pred['start_time'], gold['time_str']):
                tp['start_time'] += 1
            else:
                fp['start_time'] += 1
                fn['start_time'] += 1

            # location
            if normalize(pred['location']) == normalize(gold['location']):
                tp['location'] += 1
            else:
                # Cho phép bỏ qua nếu gold là null và pred cũng null
                if gold['location'] is None and normalize(pred['location']) == '':
                    tp['location'] += 1
                else:
                    fp['location'] += 1
                    fn['location'] += 1

            # reminder
            if int(pred['reminder_minutes'] or 0) == int(gold['reminder_minutes'] or 0):
                tp['reminder_minutes'] += 1
            else:
                fp['reminder_minutes'] += 1
                fn['reminder_minutes'] += 1

        def f1_of(k):
            P = tp[k] / max(tp[k] + fp[k], 1)
            R = tp[k] / max(tp[k] + fn[k], 1)
            return 2 * P * R / max(P + R, 1e-9)

        f1s = [f1_of(k) for k in tp]
        macro = sum(f1s) / len(f1s)
        print({k: f1_of(k) for k in tp}, 'macro_f1=', macro)
        self.assertGreaterEqual(macro, 0.80)


if __name__ == '__main__':
    unittest.main()
