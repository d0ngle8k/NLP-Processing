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

# Import SoundManager
try:
    from services.sound_manager import SoundManager
    SOUND_MANAGER_AVAILABLE = True
except ImportError:
    SOUND_MANAGER_AVAILABLE = False


# Global sound manager instance
_sound_manager: SoundManager = None


def init_sound_manager(base_dir: str = '.') -> SoundManager:
    """Initialize global sound manager"""
    global _sound_manager
    if _sound_manager is None:
        _sound_manager = SoundManager(base_dir)
    return _sound_manager


def get_sound_manager() -> SoundManager:
    """Get global sound manager instance"""
    global _sound_manager
    if _sound_manager is None:
        _sound_manager = SoundManager('.')
    return _sound_manager


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
            # Lấy tất cả sự kiện còn ở trạng thái cần xử lý (pending/reminded)
            events = db_manager.get_pending_reminders()
            
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
                
                # Ưu tiên điều kiện 1: "đúng giờ" (khi đã tới giờ hoặc trễ) cho cả 'pending' và 'reminded'
                if status in ('pending', 'reminded') and local_now >= start_time:
                    root_window.after(0, show_popup_on_time, ev['event_name'], ev['start_time'])
                    db_manager.update_event_status(ev['id'], 'notified')
                    continue

                # Điều kiện 2: "nhắc trước" (chỉ khi còn pending và có cấu hình nhắc)
                if status == 'pending' and rem_min > 0:
                    reminder_time = start_time - timedelta(minutes=rem_min)
                    if local_now >= reminder_time and local_now < start_time:
                        root_window.after(0, show_popup_pre_reminder, ev['event_name'], ev['start_time'], rem_min)
                        db_manager.update_event_status(ev['id'], 'reminded')
                        
        except Exception as e:
            print(f"Lỗi trong luồng nhắc nhở: {e}")
        time.sleep(60)


def _play_notification_sound():
    """Play notification sound using SoundManager or fallback"""
    try:
        # Try using SoundManager first
        if SOUND_MANAGER_AVAILABLE:
            sound_mgr = get_sound_manager()
            if sound_mgr.play_notification_sound():
                return  # Success
        
        # Fallback to old method
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
    except Exception as e:
        print(f"Sound playback error: {e}")


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
