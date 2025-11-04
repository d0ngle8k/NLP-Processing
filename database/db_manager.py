from __future__ import annotations
import os
import sys
import sqlite3
from datetime import date
from typing import List, Dict, Any

DB_FILE = "events.db"

def _writable_base_dir() -> str:
    """Return a writable base dir for DB when running normally or as a frozen exe.
    - In dev: use the module directory (database/)
    - In frozen exe: use a 'database' folder next to the executable
    """
    if getattr(sys, 'frozen', False):  # PyInstaller onefile
        exe_dir = os.path.dirname(sys.executable)
        base = os.path.join(exe_dir, 'database')
    else:
        base = os.path.dirname(__file__)
    os.makedirs(base, exist_ok=True)
    return base


def _schema_file_path() -> str:
    """Locate schema.sql both in dev and in PyInstaller runtime.
    In frozen mode, data files are extracted under sys._MEIPASS.
    """
    # Prefer packaged resource under _MEIPASS when frozen
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        candidate = os.path.join(sys._MEIPASS, 'database', 'schema.sql')
        if os.path.exists(candidate):
            return candidate
    # Fallback to local file next to this module
    return os.path.join(os.path.dirname(__file__), 'schema.sql')


DB_PATH = os.path.join(_writable_base_dir(), DB_FILE)
SCHEMA_PATH = _schema_file_path()


class DatabaseManager:
    def __init__(self, db_path: str = DB_PATH) -> None:
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._create_table()

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _create_table(self) -> None:
        with self._conn() as conn:
            with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
                conn.executescript(f.read())

    # CRUD
    def add_event(self, event_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add a new event to the database.
        
        Returns:
            Dict with 'success': bool and optional 'error': str or 'duplicates': List
        """
        # Check for time conflict
        start_time = event_dict.get('start_time')
        if start_time:
            duplicates = self.check_duplicate_time(start_time)
            if duplicates:
                return {
                    'success': False,
                    'error': 'duplicate_time',
                    'duplicates': duplicates
                }
        
        sql = (
            "INSERT INTO events (event_name, start_time, end_time, location, reminder_minutes) "
            "VALUES (:event, :start_time, :end_time, :location, :reminder_minutes)"
        )
        try:
            with self._conn() as conn:
                conn.execute(sql, event_dict)
            return {'success': True}
        except sqlite3.IntegrityError as e:
            return {
                'success': False,
                'error': 'integrity_error',
                'message': str(e)
            }

    def update_event(self, event_id: int, event_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing event.
        
        Returns:
            Dict with 'success': bool and optional 'error': str or 'duplicates': List
        """
        # Check for time conflict (excluding current event)
        start_time = event_dict.get('start_time')
        if start_time:
            duplicates = self.check_duplicate_time(start_time, exclude_id=event_id)
            if duplicates:
                return {
                    'success': False,
                    'error': 'duplicate_time',
                    'duplicates': duplicates
                }
        
        sql = (
            "UPDATE events SET event_name=:event, start_time=:start_time, end_time=:end_time, "
            "location=:location, reminder_minutes=:reminder_minutes WHERE id=:id"
        )
        data = dict(event_dict)
        data['id'] = event_id
        try:
            with self._conn() as conn:
                conn.execute(sql, data)
            return {'success': True}
        except sqlite3.IntegrityError as e:
            return {
                'success': False,
                'error': 'integrity_error',
                'message': str(e)
            }

    def delete_event(self, event_id: int) -> None:
        with self._conn() as conn:
            conn.execute("DELETE FROM events WHERE id=?", (event_id,))
            # Check if all events are deleted, if so reset the AUTOINCREMENT counter
            cur = conn.execute("SELECT COUNT(*) FROM events")
            count = cur.fetchone()[0]
            if count == 0:
                # Reset the sqlite_sequence table to restart ID from 1
                conn.execute("DELETE FROM sqlite_sequence WHERE name='events'")

    def get_events_by_date(self, date_obj: date) -> List[Dict[str, Any]]:
        date_str = date_obj.strftime('%Y-%m-%d')
        sql = "SELECT * FROM events WHERE DATE(start_time)=? ORDER BY start_time"
        with self._conn() as conn:
            cur = conn.execute(sql, (date_str,))
            return [dict(r) for r in cur.fetchall()]

    def get_all_events(self) -> List[Dict[str, Any]]:
        with self._conn() as conn:
            cur = conn.execute("SELECT * FROM events ORDER BY start_time")
            return [dict(r) for r in cur.fetchall()]

    def get_event_by_id(self, event_id: int) -> Dict[str, Any] | None:
        with self._conn() as conn:
            cur = conn.execute("SELECT * FROM events WHERE id=?", (event_id,))
            row = cur.fetchone()
            return dict(row) if row else None

    def get_pending_reminders(self, now_iso: str) -> List[Dict[str, Any]]:
        sql = (
            "SELECT * FROM events WHERE start_time > ? AND status='pending' AND reminder_minutes > 0 "
            "ORDER BY start_time ASC"
        )
        with self._conn() as conn:
            cur = conn.execute(sql, (now_iso,))
            return [dict(r) for r in cur.fetchall()]

    def update_event_status(self, event_id: int, new_status: str) -> None:
        with self._conn() as conn:
            conn.execute("UPDATE events SET status=? WHERE id=?", (new_status, event_id))

    # --- Search helpers ---
    def search_events_by_id(self, event_id: int) -> List[Dict[str, Any]]:
        ev = self.get_event_by_id(event_id)
        return [ev] if ev else []

    def search_events_by_name(self, keyword: str) -> List[Dict[str, Any]]:
        kw = (keyword or '').strip().lower()
        if not kw:
            return []
        like = f"%{kw}%"
        sql = "SELECT * FROM events WHERE LOWER(event_name) LIKE ? ORDER BY start_time"
        with self._conn() as conn:
            cur = conn.execute(sql, (like,))
            return [dict(r) for r in cur.fetchall()]

    def search_events_by_location(self, keyword: str) -> List[Dict[str, Any]]:
        kw = (keyword or '').strip().lower()
        if not kw:
            return []
        like = f"%{kw}%"
        sql = "SELECT * FROM events WHERE location IS NOT NULL AND LOWER(location) LIKE ? ORDER BY start_time"
        with self._conn() as conn:
            cur = conn.execute(sql, (like,))
            return [dict(r) for r in cur.fetchall()]

    # --- Duplicate checking helpers ---
    def check_duplicate_time(self, start_time_iso: str, exclude_id: int = None) -> List[Dict[str, Any]]:
        """
        Check if there's already an event at the exact same time (date + hour + minute).
        Used to prevent scheduling conflicts.
        
        Args:
            start_time_iso: ISO 8601 datetime string (e.g., "2025-11-06T10:00:00")
            exclude_id: Optional event ID to exclude from check (for updates)
            
        Returns:
            List of conflicting events (empty if no duplicates)
        """
        # Extract date and time components (YYYY-MM-DD HH:MM)
        if not start_time_iso or len(start_time_iso) < 16:
            return []
        
        datetime_key = start_time_iso[:16]  # "2025-11-06T10:00"
        
        # Check for events with same date-time (ignoring seconds)
        sql = """
            SELECT * FROM events 
            WHERE substr(start_time, 1, 16) = ?
        """
        params = [datetime_key]
        
        if exclude_id is not None:
            sql += " AND id != ?"
            params.append(exclude_id)
        
        with self._conn() as conn:
            cur = conn.execute(sql, params)
            return [dict(r) for r in cur.fetchall()]
