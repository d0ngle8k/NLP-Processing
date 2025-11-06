from __future__ import annotations
import re
from datetime import datetime, timedelta, timezone
from typing import Optional
import unicodedata
try:
    from zoneinfo import ZoneInfo  # Python 3.9+
except Exception:
    ZoneInfo = None  # Fallback: will use fixed offset

def _vn_norm(s: str) -> str:
    """Lowercase and remove Vietnamese diacritics for matching; map đ->d."""
    if not s:
        return ''
    s = s.lower()
    s = s.replace('đ', 'd').replace('Đ', 'D')
    nfkd = unicodedata.normalize('NFKD', s)
    return ''.join(c for c in nfkd if not unicodedata.combining(c))

# Only apply timezone when explicitly specified in the text. Default: naive datetimes for compatibility.
DEFAULT_TZ = None  # Could be ZoneInfo("Asia/Ho_Chi_Minh") if desired


def _has_period_flags(s_norm: str) -> dict[str, bool]:
    """Detect period hints: morning/afternoon/evening/noon/night/midnight in normalized text.
    
    Special cases:
    - "nua dem" (midnight) → 00:00
    - "12 gio sang" → 00:00 (midnight, not noon)
    - "12 gio chieu" / "12 noon" → 12:00 (noon)
    
    Also handles typos: "sang" (no accent), "toi" (no accent)
    """
    return {
        'sang': bool(re.search(r"\bs[aà]ng\b", s_norm)),
        'trua': bool(re.search(r"\btr[uư]a\b", s_norm)) or bool(re.search(r"\bnoon\b", s_norm)),
        'chieu': bool(re.search(r"\bchi[eê]u\b", s_norm)),
        'toi': bool(re.search(r"\bt[oô]i\b", s_norm) or re.search(r"\bd[eê]m\b", s_norm)),
        'nua_dem': bool(re.search(r"\bn[uư]a\s*d[eê]m\b", s_norm)) or bool(re.search(r"\bmidnight\b", s_norm)),
    }

def _adjust_hour_by_period(hh: int, flags: dict[str, bool]) -> int:
    """Convert 12-hour style to 24-hour with period validation.
    
    Định nghĩa thời gian (Time period definitions):
    - Sáng (morning): 00:00-11:59 (practical: 06:00-11:59)
    - Trưa (noon): 12:00 exactly
    - Chiều (afternoon): 12:00-17:59
    - Tối (evening): 18:00-21:59
    - Đêm (night): 22:00-23:59 and 00:00-05:59
    - Nửa đêm (midnight): 00:00 exactly
    
    Validation rules:
    - "nửa đêm" / "midnight" → 00:00
    - "12 giờ sáng" → 00:00 (midnight, following 12 AM convention)
    - "12 giờ chiều" / "12 noon" → 12:00 (noon)
    - "10 giờ trưa" → INVALID (trưa = 12:00 only) → fallback to 12:00
    - "10 giờ sáng" → 10:00 (valid)
    - "2 giờ chiều" → 14:00 (valid: 2 PM)
    - "8 giờ tối" → 20:00 (valid)
    """
    if hh is None:
        return hh
    
    # Special case: "nửa đêm" (midnight) → always 00:00
    if flags.get('nua_dem'):
        return 0
    
    # Special case: "12 giờ sáng" → 00:00 (midnight)
    # "sáng" with hour 12 is interpreted as 12 AM (start of day)
    if flags.get('sang') and hh == 12:
        return 0
    
    # Special case: "trưa" (noon) should be 12:00
    if flags.get('trua'):
        # If user says "X giờ trưa" but X != 12, it's ambiguous
        # Common interpretation: "trưa" = 12:00 or early afternoon
        if hh == 12:
            return 12  # Noon exactly
        elif 1 <= hh <= 5:
            # "1 giờ trưa", "2 giờ trưa" → 13:00, 14:00 (early afternoon)
            return hh + 12
        else:
            # Invalid: "10 giờ trưa" doesn't make sense
            # Fallback: interpret as 12:00 (noon)
            return 12
    
    # "tối" (evening) or "đêm" (night) → PM for 1-11
    if flags.get('toi'):
        if 1 <= hh <= 11:
            # "6 giờ tối" → 18:00, "10 giờ tối" → 22:00
            return hh + 12
        # 12 giờ tối → midnight (00:00)
        elif hh == 12:
            return 0
        return hh
    
    # "chiều" (afternoon) → PM for 1-11, but validate range 12:00-17:59
    if flags.get('chieu'):
        if 1 <= hh <= 5:
            # "1 giờ chiều" → 13:00, "5 giờ chiều" → 17:00
            return hh + 12
        elif hh == 12:
            return 12  # "12 giờ chiều" → 12:00 (noon/early afternoon)
        else:
            # "10 giờ chiều" is ambiguous (chiều ends ~18:00)
            # Fallback: treat as evening (add 12 if < 12)
            return hh + 12 if hh < 12 else hh
    
    # "sáng" (morning) → AM (no change for 0-11, except 12 handled above)
    # Default: keep original hour
    return hh

