import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog
import json
import os
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from collections import defaultdict
import io
import csv
import base64
import time
import getpass
from pathlib import Path

# Get the application's base directory
if getattr(sys, 'frozen', False):
    # If the application is run as a bundle (exe)
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # If the application is run as a script
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG_FILE = os.path.join(BASE_DIR, 'config.json')
DEFAULT_CONFIG_FILE = os.path.join(BASE_DIR, 'config.example.json')
LOGO_FILE = os.path.join(BASE_DIR, 'logo.png')
HEADER_ORDER = ['PREFIX', 'MASTER', 'FLIGHT', 'STATUS', 'Arrival DATE', 'PICKUP DATE', 'SLAC']
COLUMNS_TO_INCLUDE = ['PREFIX', 'MASTER', 'FLIGHT', 'Arrival DATE', 'SLAC']

class ModernTheme:
    """Custom theme colors and styles"""
    BG_COLOR = "#f0f0f0"
    ACCENT_COLOR = "#2196F3"
    SUCCESS_COLOR = "#4CAF50"
    WARNING_COLOR = "#FFC107"
    ERROR_COLOR = "#F44336"
    TEXT_COLOR = "#333333"
    HEADER_BG = "#E3F2FD"
    TABLE_HEADER_BG = "#BBDEFB"
    TABLE_ROW_BG = "#FFFFFF"
    TABLE_ALT_ROW_BG = "#F5F5F5"

class SecureCredentialDialog(simpledialog.Dialog):
    """Secure credential input dialog that doesn't store credentials in plain text"""
    
    def __init__(self, parent):
        self.email = None
        self.password = None
        super().__init__(parent, "Email Credentials")
    
    def body(self, master):
        """Create the dialog body"""
        # Email input
        ttk.Label(master, text="Email Address:", padding=5).pack(fill=tk.X, padx=10, pady=(10,0))
        self.email_entry = ttk.Entry(master, width=40)
        self.email_entry.pack(fill=tk.X, padx=10, pady=(0,10))
        
        # Password input (masked)
        ttk.Label(master, text="Password:", padding=5).pack(fill=tk.X, padx=10)
        self.password_entry = ttk.Entry(master, width=40, show="*")
        self.password_entry.pack(fill=tk.X, padx=10, pady=(0,10))
        
        # Focus on email entry
        self.email_entry.focus()
        return self.email_entry

    def apply(self):
        """Get the entered credentials"""
        self.email = self.email_entry.get().strip()
        self.password = self.password_entry.get()
        
        if not self.email or not self.password:
            messagebox.showerror("Error", "Both email and password are required!")
            return
        
        # Basic email validation
        if '@' not in self.email or '.' not in self.email:
            messagebox.showerror("Error", "Please enter a valid email address!")
            return

