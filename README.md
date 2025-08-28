# Nomination Email Sender - Secure Version

A secure desktop application for sending nomination emails to airline partners. This application helps automate the process of sending air waybill nomination requests to various airline partners based on prefix configurations.

## 🔒 Security Features

- **Secure Credential Handling**: Interactive credential input with password masking
- **Interactive Login**: Secure dialog for entering email credentials
- **Configuration Management**: Separate configuration files for easy customization
- **Input Validation**: Comprehensive validation for all user inputs

## 🚀 Features

- **Prefix-based Email Routing**: Configure different email recipients for different AWB prefixes
- **Flight-specific Rules**: Set up special routing rules for specific flight numbers
- **FIRMS Code Management**: Manage multiple FIRMS codes with descriptions
- **Email Templates**: Professional HTML email templates with company branding
- **Progress Tracking**: Real-time progress tracking for email sending
- **Error Handling**: Comprehensive error handling and retry logic
- **Configuration Manager**: GUI-based configuration management

## 📋 Requirements

- Python 3.7 or higher
- tkinter (usually included with Python)
- Standard library modules (no external dependencies)

## 🛠️ Installation

1. **Clone or download the repository**
   ```bash
   git clone <repository-url>
   cd Nomination_sender/secure-version
   ```

2. **Set up configuration**
   ```bash
   # Copy the example configuration
   cp config.example.json config.json
   ```

3. **Customize the configuration**
   - Edit `config.json` with your specific prefix and email configurations
   - Add your FIRMS codes
   - Configure email recipients for each prefix

4. **Add your company logo** (optional)
   - Place your logo as `logo.png` in the application directory
   - The logo will be automatically included in emails

## 🎯 Usage

### Starting the Application

```bash
python app.py
```

### First Time Setup

1. **Enter Email Credentials**: The application will prompt you to enter your email credentials securely
2. **Configure Prefixes**: Use the Configuration Manager to set up your AWB prefixes and email recipients
3. **Add FIRMS Codes**: Configure your FIRMS codes with descriptions

### Sending Nomination Emails

1. **Paste Raw Data**: Copy and paste your tab-separated data into the input field
   - Expected format: `PREFIX`, `MASTER`, `FLIGHT`, `STATUS`, `Arrival DATE`, `PICKUP DATE`, `SLAC`
   
2. **Select FIRMS Code**: Choose the appropriate FIRMS code for your nomination

3. **Process Data**: Click "Process & Preview Data" to group and preview the emails

4. **Review Preview**: Verify the grouped data and recipients

5. **Send Emails**: Click "Send Emails" to send the nomination requests

## ⚙️ Configuration

### Configuration File Structure

The `config.json` file contains:

```json
{
    "firms_codes": {
        "F762": {
            "description": "ZOOM"
        }
    },
    "297": {
        "type": "normal",
        "emails": ["email1@airline.com", "email2@airline.com"],
        "use_special_subject": false
    },
    "936": {
        "type": "special",
        "flights": {
            "DEFAULT": ["default@airline.com"],
            "FLIGHT123": ["flight123@airline.com"]
        },
        "use_special_subject": true
    }
}
```

### Configuration Types

#### Normal Prefix
- **Type**: `"normal"`
- **Emails**: List of email addresses for all flights
- **Use**: When all flights for a prefix go to the same recipients

#### Special Prefix
- **Type**: `"special"`
- **Flights**: Dictionary of flight rules with email lists
- **Use**: When different flights need different recipients

### Special Subject Format

When `use_special_subject` is `true`, the email subject will include the prefix and master numbers:
```
NOMINATION REQUEST 297-123456789, 297-987654321
```

## 🔧 Configuration Manager

Access the Configuration Manager by clicking the "⚙️ Manage Configurations" button.

### Features:
- **Prefix Management**: Add, edit, and delete prefixes
- **Flight Rules**: Configure flight-specific email routing
- **FIRMS Codes**: Manage FIRMS codes and descriptions
- **Real-time Updates**: Changes are saved immediately

## 📧 Email Templates

The application generates professional HTML emails with:
- Company logo (if provided)
- Professional styling
- Responsive design
- Clear data presentation
- Company contact information

## 🛡️ Security Considerations

### Credential Security
- Credentials are never stored on disk
- Passwords are masked in the input dialog
- Credentials are only held in memory during the session

### Data Privacy
- No data is sent to external servers (except email recipients)
- All processing is done locally
- Configuration files contain only email addresses (no passwords)

### Best Practices
- Use app-specific passwords for Gmail/Office 365
- Regularly update your email credentials
- Keep your configuration file secure
- Don't share your `config.json` file

## 🐛 Troubleshooting

### Common Issues

1. **SMTP Authentication Failed**
   - Check your email credentials
   - Ensure you're using app-specific passwords for Gmail
   - Verify your email provider's SMTP settings

2. **No Recipients Found**
   - Check your prefix configuration
   - Verify email addresses are correctly formatted
   - Use the Configuration Manager to add missing prefixes

3. **Data Format Errors**
   - Ensure data is tab-separated
   - Check that all required columns are present
   - Verify data doesn't contain special characters

### Debug Mode

Run with debug output:
```bash
python -u app.py
```

## 📝 Data Format

### Input Format
Tab-separated values with the following columns:
```
PREFIX    MASTER    FLIGHT    STATUS    Arrival DATE    PICKUP DATE    SLAC
297       123456789 FL123     ARRIVED   2024-01-15      2024-01-16     5
```

### Output Format
The application will group data by prefix and create separate emails for each group.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Author

**Bilal Ahmed**
- Email: [Your Email]
- Company: Fasttrack Express & Cargo Services

## 🆘 Support

For support and questions:
1. Check the troubleshooting section
2. Review the configuration examples
3. Open an issue on the repository

## 🔄 Version History

- **v1.0.0**: Initial release with secure credential handling

---

**Note**: This application implements secure credential handling and follows security best practices.
