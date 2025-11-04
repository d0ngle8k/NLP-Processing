from __future__ import annotations
import re
from typing import Optional, Tuple, Dict, Any

try:
    from underthesea import ner
except Exception:
    # Fallbacks if underthesea not available at lint-time
    def ner(_text: str):
        return []

from .time_parser import parse_vietnamese_time, parse_vietnamese_time_range
from datetime import datetime


class NLPPipeline:
    def __init__(self, *, relative_base: Optional[datetime] = None):
        self.relative_base = relative_base
        # Time patterns: nhận diện các mảnh thời gian rời rạc để ghép lại
        self.time_patterns = re.compile(
            r"(" 
            r"\b\d{1,2}(?:h|\s*giờ)(?:\s*\d{1,2}(?:p|\s*phút))?\b"  # 10h, 10 giờ 30 phút
            r"|\b\d{1,2}:\d{1,2}\b"                                   # 10:30
            r"|(?:ngày|ngay)\s*\d{1,2}\s*(?:tháng|thang)\s*\d{1,2}"   # ngày/ngay 6 tháng/thang 12
            r"|(?:hôm nay|hom nay|ngày mai|ngay mai|mai)"                 # hôm nay / hom nay / ngày mai / ngay mai / mai
            r"|(?:ngày mốt|ngay mot|mốt|mot|mai mốt|mai mot|ngày kia|ngay kia)" # ngày mốt / mai mốt / ngày kia
            r"|(?:sáng|sang)(?:\s+\w+)?|(?:chiều|chieu)(?:\s+\w+)?|(?:tối|toi)(?:\s+\w+)?"  # buổi
            r"|(?:cuối tuần|cuoi tuan)"                                   # cuối tuần / cuoi tuan
            r"|(?:thứ|thu)\s*\d(?:\s*(?:tuần|tuan) sau)?"               # thứ 2 tuần sau (diacriticless)
            r"|t\s*\d(?:\s*(?:tuần|tuan) sau)?"                         # t2..t7, tuan sau
            r"|cn(?:\s*(?:tuần|tuan) sau)?"                               # cn, cn tuần sau
            r"|(?:trong|sau)\s*\d{1,3}\s*(?:phút|phut|giờ|gio|ngày|ngay|tuần|tuan)"  # durations
            r"|\d{1,3}\s*(?:phút|phut|giờ|gio|ngày|ngay|tuần|tuan)\s*(?:nữa|nua)"    # X đơn vị nữa
            r"|(?:utc|gmt)\s*[+\-]?\d{1,2}(?::?\d{2})?"                # UTC+7, GMT+07:00
            r"|(?:múi|mui)\s*(?:giờ|gio)\s*(?:utc|gmt)?\s*[+\-]?\d{1,2}(?::?\d{2})?" # múi giờ +07:00 / mui gio
            r")",
            re.IGNORECASE,
        )
        # Reminder: nhắc trước 15 phút | nhắc sớm hơn 1 giờ
        self.reminder_patterns = re.compile(r"nhắc\s*(?:trước|sớm hơn)\s*(\d+)\s*(phút|giờ)", re.IGNORECASE)
        # Location fallback: ở/tại ... (tối đa một cụm)
        self.location_patterns = re.compile(r"\b(?:ở|tại)\s+([\w\s\d./-]{1,50})", re.IGNORECASE)

    def _extract_location_ner(self, text: str) -> Tuple[Optional[str], str]:
        """Sử dụng underthesea NER để ghép các token B-LOC/I-LOC thành một cụm địa điểm.
        Trả về (location, text_without_location)
        """
        try:
            entities = ner(text)
        except Exception:
            entities = []

        location_tokens = []
        capture = False
        for tok, tag in entities:
            if tag == 'B-LOC':
                if location_tokens:
                    break  # chỉ lấy cụm đầu tiên
                location_tokens = [tok]
                capture = True
            elif tag == 'I-LOC' and capture:
                location_tokens.append(tok)
            else:
                if capture:
                    break
        location = None
        if location_tokens:
            # underthesea tokenizes with underscores for spaces sometimes
            location = " ".join(t.replace('_', ' ') for t in location_tokens).strip()
            # Loại khỏi text (best-effort)
            text = re.sub(re.escape(location), "", text, flags=re.IGNORECASE).strip()
        return location, text

    def _extract_entities_regex(self, text: str) -> Dict[str, Any]:
        results: Dict[str, Any] = {
            "time_str": None,
            "reminder_minutes": 0,
            "location": None,
        }
        original_text = text
        # Reminder
        m = self.reminder_patterns.search(text)
        if m:
            val = int(m.group(1))
            unit = m.group(2).lower()
            if 'giờ' in unit:
                val *= 60
            results['reminder_minutes'] = val
            text = text.replace(m.group(0), '').strip()
        # Time: ghép các mảnh liền kề lớn nhất thành một cụm
        matches = list(self.time_patterns.finditer(text))
        if matches:
            start = min(m.start() for m in matches)
            end = max(m.end() for m in matches)
            # Lưu lại tiền tố/hậu tố để fallback nếu event trống
            prefix = original_text[:start].strip(" ,.-")
            suffix = original_text[end:].strip(" ,.-")
            # Trích một đoạn bao quanh để giữ từ bổ trợ
            span = text[max(0, start-5):min(len(text), end+5)]
            span = re.sub(r"\b(vào|lúc|khoảng)\b", "", span, flags=re.IGNORECASE).strip()
            results['time_str'] = span
            # Xóa đoạn thời gian khỏi văn bản gốc
            text = (text[:start] + text[end:]).strip()
        # Location fallback
        l = self.location_patterns.search(text)
        if l and not results['location']:
            results['location'] = l.group(1).strip()
            text = text.replace(l.group(0), '').strip()
        # Remaining as event name
        results['event_name'] = re.sub(r"\b(vào|lúc|khoảng|nhắc tôi|nhắc|tại|ở)\b", "", text, flags=re.IGNORECASE)
        results['event_name'] = re.sub(r"\s{2,}", " ", results['event_name']).strip(' ,.-').strip()
        # Fallback: nếu event_name rỗng, thử lấy phần trước thời gian (ưu tiên) hoặc sau thời gian
        if not results['event_name'] and matches:
            # Loại bỏ từ nối khỏi prefix/suffix
            def _clean_side(s: str) -> str:
                s2 = re.sub(r"\b(vào|lúc|khoảng|tại|ở)\b", "", s, flags=re.IGNORECASE)
                s2 = re.sub(r"\s{2,}", " ", s2).strip(' ,.-').strip()
                return s2
            prefix_clean = _clean_side(prefix)
            suffix_clean = _clean_side(suffix)
            results['event_name'] = prefix_clean or suffix_clean
        return results

    def process(self, text: str) -> Dict[str, Any]:
        processed_text = text.lower() if text else ''
        # NER location then regex
        loc_ner, rem = self._extract_location_ner(processed_text)
        ex = self._extract_entities_regex(rem)
        # Parse time
        start_dt, end_dt = parse_vietnamese_time_range(ex['time_str'], relative_base=self.relative_base)
        result = {
            'event': ex['event_name'],
            'start_time': start_dt.isoformat() if start_dt else None,
            'end_time': end_dt.isoformat() if end_dt else None,
            'location': loc_ner or ex['location'],
            'reminder_minutes': ex['reminder_minutes'],
        }
        return result