class ConfigManager(tk.Toplevel):
    def __init__(self, parent, config):
        super().__init__(parent)
        self.title("Configuration Manager")
        self.config = config
        self.parent = parent
        
        # Set window size and position
        window_width = 1000
        window_height = 800
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Make window non-resizable
        self.resizable(False, False)
        
        # Configure style
        style = ttk.Style()
        style.configure("Treeview", 
                       background=ModernTheme.TABLE_ROW_BG,
                       fieldbackground=ModernTheme.TABLE_ROW_BG,
                       foreground=ModernTheme.TEXT_COLOR)
        style.configure("Treeview.Heading", 
                       background=ModernTheme.TABLE_HEADER_BG,
                       foreground=ModernTheme.TEXT_COLOR,
                       font=('Helvetica', 10, 'bold'))
        
        # Main container with fixed padding
        main_container = ttk.Frame(self, padding="20")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_container)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        prefix_flight_tab = ttk.Frame(notebook)
        firms_tab = ttk.Frame(notebook)
        
        notebook.add(prefix_flight_tab, text="Prefixes & Flight Rules")
        notebook.add(firms_tab, text="FIRMS Codes")
        
        # Prefix Section in combined tab
        prefix_frame = ttk.LabelFrame(prefix_flight_tab, text="Prefixes", padding="10")
        prefix_frame.pack(fill=tk.X, expand=False, padx=10, pady=(10,5))
        
        # Create a fixed container for the prefix tree and scrollbar
        prefix_container = ttk.Frame(prefix_frame)
        prefix_container.pack(fill=tk.X, expand=True, pady=(0, 10))
        
        self.prefix_tree = ttk.Treeview(prefix_container, columns=("Type",), height=8)
        self.prefix_tree.heading("#0", text="Prefix")
        self.prefix_tree.heading("Type", text="Type")
        self.prefix_tree.column("#0", width=150, minwidth=150)
        self.prefix_tree.column("Type", width=100, minwidth=100)
        self.prefix_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar for prefix tree
        prefix_scroll = ttk.Scrollbar(prefix_container, orient="vertical", command=self.prefix_tree.yview)
        prefix_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.prefix_tree.configure(yscrollcommand=prefix_scroll.set)
        
        # Prefix buttons in a fixed frame
        prefix_btn_frame = ttk.Frame(prefix_frame)
        prefix_btn_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Style for buttons
        style.configure("Config.TButton", 
                       padding=5,
                       font=('Helvetica', 10))
        
        ttk.Button(prefix_btn_frame, 
                  text="Add Normal", 
                  command=lambda: self.edit_prefix('normal'),
                  style="Config.TButton",
                  width=15).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(prefix_btn_frame, 
                  text="Add Special", 
                  command=lambda: self.edit_prefix('special'),
                  style="Config.TButton",
                  width=15).pack(side=tk.LEFT, padx=2)
        
        self.edit_prefix_btn = ttk.Button(prefix_btn_frame, 
                                        text="Edit", 
                                        state=tk.DISABLED,
                                        command=self.edit_selected_prefix,
                                        style="Config.TButton",
                                        width=15)
        self.edit_prefix_btn.pack(side=tk.LEFT, padx=2)
        
        self.delete_prefix_btn = ttk.Button(prefix_btn_frame, 
                                          text="Delete", 
                                          state=tk.DISABLED,
                                          command=self.delete_selected_prefix,
                                          style="Config.TButton",
                                          width=15)
        self.delete_prefix_btn.pack(side=tk.LEFT, padx=2)
        
        # Flight Rules Section in combined tab
        flight_frame = ttk.LabelFrame(prefix_flight_tab, text="Flight Rules", padding="10")
        flight_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5,10))
        
        # Create a fixed container for the flight tree and scrollbar
        flight_container = ttk.Frame(flight_frame)
        flight_container.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.flight_tree = ttk.Treeview(flight_container, columns=("Emails",), height=8)
        self.flight_tree.heading("#0", text="Flight/Rule")
        self.flight_tree.heading("Emails", text="Emails")
        self.flight_tree.column("#0", width=200, minwidth=200)
        self.flight_tree.column("Emails", width=300, minwidth=300)
        self.flight_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar for flight tree
        flight_scroll = ttk.Scrollbar(flight_container, orient="vertical", command=self.flight_tree.yview)
        flight_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.flight_tree.configure(yscrollcommand=flight_scroll.set)
        
        # Flight buttons in a fixed frame
        flight_btn_frame = ttk.Frame(flight_frame)
        flight_btn_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.add_flight_btn = ttk.Button(flight_btn_frame, 
                                       text="Add Flight Rule", 
                                       state=tk.DISABLED,
                                       command=self.edit_flight_rule,
                                       style="Config.TButton",
                                       width=20)
        self.add_flight_btn.pack(side=tk.LEFT, padx=2)
        
        self.edit_flight_btn = ttk.Button(flight_btn_frame, 
                                        text="Edit Rule", 
                                        state=tk.DISABLED,
                                        command=self.edit_selected_flight_rule,
                                        style="Config.TButton",
                                        width=20)
        self.edit_flight_btn.pack(side=tk.LEFT, padx=2)
        
        self.delete_flight_btn = ttk.Button(flight_btn_frame, 
                                          text="Delete Rule", 
                                          state=tk.DISABLED,
                                          command=self.delete_selected_flight_rule,
                                          style="Config.TButton",
                                          width=20)
        self.delete_flight_btn.pack(side=tk.LEFT, padx=2)
        
        # FIRMS Codes Tab Content
        firms_frame = ttk.LabelFrame(firms_tab, text="FIRMS Codes", padding="10")
        firms_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create a fixed container for the tree and scrollbar
        firms_container = ttk.Frame(firms_frame)
        firms_container.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.firms_tree = ttk.Treeview(firms_container, columns=("Description",), height=15)
        self.firms_tree.heading("#0", text="FIRMS Code")
        self.firms_tree.heading("Description", text="Description")
        self.firms_tree.column("#0", width=150, minwidth=150)
        self.firms_tree.column("Description", width=300, minwidth=300)
        self.firms_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar for firms tree
        firms_scroll = ttk.Scrollbar(firms_container, orient="vertical", command=self.firms_tree.yview)
        firms_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.firms_tree.configure(yscrollcommand=firms_scroll.set)
        
        # FIRMS buttons in a fixed frame
        firms_btn_frame = ttk.Frame(firms_frame)
        firms_btn_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(firms_btn_frame, 
                  text="Add FIRMS Code", 
                  command=self.edit_firms_code,
                  style="Config.TButton",
                  width=20).pack(side=tk.LEFT, padx=2)
        
        self.edit_firms_btn = ttk.Button(firms_btn_frame, 
                                       text="Edit", 
                                       state=tk.DISABLED,
                                       command=self.edit_selected_firms_code,
                                       style="Config.TButton",
                                       width=20)
        self.edit_firms_btn.pack(side=tk.LEFT, padx=2)
        
        self.delete_firms_btn = ttk.Button(firms_btn_frame, 
                                         text="Delete", 
                                         state=tk.DISABLED,
                                         command=self.delete_selected_firms_code,
                                         style="Config.TButton",
                                         width=20)
        self.delete_firms_btn.pack(side=tk.LEFT, padx=2)
        
        # Bind events
        self.prefix_tree.bind("<<TreeviewSelect>>", self.on_prefix_select)
        self.flight_tree.bind("<<TreeviewSelect>>", self.on_flight_select)
        self.firms_tree.bind("<<TreeviewSelect>>", self.on_firms_select)
        
        # Initialize data
        self.populate_prefixes()
        self.populate_firms_codes()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def populate_prefixes(self):
        """Populate the prefixes tree"""
        # Clear existing items
        for i in self.prefix_tree.get_children():
            self.prefix_tree.delete(i)
        
        # Add each prefix to the tree
        for prefix, details in sorted(self.config.items()):
            if prefix != 'firms_codes':  # Skip firms_codes entry
                self.prefix_tree.insert("", "end", iid=prefix, text=prefix, values=(details.get('type', ''),))

    def on_prefix_select(self, event=None):
        """Handle prefix selection"""
        selected = self.prefix_tree.selection()
        if not selected:
            self.edit_prefix_btn.config(state=tk.DISABLED)
            self.delete_prefix_btn.config(state=tk.DISABLED)
            self.add_flight_btn.config(state=tk.DISABLED)
            # Clear flight tree
            for i in self.flight_tree.get_children():
                self.flight_tree.delete(i)
            return
        
        selected_prefix = selected[0]
        self.edit_prefix_btn.config(state=tk.NORMAL)
        self.delete_prefix_btn.config(state=tk.NORMAL)
        
        # Populate flights for selected prefix
        self.populate_flights(selected_prefix)

    def populate_flights(self, prefix):
        """Populate the flights tree for a selected prefix"""
        # Clear existing items
        for i in self.flight_tree.get_children():
            self.flight_tree.delete(i)
        
        # Get prefix details
        details = self.config.get(prefix, {})
        if details.get('type') == 'special':
            self.add_flight_btn.config(state=tk.NORMAL)
            for flight_rule, emails in sorted(details.get('flights', {}).items()):
                self.flight_tree.insert("", "end", iid=flight_rule, text=flight_rule, values=(", ".join(emails),))
        else:
            self.add_flight_btn.config(state=tk.DISABLED)

    def on_flight_select(self, event=None):
        """Handle flight rule selection"""
        selected = self.flight_tree.selection()
        self.edit_flight_btn.config(state=tk.NORMAL if selected else tk.DISABLED)
        self.delete_flight_btn.config(state=tk.NORMAL if selected else tk.DISABLED)

    def edit_prefix(self, p_type, prefix_to_edit=None):
        """Edit or add a prefix with previous data shown if editing"""
        # Get previous data if editing
        prev_prefix = prefix_to_edit
        prev_emails = []
        prev_use_special_subject = False
        if prefix_to_edit and prefix_to_edit in self.config:
            if self.config[prefix_to_edit]['type'] == 'normal':
                prev_emails = self.config[prefix_to_edit]['emails']
            else:  # special
                prev_emails = self.config[prefix_to_edit]['flights'].get('DEFAULT', [])
            prev_use_special_subject = self.config[prefix_to_edit].get('use_special_subject', False)

        # Create custom dialog
        dialog = tk.Toplevel(self)
        dialog.title("Edit Prefix")
        dialog.geometry("400x300")
        dialog.transient(self)
        dialog.grab_set()

        # Center the dialog
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - dialog.winfo_width()) // 2
        y = self.winfo_y() + (self.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")

        # Create and pack widgets
        ttk.Label(dialog, text="Prefix Number:", padding=5).pack(fill=tk.X, padx=10, pady=(10,0))
        prefix_entry = ttk.Entry(dialog, width=40)
        prefix_entry.pack(fill=tk.X, padx=10, pady=(0,10))
        if prev_prefix:
            prefix_entry.insert(0, prev_prefix)

        ttk.Label(dialog, text="Emails (comma-separated):", padding=5).pack(fill=tk.X, padx=10)
        email_text = scrolledtext.ScrolledText(dialog, height=5, width=40)
        email_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0,10))
        if prev_emails:
            email_text.insert("1.0", ", ".join(prev_emails))

        # Add checkbox for special subject format
        use_special_subject_var = tk.BooleanVar(value=prev_use_special_subject)
        ttk.Checkbutton(dialog, 
                       text="Use Special Subject Format (NOMINATION REQUEST prefix-master)", 
                       variable=use_special_subject_var).pack(fill=tk.X, padx=10, pady=(0,10))

        def save():
            prefix = prefix_entry.get().strip().upper()
            emails = [e.strip() for e in email_text.get("1.0", tk.END).strip().split(",") if e.strip()]
            use_special_subject = use_special_subject_var.get()
            
            if not prefix or not emails:
                messagebox.showerror("Error", "Both prefix and emails are required!", parent=dialog)
                return

            if prefix_to_edit and prefix_to_edit != prefix:
                del self.config[prefix_to_edit]

            if p_type == 'normal':
                self.config[prefix] = {
                    'type': 'normal', 
                    'emails': emails,
                    'use_special_subject': use_special_subject
                }
            else:  # special
                self.config[prefix] = {
                    'type': 'special', 
                    'flights': {'DEFAULT': emails},
                    'use_special_subject': use_special_subject
                }
            
            self.populate_prefixes()
            self.parent.save_config()
            dialog.destroy()

        # Buttons frame
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(btn_frame, text="Save", command=save, width=15).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy, width=15).pack(side=tk.RIGHT, padx=5)

    def edit_selected_prefix(self):
        """Edit the selected prefix"""
        selected = self.prefix_tree.selection()[0]
        p_type = self.config[selected]['type']
        self.edit_prefix(p_type, prefix_to_edit=selected)

    def delete_selected_prefix(self):
        """Delete the selected prefix"""
        selected = self.prefix_tree.selection()[0]
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete prefix '{selected}'?", parent=self):
            del self.config[selected]
            self.populate_prefixes()
            self.parent.save_config()

    def edit_flight_rule(self, rule_to_edit=None):
        """Edit or add a flight rule"""
        selected_prefix = self.prefix_tree.selection()[0]
        
        # Get previous data if editing
        prev_rule = rule_to_edit
        prev_emails = []
        if rule_to_edit and selected_prefix in self.config:
            prev_emails = self.config[selected_prefix]['flights'].get(rule_to_edit, [])

        # Create custom dialog
        dialog = tk.Toplevel(self)
        dialog.title("Edit Flight Rule")
        dialog.geometry("400x250")
        dialog.transient(self)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - dialog.winfo_width()) // 2
        y = self.winfo_y() + (self.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")

        # Create and pack widgets
        ttk.Label(dialog, text="Flight Number (or 'DEFAULT'):", padding=5).pack(fill=tk.X, padx=10, pady=(10,0))
        rule_entry = ttk.Entry(dialog, width=40)
        rule_entry.pack(fill=tk.X, padx=10, pady=(0,10))
        if prev_rule:
            rule_entry.insert(0, prev_rule)

        ttk.Label(dialog, text="Emails (comma-separated):", padding=5).pack(fill=tk.X, padx=10)
        email_text = scrolledtext.ScrolledText(dialog, height=5, width=40)
        email_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0,10))
        if prev_emails:
            email_text.insert("1.0", ", ".join(prev_emails))

        def save():
            rule = rule_entry.get().strip()
            emails = [e.strip() for e in email_text.get("1.0", tk.END).strip().split(",") if e.strip()]
            
            if not rule or not emails:
                messagebox.showerror("Error", "Both flight rule and emails are required!", parent=dialog)
                return

            if rule_to_edit and rule_to_edit != rule:
                del self.config[selected_prefix]['flights'][rule_to_edit]
            
            self.config[selected_prefix]['flights'][rule] = emails
            self.populate_flights(selected_prefix)
            self.parent.save_config()
            dialog.destroy()

        # Buttons frame
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(btn_frame, text="Save", command=save, width=15).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy, width=15).pack(side=tk.RIGHT, padx=5)

    def edit_selected_flight_rule(self):
        """Edit the selected flight rule"""
        selected_rule = self.flight_tree.selection()[0]
        self.edit_flight_rule(rule_to_edit=selected_rule)

    def delete_selected_flight_rule(self):
        """Delete the selected flight rule"""
        selected_prefix = self.prefix_tree.selection()[0]
        selected_rule = self.flight_tree.selection()[0]
        if messagebox.askyesno("Confirm Delete", f"Delete rule '{selected_rule}' for prefix '{selected_prefix}'?", parent=self):
            del self.config[selected_prefix]['flights'][selected_rule]
            self.populate_flights(selected_prefix)
            self.parent.save_config()

    def populate_firms_codes(self):
        """Populate the FIRMS codes tree"""
        # Clear existing items
        for i in self.firms_tree.get_children():
            self.firms_tree.delete(i)
        
        # Get FIRMS codes from config
        firms_codes = self.config.get('firms_codes', {})
        
        # Add each FIRMS code to the tree
        for code, details in sorted(firms_codes.items()):
            self.firms_tree.insert("", "end", iid=code, text=code, values=(details.get('description', ''),))
        
        # Update parent's FIRMS code display
        if hasattr(self.parent, 'refresh_firms_codes'):
            self.parent.refresh_firms_codes()

    def on_firms_select(self, event=None):
        """Handle FIRMS code selection"""
        selected = self.firms_tree.selection()
        self.edit_firms_btn.config(state=tk.NORMAL if selected else tk.DISABLED)
        self.delete_firms_btn.config(state=tk.NORMAL if selected else tk.DISABLED)

    def edit_firms_code(self, code_to_edit=None):
        """Edit or add a FIRMS code"""
        # Get previous data if editing
        prev_code = code_to_edit
        prev_description = ""
        if code_to_edit and 'firms_codes' in self.config:
            prev_description = self.config['firms_codes'].get(code_to_edit, {}).get('description', '')

        # Create custom dialog
        dialog = tk.Toplevel(self)
        dialog.title("Edit FIRMS Code")
        dialog.geometry("400x200")
        dialog.transient(self)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - dialog.winfo_width()) // 2
        y = self.winfo_y() + (self.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")

        # Create and pack widgets
        ttk.Label(dialog, text="FIRMS Code:", padding=5).pack(fill=tk.X, padx=10, pady=(10,0))
        code_entry = ttk.Entry(dialog, width=40)
        code_entry.pack(fill=tk.X, padx=10, pady=(0,10))
        if prev_code:
            code_entry.insert(0, prev_code)

        ttk.Label(dialog, text="Description:", padding=5).pack(fill=tk.X, padx=10)
        desc_entry = ttk.Entry(dialog, width=40)
        desc_entry.pack(fill=tk.X, padx=10, pady=(0,10))
        if prev_description:
            desc_entry.insert(0, prev_description)

        def save():
            code = code_entry.get().strip().upper()
            description = desc_entry.get().strip()
            
            if not code:
                messagebox.showerror("Error", "FIRMS code is required!", parent=dialog)
                return

            if 'firms_codes' not in self.config:
                self.config['firms_codes'] = {}

            if code_to_edit and code_to_edit != code:
                del self.config['firms_codes'][code_to_edit]

            self.config['firms_codes'][code] = {'description': description}
            self.populate_firms_codes()  # This will also update the parent's display
            self.parent.save_config()
            dialog.destroy()

        # Buttons frame
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(btn_frame, text="Save", command=save, width=15).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy, width=15).pack(side=tk.RIGHT, padx=5)

    def edit_selected_firms_code(self):
        """Edit the selected FIRMS code"""
        selected = self.firms_tree.selection()[0]
        self.edit_firms_code(code_to_edit=selected)

    def delete_selected_firms_code(self):
        """Delete the selected FIRMS code"""
        selected = self.firms_tree.selection()[0]
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete FIRMS code '{selected}'?", parent=self):
            del self.config['firms_codes'][selected]
            self.populate_firms_codes()  # This will also update the parent's display
            self.parent.save_config()

    def on_close(self):
        """Handle window close"""
        self.parent.config_window = None
        self.destroy()