def _parse_explicit_time(s: str) -> tuple[Optional[int], Optional[int], str]:
    s = s.strip()
    s_norm = _vn_norm(s)
    
    # Map Vietnamese number words to digits
    # Include typo variations: "bah" (ba+h), "sáuh" (sau+h), "mườih" (muoi+h)
    number_words = {
        'mot': 1, 'moh': 1, 'moth': 1,  # typo: mộth
        'hai': 2, 'haih': 2,
        'ba': 3, 'bah': 3,  # typo: bah
        'bon': 4, 'bonh': 4, 'tu': 4, 'tuh': 4,
        'nam': 5, 'namh': 5,  # typo: nămh
        'sau': 6, 'sauh': 6,  # typo: sáuh
        'bay': 7, 'bayh': 7,
        'tam': 8, 'tamh': 8,  # typo: támh
        'chin': 9, 'chinh': 9,
        'muoi': 10, 'muoi': 10, 'mười': 10, 'muoih': 10,  # typo: mườih
        'muoi mot': 11, 'muoi hai': 12, 'muoi haih': 12, 'muoih haih': 12,  # typo variations
    }
    
    # Replace number words with digits in normalized string
    s_norm_numbers = s_norm
    # Sort by length (longest first) to avoid partial replacements
    for word, num in sorted(number_words.items(), key=lambda x: -len(x[0])):
        s_norm_numbers = re.sub(r"\b" + word + r"\b", str(num), s_norm_numbers)
    
    # "lúc 12 giờ" / "lúc 12h" - remove "lúc" prefix
    s_norm_numbers = re.sub(r"\bluc\s+", "", s_norm_numbers)
    
    #  rưỡi / giờ rưỡi /  rưỡi => HH:30
    m = re.search(r"\b(\d{1,2})\s*(?:h|gio|giờ)?\s*(?:ruoi|r\u01b0oi)\b", s_norm_numbers)
    if m:
        hh = int(m.group(1))
        mm = 30
        # remove the matched raw segment approximately by digits and 'rưỡi'
        s = re.sub(r"\b" + re.escape(m.group(1)) + r"\s*(?:h|giờ)?\s*r[ưu]ỡi\b", "", s, flags=re.IGNORECASE)
        return hh, mm, s.strip()
    # 10 giờ kém 15 => 09:45
    # Allow formats: 10h|10 giờ kém 15
    mk = re.search(r"\b(\d{1,2})\s*(?:h|gio|giờ)\s*k[eé]m\s*(\d{1,2})\b", s_norm_numbers)
    if mk:
        base_h = int(mk.group(1))
        minus_m = int(mk.group(2))
        hh = base_h - 1 if minus_m > 0 else base_h
        mm = 60 - minus_m if minus_m > 0 else 0
        # strip approximate raw segment
        s = re.sub(r"\b" + re.escape(mk.group(1)) + r"\s*(?:h|giờ)\s*k[eé]m\s*" + re.escape(mk.group(2)) + r"\b", "", s, flags=re.IGNORECASE)
        return hh, mm, s.strip()
    # 17:30
    m = re.search(r"\b(\d{1,2}):(\d{1,2})\b", s)
    if m:
        return int(m.group(1)), int(m.group(2)), re.sub(m.group(0), "", s, 1).strip()
    # 17h30 | 17h
    m = re.search(r"\b(\d{1,2})\s*h\s*(\d{1,2})?\b", s)
    if m:
        hh = int(m.group(1))
        mm = int(m.group(2) or 0)
        return hh, mm, re.sub(m.group(0), "", s, 1).strip()
    # "12 giờ 30 phút" / "12 giờ" - now with number word support
    m = re.search(r"\b(\d{1,2})\s*(?:gio|giờ)(?:\s*(\d{1,2})\s*(?:phut|phút))?\b", s_norm_numbers)
    if m:
        hh = int(m.group(1))
        mm = int(m.group(2) or 0)
        return hh, mm, re.sub(r"\b\d{1,2}\s*(?:giờ|gio)(?:\s*\d{1,2}\s*(?:phút|phut))?\b", "", s, 1, flags=re.IGNORECASE).strip()
    # Standalone number (from number word conversion like "támh" -> "8", "mười haih" -> "12")
    # This catches cases where number words with typo "h" were converted to digits
    m = re.search(r"\b(\d{1,2})\b", s_norm_numbers)
    if m:
        hh = int(m.group(1))
        # Validate hour range
        if 0 <= hh <= 23:
            return hh, 0, re.sub(r"\b" + m.group(1) + r"\b", "", s_norm_numbers, 1).strip()
    return None, None, s


