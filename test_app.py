#!/usr/bin/env python3
"""
Test script for Nomination Email Sender - Secure Version
=======================================================

This script tests basic functionality without requiring user interaction.
"""

import sys
import os
import json
from pathlib import Path

def test_imports():
    """Test that all required modules can be imported"""
    try:
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
        print("✅ All required modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_config_loading():
    """Test configuration file loading"""
    try:
        # Test if config.example.json exists and is valid JSON
        config_file = Path("config.example.json")
        if config_file.exists():
            with open(config_file, 'r') as f:
                config = json.load(f)
            print("✅ Configuration file loaded successfully")
            return True
        else:
            print("❌ Configuration example file not found")
            return False
    except Exception as e:
        print(f"❌ Configuration loading error: {e}")
        return False

def test_file_structure():
    """Test that all required files exist"""
    required_files = [
        "main.py",
        "email_app.py", 
        "app.py",
        "config.example.json",
        "README.md",
        ".gitignore",
        "LICENSE",
        "requirements.txt"
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    else:
        print("✅ All required files present")
        return True

def test_python_version():
    """Test Python version compatibility"""
    if sys.version_info >= (3, 7):
        print(f"✅ Python version {sys.version_info.major}.{sys.version_info.minor} is compatible")
        return True
    else:
        print(f"❌ Python version {sys.version_info.major}.{sys.version_info.minor} is too old. Requires 3.7+")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Nomination Email Sender - Secure Version")
    print("=" * 60)
    
    tests = [
        ("Python Version", test_python_version),
        ("File Structure", test_file_structure),
        ("Module Imports", test_imports),
        ("Configuration Loading", test_config_loading),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testing: {test_name}")
        if test_func():
            passed += 1
        else:
            print(f"   Test failed: {test_name}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The application is ready to use.")
        print("\n📝 Next steps:")
        print("1. Copy config.example.json to config.json")
        print("2. Customize the configuration with your settings")
        print("3. Run: python app.py")
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
