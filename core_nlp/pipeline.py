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
        # Use Unicode category \w which includes all Vietnamese letters
        self.time_patterns = re.compile(
            r"(" 
            # Time with hours: 10h, 10h30, 10:30, 10 giờ 30 phút
            # FIXED: Support h followed by digits (17h30) using (?:h\d{1,2}|:\d{1,2})
            # Negative lookbehind ensures no word character (includes all Vietnamese) before digit
            r"(?<!\w)\d{1,2}(?:h\d{1,2}|\s*(?:giờ|gio)|:\d{1,2}|h)(?:\s*\d{1,2}(?:p|\s*phút))?\b"
            # Date patterns - FIXED: Add DD/MM and DD/MM/YYYY formats
            r"|(?:ngày|ngay)?\s*\d{1,2}/\d{1,2}(?:/\d{2,4})?"  # 20/10, 20/10/2025, ngày 20/10
            r"|(?:ngày|ngay)\s*\d{1,2}\s*(?:tháng|thang)\s*\d{1,2}"
            # Relative day markers
            r"|(?:hôm nay|hom nay|ngày mai|ngay mai|mai)(?!\w)"  # Added negative lookahead
            r"|(?:ngày mốt|ngay mot|mốt|mot|mai mốt|mai mot|ngày kia|ngay kia)(?!\w)"
            # Period words (standalone only - with word boundaries)
            # FIXED: Include "toi" (without diacritics) as standalone period word
            r"|\b(?:sáng|sang|trưa|trua|chiều|chieu|tối|toi|đêm|dem|khuya)(?=\s|$)"
            # Special handling for 'toi' without diacritics in relative context (overrides standalone)
            r"|\btoi\s+(?:nay|mai|qua|hom\s*nay|hom\s*qua|hom\s*kia)(?=\s|$)"
            # Weekend
            r"|(?:cuối tuần|cuoi tuan)(?!\w)"
            # Weekday patterns with optional period or number words (including typos with/without diacritics)
            # Pattern 1: weekday + number words (e.g., "t5 támh", "thứ 2 bah", "chu nhat mười haih")
            # Use word boundaries \b to prevent partial matches like "tam" matching "támh"
            # Include all typo variations: tamh/támh, sauh/sáuh, namh/nămh, muoih/mườih, moth, haih, bah, bonh, tuh, bayh, chinh
            r"|(?:thứ|thu|t)\s*(?:\d|hai|ba|tu|nam|sau|bay|tam|chin|muoi|moth|haih|bah|bonh|tuh|namh|sauh|bayh|tamh|chinh|muoih|támh|sáuh|nămh|mườih)\b\s+\b(?:mot|hai|ba|bon|tu|nam|sau|bay|tam|chin|muoi|mươi|muoi|moth|haih|bah|bonh|tuh|namh|sauh|bayh|tamh|chinh|muoih|mườih|mười|một|bốn|sáu|tám|chín|támh|sáuh|nămh)\b(?:\s+\b(?:mot|hai|ba|bon|tu|moth|haih|bah|bonh|tuh|một)\b)?"
            r"|(?:cn|chu\s+nhat|chu\s*nhat|chủ\s+nhật|chủ\s*nhật)\s+\b(?:mot|hai|ba|bon|tu|nam|sau|bay|tam|chin|muoi|mươi|muoi|moth|haih|bah|bonh|tuh|namh|sauh|bayh|tamh|chinh|muoih|mườih|mười|một|bốn|sáu|tám|chín|támh|sáuh|nămh)\b(?:\s+\b(?:mot|hai|ba|bon|tu|moth|haih|bah|bonh|tuh|một)\b)?"
            # Pattern 2: weekday with period or digit - MUST have word boundary before "thứ/thu/t"
            # Also support number words: "thứ năm" (Thursday), "thứ hai" (Monday), etc.
            r"|\b(?:thứ|thu)\s*(?:\d|hai|ba|tu|tư|nam|năm|sau|sáu|bay|bảy)(?:\s+(?:tuần|tuan)\s+sau\s+(?:sáng|sang|trưa|trua|chiều|chieu|tối|toi|đêm|dem|khuya))?(?:\s+(?:sáng|sang|trưa|trua|chiều|chieu|tối|toi|đêm|dem|khuya))?"
            r"|\bt\s*\d(?:\s+(?:tuần|tuan)\s+sau\s+(?:sáng|sang|trưa|trua|chiều|chieu|tối|toi|đêm|dem|khuya))?(?:\s+(?:sáng|sang|trưa|trua|chiều|chieu|tối|toi|đêm|dem|khuya))?"
            # Sunday patterns with period word (e.g., "chu nhat chieu", "cn sang")
            r"|\b(?:cn|chu\s+nhat|chu\s*nhat|chủ\s+nhật|chủ\s*nhật)(?:\s+(?:tuần|tuan)\s+sau\s+(?:sáng|sang|trưa|trua|chiều|chieu|tối|toi|đêm|dem|khuya))?(?:\s+(?:sáng|sang|trưa|trua|chiều|chieu|tối|toi|đêm|dem|khuya))?"
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
        # Cải tiến: cắt tại dấu câu hoặc từ nối thời gian để tránh nuốt phần text phía sau
        # Ví dụ: "... 5h o truong ham tu" -> "truong ham tu"
        self.location_patterns = re.compile(
            r"\b(?:ở|o|tại|tai)\s+"                        # từ khóa địa điểm
            r"([^\n,.;:!?]+?)\s*"                          # nội dung địa điểm (non-greedy)
            r"(?=$|[，,.;:!?]|\b(?:vào|vao|lúc|luc|khoảng|khoang|đến|den|tới|toi|cho\s+đến|cho\s+den|nhắc|nhac|trước|truoc))",
            re.IGNORECASE,
        )

        # Reminder keyword groups (có dấu và không dấu)
        # Note: "báo" alone removed from verb to avoid false match with "báo cáo" (report)
        # Only match "báo" when followed by context (thức, trước, etc.)
        verb = r"(?:nhắc(?:\s*nhở)?|nhac(?:\s*nho)?|báo\s*thức|bao\s*thuc|báo\s*(?:trước|truoc)|bao\s*(?:trước|truoc)|remind|notify)"
        pron = r"(?:\s*(?:tôi|toi|mình|minh|t))?"
        before = r"(?:\s*(?:trước|truoc|trc|sớm\s*hơn|som\s*hon))?"
        unit_min = r"(?:phút|phut|p|'|')"
        # FIXED: Add "tieng/tiếng" for hour unit (common typo/variant)
        unit_hour = r"(?:giờ|gio|tiếng|tieng|h|hr)"
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
        
        IMPORTANT: Skip locations that are part of compound event phrases (e.g., "đi chợ", "ra chợ")
        """
        try:
            entities = ner(text)
        except Exception:
            entities = []

        location_tokens = []
        capture = False
        for item in entities:
            # underthesea ner returns tuples: (word, pos, chunk, ner_tag)
            tok = item[0]
            tag = item[3] if len(item) > 3 else 'O'
            
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
            
            # Check if this location is part of a compound event phrase
            # Compound phrases: "đi chợ", "ra chợ", "đi cafe", "đi bệnh viện" (motion + location)
            compound_patterns = [
                r'\b(?:đi|di|ra)\s+' + re.escape(location) + r'\b',
                r'\b(?:đi|di|ra)\s+(?:den|đen|toi|tới)\s+' + re.escape(location) + r'\b',
            ]
            is_compound = any(re.search(pattern, text, re.IGNORECASE) for pattern in compound_patterns)
            
            if is_compound:
                # This is an event (e.g., "đi chợ"), not a standalone location
                return None, text
            
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
            # Check if first match is a period word that's part of a compound event phrase
            # e.g., "ăn trưa" (have lunch), "ăn sáng" (have breakfast), "ăn tối" (have dinner)
            first_match = matches[0]
            first_match_text = first_match.group(0).lower()
            
            # List of period words that can be part of event phrases
            period_words = ['sáng', 'sang', 'trưa', 'trua', 'chiều', 'chieu', 'tối', 'toi', 'đêm', 'dem']
            
            # If first match is a standalone period word, check if it's part of compound phrase
            if first_match_text in period_words:
                # Look at text before the match
                prefix = text[:first_match.start()].strip()
                # Common event verbs that combine with period words
                compound_verbs = ['ăn', 'an', '먹', 'ở', 'o', 'nghỉ', 'nghi', 'làm', 'lam', 'học', 'hoc']
                
                # If prefix ends with a compound verb, skip this match - it's part of event!
                if any(prefix.lower().endswith(verb) for verb in compound_verbs):
                    # Skip first match, use next matches if available
                    if len(matches) > 1:
                        matches = matches[1:]  # Remove first match
                        first_match = matches[0]
                    else:
                        # Only match was the compound period word - no time to extract!
                        matches = []
            
            if not matches:
                # No valid time matches after filtering
                pass
            else:
                # Merge consecutive matches that are close together (gap <= 10 chars)
                # Example: "8:30" + " " + "ngày mai" should be merged
                # Also: "chu nhat sauh" + " gio " + "chieu" (gap=5) should be merged
                
                first_match = matches[0]
                consecutive_group = [first_match]
                
                # Build consecutive group: keep adding matches with gap <= 10
                for i in range(1, len(matches)):
                    prev_match = consecutive_group[-1]
                    curr_match = matches[i]
                    gap = curr_match.start() - prev_match.end()
                    
                    if gap <= 10:
                        consecutive_group.append(curr_match)
                    else:
                        # Gap too large - stop building group
                        break
                
                # Extract time_str from consecutive group
                if len(consecutive_group) > 1:
                    # Merge all consecutive matches
                    last_in_group = consecutive_group[-1]
                    results['time_str'] = text[first_match.start():last_in_group.end()].strip()
                    # Remove merged span from text
                    text = text[:first_match.start()] + ' ' + text[last_in_group.end():]
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
        event_text = self._clean_event_name(text, results.get('time_str'))
        results['event_name'] = event_text
        
        # Fallback: if event is empty, try getting text before time in original
        if not results['event_name'] and results['time_str']:
            matches = list(self.time_patterns.finditer(original_text))
            if matches:
                start = min(m.start() for m in matches)
                end = max(m.end() for m in matches)
                prefix = original_text[:start].strip(" ,.-")
                suffix = original_text[end:].strip(" ,.-")
                
                prefix_clean = self._clean_event_name(prefix, results['time_str'])
                suffix_clean = self._clean_event_name(suffix, results['time_str'])
                results['event_name'] = prefix_clean or suffix_clean
        
        # Step 4: HEURISTIC - Extract location without marker
        # If no location found yet, check if event_name contains location-like patterns
        # Pattern: "event_verb location_nouns" (e.g., "hop cong ty ABC", "hoc truong dai hoc")
        if not results['location'] and results['event_name']:
            event_parts = results['event_name'].split()
            
            # Common single-word event verbs
            single_verbs = ['hop', 'hoc', 'lam', 'gap', 'di', 'kham', 'le']
            
            # Common two-word event phrases (verb + object/complement)
            two_word_events = [
                'lam viec', 'gap khach', 'gap ban', 'gap doi', 
                'an com', 'an tiec', 'uong cafe', 'uong tra',
                'tap gym', 'tap yoga', 'chay bo', 'di bo',
                'xem phim', 'mua sam', 'ban hang',
                'hop team', 'hop nhom', 'doc sach'
            ]
            
            # Common three-word event phrases
            three_word_events = [
                'gap doi tac', 'hop ban giam', 'lam bai tap',
                'doc bao cao', 'viet bao cao'
            ]
            
            # If event has 4+ words, try to split event from location
            if len(event_parts) >= 4:
                # Check if it's a three-word event phrase
                three_word_check = ' '.join(event_parts[:3])
                if three_word_check in three_word_events:
                    # "gap doi tac van phong ABC" → event="gap doi tac", location="van phong ABC"
                    results['event_name'] = three_word_check
                    results['location'] = ' '.join(event_parts[3:])
                # Check if it's a two-word event phrase
                elif ' '.join(event_parts[:2]) in two_word_events:
                    two_word_check = ' '.join(event_parts[:2])
                    results['event_name'] = two_word_check
                    results['location'] = ' '.join(event_parts[2:])
                elif event_parts[0] in single_verbs:
                    # Single-word event
                    results['event_name'] = event_parts[0]
                    results['location'] = ' '.join(event_parts[1:])
            
            # If event has exactly 3 words, check two-word events
            elif len(event_parts) == 3:
                two_word_check = ' '.join(event_parts[:2])
                if two_word_check in two_word_events:
                    # "an com nha hang" → event="an com", location="nha hang"
                    results['event_name'] = two_word_check
                    results['location'] = ' '.join(event_parts[2:])
                elif event_parts[0] in single_verbs:
                    # Single-word event: "hop cong ty ABC" → event="hop", location="cong ty ABC"
                    results['event_name'] = event_parts[0]
                    results['location'] = ' '.join(event_parts[1:])
                # Otherwise, keep event as-is (might be complex phrase like "le nha tho")
        
        return results
    
    def _clean_event_name(self, text: str, time_str: str = None) -> str:
        """Clean time-related words from event name.
        Only removes period words (sáng, trưa, tối, etc.) if they appeared in the extracted time_str.
        This preserves period words that are part of event phrases like "ăn trưa" (have lunch).
        """
        if not text:
            return ""
        
        # First pass: Remove time connectors and relative time words (always remove these)
        time_connectors = r"(?:vào|vao|lúc|luc|vào\s+lúc|vao\s+luc|khoảng|khoang|từ|tu|đến|den|tới|cho\s+đến|cho\s+den|bắt\s+đầu|bat\s+dau|kết\s+thúc|ket\s+thuc)"
        relative_time = r"(?:hôm\s*nay|hom\s*nay|ngày\s*mai|ngay\s*mai|mai|ngày\s*mốt|ngay\s*mot|mốt|mot|hôm\s*qua|hom\s*qua|qua|nay|tuần\s*sau|tuan\s*sau|tuần\s*trước|tuan\s*truoc)"
        timezone_words = r"(?:utc|gmt|múi\s*giờ|mui\s*gio)"
        
        cleaned = re.sub(fr"\b({time_connectors}|{relative_time}|{timezone_words})\b", " ", text, flags=re.IGNORECASE)
        
        # Second pass: Remove time-related words like "gio" (giờ) that are part of time expressions
        # This fixes: "sauh gio chieu di cafe" → "di cafe" (not "gio di cafe")
        time_unit_words = r"(?:giờ|gio|phút|phut)"
        cleaned = re.sub(fr"\b{time_unit_words}\b", " ", cleaned, flags=re.IGNORECASE)
        
        # Third pass: Only remove period words if they appeared in the extracted time_str
        # This prevents removing period words that are part of event phrases
        if time_str:
            period_words = ['sáng', 'sang', 'trưa', 'trua', 'chiều', 'chieu', 'tối', 'toi', 'đêm', 'dem', 'khuya']
            time_str_lower = time_str.lower()
            
            for period in period_words:
                # Only remove this period word if it's in the time_str
                if period in time_str_lower:
                    cleaned = re.sub(fr"\b{period}\b", " ", cleaned, flags=re.IGNORECASE)
        
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