def _parse_explicit_date(base: datetime, s_norm: str) -> tuple[Optional[datetime], str]:
    # Format: DD.MM.YYYY or DD/MM/YYYY or DD-MM-YYYY
    m = re.search(r"\b(\d{1,2})[\.\-/](\d{1,2})[\.\-/](\d{4})\b", s_norm)
    if m:
        day = int(m.group(1))
        month = int(m.group(2))
        year = int(m.group(3))
        try:
            dt = datetime(year, month, day, base.hour, base.minute)
            return dt, re.sub(m.group(0), "", s_norm, 1).strip()
        except ValueError:
            pass
    
    # Format: DD.MM or DD/MM or DD-MM (short date, current year)
    m = re.search(r"\b(\d{1,2})[\.\-/](\d{1,2})\b", s_norm)
    if m:
        day = int(m.group(1))
        month = int(m.group(2))
        year = base.year
        try:
            dt = datetime(year, month, day, base.hour, base.minute)
            return dt, re.sub(m.group(0), "", s_norm, 1).strip()
        except ValueError:
            pass
    
    # Format: ngay 6 thang 12 (normalized Vietnamese)
    m = re.search(r"ngay\s*(\d{1,2})\s*thang\s*(\d{1,2})", s_norm)
    if m:
        day = int(m.group(1))
        month = int(m.group(2))
        year = base.year
        try:
            dt = datetime(year, month, day, base.hour, base.minute)
            return dt, re.sub(m.group(0), "", s_norm, 1).strip()
        except ValueError:
            pass
    
    return None, s_norm


