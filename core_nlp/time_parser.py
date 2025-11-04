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
    """Detect period hints: morning/afternoon/evening/noon/night in normalized text."""
    return {
        'sang': bool(re.search(r"\bsang\b", s_norm)),
        'trua': bool(re.search(r"\btrua\b", s_norm)),
        'chieu': bool(re.search(r"\bchieu\b", s_norm)),
        'toi': bool(re.search(r"\btoi\b", s_norm) or re.search(r"\bdem\b", s_norm)),
    }

def _adjust_hour_by_period(hh: int, flags: dict[str, bool]) -> int:
    """Convert 12-hour style to 24-hour if a PM-like period is present."""
    if hh is None:
        return hh
    # Evening/night/afternoon => PM for 1..11
    if flags.get('toi') or flags.get('chieu') or flags.get('trua'):
        if 1 <= hh <= 11:
            return hh + 12
    # Morning keeps AM
    return hh

def _parse_explicit_time(s: str) -> tuple[Optional[int], Optional[int], str]:
    s = s.strip()
    s_norm = _vn_norm(s)
    # 10 rưỡi / 10 giờ rưỡi / 10h rưỡi => HH:30
    m = re.search(r"\b(\d{1,2})\s*(?:h|gio|giờ)?\s*(?:ruoi|r\u01b0oi)\b", s_norm)
    if m:
        hh = int(m.group(1))
        mm = 30
        # remove the matched raw segment approximately by digits and 'rưỡi'
        s = re.sub(r"\b" + re.escape(m.group(1)) + r"\s*(?:h|giờ)?\s*r[ưu]ỡi\b", "", s, flags=re.IGNORECASE)
        return hh, mm, s.strip()
    # 10 giờ kém 15 => 09:45
    # Allow formats: 10h|10 giờ kém 15
    mk = re.search(r"\b(\d{1,2})\s*(?:h|gio|giờ)\s*k[eé]m\s*(\d{1,2})\b", s_norm)
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
    # 17 giờ 30 phút | 17 giờ
    m = re.search(r"\b(\d{1,2})\s*giờ(?:\s*(\d{1,2})\s*phút)?\b", s)
    if m:
        hh = int(m.group(1))
        mm = int(m.group(2) or 0)
        return hh, mm, re.sub(m.group(0), "", s, 1).strip()
    return None, None, s


def _parse_explicit_date(base: datetime, s_norm: str) -> tuple[Optional[datetime], str]:
    # ngay 6 thang 12 (normalized)
    m = re.search(r"ngay\s*(\d{1,2})\s*thang\s*(\d{1,2})", s_norm)
    if m:
        day = int(m.group(1))
        month = int(m.group(2))
        year = base.year
        try:
            dt = datetime(year, month, day, base.hour, base.minute)
        except ValueError:
            return None, s_norm
        return dt, re.sub(m.group(0), "", s_norm, 1).strip()
    return None, s_norm


def _parse_relative_words(base: datetime, s_norm: str) -> tuple[Optional[datetime], str]:
    text = s_norm
    # hom nay / ngay mai / mai
    if re.search(r"\bhom nay\b", text):
        dt = base.replace(hour=base.hour, minute=base.minute)
        text = re.sub(r"\bhom nay\b", "", text).strip()
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
    m = re.search(r"\b(?:thu|t)\s*(\d)(?:\s*tuan sau)?\b", text)
    if m:
        thu = int(m.group(1))  # 2..7 (2=Mon)
        target_wd = (thu - 2) % 7  # map: 2->0 (Mon), 7->5 (Sat)
        days_ahead = (target_wd - base.weekday()) % 7
        if 'tuan sau' in m.group(0) or days_ahead == 0:
            days_ahead += 7
        dt = (base + timedelta(days=days_ahead)).replace(hour=base.hour, minute=base.minute)
        text = text.replace(m.group(0), '').strip()
        return dt, text
    # CN (Chủ nhật) (tuần sau)?
    m = re.search(r"\bcn(?:\s*tuan sau)?\b", text)
    if m:
        target_wd = 6  # Sunday
        days_ahead = (target_wd - base.weekday()) % 7
        if 'tuan sau' in m.group(0) or days_ahead == 0:
            days_ahead += 7
        dt = (base + timedelta(days=days_ahead)).replace(hour=base.hour, minute=base.minute)
        text = text.replace(m.group(0), '').strip()
        return dt, text
    # hom kia (two days ago)
    if re.search(r"\bhom kia\b", text):
        dt = (base - timedelta(days=2)).replace(hour=base.hour, minute=base.minute)
        text = re.sub(r"\bhom kia\b", "", text).strip()
        return dt, text
    return None, s_norm


def _parse_duration(base: datetime, s_norm: str) -> tuple[Optional[datetime], str]:
    """Parse phrases like 'trong 2 tuần', 'sau 3 ngày', '5 ngày nữa', '30 phút nữa'.
    Returns (dt, remaining_text). dt uses base date/time for time-of-day unless overridden later.
    """
    text = s_norm
    # trong/sau X đơn vị
    m = re.search(r"\b(trong|sau)\s*(\d{1,3})\s*(phut|gio|ngay|tuan)\b", text)
    if m:
        val = int(m.group(2))
        unit = m.group(3)
        delta = {
            'phut': timedelta(minutes=val),
            'gio': timedelta(hours=val),
            'ngay': timedelta(days=val),
            'tuan': timedelta(weeks=val),
        }[unit]
        dt = base + delta
        text = text.replace(m.group(0), '').strip()
        return dt, text
    # X đơn vị nữa
    m = re.search(r"\b(\d{1,3})\s*(phut|gio|ngay|tuan)\s*nua\b", text)
    if m:
        val = int(m.group(1))
        unit = m.group(2)
        delta = {
            'phut': timedelta(minutes=val),
            'gio': timedelta(hours=val),
            'ngay': timedelta(days=val),
            'tuan': timedelta(weeks=val),
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

    # Detect general period flags from the entire string
    flags = _has_period_flags(rest_norm)

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
        # Single time expression
        sh, sm, _rest = _parse_explicit_time(s_raw)
        start_h, start_m = sh, sm

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
