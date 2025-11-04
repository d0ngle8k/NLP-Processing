from __future__ import annotations
import sys
from pathlib import Path

# --- PyInstaller _MEIPASS Hack cho underthesea ---
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    Path.home = lambda: Path(sys._MEIPASS)
# -------------------------------------------------

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import Calendar
from datetime import date

from core_nlp.pipeline import NLPPipeline
from database.db_manager import DatabaseManager
from services.notification_service import start_notification_service
from services.export_service import export_to_json, export_to_ics
from services.import_service import import_from_json, import_from_ics


class Application(tk.Tk):
    def __init__(self, database: DatabaseManager, nlp_pipeline: NLPPipeline):
        super().__init__()
        self.title("Trợ lý Lịch trình Cá nhân")
        self.geometry("960x720")

        self.db_manager = database
        self.nlp_pipeline = nlp_pipeline

        self._build_ui()
        self._load_today()

    def _build_ui(self):
        # Frames
        input_frame = ttk.Frame(self, padding=10)
        input_frame.pack(fill='x', side='top')

        # Search frame (below input)
        search_frame = ttk.Frame(self, padding=(10, 0))
        search_frame.pack(fill='x', side='top')
        self.search_mode = False

        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill='both', expand=True)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)

        control_frame = ttk.Frame(self, padding=10)
        control_frame.pack(fill='x', side='bottom')
        self.control_frame = control_frame

        # Input
        ttk.Label(input_frame, text="Nhập lệnh:").pack(side='left', padx=(0, 8))
        self.nlp_entry = ttk.Entry(input_frame)
        self.nlp_entry.pack(side='left', fill='x', expand=True)
        ttk.Button(input_frame, text="Thêm sự kiện", command=self.handle_add_event).pack(side='left', padx=(8, 0))

        # Search controls
        ttk.Label(search_frame, text="Tìm:").pack(side='left', padx=(0, 8))
        self.search_mode_var = tk.StringVar(value='Nội dung')
        self.search_field = ttk.Combobox(
            search_frame,
            textvariable=self.search_mode_var,
            state='readonly',
            width=12,
            values=['ID', 'Nội dung', 'Địa điểm']
        )
        self.search_field.pack(side='left')
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(side='left', padx=6, fill='x', expand=True)
        ttk.Button(search_frame, text="Tìm", command=self.handle_search).pack(side='left', padx=4)
        ttk.Button(search_frame, text="Xóa lọc", command=self.handle_clear_search).pack(side='left', padx=4)

        # Calendar
        self.calendar = Calendar(main_frame, selectmode='day', date_pattern='y-mm-dd')
        self.calendar.grid(row=0, column=0, sticky='ns', padx=(0, 10))
        self.calendar.bind("<<CalendarSelected>>", self.handle_date_select)

        # Treeview
        tree_wrap = ttk.Frame(main_frame)
        tree_wrap.grid(row=0, column=1, sticky='nsew')
        cols = ('id', 'event_name', 'time', 'location')
        self.tree = ttk.Treeview(tree_wrap, columns=cols, show='headings')
        self.tree.heading('id', text='ID')
        self.tree.heading('event_name', text='Sự kiện')
        self.tree.heading('time', text='Thời gian')
        self.tree.heading('location', text='Địa điểm')
        self.tree.column('id', width=50, stretch=False)
        self.tree.column('event_name', width=360)
        self.tree.column('time', width=120)
        self.tree.column('location', width=180)
        self.tree.pack(fill='both', expand=True)

        # Controls
        ttk.Button(control_frame, text="Sửa", command=self.handle_edit_start).pack(side='left', padx=4)
        ttk.Button(control_frame, text="Xóa", command=self.handle_delete_event).pack(side='left', padx=4)
        ttk.Button(control_frame, text="Nhập JSON", command=self.handle_import_json).pack(side='right', padx=4)
        ttk.Button(control_frame, text="Nhập ICS", command=self.handle_import_ics).pack(side='right', padx=4)
        ttk.Button(control_frame, text="Xuất JSON", command=self.handle_export_json).pack(side='right', padx=4)
        ttk.Button(control_frame, text="Xuất ICS", command=self.handle_export_ics).pack(side='right', padx=4)

        # Inline edit frame (hidden by default)
        self.edit_frame = ttk.LabelFrame(self, text="Chỉnh sửa sự kiện", padding=10)
        # Widgets inside edit frame
        self.edit_vars = {
            'id': tk.StringVar(),
            'event_name': tk.StringVar(),
            'date': tk.StringVar(),
            'time': tk.StringVar(),
            'location': tk.StringVar(),
            'reminder': tk.StringVar(value='0'),
        }
        # Layout
        row = 0
        ttk.Label(self.edit_frame, text="ID:").grid(row=row, column=0, sticky='e')
        ttk.Label(self.edit_frame, textvariable=self.edit_vars['id']).grid(row=row, column=1, sticky='w')
        row += 1
        ttk.Label(self.edit_frame, text="Sự kiện:").grid(row=row, column=0, sticky='e')
        ttk.Entry(self.edit_frame, textvariable=self.edit_vars['event_name'], width=40).grid(row=row, column=1, sticky='w')
        row += 1
        ttk.Label(self.edit_frame, text="Ngày (YYYY-MM-DD):").grid(row=row, column=0, sticky='e')
        ttk.Entry(self.edit_frame, textvariable=self.edit_vars['date'], width=16).grid(row=row, column=1, sticky='w')
        row += 1
        ttk.Label(self.edit_frame, text="Giờ (HH:MM):").grid(row=row, column=0, sticky='e')
        ttk.Entry(self.edit_frame, textvariable=self.edit_vars['time'], width=10).grid(row=row, column=1, sticky='w')
        row += 1
        ttk.Label(self.edit_frame, text="Địa điểm:").grid(row=row, column=0, sticky='e')
        ttk.Entry(self.edit_frame, textvariable=self.edit_vars['location'], width=30).grid(row=row, column=1, sticky='w')
        row += 1
        ttk.Label(self.edit_frame, text="Nhắc (phút):").grid(row=row, column=0, sticky='e')
        ttk.Entry(self.edit_frame, textvariable=self.edit_vars['reminder'], width=8).grid(row=row, column=1, sticky='w')
        row += 1
        btns = ttk.Frame(self.edit_frame)
        btns.grid(row=row, column=0, columnspan=2, pady=(8, 0))
        ttk.Button(btns, text="Lưu", command=self.handle_edit_save).pack(side='left', padx=4)
        ttk.Button(btns, text="Hủy", command=self.handle_edit_cancel).pack(side='left', padx=4)

    def _not_implemented(self):
        messagebox.showinfo("Thông báo", "Chức năng đang được phát triển.")

    def _load_today(self):
        self.refresh_for_date(self.calendar.selection_get())

    def handle_add_event(self):
        text = self.nlp_entry.get().strip()
        if not text:
            messagebox.showwarning("Đầu vào trống", "Vui lòng nhập một lệnh.")
            return
        try:
            event_dict = self.nlp_pipeline.process(text)
            if not event_dict.get('event') or not event_dict.get('start_time'):
                messagebox.showerror("Phân tích thất bại", "Không thể trích xuất tên sự kiện hoặc thời gian.")
                return
            self.db_manager.add_event(event_dict)
            self.nlp_entry.delete(0, 'end')
            self.refresh_for_date(self.calendar.selection_get())
            messagebox.showinfo("Thành công", "Đã thêm sự kiện.")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Đã xảy ra lỗi: {e}")

    def handle_date_select(self, _evt=None):
        # Nếu đang ở chế độ tìm kiếm, bỏ qua refresh theo ngày để không mất kết quả
        if not getattr(self, 'search_mode', False):
            self.refresh_for_date(self.calendar.selection_get())

    def refresh_for_date(self, date_obj: date):
        events = self.db_manager.get_events_by_date(date_obj)
        for item in self.tree.get_children():
            self.tree.delete(item)
        for ev in events:
            time_str = (ev['start_time'] or '')[11:16] if ev.get('start_time') else ''
            self.tree.insert('', 'end', values=(ev['id'], ev['event_name'], time_str, ev.get('location') or ''))

    def _render_events(self, events):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for ev in events:
            time_str = (ev.get('start_time') or '')[11:16] if ev.get('start_time') else ''
            self.tree.insert('', 'end', values=(ev.get('id'), ev.get('event_name'), time_str, ev.get('location') or ''))

    def handle_search(self):
        mode = self.search_mode_var.get()
        query = self.search_entry.get().strip()
        try:
            if mode == 'ID':
                if not query.isdigit():
                    messagebox.showwarning("Tìm kiếm", "Vui lòng nhập ID là số.")
                    return
                events = self.db_manager.search_events_by_id(int(query))
            elif mode == 'Nội dung':
                if not query:
                    messagebox.showwarning("Tìm kiếm", "Vui lòng nhập từ khóa nội dung.")
                    return
                events = self.db_manager.search_events_by_name(query)
            else:  # Địa điểm
                if not query:
                    messagebox.showwarning("Tìm kiếm", "Vui lòng nhập từ khóa địa điểm.")
                    return
                events = self.db_manager.search_events_by_location(query)
            self._render_events(events)
            self.search_mode = True
        except Exception as e:
            messagebox.showerror("Lỗi tìm kiếm", f"Không thể tìm kiếm: {e}")

    def handle_clear_search(self):
        self.search_entry.delete(0, 'end')
        self.search_mode = False
        self.refresh_for_date(self.calendar.selection_get())

    def handle_delete_event(self):
        sel = self.tree.focus()
        if not sel:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn một sự kiện.")
            return
        ev_id = self.tree.item(sel)['values'][0]
        if messagebox.askyesno("Xác nhận", "Xóa sự kiện đã chọn?"):
            self.db_manager.delete_event(int(ev_id))
            self.refresh_for_date(self.calendar.selection_get())

    def handle_export_json(self):
        try:
            export_to_json(self.db_manager)
            messagebox.showinfo("Xuất JSON", "Đã xuất file schedule_export.json")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Xuất JSON thất bại: {e}")

    def handle_export_ics(self):
        try:
            export_to_ics(self.db_manager)
            messagebox.showinfo("Xuất ICS", "Đã xuất file schedule_export.ics")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Xuất ICS thất bại: {e}")

    # --- Import Handlers ---
    def handle_import_json(self):
        path = filedialog.askopenfilename(title="Chọn file JSON", filetypes=[("JSON", "*.json")])
        if not path:
            return
        try:
            count = import_from_json(self.db_manager, path)
            self.refresh_for_date(self.calendar.selection_get())
            messagebox.showinfo("Nhập JSON", f"Đã nhập {count} sự kiện từ JSON.")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Nhập JSON thất bại: {e}")

    def handle_import_ics(self):
        path = filedialog.askopenfilename(title="Chọn file ICS", filetypes=[("iCalendar", "*.ics")])
        if not path:
            return
        try:
            count = import_from_ics(self.db_manager, path)
            self.refresh_for_date(self.calendar.selection_get())
            messagebox.showinfo("Nhập ICS", f"Đã nhập {count} sự kiện từ ICS.")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Nhập ICS thất bại: {e}")

    # --- Inline Edit ---
    def handle_edit_start(self):
        sel = self.tree.focus()
        if not sel:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn một sự kiện để sửa.")
            return
        ev_id = int(self.tree.item(sel)['values'][0])
        ev = self.db_manager.get_event_by_id(ev_id)
        if not ev:
            messagebox.showerror("Lỗi", "Không tìm thấy sự kiện.")
            return
        st = ev.get('start_time') or ''
        date_str = st[:10] if len(st) >= 10 else ''
        time_str = st[11:16] if len(st) >= 16 else ''
        self.edit_vars['id'].set(str(ev['id']))
        self.edit_vars['event_name'].set(ev.get('event_name') or '')
        self.edit_vars['date'].set(date_str)
        self.edit_vars['time'].set(time_str)
        self.edit_vars['location'].set(ev.get('location') or '')
        self.edit_vars['reminder'].set(str(ev.get('reminder_minutes') or 0))
        # Show frame just above control buttons
        self.edit_frame.pack(fill='x', side='bottom', padx=10, pady=(0, 10))

    def handle_edit_cancel(self):
        self.edit_frame.pack_forget()

    def handle_edit_save(self):
        try:
            ev_id = int(self.edit_vars['id'].get())
            event_name = self.edit_vars['event_name'].get().strip()
            date_str = self.edit_vars['date'].get().strip()
            time_str = self.edit_vars['time'].get().strip()
            location = self.edit_vars['location'].get().strip() or None
            reminder = int(self.edit_vars['reminder'].get() or 0)
            if not (event_name and date_str and time_str):
                messagebox.showwarning("Thiếu dữ liệu", "Vui lòng điền đủ Sự kiện, Ngày và Giờ.")
                return
            # Rebuild ISO start time, preserve timezone if any from existing
            old = self.db_manager.get_event_by_id(ev_id)
            tz_suffix = ''
            if old and isinstance(old.get('start_time'), str):
                st = old['start_time']
                # Keep timezone suffix if present
                if len(st) > 19 and (st[19] in ['+', '-'] or st.endswith('Z')):
                    tz_suffix = st[19:]
            new_iso = f"{date_str}T{time_str}:00{tz_suffix}"
            payload = {
                'event': event_name,
                'start_time': new_iso,
                'end_time': old.get('end_time') if old else None,
                'location': location,
                'reminder_minutes': reminder,
            }
            self.db_manager.update_event(ev_id, payload)
            self.refresh_for_date(self.calendar.selection_get())
            self.handle_edit_cancel()
            messagebox.showinfo("Đã lưu", "Cập nhật sự kiện thành công.")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu chỉnh sửa: {e}")


if __name__ == '__main__':
    db = DatabaseManager()
    nlp = NLPPipeline()
    app = Application(db, nlp)
    # Dịch vụ nhắc nhở nền
    start_notification_service(app, db)
    app.mainloop()