def _parse_relative_words(base: datetime, s_norm: str) -> tuple[Optional[datetime], str]:
    text = s_norm
    
    # Handle compound time expressions: "tối mai", "sáng mai", "chiều mai", "đêm nay"
    # Support both with/without diacritics and typos (toi/tối, dem/đêm, sang/sáng)
    # Strategy: Only set DATE, let explicit time + period flags determine HOUR
    # Exception: If no explicit time, use default hours
    
    # "tối mai" = tomorrow evening (default 20:00 if no explicit time)
    if re.search(r"\btoi\s+mai\b", text):
        dt = (base + timedelta(days=1)).replace(hour=20, minute=0)
        text = re.sub(r"\btoi\s+mai\b", "", text).strip()
        return dt, text
    # "đêm nay" = tonight (default 22:00 if no explicit time)
    if re.search(r"\bdem\s+nay\b", text):
        dt = base.replace(hour=22, minute=0)
        text = re.sub(r"\bdem\s+nay\b", "", text).strip()
        return dt, text
    # "sáng mai" = tomorrow morning (default 08:00 if no explicit time)
    if re.search(r"\bsang\s+mai\b", text):
        dt = (base + timedelta(days=1)).replace(hour=8, minute=0)
        text = re.sub(r"\bsang\s+mai\b", "", text).strip()
        return dt, text
    # "chiều mai" = tomorrow afternoon (default 15:00 if no explicit time)
    if re.search(r"\bchieu\s+mai\b", text):
        dt = (base + timedelta(days=1)).replace(hour=15, minute=0)
        text = re.sub(r"\bchieu\s+mai\b", "", text).strip()
        return dt, text
    # "trưa mai" = tomorrow noon (default 12:00 if no explicit time)
    if re.search(r"\btrua\s+mai\b", text):
        dt = (base + timedelta(days=1)).replace(hour=12, minute=0)
        text = re.sub(r"\btrua\s+mai\b", "", text).strip()
        return dt, text
    
    # hom nay / ngay mai / mai
    # "hôm nay" keeps base date (today) but preserves base time
    # Will be overridden if explicit time is found later
    if re.search(r"\bhom\s+nay\b", text):
        dt = base  # Keep current base datetime
        text = re.sub(r"\bhom\s+nay\b", "", text).strip()
        return dt, text
    if re.search(r"\b(ngay mai|mai)\b", text):
        dt = (base + timedelta(days=1)).replace(hour=base.hour, minute=base.minute)
        text = re.sub(r"\b(ngay mai|mai)\b", "", text).strip()
        return dt, text
    # ngay mot / mot / ngay kia / mai mot => +2 days
    if re.search(r"\b(ngay mot|mai mot|mot|ngay kia)\b", text):
        dt = (base + timedelta(days=2)).replace(hour=base.hour, minute=base.minute)
        text = re.sub(r"\b(ngay mot|mai mot|mot|ngay kia)\b", "", text).strip()
        return dt, text
    # cuoi tuan -> Saturday 09:00 upcoming
    if re.search(r"\bcuoi tuan\b", text):
        days_ahead = (5 - base.weekday()) % 7  # 5 = Saturday
        days_ahead = 7 if days_ahead == 0 else days_ahead
        dt = (base + timedelta(days=days_ahead)).replace(hour=9, minute=0)
        text = re.sub(r"\bcuoi tuan\b", "", text).strip()
        return dt, text
    # thứ d / t d (tuần sau)?
    # Match "thứ 3", "thu 3", "t 3", "thứ ba", "thứ hai" etc.
    # Also match "tuần sau" before or after: "tuần sau thứ 3", "thứ 3 tuần sau"
    m = re.search(r"\b(?:(?:tuan sau\s+)?(?:thu[sứ]?|t)\s*(\d|hai|ba|tu|nam|sau|bay|tam)(?:\s+tuan sau)?)\b", text)
    if m:
        # Check if "tuần sau" appears anywhere in the match
        has_tuan_sau = 'tuan sau' in m.group(0)
        # Map word to number
        word_map = {'hai': 2, 'ba': 3, 'tu': 4, 'nam': 5, 'sau': 6, 'bay': 7, 'tam': 8}
        thu_str = m.group(1)
        thu = word_map.get(thu_str, int(thu_str) if thu_str.isdigit() else 2)
        
        # Validate range 2-8 (Mon-Sun: thứ 2-7, thứ 8=CN)
        if thu == 8:
            thu = 1  # Chủ nhật (Sunday) = thứ 8 = day 0
        if not (1 <= thu <= 7):
            thu = 2  # Default to Monday
        
        # Map to weekday (0=Mon, 6=Sun)
        if thu == 1:  # Chủ nhật
            target_wd = 6
        else:
            target_wd = (thu - 2) % 7  # thứ 2->0 (Mon), thứ 7->5 (Sat)
        
        days_ahead = (target_wd - base.weekday()) % 7
        
        # If "tuần sau" specified, always go to next week
        if has_tuan_sau:
            if days_ahead == 0:
                days_ahead = 7
            else:
                days_ahead += 7
        # If days_ahead == 0 (today is the target weekday), only skip if it's too late
        # For now, if it's the same day and no specific time extracted yet, keep it today
        # This will be refined when combining with time
        elif days_ahead == 0:
            # Keep today (will check time later)
            pass
        
        dt = (base + timedelta(days=days_ahead)).replace(hour=base.hour, minute=base.minute)
        text = text.replace(m.group(0), '').strip()
        return dt, text
    # CN / Chủ nhật (tuần sau)?
    m = re.search(r"\b(?:cn|chu\s+nhat)(?:\s*tuan sau)?\b", text)
    if m:
        target_wd = 6  # Sunday
        days_ahead = (target_wd - base.weekday()) % 7
        has_tuan_sau = 'tuan sau' in m.group(0)
        if has_tuan_sau:
            if days_ahead == 0:
                days_ahead = 7
            else:
                days_ahead += 7
        elif days_ahead == 0:
            # Same day - keep it
            pass
        dt = (base + timedelta(days=days_ahead)).replace(hour=base.hour, minute=base.minute)
        text = text.replace(m.group(0), '').strip()
        return dt, text
    # hom kia (two days ago)
    if re.search(r"\bhom kia\b", text):
        dt = (base - timedelta(days=2)).replace(hour=base.hour, minute=base.minute)
        text = re.sub(r"\bhom kia\b", "", text).strip()
        return dt, text
    # tuần sau / tuần tới (next week - Monday of next week)
    if re.search(r"\btuan\s+(?:sau|toi)\b", text):
        days_ahead = (7 - base.weekday()) % 7  # Days until next Monday
        days_ahead = 7 if days_ahead == 0 else days_ahead  # If today is Monday, go to next Monday
        dt = (base + timedelta(days=days_ahead)).replace(hour=base.hour, minute=base.minute)
        text = re.sub(r"\btuan\s+(?:sau|toi)\b", "", text).strip()
        return dt, text
    # tháng sau / tháng tới (next month - 1st day of next month)
    if re.search(r"\bthang\s+(?:sau|toi)\b", text):
        # Approximate: add 30 days
        dt = (base + timedelta(days=30)).replace(hour=base.hour, minute=base.minute)
        text = re.sub(r"\bthang\s+(?:sau|toi)\b", "", text).strip()
        return dt, text
    return None, s_norm


