"""
Event Card Widget - Modern replacement for Treeview row
Hiển thị sự kiện dạng card với hover effect và action buttons
"""

import customtkinter as ctk


class EventCard(ctk.CTkFrame):
    """Modern event card widget - replaces Treeview row"""
    
    def __init__(self, parent, event_data, callbacks=None):
        """
        Initialize event card
        
        Args:
            parent: Parent widget
            event_data: Dictionary with event info {id, event_name, start_time, location, reminder_minutes}
            callbacks: Dict with 'on_edit' and 'on_delete' functions
        """
        super().__init__(
            parent, 
            corner_radius=12, 
            fg_color=("#e8e8e8", "#2b2b2b"),
            border_width=1,
            border_color=("#d0d0d0", "#404040")
        )
        
        self.event_data = event_data
        self.callbacks = callbacks or {}
        
        # Hover effect
        self.bind("<Enter>", self._on_hover_enter)
        self.bind("<Leave>", self._on_hover_leave)
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Build card UI components"""
        # ID Badge (left side)
        id_frame = ctk.CTkFrame(
            self, 
            corner_radius=8, 
            fg_color=("#667eea", "#667eea"),
            width=50
        )
        id_frame.pack(side='left', padx=12, pady=12, fill='y')
        id_frame.pack_propagate(False)
        
        id_label = ctk.CTkLabel(
            id_frame,
            text=f"#{self.event_data.get('id', '?')}",
            font=("Arial", 13, "bold"),
            text_color="white"
        )
        id_label.pack(expand=True)
        
        # Content area (center)
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(side='left', fill='both', expand=True, padx=10, pady=12)
        
        # Event name (bold, large)
        name_text = self.event_data.get('event_name', 'N/A')
        name = ctk.CTkLabel(
            content,
            text=f"📌 {name_text}",
            font=("Arial", 15, "bold"),
            anchor='w'
        )
        name.pack(anchor='w', pady=(0, 4))
        
        # Time + Location (smaller, gray)
        time_str = self.event_data.get('start_time', 'N/A')
        # Format: YYYY-MM-DD HH:MM:SS → YYYY-MM-DD HH:MM
        if len(time_str) > 16:
            time_str = time_str[:16]
        
        location = self.event_data.get('location', 'Không có địa điểm')
        details = f"🕐 {time_str}  |  📍 {location}"
        
        details_label = ctk.CTkLabel(
            content,
            text=details,
            font=("Arial", 12),
            text_color=("#666666", "#999999"),
            anchor='w'
        )
        details_label.pack(anchor='w')
        
        # Reminder badge (right side, optional)
        reminder = self.event_data.get('reminder_minutes', 0)
        if reminder and reminder > 0:
            remind_text = self._format_reminder(reminder)
            remind_frame = ctk.CTkFrame(
                self,
                corner_radius=8,
                fg_color=("#764ba2", "#764ba2")
            )
            remind_frame.pack(side='right', padx=12, pady=12)
            
            ctk.CTkLabel(
                remind_frame,
                text=f"🔔 {remind_text}",
                font=("Arial", 11),
                text_color="white",
                padx=12,
                pady=6
            ).pack()
        
        # Action buttons (right side)
        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.pack(side='right', padx=8, pady=12)
        
        # Edit button (yellow with text)
        edit_btn = ctk.CTkButton(
            actions,
            text="✏️ Sửa",
            width=75,
            height=35,
            corner_radius=8,
            fg_color=("#FFC107", "#F57F17"),
            hover_color=("#FFB300", "#E65100"),
            font=("Arial", 11, "bold"),
            command=lambda: self.callbacks.get('on_edit', lambda x: None)(self.event_data)
        )
        edit_btn.pack(side='top', pady=2)
        
        # Delete button (red with text)
        delete_btn = ctk.CTkButton(
            actions,
            text="🗑️ Xóa",
            width=75,
            height=35,
            corner_radius=8,
            fg_color=("#f44336", "#c62828"),
            hover_color=("#da190b", "#8e0000"),
            font=("Arial", 11, "bold"),
            command=lambda: self.callbacks.get('on_delete', lambda x: None)(self.event_data)
        )
        delete_btn.pack(side='top', pady=2)
    
    def _format_reminder(self, minutes):
        """
        Format reminder minutes to readable text
        
        Args:
            minutes: Number of minutes
            
        Returns:
            Formatted string (e.g., "30 phút", "2 giờ", "1 tuần")
        """
        if minutes < 60:
            return f"{minutes} phút"
        elif minutes < 1440:  # Less than 1 day
            hours = minutes // 60
            return f"{hours} giờ"
        elif minutes < 10080:  # Less than 1 week
            days = minutes // 1440
            return f"{days} ngày"
        elif minutes < 43200:  # Less than 1 month
            weeks = minutes // 10080
            return f"{weeks} tuần"
        else:
            months = minutes // 43200
            return f"{months} tháng"
    
    def _on_hover_enter(self, event):
        """Handle mouse enter - lighten background"""
        self.configure(fg_color=("#d8d8d8", "#353535"))
    
    def _on_hover_leave(self, event):
        """Handle mouse leave - restore background"""
        self.configure(fg_color=("#e8e8e8", "#2b2b2b"))
    
    def update_data(self, new_data):
        """
        Update card with new event data (re-render)
        
        Args:
            new_data: New event dictionary
        """
        self.event_data = new_data
        
        # Clear and rebuild
        for widget in self.winfo_children():
            widget.destroy()
        
        self._create_widgets()
