"""
Trợ lý Lịch trình Cá nhân - CustomTkinter Version
Modern UI with Material Design, Dark/Light mode, Event Cards

Migrated from Tkinter to CustomTkinter for better UX
Author: d0ngle8k
Version: 1.0.0-CTk
"""

from __future__ import annotations
import sys
from pathlib import Path

# --- PyInstaller _MEIPASS Hack cho underthesea ---
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    Path.home = lambda: Path(sys._MEIPASS)
# -------------------------------------------------

import customtkinter as ctk
from tkinter import messagebox, filedialog
import tkinter as tk  # Only for messagebox/filedialog compatibility
from tkcalendar import Calendar
from datetime import date, datetime, timedelta

from database.db_manager import DatabaseManager
from services.notification_service import start_notification_service
from services.export_service import export_to_json, export_to_ics
from services.import_service import import_from_json, import_from_ics
from widgets.event_card import EventCard

# NLP Pipeline - Hybrid (Rule-based + PhoBERT)
# Silence verbose startup logs in production builds
VERBOSE_LOG = False
try:
    from core_nlp.hybrid_pipeline import HybridNLPPipeline
    USE_HYBRID = True
    if VERBOSE_LOG:
        print("🔥 Using Hybrid NLP (Rule-based + PhoBERT AI)")
except ImportError:
    try:
        from core_nlp.phobert_model import PhoBERTNLPPipeline
        USE_HYBRID = False
        USE_PHOBERT = True
        if VERBOSE_LOG:
            print("✅ Using PhoBERT-based NLP (AI Model)")
    except ImportError:
        from core_nlp.pipeline import NLPPipeline
        USE_HYBRID = False
        USE_PHOBERT = False
        if VERBOSE_LOG:
            print("⚠️ Using Rule-based NLP (Hybrid/PhoBERT not available)")

# Set CustomTkinter appearance with smooth animations
ctk.set_appearance_mode("dark")  # "dark", "light", "system"
ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"

# Enable widget scaling for smoother transitions
ctk.deactivate_automatic_dpi_awareness()  # Better control over scaling


