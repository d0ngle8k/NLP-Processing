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


def _parse_explicit_time(s: str) -> tuple[Optional[int], Optional[int], str]:
    s = s.strip()
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

    # 0) Timezone (chỉ áp dụng nếu có chỉ định)
    tzinfo, _ = _parse_timezone(s_norm)

    # 1) Giờ/phút tường minh
    hh, mm, _ = _parse_explicit_time(s_raw)

    # 2) Ngày tường minh
    date_dt, _ = _parse_explicit_date(base, s_norm)

    # 3) Khoảng thời lượng tương đối (trong/sau X; X nữa)
    dur_dt, _ = _parse_duration(base, s_norm)

    # 4) Từ khóa tương đối (hôm nay/mai/cuối tuần/thứ d ...)
    rel_dt, rest_norm = _parse_relative_words(base, s_norm)

    # 5) Sáng/chiều/tối (đặt giờ mặc định nếu chưa có giờ)
    default_hour = None
    if re.search(r"\bsang\b", rest_norm):
        default_hour = 8
        rest_norm = re.sub(r"\bsang\b", "", rest_norm).strip()
    elif re.search(r"\bchieu\b", rest_norm):
        default_hour = 15
        rest_norm = re.sub(r"\bchieu\b", "", rest_norm).strip()
    elif re.search(r"\btoi\b", rest_norm):
        default_hour = 20
        rest_norm = re.sub(r"\btoi\b", "", rest_norm).strip()

    # Xác định ngày
    if date_dt:
        day_dt = date_dt
    elif dur_dt:
        day_dt = dur_dt
    elif rel_dt:
        day_dt = rel_dt
    else:
        # không có ngày, dùng base date
        day_dt = base

    # Xác định giờ
    if hh is not None:
        hour, minute = hh, (mm or 0)
    elif default_hour is not None:
        hour, minute = default_hour, 0
    else:
        # Nếu không có thông tin giờ, mặc định 09:00
        hour, minute = 9, 0

    result = day_dt.replace(hour=hour, minute=minute, second=0, microsecond=0)
    # Chỉ gán tzinfo nếu được chỉ định trong chuỗi
    if tzinfo is not None:
        if result.tzinfo is None:
            result = result.replace(tzinfo=tzinfo)
        else:
            # Convert to the parsed tz if different
            try:
                result = result.astimezone(tzinfo)
            except Exception:
                pass
    return result
