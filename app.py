#!/usr/bin/env python3
"""
Nomination Email Sender - Secure Version
========================================

A secure desktop application for sending nomination emails to airline partners.
This version includes secure credential handling and proper configuration management.

Author: Bilal Ahmed
Version: 2.0.0
"""

import sys
import os
from email_app import EmailApp

def main():
    """Main entry point for the application"""
    try:
        app = EmailApp()
        app.mainloop()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
