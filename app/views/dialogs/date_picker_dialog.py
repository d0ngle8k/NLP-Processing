"""
Date Picker Dialog - Google Calendar style
Interactive calendar picker for selecting dates
"""
import customtkinter as ctk
from datetime import date, timedelta
from calendar import monthrange
import calendar

# Import from config
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from app.config import COLORS, FONTS, SPACING


class DatePickerDialog(ctk.CTkToplevel):
    """
    Modal date picker dialog with calendar view
    """
    
    def __init__(self, parent, initial_date=None):
        """
        Initialize date picker dialog
        
        Args:
            parent: Parent window
            initial_date: Initially selected date (default: today)
        """
        super().__init__(parent)
        
        # Initialize
        self.result = None
        self.selected_date = initial_date if initial_date else date.today()
        self.viewing_date = self.selected_date  # Month/year being viewed
        
        # Configure window
        self.title("Chọn ngày")
        self.geometry("340x380")
        self.resizable(False, False)
        
        # Modal behavior
        self.transient(parent)
        self.grab_set()
        
        # Center on parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 340) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 380) // 2
        self.geometry(f"+{x}+{y}")
        
        # Build UI
        self._create_ui()
        
        # Keyboard shortcuts
        self.bind('<Escape>', lambda e: self._cancel())
        self.bind('<Return>', lambda e: self._confirm())
        
        # Focus
        self.focus_set()
    
    def _create_ui(self):
        """Build the UI"""
        # Main container with padding
        container = ctk.CTkFrame(self, fg_color=COLORS['bg_white'])
        container.pack(fill='both', expand=True, padx=SPACING['lg'], pady=SPACING['lg'])
        
        # Header with month/year navigation
        self._create_header(container)
        
        # Calendar grid
        self._create_calendar_grid(container)
        
        # Action buttons
        self._create_buttons(container)
    
    def _create_header(self, parent):
        """Create month/year header with navigation"""
        header_frame = ctk.CTkFrame(parent, fg_color='transparent')
        header_frame.pack(fill='x', pady=(0, SPACING['md']))
        
        # Previous month button (BLACK ARROWS)
        prev_btn = ctk.CTkButton(
            header_frame,
            text="◀",
            width=40,
            height=36,
            fg_color=COLORS['bg_gray'],
            hover_color=COLORS['bg_gray_hover'],
            text_color='#000000',  # BLACK
            font=FONTS['body_bold'],
            command=self._prev_month
        )
        prev_btn.pack(side='left')
        
        # Month/Year label (clickable for sliders)
        self.month_label = ctk.CTkLabel(
            header_frame,
            text=self._get_month_year_text(),
            font=FONTS['heading'],
            text_color=COLORS['text_primary'],
            cursor='hand2'  # Show it's clickable
        )
        self.month_label.pack(side='left', fill='x', expand=True)
        
        # Click month label to show month slider
        self.month_label.bind('<Button-1>', lambda e: self._show_month_slider())
        
        # Next month button (BLACK ARROWS)
        next_btn = ctk.CTkButton(
            header_frame,
            text="▶",
            width=40,
            height=36,
            fg_color=COLORS['bg_gray'],
            hover_color=COLORS['bg_gray_hover'],
            text_color='#000000',  # BLACK
            font=FONTS['body_bold'],
            command=self._next_month
        )
        next_btn.pack(side='right')
        
        # Store header frame reference for sliders
        self.header_frame = header_frame
        self.slider_active = False
    
    def _create_calendar_grid(self, parent):
        """Create calendar grid with dates"""
        # Container for calendar
        cal_frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_gray'], corner_radius=8)
        cal_frame.pack(fill='both', expand=True, pady=(0, SPACING['md']))
        
        # Weekday headers
        weekdays = ['CN', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7']
        header_row = ctk.CTkFrame(cal_frame, fg_color='transparent')
        header_row.pack(fill='x', padx=4, pady=(4, 2))
        
        for weekday in weekdays:
            label = ctk.CTkLabel(
                header_row,
                text=weekday,
                font=("Segoe UI", 10, "bold"),
                text_color=COLORS['text_secondary'],
                width=40
            )
            label.pack(side='left', expand=True)
        
        # Date cells container
        self.date_cells_frame = ctk.CTkFrame(cal_frame, fg_color='transparent')
        self.date_cells_frame.pack(fill='both', expand=True, padx=4, pady=(2, 4))
        
        # Create date cells
        self._populate_dates()
    
    def _populate_dates(self):
        """Populate calendar with dates for current viewing month"""
        # Clear existing cells
        for widget in self.date_cells_frame.winfo_children():
            widget.destroy()
        
        # Get calendar data
        year = self.viewing_date.year
        month = self.viewing_date.month
        
        # First day of month and number of days
        first_weekday = date(year, month, 1).weekday()
        first_weekday = (first_weekday + 1) % 7  # Convert to Sunday=0
        days_in_month = monthrange(year, month)[1]
        
        # Today
        today = date.today()
        
        # Create 6 rows (max weeks in month)
        row_index = 0
        col_index = 0
        
        # Previous month days (grayed out)
        if first_weekday > 0:
            prev_month = month - 1 if month > 1 else 12
            prev_year = year if month > 1 else year - 1
            days_in_prev = monthrange(prev_year, prev_month)[1]
            
            for i in range(first_weekday):
                day = days_in_prev - first_weekday + i + 1
                self._create_date_cell(
                    row_index, col_index, day,
                    is_current_month=False
                )
                col_index += 1
        
        # Current month days
        for day in range(1, days_in_month + 1):
            current_date = date(year, month, day)
            is_today = (current_date == today)
            is_selected = (current_date == self.selected_date)
            
            self._create_date_cell(
                row_index, col_index, day,
                is_current_month=True,
                is_today=is_today,
                is_selected=is_selected,
                date_obj=current_date
            )
            
            col_index += 1
            if col_index >= 7:
                col_index = 0
                row_index += 1
        
        # Next month days (grayed out)
        if col_index > 0:
            day = 1
            while col_index < 7:
                self._create_date_cell(
                    row_index, col_index, day,
                    is_current_month=False
                )
                col_index += 1
                day += 1
                if col_index >= 7 and row_index < 5:
                    col_index = 0
                    row_index += 1
    
    def _create_date_cell(self, row, col, day, is_current_month=True, 
                          is_today=False, is_selected=False, date_obj=None):
        """Create a single date cell"""
        # Determine colors
        if is_selected:
            bg_color = COLORS['primary_blue']
            text_color = 'white'
            hover_color = COLORS['primary_blue_hover']
        elif is_today:
            bg_color = COLORS['bg_gray']
            text_color = COLORS['primary_blue']
            hover_color = COLORS['border_light']
        elif not is_current_month:
            bg_color = 'transparent'
            text_color = COLORS['text_disabled']
            hover_color = COLORS['bg_gray']
        else:
            bg_color = 'transparent'
            text_color = COLORS['text_primary']
            hover_color = COLORS['bg_gray']
        
        # Create button (NO COMMAND - use double-click binding instead)
        btn = ctk.CTkButton(
            self.date_cells_frame,
            text=str(day),
            width=40,
            height=36,
            fg_color=bg_color,
            text_color=text_color,
            hover_color=hover_color,
            font=FONTS['body'],
            corner_radius=6
        )
        btn.grid(row=row, column=col, padx=1, pady=1, sticky='nsew')
        
        # DOUBLE-CLICK to select date
        if date_obj:
            btn.bind('<Double-Button-1>', lambda e, d=date_obj: self._select_date(d))
        
        # Configure grid weights
        self.date_cells_frame.grid_rowconfigure(row, weight=1)
        self.date_cells_frame.grid_columnconfigure(col, weight=1)
    
    def _create_buttons(self, parent):
        """Create action buttons"""
        button_frame = ctk.CTkFrame(parent, fg_color='transparent')
        button_frame.pack(fill='x')
        
        # Today button (left)
        today_btn = ctk.CTkButton(
            button_frame,
            text="📅 Hôm nay",
            width=100,
            height=40,
            fg_color=COLORS['bg_gray'],
            hover_color=COLORS['bg_gray_hover'],
            font=FONTS['body'],
            command=self._select_today
        )
        today_btn.pack(side='left')
        
        # Cancel button
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Hủy",
            width=80,
            height=40,
            fg_color=COLORS['bg_gray'],
            hover_color=COLORS['border_light'],
            font=FONTS['body'],
            command=self._cancel
        )
        cancel_btn.pack(side='right', padx=(SPACING['sm'], 0))
        
        # Confirm button
        confirm_btn = ctk.CTkButton(
            button_frame,
            text="✓ Chọn",
            width=100,
            height=40,
            fg_color=COLORS['primary_blue'],
            hover_color=COLORS['primary_blue_hover'],
            font=FONTS['body_bold'],
            command=self._confirm
        )
        confirm_btn.pack(side='right')
    
    def _show_month_slider(self):
        """Show month/year selection sliders"""
        if self.slider_active:
            return
        
        self.slider_active = True
        
        # Create slider container
        slider_frame = ctk.CTkFrame(self.header_frame, fg_color=COLORS['bg_white'], corner_radius=8)
        slider_frame.place(relx=0.5, rely=1.2, anchor='n', relwidth=0.9)
        
        # Month slider label
        month_label = ctk.CTkLabel(
            slider_frame,
            text="Tháng:",
            font=FONTS['body_bold'],
            text_color=COLORS['text_primary']
        )
        month_label.grid(row=0, column=0, padx=(10, 5), pady=(10, 5), sticky='w')
        
        # Month slider (1-12)
        self.month_slider = ctk.CTkSlider(
            slider_frame,
            from_=1,
            to=12,
            number_of_steps=11,
            width=200,
            command=lambda v: self._update_month_preview(int(v))
        )
        self.month_slider.set(self.viewing_date.month)
        self.month_slider.grid(row=0, column=1, padx=5, pady=(10, 5), sticky='ew')
        
        # Month value display
        self.month_value_label = ctk.CTkLabel(
            slider_frame,
            text=f"{self.viewing_date.month}",
            font=FONTS['body_bold'],
            text_color=COLORS['primary_blue'],
            width=30
        )
        self.month_value_label.grid(row=0, column=2, padx=(5, 10), pady=(10, 5))
        
        # Year slider label
        year_label = ctk.CTkLabel(
            slider_frame,
            text="Năm:",
            font=FONTS['body_bold'],
            text_color=COLORS['text_primary']
        )
        year_label.grid(row=1, column=0, padx=(10, 5), pady=5, sticky='w')
        
        # Year slider (2000-2025)
        self.year_slider = ctk.CTkSlider(
            slider_frame,
            from_=2000,
            to=2025,
            number_of_steps=25,
            width=200,
            command=lambda v: self._update_year_preview(int(v))
        )
        self.year_slider.set(self.viewing_date.year)
        self.year_slider.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        
        # Year value display
        self.year_value_label = ctk.CTkLabel(
            slider_frame,
            text=f"{self.viewing_date.year}",
            font=FONTS['body_bold'],
            text_color=COLORS['primary_blue'],
            width=50
        )
        self.year_value_label.grid(row=1, column=2, padx=(5, 10), pady=5)
        
        # Apply button
        apply_btn = ctk.CTkButton(
            slider_frame,
            text="✓ Áp dụng",
            width=120,
            height=32,
            fg_color=COLORS['primary_blue'],
            hover_color=COLORS['primary_blue_hover'],
            font=FONTS['body'],
            command=lambda: self._apply_slider_changes(slider_frame)
        )
        apply_btn.grid(row=2, column=0, columnspan=3, pady=(5, 10))
        
        # Configure grid
        slider_frame.grid_columnconfigure(1, weight=1)
        
        # Store reference
        self.active_slider_frame = slider_frame
    
    def _update_month_preview(self, month):
        """Update month preview label"""
        self.month_value_label.configure(text=f"{month}")
    
    def _update_year_preview(self, year):
        """Update year preview label"""
        self.year_value_label.configure(text=f"{year}")
    
    def _apply_slider_changes(self, slider_frame):
        """Apply month/year changes from sliders"""
        # Get values from sliders
        new_month = int(self.month_slider.get())
        new_year = int(self.year_slider.get())
        
        # Update viewing date
        self.viewing_date = date(new_year, new_month, 1)
        
        # Update UI
        self.month_label.configure(text=self._get_month_year_text())
        self._populate_dates()
        
        # Close slider
        slider_frame.destroy()
        self.slider_active = False
    
    def _get_month_year_text(self):
        """Get formatted month/year text"""
        month_names = [
            '', 'Tháng 1', 'Tháng 2', 'Tháng 3', 'Tháng 4', 'Tháng 5', 'Tháng 6',
            'Tháng 7', 'Tháng 8', 'Tháng 9', 'Tháng 10', 'Tháng 11', 'Tháng 12'
        ]
        return f"{month_names[self.viewing_date.month]} {self.viewing_date.year}"
    
    def _prev_month(self):
        """Navigate to previous month"""
        year = self.viewing_date.year
        month = self.viewing_date.month - 1
        if month < 1:
            month = 12
            year -= 1
        self.viewing_date = date(year, month, 1)
        self.month_label.configure(text=self._get_month_year_text())
        self._populate_dates()
    
    def _next_month(self):
        """Navigate to next month"""
        year = self.viewing_date.year
        month = self.viewing_date.month + 1
        if month > 12:
            month = 1
            year += 1
        self.viewing_date = date(year, month, 1)
        self.month_label.configure(text=self._get_month_year_text())
        self._populate_dates()
    
    def _select_date(self, date_obj):
        """Select a date"""
        if date_obj:
            self.selected_date = date_obj
            self._populate_dates()  # Refresh to show selection
    
    def _select_today(self):
        """Select today's date"""
        self.selected_date = date.today()
        self.viewing_date = date.today()
        self.month_label.configure(text=self._get_month_year_text())
        self._populate_dates()
    
    def _confirm(self):
        """Confirm selection and close"""
        self.result = self.selected_date
        self.destroy()
    
    def _cancel(self):
        """Cancel and close"""
        self.result = None
        self.destroy()
    
    def get_result(self):
        """Get selected date"""
        return self.result