class Application(ctk.CTk):
    """Main application with CustomTkinter modern UI"""
    
    def __init__(self, database: DatabaseManager, nlp_pipeline):
        super().__init__()
        self.title("🗓️ Trợ lý Lịch trình Cá nhân")
        self.geometry("1200x800")
        
        self.db_manager = database
        self.nlp_pipeline = nlp_pipeline
        
        # Sorting state tracking
        self.sort_states = {
            'time': False,  # Default sort by time
            'name': False,
            'location': False
        }
        self.current_sort = 'time'
        
        self._build_ui()
        self._load_today()
    
    def _build_ui(self):
        """Build the modern UI with CustomTkinter"""
        
        # ===== TOP BAR: Title + Theme Toggle =====
        top_bar = ctk.CTkFrame(
            self,
            height=55,
            corner_radius=0,
            fg_color=("#667eea", "#1e1e2e")
        )
        top_bar.pack(fill='x', side='top')
        top_bar.pack_propagate(False)
        
        title_label = ctk.CTkLabel(
            top_bar,
            text="🗓️ Trợ lý Lịch trình Cá nhân",
            font=("Arial", 19, "bold"),
            text_color="white"
        )
        title_label.pack(side='left', padx=25)
        
        # Theme toggle
        self.theme_var = tk.StringVar(value="dark")
        theme_switch = ctk.CTkSwitch(
            top_bar,
            text="🌙 Dark Mode",
            variable=self.theme_var,
            onvalue="dark",
            offvalue="light",
            command=self._toggle_theme,
            text_color="white",
            font=("Arial", 12)
        )
        theme_switch.pack(side='right', padx=25)
        theme_switch.select()  # Default dark
        
        settings_btn = ctk.CTkButton(
            top_bar,
            text="⚙️ Cài đặt",
            width=110,
            height=35,
            corner_radius=8,
            fg_color="transparent",
            border_width=2,
            border_color="white",
            hover_color=("#5566d8", "#2e2e3e"),
            font=("Arial", 12, "bold"),
            command=self.handle_show_settings
        )
        settings_btn.pack(side='right', padx=15)
        
        # ===== INPUT FRAME: NLP Entry + Buttons =====
        input_frame = ctk.CTkFrame(self, corner_radius=12, fg_color="transparent")
        input_frame.pack(fill='x', side='top', padx=20, pady=15)
        
        input_label = ctk.CTkLabel(
            input_frame,
            text="📝 Lập lịch:",
            font=("Arial", 14, "bold")
        )
        input_label.pack(side='left', padx=(10, 10))
        
        self.nlp_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="VD: Họp nhóm lúc 10h sáng mai ở phòng 302 nhắc trước 30 phút",
            height=45,
            corner_radius=10,
            font=("Arial", 13),
            border_width=2
        )
        self.nlp_entry.pack(side='left', fill='x', expand=True, padx=10)
        # Validation for 300 chars limit
        self.nlp_entry.configure(validate='key', validatecommand=(self.register(lambda s: len(s) <= 300), '%P'))
        
        # Button styling
        btn_style = {
            'height': 45,
            'corner_radius': 10,
            'font': ("Arial", 13, "bold")
        }
        
        add_btn = ctk.CTkButton(
            input_frame,
            text="➕ Thêm",
            fg_color=("#4CAF50", "#2e7d32"),
            hover_color=("#45a049", "#1b5e20"),
            command=self.handle_add_event,
            width=100,
            **btn_style
        )
        add_btn.pack(side='left', padx=4)
        
        delete_btn = ctk.CTkButton(
            input_frame,
            text="🗑️ Xóa tất cả",
            fg_color=("#f44336", "#c62828"),
            hover_color=("#da190b", "#8e0000"),
            command=self.handle_delete_all_events,
            width=120,
            **btn_style
        )
        delete_btn.pack(side='left', padx=4)
        
        # ===== SEARCH FRAME =====
        search_frame = ctk.CTkFrame(self, corner_radius=12, fg_color="transparent")
        search_frame.pack(fill='x', side='top', padx=20, pady=(0, 15))
        
        search_label = ctk.CTkLabel(
            search_frame,
            text="🔍 Tìm kiếm:",
            font=("Arial", 13, "bold")
        )
        search_label.pack(side='left', padx=(10, 10))
        
        self.search_mode_var = tk.StringVar(value='Nội dung')
        self.search_field = ctk.CTkComboBox(
            search_frame,
            values=['ID', 'Nội dung', 'Địa điểm', 'Lịch đã đặt'],
            width=150,
            height=38,
            corner_radius=8,
            state='readonly',
            variable=self.search_mode_var,
            font=("Arial", 12)
        )
        self.search_field.pack(side='left', padx=6)
        self.search_field.set('Nội dung')
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Nhập từ khóa...",
            height=38,
            corner_radius=8,
            font=("Arial", 12)
        )
        self.search_entry.pack(side='left', fill='x', expand=True, padx=6)
        # Validation for 100 chars limit
        self.search_entry.configure(validate='key', validatecommand=(self.register(lambda s: len(s) <= 100), '%P'))
        
        search_btn = ctk.CTkButton(
            search_frame,
            text="Tìm",
            width=80,
            height=38,
            corner_radius=8,
            font=("Arial", 12, "bold"),
            command=self.handle_search
        )
        search_btn.pack(side='left', padx=4)
        
        clear_search_btn = ctk.CTkButton(
            search_frame,
            text="Xóa lọc",
            width=90,
            height=38,
            corner_radius=8,
            fg_color=("gray70", "gray30"),
            font=("Arial", 12, "bold"),
            command=self.handle_clear_search
        )
        clear_search_btn.pack(side='left', padx=4)
        
        # ===== MAIN CONTENT: Calendar + Event List =====
        main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        main_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        main_frame.grid_columnconfigure(0, weight=0, minsize=320)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
        
        # Calendar (left side) - Dynamic theme support
        calendar_frame = ctk.CTkFrame(main_frame, corner_radius=12)
        calendar_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 15))
        
        calendar_title = ctk.CTkLabel(
            calendar_frame,
            text="📅 Lịch",
            font=("Arial", 15, "bold")
        )
        calendar_title.pack(pady=10)
        
        # Get initial theme colors
        is_dark = ctk.get_appearance_mode() == "Dark"
        
        self.calendar = Calendar(
            calendar_frame,
            selectmode='day',
            date_pattern='y-mm-dd',
            borderwidth=0,
            # Dark theme colors (will be updated on theme change)
            background='#2b2b2b' if is_dark else 'white',
            foreground='white' if is_dark else 'black',
            selectbackground='#1e88e5',
            selectforeground='white',
            normalbackground='#2b2b2b' if is_dark else 'white',
            normalforeground='white' if is_dark else 'black',
            weekendbackground='#363636' if is_dark else '#f5f5f5',
            weekendforeground='white' if is_dark else 'black',
            othermonthforeground='#666666' if is_dark else '#999999',
            othermonthbackground='#2b2b2b' if is_dark else 'white',
            othermonthweforeground='#666666' if is_dark else '#999999',
            othermonthwebackground='#2b2b2b' if is_dark else 'white',
            headersbackground='#1e1e1e' if is_dark else '#e0e0e0',
            headersforeground='white' if is_dark else 'black'
        )
        self.calendar.pack(padx=10, pady=(0, 10), fill='both', expand=True)
        self.calendar.bind("<<CalendarSelected>>", self.handle_date_select)
        
        # Event list (right side)
        event_list_frame = ctk.CTkFrame(main_frame, corner_radius=12)
        event_list_frame.grid(row=0, column=1, sticky='nsew')
        
        # Header bar
        header = ctk.CTkFrame(
            event_list_frame,
            height=55,
            corner_radius=0,
            fg_color=("#667eea", "#1e1e2e")
        )
        header.pack(fill='x', side='top')
        header.pack_propagate(False)
        
        self.event_count_label = ctk.CTkLabel(
            header,
            text="📅 SỰ KIỆN (0 sự kiện)",
            font=("Arial", 16, "bold"),
            text_color="white"
        )
        self.event_count_label.pack(side='left', padx=20, pady=12)
        
        # Sort dropdown
        self.sort_var = tk.StringVar(value="Thời gian")
        sort_menu = ctk.CTkComboBox(
            header,
            values=["Thời gian", "Tên A-Z", "Địa điểm", "ID"],
            width=140,
            height=35,
            corner_radius=8,
            variable=self.sort_var,
            command=self._handle_sort_change,
            font=("Arial", 11, "bold"),
            state='readonly'
        )
        sort_menu.pack(side='right', padx=20)
        
        # Scrollable container for event cards
        self.event_container = ctk.CTkScrollableFrame(
            event_list_frame,
            corner_radius=0,
            fg_color="transparent"
        )
        self.event_container.pack(fill='both', expand=True, padx=15, pady=15)
        
        # ===== EDIT FRAME (Popup Dialog Style) =====
        self.edit_window = None  # Will be created when needed
        
        # Search mode flag
        self.search_mode = False
    
    def _toggle_theme(self):
        """Toggle between dark and light mode with smooth transition"""
        mode = self.theme_var.get()
        ctk.set_appearance_mode(mode)
        
        # Update calendar colors based on theme
        if mode == "dark":
            self.calendar.configure(
                background='#2b2b2b',
                foreground='white',
                selectbackground='#1e88e5',
                selectforeground='white',
                normalbackground='#2b2b2b',
                normalforeground='white',
                weekendbackground='#363636',
                weekendforeground='white',
                othermonthforeground='#666666',
                othermonthbackground='#2b2b2b',
                othermonthweforeground='#666666',
                othermonthwebackground='#2b2b2b',
                headersbackground='#1e1e1e',
                headersforeground='white'
            )
        else:  # light mode
            self.calendar.configure(
                background='white',
                foreground='black',
                selectbackground='#1e88e5',
                selectforeground='white',
                normalbackground='white',
                normalforeground='black',
                weekendbackground='#f5f5f5',
                weekendforeground='black',
                othermonthforeground='#999999',
                othermonthbackground='white',
                othermonthweforeground='#999999',
                othermonthwebackground='white',
                headersbackground='#e0e0e0',
                headersforeground='black'
            )
        
        # Force refresh calendar display
        self.calendar.update()
    
    def _handle_sort_change(self, choice):
        """Handle sort dropdown change"""
        if choice == "Thời gian":
            self.current_sort = 'time'
        elif choice == "Tên A-Z":
            self.current_sort = 'name'
        elif choice == "Địa điểm":
            self.current_sort = 'location'
        elif choice == "ID":
            self.current_sort = 'id'
        
        # Re-sort current events
        if hasattr(self, 'current_events') and self.current_events:
            self._sort_and_render()
    
    def _sort_and_render(self):
        """Sort current events and re-render"""
        if not hasattr(self, 'current_events') or not self.current_events:
            return
        
        events = self.current_events.copy()
        
        if self.current_sort == 'time':
            # Sort by time (nearest first)
            events.sort(key=lambda x: x.get('start_time') or '9999-12-31')
        elif self.current_sort == 'name':
            # Sort by event name A-Z
            events.sort(key=lambda x: (x.get('event_name') or '').lower())
        elif self.current_sort == 'location':
            # Sort by location
            events.sort(key=lambda x: (x.get('location') or 'zzz').lower())
        elif self.current_sort == 'id':
            # Sort by ID (ascending)
            events.sort(key=lambda x: x.get('id', 0))
        
        self._render_events(events)
    
    def _load_today(self):
        """Load events for initial display"""
        today = date.today()
        start_date = today - timedelta(days=30)
        end_date = today + timedelta(days=60)
        
        events = self.db_manager.get_events_by_date_range(start_date, end_date)
        
        if len(events) > 1000:
            events = events[:1000]
        
        self._render_events(events)
    
    def _render_events(self, events):
        """Render event cards (replaces Treeview)"""
        # Store current events
        self.current_events = events
        
        # Clear existing cards
        for widget in self.event_container.winfo_children():
            widget.destroy()
        
        # Update header count
        self.event_count_label.configure(
            text=f"📅 SỰ KIỆN ({len(events)} sự kiện)"
        )
        
        # Empty state
        if not events:
            empty_label = ctk.CTkLabel(
                self.event_container,
                text="📭 Chưa có sự kiện nào\n\nHãy thêm sự kiện mới bằng cách nhập lệnh ở trên",
                font=("Arial", 15),
                text_color=("gray50", "gray60")
            )
            empty_label.pack(pady=80)
            return
        
        # Render event cards
        callbacks = {
            'on_edit': self._handle_card_edit,
            'on_delete': self._handle_card_delete
        }
        
        for event in events:
            card = EventCard(self.event_container, event, callbacks)
            card.pack(fill='x', pady=6, padx=5)
    
    def _handle_card_edit(self, event_data):
        """Handle edit button click from card"""
        self._show_edit_dialog(event_data)
    
    def _handle_card_delete(self, event_data):
        """Handle delete button click from card"""
        ev_id = event_data.get('id')
        ev_name = event_data.get('event_name', 'N/A')
        
        confirm = messagebox.askyesno(
            "Xác nhận xóa",
            f"Bạn có chắc muốn xóa sự kiện:\n\n{ev_name}?"
        )
        
        if confirm:
            self.db_manager.delete_event(int(ev_id))
            self.refresh_for_date(self.calendar.selection_get())
            messagebox.showinfo("Thành công", "Đã xóa sự kiện")
    
    def _show_edit_dialog(self, event_data):
        """Show edit dialog as popup window"""
        if self.edit_window and self.edit_window.winfo_exists():
            self.edit_window.destroy()
        
        self.edit_window = ctk.CTkToplevel(self)
        self.edit_window.title("✏️ Chỉnh sửa sự kiện")
        self.edit_window.geometry("550x500")
        self.edit_window.transient(self)
        self.edit_window.grab_set()
        
        # Title bar
        title_bar = ctk.CTkFrame(
            self.edit_window,
            height=50,
            fg_color=("#667eea", "#1e1e2e")
        )
        title_bar.pack(fill='x')
        title_bar.pack_propagate(False)
        
        ctk.CTkLabel(
            title_bar,
            text="✏️ Chỉnh sửa sự kiện",
            font=("Arial", 16, "bold"),
            text_color="white"
        ).pack(side='left', padx=20, pady=10)
        
        # Content
        content = ctk.CTkScrollableFrame(self.edit_window)
        content.pack(fill='both', expand=True, padx=25, pady=20)
        
        # Parse start_time
        st = event_data.get('start_time', '')
        date_str = st[:10] if len(st) >= 10 else ''
        time_str = st[11:16] if len(st) >= 16 else ''
        
        # Form fields
        self.edit_vars = {
            'id': tk.StringVar(value=str(event_data.get('id', ''))),
            'event_name': tk.StringVar(value=event_data.get('event_name', '')),
            'date': tk.StringVar(value=date_str),
            'time': tk.StringVar(value=time_str),
            'location': tk.StringVar(value=event_data.get('location', '')),
            'reminder': tk.StringVar(value=str(event_data.get('reminder_minutes', 0)))
        }
        
        fields = [
            ('ID:', 'id', True),  # Read-only
            ('Sự kiện:', 'event_name', False),
            ('Ngày (YYYY-MM-DD):', 'date', False),
            ('Giờ (HH:MM):', 'time', False),
            ('Địa điểm:', 'location', False),
            ('Nhắc trước (phút):', 'reminder', False)
        ]
        
        for i, (label_text, var_name, readonly) in enumerate(fields):
            # Label
            ctk.CTkLabel(
                content,
                text=label_text,
                font=("Arial", 13),
                anchor='w'
            ).grid(row=i, column=0, sticky='w', pady=10, padx=(0, 15))
            
            # Entry or Label (for ID)
            if readonly:
                ctk.CTkLabel(
                    content,
                    textvariable=self.edit_vars[var_name],
                    font=("Arial", 13, "bold"),
                    anchor='w'
                ).grid(row=i, column=1, sticky='w', pady=10)
            else:
                entry = ctk.CTkEntry(
                    content,
                    textvariable=self.edit_vars[var_name],
                    width=320,
                    height=38,
                    corner_radius=8,
                    font=("Arial", 12)
                )
                entry.grid(row=i, column=1, sticky='w', pady=10)
        
        # Buttons
        btn_frame = ctk.CTkFrame(content, fg_color="transparent")
        btn_frame.grid(row=len(fields), column=0, columnspan=2, pady=(20, 10))
        
        ctk.CTkButton(
            btn_frame,
            text="💾 Lưu",
            width=130,
            height=42,
            corner_radius=10,
            fg_color=("#4CAF50", "#2e7d32"),
            hover_color=("#45a049", "#1b5e20"),
            font=("Arial", 13, "bold"),
            command=self._save_edit
        ).pack(side='left', padx=8)
        
        ctk.CTkButton(
            btn_frame,
            text="❌ Hủy",
            width=130,
            height=42,
            corner_radius=10,
            fg_color=("gray70", "gray30"),
            font=("Arial", 13, "bold"),
            command=self.edit_window.destroy
        ).pack(side='left', padx=8)
    
    def _save_edit(self):
        """Save edited event"""
        try:
            ev_id = int(self.edit_vars['id'].get())
            event_name = self.edit_vars['event_name'].get().strip()
            date_str = self.edit_vars['date'].get().strip()
            time_str = self.edit_vars['time'].get().strip()
            location = self.edit_vars['location'].get().strip() or None
            reminder = int(self.edit_vars['reminder'].get() or 0)
            
            if not (event_name and date_str and time_str):
                messagebox.showwarning(
                    "Thiếu dữ liệu",
                    "Vui lòng điền đủ Sự kiện, Ngày và Giờ."
                )
                return
            
            # Build ISO datetime
            old = self.db_manager.get_event_by_id(ev_id)
            tz_suffix = ''
            if old and isinstance(old.get('start_time'), str):
                st = old['start_time']
                if len(st) > 19 and (st[19] in ['+', '-'] or st.endswith('Z')):
                    tz_suffix = st[19:]
            
            new_iso = f"{date_str}T{time_str}:00{tz_suffix}"
            
            payload = {
                'event_name': event_name,
                'start_time': new_iso,
                'end_time': old.get('end_time') if old else None,
                'location': location,
                'reminder_minutes': reminder
            }
            
            result = self.db_manager.update_event(ev_id, payload)
            
            if not result.get('success'):
                if result.get('error') == 'duplicate_time':
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
            self.edit_window.destroy()
            messagebox.showinfo("Thành công", "Đã cập nhật sự kiện")
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu: {e}")
    
    def handle_add_event(self):
        """Add event via NLP input"""
        text = self.nlp_entry.get().strip()
        
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
                "Lệnh không được vượt quá 300 ký tự."
            )
            return
        
        try:
            event_dict = self.nlp_pipeline.process(text)
            
            # Validation
            event_name = event_dict.get('event_name')
            if not event_name or not event_name.strip():
                messagebox.showerror(
                    "Thiếu tên sự kiện",
                    "Không thể xác định tên sự kiện.\n\n"
                    "Ví dụ hợp lệ:\n"
                    "• Họp nhóm lúc 10h sáng mai ở phòng 302\n"
                    "• Đi khám bệnh 8:30 ngày mai tại bệnh viện\n"
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
                )
                self.nlp_entry.focus()
                return
            
            # Warning for missing location
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
            
            # Add to database
            result = self.db_manager.add_event(event_dict)
            
            if not result.get('success'):
                if result.get('error') == 'duplicate_time':
                    duplicates = result.get('duplicates', [])
                    dup_info = []
                    for d in duplicates[:3]:
                        dup_info.append(f"  • ID {d['id']}: {d['event_name']} - {d['start_time'][:16]}")
                    dup_list = "\n".join(dup_info)
                    
                    messagebox.showerror(
                        "Trùng lặp thời gian",
                        f"Đã có sự kiện khác vào thời điểm này!\n\n"
                        f"Thời gian: {event_dict['start_time'][:16]}\n\n"
                        f"Sự kiện trùng:\n{dup_list}"
                    )
                else:
                    err_msg = result.get('message', 'Unknown error')
                    messagebox.showerror(
                        "Lỗi database",
                        f"Không thể thêm sự kiện:\n{err_msg}"
                    )
                self.nlp_entry.focus()
                return
            
            # Success
            self.nlp_entry.delete(0, 'end')
            self.refresh_for_date(self.calendar.selection_get())
            
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
            messagebox.showerror("Lỗi xử lý", f"Đã xảy ra lỗi:\n{e}")
    
    def handle_delete_all_events(self):
        """Delete all events with confirmation"""
        try:
            all_events = self.db_manager.get_all_events()
            total_count = len(all_events)
            
            if total_count == 0:
                messagebox.showinfo(
                    "Không có lịch",
                    "Không có sự kiện nào để xóa."
                )
                return
            
            confirm = messagebox.askokcancel(
                "Xác nhận xóa tất cả",
                f"⚠️ CẢNH BÁO: Thao tác nguy hiểm!\n\n"
                f"Bạn sắp xóa TẤT CẢ {total_count} sự kiện.\n\n"
                f"Thao tác này KHÔNG THỂ HOÀN TÁC!\n\n"
                f"Bạn có chắc chắn?",
                icon='warning'
            )
            
            if not confirm:
                return
            
            # Second confirmation
            second_confirm = messagebox.askyesno(
                "Xác nhận lần 2",
                f"Xóa {total_count} sự kiện?\n\n"
                f"YES = XÓA HẾT\nNO = HỦY BỎ",
                icon='warning'
            )
            
            if not second_confirm:
                messagebox.showinfo("Đã hủy", "Đã hủy thao tác xóa.")
                return
            
            deleted_count = self.db_manager.delete_all_events()
            self.refresh_for_date(self.calendar.selection_get())
            
            if self.search_mode:
                self.search_entry.delete(0, 'end')
                self.search_mode = False
            
            messagebox.showinfo(
                "Thành công",
                f"✅ Đã xóa {deleted_count} sự kiện."
            )
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xóa:\n{e}")
    
    def handle_search(self):
        """Search events"""
        mode = self.search_mode_var.get()
        query = self.search_entry.get().strip()
        
        try:
            if mode == 'Lịch đã đặt':
                events = self.db_manager.get_all_events()
            elif mode == 'ID':
                if not query.isdigit():
                    messagebox.showwarning("Tìm kiếm", "ID phải là số.")
                    return
                events = self.db_manager.search_events_by_id(int(query))
            elif mode == 'Nội dung':
                if not query:
                    messagebox.showwarning("Tìm kiếm", "Vui lòng nhập từ khóa.")
                    return
                events = self.db_manager.search_events_by_name(query)
            else:  # Địa điểm
                if not query:
                    messagebox.showwarning("Tìm kiếm", "Vui lòng nhập địa điểm.")
                    return
                events = self.db_manager.search_events_by_location(query)
            
            self._render_events(events)
            self.search_mode = True
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tìm kiếm: {e}")
    
    def handle_clear_search(self):
        """Clear search and reload"""
        self.search_entry.delete(0, 'end')
        self.search_mode = False
        self.refresh_for_date(self.calendar.selection_get())
    
    def handle_date_select(self, _evt=None):
        """Handle calendar date selection"""
        if not self.search_mode:
            selected_date = self.calendar.selection_get()
            start_date = selected_date - timedelta(days=30)
            end_date = selected_date + timedelta(days=30)
            events = self.db_manager.get_events_by_date_range(start_date, end_date)
            
            if len(events) > 1000:
                events = events[:1000]
            
            self._render_events(events)
    
    def refresh_for_date(self, date_obj: date):
        """Refresh display for specific date"""
        start_date = date_obj - timedelta(days=30)
        end_date = date_obj + timedelta(days=30)
        events = self.db_manager.get_events_by_date_range(start_date, end_date)
        
        if len(events) > 1000:
            events = events[:1000]
        
        self._render_events(events)
    
    def handle_show_settings(self):
        """Show settings dialog"""
        settings = ctk.CTkToplevel(self)
        settings.title("⚙️ Cài đặt")
        settings.geometry("600x650")
        settings.transient(self)
        settings.grab_set()
        
        # Title bar
        title_bar = ctk.CTkFrame(
            settings,
            height=55,
            fg_color=("#667eea", "#1e1e2e")
        )
        title_bar.pack(fill='x')
        title_bar.pack_propagate(False)
        
        ctk.CTkLabel(
            title_bar,
            text="⚙️ Cài đặt",
            font=("Arial", 17, "bold"),
            text_color="white"
        ).pack(side='left', padx=25, pady=12)
        
        # Content
        content = ctk.CTkScrollableFrame(settings)
        content.pack(fill='both', expand=True, padx=25, pady=20)
        
        # === SOUND SETTINGS SECTION ===
        ctk.CTkLabel(
            content,
            text="🔔 Âm thanh thông báo",
            font=("Arial", 15, "bold")
        ).pack(anchor='w', pady=(5, 12))
        
        sound_frame = ctk.CTkFrame(content, fg_color="transparent")
        sound_frame.pack(fill='x', pady=(0, 25))
        
        # Get sound manager
        from services.notification_service import get_sound_manager
        sound_mgr = get_sound_manager()
        
        # Current sound info
        current_info = sound_mgr.get_current_sound_info()
        current_label = ctk.CTkLabel(
            sound_frame,
            text=f"Hiện tại: {current_info['name']}",
            font=("Arial", 11),
            text_color=("gray50", "gray70")
        )
        current_label.pack(anchor='w', pady=(0, 10))
        
        # Get all sounds (presets + custom)
        def get_all_sound_items():
            """Get combined list of all sounds for dropdown"""
            all_sounds = sound_mgr.get_all_sounds()
            items = []
            
            # Presets
            for preset in all_sounds['presets']:
                items.append({
                    'id': preset['id'],
                    'display': f"🔔 {preset['name']}",
                    'name': preset['name'],
                    'type': 'preset'
                })
            
            # Custom sounds
            if all_sounds['custom']:
                items.append({'id': 'separator', 'display': '─── Custom Sounds ───', 'type': 'separator'})
                for custom in all_sounds['custom']:
                    items.append({
                        'id': custom['id'],
                        'display': f"🎵 {custom['name']}",
                        'name': custom['name'],
                        'type': 'custom'
                    })
            
            return items
        
        # Sound selection row
        select_row = ctk.CTkFrame(sound_frame, fg_color="transparent")
        select_row.pack(fill='x', pady=5)
        
        ctk.CTkLabel(
            select_row,
            text="Chọn âm thanh:",
            font=("Arial", 12),
            width=140,
            anchor='w'
        ).pack(side='left')
        
        # Build dropdown items
        sound_items = get_all_sound_items()
        sound_map = {item['id']: item for item in sound_items if item['type'] != 'separator'}
        display_values = [item['display'] for item in sound_items]
        
        # Find current selection
        current_id = current_info.get('id', 'system_default')
        current_display = next((item['display'] for item in sound_items if item.get('id') == current_id), display_values[0])
        
        sound_var = tk.StringVar(value=current_display)
        sound_menu = ctk.CTkComboBox(
            select_row,
            values=display_values,
            variable=sound_var,
            width=250,
            state='readonly'
        )
        sound_menu.pack(side='left', padx=10)
        
        def refresh_sound_dropdown():
            """Refresh dropdown after adding/removing sounds"""
            nonlocal sound_items, sound_map
            sound_items = get_all_sound_items()
            sound_map = {item['id']: item for item in sound_items if item['type'] != 'separator'}
            display_values = [item['display'] for item in sound_items]
            
            sound_menu.configure(values=display_values)
            
            # Update current selection
            current_info = sound_mgr.get_current_sound_info()
            current_id = current_info.get('id', 'system_default')
            current_display = next((item['display'] for item in sound_items if item.get('id') == current_id), display_values[0])
            sound_var.set(current_display)
            current_label.configure(text=f"Hiện tại: {current_info['name']}")
        
        def on_sound_change(display_choice):
            # Skip separator
            if '───' in display_choice:
                # Reset to current
                current_info = sound_mgr.get_current_sound_info()
                current_id = current_info.get('id', 'system_default')
                current_display = next((item['display'] for item in sound_items if item.get('id') == current_id), display_values[0])
                sound_var.set(current_display)
                return
            
            # Find selected item
            selected_item = next((item for item in sound_items if item.get('display') == display_choice), None)
            if not selected_item:
                return
            
            sound_id = selected_item['id']
            sound_type = selected_item['type']
            
            print(f"🔊 User selected: {selected_item['name']} (id: {sound_id}, type: {sound_type})")
            
            try:
                if sound_type == 'preset':
                    # Preset sound - CẬP NHẬT NGAY (nhanh)
                    sound_mgr.set_preset_sound(sound_id)
                    
                    # Save to DB in background thread (BATCH - 1 DB call thay vì 2)
                    def save_preset():
                        try:
                            self.db_manager.set_settings_batch({
                                'notification_sound_type': 'preset',
                                'notification_sound_preset': sound_id
                            })
                            print(f"✅ Saved preset to DB: {sound_id}")
                        except Exception as e:
                            print(f"⚠️ DB save error: {e}")
                    
                    import threading
                    threading.Thread(target=save_preset, daemon=True).start()
                    
                elif sound_type == 'custom':
                    # Custom sound - ensure file exists
                    filename = sound_id.replace('custom:', '')
                    file_path = sound_mgr.custom_dir / filename
                    
                    if not file_path.exists():
                        messagebox.showerror(
                            "❌ Lỗi",
                            f"File âm thanh không tồn tại:\n{filename}\n\nVui lòng thêm lại file."
                        )
                        return
                    
                    # CẬP NHẬT NGAY (nhanh)
                    sound_mgr.set_custom_sound(str(file_path))
                    
                    # Save to DB in background thread (BATCH - 1 DB call thay vì 3)
                    def save_custom():
                        try:
                            self.db_manager.set_settings_batch({
                                'notification_sound_type': 'custom',
                                'notification_sound_path': str(file_path),
                                'notification_sound_filename': filename
                            })
                            print(f"✅ Saved custom sound to DB: {filename}")
                        except Exception as e:
                            print(f"⚠️ DB save error: {e}")
                    
                    import threading
                    threading.Thread(target=save_custom, daemon=True).start()
                
                # Update UI NGAY LẬP TỨC (không đợi DB)
                current_label.configure(text=f"Hiện tại: {selected_item['name']}")
                
            except Exception as e:
                print(f"❌ Error changing sound: {e}")
                import traceback
                traceback.print_exc()
                messagebox.showerror("❌ Lỗi", f"Không thể thay đổi âm thanh:\n{str(e)}")
        
        sound_menu.configure(command=on_sound_change)
        
        # Buttons row
        buttons_row = ctk.CTkFrame(sound_frame, fg_color="transparent")
        buttons_row.pack(fill='x', pady=10)
        
        # Add custom sound
        def add_custom_sound():
            filepath = filedialog.askopenfilename(
                title="Chọn file âm thanh",
                filetypes=[
                    ("Audio files", "*.wav *.mp3 *.ogg *.m4a"),
                    ("WAV files", "*.wav"),
                    ("MP3 files", "*.mp3"),
                    ("All files", "*.*")
                ]
            )
            if filepath:
                filename = sound_mgr.add_custom_sound(filepath)
                if filename:
                    # Set as current sound NGAY
                    file_path = sound_mgr.custom_dir / filename
                    sound_mgr.set_custom_sound(str(file_path))
                    
                    # Refresh UI NGAY (không đợi DB)
                    refresh_sound_dropdown()
                    
                    # Save to database in background (BATCH - 1 DB call thay vì 3)
                    def save_to_db():
                        try:
                            self.db_manager.set_settings_batch({
                                'notification_sound_type': 'custom',
                                'notification_sound_path': str(file_path),
                                'notification_sound_filename': filename
                            })
                            print(f"✅ Saved to DB: {filename}")
                        except Exception as e:
                            print(f"⚠️ DB save error: {e}")
                    
                    import threading
                    threading.Thread(target=save_to_db, daemon=True).start()
                    
                    # Show success message
                    messagebox.showinfo("✅ Thành công", f"Đã thêm âm thanh:\n{filename}")
                else:
                    messagebox.showerror("❌ Lỗi", "Không thể thêm file âm thanh")
        
        ctk.CTkButton(
            buttons_row,
            text="➕ Thêm âm thanh",
            width=140,
            height=35,
            corner_radius=8,
            font=("Arial", 12),
            fg_color=("#4CAF50", "#2e7d32"),
            hover_color=("#45a049", "#1b5e20"),
            command=add_custom_sound
        ).pack(side='left', padx=(0, 10))
        
        # Delete custom sound
        def delete_custom_sound():
            current_info = sound_mgr.get_current_sound_info()
            
            # Check if current is custom
            if current_info['type'] != 'custom':
                messagebox.showwarning("⚠️ Chú ý", "Vui lòng chọn một âm thanh custom để xóa")
                return
            
            filename = current_info['name']
            
            # Confirm deletion
            confirm = messagebox.askyesno(
                "❓ Xác nhận xóa",
                f"Bạn có chắc muốn xóa âm thanh:\n{filename}?",
                icon='question'
            )
            
            if confirm:
                # Delete file NGAY (fast operation)
                success = sound_mgr.remove_custom_sound(filename)
                
                if success:
                    # Refresh UI NGAY (không đợi DB)
                    refresh_sound_dropdown()
                    
                    # Show success message NGAY
                    messagebox.showinfo("✅ Thành công", f"Đã xóa âm thanh:\n{filename}")
                    
                    # Clear from database in background (BATCH - 1 DB call thay vì 2)
                    def cleanup_db():
                        try:
                            self.db_manager.delete_settings_batch([
                                'notification_sound_filename',
                                'notification_sound_path'
                            ])
                            print(f"✅ Cleaned up DB for: {filename}")
                        except Exception as e:
                            print(f"⚠️ DB cleanup error: {e}")
                    
                    import threading
                    threading.Thread(target=cleanup_db, daemon=True).start()
                else:
                    messagebox.showerror("❌ Lỗi", "Không thể xóa file âm thanh")
        
        ctk.CTkButton(
            buttons_row,
            text="🗑️ Xóa âm thanh",
            width=140,
            height=35,
            corner_radius=8,
            font=("Arial", 12),
            fg_color=("#f44336", "#c62828"),
            hover_color=("#da190b", "#b71c1c"),
            command=delete_custom_sound
        ).pack(side='left', padx=(0, 10))
        
        # Preview button with loading state
        preview_btn = ctk.CTkButton(
            buttons_row,
            text="▶️ Nghe thử",
            width=120,
            height=35,
            corner_radius=8,
            font=("Arial", 12),
            fg_color=("#2196F3", "#1565C0"),
            hover_color=("#1976D2", "#0D47A1")
        )
        preview_btn.pack(side='left')
        
        def preview_sound():
            print(f"\n▶️ PREVIEW - Testing sound...")
            current = sound_mgr.get_current_sound_info()
            print(f"   Type: {current['type']}, Name: {current['name']}")
            
            # Show loading state
            preview_btn.configure(text="⏳ Đang phát...", state="disabled")
            
            # Reset button về ban đầu SAU 0.5 giây (đủ để user thấy feedback)
            settings.after(500, lambda: preview_btn.configure(text="▶️ Nghe thử", state="normal"))
            
            def play_async():
                try:
                    # Play sound trong background (không chờ)
                    success = sound_mgr.preview_sound(skip_debounce=True)
                    
                    if success:
                        print(f"✅ Sound preview started")
                    else:
                        print(f"⚠️ Preview failed")
                        settings.after(0, lambda: messagebox.showerror(
                            "❌ Lỗi phát âm thanh",
                            f"Không thể phát file:\n{current['name']}\n\n"
                            f"Vui lòng kiểm tra:\n"
                            f"1. File có tồn tại không\n"
                            f"2. Format được hỗ trợ (.wav, .mp3, .ogg)\n"
                            f"3. Thử cài: pip install playsound"
                        ))
                except Exception as e:
                    print(f"❌ Exception in preview: {e}")
                    import traceback
                    traceback.print_exc()
                    
                    def show_error():
                        messagebox.showerror("❌ Lỗi", f"Lỗi khi phát âm thanh:\n{str(e)}")
                    
                    settings.after(0, show_error)
            
            # Run in thread to avoid blocking UI
            import threading
            threading.Thread(target=play_async, daemon=True).start()
        
        preview_btn.configure(command=preview_sound)
        
        # === Import/Export Section ===
        ctk.CTkLabel(
            content,
            text="📤 Import/Export",
            font=("Arial", 15, "bold")
        ).pack(anchor='w', pady=(15, 12))
        
        io_frame = ctk.CTkFrame(content, fg_color="transparent")
        io_frame.pack(fill='x', pady=(0, 25))
        
        io_buttons = [
            ("📥 Import JSON", self.handle_import_json),
            ("📥 Import ICS", self.handle_import_ics),
            ("📤 Export JSON", self.handle_export_json),
            ("📤 Export ICS", self.handle_export_ics)
        ]
        
        for i, (text, cmd) in enumerate(io_buttons):
            if i % 2 == 0:
                row = ctk.CTkFrame(io_frame, fg_color="transparent")
                row.pack(fill='x', pady=5)
            
            ctk.CTkButton(
                row,
                text=text,
                width=260,
                height=40,
                corner_radius=10,
                font=("Arial", 12, "bold"),
                command=cmd
            ).pack(side='left', padx=8)
        
        # === App Info ===
        ctk.CTkLabel(
            content,
            text="ℹ️ Thông tin ứng dụng",
            font=("Arial", 15, "bold")
        ).pack(anchor='w', pady=(15, 12))
        
        info_frame = ctk.CTkFrame(content, corner_radius=12)
        info_frame.pack(fill='x', pady=(0, 15))
        
        info_items = [
            ("📋 Tên:", "Trợ Lý Lịch Trình"),
            ("📦 Phiên bản:", "1.0.0-CTk (CustomTkinter)"),
            ("👨‍💻 Phát triển:", "Trương Gia Thành"),
            ("📅 Năm:", "2025"),
            ("🎨 UI Framework:", "CustomTkinter 5.2+")
        ]
        
        for label, value in info_items:
            row = ctk.CTkFrame(info_frame, fg_color="transparent")
            row.pack(pady=8, padx=20, anchor='w')
            
            ctk.CTkLabel(
                row,
                text=label,
                font=("Arial", 11),
                width=120,
                anchor='w'
            ).pack(side='left')
            
            ctk.CTkLabel(
                row,
                text=value,
                font=("Arial", 11, "bold"),
                anchor='w'
            ).pack(side='left')
        
        # Close button
        ctk.CTkButton(
            settings,
            text="Đóng",
            width=120,
            height=40,
            corner_radius=10,
            font=("Arial", 13, "bold"),
            command=settings.destroy
        ).pack(pady=20)
    
    def handle_export_json(self):
        """Export to JSON with file dialog"""
        # Ask user for save location
        filepath = filedialog.asksaveasfilename(
            title="Lưu file JSON",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile="schedule_export.json"
        )
        
        if not filepath:  # User cancelled
            return
        
        try:
            export_to_json(self.db_manager, filepath)
            messagebox.showinfo("Xuất JSON", f"✅ Đã xuất file thành công:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Xuất JSON thất bại: {e}")
    
    def handle_export_ics(self):
        """Export to ICS with file dialog"""
        # Ask user for save location
        filepath = filedialog.asksaveasfilename(
            title="Lưu file ICS",
            defaultextension=".ics",
            filetypes=[("ICS files", "*.ics"), ("All files", "*.*")],
            initialfile="schedule_export.ics"
        )
        
        if not filepath:  # User cancelled
            return
        
        try:
            export_to_ics(self.db_manager, filepath)
            messagebox.showinfo("Xuất ICS", f"✅ Đã xuất file thành công:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Xuất ICS thất bại: {e}")
    
    def handle_import_json(self):
        """Import from JSON"""
        path = filedialog.askopenfilename(
            title="Chọn file JSON",
            filetypes=[("JSON", "*.json")]
        )
        if not path:
            return
        
        try:
            before_count = len(self.db_manager.get_all_events())
            count = import_from_json(self.db_manager, path, self.nlp_pipeline)
            after_count = len(self.db_manager.get_all_events())
            actual_added = after_count - before_count
            
            self.refresh_for_date(self.calendar.selection_get())
            
            if count == 0:
                messagebox.showwarning(
                    "Không nhập được",
                    "Không có sự kiện mới nào được nhập."
                )
            elif actual_added < count:
                messagebox.showinfo(
                    "Nhập JSON",
                    f"✅ Đã nhập {actual_added}/{count} sự kiện mới.\n\n"
                    f"⚠️ {count - actual_added} sự kiện bị bỏ qua do trùng."
                )
            else:
                messagebox.showinfo("Nhập JSON", f"✅ Đã nhập {count} sự kiện.")
                
        except Exception as e:
            messagebox.showerror("Lỗi", f"Nhập JSON thất bại: {e}")
    
    def handle_import_ics(self):
        """Import from ICS"""
        path = filedialog.askopenfilename(
            title="Chọn file ICS",
            filetypes=[("iCalendar", "*.ics")]
        )
        if not path:
            return
        
        try:
            count = import_from_ics(self.db_manager, path)
            self.refresh_for_date(self.calendar.selection_get())
            messagebox.showinfo("Nhập ICS", f"✅ Đã nhập {count} sự kiện.")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Nhập ICS thất bại: {e}")


