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
        
        # ========== IMPROVED TIME PATTERNS ==========
        # Fix: Prevent matching time patterns adjacent to letters (both upper and lowercase)
        # Negative lookbehind includes all Vietnamese letters to prevent "nhật 8:30" matching "t 8:30"
        self.time_patterns = re.compile(
            r"(" 
            # Time with hours: 10h, 10:30, 10 giờ 30 phút
            # Negative lookbehind ensures no Vietnamese letter (upper/lower) before digit
            r"(?<![a-zA-ZàáảãạâầấẩẫậăằắẳẵặèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđÀÁẢÃẠÂẦẤẨẪẬĂẰẮẲẴẶÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸỴĐ])\d{1,2}(?:h|\s*giờ|:\d{1,2})(?:\s*\d{1,2}(?:p|\s*phút))?\b"
            # Date patterns
            r"|(?:ngày|ngay)\s*\d{1,2}\s*(?:tháng|thang)\s*\d{1,2}"
            # Relative day markers
            r"|(?:hôm nay|hom nay|ngày mai|ngay mai|mai)(?!\w)"  # Added negative lookahead
            r"|(?:ngày mốt|ngay mot|mốt|mot|mai mốt|mai mot|ngày kia|ngay kia)(?!\w)"
            # Period words (standalone only - with word boundaries)
            r"|\b(?:sáng|sang|trưa|trua|chiều|chieu|tối|đêm|dem|khuya)(?=\s|$)"
            # Special handling for 'toi' without diacritics (context-dependent)
            r"|\btoi\s+(?:nay|mai|qua|hom\s*nay|hom\s*qua|hom\s*kia)(?=\s|$)"
            # Weekend
            r"|(?:cuối tuần|cuoi tuan)(?!\w)"
            # Weekday patterns with optional period
            r"|(?:thứ|thu)\s*\d(?:\s+(?:tuần|tuan)\s+sau\s+(?:sáng|sang|trưa|trua|chiều|chieu|tối|toi|đêm|dem|khuya))?(?:\s+(?:sáng|sang|trưa|trua|chiều|chieu|tối|toi|đêm|dem|khuya))?"
            r"|t\s*\d(?:\s+(?:tuần|tuan)\s+sau\s+(?:sáng|sang|trưa|trua|chiều|chieu|tối|toi|đêm|dem|khuya))?(?:\s+(?:sáng|sang|trưa|trua|chiều|chieu|tối|toi|đêm|dem|khuya))?"
            r"|cn(?:\s+(?:tuần|tuan)\s+sau\s+(?:sáng|sang|trưa|trua|chiều|chieu|tối|toi|đêm|dem|khuya))?(?:\s+(?:sáng|sang|trưa|trua|chiều|chieu|tối|toi|đêm|dem|khuya))?"
            # Duration patterns
            r"|(?:trong|sau)\s*\d{1,3}\s*(?:phút|phut|giờ|gio|ngày|ngay|tuần|tuan)"
            r"|\d{1,3}\s*(?:phút|phut|giờ|gio|ngày|ngay|tuần|tuan)\s*(?:nữa|nua)"
            # Timezone
            r"|(?:utc|gmt)\s*[+\-]?\d{1,2}(?::?\d{2})?"
            r"|(?:múi|mui)\s*(?:giờ|gio)\s*(?:utc|gmt)?\s*[+\-]?\d{1,2}(?::?\d{2})?"
            r")",
            re.IGNORECASE,
        )
        # Location fallback: ở|o / tại|tai ... (tối đa một cụm, hỗ trợ không dấu)
        self.location_patterns = re.compile(r"\b(?:ở|o|tại|tai)\s+([\w\s\d./-]{1,50})", re.IGNORECASE)

        # Reminder keyword groups (có dấu và không dấu)
        # Note: "báo" alone removed from verb to avoid false match with "báo cáo" (report)
        # Only match "báo" when followed by context (thức, trước, etc.)
        verb = r"(?:nhắc(?:\s*nhở)?|nhac(?:\s*nho)?|báo\s*thức|bao\s*thuc|báo\s*(?:trước|truoc)|bao\s*(?:trước|truoc)|remind|notify)"
        pron = r"(?:\s*(?:tôi|toi|mình|minh|t))?"
        before = r"(?:\s*(?:trước|truoc|trc|sớm\s*hơn|som\s*hon))?"
        unit_min = r"(?:phút|phut|p|’|')"
        unit_hour = r"(?:giờ|gio|h|hr)"
        num = r"(\d{1,3})"
        # Forms: verb [pron] [before]? NUM UNIT [before]?  (covers: 'nhắc trước 10p' and 'nhắc 10p trước')
        self.reminder_min_regex1 = re.compile(fr"{verb}{pron}(?:{before}\s*)?{num}\s*{unit_min}(?:\s*(?:trước|truoc|trc))?\b", re.IGNORECASE)
        self.reminder_hour_regex1 = re.compile(fr"{verb}{pron}(?:{before}\s*)?{num}\s*{unit_hour}(?:\s*(?:trước|truoc|trc))?\b", re.IGNORECASE)
        # Forms: NUM UNIT [before] [verb] (e.g., '10p trước nhắc tôi')
        self.reminder_min_regex2 = re.compile(fr"\b{num}\s*{unit_min}{before}\s*(?:{verb})", re.IGNORECASE)
        self.reminder_hour_regex2 = re.compile(fr"\b{num}\s*{unit_hour}{before}\s*(?:{verb})", re.IGNORECASE)
        # Presence-only (no number): used to strip from text and optional boolean
        self.reminder_presence_regex = re.compile(fr"{verb}{pron}(?:\s*(?:trước|truoc|trc))?\b", re.IGNORECASE)

        # Time connectors and period words to strip from event name (comprehensive list with/without diacritics)
        time_connectors = r"(?:vào|vao|lúc|luc|vào\s+lúc|vao\s+luc|khoảng|khoang|từ|tu|đến|den|tới|cho\s+đến|cho\s+den|bắt\s+đầu|bat\s+dau|kết\s+thúc|ket\s+thuc)"
        # Period words: only match as standalone words (not part of longer words like 'thuyet trinh')
        period_words = r"(?:sáng|sang|trưa|trua|chiều|chieu|tối|đêm|dem|khuya)(?=\s|$)"
        # Include standalone relative fragments: nay (from hom nay), qua (from hom qua), mot (from ngay mot)
        relative_time = r"(?:hôm\s*nay|hom\s*nay|ngày\s*mai|ngay\s*mai|mai|ngày\s*mốt|ngay\s*mot|mốt|mot|hôm\s*qua|hom\s*qua|qua|nay|tuần\s*sau|tuan\s*sau|tuần\s*trước|tuan\s*truoc)"
        timezone_words = r"(?:utc|gmt|múi\s*giờ|mui\s*gio)"
        self.time_related_words = re.compile(fr"\b({time_connectors}|{period_words}|{relative_time}|{timezone_words})\b", re.IGNORECASE)

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
        """
        Extract event, time, and location using regex.
        Improved to extract ALL consecutive time segments (e.g., "10h sáng").
        """
        results: Dict[str, Any] = {
            "time_str": None,
            "location": None,
        }
        original_text = text
        
        # Step 1: Extract time_str - find ALL matches and merge if consecutive
        matches = list(self.time_patterns.finditer(text))
        if matches:
            # If there are consecutive matches (like "10h" followed by "sáng"),
            # merge them into one time_str
            first_match = matches[0]
            last_match = matches[-1]
            
            # Check if matches are close together (within 3 chars gap)
            if len(matches) > 1:
                merged_needed = True
                for i in range(len(matches) - 1):
                    gap = matches[i+1].start() - matches[i].end()
                    if gap > 3:  # Too far apart
                        merged_needed = False
                        break
                
                if merged_needed:
                    # Merge all matches into one time_str
                    results['time_str'] = text[first_match.start():last_match.end()].strip()
                    # Remove merged span from text
                    text = text[:first_match.start()] + ' ' + text[last_match.end():]
                else:
                    # Only use first match
                    results['time_str'] = first_match.group(0).strip()
                    text = text[:first_match.start()] + ' ' + text[first_match.end():]
            else:
                # Single match
                results['time_str'] = first_match.group(0).strip()
                text = text[:first_match.start()] + ' ' + text[first_match.end():]
            
            text = ' '.join(text.split())  # Normalize whitespace
        
        # Step 2: Extract location
        loc_match = self.location_patterns.search(text)
        if loc_match:
            results['location'] = loc_match.group(1).strip()
            # Remove location while preserving spaces
            text = text[:loc_match.start()] + ' ' + text[loc_match.end():]
            text = ' '.join(text.split())
        
        # Step 3: Clean remaining text to get event
        event_text = self._clean_event_name(text)
        results['event_name'] = event_text
        
        # Fallback: if event is empty, try getting text before time in original
        if not results['event_name'] and results['time_str']:
            matches = list(self.time_patterns.finditer(original_text))
            if matches:
                start = min(m.start() for m in matches)
                end = max(m.end() for m in matches)
                prefix = original_text[:start].strip(" ,.-")
                suffix = original_text[end:].strip(" ,.-")
                
                prefix_clean = self._clean_event_name(prefix)
                suffix_clean = self._clean_event_name(suffix)
                results['event_name'] = prefix_clean or suffix_clean
        
        return results
    
    def _clean_event_name(self, text: str) -> str:
        """Clean time-related words from event name.
        NOTE: Assumes time has already been removed from text, so don't re-apply time_patterns.
        """
        if not text:
            return ""
        # Remove time-related words (lúc, vào, etc.)
        cleaned = self.time_related_words.sub(' ', text)
        # Remove location/time connectors
        cleaned = re.sub(r"\b(vào|vao|lúc|luc|khoảng|khoang|tại|tai|ở|o)\b", "", cleaned, flags=re.IGNORECASE)
        # Collapse spaces and trim punctuation
        cleaned = re.sub(r"\s{2,}", " ", cleaned).strip(' ,.-').strip()
        return cleaned

    def process(self, text: str) -> Dict[str, Any]:
        processed_text = text.lower() if text else ''
        # 1) Extract reminder minutes first, strip reminder phrases from text to avoid leaking into location
        reminder_minutes, text_wo_reminder, has_reminder_phrase = self._extract_reminder(processed_text)
        # 2) Extract entities (time, location, event) - location fallback runs inside _extract_entities_regex
        ex = self._extract_entities_regex(text_wo_reminder)
        # 3) If location not found by regex fallback, try NER as backup
        if not ex.get('location'):
            loc_ner, _ = self._extract_location_ner(text_wo_reminder)
            if loc_ner:
                ex['location'] = loc_ner
        # Parse time
        start_dt, end_dt = parse_vietnamese_time_range(ex['time_str'], relative_base=self.relative_base)
        result = {
            'event': ex['event_name'],
            'start_time': start_dt.isoformat() if start_dt else None,
            'end_time': end_dt.isoformat() if end_dt else None,
            'location': self._clean_location_of_reminder(ex.get('location')),
            'reminder_minutes': reminder_minutes,
        }
        return result

    def _extract_reminder(self, text: str) -> Tuple[int, str, bool]:
        """Trích số phút nhắc nhở (nếu có) và loại bỏ mọi cụm từ liên quan 'nhắc tôi' khỏi text.
        Hỗ trợ cả có dấu/không dấu và các biến thể phổ biến.
        Trả về: (reminder_minutes, text_without_reminder, has_reminder_phrase)
        """
        minutes = 0
        has = False
        working = text
        # Try different forms, prioritize the first explicit number found
        for rx, factor in [
            (self.reminder_hour_regex1, 60),
            (self.reminder_min_regex1, 1),
            (self.reminder_hour_regex2, 60),
            (self.reminder_min_regex2, 1),
        ]:
            m = rx.search(working)
            if m:
                try:
                    val = int(m.group(1))
                    minutes = max(minutes, val * factor)
                except Exception:
                    pass
                has = True
                working = working.replace(m.group(0), ' ').strip()
        # If no number captured but reminder words exist, strip them
        if not has:
            if self.reminder_presence_regex.search(working):
                has = True
                working = self.reminder_presence_regex.sub(' ', working).strip()
        # Collapse multiple spaces
        working = re.sub(r"\s{2,}", " ", working)
        return minutes, working, has

    def _clean_location_of_reminder(self, loc: Optional[str]) -> Optional[str]:
        if not loc:
            return loc
        # Remove reminder keywords from location, both diacritic and non-diacritic
        loc2 = self.reminder_presence_regex.sub(' ', loc)
        loc2 = re.sub(r"\s{2,}", " ", loc2).strip(" ,.-").strip()
        return loc2 or None
