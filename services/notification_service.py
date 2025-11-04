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
    """Vòng lặp chạy nền để kiểm tra và hiển thị nhắc nhở (thread-safe)."""
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
                rem_min = int(ev.get('reminder_minutes') or 0)
                if rem_min > 0:
                    # Align 'now' timezone with event start timezone if present
                    local_now = now
                    if start_time.tzinfo is not None and now.tzinfo is None:
                        try:
                            local_now = datetime.now(start_time.tzinfo)
                        except Exception:
                            local_now = now
                    reminder_time = start_time - timedelta(minutes=rem_min)
                    if local_now >= reminder_time:
                        # Đẩy nhiệm vụ hiển thị popup về luồng GUI chính
                        root_window.after(0, show_popup, ev['event_name'], ev['start_time'])
                        db_manager.update_event_status(ev['id'], 'notified')
        except Exception as e:
            print(f"Lỗi trong luồng nhắc nhở: {e}")
        time.sleep(60)


def show_popup(event_name, event_time):
    # Play a notification sound (Windows if available), otherwise try Tk bell
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

    messagebox.showinfo("Nhắc nhở Sự kiện", f"Sự kiện sắp diễn ra:\n\n{event_name}\nLúc: {event_time}")


def start_notification_service(root_window, db_manager):
    t = threading.Thread(target=check_reminders_loop, args=(root_window, db_manager), daemon=True)
    t.start()
