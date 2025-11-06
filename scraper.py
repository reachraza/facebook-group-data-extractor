"""
Core Group Scraper for Facebook Group Data Extractor
Phase 1: Function to navigate to a single known group URL and extract data

Purpose:
- Navigate to individual Facebook group pages
- Extract comprehensive group information from the page DOM
- Parse multiple data fields with robust error handling
- Support both logged-in and public-only extraction modes

Key Features:
- Multiple selector strategies for each field (fault-tolerant)
- Regex-based text parsing for structured data extraction
- Session recovery and retry logic
- Admin information extraction from /members/admins page
- Member information extraction from /members page
- Graceful degradation when elements are not found

Data Extracted:
1. Group Name: The official title of the Facebook group
2. Member Count: Number of members (extracted from /about page)
3. Description: About section from /about page
4. Privacy: Public or Private status
5. Admin Names: List of group administrators
6. Admin Profile URLs: Direct links to admin profiles
7. Member Names: First 5 member names
8. Member Profile URLs: Direct links to member profiles
9. Extraction Date: Timestamp of when data was collected
"""

# Standard library imports
import time          # For adding delays between page interactions
import re            # For regex pattern matching (member counts, parsing)
from datetime import datetime  # For timestamping when data was extracted

# Selenium WebDriver imports
from selenium.webdriver.common.by import By  # Locator strategies (ID, CSS, XPath)
from selenium.webdriver.support.ui import WebDriverWait  # Wait for elements to load
from selenium.webdriver.support import expected_conditions as EC  # Expected conditions for waits
from selenium.common.exceptions import TimeoutException, NoSuchElementException  # Common exceptions
from selenium.webdriver.common.keys import Keys  # For keyboard input (Enter key to send message)


def _send_message_to_profile(driver, message_text="Hi"):
    """
    Send a message to the currently open profile page
    
    This function:
    1. Finds the "Message" button on the profile page (or group user page)
    2. Clicks it to open the message composer
    3. Finds the message input field
    4. Types the message text
    5. Sends the message (either by clicking send button or pressing Enter)
    
    Args:
        driver: Selenium WebDriver instance (should be on a profile page or group user page)
        message_text (str): Text message to send (default: "Hi")
    
    Returns:
        bool: True if message was sent successfully, False otherwise
    """
    try:
        current_url = driver.current_url
        print(f"      💬 Attempting to send message: '{message_text}' (from: {current_url[:80]}...)")
        
        # Wait for page to fully load and scroll to ensure button is visible
        time.sleep(2)
        try:
            # Scroll to top first, then scroll down a bit to ensure page is loaded
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
            driver.execute_script("window.scrollTo(0, 500);")
            time.sleep(1)
        except:
            pass
        
        # Find the "Message" button - try multiple selectors
        message_button = None
        message_selectors = [
            "//span[contains(text(), 'Message')]/ancestor::a",
            "//a[contains(@aria-label, 'Message') or contains(@aria-label, 'message')]",
            "//div[contains(@aria-label, 'Message')]",
            "//a[contains(@href, '/messages/')]",
            "//div[@role='button' and contains(., 'Message')]",
            "//span[text()='Message']/ancestor::div[@role='button']",
            "//span[text()='Message']/ancestor::a",
            "//a[contains(@href, 'messages')]",
            "//button[contains(., 'Message')]",
            "//div[contains(@class, 'message') and @role='button']",
            # Also try case-insensitive matching
            "//*[contains(translate(text(), 'MESSAGE', 'message'), 'message')]/ancestor::a | //*[contains(translate(text(), 'MESSAGE', 'message'), 'message')]/ancestor::div[@role='button']",
        ]
        
        for i, selector in enumerate(message_selectors):
            try:
                message_button = driver.find_element(By.XPATH, selector)
                if message_button and message_button.is_displayed():
                    print(f"      ✅ Found Message button (selector {i+1})")
                    break
            except Exception as e:
                continue
        
        if not message_button:
            # Try one more time with a longer wait and all buttons/links
            print(f"      🔍 Message button not found with XPath, trying broader search...")
            time.sleep(2)
            try:
                # Find all buttons and links containing "Message" text
                all_elements = driver.find_elements(By.XPATH, "//a | //button | //div[@role='button']")
                for elem in all_elements:
                    try:
                        text = elem.text.lower()
                        aria_label = (elem.get_attribute('aria-label') or '').lower()
                        if 'message' in text or 'message' in aria_label:
                            if elem.is_displayed():
                                message_button = elem
                                print(f"      ✅ Found Message button via text search")
                                break
                    except:
                        continue
            except:
                pass
        
        if not message_button:
            print(f"      ⚠️  Could not find Message button - it may not be available on this page")
            print(f"      💡 Tip: Message button might not appear if you're not friends or if privacy settings restrict messaging")
            return False
        
        # Click the Message button using JavaScript (more reliable)
        driver.execute_script("arguments[0].click();", message_button)
        time.sleep(3)  # Wait for message composer to open
        
        # Look for message input field - try multiple selectors
        message_input = None
        input_selectors = [
            "//div[@contenteditable='true' and @role='textbox']",
            "//div[@contenteditable='true' and contains(@aria-label, 'message')]",
            "//div[@contenteditable='true' and contains(@aria-label, 'Message')]",
            "//div[@contenteditable='true' and @data-lexical-editor='true']",
            "//textarea[contains(@placeholder, 'message') or contains(@placeholder, 'Message')]",
            "//div[contains(@class, 'message') and @contenteditable='true']",
        ]
        
        for selector in input_selectors:
            try:
                message_input = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, selector))
                )
                if message_input:
                    print(f"      ✅ Found message input field")
                    break
            except:
                continue
        
        if not message_input:
            print(f"      ⚠️  Could not find message input field")
            return False
        
        # Click on the input field to focus it
        driver.execute_script("arguments[0].click();", message_input)
        time.sleep(1)
        
        # Type the message text
        # For contenteditable divs, we need to use JavaScript
        driver.execute_script("arguments[0].innerText = arguments[1];", message_input, message_text)
        time.sleep(1)
        
        # Also trigger input event to ensure Facebook detects the text
        driver.execute_script("""
            var event = new Event('input', { bubbles: true });
            arguments[0].dispatchEvent(event);
        """, message_input)
        time.sleep(1)
        
        # Find and click the Send button - try multiple selectors
        send_button = None
        send_selectors = [
            "//div[@aria-label='Send' or @aria-label='send']",
            "//div[@role='button' and contains(@aria-label, 'Send')]",
            "//span[contains(text(), 'Send')]/ancestor::div[@role='button']",
            "//div[contains(@aria-label, 'Press Enter to send')]",
            "//div[@data-testid='send-button']",
        ]
        
        for selector in send_selectors:
            try:
                send_button = driver.find_element(By.XPATH, selector)
                if send_button:
                    print(f"      ✅ Found Send button")
                    break
            except:
                continue
        
        if send_button:
            # Click Send button
            driver.execute_script("arguments[0].click();", send_button)
            print(f"      ✅ Message sent via Send button")
        else:
            # If no Send button found, try pressing Enter
            message_input.send_keys(Keys.ENTER)
            print(f"      ✅ Message sent via Enter key")
        
        time.sleep(2)  # Wait for message to be sent
        
        return True
        
    except Exception as e:
        print(f"      ⚠️  Error sending message: {str(e)}")
        return False


