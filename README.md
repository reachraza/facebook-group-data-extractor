# Facebook Group Data Extractor

An automated tool for extracting Facebook group data including group names, member counts, descriptions, admin/member information, and profile URLs. Supports both manual URL extraction (Phase 1) and automated group discovery through keyword-based search (Phase 2).

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Google Chrome browser
- Facebook account credentials

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/reachraza/facebook-group-data-extractor.git
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

## 📖 Usage

### Phase 1: Extract Data from Known Group URLs

Extract data from a list of Facebook group URLs:

```bash
python phase1_main.py
```

The script will:
1. Load Facebook group URLs from `extracted_urls.txt`
2. Attempt login to Facebook
3. Extract comprehensive data from each group
4. Save results to `output/scraped_data_raw.csv`

### Phase 2: Search and Discover Groups

Automatically search for groups using keywords and extract data:

```bash
python phase2_main.py
```

The script will:
1. Generate keywords from `Resources/All Teams by Sport.xlsx` (or CSV files)
2. Search Facebook for groups matching each keyword
3. Extract group URLs from search results
4. Optionally enrich data with member/admin details
5. Save results to `output/search_results_*.csv`

### Test Single Group

Test extraction on a single group URL:

```bash
python test_single_group.py https://www.facebook.com/groups/YOUR_GROUP_ID
```

Results are saved to `output/test_single_group_results.csv`

## 📁 Project Structure

```
facebook-group-data-extractor/
├── phase1_main.py           # Phase 1: Extract from known URLs
├── phase2_main.py           # Phase 2: Search and discover groups
├── test_single_group.py     # Test script for single group extraction
├── scraper.py               # Core scraping logic
├── login.py                 # Facebook login functionality
├── search.py                # Group search functionality
├── input_processor.py       # Keyword generation from Excel/CSV
├── config.ini.example       # Configuration template
├── config.ini               # Your credentials (not in git)
├── requirements.txt         # Python dependencies
├── extracted_urls.txt       # Input: Facebook group URLs (Phase 1)
├── output/                  # Generated files
│   ├── scraped_data_raw.csv # Phase 1 output
│   └── search_results_*.csv # Phase 2 output
├── Resources/               # Project resources
│   └── All Teams by Sport.xlsx # Keyword source for Phase 2
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## 🎯 Features

### Data Extraction
- ✅ Group Name
- ✅ Group URL  
- ✅ Exact Member Count (from /about page)
- ✅ Group Description (from /about page)
- ✅ Privacy Settings (Public/Private)
- ✅ Admin Names (from /members/admins page)
- ✅ Admin Profile URLs
- ✅ Member Names (first 5 members)
- ✅ Member Profile URLs
- ✅ Extraction Date

### Phase 2: Search & Discovery
- ✅ Keyword-based group search
- ✅ Automatic keyword generation from Excel/CSV files
- ✅ URL validation and deduplication
- ✅ Rate limiting and cooldown management
- ✅ Session keepalive during long searches

### Member Messaging (Optional)
- ✅ Automatically sends "Hi" message to first 5 members
- ✅ Navigates to member profiles
- ✅ Finds and clicks Message button
- ✅ Sends personalized messages

### Anti-Detection
- ✅ Headless browser option
- ✅ Random delays between requests
- ✅ Human-like behavior patterns
- ✅ Session management and recovery
- ✅ CAPTCHA detection and manual solving

### Error Handling
- ✅ Graceful login failures
- ✅ Permission error handling (saves to timestamped files)
- ✅ Session expiration recovery
- ✅ Fallback for public-only data
- ✅ Comprehensive logging

## 📊 Output Format

### Phase 1 Output (`output/scraped_data_raw.csv`)

```csv
group_name,group_url,member_count,description,privacy,admin_names,admin_profile_urls,member_names,member_profile_urls,extraction_date
Miami Heat Tickets Hub,https://www.facebook.com/groups/123456,1169,"Welcome to the ultimate...",Public,"Classic Olinger; Melissa Joe","https://facebook.com/profile.php?id=100; https://facebook.com/profile.php?id=200","Mishka Mishi Blake; Kory Scholten","https://facebook.com/profile.php?id=300; https://facebook.com/profile.php?id=400",2025-11-04 19:06:11
```

### Phase 2 Output (`output/search_results_*.csv`)

```csv
keyword,group_url,captured_at,description,group_name,member_count,privacy,admin_names,admin_profile_urls,member_names,member_profile_urls
Arizona Cardinals Tickets,https://www.facebook.com/groups/1679801736170853,2025-10-30 21:57:58,"Anyone can find this group.",Arizona Cardinals Tickets buy/Sell (Verified Sellers),13600,Public,"Admin1; Admin2",...","Member1; Member2",...,
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

