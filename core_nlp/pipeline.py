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
        # CRITICAL: Date patterns MUST come before period words to avoid "toi" (I) being matched as "tối" (evening)
        # v1.0.6: CRITICAL FIX - Prevent "24h" from matching when part of location names like "Cafe 24h"
        self.time_patterns = re.compile(
            r"(" 
            # === PRIORITY 1: EXPLICIT DATE PATTERNS (MUST COME FIRST) ===
            # Date patterns with year - HIGHEST PRIORITY
            r"(?:ngày|ngay)\s*\d{1,2}\s*(?:tháng|thang)\s*\d{1,2}\s*(?:năm|nam)\s*\d{4}"  # ngày 20 tháng 11 năm 2025
            r"|(?:ngày|ngay)?\s*\d{1,2}/\d{1,2}/\d{2,4}"  # 20/10/2025, ngày 20/10/2025
            # Date patterns without year
            r"|(?:ngày|ngay)\s*\d{1,2}\s*(?:tháng|thang)\s*\d{1,2}(?!\s*(?:năm|nam))"  # ngày 20 tháng 10 (without năm)
            r"|(?:ngày|ngay)?\s*\d{1,2}/\d{1,2}(?!/)"  # 20/10, ngày 20/10 (not followed by /)
            # Specific day without month (assumes current/next month)
            r"|(?:ngày|ngay)\s+\d{1,2}(?!\s*(?:tháng|thang|/))(?!\w)"  # ngày 15 (without tháng)
            # Specific month with/without year (assumes 1st of month)
            r"|(?:tháng|thang)\s+\d{1,2}\s*(?:năm|nam)\s*\d{4}"  # tháng 12 năm 2025
            r"|(?:tháng|thang)\s+\d{1,2}(?!\s*(?:năm|nam))(?!\w)"  # tháng 12 (without năm)
            # Year patterns
            r"|\b(?:năm|nam)\s+\d{4}(?!\w)"  # năm 2026, năm 2027
            r"|\b(?:năm|nam)\s+(?:sau|toi|tới|nay|này|trước|truoc)(?!\w)"  # năm sau, năm tới, năm nay
            # === PRIORITY 2: TIME WITH HOURS ===
            # Time with hours: 10h, 10h30, 10:30, 10 giờ 30 phút
            # v1.0.6 CRITICAL FIX: Exclude "24h" to prevent "Cafe 24h" from being parsed as time
            # Only match hours 0-23 for standalone "Xh" patterns
            # Pattern breakdown:
            #   - (?<!\w) = not preceded by word char (prevents "Cafe24h")
            #   - (?:1?\d|2[0-3]) = hours 0-23 (excludes 24+)
            #   - (?:h\d{1,2}|...) = followed by h+minutes, giờ, :minutes, or standalone h
            r"|(?<!\w)(?:1?\d|2[0-3])(?:h\d{1,2}|\s*(?:giờ|gio)|:\d{1,2}|h)(?:\s*\d{1,2}(?:p|\s*phút))?\b"
            # === PRIORITY 3: RELATIVE DAY MARKERS ===
            r"|(?:hôm nay|hom nay|ngày mai|ngay mai|mai)(?!\w)"
            r"|(?:ngày mốt|ngay mot|mốt|mot|mai mốt|mai mot|ngày kia|ngay kia)(?!\w)"
            # === PRIORITY 4: RELATIVE WEEK/MONTH PATTERNS ===
            r"|\b(?:tuần|tuan)\s+(?:sau|toi|tới|này|nay|trước|truoc)(?!\w)"  # tuần sau, tuần tới, tuần này, tuần trước
            r"|\b(?:tháng|thang)\s+(?:sau|toi|tới|này|nay|trước|truoc)(?!\w)"  # tháng sau, tháng tới, tháng này, tháng trước
            # === PRIORITY 5: PERIOD WORDS (LOWEST PRIORITY) ===
            # Period words (standalone only - with word boundaries)
            # CRITICAL FIX: "toi" must have stronger constraints to avoid matching "toi" (I/me)
            # Only match if preceded by time-related context or at start of sentence
            r"|\b(?:sáng|sang|trưa|trua|chiều|chieu|tối|đêm|dem|khuya)(?=\s|$)"
            # "toi" only matches in specific time contexts to avoid "toi" (I/me)
            r"|(?:vào|vao|lúc|luc)\s+(?:toi)(?=\s|$)"  # "vào tối", "lúc tối"
            r"|\btoi\s+(?:nay|mai|qua|hom\s*nay|hom\s*qua|hom\s*kia)(?=\s|$)"  # "tối nay", "tối mai"
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
        unit_day = r"(?:ngày|ngay|d|day)"
        unit_week = r"(?:tuần|tuan|week|w)"
        unit_month = r"(?:tháng|thang|month|m)"
        num = r"(\d{1,3})"
        # Forms: verb [pron] [before]? NUM UNIT [before]?  (covers: 'nhắc trước 10p' and 'nhắc 10p trước')
        self.reminder_min_regex1 = re.compile(fr"{verb}{pron}(?:{before}\s*)?{num}\s*{unit_min}(?:\s*(?:trước|truoc|trc))?\b", re.IGNORECASE)
        self.reminder_hour_regex1 = re.compile(fr"{verb}{pron}(?:{before}\s*)?{num}\s*{unit_hour}(?:\s*(?:trước|truoc|trc))?\b", re.IGNORECASE)
        self.reminder_day_regex1 = re.compile(fr"{verb}{pron}(?:{before}\s*)?{num}\s*{unit_day}(?:\s*(?:trước|truoc|trc))?\b", re.IGNORECASE)
        self.reminder_week_regex1 = re.compile(fr"{verb}{pron}(?:{before}\s*)?{num}\s*{unit_week}(?:\s*(?:trước|truoc|trc))?\b", re.IGNORECASE)
        self.reminder_month_regex1 = re.compile(fr"{verb}{pron}(?:{before}\s*)?{num}\s*{unit_month}(?:\s*(?:trước|truoc|trc))?\b", re.IGNORECASE)
        # Forms: NUM UNIT [before] [verb] (e.g., '10p trước nhắc tôi')
        self.reminder_min_regex2 = re.compile(fr"\b{num}\s*{unit_min}{before}\s*(?:{verb})", re.IGNORECASE)
        self.reminder_hour_regex2 = re.compile(fr"\b{num}\s*{unit_hour}{before}\s*(?:{verb})", re.IGNORECASE)
        self.reminder_day_regex2 = re.compile(fr"\b{num}\s*{unit_day}{before}\s*(?:{verb})", re.IGNORECASE)
        self.reminder_week_regex2 = re.compile(fr"\b{num}\s*{unit_week}{before}\s*(?:{verb})", re.IGNORECASE)
        self.reminder_month_regex2 = re.compile(fr"\b{num}\s*{unit_month}{before}\s*(?:{verb})", re.IGNORECASE)
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
    
    def _extract_location_heuristic(self, text: str, event_name: str) -> Optional[str]:
        """
        v1.0.7: Extract location using heuristic patterns (no marker "ở/tại" needed)
        
        Strategy:
        1. Clean text from reminder keywords first
        2. Look for known location patterns (cities, buildings, venues)
        3. Validate and return if not part of event
        
        IMPORTANT: This runs AFTER event/time extraction, so text should be relatively clean.
        """
        if not text:
            return None
        
        # Step 1: Clean reminder keywords (before, earlier, som hon, notify, etc.)
        reminder_keywords = r'\b(?:before|earlier|notify|nhac|nhắc|báo|bao|trc|truoc|trước|som|sớm|hon|hơn)\b'
        text_cleaned = re.sub(reminder_keywords, ' ', text, flags=re.IGNORECASE)
        text_cleaned = re.sub(r'\s{2,}', ' ', text_cleaned).strip()
        
        # Common Vietnamese location names (cities, districts, venues)
        # v1.0.7: Extracted from training_100k_comprehensive.json top locations
        # ENHANCED: Added many more location keywords to improve 24.8% detection rate
        known_locations = [
            # Cities (highest priority - most specific)
            r'\b(?:hà\s*nội|ha\s*noi|sài\s*gòn|sai\s*gon|đà\s*nẵng|da\s*nang|hải\s*phòng|hai\s*phong|cần\s*thơ|can\s*tho|hồ\s*chí\s*minh|ho\s*chi\s*minh)\b',
            # Branded venues (specific names)
            r'\b(?:30\s*shines|highlands?\s*coffee|starbucks?|kfc|lotteria|phúc\s*long|phuc\s*long|trung\s*nguyên|trung\s*nguyen|café|cafe)\b',
            # Building components (specific)
            r'\b(?:tầng\s*\d+|tang\s*\d+|toà\s*[a-z]|toa\s*[a-z]|khu\s*[a-z]|phòng\s*\d+|phong\s*\d+|lầu\s*\d+|lau\s*\d+)\b',
            r'\b(?:quận\s*\d+|quan\s*\d+|phường\s*\d+|phuong\s*\d+|huyện\s*\d+|huyen\s*\d+)\b',
            r'\b(?:ngõ\s*\d+|ngo\s*\d+|hẻm\s*\d+|hem\s*\d+|đường\s*\d+|duong\s*\d+)\b',
            # Generic venues (lower priority - more ambiguous)
            r'\b(?:rạp\s*chiếu\s*phim|rap\s*chieu\s*phim|cinema|lotte|cgv|galaxy)\b',
            r'\b(?:trung\s*tâm\s*thương\s*mại|trung\s*tam\s*thuong\s*mai|mall|plaza|center|centre)\b',
            r'\b(?:sân\s*bay|san\s*bay|ga\s*tàu|ga\s*tau|bến\s*xe|ben\s*xe|trạm\s*xe\s*buýt|tram\s*xe\s*buyt)\b',
            r'\b(?:bệnh\s*viện|benh\s*vien|phòng\s*khám|phong\s*kham|nha\s*khoa|nha\s*khoa)\b',
            r'\b(?:trường\s*học|truong\s*hoc|đại\s*học|dai\s*hoc|học\s*viện|hoc\s*vien|trường\s*đại\s*học|truong\s*dai\s*hoc)\b',
            r'\b(?:thư\s*viện|thu\s*vien|thư\s*viện\s*tỉnh|thu\s*vien\s*tinh)\b',
            r'\b(?:nhà\s*hàng|nha\s*hang|quán\s*ăn|quan\s*an|quán\s*cà\s*phê|quan\s*ca\s*phe|cafe|restaurant)\b',
            r'\b(?:khách\s*sạn|khach\s*san|hotel|resort|homestay|nhà\s*nghỉ|nha\s*nghi)\b',
            r'\b(?:công\s*viên|cong\s*vien|park|công\s*viên\s*thống\s*nhất|cong\s*vien\s*thong\s*nhat)\b',
            r'\b(?:văn\s*phòng|van\s*phong|office|công\s*ty|cong\s*ty|company)\b',
            r'\b(?:phòng\s*họp|phong\s*hop|meeting\s*room|conference\s*room)\b',
            r'\b(?:giảng\s*đường|giang\s*duong|lecture\s*hall|lớp\s*học|lop\s*hoc|classroom)\b',
            r'\b(?:siêu\s*thị|sieu\s*thi|market|vinmart|co\.op|coop)\b',
            r'\b(?:bể\s*bơi|be\s*boi|pool|gym|hồ\s*bơi|ho\s*boi|fitness\s*center)\b',
            r'\b(?:spa|salon|làm\s*đẹp|lam\s*dep|beauty\s*salon)\b',
            r'\b(?:chợ|cho|market|traditional\s*market)\b',
            r'\b(?:công\s*viên\s*thống\s*nhất|cong\s*vien\s*thong\s*nhat|thống\s*nhất|thong\s*nhat)\b',
            r'\b(?:sông\s*hàn|song\s*han|cafe\s*sông\s*hàn|cafe\s*song\s*han)\b',
            r'\b(?:hương\s*sen|huong\s*sen|café\s*hương\s*sen|cafe\s*huong\s*sen)\b',
            r'\b(?:đà\s*nẵng|da\s*nang|lotte\s*cinema|lotte\s*cinema\s*đà\s*nẵng)\b',
            # Additional common locations from training data
            r'\b(?:villa|căn\s*hộ|can\s*ho|apartment|chung\s*cư|chung\s*cu)\b',
            r'\b(?:trạm\s*xe\s*buýt|tram\s*xe\s*buyt|bus\s*station)\b',
            r'\b(?:ga\s*tàu\s*xe\s*lửa|ga\s*tau\s*xe\s*lua|train\s*station)\b',
            r'\b(?:cảng|cang|port|harbor)\b',
            r'\b(?:sân\s*tennis|san\s*tennis|court)\b',
            r'\b(?:sân\s*bóng|san\s*bong|stadium|field)\b',
            r'\b(?:sân\s*bay\s*tân\s*sơn\s*nhất|san\s*bay\s*tan\s*son\s*nhat)\b',
            r'\b(?:bệnh\s*viện\s*việt\s*đức|benh\s*vien\s*viet\s*duc)\b',
            r'\b(?:trường\s*đại\s*học\s*bách\s*khoa|truong\s*dai\s*hoc\s*bach\s*khoa)\b',
        ]
        
        # Search for location patterns (highest priority first)
        # Use text_cleaned (reminder keywords already removed)
        text_lower = text_cleaned.lower()
        
        for pattern in known_locations:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                location_candidate = match.group(0).strip()
                
                # Validate: Make sure it's not part of the event name
                if event_name and location_candidate.lower() in event_name.lower():
                    continue
                
                # Additional validation: Skip if it's a compound event phrase
                # e.g., "đi chợ", "ăn buffet" where "chợ"/"buffet" is event, not location
                # ENHANCED: Added more compound event patterns to avoid false positives
                compound_event_patterns = [
                    r'\b(?:đi|di|ra|den|đến|toi|tới)\s+' + re.escape(location_candidate) + r'\b',
                    r'\b(?:ăn|an|uống|uong|mua|mua|ban|ban)\s+' + re.escape(location_candidate) + r'\b',
                    r'\b(?:xem|xem|choi|chơi|tap|tap|hoc|học)\s+' + re.escape(location_candidate) + r'\b',
                    r'\b(?:gap|gặp|tham|thăm|kham|khám)\s+' + re.escape(location_candidate) + r'\b',
                ]
                is_event_part = any(re.search(p, text_lower, re.IGNORECASE) for p in compound_event_patterns)
                if is_event_part:
                    continue
                
                # Final cleaning and validation
                location_candidate = self._clean_location_of_time_components(location_candidate)
                if location_candidate and self._validate_location(location_candidate):
                    return location_candidate
        
        return None

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
            location_candidate = loc_match.group(1).strip()
            
            # CRITICAL FIX v0.6.3: Enhanced time component filtering
            location_candidate = self._clean_location_of_time_components(location_candidate)
            
            # Only set location if something remains after cleaning
            if location_candidate:
                results['location'] = location_candidate
            
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
        # v0.6.3: Only apply if event has explicit location keywords to avoid false splits
        if not results['location'] and results['event_name']:
            # Check if event contains location keywords
            location_keywords = [
                'phong', 'phòng', 'cong ty', 'công ty', 'van phong', 'văn phòng',
                'nha', 'nhà', 'truong', 'trường', 'benh vien', 'bệnh viện',
                'quan', 'quán', 'san', 'sân', 'cong vien', 'công viên',
                'be boi', 'bể bơi', 'rap', 'rạp', 'vincom', 'vinmart',
                'california', 'paris', 'trung nguyen', 'trung nguyên',
                'linh dam', 'linh đàm', 'thong nhat', 'thống nhất',
                'bach mai', 'bạch mai', 'cho', 'chợ', 'sieu thi', 'siêu thị'
            ]
            
            has_location_keyword = any(kw in results['event_name'].lower() for kw in location_keywords)
            
            # Only split event/location if we have location keywords
            if has_location_keyword:
                event_parts = results['event_name'].split()
            
                # Common single-word event verbs (both diacritic and non-diacritic)
                # v0.6.3: Expanded list with more variants
                # v1.0.6: Significantly expanded to match training_100k_comprehensive.json dataset
                single_verbs = [
                    'hop', 'họp', 'hoc', 'học', 'lam', 'làm', 'gap', 'gặp', 
                    'di', 'đi', 'kham', 'khám', 'le', 'lễ', 'an', 'ăn',
                    'uong', 'uống', 'tap', 'tập', 'chay', 'chạy', 'xem',
                    'mua', 'ban', 'bán', 'doc', 'đọc', 'viet', 'viết',
                    'nop', 'nộp', 'goi', 'gọi', 'dat', 'đặt', 'dua', 'đưa',
                    'tham', 'nau', 'nấu', 'don', 'dọn', 'review', 'cafe',
                    # v1.0.6: Additional common Vietnamese verbs
                    'ngủ', 'ngu', 'nghi', 'nghỉ', 'choi', 'chơi', 'hat', 'hát',
                    'dao', 'dạo', 'boi', 'bơi', 'nhay', 'nhảy', 'dua', 'đua',
                    'thi', 'thi', 'trao', 'giao', 'nhan', 'nhận', 'gui', 'gửi',
                    'sua', 'sửa', 'cai', 'cài', 'chuẩn', 'chuan', 'kiem', 'kiểm',
                    'thuc', 'thực', 'trien', 'triển', 'phat', 'phát', 'thu', 'thử'
                ]
                
                # Common two-word event phrases (verb + object/complement)
                # v0.6.3: Added more variants including non-diacritic versions
                # v0.6.4: Added more common phrases
                # v1.0.6: Massively expanded to cover training_100k_comprehensive.json patterns
                two_word_events = [
                    'lam viec', 'làm việc', 'gap khach', 'gặp khách', 'gap ban', 'gặp bạn', 
                    'gap doi', 'gặp đối', 'gap khach hang', 'gặp khách hàng',
                    'an com', 'ăn cơm', 'an tiec', 'ăn tiệc', 'uong cafe', 'uống cafe', 
                    'uong tra', 'uống trà', 'tap gym', 'tập gym', 'tap yoga', 'tập yoga', 
                    'chay bo', 'chạy bộ', 'di bo', 'đi bộ', 'xem phim', 'mua sam', 'mua sắm',
                    'ban hang', 'bán hàng', 'hop team', 'họp team', 'hop nhom', 'họp nhóm', 
                    'doc sach', 'đọc sách', 'viet bao', 'viết báo', 'nop bao', 'nộp báo',
                    'di cong', 'đi công', 'di kham', 'đi khám', 'di cho', 'đi chợ',
                    'di sieu', 'đi siêu', 'goi dien', 'gọi điện', 'dat lich', 'đặt lịch',
                    'hoc bai', 'học bài', 'hoc online', 'học online', 'tap the', 'tập thể',
                    'dua con', 'đưa con', 'tham ba', 'thăm bà', 'di cong vien', 'đi công viên',
                    # v0.6.4: Add compound phrases
                    'sinh nhat', 'sinh nhật', 'ky niem', 'kỷ niệm', 'le ky', 'lễ ký',
                    'goi dien', 'gọi điện',
                    # v1.0.6: Additional two-word events from training dataset
                    'an sang', 'ăn sáng', 'an trua', 'ăn trưa', 'an toi', 'ăn tối',
                    'lam bao', 'làm báo', 'lam du', 'làm dự', 'hop giao', 'họp giao',
                    'hop du', 'họp dự', 'hop ke', 'họp kế', 'nop du', 'nộp dự',
                    'nop bao', 'nộp báo', 'tap boi', 'tập bơi', 'di yoga', 'đi yoga',
                    'di gym', 'đi gym', 'xem rap', 'xem rạp', 'di rap', 'đi rạp',
                    'tham benh', 'thăm bệnh', 'kham benh', 'khám bệnh', 'kham suc', 'khám sức',
                    'hop ban', 'họp ban', 'hop phu', 'họp phụ', 'lam an', 'làm ăn',
                    'di an', 'đi ăn', 'di uong', 'đi uống', 'di cafe', 'đi cafe',
                    'di tra', 'đi trà', 'review san', 'review sản', 'mua do', 'mua đồ',
                    'ban do', 'bán đồ', 'don dep', 'dọn dẹp', 'nau an', 'nấu ăn',
                    'giao hang', 'giao hàng', 'nhan hang', 'nhận hàng', 'gui hang', 'gửi hàng',
                    'cai dat', 'cài đặt', 'sua chua', 'sửa chữa', 'kiem tra', 'kiểm tra',
                    'thuc hien', 'thực hiện', 'trien khai', 'triển khai', 'phat trien', 'phát triển'
                ]
                
                # Common three-word event phrases
                # v0.6.3: Added more variants including non-diacritic versions
                # v0.6.4: Significantly expanded for complex events
                # v1.0.6: Massively expanded to cover training_100k_comprehensive.json patterns
                three_word_events = [
                    'gap doi tac', 'gặp đối tác', 'gap khach hang', 'gặp khách hàng',
                    'hop ban giam', 'họp ban giám', 'lam bai tap', 'làm bài tập',
                    'doc bao cao', 'đọc báo cáo', 'viet bao cao', 'viết báo cáo',
                    'nop bao cao', 'nộp báo cáo', 'di kham benh', 'đi khám bệnh',
                    'di cong tac', 'đi công tác', 'tham gia le', 'tham gia lễ',
                    'sinh nhat me', 'sinh nhật mẹ', 'ky niem cuoi', 'kỷ niệm cưới',
                    'hop phu huynh', 'họp phụ huynh', 'di sieu thi', 'đi siêu thị',
                    'goi dien cho', 'gọi điện cho', 'dat lich nha', 'đặt lịch nha',
                    'hoc tieng anh', 'học tiếng anh', 'hoc boi loi', 'học bơi lội',
                    'dua con di', 'đưa con đi', 'tham ba ngoai', 'thăm bà ngoại',
                    # v0.6.4: Add more complex 3-word events
                    'le ky ket', 'lễ ký kết', 'di cong vien', 'đi công viên',
                    # v1.0.6: Additional three-word events from training dataset
                    'lam bao cao', 'làm báo cáo', 'hop ke hoach', 'họp kế hoạch',
                    'hop du an', 'họp dự án', 'lam du an', 'làm dự án',
                    'nop du an', 'nộp dự án', 'hop giao ban', 'họp giao ban',
                    'di kham suc', 'đi khám sức', 'kham suc khoe', 'khám sức khỏe',
                    'di mua sam', 'đi mua sắm', 'di xem phim', 'đi xem phim',
                    'tap the duc', 'tập thể dục', 'tap the hinh', 'tập thể hình',
                    'di tap gym', 'đi tập gym', 'di tap yoga', 'đi tập yoga',
                    'di tap boi', 'đi tập bơi', 'review san pham', 'di cafe 24h',
                    'an tiec cuoi', 'ăn tiệc cưới', 'hop ban giam', 'họp ban giám',
                    'sinh nhat ban', 'sinh nhật bạn', 'sinh nhat con', 'sinh nhật con',
                    'ky niem ngay', 'kỷ niệm ngày', 'le khai truong', 'lễ khai trương',
                    'le tot nghiep', 'lễ tốt nghiệp', 'le thanh lap', 'lễ thành lập'
                ]
                
                # v0.6.4: NEW - Four+ word event phrases for very complex events
                # These are extracted FIRST before checking shorter patterns
                complex_events = [
                    'le ky ket hop tac', 'lễ ký kết hợp tác',
                    'le ky ket hop tac chien luoc', 'lễ ký kết hợp tác chiến lược',
                ]
                
                # v0.6.4: Check for very long complex events FIRST (4-15 words)
                complex_event_found = False
                if len(event_parts) >= 4:
                    # Try to match complex multi-word events (up to 15 words for very long formal events)
                    for length in range(min(15, len(event_parts)), 3, -1):
                        check_phrase = ' '.join(event_parts[:length])
                        # Check if it starts with common complex event patterns
                        if check_phrase.startswith(('le ky ket', 'lễ ký kết', 'hop dong', 'hợp đồng')):
                            # This is likely a long event name, keep it all
                            results['event_name'] = self._clean_event_name(check_phrase, results.get('time_str'))
                            complex_event_found = True
                            # Check if there's location after
                            if len(event_parts) > length:
                                location_candidate = ' '.join(event_parts[length:])
                                location_candidate = self._clean_location_of_time_components(location_candidate)
                                if location_candidate:
                                    results['location'] = location_candidate
                            break
                
                # If event has 4+ words and NOT a complex event, try to split event from location
                if len(event_parts) >= 4 and not complex_event_found:
                    # v0.6.4: Special case for "gọi điện cho <person>" - keep person name as part of event
                    three_word_check = ' '.join(event_parts[:3])
                    if three_word_check in ['goi dien cho', 'gọi điện cho'] and len(event_parts) == 4:
                        # "goi dien cho lan" → event="goi dien cho lan" (all 4 words)
                        results['event_name'] = self._clean_event_name(' '.join(event_parts[:4]), results.get('time_str'))
                    # Check if it's a three-word event phrase
                    elif three_word_check in three_word_events:
                        # "gap doi tac van phong ABC" → event="gap doi tac", location="van phong ABC"
                        results['event_name'] = self._clean_event_name(three_word_check, results.get('time_str'))
                        location_candidate = ' '.join(event_parts[3:])
                        location_candidate = self._clean_location_of_time_components(location_candidate)
                        if location_candidate:
                            results['location'] = location_candidate
                    # Check if it's a two-word event phrase
                    elif ' '.join(event_parts[:2]) in two_word_events:
                        two_word_check = ' '.join(event_parts[:2])
                        results['event_name'] = self._clean_event_name(two_word_check, results.get('time_str'))
                        location_candidate = ' '.join(event_parts[2:])
                        location_candidate = self._clean_location_of_time_components(location_candidate)
                        if location_candidate:
                            results['location'] = location_candidate
                    elif event_parts[0] in single_verbs:
                        # Single-word event
                        results['event_name'] = self._clean_event_name(event_parts[0], results.get('time_str'))
                        location_candidate = ' '.join(event_parts[1:])
                        location_candidate = self._clean_location_of_time_components(location_candidate)
                        if location_candidate:
                            results['location'] = location_candidate
                
                # If event has exactly 3 words, check three-word events first, then two-word
                elif len(event_parts) == 3:
                    three_word_check = ' '.join(event_parts[:3])
                    two_word_check = ' '.join(event_parts[:2])
                    
                    # v0.6.4: Check 3-word events FIRST to avoid false splits
                    # Example: "di sieu thi" should be 1 event, not "di sieu" + location "thi"
                    if three_word_check in three_word_events:
                        # Keep all 3 words as event (no location split)
                        results['event_name'] = self._clean_event_name(three_word_check, results.get('time_str'))
                    elif two_word_check in two_word_events:
                        # "an com nha hang" → event="an com", location="nha hang"
                        results['event_name'] = self._clean_event_name(two_word_check, results.get('time_str'))
                        location_candidate = ' '.join(event_parts[2:])
                        location_candidate = self._clean_location_of_time_components(location_candidate)
                        if location_candidate:
                            results['location'] = location_candidate
                    elif event_parts[0] in single_verbs:
                        # Single-word event: "hop cong ty ABC" → event="hop", location="cong ty ABC"
                        results['event_name'] = self._clean_event_name(event_parts[0], results.get('time_str'))
                        location_candidate = ' '.join(event_parts[1:])
                        location_candidate = self._clean_location_of_time_components(location_candidate)
                        if location_candidate:
                            results['location'] = location_candidate
                    # Otherwise, keep event as-is (might be complex phrase like "le nha tho")
        
        # v0.6.4: FINAL cleanup of event_name to remove date patterns and standalone period words
        # This runs after all heuristic logic to ensure all extractions are cleaned
        if results.get('event_name'):
            results['event_name'] = self._clean_event_name(results['event_name'], results.get('time_str'))

        # ------------------- Post-validation rules -------------------
        # If there is no time context (no explicit time_str and no relative time words in original text),
        # treat the input as 'no schedule' and clear the event_name to avoid creating events without time.
        # This reduces false-positives for stress_missing cases like "viết email" or single verbs like "gặp".
        try:
            orig_text = original_text or ''
        except NameError:
            orig_text = ''

        # If there's no extracted time and the original text doesn't contain time-related words, clear event
        if not results.get('time_str'):
            if not self.time_related_words.search(orig_text):
                results['event_name'] = ''

        # Also reject extremely short or nonsensical event names (boundary_short cases)
        ev = results.get('event_name') or ''
        ev_stripped = ev.strip()
        token_count = len(orig_text.split()) if orig_text else 0
        # Clear if event looks purely time-like (always) OR if it's extremely short AND the original input is a single token
        if ev_stripped:
            is_time_like = re.fullmatch(r"^[\d\s:hmghgio\.\/\-]+$", ev_stripped, flags=re.IGNORECASE) is not None
            if is_time_like:
                results['event_name'] = ''
            else:
                # Only clear very short single-token inputs (likely noise). If a time_str exists (we have time), keep short verbs like 'ăn', 'đi'.
                if not results.get('time_str') and len(ev_stripped) <= 2 and token_count <= 1:
                    results['event_name'] = ''
        
        return results
    
    def _clean_event_name(self, text: str, time_str: str = None) -> str:
        """Clean time-related words from event name.
        Only removes period words (sáng, trưa, tối, etc.) if they appeared in the extracted time_str.
        This preserves period words that are part of event phrases like "ăn trưa" (have lunch).
        """
        if not text:
            return ""
        
        # NEW: Remove common pronoun + verb prefixes (tôi đi, tôi sẽ, mình đi, etc.)
        # These are filler words that don't add meaning to the event
        pronoun_verb_patterns = r"\b(?:toi|tôi|minh|mình|chúng\s*tôi|chung\s*toi)\s+(?:di|đi|se|sẽ|can|cần|phai|phải|muon|muốn|den|đến|ve|về)\b"
        cleaned = re.sub(pronoun_verb_patterns, " ", text, flags=re.IGNORECASE)
        
        # v0.6.4: Remove date patterns that leak into event name
        # Pattern: "6.12", "06-12", "6-12", "12/12", etc.
        cleaned = re.sub(r'\b\d{1,2}[-./]\d{1,2}\b', '', cleaned)
        cleaned = re.sub(r'\b\d{1,2}\.\d{1,2}\b', '', cleaned)
        
        # v0.6.4: Remove standalone time period words if NOT part of common event phrases
        # Check if "toi/tối" is standalone (not part of "ăn tối", "về tối", etc.)
        # Common event phrases with time periods: "ăn sáng", "ăn trưa", "ăn tối", "về tối"
        event_with_period = r'\b(?:an|ăn|ve|về)\s+(?:sang|sáng|trua|trưa|toi|tối|chieu|chiều)\b'
        if not re.search(event_with_period, cleaned, re.IGNORECASE):
            # Remove standalone period words
            cleaned = re.sub(r'\b(?:toi|tối|sang|sáng|trua|trưa|chieu|chiều)\b', '', cleaned, flags=re.IGNORECASE)
        
        # First pass: Remove time connectors and relative time words (always remove these)
        time_connectors = r"(?:vào|vao|lúc|luc|vào\s+lúc|vao\s+luc|khoảng|khoang|từ|tu|đến|den|tới|cho\s+đến|cho\s+den|bắt\s+đầu|bat\s+dau|kết\s+thúc|ket\s+thuc)"
        relative_time = r"(?:hôm\s*nay|hom\s*nay|ngày\s*mai|ngay\s*mai|mai|ngày\s*mốt|ngay\s*mot|mốt|mot|hôm\s*qua|hom\s*qua|qua|nay|tuần\s*sau|tuan\s*sau|tuần\s*trước|tuan\s*truoc)"
        timezone_words = r"(?:utc|gmt|múi\s*giờ|mui\s*gio)"
        
        cleaned = re.sub(fr"\b({time_connectors}|{relative_time}|{timezone_words})\b", " ", cleaned, flags=re.IGNORECASE)
        
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
        # 3) v1.0.7: If location not found by regex, try heuristic extraction (no marker needed)
        if not ex.get('location'):
            loc_heuristic = self._extract_location_heuristic(text_wo_reminder, ex.get('event_name', ''))
            if loc_heuristic:
                ex['location'] = loc_heuristic
        # 4) If still no location, try NER as final backup (slowest but most comprehensive)
        if not ex.get('location'):
            loc_ner, _ = self._extract_location_ner(text_wo_reminder)
            if loc_ner:
                # CRITICAL FIX v0.6.3: Enhanced time component filtering for NER
                loc_ner = self._clean_location_of_time_components(loc_ner)
                if loc_ner:  # Only set if something remains after cleaning
                    ex['location'] = loc_ner
        # Parse time
        start_dt, end_dt = parse_vietnamese_time_range(ex['time_str'], relative_base=self.relative_base)
        # If parsing produced no start_dt but we have a period-only time_str (e.g., "tối", "hôm nay"),
        # infer a reasonable default hour so 'gặp nay' / 'học tối' produce a start_time.
        if not start_dt and ex.get('time_str'):
            ts = ex['time_str'].lower()
            # Map period words to default hours
            period_map = {
                'sáng': 9, 'sang': 9, 'sáng': 9, 'sang': 9,
                'trưa': 12, 'trua': 12,
                'chiều': 15, 'chieu': 15,
                'tối': 20, 'toi': 20, 'đêm': 22, 'dem': 22, 'khuya': 22
            }
            chosen_hour = None
            for p, h in period_map.items():
                if p in ts:
                    chosen_hour = h
                    break

            # If found a period, build a datetime at that hour for the relative date
            if chosen_hour is not None:
                try:
                    base = self.relative_base or datetime.now()
                    # Use parse_vietnamese_time_range to resolve the date (day/month/year) if possible
                    # Fallback: if parse didn't resolve day, assume today/relative base
                    # We'll set start_dt to base with chosen_hour and zero minutes
                    start_dt = base.replace(hour=chosen_hour, minute=0, second=0, microsecond=0)
                except Exception:
                    start_dt = None
        
        # ENHANCED: If still no time but we have relative time context, infer default time
        # This handles cases like "tháng này điều trị" (this month treatment) - assume morning
        if not start_dt and ex.get('time_str'):
            ts_lower = ex['time_str'].lower()
            # Check for relative time indicators that suggest we should have a time
            relative_indicators = [
                'tháng này', 'thang nay', 'tuần này', 'tuan nay', 'tuần sau', 'tuan sau',
                'tháng sau', 'thang sau', 'tháng tới', 'thang toi', 'tuần tới', 'tuan toi',
                'ngày mai', 'ngay mai', 'mai', 'ngày kia', 'ngay kia', 'hôm nay', 'hom nay',
                'thứ hai', 'thu hai', 'thứ ba', 'thu ba', 'thứ tư', 'thu tu', 'thứ năm', 'thu nam',
                'thứ sáu', 'thu sau', 'thứ bảy', 'thu bay', 'chủ nhật', 'chu nhat'
            ]
            
            has_relative = any(indicator in ts_lower for indicator in relative_indicators)
            
            if has_relative:
                # Infer morning time (9 AM) for relative time expressions without explicit hours
                try:
                    base = self.relative_base or datetime.now()
                    start_dt = base.replace(hour=9, minute=0, second=0, microsecond=0)
                except Exception:
                    start_dt = None
        result = {
            'event_name': ex['event_name'],  # Changed from 'event' to match database schema
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
            (self.reminder_month_regex1, 43200),  # 30 days * 24 hours * 60 min
            (self.reminder_week_regex1, 10080),   # 7 days * 24 hours * 60 min
            (self.reminder_day_regex1, 1440),     # 24 hours * 60 min
            (self.reminder_hour_regex1, 60),
            (self.reminder_min_regex1, 1),
            (self.reminder_month_regex2, 43200),
            (self.reminder_week_regex2, 10080),
            (self.reminder_day_regex2, 1440),
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
        
        # v1.0.7: Clean standalone reminder keywords that weren't matched by patterns
        # (e.g., "before 2" when pattern matched "nhac 2 week" but left "before" behind)
        standalone_reminder = r'\b(?:before|earlier|notify|som|sớm|hon|hơn)\b'
        working = re.sub(standalone_reminder, ' ', working, flags=re.IGNORECASE)
        
        # Collapse multiple spaces
        working = re.sub(r"\s{2,}", " ", working).strip()
        return minutes, working, has

    def _clean_location_of_reminder(self, loc: Optional[str]) -> Optional[str]:
        if not loc:
            return loc
        # Remove reminder keywords from location, both diacritic and non-diacritic
        loc2 = self.reminder_presence_regex.sub(' ', loc)
        loc2 = re.sub(r"\s{2,}", " ", loc2).strip(" ,.-").strip()
        return loc2 or None
    
    def _validate_location(self, loc: Optional[str]) -> bool:
        """
        v1.0.5: Validation rules to reduce false positives in location extraction.
        v1.0.6: Enhanced to better recognize location names like "Cafe 24h", "Trung Nguyen"
        Returns True if location is valid, False otherwise.
        """
        if not loc:
            return False
        
        # Rule 1: Minimum length (at least 2 characters after cleaning)
        if len(loc.strip()) < 2:
            return False
        
        # Rule 2: Reject pure time period words
        time_periods = ['sang', 'sáng', 'trua', 'trưa', 'chieu', 'chiều', 'toi', 'tối', 'dem', 'đêm', 'khuya']
        if loc.strip().lower() in time_periods:
            return False
        
        # Rule 3: Reject if contains only digits and whitespace
        if re.match(r'^[\d\s:]+$', loc):
            return False
        
        # Rule 4: Reject common time-only phrases
        invalid_phrases = [
            r'^\d{1,2}\s*h\s*\d{1,2}$',  # "14h30", "9h15"
            r'^\d{1,2}:\d{1,2}$',  # "14:30"
            r'^thứ\s+[2-8]$',  # "thứ 2"
            r'^t[2-8]$',  # "t2"
            r'^cn$',  # "cn"
            r'^mai$',  # "mai"
            r'^nay$',  # "nay"
            r'^qua$',  # "qua"
        ]
        
        loc_lower = loc.lower().strip()
        for pattern in invalid_phrases:
            if re.match(pattern, loc_lower):
                return False
        
        # Rule 5: Must contain at least one location indicator OR be a known location
        # v1.0.6: Expanded location indicators to cover training_100k_comprehensive.json locations
        # ENHANCED: Added many more location indicators to improve detection rate
        location_indicators = [
            'phong', 'phòng', 'cong ty', 'công ty', 'van phong', 'văn phòng',
            'nha', 'nhà', 'truong', 'trường', 'benh vien', 'bệnh viện',
            'quan', 'quán', 'san', 'sân', 'cong vien', 'công viên',
            'be boi', 'bể bơi', 'rap', 'rạp', 'vincom', 'vinmart',
            'california', 'paris', 'trung nguyen', 'trung nguyên',
            'linh dam', 'linh đàm', 'thong nhat', 'thống nhất',
            'bach mai', 'bạch mai', 'cho', 'chợ', 'sieu thi', 'siêu thị',
            'cafe', 'coffee', 'hotel', 'khach san', 'khách sạn',
            'dai hoc', 'đại học', 'hoc vien', 'học viện',
            # v1.0.6: Additional location keywords from training dataset
            '24h', 'highlands', 'starbucks', 'kfc', 'lotte', 'aeon',
            'gym', 'fitness', 'yoga', 'spa', 'salon', 'clinic',
            'mall', 'plaza', 'tower', 'center', 'centre', 'building',
            'huong', 'hương', 'tram', 'trạm', 'toa', 'toà', 'khu',
            'duong', 'đường', 'pho', 'phố', 'hem', 'hẻm', 'ngo', 'ngõ',
            'xa', 'xã', 'thi tran', 'thị trấn', 'huyen', 'huyện',
            'thanh pho', 'thành phố', 'tp', 'ha noi', 'hà nội',
            'sai gon', 'sài gòn', 'da nang', 'đà nẵng',
            'golden', 'diamond', 'pearl', 'star', 'green', 'blue', 'red',
            'luxury', 'royal', 'king', 'queen', 'prince', 'princess',
            # Additional common Vietnamese location patterns
            'homestay', 'resort', 'villa', 'apartment', 'chung cu', 'chung cư',
            'bus station', 'train station', 'airport', 'cinema', 'theater',
            'restaurant', 'coffee shop', 'bar', 'pub', 'club',
            'park', 'garden', 'lake', 'river', 'beach', 'mountain',
            'hospital', 'clinic', 'school', 'university', 'library',
            'office', 'company', 'factory', 'warehouse', 'store',
            'market', 'supermarket', 'mall', 'plaza', 'center'
        ]
        
        # Check if location contains ANY indicator
        has_indicator = any(indicator in loc_lower for indicator in location_indicators)
        
        # Rule 6: If no indicator, check for proper location names (capitalized multi-word)
        # Example: "Bạch Mai", "Trung Nguyên", "California Fitness"
        if not has_indicator:
            # Must have at least 2 words OR be a single capitalized word with length >= 4
            words = loc.split()
            if len(words) >= 2:
                # Multi-word location likely valid
                has_indicator = True
            elif len(words) == 1 and len(words[0]) >= 4:
                # Single word but substantial length (e.g., "Vincom")
                has_indicator = True
        
        return has_indicator
    
    def _clean_location_of_time_components(self, loc: Optional[str]) -> Optional[str]:
        """
        CRITICAL: Remove time-related components from location extraction.
        Fixes bug where "18:00 thứ 2" → location="00 thứ 2"
        v1.0.5: Enhanced with validation rules
        """
        if not loc:
            return loc
        
        original = loc
        
        # Pattern 1: Remove "X:00 thứ Y" → "00 thứ Y" (e.g., "18:00 thứ 2" → "00 thứ 2")
        loc = re.sub(r'\b\d{1,2}:00\s+', '', loc, flags=re.IGNORECASE)
        
        # Pattern 2: Remove "Xh thứ Y" → "h thứ Y" (e.g., "9h thứ 2" → "h thứ 2")
        loc = re.sub(r'\b\d{1,2}h\s+', '', loc, flags=re.IGNORECASE)
        
        # Pattern 3: Remove standalone time indicators
        # "thứ 2", "thứ 3", "t2", "t3", etc.
        time_day_patterns = [
            r'\b(?:thứ|thu)\s*[2-8]\b',  # thứ 2-8
            r'\bt[2-8]\b',                # t2-t8
            r'\bcn\b',                    # cn (chủ nhật)
        ]
        for pattern in time_day_patterns:
            loc = re.sub(pattern, '', loc, flags=re.IGNORECASE)
        
        # Pattern 4: Remove "h sáng/chiều/tối/trưa" patterns
        loc = re.sub(r'\bh\s+(?:sáng|sang|chiều|chieu|tối|toi|trưa|trua)\b', '', loc, flags=re.IGNORECASE)
        
        # Pattern 5: Remove "h ngày X" patterns
        loc = re.sub(r'\bh\s+(?:ngày|ngay)\s+\w+\b', '', loc, flags=re.IGNORECASE)
        
        # Pattern 6: Remove standalone "00" from ":00"
        loc = re.sub(r'\b00\b', '', loc)
        
        # Pattern 7: Remove standalone "h" or "giờ"
        loc = re.sub(r'\b(?:h|giờ|gio)\b', '', loc, flags=re.IGNORECASE)
        
        # Pattern 8: Remove year/month/day patterns (already handled but double-check)
        loc = re.sub(r'\b(?:năm|nam)\s+\d{4}\b', '', loc, flags=re.IGNORECASE)
        loc = re.sub(r'\b(?:tháng|thang)\s+\d{1,2}\b', '', loc, flags=re.IGNORECASE)
        loc = re.sub(r'\b(?:ngày|ngay)\s+\d{1,2}\b', '', loc, flags=re.IGNORECASE)
        
        # Pattern 9: Remove time range indicators
        loc = re.sub(r'\b(?:mai|hôm nay|hom nay|ngày mai|ngay mai)\b', '', loc, flags=re.IGNORECASE)
        loc = re.sub(r'\b(?:sáng|sang|chiều|chieu|tối|toi|trưa|trua)\s+(?:mai|nay)\b', '', loc, flags=re.IGNORECASE)
        
        # Pattern 10: Remove "ngày mốt", "ngày kia", "mai mốt"
        loc = re.sub(r'\b(?:ngày|ngay)\s+(?:mốt|mot|kia)\b', '', loc, flags=re.IGNORECASE)
        loc = re.sub(r'\b(?:mai)\s+(?:mốt|mot)\b', '', loc, flags=re.IGNORECASE)
        
        # Clean up whitespace
        loc = re.sub(r'\s{2,}', ' ', loc).strip(" ,.-").strip()
        
        # If nothing left or only punctuation/numbers, return None
        if not loc or len(loc) <= 2 or loc.isdigit() or all(c in ' ,.-:' for c in loc):
            return None
        
        # v1.0.5: Apply validation rules
        if not self._validate_location(loc):
            return None
        
        # Return cleaned location
        return loc