def _click_and_get_profile_url(driver, name, current_page_url, send_message=False, message_text="Hi"):
    """
    Helper function to click on a name link, get the profile URL, optionally send message, and go back
    
    This function:
    1. Finds the link element with the given name
    2. Clicks on it to open the profile
    3. Waits for the profile page to load
    4. Gets the current URL (which is the profile URL)
    5. Optionally sends a message if send_message is True
    6. Navigates back to the original page
    7. Returns the profile URL
    
    Args:
        driver: Selenium WebDriver instance
        name (str): Name of the person to click on
        current_page_url (str): URL of the current page (to return to)
        send_message (bool): If True, send a message after opening profile (default: False)
        message_text (str): Text message to send if send_message is True (default: "Hi")
    
    Returns:
        str: Profile URL if successful, empty string if failed
    """
    try:
        # Find the link element with this name
        name_link = None
        try:
            # Escape single quotes in name for XPath
            name_escaped = name.replace("'", "\\'")
            # Try to find by exact text match first
            try:
                name_link = driver.find_element(By.XPATH, 
                    f"//a[normalize-space(text())='{name_escaped}' and contains(@href, 'facebook.com/')]")
            except:
                # If exact match fails, try partial match
                name_link = driver.find_element(By.XPATH, 
                    f"//a[contains(text(), '{name_escaped}') and contains(@href, 'facebook.com/')]")
        except:
            # If XPath fails, try CSS selector or find by link text
            try:
                # Try finding by partial link text
                name_link = driver.find_element(By.PARTIAL_LINK_TEXT, name.split()[0] if name.split() else name)
            except:
                # Last resort: find all links and match by text
                try:
                    all_links = driver.find_elements(By.XPATH, "//a[contains(@href, 'facebook.com/')]")
                    for link in all_links:
                        if name.lower() in link.text.lower() and name.lower() == link.text.strip().lower():
                            name_link = link
                            break
                except:
                    pass
        
        if not name_link:
            print(f"      ⚠️  Could not find link for: {name}")
            return ''
        
        # Get the href before clicking (as backup)
        href_before = name_link.get_attribute('href') or ''
        
        # Click on the link using JavaScript (more reliable)
        driver.execute_script("arguments[0].click();", name_link)
        
        # Wait for page to load (profile page)
        time.sleep(3)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Get the current URL (this is the profile URL)
        profile_url = driver.current_url
        
        # Check if we're on a group-specific user page (not actual profile)
        if '/groups/' in profile_url and '/user/' in profile_url:
            print(f"      📍 On group user page, extracting user ID to get actual profile...")
            # Extract user ID from URL like: https://www.facebook.com/groups/1010596414530403/user/100051688324105/
            user_id_match = re.search(r'/user/(\d+)/?', profile_url)
            if user_id_match:
                user_id = user_id_match.group(1)
                # Try to find a link to the actual profile on this page
                try:
                    # Look for a profile link or try to click on the name again
                    profile_link_selectors = [
                        f"//a[contains(@href, 'profile.php?id={user_id}')]",
                        f"//a[contains(@href, '/{user_id}') and not(contains(@href, '/groups/'))]",
                        f"//a[contains(@href, 'facebook.com/{user_id}')]",
                        "//a[@aria-label and contains(@aria-label, 'profile')]",
                        "//a[contains(text(), name) and contains(@href, 'profile')]",
                    ]
                    actual_profile_link = None
                    for selector in profile_link_selectors:
                        try:
                            actual_profile_link = driver.find_element(By.XPATH, selector)
                            if actual_profile_link:
                                actual_profile_url = actual_profile_link.get_attribute('href')
                                if actual_profile_url and '/groups/' not in actual_profile_url:
                                    print(f"      ✅ Found actual profile link, navigating...")
                                    driver.get(actual_profile_url)
                                    time.sleep(3)
                                    profile_url = driver.current_url
                                    break
                        except:
                            continue
                    
                    # If no link found, construct profile URL directly
                    if '/groups/' in profile_url:
                        profile_url = f"https://www.facebook.com/profile.php?id={user_id}"
                        print(f"      🔗 Constructing profile URL: {profile_url}")
                        driver.get(profile_url)
                        time.sleep(3)
                        profile_url = driver.current_url
                except Exception as e:
                    print(f"      ⚠️  Error extracting profile URL: {str(e)}")
                    # Construct profile URL anyway
                    if user_id_match:
                        profile_url = f"https://www.facebook.com/profile.php?id={user_id}"
                        driver.get(profile_url)
                        time.sleep(3)
                        profile_url = driver.current_url
        
        # Validate it's actually a profile URL (not still on members page)
        if '/groups/' in profile_url and '/members/' not in profile_url and '/user/' not in profile_url:
            # This is okay - it might be a profile.php?id= URL or username-based profile
            pass
        elif '/groups/' in profile_url:
            print(f"      ⚠️  Still on group page, trying to find profile link...")
            # Try one more time to find and click profile link
            try:
                profile_links = driver.find_elements(By.XPATH, "//a[contains(@href, 'profile') or contains(@href, 'facebook.com')]")
                for link in profile_links[:5]:  # Check first 5 links
                    href = link.get_attribute('href') or ''
                    if href and '/groups/' not in href and ('profile.php' in href or '/people/' in href or re.match(r'https://www\.facebook\.com/[a-zA-Z0-9.]+/?$', href)):
                        print(f"      🔗 Found potential profile link: {href[:80]}...")
                        driver.get(href)
                        time.sleep(3)
                        profile_url = driver.current_url
                        if '/groups/' not in profile_url:
                            break
            except:
                pass
        
        # Final check - if still on group page, use href as fallback but still try to send message
        if '/groups/' in profile_url and '/user/' in profile_url:
            print(f"      ⚠️  Could not navigate to actual profile, but will try to send message from current page")
            # Don't return early - continue to try sending message
        
        # Wait a bit more to ensure page fully loaded
        time.sleep(1)
        
        print(f"      ✅ Current page URL for {name}: {profile_url[:80]}...")
        
        # Optionally send a message if requested
        if send_message:
            message_sent = _send_message_to_profile(driver, message_text)
            if message_sent:
                print(f"      ✅ Message sent to {name}")
            else:
                print(f"      ⚠️  Failed to send message to {name}")
            # Wait a bit after sending message
            time.sleep(2)
        
        # Navigate back to the original page
        driver.back()
        time.sleep(2)
        
        # Wait for the page to load back
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # If we're not on the right page, navigate directly
        if current_page_url not in driver.current_url:
            driver.get(current_page_url)
            time.sleep(2)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
        
        return profile_url
        
    except Exception as e:
        print(f"      ⚠️  Error clicking and getting profile for {name}: {str(e)}")
        try:
            # Try to go back if we're on a different page
            if current_page_url not in driver.current_url:
                driver.get(current_page_url)
                time.sleep(2)
        except:
            pass
        return ''


