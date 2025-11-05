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
from datetime import date, datetime

from core_nlp.pipeline import NLPPipeline
from database.db_manager import DatabaseManager
from services.notification_service import start_notification_service
from services.export_service import export_to_json, export_to_ics
from services.import_service import import_from_json, import_from_ics
from services.statistics_service import StatisticsService

# Matplotlib for charts
try:
    import matplotlib
    matplotlib.use('TkAgg')
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("⚠️ WARNING: matplotlib not installed - statistics dashboard disabled")


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
        ttk.Button(input_frame, text="Xóa tất cả", command=self.handle_delete_all_events).pack(side='left', padx=(8, 0))
        
        # Statistics button (only if matplotlib is available)
        if MATPLOTLIB_AVAILABLE:
            ttk.Button(input_frame, text="📊 Thống kê", command=self.handle_show_statistics).pack(side='left', padx=(8, 0))

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

    def handle_delete_all_events(self):
        """
        Delete all events from database with double confirmation.
        This is a dangerous operation that cannot be undone.
        """
        try:
            # Get total event count
            all_events = self.db_manager.get_all_events()
            total_count = len(all_events)
            
            # Check if there are any events
            if total_count == 0:
                messagebox.showinfo(
                    "Không có lịch",
                    "Không có sự kiện nào trong hệ thống để xóa."
                )
                return
            
            # First confirmation - Show impact
            confirm_msg = (
                f"⚠️ CẢNH BÁO: Thao tác nguy hiểm!\n\n"
                f"Bạn sắp xóa TẤT CẢ {total_count} sự kiện trong hệ thống.\n\n"
                f"Thao tác này KHÔNG THỂ HOÀN TÁC!\n\n"
                f"Bạn có chắc chắn muốn tiếp tục không?"
            )
            
            first_confirm = messagebox.askokcancel(
                "Xác nhận xóa tất cả",
                confirm_msg,
                icon='warning'
            )
            
            if not first_confirm:
                return
            
            # Second confirmation - Double check
            second_confirm = messagebox.askyesno(
                "Xác nhận lần 2",
                f"Lần xác nhận cuối cùng!\n\n"
                f"Xóa {total_count} sự kiện?\n\n"
                f"Nhấn YES để XÓA HẾT\n"
                f"Nhấn NO để HỦY BỎ",
                icon='warning'
            )
            
            if not second_confirm:
                messagebox.showinfo("Đã hủy", "Đã hủy thao tác xóa tất cả.")
                return
            
            # Perform deletion
            deleted_count = self.db_manager.delete_all_events()
            
            # Refresh UI
            self.refresh_for_date(self.calendar.selection_get())
            
            # Clear search if active
            if getattr(self, 'search_mode', False):
                self.search_entry.delete(0, 'end')
                self.search_mode = False
            
            # Success message
            messagebox.showinfo(
                "Đã xóa thành công",
                f"✅ Đã xóa {deleted_count} sự kiện.\n\n"
                f"Hệ thống đã được làm sạch hoàn toàn."
            )
            
        except Exception as e:
            messagebox.showerror(
                "Lỗi xóa",
                f"Không thể xóa tất cả sự kiện:\n{e}\n\n"
                f"Vui lòng thử lại hoặc liên hệ hỗ trợ."
            )

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

    # --- Statistics Dashboard ---
    def handle_show_statistics(self):
        """Show comprehensive statistics dashboard"""
        if not MATPLOTLIB_AVAILABLE:
            messagebox.showerror(
                "Thiếu thư viện",
                "Tính năng thống kê yêu cầu matplotlib.\n\n"
                "Vui lòng cài đặt: pip install matplotlib reportlab"
            )
            return
            
        try:
            # Initialize statistics service
            stats_service = StatisticsService(self.db_manager)
            
            # Get all statistics
            stats = stats_service.get_comprehensive_stats()
            
            # Check if there are events
            if stats['overview']['total_events'] == 0:
                messagebox.showinfo(
                    "Không có dữ liệu",
                    "Chưa có sự kiện nào trong hệ thống.\n\n"
                    "Hãy thêm sự kiện để xem thống kê."
                )
                return
            
            # Create statistics dialog
            self._show_statistics_dialog(stats, stats_service)
            
        except Exception as e:
            messagebox.showerror(
                "Lỗi thống kê",
                f"Không thể tạo thống kê:\n{e}\n\n"
                "Vui lòng thử lại."
            )
    
    def _show_statistics_dialog(self, stats: dict, stats_service):
        """Display statistics in a tabbed dialog window"""
        # Create dialog window
        stats_window = tk.Toplevel(self)
        stats_window.title("📊 Thống kê & Phân tích")
        stats_window.geometry("900x700")
        stats_window.transient(self)  # Set as child of main window
        
        # Create notebook (tabs)
        notebook = ttk.Notebook(stats_window)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Tab 1: Overview
        overview_frame = ttk.Frame(notebook)
        notebook.add(overview_frame, text="📊 Tổng quan")
        self._build_overview_tab(overview_frame, stats['overview'])
        
        # Tab 2: Time Analysis
        time_frame = ttk.Frame(notebook)
        notebook.add(time_frame, text="⏰ Thời gian")
        self._build_time_tab(time_frame, stats['time'], stats_service)
        
        # Tab 3: Location
        location_frame = ttk.Frame(notebook)
        notebook.add(location_frame, text="📍 Địa điểm")
        self._build_location_tab(location_frame, stats['location'], stats_service)
        
        # Tab 4: Event Type
        type_frame = ttk.Frame(notebook)
        notebook.add(type_frame, text="🏷️ Phân loại")
        self._build_event_type_tab(type_frame, stats['event_type'], stats_service)
        
        # Tab 5: Trends
        trend_frame = ttk.Frame(notebook)
        notebook.add(trend_frame, text="📈 Xu hướng")
        self._build_trend_tab(trend_frame, stats['trends'], stats_service)
        
        # Bottom frame with export buttons
        export_frame = ttk.Frame(stats_window)
        export_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(
            export_frame,
            text="📄 Xuất PDF",
            command=lambda: self._export_stats_pdf(stats)
        ).pack(side='left', padx=5)
        
        ttk.Button(
            export_frame,
            text="📊 Xuất Excel",
            command=lambda: self._export_stats_excel(stats)
        ).pack(side='left', padx=5)
        
        ttk.Button(
            export_frame,
            text="Đóng",
            command=stats_window.destroy
        ).pack(side='right', padx=5)
    
    def _build_overview_tab(self, parent, stats):
        """Build overview statistics tab"""
        # Scrollable frame
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Title
        title = ttk.Label(
            scrollable_frame,
            text="📊 THỐNG KÊ TỔNG QUAN",
            font=('Arial', 16, 'bold')
        )
        title.pack(pady=20)
        
        # Stats container
        stats_container = ttk.Frame(scrollable_frame)
        stats_container.pack(fill='both', expand=True, padx=40)
        
        # Display stats with cards
        self._add_stat_card(stats_container, "📋 Tổng số sự kiện", stats['total_events'], 0)
        self._add_stat_card(stats_container, "📅 Sự kiện tuần này", stats['week_events'], 1)
        self._add_stat_card(stats_container, "📆 Sự kiện tháng này", stats['month_events'], 2)
        
        # Separator
        ttk.Separator(stats_container, orient='horizontal').grid(
            row=3, column=0, columnspan=2, sticky='ew', pady=20
        )
        
        self._add_stat_card(stats_container, "🔔 Có nhắc nhở", 
                           f"{stats['with_reminder']} ({stats['reminder_percentage']:.1f}%)", 4)
        self._add_stat_card(stats_container, "📍 Có địa điểm", 
                           f"{stats['with_location']} ({stats['location_percentage']:.1f}%)", 5)
        
        ttk.Separator(stats_container, orient='horizontal').grid(
            row=6, column=0, columnspan=2, sticky='ew', pady=20
        )
        
        self._add_stat_card(stats_container, "🔥 Streak hiện tại", 
                           f"{stats['current_streak']} ngày", 7)
        self._add_stat_card(stats_container, "🏆 Streak dài nhất", 
                           f"{stats['longest_streak']} ngày", 8)
        self._add_stat_card(stats_container, "📊 TB sự kiện/ngày (30 ngày)", 
                           f"{stats['avg_events_per_day']:.1f}", 9)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def _add_stat_card(self, parent, label: str, value, row: int):
        """Add a statistic card to the grid"""
        # Label
        lbl = ttk.Label(
            parent,
            text=label,
            font=('Arial', 12)
        )
        lbl.grid(row=row, column=0, sticky='w', pady=10, padx=10)
        
        # Value
        val = ttk.Label(
            parent,
            text=str(value),
            font=('Arial', 14, 'bold'),
            foreground='blue'
        )
        val.grid(row=row, column=1, sticky='e', pady=10, padx=10)
        
        parent.columnconfigure(0, weight=1)
        parent.columnconfigure(1, weight=1)
    
    def _build_time_tab(self, parent, stats, stats_service):
        """Build time analysis tab with charts"""
        # Create notebook for sub-tabs
        time_notebook = ttk.Notebook(parent)
        time_notebook.pack(fill='both', expand=True)
        
        # Weekday chart
        weekday_frame = ttk.Frame(time_notebook)
        time_notebook.add(weekday_frame, text="Theo ngày")
        
        fig_weekday = stats_service.create_weekday_chart(stats)
        canvas_weekday = FigureCanvasTkAgg(fig_weekday, weekday_frame)
        canvas_weekday.draw()
        canvas_weekday.get_tk_widget().pack(fill='both', expand=True)
        
        # Hourly chart
        hourly_frame = ttk.Frame(time_notebook)
        time_notebook.add(hourly_frame, text="Theo giờ")
        
        fig_hourly = stats_service.create_hourly_chart(stats)
        canvas_hourly = FigureCanvasTkAgg(fig_hourly, hourly_frame)
        canvas_hourly.draw()
        canvas_hourly.get_tk_widget().pack(fill='both', expand=True)
        
        # Summary info
        summary_frame = ttk.Frame(time_notebook)
        time_notebook.add(summary_frame, text="Tóm tắt")
        
        info_text = f"""
        📊 PHÂN TÍCH THỜI GIAN
        
        🔥 Ngày bận nhất: {['Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6', 'Thứ 7', 'Chủ nhật'][stats['peak_day']]} 
           → {stats['peak_day_count']} sự kiện
        
        ⏰ Giờ bận nhất: {stats['peak_hour']}:00
           → {stats['peak_hour_count']} sự kiện
        
        💡 Insight:
        - Hãy tránh đặt thêm lịch vào {['Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6', 'Thứ 7', 'Chủ nhật'][stats['peak_day']]}
        - Khoảng {stats['peak_hour']}:00 là thời gian bạn bận nhất
        """
        
        ttk.Label(summary_frame, text=info_text, justify='left', font=('Arial', 11)).pack(
            pady=20, padx=20
        )
    
    def _build_location_tab(self, parent, stats, stats_service):
        """Build location tab with chart"""
        if stats['total_unique_locations'] == 0:
            ttk.Label(
                parent,
                text="📍 Chưa có dữ liệu địa điểm\n\nHãy thêm địa điểm vào các sự kiện",
                font=('Arial', 14),
                justify='center'
            ).pack(expand=True)
            return
        
        # Chart
        chart_frame = ttk.Frame(parent)
        chart_frame.pack(fill='both', expand=True, side='top')
        
        fig = stats_service.create_location_chart(stats)
        canvas = FigureCanvasTkAgg(fig, chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
        
        # Summary
        summary_frame = ttk.Frame(parent)
        summary_frame.pack(fill='x', side='bottom', padx=20, pady=10)
        
        summary_text = f"Tổng {stats['total_unique_locations']} địa điểm khác nhau"
        ttk.Label(summary_frame, text=summary_text, font=('Arial', 11, 'bold')).pack()
    
    def _build_event_type_tab(self, parent, stats, stats_service):
        """Build event type tab with pie chart"""
        # Chart
        chart_frame = ttk.Frame(parent)
        chart_frame.pack(fill='both', expand=True)
        
        fig = stats_service.create_event_type_pie_chart(stats)
        canvas = FigureCanvasTkAgg(fig, chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
    
    def _build_trend_tab(self, parent, stats, stats_service):
        """Build trend analysis tab"""
        # Chart
        chart_frame = ttk.Frame(parent)
        chart_frame.pack(fill='both', expand=True, side='top')
        
        fig = stats_service.create_trend_chart(stats)
        canvas = FigureCanvasTkAgg(fig, chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
        
        # Growth info
        info_frame = ttk.Frame(parent)
        info_frame.pack(fill='x', side='bottom', padx=20, pady=20)
        
        growth = stats['growth_rate']
        if growth > 0:
            trend_text = f"📈 Tăng {growth:.1f}% so với tuần trước"
            color = 'green'
        elif growth < 0:
            trend_text = f"📉 Giảm {abs(growth):.1f}% so với tuần trước"
            color = 'red'
        else:
            trend_text = "➡️ Không thay đổi so với tuần trước"
            color = 'black'
        
        ttk.Label(
            info_frame,
            text=trend_text,
            font=('Arial', 12, 'bold'),
            foreground=color
        ).pack()
    
    def _export_stats_pdf(self, stats):
        """Export statistics to PDF"""
        try:
            filepath = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                initialfile=f"thong-ke-{datetime.now().strftime('%Y%m%d')}.pdf"
            )
            
            if not filepath:
                return
            
            stats_service = StatisticsService(self.db_manager)
            stats_service.export_to_pdf(filepath, stats)
            
            messagebox.showinfo(
                "Xuất PDF thành công",
                f"Đã xuất thống kê ra file:\n{filepath}"
            )
            
        except Exception as e:
            messagebox.showerror(
                "Lỗi xuất PDF",
                f"Không thể xuất PDF:\n{e}"
            )
    
    def _export_stats_excel(self, stats):
        """Export statistics to Excel"""
        try:
            filepath = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                initialfile=f"thong-ke-{datetime.now().strftime('%Y%m%d')}.xlsx"
            )
            
            if not filepath:
                return
            
            stats_service = StatisticsService(self.db_manager)
            stats_service.export_to_excel(filepath, stats)
            
            messagebox.showinfo(
                "Xuất Excel thành công",
                f"Đã xuất thống kê ra file:\n{filepath}"
            )
            
        except Exception as e:
            messagebox.showerror(
                "Lỗi xuất Excel",
                f"Không thể xuất Excel:\n{e}"
            )


if __name__ == '__main__':
    db = DatabaseManager()
    nlp = NLPPipeline()
    app = Application(db, nlp)
    # Dịch vụ nhắc nhở nền
    start_notification_service(app, db)
    app.mainloop()
