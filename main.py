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
from datetime import date, datetime, timedelta

from database.db_manager import DatabaseManager
from services.notification_service import start_notification_service
from services.export_service import export_to_json, export_to_ics
from services.import_service import import_from_json, import_from_ics
# Statistics dashboard removed per request

# NLP Pipeline - Hybrid (Rule-based + PhoBERT)
try:
    from core_nlp.hybrid_pipeline import HybridNLPPipeline
    USE_HYBRID = True
    print("🔥 Using Hybrid NLP (Rule-based + PhoBERT AI)")
except ImportError:
    try:
        from core_nlp.phobert_model import PhoBERTNLPPipeline
        USE_HYBRID = False
        USE_PHOBERT = True
        print("✅ Using PhoBERT-based NLP (AI Model)")
    except ImportError:
        from core_nlp.pipeline import NLPPipeline
        USE_HYBRID = False
        USE_PHOBERT = False
        print("⚠️ Using Rule-based NLP (Hybrid/PhoBERT not available)")

# Matplotlib-based statistics dashboard has been removed/disabled
MATPLOTLIB_AVAILABLE = False


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
        
        # Sorting state tracking (column_name -> is_reverse)
        self.sort_states = {
            'id': False,
            'event_name': False,
            'time': False,
            'remind': False,
            'location': False
        }

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
        
        # Center headings - Bind click events for sorting
        self.tree.heading('id', text='ID ▼', anchor='center', command=lambda: self.handle_column_sort('id'))
        self.tree.heading('event_name', text='Sự kiện ▼', anchor='center', command=lambda: self.handle_column_sort('event_name'))
        self.tree.heading('time', text='Thời gian ▼', anchor='center', command=lambda: self.handle_column_sort('time'))
        self.tree.heading('remind', text='Nhắc tôi ▼', anchor='center', command=lambda: self.handle_column_sort('remind'))
        self.tree.heading('location', text='Địa điểm ▼', anchor='center', command=lambda: self.handle_column_sort('location'))
        
        # Center column contents
        self.tree.column('id', width=50, stretch=False, anchor='center')
        self.tree.column('event_name', width=330, anchor='center')
        self.tree.column('time', width=150, anchor='center')
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

        # Controls - Settings button (bottom left corner)
        ttk.Button(control_frame, text="⚙️ Cài đặt", command=self.handle_show_settings).pack(side='left', padx=4)

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
        """Load events for initial display - shows wider date range for better UX"""
        # Load events from 30 days ago to 60 days in future (90 days total)
        # This ensures users can see past and upcoming events without searching
        today = date.today()
        start_date = today - timedelta(days=30)
        end_date = today + timedelta(days=60)
        
        events = self.db_manager.get_events_by_date_range(start_date, end_date)
        
        # Limit to max 1000 events for performance
        if len(events) > 1000:
            events = events[:1000]
        
        self._render_events(events)
        
        # Optional: Set search mode to indicate we're showing filtered view
        # self.search_mode = True  # Uncomment if you want "Xóa lọc" to show today only

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
            # Check for None or empty string
            event_name = event_dict.get('event_name')
            if not event_name or not event_name.strip():
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
                    f"Sự kiện: {event_dict['event_name']}\n"
                    f"Thời gian: {event_dict['start_time'][:16]}\n\n"
                    "Bạn chưa chỉ định địa điểm.\n"
                    "Bạn có muốn tiếp tục không?",
                    icon='warning'
                )
                if not response:
                    self.nlp_entry.focus()
                    return
            
            # Add event to database with duplicate checking (keys already match schema)
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
                f"• Tên: {event_dict['event_name']}\n"
                f"• Thời gian: {event_dict['start_time'][:16]}\n"
                f"• Địa điểm: {loc_text}\n"
                f"• Nhắc trước: {rem_text}"
            )
            
        except Exception as e:
            messagebox.showerror("Lỗi xử lý", f"Đã xảy ra lỗi khi xử lý lệnh:\n{e}\n\nVui lòng thử lại.")

    def handle_date_select(self, _evt=None):
        # Nếu đang ở chế độ tìm kiếm, bỏ qua refresh theo ngày để không mất kết quả
        if not getattr(self, 'search_mode', False):
            # Load events around selected date (±30 days) for better context
            selected_date = self.calendar.selection_get()
            start_date = selected_date - timedelta(days=30)
            end_date = selected_date + timedelta(days=30)
            events = self.db_manager.get_events_by_date_range(start_date, end_date)
            
            # Limit to 1000 events max
            if len(events) > 1000:
                events = events[:1000]
            
            self._render_events(events)

    def refresh_for_date(self, date_obj: date):
        """Refresh display to show events around the given date (±30 days)"""
        start_date = date_obj - timedelta(days=30)
        end_date = date_obj + timedelta(days=30)
        events = self.db_manager.get_events_by_date_range(start_date, end_date)
        
        # Limit to 1000 events max
        if len(events) > 1000:
            events = events[:1000]
        
        self._render_events(events)

    def _render_events(self, events):
        # Clear current items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Store events for sorting (keep reference)
        self.current_events = events
        
        # Insert events
        for ev in events:
            # Hiển thị đầy đủ: DD/MM/YYYY HH:MM
            time_str = ''
            if ev.get('start_time'):
                try:
                    dt = datetime.fromisoformat(ev.get('start_time'))
                    time_str = dt.strftime('%d/%m/%Y %H:%M')
                except:
                    time_str = ev.get('start_time') or ''
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

    def handle_column_sort(self, column):
        """
        Sort table by column with intelligent sorting logic.
        
        Sorting behaviors:
        - ID: Numeric ASC/DESC toggle
        - Event name: Alphanumeric (numbers first, then A-Z, case-insensitive)
        - Time: Nearest first / Farthest first
        - Remind: 'Không' first / 'Có' first
        - Location: Alphanumeric (same as event name)
        
        Each click toggles between normal and reverse order.
        """
        # Check if we have events to sort
        if not hasattr(self, 'current_events') or not self.current_events:
            return
        
        # Toggle sort direction
        is_reverse = self.sort_states.get(column, False)
        self.sort_states[column] = not is_reverse
        
        # Update header indicators
        self._update_sort_indicators(column, not is_reverse)
        
        # Sort logic based on column
        if column == 'id':
            # Numeric sort
            sorted_events = sorted(
                self.current_events,
                key=lambda x: int(x.get('id', 0)),
                reverse=is_reverse
            )
        
        elif column == 'event_name':
            # Alphanumeric sort: numbers first, then letters (case-insensitive)
            def alphanumeric_key(event):
                name = (event.get('event_name') or '').strip()
                if not name:
                    return (2, '')  # Empty names go last
                first_char = name[0]
                if first_char.isdigit():
                    return (0, name.lower())  # Numbers first
                else:
                    return (1, name.lower())  # Letters after numbers
            
            sorted_events = sorted(
                self.current_events,
                key=alphanumeric_key,
                reverse=is_reverse
            )
        
        elif column == 'time':
            # Time sort: nearest first (ASC) or farthest first (DESC)
            def time_key(event):
                time_str = event.get('start_time', '')
                if not time_str:
                    # Events without time go to end
                    return datetime.max if not is_reverse else datetime.min
                try:
                    return datetime.fromisoformat(time_str)
                except:
                    return datetime.max if not is_reverse else datetime.min
            
            sorted_events = sorted(
                self.current_events,
                key=time_key,
                reverse=is_reverse
            )
        
        elif column == 'remind':
            # Reminder sort: 'Không' first (0), then 'Có' (1)
            def remind_key(event):
                reminder = event.get('reminder_minutes', 0) or 0
                return 1 if reminder > 0 else 0
            
            sorted_events = sorted(
                self.current_events,
                key=remind_key,
                reverse=is_reverse
            )
        
        elif column == 'location':
            # Alphanumeric sort (same as event name)
            def location_alphanumeric_key(event):
                loc = (event.get('location') or '').strip()
                if not loc:
                    return (2, '')  # Empty locations go last
                first_char = loc[0]
                if first_char.isdigit():
                    return (0, loc.lower())  # Numbers first
                else:
                    return (1, loc.lower())  # Letters after
            
            sorted_events = sorted(
                self.current_events,
                key=location_alphanumeric_key,
                reverse=is_reverse
            )
        
        else:
            # Fallback: no sorting
            sorted_events = self.current_events
        
        # Re-render with sorted events
        self._render_events(sorted_events)
    
    def _update_sort_indicators(self, active_column, is_reverse):
        """Update column headers with sort direction indicators"""
        headers = {
            'id': 'ID',
            'event_name': 'Sự kiện',
            'time': 'Thời gian',
            'remind': 'Nhắc tôi',
            'location': 'Địa điểm'
        }
        
        for col, label in headers.items():
            if col == active_column:
                # Show indicator for active column
                indicator = ' ▲' if is_reverse else ' ▼'
                self.tree.heading(col, text=label + indicator)
            else:
                # No indicator for inactive columns
                self.tree.heading(col, text=label + ' ▼')

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
            # Get count before import
            before_count = len(self.db_manager.get_all_events())
            
            count = import_from_json(self.db_manager, path, self.nlp_pipeline)
            
            # Get count after import
            after_count = len(self.db_manager.get_all_events())
            actual_added = after_count - before_count
            
            self.refresh_for_date(self.calendar.selection_get())
            
            # Show detailed message
            if count == 0:
                messagebox.showwarning(
                    "Không nhập được",
                    "Không có sự kiện mới nào được nhập.\n\n"
                    "Có thể do:\n"
                    "• File JSON không hợp lệ\n"
                    "• Tất cả sự kiện đã tồn tại (trùng thời gian)\n"
                    "• Thiếu thông tin bắt buộc (tên hoặc thời gian)"
                )
            elif actual_added < count:
                messagebox.showinfo(
                    "Nhập JSON",
                    f"✅ Đã nhập {actual_added}/{count} sự kiện mới.\n\n"
                    f"⚠️ {count - actual_added} sự kiện bị bỏ qua do trùng thời gian."
                )
            else:
                messagebox.showinfo("Nhập JSON", f"✅ Đã nhập {count} sự kiện từ JSON.")
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
                'event_name': event_name,  # ✅ FIXED: Use correct key
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

    # --- Statistics Dashboard removed ---
    
    # --- Settings Window ---
    def handle_show_settings(self):
        """Show settings window with app info and import/export"""
        # Create settings window
        settings_window = tk.Toplevel(self)
        settings_window.title("⚙️ Cài đặt")
        settings_window.geometry("550x600")
        settings_window.transient(self)  # Set as child of main window
        settings_window.resizable(False, False)
        
        # Main container
        main_container = ttk.Frame(settings_window, padding=20)
        main_container.pack(fill='both', expand=True)
        
        # === Section 1: Import/Export Data ===
        import_export_frame = ttk.LabelFrame(
            main_container,
            text="📁 Nhập/Xuất Dữ liệu",
            padding=15
        )
        import_export_frame.pack(fill='x', pady=(0, 20))
        
        # Description
        ttk.Label(
            import_export_frame,
            text="Sao lưu hoặc khôi phục dữ liệu lịch trình của bạn",
            font=('Arial', 9),
            foreground='gray'
        ).pack(pady=(0, 15))
        
        # Export buttons (centered)
        export_frame = ttk.Frame(import_export_frame)
        export_frame.pack(fill='x', pady=5)
        
        export_container = ttk.Frame(export_frame)
        export_container.pack(expand=True)
        
        ttk.Button(
            export_container,
            text="📤 Xuất ra JSON",
            command=self.handle_export_json,
            width=25
        ).pack(side='left', padx=5)
        
        ttk.Button(
            export_container,
            text="📤 Xuất ra ICS",
            command=self.handle_export_ics,
            width=25
        ).pack(side='left', padx=5)
        
        # Import buttons (centered)
        import_frame = ttk.Frame(import_export_frame)
        import_frame.pack(fill='x', pady=5)
        
        import_container = ttk.Frame(import_frame)
        import_container.pack(expand=True)
        
        ttk.Button(
            import_container,
            text="📥 Nhập từ JSON",
            command=self.handle_import_json,
            width=25
        ).pack(side='left', padx=5)
        
        ttk.Button(
            import_container,
            text="📥 Nhập từ ICS",
            command=self.handle_import_ics,
            width=25
        ).pack(side='left', padx=5)
        
        # === Section 2: Advanced Options ===
        advanced_frame = ttk.LabelFrame(
            main_container,
            text="🔧 Dọn Dẹp Dữ Liệu",
            padding=15
        )
        advanced_frame.pack(fill='x', pady=(0, 20))
        
        # Description (centered)
        ttk.Label(
            advanced_frame,
            text="Xóa toàn bộ sự kiện (không thể hoàn tác)",
            font=('Arial', 9),
            foreground='red'
        ).pack(pady=(0, 10))
        
        # Delete all button (centered)
        delete_container = ttk.Frame(advanced_frame)
        delete_container.pack(expand=True)
        
        ttk.Button(
            delete_container,
            text="🗑️ Xóa tất cả sự kiện",
            command=self.handle_delete_all_events,
        ).pack()
        
        # === Section 3: App Information ===
        info_frame = ttk.LabelFrame(
            main_container,
            text="ℹ️ Thông tin ứng dụng",
            padding=15
        )
        info_frame.pack(fill='both', expand=True, pady=(0, 20))
        
        # App info with styling
        info_container = ttk.Frame(info_frame)
        info_container.pack(expand=True)
        
        # App name
        ttk.Label(
            info_container,
            text="Trợ Lý Lịch Trình",
            font=('Arial', 16, 'bold'),
            foreground='#2196F3'
        ).pack(pady=(10, 5))
        
        # Separator
        ttk.Separator(info_container, orient='horizontal').pack(fill='x', pady=10)
        
        # Version info
        info_items = [
            ("📋 Tên ứng dụng:", "Trợ Lý Lịch Trình"),
            ("📦 Phiên bản:", "0.8.1"),
            ("👨‍💻 Phát triển bởi:", "Trương Gia Thành"),
            ("📅 Năm:", "2025"),
        ]
        
        for label, value in info_items:
            row = ttk.Frame(info_container)
            row.pack(pady=5, anchor='w', padx=20)
            
            ttk.Label(
                row,
                text=label,
                font=('Arial', 10),
                width=22,
                anchor='w'
            ).pack(side='left')
            
            ttk.Label(
                row,
                text=value,
                font=('Arial', 10, 'bold'),
                foreground='#424242',
                anchor='w'
            ).pack(side='left')
        
        # === Bottom: Close Button ===
        bottom_frame = ttk.Frame(main_container)
        bottom_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Button(
            bottom_frame,
            text="Đóng",
            command=settings_window.destroy,
            width=15
        ).pack(side='right')


if __name__ == '__main__':
    db = DatabaseManager()
    
    # Initialize NLP Pipeline (Hybrid > PhoBERT > Rule-based)
    if USE_HYBRID:
        # Use Hybrid Pipeline (Rule-based + PhoBERT)
        import os
        model_path = "./models/phobert_finetuned"
        print("🔥 Initializing Hybrid NLP Pipeline...")
        nlp = HybridNLPPipeline(model_path=model_path if os.path.exists(model_path) else None)
        model_info = nlp.get_model_info()
        print(f"📊 Models: {model_info['mode']}")
    elif USE_PHOBERT:
        # Use PhoBERT only
        import os
        model_path = "./models/phobert_finetuned"
        if os.path.exists(model_path):
            print(f"🎯 Loading fine-tuned PhoBERT from {model_path}")
            nlp = PhoBERTNLPPipeline(model_path=model_path)
        else:
            print("🤖 Loading base PhoBERT (not fine-tuned)")
            nlp = PhoBERTNLPPipeline()
    else:
        # Fallback to rule-based
        nlp = NLPPipeline()
    
    app = Application(db, nlp)
    # Dịch vụ nhắc nhở nền
    start_notification_service(app, db)
    app.mainloop()