def _parse_duration(base: datetime, s_norm: str) -> tuple[Optional[datetime], str]:
    """Parse phrases like 'trong 2 tuần', 'sau 3 ngày', '5 ngày nữa', '30 phút nữa'.
    Returns (dt, remaining_text). dt uses base date/time for time-of-day unless overridden later.
    """
    text = s_norm
    # trong/sau X đơn vị (add "thang" for month)
    m = re.search(r"\b(trong|sau)\s*(\d{1,3})\s*(phut|gio|ngay|tuan|thang)\b", text)
    if m:
        val = int(m.group(2))
        unit = m.group(3)
        delta = {
            'phut': timedelta(minutes=val),
            'gio': timedelta(hours=val),
            'ngay': timedelta(days=val),
            'tuan': timedelta(weeks=val),
            'thang': timedelta(days=val*30),  # Approximate: 1 month = 30 days
        }[unit]
        dt = base + delta
        text = text.replace(m.group(0), '').strip()
        return dt, text
    # X đơn vị nữa
    m = re.search(r"\b(\d{1,3})\s*(phut|gio|ngay|tuan|thang)\s*nua\b", text)
    if m:
        val = int(m.group(1))
        unit = m.group(2)
        delta = {
            'phut': timedelta(minutes=val),
            'gio': timedelta(hours=val),
            'ngay': timedelta(days=val),
            'tuan': timedelta(weeks=val),
            'thang': timedelta(days=val*30),  # Approximate: 1 month = 30 days
        }[unit]
        dt = base + delta
        text = text.replace(m.group(0), '').strip()
        return dt, text
    return None, s_norm


def _parse_timezone(s_norm: str) -> tuple[Optional[timezone], str]:
    """Parse timezone hints like 'UTC+7', 'GMT+07:00', 'múi giờ +07:00', 'múi giờ UTC+7'.
    Returns (tzinfo or None, remaining_text).
    """
    text = s_norm
    # múi giờ ...
    m = re.search(r"mui\s*gio\s*(?:utc|gmt)?\s*([+\-]?\d{1,2})(?::?(\d{2}))?", text)
    if not m:
        # UTC/GMT prefix
        m = re.search(r"\b(?:utc|gmt)\s*([+\-]?\d{1,2})(?::?(\d{2}))?\b", text)
    if m:
        hours = int(m.group(1))
        minutes = int(m.group(2) or 0)
        offset = timedelta(hours=hours, minutes=minutes if hours >= 0 else -minutes)
        tz = timezone(offset)
        text = text.replace(m.group(0), '').strip()
        return tz, text
    return None, s_norm


def _parse_common_day(base: datetime, s_raw: str, s_norm: str) -> tuple[datetime, str, Optional[timezone]]:
    """Extract timezone and day (explicit date, duration, relative words). Returns (day_dt, rest_norm, tzinfo)."""
    tzinfo, _ = _parse_timezone(s_norm)
    # 1) Giờ/phút tường minh (not used here)
    # 2) Ngày tường minh
    date_dt, s_norm2 = _parse_explicit_date(base, s_norm)
    # 3) Khoảng thời lượng tương đối
    dur_dt, s_norm3 = _parse_duration(base, s_norm2)
    # 4) Từ khóa tương đối
    rel_dt, rest_norm = _parse_relative_words(base, s_norm3)

    if date_dt:
        day_dt = date_dt
    elif dur_dt:
        day_dt = dur_dt
    elif rel_dt:
        day_dt = rel_dt
    else:
        day_dt = base
    
    return day_dt, rest_norm, tzinfo