if __name__ == '__main__':
    if VERBOSE_LOG:
        print("\n" + "="*70)
        print("🚀 CUSTOMTKINTER VERSION - Modern UI")
        print("="*70)
        print("✨ Features:")
        print("  • Material Design with rounded corners")
        print("  • Dark/Light mode toggle")
        print("  • Event cards (no more boring Treeview!)")
        print("  • Smooth animations and hover effects")
        print("  • Better spacing and modern colors")
        print("="*70 + "\n")
    
    db = DatabaseManager()
    
    # Initialize Sound Manager
    from services.notification_service import init_sound_manager
    sound_mgr = init_sound_manager('.')
    
    # Load saved sound settings from DB
    try:
        sound_type = db.get_setting('notification_sound_type', 'preset')
        if sound_type == 'preset':
            preset = db.get_setting('notification_sound_preset', 'system_default')
            sound_mgr.set_preset_sound(preset)
            if VERBOSE_LOG:
                print(f"🔊 Loaded preset sound: {preset}")
        elif sound_type == 'custom':
            # Try to load from saved path
            custom_path = db.get_setting('notification_sound_path')
            if custom_path and Path(custom_path).exists():
                sound_mgr.set_custom_sound(custom_path)
                if VERBOSE_LOG:
                    print(f"🔊 Loaded custom sound: {Path(custom_path).name}")
            else:
                # Fallback: try to load from filename in custom directory
                filename = db.get_setting('notification_sound_filename')
                if filename:
                    file_path = sound_mgr.custom_dir / filename
                    if file_path.exists():
                        sound_mgr.set_custom_sound(str(file_path))
                        if VERBOSE_LOG:
                            print(f"🔊 Loaded custom sound from filename: {filename}")
                    else:
                        if VERBOSE_LOG:
                            print(f"⚠️ Custom sound file not found, using default")
                        sound_mgr.set_preset_sound('system_default')
                else:
                    if VERBOSE_LOG:
                        print(f"⚠️ Custom sound path not found, using default")
                    sound_mgr.set_preset_sound('system_default')
    except Exception as e:
        if VERBOSE_LOG:
            print(f"⚠️ Could not load sound settings: {e}")
        sound_mgr.set_preset_sound('system_default')
    
    # Initialize NLP Pipeline
    if USE_HYBRID:
        import os
        model_path = "./models/phobert_finetuned"
        if VERBOSE_LOG:
            print("🔥 Initializing Hybrid NLP Pipeline...")
        nlp = HybridNLPPipeline(model_path=model_path if os.path.exists(model_path) else None)
        if VERBOSE_LOG:
            model_info = nlp.get_model_info()
            print(f"📊 Models: {model_info['mode']}")
    elif USE_PHOBERT:
        import os
        model_path = "./models/phobert_finetuned"
        if os.path.exists(model_path):
            if VERBOSE_LOG:
                print(f"🎯 Loading fine-tuned PhoBERT from {model_path}")
            nlp = PhoBERTNLPPipeline(model_path=model_path)
        else:
            if VERBOSE_LOG:
                print("🤖 Loading base PhoBERT (not fine-tuned)")
            nlp = PhoBERTNLPPipeline()
    else:
        nlp = NLPPipeline()
    
    app = Application(db, nlp)
    start_notification_service(app, db)
    
    if VERBOSE_LOG:
        print("✅ Application started! Enjoy the modern UI!\n")
    app.mainloop()