def scrape_group_data(driver, group_url):
    """
    Extract comprehensive data from a single Facebook group page
    
    This is the core scraping function that navigates to a group URL and extracts
    all available information. It uses multiple selector strategies and regex patterns
    to handle variations in Facebook's page structure.
    
    Extraction Strategy:
    1. Navigate to group URL and wait for page load
    2. Detect if access is restricted (login required page)
    3. Extract group name using multiple CSS selectors
    4. Navigate to /about page for description, exact member count, and privacy
    5. Navigate to /members page
    6. Click "See All" for admins and extract from /members/admins page
    7. Extract first 5 members from "New to the group" section
    8. Return structured data dictionary
    
    Args:
        driver (webdriver.Chrome): Active Selenium WebDriver instance with session
        group_url (str): Facebook group URL to scrape (e.g., "https://www.facebook.com/groups/123")
    
    Returns:
        dict: Group data dictionary with keys:
              - 'group_name': String name of the group
              - 'group_url': Original URL
              - 'member_count': Integer count of members
              - 'description': String description text
              - 'privacy': String (Public/Private)
              - 'admin_names': Semicolon-separated admin names
              - 'admin_profile_urls': Semicolon-separated profile URLs
              - 'member_names': Semicolon-separated member names (first 5)
              - 'member_profile_urls': Semicolon-separated profile URLs
              - 'extraction_date': Timestamp of extraction
              Returns None if extraction fails completely
    """
    print(f"📊 Scraping group: {group_url}")
    
    try:
        # ========== STEP 1: NAVIGATE TO GROUP PAGE ==========
        # Navigate the browser to the Facebook group page
        driver.get(group_url)
        # Wait 3 seconds for initial page load and JavaScript execution
        time.sleep(3)
        
        # Wait for page body element to be present in DOM (confirms page loaded)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # ========== STEP 2: INITIALIZE DATA STRUCTURE ==========
        # Create a dictionary with default values for all fields
        # These defaults will be overwritten if data is successfully extracted
        group_data = {
            'group_name': 'Unknown',              # Default: will be overwritten if found
            'group_url': group_url,               # Always set to the provided URL
            'member_count': 0,                    # Default: will be overwritten if found
            'description': 'No description available',  # Default: will be overwritten if found
            'privacy': '',                        # Default: empty string (Public/Private)
            'admin_names': '',                    # Default: empty string if admins not visible
            'admin_profile_urls': '',             # Default: empty string if URLs not found
            'member_names': '',                   # Default: empty string if members not visible
            'member_profile_urls': '',            # Default: empty string if URLs not found
            'extraction_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Current timestamp
        }
        
        # ========== STEP 3: DETECT ACCESS RESTRICTIONS ==========
        # Check if we've been redirected to a login/restricted page
        # Facebook shows these pages when group is private or session expired
        
        # Only check the URL - this is the most reliable indicator
        # Don't check page text as it can have "log in" text even when logged in
        current_url = driver.current_url
        print(f"   📍 Current URL: {current_url[:100]}...")  # Debug: show what URL we're on
        current_url_lower = current_url.lower()
        is_login_page = (
            'facebook.com/login' in current_url_lower or
            'facebook.com/checkpoint' in current_url_lower or
            'facebook.com/reg' in current_url_lower
        )
        
        # If we detected a login page URL, warn but continue trying to extract data
        # (Some public groups might still show basic info even when redirected)
        if is_login_page:
            print("   ⚠️  Login page detected - will attempt to extract available data")
            
            # Try to get the group name from page title as a fallback
            try:
                # Facebook sometimes includes group name in page title even on login page
                title = driver.title
                if title and 'facebook' not in title.lower() and 'log in' not in title.lower():
                    group_data['group_name'] = title
                    print(f"   ✅ Found group name from title: {title}")
            except:
                pass
        else:
            print(f"   ✅ On group page - proceeding with full extraction")
        
        # ========== STEP 4: EXTRACT GROUP NAME ==========
        # Try multiple CSS selectors because Facebook's HTML structure can vary
        # We use a fallback strategy: try the most common selector first, then alternatives
        name_selectors = [
            "h1",                       # Most common: group name is usually in h1 tag
            "[data-testid='group-name']",  # Facebook's official test ID for group name
            "h1[class*='group']",       # Alternative: h1 with class containing "group"
            "[role='main'] h1",         # Main content area heading
            "h2"                        # Fallback: sometimes it's an h2 tag
        ]
        
        # Iterate through selectors until we find one that works
        for selector in name_selectors:
            try:
                # Try to locate element using this selector
                name_element = driver.find_element(By.CSS_SELECTOR, selector)
                # Verify element exists and has non-empty text content
                if name_element and name_element.text.strip():
                    # Successfully found group name
                    group_data['group_name'] = name_element.text.strip()
                    print(f"   ✅ Found group name: {group_data['group_name']}")
                    # Break loop since we found the name
                    break
            except NoSuchElementException:
                # Selector didn't match anything on this page - try next selector
                continue
        
        # ========== STEP 5: NAVIGATE TO /ABOUT PAGE FOR DETAILED DATA ==========
        # Extract description, exact member count, and privacy settings from /about page
        about_url = group_url.rstrip('/') + '/about'
        print(f"   📄 Navigating to /about page...")
        try:
            driver.get(about_url)
            time.sleep(3)  # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Get page text for parsing
            page_text = driver.find_element(By.TAG_NAME, "body").text
            
            # ========== EXTRACT DESCRIPTION FROM "ABOUT THIS GROUP" SECTION ==========
            try:
                # Look for "About this group" heading
                about_heading = None
                try:
                    about_heading = driver.find_element(By.XPATH, 
                        "//*[contains(text(), 'About this group') or contains(text(), 'About this Group')]")
                except:
                    pass
                
                if about_heading:
                    # Find the description text after the heading
                    # Try multiple approaches
                    description_found = False
                    
                    # Method 1: Look for span or div with dir='auto' after the heading
                    try:
                        parent = about_heading.find_element(By.XPATH, "./ancestor::div[position()<10]")
                        desc_elements = parent.find_elements(By.XPATH, 
                            ".//span[@dir='auto'] | .//div[@dir='auto'] | .//p[@dir='auto']")
                        for elem in desc_elements:
                            text = elem.text.strip()
                            if text and len(text) > 20:
                                # Filter out junk
                                if 'see more' not in text.lower() and 'facebook' not in text.lower():
                                    group_data['description'] = text[:500]
                                    print(f"   ✅ Found description from /about page: {group_data['description'][:100]}...")
                                    description_found = True
                                    break
                    except:
                        pass
                    
                    # Method 2: Parse from page text
                    if not description_found:
                        lines = page_text.split('\n')
                        found_about_heading = False
                        for i, line in enumerate(lines):
                            if 'about this group' in line.lower():
                                found_about_heading = True
                                # Look for description in next few lines
                                for j in range(i+1, min(i+5, len(lines))):
                                    desc_line = lines[j].strip()
                                    if desc_line and len(desc_line) > 20:
                                        # Filter out junk
                                        skip_words = ['public', 'private', 'visible', 'anyone can see', 
                                                     'see more', 'members', 'activity', 'created']
                                        if not any(skip in desc_line.lower() for skip in skip_words):
                                            group_data['description'] = desc_line[:500]
                                            print(f"   ✅ Found description from /about page: {group_data['description'][:100]}...")
                                            description_found = True
                                            break
                                break
            except Exception as e:
                print(f"   Note: Could not extract description from /about: {str(e)}")
            
            # ========== EXTRACT EXACT MEMBER COUNT FROM /ABOUT PAGE ==========
            try:
                # Look for "total members" or exact member count
                # Pattern: "1,169 total members" or "1,167 members"
                member_count_patterns = [
                    r'(\d{1,3}(?:,\d{3})*)\s+total\s+members?',  # "1,169 total members"
                    r'Members\s+·\s+(\d{1,3}(?:,\d{3})*)',        # "Members · 1,167"
                    r'(\d{1,3}(?:,\d{3})*)\s+members?\s*$',        # "1,167 members" at end of line
                ]
                
                for pattern in member_count_patterns:
                    matches = re.findall(pattern, page_text, re.IGNORECASE)
                    if matches:
                        # Get the first match and remove commas
                        count_str = matches[0].replace(',', '')
                        try:
                            count = int(count_str)
                            if count > 0:
                                group_data['member_count'] = count
                                print(f"   ✅ Found exact member count from /about: {count:,}")
                                break
                        except:
                            continue
            except Exception as e:
                print(f"   Note: Could not extract member count from /about: {str(e)}")
            
            # ========== EXTRACT PRIVACY SETTINGS ==========
            try:
                # Look for "Public" or "Private" text
                if 'public' in page_text.lower() and 'public group' in page_text.lower():
                    group_data['privacy'] = 'Public'
                    print(f"   ✅ Group privacy: Public")
                elif 'private' in page_text.lower() and 'private group' in page_text.lower():
                    group_data['privacy'] = 'Private'
                    print(f"   ✅ Group privacy: Private")
            except Exception as e:
                print(f"   Note: Could not extract privacy settings: {str(e)}")
                
        except Exception as e:
            print(f"   ⚠️  Could not navigate to /about page: {str(e)}")
        
        # ========== STEP 6: NAVIGATE TO /MEMBERS PAGE FOR ADMIN AND MEMBER DATA ==========
        members_url = group_url.rstrip('/') + '/members'
        print(f"   👥 Navigating to /members page...")
        try:
            driver.get(members_url)
            time.sleep(3)  # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            admin_names = []
            admin_profile_urls = []
            member_names = []
            member_profile_urls = []
            
            # ========== EXTRACT ADMIN NAMES FROM /MEMBERS/ADMINS PAGE ==========
            try:
                # Look for "See All" button in the "Admins & moderators" section
                see_all_buttons = driver.find_elements(By.XPATH, 
                    "//*[contains(text(), 'See All') or contains(text(), 'See all') or contains(text(), 'See All')]")
                
                clicked_see_all = False
                for button in see_all_buttons:
                    try:
                        # Check if this button is in the admin section
                        parent_text = button.find_element(By.XPATH, "./ancestor::div[position()<10]").text
                        if 'admin' in parent_text.lower() or 'moderator' in parent_text.lower():
                            print(f"   🔍 Clicking 'See All' for admins...")
                            driver.execute_script("arguments[0].click();", button)  # Use JavaScript click for reliability
                            time.sleep(5)  # Wait longer for page to load
                            clicked_see_all = True
                            break
                    except:
                        continue
                
                # Check if we're now on /members/admins page
                current_url = driver.current_url
                is_admins_page = '/admins' in current_url
                print(f"   📍 Current URL after clicking: {current_url[:100]}...")
                print(f"   📍 Is on /admins page: {is_admins_page}")
                
                # Wait a bit more for page to fully load
                time.sleep(3)
                
                # Scroll to load content if on /admins page
                if is_admins_page:
                    print(f"   📜 Scrolling to load admin content...")
                    for i in range(3):
                        driver.execute_script("window.scrollBy(0, 500);")
                        time.sleep(1)
                    # Scroll back to top
                    driver.execute_script("window.scrollTo(0, 0);")
                    time.sleep(2)
                
                # Get page text for parsing
                page_text = driver.find_element(By.TAG_NAME, "body").text
                print(f"   📝 Page text length: {len(page_text)} chars")
                
                # Find all profile links on the page
                all_links = driver.find_elements(By.XPATH, "//a[contains(@href, 'facebook.com/')]")
                print(f"   📝 Found {len(all_links)} total links on page")
                
                # If we're on /members/admins page, ALL profile links are admins
                if is_admins_page:
                    print(f"   ✅ On /admins page - extracting all profile links as admins...")
                    
                    # Try regex-based extraction first (like we do for members)
                    # Look for pattern: "Name\nAdmin" or "Name\nModerator"
                    admin_pattern = r'\n([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})\n.*?(?:Admin|Moderator)'
                    admin_matches = re.findall(admin_pattern, page_text)
                    print(f"   📝 Found {len(admin_matches)} 'Name\nAdmin' patterns via regex")
                    
                    # Extract from regex matches first
                    for match in admin_matches:
                        name = match.strip()
                        if name and len(name) > 1:
                            # Skip UI elements
                            skip_ui_words = ['learn more', 'see all', 'see more', 'find a member', 
                                           'admin', 'moderator', 'joined', 'new to the group']
                            if any(skip in name.lower() for skip in skip_ui_words):
                                continue
                            
                            # Validate name format
                            words = name.split()
                            if 1 <= len(words) <= 4:
                                if sum(c.isalpha() or c.isspace() for c in name) / len(name) > 0.7:
                                    if name.lower() not in [a.lower() for a in admin_names]:
                                        # Try to find the profile link for this name
                                        href = ''
                                        try:
                                            name_link = driver.find_element(By.XPATH, 
                                                f"//a[contains(text(), '{name}') and contains(@href, 'facebook.com/')]")
                                            href = name_link.get_attribute('href') or ''
                                        except:
                                            pass
                                        
                                        admin_names.append(name)
                                        admin_profile_urls.append(href)
                                        print(f"      ✅ Found admin (regex): {name}")
                    
                    # Also try link-based extraction
                    if len(admin_names) == 0:
                        print(f"   🔄 Trying link-based extraction...")
                        for link in all_links:
                            try:
                                name = link.text.strip()
                                href = link.get_attribute('href') or ''
                                
                                # Skip if no name or href
                                if not name or not href or len(name) < 2:
                                    continue
                                
                                # Validate it's a profile link (not group/page/event link)
                                url_lower = href.lower()
                                is_profile = (
                                    'profile.php' in url_lower or
                                    (url_lower.count('/') >= 3 and 
                                     'facebook.com/' in url_lower and 
                                     '/groups/' not in url_lower and 
                                     '/pages/' not in url_lower and
                                     '/events/' not in url_lower and
                                     '/marketplace/' not in url_lower and
                                     '/hashtag/' not in url_lower)
                                )
                                
                                if not is_profile:
                                    continue
                                
                                # Skip UI elements
                                skip_ui_words = ['learn more', 'see all', 'see more', 'find a member', 
                                               'admin', 'moderator', 'joined', 'new to the group']
                                if any(skip in name.lower() for skip in skip_ui_words):
                                    continue
                                
                                # Validate name format (should be 1-4 words, mostly letters)
                                words = name.split()
                                if not (1 <= len(words) <= 4):
                                    continue
                                
                                # Check if mostly letters (at least 70%)
                                if sum(c.isalpha() or c.isspace() for c in name) / len(name) < 0.7:
                                    continue
                                
                                # On /admins page, all profile links are admins
                                if name.lower() not in [a.lower() for a in admin_names]:
                                    admin_names.append(name)
                                    admin_profile_urls.append(href)
                                    print(f"      ✅ Found admin (link): {name}")
                            except Exception as e:
                                print(f"      ⚠️  Error processing link: {str(e)}")
                                continue
                else:
                    # Not on /admins page - use the original logic to find admins
                    print(f"   🔍 Not on /admins page - using pattern matching...")
                    for link in all_links:
                        try:
                            name = link.text.strip()
                            href = link.get_attribute('href') or ''
                            
                            # Skip if no name or href
                            if not name or not href or len(name) < 2:
                                continue
                            
                            # Validate it's a profile link (not group/page/event link)
                            url_lower = href.lower()
                            is_profile = (
                                'profile.php' in url_lower or
                                (url_lower.count('/') >= 3 and 
                                 'facebook.com/' in url_lower and 
                                 '/groups/' not in url_lower and 
                                 '/pages/' not in url_lower and
                                 '/events/' not in url_lower and
                                 '/marketplace/' not in url_lower and
                                 '/hashtag/' not in url_lower)
                            )
                            
                            if not is_profile:
                                continue
                            
                            # Skip UI elements
                            skip_ui_words = ['learn more', 'see all', 'see more', 'find a member', 
                                           'admin', 'moderator', 'joined', 'new to the group']
                            if any(skip in name.lower() for skip in skip_ui_words):
                                continue
                            
                            # Validate name format (should be 1-4 words, mostly letters)
                            words = name.split()
                            if not (1 <= len(words) <= 4):
                                continue
                            
                            # Check if mostly letters (at least 70%)
                            if sum(c.isalpha() or c.isspace() for c in name) / len(name) < 0.7:
                                continue
                            
                            # Check if this name appears near "Admin" or "Moderator" text
                            try:
                                # Get the parent container
                                parent = link.find_element(By.XPATH, "./ancestor::div[position()<8]")
                                parent_text = parent.text
                                
                                # Check if "Admin" or "Moderator" appears near this name
                                # Look for pattern: "Name\nAdmin" or "Name\nModerator"
                                if name.lower() in parent_text.lower():
                                    # Find the position of the name in parent text
                                    name_pos = parent_text.lower().find(name.lower())
                                    if name_pos != -1:
                                        # Check text after the name (next 50 chars)
                                        text_after = parent_text[name_pos + len(name):name_pos + len(name) + 50].lower()
                                        if 'admin' in text_after or 'moderator' in text_after:
                                            # This is likely an admin
                                            if name.lower() not in [a.lower() for a in admin_names]:
                                                admin_names.append(name)
                                                admin_profile_urls.append(href)
                                                print(f"      ✅ Found admin: {name}")
                            except:
                                # If parent check fails, skip this link
                                continue
                                
                        except:
                            continue
                
                # ========== CLICK ON EACH ADMIN NAME TO GET PROFILE URL ==========
                if admin_names:
                    print(f"   🔍 Clicking on {len(admin_names)} admin names to get profile URLs...")
                    final_admin_profile_urls = []
                    current_page_url = driver.current_url
                    
                    for i, admin_name in enumerate(admin_names, 1):
                        print(f"   [{i}/{len(admin_names)}] Getting profile URL for: {admin_name}")
                        profile_url = _click_and_get_profile_url(driver, admin_name, current_page_url)
                        if profile_url:
                            final_admin_profile_urls.append(profile_url)
                        else:
                            # Use the href we found earlier if clicking didn't work
                            if i <= len(admin_profile_urls) and admin_profile_urls[i-1]:
                                final_admin_profile_urls.append(admin_profile_urls[i-1])
                            else:
                                final_admin_profile_urls.append('')
                        time.sleep(1)  # Small delay between clicks
                    
                    group_data['admin_names'] = '; '.join(admin_names)
                    group_data['admin_profile_urls'] = '; '.join(final_admin_profile_urls)
                    print(f"   ✅ Found {len(admin_names)} admins with profile URLs")
                else:
                    print(f"   ⚠️  No admins found")
                    
            except Exception as e:
                print(f"   Note: Could not extract admin names: {str(e)}")
            
            # ========== EXTRACT FIRST 5 MEMBER NAMES FROM "NEW TO THE GROUP" SECTION ==========
            try:
                # Navigate back to /members page if we went to /members/admins
                if '/admins' in driver.current_url:
                    print(f"   🔄 Navigating back to /members page...")
                    driver.get(members_url)
                    time.sleep(4)  # Wait for page to load
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                
                # Scroll to find "New to the group" section
                print(f"   🔍 Looking for 'New to the group' section...")
                
                # Find the "New to the group" heading
                try:
                    new_to_group_heading = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH,
                            "//*[contains(text(), 'New to the group') or contains(text(), 'New to the Group')]"))
                    )
                    
                    # Scroll to the heading
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", new_to_group_heading)
                    time.sleep(3)
                    
                    # Scroll down multiple times to load more members
                    print(f"   📜 Scrolling to load members...")
                    for i in range(8):
                        driver.execute_script("window.scrollBy(0, 600);")
                        time.sleep(1.5)
                    
                    # Get fresh page text after scrolling
                    page_text_after_scroll = driver.find_element(By.TAG_NAME, "body").text
                    print(f"   📝 Page text length after scroll: {len(page_text_after_scroll)} chars")
                    
                    # Find all profile links on the page
                    all_links = driver.find_elements(By.XPATH, "//a[contains(@href, 'facebook.com/')]")
                    print(f"   📝 Found {len(all_links)} total links on page")
                    
                    # Find the section starting from "New to the group"
                    new_to_group_pos = page_text_after_scroll.lower().find('new to the group')
                    if new_to_group_pos == -1:
                        print(f"   ⚠️  'New to the group' text not found in page")
                    else:
                        print(f"   📍 Found 'New to the group' at position {new_to_group_pos}")
                    
                    # Also try to find members by looking for "Joined" patterns
                    # Members typically have "Joined" text after their name
                    joined_pattern = r'\n([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})\n.*Joined'
                    joined_matches = re.findall(joined_pattern, page_text_after_scroll)
                    print(f"   📝 Found {len(joined_matches)} 'Name\nJoined' patterns")
                    
                    for link in all_links:
                        try:
                            name = link.text.strip()
                            href = link.get_attribute('href') or ''
                            
                            # Skip if no name or href
                            if not name or not href or len(name) < 2:
                                continue
                            
                            # Skip if it's an admin
                            if name.lower() in [a.lower() for a in admin_names]:
                                continue
                            
                            # Skip UI elements
                            skip_words = ['see all', 'see more', 'find a member', 'new to the group', 
                                        'learn more', 'admin', 'moderator', 'joined', 'joined on', 
                                        'joined about', 'works at', 'lives in', 'studied at']
                            if any(skip in name.lower() for skip in skip_words):
                                continue
                            
                            # Validate it's a profile link
                            url_lower = href.lower()
                            is_profile = (
                                'profile.php' in url_lower or
                                (url_lower.count('/') >= 3 and 
                                 'facebook.com/' in url_lower and 
                                 '/groups/' not in url_lower and 
                                 '/pages/' not in url_lower and
                                 '/events/' not in url_lower and
                                 '/marketplace/' not in url_lower and
                                 '/hashtag/' not in url_lower)
                            )
                            
                            if not is_profile:
                                continue
                            
                            # Check if this link appears after "New to the group" section
                            try:
                                # Get the parent container
                                parent = link.find_element(By.XPATH, "./ancestor::div[position()<10]")
                                parent_text = parent.text
                                
                                # Check if "Joined" appears near this name (indicates it's a member)
                                if name.lower() in parent_text.lower():
                                    name_pos = parent_text.lower().find(name.lower())
                                    if name_pos != -1:
                                        # Check text after the name (next 100 chars)
                                        text_after = parent_text[name_pos + len(name):name_pos + len(name) + 100].lower()
                                        if 'joined' in text_after:
                                            # This is likely a member
                                            if name.lower() not in [m.lower() for m in member_names]:
                                                # Validate name format (should be 1-4 words, mostly letters)
                                                words = name.split()
                                                if 1 <= len(words) <= 4:
                                                    # Check if mostly letters
                                                    if sum(c.isalpha() or c.isspace() for c in name) / len(name) > 0.7:
                                                        member_names.append(name)
                                                        member_profile_urls.append(href)
                                                        print(f"      ✅ Found member: {name}")
                                                        if len(member_names) >= 5:
                                                            break
                            except:
                                # If validation fails, try a simpler check
                                # Just check if name appears in the page text after "New to the group"
                                if new_to_group_pos != -1:
                                    name_pos = page_text_after_scroll.lower().find(name.lower())
                                    if name_pos > new_to_group_pos:
                                        # Name appears after "New to the group"
                                        if name.lower() not in [m.lower() for m in member_names]:
                                            words = name.split()
                                            if 1 <= len(words) <= 4:
                                                if sum(c.isalpha() or c.isspace() for c in name) / len(name) > 0.7:
                                                    member_names.append(name)
                                                    member_profile_urls.append(href)
                                                    print(f"      ✅ Found member: {name}")
                                                    if len(member_names) >= 5:
                                                        break
                        except:
                            continue
                    
                    # If we didn't find enough members via links, try regex method
                    if len(member_names) < 5 and joined_matches:
                        print(f"   🔄 Trying regex-based extraction for members...")
                        for match in joined_matches[:10]:  # Try first 10 matches
                            name = match.strip()
                            if name and len(name) > 1:
                                # Skip if it's an admin
                                if name.lower() in [a.lower() for a in admin_names]:
                                    continue
                                
                                # Skip UI elements
                                skip_words = ['see all', 'see more', 'find a member', 'new to the group', 
                                            'learn more', 'admin', 'moderator', 'joined', 'joined on', 
                                            'joined about', 'works at', 'lives in', 'studied at']
                                if any(skip in name.lower() for skip in skip_words):
                                    continue
                                
                                # Validate name format
                                words = name.split()
                                if 1 <= len(words) <= 4:
                                    if sum(c.isalpha() or c.isspace() for c in name) / len(name) > 0.7:
                                        if name.lower() not in [m.lower() for m in member_names]:
                                            # Try to find the profile link for this name
                                            href = ''
                                            try:
                                                name_link = driver.find_element(By.XPATH, 
                                                    f"//a[contains(text(), '{name}') and contains(@href, 'facebook.com/')]")
                                                href = name_link.get_attribute('href') or ''
                                            except:
                                                pass
                                            
                                            member_names.append(name)
                                            member_profile_urls.append(href)
                                            print(f"      ✅ Found member (regex): {name}")
                                            if len(member_names) >= 5:
                                                break
                    
                    if len(member_names) < 5:
                        print(f"   ⚠️  Only found {len(member_names)} members (expected 5)")
                    
                except Exception as e:
                    print(f"   Note: Could not find 'New to the group' section: {str(e)}")
                    import traceback
                    traceback.print_exc()
                
                # ========== CLICK ON EACH MEMBER NAME TO GET PROFILE URL AND SEND MESSAGE ==========
                if member_names:
                    # Limit to first 5 members
                    member_names = member_names[:5]
                    print(f"   🔍 Clicking on {len(member_names)} member names to get profile URLs and send messages...")
                    final_member_profile_urls = []
                    current_page_url = driver.current_url
                    
                    for i, member_name in enumerate(member_names, 1):
                        print(f"   [{i}/{len(member_names)}] Getting profile URL for: {member_name}")
                        # Send message to members (send_message=True)
                        profile_url = _click_and_get_profile_url(
                            driver, 
                            member_name, 
                            current_page_url,
                            send_message=True,  # Enable messaging for members
                            message_text="Hi"   # Message text
                        )
                        if profile_url:
                            final_member_profile_urls.append(profile_url)
                        else:
                            # Use the href we found earlier if clicking didn't work
                            if i <= len(member_profile_urls) and member_profile_urls[i-1]:
                                final_member_profile_urls.append(member_profile_urls[i-1])
                            else:
                                final_member_profile_urls.append('')
                        time.sleep(1)  # Small delay between clicks
                    
                    group_data['member_names'] = '; '.join(member_names)
                    group_data['member_profile_urls'] = '; '.join(final_member_profile_urls)
                    print(f"   ✅ Found {len(member_names)} members with profile URLs")
                else:
                    print(f"   ⚠️  No members found")
                    
            except Exception as e:
                print(f"   Note: Could not extract member names: {str(e)}")
                import traceback
                traceback.print_exc()
                
        except Exception as e:
            print(f"   ⚠️  Could not navigate to /members page: {str(e)}")
        
        # Print summary
        print(f"   ✅ Successfully extracted data")
        print(f"      Name: {group_data['group_name']}")
        print(f"      Members: {group_data['member_count']:,}")
        
        return group_data
        
    except Exception as e:
        print(f"   ❌ Error scraping {group_url}: {str(e)}")
        # If session expired, try to refresh the page
        if "invalid session id" in str(e).lower():
            print("   🔄 Session expired, attempting to refresh...")
            try:
                driver.refresh()
                time.sleep(2)
                return scrape_group_data(driver, group_url)  # Retry once
            except:
                pass
        return None