def parse_vietnamese_time_range(time_str: str | None, *, relative_base: Optional[datetime] = None) -> tuple[Optional[datetime], Optional[datetime]]:
    """
    Parse time expressions possibly containing a range (từ X đến Y, X-Y). Returns (start_dt, end_dt).
    If no range present, end_dt is None.
    """
    if not time_str:
        return None, None
    base = relative_base or datetime.now()
    s_raw = time_str.strip()
    s_norm = _vn_norm(s_raw)

    day_dt, rest_norm, tzinfo = _parse_common_day(base, s_raw, s_norm)

    # Detect general period flags from the ORIGINAL string (before relative words removed)
    # This ensures "6h chiều mai" detects "chiều" flag correctly
    flags = _has_period_flags(s_norm)

    # Split range using common separators
    # Patterns: "tu 10h den 12h", "10:00 den 11:30", "10h-12h", "10h – 12h"
    parts = re.split(r"\bden\b|\-|\u2013|\u2014|\u2015|\u2212", rest_norm)
    parts = [p.strip() for p in parts if p.strip()]
    start_h = start_m = end_h = end_m = None

    def parse_hhmm(segment: str) -> tuple[Optional[int], Optional[int]]:
        hh, mm, _ = _parse_explicit_time(segment)
        return hh, mm

    if len(parts) >= 2:
        # Handle optional leading 'tu' token
        parts[0] = re.sub(r"\btu\b", "", parts[0]).strip()
        sh, sm = parse_hhmm(parts[0])
        eh, em = parse_hhmm(parts[1])
        start_h, start_m = sh, sm
        end_h, end_m = eh, em
    else:
        # Single time expression - use rest_norm (after relative words removed)
        sh, sm, _rest = _parse_explicit_time(rest_norm)
        start_h, start_m = sh, sm

    # If no explicit time found, check if day_dt already has the time set
    # (e.g., from "đêm nay" = 22:00 or "tối mai" = 20:00)
    # BUT: Only use day_dt time if rest_norm has NO time patterns
    # (e.g., "tối mai" alone is OK, but "6h tối mai" should use 6h + tối flag)
    if start_h is None and day_dt != base and not re.search(r"\d{1,2}\s*(?:h|gio|:|giờ)", rest_norm):
        # day_dt was set by relative words with specific time, use it directly
        return day_dt, None
    
    # If no explicit time found, use default mapping by period
    default_hour = None
    if flags.get('sang'):
        default_hour = 8
    elif flags.get('chieu'):
        default_hour = 15
    elif flags.get('toi'):
        default_hour = 20
    elif flags.get('trua'):
        default_hour = 12

    # Build datetimes
    def build_dt(hh: Optional[int], mm: Optional[int]) -> Optional[datetime]:
        if hh is None:
            if default_hour is None:
                return None
            hh2, mm2 = default_hour, 0
        else:
            hh2, mm2 = hh, (mm or 0)
        hh2 = _adjust_hour_by_period(hh2, flags)
        dt = day_dt.replace(hour=hh2, minute=mm2, second=0, microsecond=0)
        if tzinfo is not None:
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=tzinfo)
            else:
                try:
                    dt = dt.astimezone(tzinfo)
                except Exception:
                    pass
        return dt

    start_dt = build_dt(start_h, start_m)
    end_dt = build_dt(end_h, end_m) if end_h is not None else None
    # Ensure end after start if both present
    if start_dt and end_dt and end_dt <= start_dt:
        # If end <= start, assume same day but later hour ambiguity; keep as-is for now.
        pass
    return start_dt, end_dt

def parse_vietnamese_time(time_str: str | None, *, relative_base: Optional[datetime] = None) -> Optional[datetime]:
    """
    Phân tích chuỗi thời gian tiếng Việt và trả về datetime.
    Ưu tiên quy tắc thủ công cho định dạng phổ biến; fallback: None nếu không hiểu.
    """
    if not time_str:
        return None
    base = relative_base or datetime.now()
    s_raw = time_str.strip().lower()
    s_norm = _vn_norm(s_raw)

    # Use the range parser and return only the start time for compatibility
    start_dt, _ = parse_vietnamese_time_range(time_str, relative_base=relative_base)
    # If still None, fallback to 09:00 of base date
    if start_dt is None:
        base = relative_base or datetime.now()
        return base.replace(hour=9, minute=0, second=0, microsecond=0)
    return start_dt