[search]
cooldown_seconds = 30      # Delay between searches in Phase 2
enable_enrichment = false  # true = extract full details, false = URL only
keepalive_interval = 30    # Ping Facebook every N searches to keep session alive

[logging]
log_level = INFO
log_file = extraction.log
```

## 🚨 Important Notes

### Legal Compliance
- This tool is designed for **public groups only**
- Respect Facebook's Terms of Service
- Use responsibly and ethically
- No private data extraction without permission
- Member messaging should be used ethically and with consent

### Rate Limiting & Session Management
Facebook may rate-limit your account if:
- Too many requests are made
- Login appears automated
- Session expires frequently
- Too many messages are sent quickly

**Recommendations:**
- Process in smaller batches (30-50 groups)
- Add delays between requests (5-10 seconds)
- Monitor session status
- Use visible mode (`headless_mode = false`) for manual intervention
- Be cautious with member messaging feature

### Member Data Limitations
- **Admin extraction**: Works best when logged in and a member of the group
- **Member extraction**: Requires being a member or admin of the group
- **Profile visibility**: Depends on privacy settings of each user
- **Message sending**: Only works if the user accepts messages from non-friends

## 🛠️ Troubleshooting

### Common Issues

1. **Login fails:**
   - Check credentials in `config.ini`
   - Ensure 2FA is disabled temporarily (or handle manually)
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
   - Enable `keepalive_interval` in Phase 2

4. **ChromeDriver errors:**
   - Update Chrome browser to latest version
   - Run: `pip install --upgrade selenium webdriver-manager`

5. **No members/admins extracted:**
   - Ensure you're logged in
   - Verify you're a member of the group (for member data)
   - Some groups restrict member list visibility
   - Check group privacy settings

6. **Message sending fails:**
   - User may have restricted messaging
   - May require being friends with the user
   - Privacy settings may prevent messaging

### Manual Intervention Mode

For better reliability:

1. Set `headless_mode = false` in `config.ini`
2. Run the script
3. When browser opens, complete any manual login steps
4. Handle CAPTCHA if prompted
5. Let the script continue automatically
6. Monitor for Facebook security checks

## 📈 Usage Examples

### Phase 1: Quick Test (Single Group)
```bash
python test_single_group.py https://www.facebook.com/groups/1010596414530403
```

### Phase 1: Extract from URL List
```bash
# Edit extracted_urls.txt with your group URLs
python phase1_main.py
```

### Phase 2: Search and Extract
```bash
# Ensure Resources/All Teams by Sport.xlsx exists
# Or update input_processor.py to read from your CSV
python phase2_main.py
```

### Phase 2: Search with Enrichment
```bash
# Edit config.ini:
# enable_enrichment = true
# This will extract full details but takes longer
python phase2_main.py
```

## 📝 Development Notes

### Adding New Keywords for Phase 2

1. Edit `Resources/All Teams by Sport.xlsx` or create a CSV file
2. Ensure the file has a column with team names
3. Update `input_processor.py` if needed to read your file format
4. Run `phase2_main.py`

### Customizing Message Text

Edit `scraper.py` in the member extraction section:
```python
message_text="Hi"   # Change this to your desired message
```

### Extending Data Fields

To extract additional fields:
1. Update `scraper.py` → `scrape_group_data()` function
2. Add extraction logic for new fields
3. Update CSV writer in `phase1_main.py` and `phase2_main.py`
4. Update fieldnames list in save functions

## 🤝 Contributing

Contributions welcome! Please:
- Follow the existing code style
- Add comprehensive error handling
- Test with sample data first
- Document new features
- Update README for new features

## 📄 License

See `LICENSE` file for details.

---

**Happy extracting! 🎯**