def scrape_multiple_groups(driver, group_urls, delay_between=3, login_func=None, credentials=None):
    """
    Scrape data from multiple group URLs
    
    Args:
        driver: Selenium WebDriver instance
        group_urls (list): List of Facebook group URLs
        delay_between (int): Delay in seconds between scrapes
        login_func: Function to re-login if session expires
        credentials: Login credentials (email, password)
    
    Returns:
        list: List of group data dictionaries
    """
    print(f"\n📊 Starting extraction from {len(group_urls)} groups...")
    print("=" * 60)
    
    results = []
    
    for i, url in enumerate(group_urls, 1):
        print(f"\n[{i}/{len(group_urls)}]")
        
        # Check login status every 10 groups
        if i % 10 == 1 and i > 1 and login_func and credentials:
            print("🔍 Checking login status...")
            try:
                # Try to access Facebook home to check if still logged in
                driver.get("https://www.facebook.com")
                time.sleep(2)
                page_text = driver.find_element(By.TAG_NAME, "body").text.lower()
                if any(phrase in page_text for phrase in ['log in', 'sign up', 'create account']):
                    print("⚠️  Session expired, attempting to re-login...")
                    email, password = credentials
                    login_success = login_func(driver, email, password)
                    if login_success:
                        print("✅ Re-login successful")
                    else:
                        print("❌ Re-login failed - continuing with limited access")
            except Exception as e:
                print(f"⚠️  Could not check login status: {str(e)}")
        
        group_data = scrape_group_data(driver, url)
        
        if group_data:
            results.append(group_data)
        
        # Add delay between extractions
        if i < len(group_urls):
            time.sleep(delay_between)
    
    print("\n" + "=" * 60)
    print(f"✅ Successfully extracted data from {len(results)}/{len(group_urls)} groups")
    
    return results


