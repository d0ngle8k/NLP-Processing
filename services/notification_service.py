from __future__ import annotations
import threading
import time
from datetime import datetime, timedelta
from tkinter import messagebox
import platform

try:
    # Windows-specific sound support
    import winsound  # type: ignore
except Exception:
    winsound = None


def check_reminders_loop(root_window, db_manager):
    """
    Vòng lặp chạy nền để kiểm tra và hiển thị nhắc nhở (thread-safe).
    
    Logic thông báo kép:
    1. Nếu sự kiện có reminder_minutes > 0 và status='pending':
       - Khi now >= (start_time - reminder_minutes): popup "sắp diễn ra", chuyển status='reminded'.
    2. Khi now >= start_time và status in ('pending', 'reminded'):
       - Popup "đã đến giờ", chuyển status='notified'.
    
    Kết quả:
    - Sự kiện có "nhắc trước": 2 popup (trước X phút + đúng giờ).
    - Sự kiện không có "nhắc trước": 1 popup (đúng giờ).
    """
    while True:
        try:
            now = datetime.now()
            # Normalize to seconds precision to avoid microsecond string-compare issues in SQLite
            now_iso = now.replace(microsecond=0).isoformat()
            events = db_manager.get_pending_reminders(now_iso)
            
            for ev in events:
                try:
                    start_time = datetime.fromisoformat(ev['start_time'])
                except Exception:
                    continue
                
                # Align 'now' timezone with event start timezone if present
                local_now = now
                if start_time.tzinfo is not None and now.tzinfo is None:
                    try:
                        local_now = datetime.now(start_time.tzinfo)
                    except Exception:
                        local_now = now
                
                status = ev.get('status', 'pending')
                rem_min = int(ev.get('reminder_minutes') or 0)
                
                # Điều kiện 1: Thông báo "nhắc trước" (nếu có reminder_minutes > 0 và status='pending')
                if status == 'pending' and rem_min > 0:
                    reminder_time = start_time - timedelta(minutes=rem_min)
                    if local_now >= reminder_time:
                        # Popup "sắp diễn ra" (trước X phút)
                        root_window.after(0, show_popup_pre_reminder, ev['event_name'], ev['start_time'], rem_min)
                        db_manager.update_event_status(ev['id'], 'reminded')
                        continue  # Chờ đến lần check tiếp theo để popup "đúng giờ"
                
                # Điều kiện 2: Thông báo "đúng giờ" (cho cả 'pending' và 'reminded')
                if status in ('pending', 'reminded'):
                    if local_now >= start_time:
                        # Popup "đã đến giờ"
                        root_window.after(0, show_popup_on_time, ev['event_name'], ev['start_time'])
                        db_manager.update_event_status(ev['id'], 'notified')
                        
        except Exception as e:
            print(f"Lỗi trong luồng nhắc nhở: {e}")
        time.sleep(60)


def _play_notification_sound():
    """Play a notification sound (Windows if available), otherwise try Tk bell."""
    try:
        if winsound and platform.system() == 'Windows':
            # Play system exclamation sound
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        else:
            # Fallback: simple bell via Tk (if any root exists)
            try:
                import tkinter as tk
                root = tk._get_default_root()
                if root is not None:
                    root.bell()
            except Exception:
                pass
    except Exception:
        pass


def show_popup_pre_reminder(event_name, event_time, reminder_minutes):
    """Popup thông báo 'nhắc trước' (trước X phút)."""
    _play_notification_sound()
    time_str = event_time[:16] if len(event_time) >= 16 else event_time
    messagebox.showinfo(
        "Nhắc nhở Sự kiện", 
        f"Sự kiện sắp diễn ra:\n\n{event_name}\nLúc: {time_str}\n\n(Nhắc trước {reminder_minutes} phút)"
    )


def show_popup_on_time(event_name, event_time):
    """Popup thông báo 'đúng giờ' (đã đến giờ sự kiện)."""
    _play_notification_sound()
    time_str = event_time[:16] if len(event_time) >= 16 else event_time
    messagebox.showinfo(
        "Thông báo Sự kiện", 
        f"Sự kiện đã đến giờ:\n\n{event_name}\nLúc: {time_str}"
    )


def start_notification_service(root_window, db_manager):
    t = threading.Thread(target=check_reminders_loop, args=(root_window, db_manager), daemon=True)
    t.start()
