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
        self.title("Trợ lý Lịch trình Cá nhân made by d0ngle8k")
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
        ttk.Label(input_frame, text="Lập lịch:").pack(side='left', padx=(0, 8))
        self.nlp_entry = ttk.Entry(input_frame)
        self.nlp_entry.pack(side='left', fill='x', expand=True)
        # Limit NLP input to 300 characters
        self.nlp_entry.config(validate='key', validatecommand=(self.register(lambda s: len(s) <= 300), '%P'))
        ttk.Button(input_frame, text="Thêm sự kiện", command=self.handle_add_event).pack(side='left', padx=(8, 0))
        ttk.Button(input_frame, text="Sửa", command=self.handle_edit_start).pack(side='left', padx=(8, 0))
        ttk.Button(input_frame, text="Xóa", command=self.handle_delete_event).pack(side='left', padx=(8, 0))

        # Search controls
        ttk.Label(search_frame, text="Tìm:").pack(side='left', padx=(0, 8))
        self.search_mode_var = tk.StringVar(value='Nội dung')
        self.search_field = ttk.Combobox(
            search_frame,
            textvariable=self.search_mode_var,
            state='readonly',
            width=14,
            values=['ID', 'Nội dung', 'Địa điểm', 'Lịch đã đặt']
        )
        self.search_field.pack(side='left')
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(side='left', padx=6, fill='x', expand=True)
        # Limit search input to 100 characters
        self.search_entry.config(validate='key', validatecommand=(self.register(lambda s: len(s) <= 100), '%P'))
        ttk.Button(search_frame, text="Tìm", command=self.handle_search).pack(side='left', padx=4)
        ttk.Button(search_frame, text="Xóa lọc", command=self.handle_clear_search).pack(side='left', padx=4)

        # Calendar
        self.calendar = Calendar(main_frame, selectmode='day', date_pattern='y-mm-dd')
        self.calendar.grid(row=0, column=0, sticky='ns', padx=(0, 10))
        self.calendar.bind("<<CalendarSelected>>", self.handle_date_select)

        # Treeview with scrollbars
        tree_wrap = ttk.Frame(main_frame)
        tree_wrap.grid(row=0, column=1, sticky='nsew')
        
        # Configure grid weights for proper resizing
        tree_wrap.columnconfigure(0, weight=1)
        tree_wrap.rowconfigure(0, weight=1)
        
        # Create Treeview
        cols = ('id', 'event_name', 'time', 'remind', 'location')
        self.tree = ttk.Treeview(tree_wrap, columns=cols, show='headings')
        
        # Center headings
        self.tree.heading('id', text='ID', anchor='center')
        self.tree.heading('event_name', text='Sự kiện', anchor='center')
        self.tree.heading('time', text='Thời gian', anchor='center')
        self.tree.heading('remind', text='Nhắc tôi', anchor='center')
        self.tree.heading('location', text='Địa điểm', anchor='center')
        
        # Center column contents
        self.tree.column('id', width=50, stretch=False, anchor='center')
        self.tree.column('event_name', width=330, anchor='center')
        self.tree.column('time', width=110, anchor='center')
        self.tree.column('remind', width=80, anchor='center')
        self.tree.column('location', width=180, anchor='center')
        
        # Vertical scrollbar
        vsb = ttk.Scrollbar(tree_wrap, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        
        # Horizontal scrollbar (optional, useful if content is wide)
        hsb = ttk.Scrollbar(tree_wrap, orient='horizontal', command=self.tree.xview)
        self.tree.configure(xscrollcommand=hsb.set)
        
        # Grid layout for tree and scrollbars
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')

        # Controls
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
        
        # Validate input length and format
        if not text:
            messagebox.showwarning("Đầu vào trống", "Vui lòng nhập một lệnh.")
            return
        
        if len(text) < 5:
            messagebox.showwarning(
                "Đầu vào không hợp lệ",
                "Lệnh quá ngắn. Vui lòng nhập đầy đủ thông tin sự kiện."
            )
            return
        
        if len(text) > 300:
            messagebox.showwarning(
                "Đầu vào quá dài",
                "Lệnh không được vượt quá 300 ký tự. Vui lòng rút gọn lại."
            )
            return
        
        try:
            event_dict = self.nlp_pipeline.process(text)
            
            # Strict validation: event name and start_time are mandatory
            if not event_dict.get('event'):
                messagebox.showerror(
                    "Thiếu tên sự kiện",
                    "Không thể xác định tên sự kiện.\n\n"
                    "Ví dụ hợp lệ:\n"
                    "• Họp nhóm lúc 10h sáng mai ở phòng 302\n"
                    "• Đi khám bệnh 8:30 ngày mai tại bệnh viện\n"
                    "• Gặp khách 14h thứ 2\n\n"
                    "Vui lòng nhập lại với cấu trúc: [Sự kiện] + [Thời gian] + [Địa điểm (tùy chọn)]"
                )
                self.nlp_entry.focus()
                return
            
            if not event_dict.get('start_time'):
                messagebox.showerror(
                    "Thiếu thông tin thời gian",
                    "Không thể xác định thời gian.\n\n"
                    "Ví dụ hợp lệ:\n"
                    "• 10h sáng mai\n"
                    "• 8:30 ngày mai\n"
                    "• 14h thứ 2\n"
                    "• 9:00 CN tuần sau\n\n"
                    "Vui lòng nhập lại với thời gian rõ ràng."
                )
                self.nlp_entry.focus()
                return
            
            # Warning for missing location (not blocking)
            if not event_dict.get('location'):
                response = messagebox.askyesno(
                    "Thiếu địa điểm",
                    f"Sự kiện: {event_dict['event']}\n"
                    f"Thời gian: {event_dict['start_time'][:16]}\n\n"
                    "Bạn chưa chỉ định địa điểm.\n"
                    "Bạn có muốn tiếp tục không?",
                    icon='warning'
                )
                if not response:
                    self.nlp_entry.focus()
                    return
            
            # Add event to database with duplicate checking
            result = self.db_manager.add_event(event_dict)
            
            if not result.get('success'):
                if result.get('error') == 'duplicate_time':
                    # Show duplicate events
                    duplicates = result.get('duplicates', [])
                    dup_info = []
                    for d in duplicates[:3]:  # Show max 3 duplicates
                        dup_info.append(f"  • ID {d['id']}: {d['event_name']} - {d['start_time'][:16]}")
                    dup_list = "\n".join(dup_info)
                    
                    messagebox.showerror(
                        "Trùng lặp thời gian",
                        f"Đã có sự kiện khác vào thời điểm này!\n\n"
                        f"Thời gian: {event_dict['start_time'][:16]}\n\n"
                        f"Sự kiện trùng:\n{dup_list}\n\n"
                        f"Vui lòng chọn thời gian khác."
                    )
                else:
                    # Other integrity errors
                    err_msg = result.get('message', 'Unknown error')
                    messagebox.showerror(
                        "Lỗi database",
                        f"Không thể thêm sự kiện:\n{err_msg}"
                    )
                self.nlp_entry.focus()
                return
            
            # Success - clear input and refresh
            self.nlp_entry.delete(0, 'end')
            self.refresh_for_date(self.calendar.selection_get())
            
            # Success message with details
            # Success message with details
            loc_text = event_dict.get('location') or '(không có)'
            rem_text = f"{event_dict.get('reminder_minutes', 0)} phút" if event_dict.get('reminder_minutes') else "không"
            messagebox.showinfo(
                "Thành công",
                f"Đã thêm sự kiện:\n\n"
                f"• Tên: {event_dict['event']}\n"
                f"• Thời gian: {event_dict['start_time'][:16]}\n"
                f"• Địa điểm: {loc_text}\n"
                f"• Nhắc trước: {rem_text}"
            )
            
        except Exception as e:
            messagebox.showerror("Lỗi xử lý", f"Đã xảy ra lỗi khi xử lý lệnh:\n{e}\n\nVui lòng thử lại.")

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
            remind_str = 'Có' if (ev.get('reminder_minutes') or 0) > 0 else 'Không'
            self.tree.insert('', 'end', values=(ev['id'], ev['event_name'], time_str, remind_str, ev.get('location') or ''))

    def _render_events(self, events):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for ev in events:
            time_str = (ev.get('start_time') or '')[11:16] if ev.get('start_time') else ''
            remind_str = 'Có' if (ev.get('reminder_minutes') or 0) > 0 else 'Không'
            self.tree.insert('', 'end', values=(ev.get('id'), ev.get('event_name'), time_str, remind_str, ev.get('location') or ''))

    def handle_search(self):
        mode = self.search_mode_var.get()
        query = self.search_entry.get().strip()
        try:
            if mode == 'Lịch đã đặt':
                # Lấy tất cả sự kiện đã lên lịch
                events = self.db_manager.get_all_events()
            elif mode == 'ID':
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
            count = import_from_json(self.db_manager, path, self.nlp_pipeline)
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
            result = self.db_manager.update_event(ev_id, payload)
            
            if not result.get('success'):
                if result.get('error') == 'duplicate_time':
                    # Show duplicate events
                    duplicates = result.get('duplicates', [])
                    dup_info = []
                    for d in duplicates[:3]:
                        dup_info.append(f"  • ID {d['id']}: {d['event_name']} - {d['start_time'][:16]}")
                    dup_list = "\n".join(dup_info)
                    
                    messagebox.showerror(
                        "Trùng lặp thời gian",
                        f"Đã có sự kiện khác vào thời điểm này!\n\n"
                        f"Thời gian: {new_iso[:16]}\n\n"
                        f"Sự kiện trùng:\n{dup_list}\n\n"
                        f"Vui lòng chọn thời gian khác."
                    )
                else:
                    err_msg = result.get('message', 'Unknown error')
                    messagebox.showerror(
                        "Lỗi database",
                        f"Không thể cập nhật:\n{err_msg}"
                    )
                return
            
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