def validate_group_url(url):
    """
    Validate if URL is a Facebook group URL
    
    Args:
        url (str): URL to validate
    
    Returns:
        bool: True if valid Facebook group URL
    """
    if not url:
        return False
    
    # Check if URL contains facebook.com/groups/
    if 'facebook.com' not in url.lower():
        return False
    
    if '/groups/' not in url.lower():
        return False
    
    return True


def format_member_count_text(text):
    """
    Parse member count text and return integer
    
    Handles formats like:
    - "1,234 members"
    - "1.2K members"
    - "13.6K members"
    - "1.5M members"
    
    Args:
        text (str): Member count text
    
    Returns:
        int: Parsed member count
    """
    if not text:
        return 0
    
    try:
        # Remove extra whitespace and convert to lowercase
        text = text.strip().lower()
        
        # Extract numbers with decimal support
        number_match = re.search(r'([\d.,]+)\s*[km]?', text)
        if not number_match:
            return 0
        
        number_str = number_match.group(1).replace(',', '')
        number = float(number_str)
        
        # Handle "K" suffix (thousands) - e.g., "13.6K" -> 13600
        if 'k' in text and 'km' not in text:  # 'km' for kilometers, 'k' for thousands
            return int(number * 1000)
        
        # Handle "M" suffix (millions) - e.g., "1.5M" -> 1500000
        if 'm' in text and 'member' in text:
            return int(number * 1000000)
        
        # Regular number without suffix
        if re.search(r'\d+', text):
            return int(number)
        
        return 0
        
    except (ValueError, AttributeError):
        return 0


if __name__ == "__main__":
    """Test the scraper functionality"""
    print("=" * 60)
    print("🧪 Testing Phase 1: Core Group Scraper")
    print("=" * 60)
    
    # Import login module to get driver
    from login import get_driver_with_config
    
    # Get driver
    driver = get_driver_with_config()
    
    if not driver:
        print("❌ Failed to initialize WebDriver")
        exit(1)
    
    # Test URLs (you can replace these with actual group URLs)
    test_urls = [
        "https://www.facebook.com/groups/example1",
        "https://www.facebook.com/groups/example2"
    ]
    
    print("\n⚠️  Note: Test will attempt to scrape real URLs")
    print("   Make sure to be logged in with login_to_facebook() first")
    
    # Try to scrape
    results = scrape_multiple_groups(driver, test_urls, delay_between=5)
    
    # Print results
    print(f"\n📊 Extraction Results:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['group_name']}")
        print(f"   URL: {result['group_url']}")
        print(f"   Members: {result['member_count']:,}")
        print(f"   Description: {result['description'][:100]}...")
    
    # Cleanup
    driver.quit()
    print("\n✅ Test complete!")
