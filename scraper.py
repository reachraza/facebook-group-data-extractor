"""
Core Group Scraper for Facebook Group Data Extractor
Phase 1: Function to navigate to a single known group URL and extract data
"""
import time
import re
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


def scrape_group_data(driver, group_url):
    """
    Extract data from a single Facebook group URL
    
    Extracts:
    - Group Name
    - Group URL
    - Visible Member Count
    - Short Description
    
    Args:
        driver: Selenium WebDriver instance
        group_url (str): Facebook group URL to scrape
    
    Returns:
        dict: Group data containing name, url, member_count, description
    """
    print(f"📊 Scraping group: {group_url}")
    
    try:
        # Navigate to group page
        driver.get(group_url)
        time.sleep(3)  # Wait for page to load
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        group_data = {
            'group_name': 'Unknown',
            'group_url': group_url,
            'member_count': 0,
            'description': 'No description available',
            'admin_names': '',
            'admin_profile_urls': '',
            'extraction_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Check if we're on a login page or restricted page
        page_text = driver.find_element(By.TAG_NAME, "body").text.lower()
        if any(phrase in page_text for phrase in ['log in', 'sign up', 'create account', 'forgot password']):
            print("   ⚠️  Login required - limited data available")
            # Try to extract any visible group info
            try:
                # Look for group name in title or meta tags
                title = driver.title
                if title and 'facebook' not in title.lower():
                    group_data['group_name'] = title
                    print(f"   ✅ Found group name from title: {title}")
            except:
                pass
            return group_data
        
        # Extract group name - try multiple selectors
        name_selectors = [
            "h1",  # Most common
            "[data-testid='group-name']",
            "h1[class*='group']",
            "[role='main'] h1",
            "h2"  # Fallback
        ]
        
        for selector in name_selectors:
            try:
                name_element = driver.find_element(By.CSS_SELECTOR, selector)
                if name_element and name_element.text.strip():
                    group_data['group_name'] = name_element.text.strip()
                    print(f"   ✅ Found group name: {group_data['group_name']}")
                    break
            except NoSuchElementException:
                continue
        
        # Extract member count - try multiple selectors
        member_selectors = [
            "span[class*='member']",
            "[class*='members']",
            "[aria-label*='member']",
            "*[href*='groups/*/members']",
            "a[href*='members']",
            "[data-testid*='member']"
        ]
        
        # Extract member count - better approach: look for specific patterns in page text
        try:
            # Get all page text
            page_text = driver.find_element(By.TAG_NAME, "body").text
            
            # Look for patterns like "X.XK members" or "X members" in the page
            # This is more reliable than searching all DOM elements
            member_patterns = [
                r'(\d+\.?\d*)\s*K?\s*members?\s*·',  # "13.6K members ·" or "6000 members ·"
                r'(\d+\.?\d*)\s*members?\s*',        # "6000 members"
                r'(\d+\.?\d*K)\s*members?',          # "13.6K members"
                r'(\d+\.?\d*M)\s*members?',          # "1.5M members"
                r'(\d+\.?\d*)\s*people',            # "6000 people"
            ]
            
            for pattern in member_patterns:
                matches = re.findall(pattern, page_text, re.IGNORECASE)
                for match in matches:
                    # Extract number from match
                    number_str = str(match).replace(',', '').replace('K', '').replace('M', '').strip()
                    try:
                        number = float(number_str)
                        # Apply multiplier if needed
                        if 'K' in str(match).upper():
                            number = number * 1000
                        elif 'M' in str(match).upper():
                            number = number * 1000000
                        
                        if number > 0:
                            group_data['member_count'] = int(number)
                            print(f"   ✅ Found member count: {int(number):,}")
                            break
                    except:
                        continue
                if group_data['member_count'] > 0:
                    break
            
            # Fallback: Try specific selectors if regex didn't work
            if group_data['member_count'] == 0:
                for selector in member_selectors:
                    try:
                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        for element in elements:
                            text = element.text.strip()
                            # More specific validation
                            if text and re.search(r'^[\d.,]+\s*[km]?\s*members?', text.lower()):
                                count = format_member_count_text(text)
                                if count > 0:
                                    group_data['member_count'] = count
                                    print(f"   ✅ Found member count: {count:,} (from: {text})")
                                    break
                        if group_data['member_count'] > 0:
                            break
                    except:
                        continue
        except Exception as e:
            print(f"   Note: Could not parse member count: {str(e)}")
        
        # Extract description - try multiple selectors including About section
        description_selectors = [
            "[aria-label*='About']",
            "[class*='description']",
            "[class*='about']",
            "div[role='article'] p",
            "[dir='auto'] p",
            "span[dir='auto']"
        ]
        
        # Look for "About" section text properly
        try:
            # Get all text on the page
            page_text = driver.find_element(By.TAG_NAME, "body").text
            
            # Try to find About section - look for text after "About" header
            if 'About' in page_text:
                lines = page_text.split('\n')
                found_about = False
                skip_next = False
                for i, line in enumerate(lines):
                    line_lower = line.lower().strip()
                    line_stripped = line.strip()
                    
                    # Skip empty lines
                    if not line_stripped:
                        continue
                    
                    # Look for "About" followed by description
                    if 'about' in line_lower and not found_about:
                        # Check if this is actually the "About" header (not just containing "about" word)
                        if line_lower in ['about', 'about this group']:
                            found_about = True
                            skip_next = True  # Skip the first line after "About"
                            continue
                    
                    # After "About", get the next substantial line as description
                    if found_about:
                        if skip_next:
                            skip_next = False
                            continue
                        
                        # Take first substantial line after About
                        if len(line_stripped) > 20 and group_data['group_name'] not in line_stripped:
                            desc = line_stripped[:500]
                            # Skip common navigation items and privacy settings
                            skip_words = ['public', 'private', 'visible', 'recent media', 'discussion', 'events', 'media', 
                                        'anyone can see', 'only members', 'tags', 'members', 'activity', 'created']
                            if not any(skip in desc.lower() for skip in skip_words):
                                group_data['description'] = desc
                                print(f"   ✅ Found description in About section (length: {len(desc)})")
                                break
        except Exception as e:
            print(f"   Note: Could not parse About section: {str(e)}")
        
        # If not found, try specific selectors
        if group_data['description'] == 'No description available':
            for selector in description_selectors:
                try:
                    desc_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in desc_elements:
                        text = element.text.strip()
                        # Avoid using group name as description
                        if text and len(text) > 20 and group_data['group_name'] not in text:
                            desc = text[:500]  # Limit to 500 chars
                            group_data['description'] = desc
                            print(f"   ✅ Found description (length: {len(desc)})")
                            break
                    if group_data['description'] != 'No description available':
                        break
                except Exception:
                    continue

        # Extract admin names and profile URLs when visible (People/Admins section)
        try:
            # Try to navigate to People tab if present
            people_tab_candidates = [
                (By.PARTIAL_LINK_TEXT, 'People'),
                (By.XPATH, "//a[contains(@href, '/people') and contains(., 'People')]")
            ]
            clicked_people = False
            for by_, val in people_tab_candidates:
                try:
                    el = driver.find_element(by_, val)
                    if el:
                        el.click()
                        time.sleep(2)
                        clicked_people = True
                        break
                except Exception:
                    continue

            # If People tab is not clickable, stay on current page and try to locate admin chips/cards
            admin_names: list[str] = []
            admin_urls: list[str] = []

            # Candidates for admin elements - prioritize links within Admin context
            admin_xpath_candidates = [
                # Link under a node that contains an Admin badge
                "//div[.//span[contains(translate(., 'ADMIN', 'admin'), 'admin')]]//a[contains(@href, 'facebook.com/') and @role='link']",
                # Any profile link with nearby text 'Admin'
                "//a[contains(@href, 'facebook.com/') and @role='link' and (contains(../., 'Admin') or contains(../../., 'Admin'))]",
            ]

            for xp in admin_xpath_candidates:
                try:
                    anchors = driver.find_elements(By.XPATH, xp)
                except Exception:
                    anchors = []
                for a in anchors:
                    try:
                        name = a.text.strip()
                        href = a.get_attribute('href') or ''
                        if not href:
                            continue
                        url_l = href.lower()
                        # Exclude obvious non-admin/non-profile links
                        if (
                            '/groups/' in url_l or
                            '/hashtag/' in url_l or
                            'l.facebook.com' in url_l or
                            '/help/727473' in url_l or
                            '/search/top' in url_l
                        ):
                            continue
                        # Prefer profile-like links
                        if not (
                            'profile.php?id=' in url_l or
                            '/people/' in url_l or
                            (url_l.count('/') >= 3 and 'facebook.com/' in url_l and '?' not in url_l)
                        ):
                            continue
                        # Require an Admin context nearby (text check on ancestors)
                        try:
                            ctx_text = (a.get_attribute('outerHTML') or '') + (a.get_attribute('innerText') or '')
                        except Exception:
                            ctx_text = name
                        # name sanity
                        if name and name.lower() not in [n.lower() for n in admin_names]:
                            admin_names.append(name)
                            admin_urls.append(href)
                        if len(admin_names) >= 3:  # cap to first 3 admins
                            break
                    except Exception:
                        continue
                if len(admin_names) >= 1:
                    break

            if admin_names:
                group_data['admin_names'] = '; '.join(admin_names)
                group_data['admin_profile_urls'] = '; '.join(admin_urls[:len(admin_names)])
                print(f"   ✅ Found admins: {group_data['admin_names']}")
        except Exception as e:
            print(f"   Note: Could not extract admin info: {str(e)}")
        
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

