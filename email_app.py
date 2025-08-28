import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
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
from main import ModernTheme, SecureCredentialDialog, ConfigManager

class EmailApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.credentials = None  # Will be set by secure credential dialog
        self.config = self.load_config()
        self.processed_groups = {}
        self.config_window = None
        self.selected_format = tk.StringVar()  # Will be set after loading FIRMS codes
        self.format_frame = None  # Store reference to format frame
        self.setup_main_window()
        
        # Load logo for email
        self.logo_data = self.load_logo()
        
        # Request credentials on startup
        self.request_credentials()

    def request_credentials(self):
        """Request email credentials securely"""
        dialog = SecureCredentialDialog(self)
        if dialog.email and dialog.password:
            self.credentials = (dialog.email, dialog.password)
            self.update_status("Credentials set successfully", "success")
        else:
            self.update_status("Credentials required to send emails", "warning")

    def get_credentials(self):
        """Get credentials, request if not set"""
        if not self.credentials:
            self.request_credentials()
        return self.credentials

    def load_config(self):
        """Load configuration from JSON file, create default if not exists"""
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
            else:
                # Try to load default config from file
                if os.path.exists(DEFAULT_CONFIG_FILE):
                    with open(DEFAULT_CONFIG_FILE, 'r') as f:
                        default_config = json.load(f)
                else:
                    # If no default config file exists, create an empty config
                    default_config = {}
                
                # Save the default config as the new config file
                with open(CONFIG_FILE, 'w') as f:
                    json.dump(default_config, f, indent=4)
                return default_config
        except Exception as e:
            messagebox.showerror("Config Error", f"Error loading configuration: {e}")
            return {}
    
    def save_config(self):
        """Save configuration to file"""
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config, f, indent=4)
        self.log("Configuration saved to config.json")
    
    def open_config_manager(self):
        """Open configuration manager window"""
        if self.config_window:
            self.config_window.lift()
        else:
            self.config_window = ConfigManager(self, self.config)

    def update_status(self, message, status_type="info"):
        """Update the status button with message and appropriate emoji"""
        emojis = {
            "info": "ℹ️",
            "success": "✅",
            "error": "❌",
            "warning": "⚠️",
            "processing": "⏳",
            "email": "📧"
        }
        emoji = emojis.get(status_type, "ℹ️")
        self.status_button.config(text=f"{emoji} {message}")

    def setup_main_window(self):
        """Setup the main application window"""
        self.title("Nomination Email Sender - Secure Version")
        self.geometry("800x800")
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TButton", 
                       padding=6, 
                       relief="flat", 
                       font=('Helvetica', 10, 'bold'),
                       background=ModernTheme.ACCENT_COLOR)
        style.configure("TLabel", 
                       font=('Helvetica', 11),
                       background=ModernTheme.BG_COLOR)
        style.configure("Header.TLabel", 
                       font=('Helvetica', 12, 'bold'),
                       background=ModernTheme.HEADER_BG)
        
        # Main container with padding
        main_container = ttk.Frame(self, padding="10")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Data input section
        input_frame = ttk.LabelFrame(main_container, 
                                   text="1. Paste Raw Data Below (PREFIX', 'MASTER', 'FLIGHT', 'STATUS', 'Arrival DATE', 'PICKUP DATE', 'SLAC)", 
                                   padding="5")
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.input_text = scrolledtext.ScrolledText(
            input_frame, 
            height=10, 
            width=80,
            font=("Courier New", 10),
            relief=tk.SOLID,
            borderwidth=1
        )
        self.input_text.pack(fill=tk.BOTH, expand=True, pady=5)

        # Options section
        options_frame = ttk.LabelFrame(main_container, text="Options", padding="5")
        options_frame.pack(fill=tk.X, pady=(0, 10))

        # Create a frame for options with better organization
        options_container = ttk.Frame(options_frame)
        options_container.pack(fill=tk.X, pady=5)

        # Left side options
        left_options = ttk.Frame(options_container)
        left_options.pack(side=tk.LEFT, padx=10)

        # Email format selection with improved styling
        format_label = ttk.Label(left_options, text="Email FIRMS Code:", font=('Helvetica', 10, 'bold'))
        format_label.pack(side=tk.LEFT, padx=(0, 10))

        # Style for radio buttons
        style.configure("TRadiobutton", 
                       font=('Helvetica', 10),
                       background=ModernTheme.BG_COLOR)

        # Create format frame for FIRMS code radio buttons
        self.format_frame = ttk.Frame(left_options)
        self.format_frame.pack(side=tk.LEFT)

        # Initial population of FIRMS codes
        self.refresh_firms_codes()

        # Middle options - Process and Clear buttons
        middle_options = ttk.Frame(options_container)
        middle_options.pack(side=tk.LEFT, expand=True, padx=10)
        
        # Create a frame for the middle buttons
        middle_buttons = ttk.Frame(middle_options)
        middle_buttons.pack(expand=True)
        
        self.process_button = ttk.Button(
            middle_buttons,
            text="Process & Preview Data",
            command=self.process_and_preview,
            width=20
        )
        self.process_button.pack(side=tk.LEFT, padx=5)
        
        self.clear_button = ttk.Button(
            middle_buttons,
            text="Clear Data",
            command=self.clear_data,
            width=15
        )
        self.clear_button.pack(side=tk.LEFT, padx=5)

        # Right side options
        right_options = ttk.Frame(options_container)
        right_options.pack(side=tk.RIGHT, padx=10)

        config_button = ttk.Button(right_options, 
                                 text="⚙️ Manage Configurations", 
                                 command=self.open_config_manager)
        config_button.pack(side=tk.RIGHT, padx=5)
        
        # Preview section
        preview_frame = ttk.LabelFrame(main_container, 
                                     text="2. Verify Grouped Data", 
                                     padding="5")
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.preview_text = scrolledtext.ScrolledText(
            preview_frame, 
            height=15, 
            width=80,
            font=("Courier New", 10),
            relief=tk.SOLID,
            borderwidth=1
        )
        self.preview_text.config(state=tk.DISABLED)
        self.preview_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Action section
        action_frame = ttk.Frame(main_container, padding="10")
        action_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Create a container for buttons with better spacing
        button_container = ttk.Frame(action_frame)
        button_container.pack(expand=True)
        
        # Add buttons with fixed width and proper spacing
        self.send_button = ttk.Button(
            button_container,
            text="Send Emails",
            command=self.send_emails_command,
            state=tk.DISABLED,
            width=20
        )
        self.send_button.pack(side=tk.LEFT, padx=5)
        
        # Status button with increased width
        self.status_button = ttk.Button(
            button_container,
            text="ℹ️ Ready",
            width=30  # Increased width for better visibility
        )
        self.status_button.pack(side=tk.LEFT, padx=5)
        
        # Add a horizontal separator
        ttk.Separator(main_container, orient='horizontal').pack(fill=tk.X, padx=20, pady=5)

        # Bind paste event for Mac
        self.input_text.bind('<<Paste>>', self.handle_paste)

    def handle_paste(self, event):
        """Handle paste event for Windows"""
        try:
            # Get clipboard content
            clipboard_content = self.clipboard_get()
            
            # Clear the current selection if any
            try:
                self.input_text.delete("sel.first", "sel.last")
            except tk.TclError:
                pass
            
            # Insert the clipboard content at the current cursor position
            self.input_text.insert("insert", clipboard_content)
            
            # Prevent the default paste behavior
            return "break"
        except tk.TclError:
            # If clipboard is empty or contains non-text data
            return "break"

    def log(self, message):
        """Log message to console"""
        print(f"[LOG] {message}")

    def process_and_preview(self):
        """Process input data and show preview"""
        self.processed_groups.clear()
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete("1.0", tk.END)
        self.send_button.config(state=tk.DISABLED)
        
        input_data = self.input_text.get("1.0", tk.END)
        if not input_data.strip():
            self.update_status("Please paste data first", "warning")
            return

        self.update_status("Processing data...", "processing")
        col_map = {col_name: i for i, col_name in enumerate(HEADER_ORDER)}
        temp_groups = defaultdict(list)
        
        try:
            reader = csv.reader(io.StringIO(input_data), delimiter='\t')
            for i, row in enumerate(reader):
                if len(row) < len(HEADER_ORDER):
                    self.update_status(f"Row {i+1} has incorrect format", "error")
                    return
                prefix = row[col_map['PREFIX']].strip()
                if not prefix: continue
                
                group_key = prefix
                config = self.config.get(prefix, {})
                if config.get('type') == 'special':
                    flight = row[col_map['FLIGHT']].strip()
                    # Check if any flight rule matches the flight number
                    matched_rule = None
                    for rule in config['flights'].keys():
                        if rule != 'DEFAULT' and rule in flight:
                            matched_rule = rule
                            break
                    group_key = f"{prefix}_FLIGHT_{matched_rule}" if matched_rule else f"{prefix}_DEFAULT"
                temp_groups[group_key].append(row)
        except Exception as e:
            self.update_status(f"Error: {str(e)}", "error")
            return
        
        self.processed_groups = temp_groups
        self.display_preview()
        self.update_status(f"Found {len(self.processed_groups)} groups", "success")
        self.send_button.config(state=tk.NORMAL)

    def display_preview(self):
        """Display preview of processed data"""
        preview_content = ""
        for group_key, rows in self.processed_groups.items():
            recipients, subject = self.get_email_details(group_key)
            preview_content += f"{'='*80}\nGROUP: {subject}\nTO: {', '.join(recipients)}\n{'-'*80}\n"
            preview_content += "\t".join(COLUMNS_TO_INCLUDE) + "\n\n"
            for row in rows:
                filtered_row = [row[i] for i in [HEADER_ORDER.index(col) for col in COLUMNS_TO_INCLUDE]]
                preview_content += "\t".join(filtered_row) + "\n"
            preview_content += "\n"
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.insert("1.0", preview_content)
        self.preview_text.config(state=tk.DISABLED)

    def get_email_details(self, group_key):
        """Get email recipients and subject for a group"""
        prefix = group_key.split('_')[0]
        config = self.config.get(prefix, {})
        
        # Get FIRMS code from selected format
        firms_code = self.selected_format.get()
        
        # Create the subject based on configuration
        if config.get('use_special_subject', False):
            # Get the rows for this group
            rows = self.processed_groups.get(group_key, [])
            if rows:
                # Get prefix and master values from the rows
                col_map = {col_name: i for i, col_name in enumerate(HEADER_ORDER)}
                nominations = []
                for row in rows:
                    prefix_val = row[col_map['PREFIX']].strip()
                    master_val = row[col_map['MASTER']].strip()
                    if prefix_val and master_val:
                        nominations.append(f"{prefix_val}-{master_val}")
                
                # Create the subject with all nominations
                if nominations:
                    subject = f"NOMINATION REQUEST {','.join(nominations)}"
                else:
                    subject = f"Request for AWB {prefix} Nomination - FIRMS Code {firms_code}"
            else:
                subject = f"Request for AWB {prefix} Nomination - FIRMS Code {firms_code}"
        else:
            subject = f"Request for AWB {prefix} Nomination - FIRMS Code {firms_code}"
        
        if config.get('type') == 'normal':
            return config.get('emails', []), subject
        elif config.get('type') == 'special':
            if "DEFAULT" in group_key:
                return config['flights'].get('DEFAULT', []), subject
            else:
                flight = group_key.split('_')[2]
                return config['flights'].get(flight, []), subject
        return ["example@company.com"], "Nomination Email has not been sent"

    def send_emails_command(self):
        """Send emails command with progress tracking"""
        if not self.processed_groups:
            self.update_status("No data to send", "error")
            return

        # Check credentials
        if not self.credentials:
            self.update_status("Please set email credentials first", "error")
            self.request_credentials()
            return

        # Create progress window
        progress_window = tk.Toplevel(self)
        progress_window.title("Sending Emails")
        progress_window.geometry("400x150")
        progress_window.transient(self)
        progress_window.grab_set()
        
        # Center the progress window
        progress_window.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - progress_window.winfo_width()) // 2
        y = self.winfo_y() + (self.winfo_height() - progress_window.winfo_height()) // 2
        progress_window.geometry(f"+{x}+{y}")
        
        # Add progress label
        progress_label = ttk.Label(progress_window, text="Sending emails...", font=('Helvetica', 10))
        progress_label.pack(pady=(20,10))
        
        # Add progress bar
        progress_bar = ttk.Progressbar(progress_window, length=300, mode='determinate')
        progress_bar.pack(pady=10)
        
        # Add status label
        status_label = ttk.Label(progress_window, text="", font=('Helvetica', 9))
        status_label.pack(pady=10)
        
        # Update progress window
        progress_window.update()

        self.update_status("Starting to send emails...", "email")
        sent_count = 0
        failed_count = 0
        failed_groups = []
        
        total_groups = len(self.processed_groups)
        progress_bar['maximum'] = total_groups

        for i, (group_key, rows) in enumerate(self.processed_groups.items(), 1):
            recipients, subject = self.get_email_details(group_key)
            if not recipients:
                self.update_status(f"No recipients for {subject}", "warning")
                failed_count += 1
                failed_groups.append(f"{subject} (No recipients)")
                continue
            
            # Update progress
            progress_bar['value'] = i
            status_label.config(text=f"Sending email {i} of {total_groups}: {subject}")
            progress_window.update()
            
            html = self.build_html_table(subject, rows)
            try:
                self._send_email_smtp(recipients, subject, html)
                sent_count += 1
                self.update_status(f"✅ Sent: {subject}", "success")
            except Exception as e:
                failed_count += 1
                failed_groups.append(f"{subject} ({str(e)})")
                self.update_status(f"❌ Failed: {subject}", "error")
                continue

        # Close progress window
        progress_window.destroy()

        # Final status report
        if sent_count > 0 and failed_count == 0:
            self.update_status(f"✅ Successfully sent all {sent_count} emails", "success")
        elif sent_count > 0 and failed_count > 0:
            self.update_status(
                f"⚠️ Sent {sent_count} emails, {failed_count} failed. Check status for details.", 
                "warning"
            )
            # Show detailed error report
            error_details = "\nFailed emails:\n" + "\n".join(failed_groups)
            messagebox.showwarning(
                "Email Status Report",
                f"Successfully sent: {sent_count}\nFailed: {failed_count}\n{error_details}"
            )
        else:
            self.update_status("❌ Failed to send all emails", "error")
            # Show detailed error report
            error_details = "\nFailed emails:\n" + "\n".join(failed_groups)
            messagebox.showerror(
                "Email Status Report",
                f"Failed to send all {failed_count} emails.\n{error_details}"
            )

        self.send_button.config(state=tk.DISABLED)

    def load_logo(self):
        """Load and encode the logo for email use"""
        try:
            if os.path.exists(LOGO_FILE):
                with open(LOGO_FILE, 'rb') as f:
                    return base64.b64encode(f.read()).decode()
            return None
        except Exception as e:
            print(f"Error loading logo: {e}")
            return None

    def build_html_table(self, title, rows):
        """Build HTML email with centered logo and data"""
        col_map = {name: i for i, name in enumerate(HEADER_ORDER)}
        
        # Get FIRMS code from selected format
        firms_code = self.selected_format.get()
        
        # Start HTML with centered content
        html = """
        <html>
        <head>
            <style>
                body { 
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333333;
                }
                .container { 
                    max-width: 800px; 
                    margin: 0 auto; 
                    text-align: center;
                    padding: 20px;
                }
                .logo { 
                    max-width: 200px; 
                    margin: 20px auto;
                    display: block;
                }
                .email-content { 
                    text-align: left; 
                    margin: 30px 0;
                    font-size: 14px;
                }
                .greeting {
                    font-size: 16px;
                    font-weight: bold;
                    margin-bottom: 20px;
                }
                .main-text {
                    font-size: 14px;
                    margin-bottom: 20px;
                }
                .firms-code { 
                    font-weight: bold;
                    color: #FFBE04;
                    font-size: 15px;
                }
                table { 
                    width: 100%; 
                    border-collapse: collapse; 
                    margin: 30px auto;
                    text-align: center;
                    box-shadow: 0 2px 3px rgba(0,0,0,0.1);
                }
                th { 
                    background-color: #f2f2f2; 
                    color: #333333;
                    padding: 12px;
                    border: 1px solid #ddd;
                    font-size: 14px;
                }
                td { 
                    padding: 10px;
                    border: 1px solid #ddd;
                    font-size: 13px;
                }
                tr:nth-child(even) { 
                    background-color: #f8f9fa; 
                }
                tr:hover {
                    background-color: #f5f5f5;
                }
                .closing {
                    margin-top: 30px;
                    font-size: 14px;
                }
                .signature {
                    margin-top: 20px;
                    font-weight: bold;
                    color: #FFBE04;
                }
                .divider {
                    border-top: 1px solid #e0e0e0;
                    margin: 30px 0;
                }
                .best-regards {
                    color: #FFBE04;
                    font-weight: bold;
                }
                .company-info {
                    color: #FFBE04;
                    font-size: 13px;
                    line-height: 1.4;
                    margin-top: 10px;
                }
            </style>
        </head>
        <body>
            <div class="container">
        """
        
        # Add logo if available
        if self.logo_data:
            html += '<img src="cid:logo" class="logo" alt="Company Logo">'
        
        # Add email content based on whether it's an unconfigured group
        if title == "Nomination Email has not been sent":
            html += """
            <div class="email-content">
                <p class="greeting">Hi Team,</p>
                <p class="main-text">Please add the following prefixes in the system and resend the nominations again:</p>
            </div>
            """
        else:
            html += f"""
            <div class="email-content">
                <p class="greeting">Hi Team,</p>
                <p class="main-text">We kindly request the nomination of the master air waybills listed below to our FIRMS code, <span class="firms-code">{firms_code}</span>, with their respective SLAC details.</p>
            </div>
            """
        
        # Add table
        html += '<table>'
        html += '<tr><th>' + '</th><th>'.join(COLUMNS_TO_INCLUDE) + '</th></tr>'
        
        for row in rows:
            html += '<tr>' + ''.join([f'<td>{row[col_map[col]]}</td>' for col in COLUMNS_TO_INCLUDE]) + '</tr>'
        
        # Add closing content
        if title == "Nomination Email has not been sent":
            html += """
            </table>
            <div class="email-content">
                <div class="divider"></div>
                <p class="closing"><span class="best-regards">Best regards,</span><br><span class="signature">Bilal</span></p>
                <div class="company-info">
                    Fasttrack Express & Cargo Services<br>
                    182-08 149th Avenue,<br>
                    Springfield Gardens, NY 11413<br>
                    Toll Free: (888) 661-8857<br>
                    Fax: (718) 701-5886<br>
                    Email: csd@fasttrackexp.com, fasttrackexpressny@gmail.com<br>
                    Web: www.fasttrackexp.com
                </div>
            </div>
            """
        else:
            html += """
            </table>
            <div class="email-content">
                <div class="divider"></div>
                <p class="main-text">Please let us know if you require any further information.</p>
                <p class="main-text">Thank you for your assistance.</p>
                <p class="closing"><span class="best-regards">Best regards,</span><br><span class="signature">The FTE Team</span></p>
                <div class="company-info">
                    Fasttrack Express & Cargo Services<br>
                    182-08 149th Avenue,<br>
                    Springfield Gardens, NY 11413<br>
                    Toll Free: (888) 661-8857<br>
                    Fax: (718) 701-5886<br>
                    Email: csd@fasttrackexp.com, fasttrackexpressny@gmail.com<br>
                    Web: www.fasttrackexp.com
                </div>
            </div>
            """
        
        html += """
            </div>
        </body>
        </html>
        """
        return html

    def _send_email_smtp(self, recipients, subject, body_html):
        """Send email with improved error handling and retry logic"""
        max_retries = 3
        retry_delay = 5  # seconds
        
        for attempt in range(max_retries):
            try:
                sender_email, sender_password = self.credentials
                msg = MIMEMultipart('related')
                msg['From'] = sender_email
                msg['To'] = ", ".join(recipients)
                msg['Subject'] = subject

                # Create the HTML part
                html_part = MIMEMultipart('alternative')
                msg.attach(html_part)

                # Attach the HTML content
                html_part.attach(MIMEText(body_html, 'html'))

                # Attach the logo if available
                if self.logo_data:
                    try:
                        # Create the image part
                        image = MIMEImage(base64.b64decode(self.logo_data))
                        image.add_header('Content-ID', '<logo>')
                        msg.attach(image)
                    except Exception as e:
                        print(f"Warning: Error attaching logo: {e}")

                # Send email with timeout and retry logic
                try:
                    # Try different SMTP servers in order
                    smtp_servers = [
                        ('smtp.gmail.com', 587),
                        ('smtp.gmail.com', 465),
                        ('smtp.office365.com', 587)
                    ]
                    
                    last_error = None
                    for smtp_server, port in smtp_servers:
                        try:
                            print(f"Attempting to connect to {smtp_server}:{port}")
                            if port == 465:
                                server = smtplib.SMTP_SSL(smtp_server, port, timeout=30)
                            else:
                                server = smtplib.SMTP(smtp_server, port, timeout=30)
                                server.starttls()
                            
                            print("Connected to SMTP server, attempting login...")
                            server.login(sender_email, sender_password)
                            print("Login successful, sending email...")
                            server.sendmail(sender_email, recipients, msg.as_string())
                            server.quit()
                            print("Email sent successfully!")
                            return  # Success - exit the function
                        except Exception as e:
                            last_error = e
                            print(f"Failed to connect to {smtp_server}:{port} - {str(e)}")
                            continue
                    
                    # If we get here, all SMTP servers failed
                    raise last_error or Exception("All SMTP servers failed")
                    
                except smtplib.SMTPConnectError as e:
                    if attempt < max_retries - 1:
                        print(f"Connection attempt {attempt + 1} failed, retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                        continue
                    raise Exception(f"Failed to connect to SMTP server after {max_retries} attempts: {str(e)}")
                except smtplib.SMTPAuthenticationError:
                    raise Exception("SMTP Authentication failed. Please check your credentials.")
                except smtplib.SMTPException as e:
                    raise Exception(f"SMTP error occurred: {str(e)}")
                except Exception as e:
                    raise Exception(f"Failed to send email: {str(e)}")
                
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"Attempt {attempt + 1} failed, retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    continue
                raise Exception(f"Failed to send email after {max_retries} attempts: {str(e)}")

    def clear_data(self):
        """Clear all input and preview data"""
        self.input_text.delete("1.0", tk.END)
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete("1.0", tk.END)
        self.preview_text.config(state=tk.DISABLED)
        self.send_button.config(state=tk.DISABLED)
        self.processed_groups.clear()
        self.update_status("Data cleared", "info")

    def refresh_firms_codes(self):
        """Refresh the FIRMS code radio buttons"""
        if not self.format_frame:
            return
            
        # Clear existing radio buttons
        for widget in self.format_frame.winfo_children():
            widget.destroy()

        # Get FIRMS codes from config
        firms_codes = self.config.get('firms_codes', {})
        
        # Create radio buttons for each FIRMS code
        for code, details in sorted(firms_codes.items()):
            ttk.Radiobutton(self.format_frame, 
                          text=f"{code} ({details['description']})", 
                          variable=self.selected_format,
                          value=code,
                          style="TRadiobutton").pack(side=tk.LEFT, padx=5)

        # Set default selected format to first FIRMS code if none selected
        if not self.selected_format.get() and firms_codes:
            self.selected_format.set(next(iter(firms_codes)))
