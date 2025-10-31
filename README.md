# Facebook Group Data Extractor

An automated tool for extracting Facebook group data including group names, member counts, descriptions, and URLs.

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Google Chrome browser
- Facebook account credentials

### Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd facebook-group-data-extractor
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Facebook credentials:**
   ```bash
   # Copy the configuration template
   cp config.ini.example config.ini
   
   # Edit config.ini and add your Facebook credentials
   # email = your-email@example.com
   # password = your-password
   ```

### Usage

**Run the extraction:**
```bash
python phase1_main.py
```

The script will:
1. Load Facebook group URLs from `extracted_urls.txt`
2. Attempt login to Facebook
3. Extract data from each group
4. Save results to `output/scraped_data_raw.csv`

## 📁 Project Structure

```
facebook-group-data-extractor/
├── phase1_main.py           # Main execution script
├── scraper.py               # Core scraping logic
├── login.py                 # Facebook login functionality
├── config.ini.example       # Configuration template
├── config.ini               # Your credentials (not in git)
├── requirements.txt         # Python dependencies
├── extracted_urls.txt       # Input: Facebook group URLs
├── output/                  # Generated files
│   └── scraped_data_raw.csv # Extracted data output
├── Resources/               # Project resources
└── README.md               # This file
```

## 🎯 Features

### Data Extraction
- ✅ Group Name
- ✅ Group URL  
- ✅ Visible Member Count
- ✅ Short Description
- ✅ Extraction Date

### Anti-Detection
- ✅ Headless browser option
- ✅ Random delays between requests
- ✅ Human-like behavior patterns
- ✅ Session management

### Error Handling
- ✅ Graceful login failures
- ✅ Permission error handling
- ✅ Session expiration recovery
- ✅ Fallback for public-only data

## 📊 Output Format

The script generates `output/scraped_data_raw.csv` with the following columns:

```csv
group_name,group_url,member_count,description,extraction_date
Arizona Cardinals Tickets,https://www.facebook.com/groups/123456,6000,"Welcome to our group...",2025-10-28 12:00:00
```

## ⚙️ Configuration

Edit `config.ini` to customize:

```ini
[facebook]
email = your-email@example.com
password = your-password

[selenium]
headless_mode = false      # true = no browser window, false = visible
delay_min = 2              # Min seconds between requests
delay_max = 5              # Max seconds between requests
timeout = 10               # Page load timeout (seconds)

[scraping]
output_dir = output
raw_output_file = scraped_data_raw.csv

[logging]
log_level = INFO
log_file = extraction.log
```

## 🚨 Important Notes

### Legal Compliance
- This tool is designed for **public groups only**
- Respect Facebook's Terms of Service
- Use responsibly and ethically
- No private data extraction

### Rate Limiting
Facebook may rate-limit your account if:
- Too many requests are made
- Login appears automated
- Session expires frequently

**Recommendations:**
- Process in smaller batches
- Add delays between requests
- Monitor session status
- Use visible mode for manual intervention

## 🛠️ Troubleshooting

### Common Issues

1. **Login fails:**
   - Check credentials in `config.ini`
   - Ensure 2FA is disabled temporarily
   - Try visible mode (`headless_mode = false`)
   - Manually complete login when browser opens

2. **Permission denied error:**
   - Close CSV file if open in IDE/Excel
   - Script will auto-save to timestamped file
   - Check `output/` directory for backups

3. **Session expires:**
   - Facebook sessions timeout during long runs
   - Process smaller batches (30-50 groups)
   - Consider breaking up the URL list

4. **ChromeDriver errors:**
   - Update Chrome browser
   - Run: `pip install --upgrade selenium webdriver-manager`

### Manual Intervention Mode

For better reliability with many groups:

1. Set `headless_mode = false` in `config.ini`
2. Run the script
3. When browser opens, complete any manual login steps
4. Let the script continue automatically
5. Monitor for Facebook security checks

## 📈 Usage Examples

### Quick Test (5 groups)
```bash
# Edit phase1_main.py to limit URL processing
# Set: example_urls = example_urls[:5]
python phase1_main.py
```

### Full Extraction
```bash
# Loads all URLs from extracted_urls.txt
python phase1_main.py
```

### Check Progress
```bash
# Monitor output file
# Windows: type output\scraped_data_raw.csv
# Linux/Mac: cat output/scraped_data_raw.csv
```

## 📝 Notes

- **Member counts** are extracted from public view only
- **Descriptions** are taken from the "About" section
- **Login** may require manual completion of security checks
- **Session** may expire during long extraction runs

## 🤝 Contributing

Contributions welcome! Please:
- Follow the existing code style
- Add error handling for edge cases
- Test with sample data first
- Document new features

## 📄 License

See `LICENSE` file for details.

---

**Happy extracting! 🎯**
# facebook-group-data-extractor
# facebook-group-data-extractor
