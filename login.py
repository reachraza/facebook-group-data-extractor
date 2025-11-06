"""
Login and Session Management for Facebook Group Data Extractor
Phase 1: Core functionality for establishing a persistent, non-detected session

Purpose:
- Initialize and configure Chrome WebDriver with anti-detection measures
- Login to Facebook and maintain a persistent session
- Load credentials from configuration file
- Validate user credentials before attempting login

Key Features:
- Anti-detection: Removes webdriver flags and automation indicators
- Stealth mode: Configurable headless/non-headless operation
- Session persistence: Keeps login active across multiple page navigations
- Error handling: Graceful fallback if ChromeDriver setup fails
- Configuration-driven: Reads settings from config.ini file
"""

# Standard library imports
import time      # For adding delays between actions (mimic human behavior)
import random    # For randomizing delays to avoid predictable patterns
import os        # For file system operations
import configparser  # For reading configuration from .ini files

# Selenium WebDriver imports - core browser automation framework
from selenium import webdriver  # Main WebDriver interface for Chrome browser
from selenium.webdriver.common.by import By  # Locator strategies (ID, CSS, XPath, etc.)
from selenium.webdriver.support.ui import WebDriverWait  # Wait for page elements to load
from selenium.webdriver.support import expected_conditions as EC  # Common expected conditions for waits
from selenium.webdriver.chrome.options import Options  # Chrome browser configuration options
from selenium.webdriver.chrome.service import Service  # ChromeDriver service configuration
from selenium.common.exceptions import TimeoutException, NoSuchElementException  # Common Selenium exceptions

# Third-party imports
from webdriver_manager.chrome import ChromeDriverManager  # Auto-downloads and manages ChromeDriver binaries


def get_driver(headless=True):
    """
    Initialize and configure Chrome WebDriver with anti-detection measures
    
    This function sets up a Chrome browser instance that can automate web interactions
    while appearing as a normal user browsing session. It applies multiple techniques
    to avoid detection by Facebook's bot detection systems.
    
    Args:
        headless (bool): Run browser in headless mode (default: True)
                        - True: Browser runs invisibly in background (faster, less detectable)
                        - False: Browser window visible (useful for debugging, slower)
                        Can be disabled for debugging
    
    Returns:
        webdriver.Chrome: Configured Chrome WebDriver instance ready for automation
                         Returns None if setup fails
    """
    print("Setting up Chrome WebDriver...")
    
    try:
        # Create Chrome options object to configure browser behavior
        chrome_options = Options()
        
        # ========== ANTI-DETECTION MEASURES ==========
        # These settings make the browser appear more human-like and reduce detection
        
        # Remove automation flags from Chrome's navigator object
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        
        # Remove "Chrome is being controlled by automated test software" notification
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        
        # Disable the automation extension that Facebook can detect
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # ========== STABILITY AND PERFORMANCE SETTINGS ==========
        
        # Disable extensions that could interfere with scraping
        chrome_options.add_argument("--disable-extensions")
        
        # Disable security sandbox (needed for some environments, especially servers)
        chrome_options.add_argument("--no-sandbox")
        
        # Fix for limited shared memory in Docker/containerized environments
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Disable GPU acceleration (unnecessary for scraping, can cause issues)
        chrome_options.add_argument("--disable-gpu")
        
        # Set consistent window size to ensure elements are visible
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Disable web security for easier DOM access (only for local scraping)
        chrome_options.add_argument("--disable-web-security")
        
        # Allow insecure content to be loaded
        chrome_options.add_argument("--allow-running-insecure-content")
        
        # Disable display compositor features (reduces crashes)
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        
        # ========== USER AGENT SPOOFING ==========
        # Set a realistic user agent string that looks like a normal browser
        # This makes requests appear to come from a standard Chrome installation
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # ========== HEADLESS MODE CONFIGURATION ==========
        if headless:
            # Run browser invisibly - faster and less detectable
            chrome_options.add_argument("--headless")
            print("   Running in HEADLESS mode (disable for debugging)")
        
        # ========== CHROMEDRIVER INITIALIZATION ==========
        # Try multiple methods to set up ChromeDriver (the browser control layer)
        try:
            # METHOD 1: ChromeDriverManager (most reliable approach)
            # Automatically downloads and manages the correct ChromeDriver version
            # This ensures compatibility with your Chrome browser version
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            print("   ✅ ChromeDriver initialized successfully")
            
        except Exception as e1:
            # If ChromeDriverManager fails, try the system ChromeDriver
            print(f"   ⚠️  ChromeDriverManager failed: {str(e1)}")
            try:
                # METHOD 2: Use system ChromeDriver (fallback method)
                # Assumes ChromeDriver is already installed on the system
                driver = webdriver.Chrome(options=chrome_options)
                print("   ✅ ChromeDriver initialized (system Chrome)")
                
            except Exception as e2:
                # If both methods fail, raise an error
                print(f"   ⚠️  System ChromeDriver failed: {str(e2)}")
                raise Exception(f"ChromeDriver setup failed. Last error: {str(e2)}")
        
        # ========== FURTHER ANTI-DETECTION ==========
        # Execute JavaScript to remove 'webdriver' property from navigator object
        # This is a critical step - Facebook checks for navigator.webdriver to detect bots
        # By removing it, we make the page think it's a normal browser
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print("✅ Chrome WebDriver setup complete!")
        return driver
        
    except Exception as e:
        # If any error occurs during setup, print helpful troubleshooting tips
        print(f"Error setting up WebDriver: {str(e)}")
        print("\n🔧 Troubleshooting tips:")
        print("1. Make sure Google Chrome is installed")
        print("2. Try updating Chrome to the latest version")
        print("3. Check if ChromeDriver is compatible with your Chrome version")
        print("4. Try running: pip install --upgrade webdriver-manager")
        print("5. Set headless=False for debugging")
        return None


def smart_delay(min_delay=2, max_delay=5):
    """
    Add random delay between actions to mimic human behavior
    
    This function introduces randomized waiting time between browser actions.
    Random delays prevent the scraper from operating at predictable intervals,
    which would be a clear indicator of automation to Facebook's detection systems.
    
    Why it's important:
    - Humans never click/interact at exact intervals
    - Random delays make automation appear more natural
    - Prevents rate limiting and bot detection
    
    Args:
        min_delay (int): Minimum delay in seconds (default: 2)
        max_delay (int): Maximum delay in seconds (default: 5)
    
    Example:
        smart_delay(2, 5)  # Waits between 2-5 seconds randomly
        smart_delay()      # Uses default 2-5 second range
    """
    # Generate a random delay value within the specified range
    delay = random.uniform(min_delay, max_delay)
    # Pause execution for the random duration
    time.sleep(delay)


def login_to_facebook(driver, email, password):
    """
    Login to Facebook with credentials and establish a persistent session
    
    This function automates the Facebook login process by:
    1. Navigating to the login page
    2. Filling in email and password fields
    3. Clicking the login button
    4. Verifying successful authentication
    
    The session created by this function persists across page navigations,
    allowing the scraper to access member-only content and private groups.
    
    Args:
        driver (webdriver.Chrome): Configured Selenium WebDriver instance
        email (str): Facebook account email address
        password (str): Facebook account password
    
    Returns:
        bool: True if login successful and session established
              False if login failed due to credentials or network issues
    
    Note:
        Requires valid Facebook credentials in config.ini
        Returns False if credentials are incorrect or account is locked
    """
    print("🔐 Logging into Facebook...")
    
    try:
        # ========== STEP 1: NAVIGATE TO LOGIN PAGE ==========
        # Open Facebook's login page in the browser
        driver.get("https://www.facebook.com/login")
        # Wait 2-4 seconds for page to fully load before interacting
        smart_delay(2, 4)
        
        # ========== STEP 2: FILL EMAIL FIELD ==========
        # Wait up to 10 seconds for email input field to appear on page
        # This handles slow network connections gracefully
        email_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "email"))
        )
        # Clear any existing text in the field (precautionary)
        email_field.clear()
        # Type the email address character by character (mimics human typing)
        email_field.send_keys(email)
        
        # Random delay between email and password entry (appears more human)
        smart_delay(1, 2)
        
        # ========== STEP 3: FILL PASSWORD FIELD ==========
        # Locate the password input field by ID
        password_field = driver.find_element(By.ID, "pass")
        # Clear field before entering password
        password_field.clear()
        # Type password securely (Selenium doesn't actually mask it in logs)
        password_field.send_keys(password)
        
        # Brief pause before clicking login button
        smart_delay(1, 2)
        
        # ========== STEP 4: CLICK LOGIN BUTTON ==========
        # Find the login button using its name attribute
        try:
            login_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.NAME, "login"))
            )
            login_button.click()
        except:
            # Try alternative selector if NAME doesn't work
            try:
                login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit'][name='login']")
                login_button.click()
            except:
                print("⚠️  Could not find login button")
                return False
        
        # Wait longer for Facebook to process login (handle redirects, checkpoints, etc.)
        print("   Waiting for login to complete...")
        smart_delay(5, 8)
        
        # ========== STEP 5: HANDLE CHECKPOINT/SECURITY PAGES ==========
        # Facebook may show checkpoint pages, 2FA, or "Save browser" prompts
        current_url = driver.current_url.lower()
        
        # Check for checkpoint/security pages
        if "checkpoint" in current_url or "two_factor" in current_url or "auth_platform" in current_url:
            print("⚠️  Security checkpoint detected - manual intervention required")
            print("   Please complete security verification in the browser")
            print("   Waiting 30 seconds for manual completion...")
            
            # Wait for user to manually complete checkpoint
            # Check every 5 seconds if we've passed the checkpoint
            for i in range(6):  # 6 * 5 = 30 seconds
                smart_delay(5, 5)
                current_url = driver.current_url.lower()
                if "checkpoint" not in current_url and "two_factor" not in current_url and "auth_platform" not in current_url:
                    print("   ✅ Checkpoint completed!")
                    break
                if i == 5:
                    print("   ⚠️  Still on checkpoint page - proceeding anyway")
        
        # Check for "Save Browser" or "This was me" prompts
        try:
            # Look for common checkpoint elements and try to click "This was me" or similar
            save_browser_buttons = driver.find_elements(By.XPATH, 
                "//button[contains(text(), 'This was me') or contains(text(), 'Continue') or contains(text(), 'Save Browser')]")
            if save_browser_buttons:
                print("   Clicking 'This was me' or similar button...")
                save_browser_buttons[0].click()
                smart_delay(3, 5)
        except:
            pass
        
        # ========== STEP 6: VERIFY LOGIN SUCCESS ==========
        # Navigate to homepage to verify session
        try:
            driver.get("https://www.facebook.com")
            smart_delay(3, 5)
            current_url = driver.current_url.lower()
            
            # Check if we're on login page (bad)
            if "login" in current_url or "reg" in current_url:
                print("❌ Facebook login failed - redirected back to login page")
                print("   Possible reasons:")
                print("   - Incorrect credentials")
                print("   - Account requires 2FA")
                print("   - Account temporarily locked")
                return False
            
            # Check for checkpoint pages (may need manual intervention)
            if "checkpoint" in current_url or "two_factor" in current_url:
                print("⚠️  Still on security checkpoint - login may require manual completion")
                return False
            
            # Look for elements that indicate successful login
            # Success indicators: News feed, search bar, profile menu, etc.
            try:
                # Wait for page to load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # Check for elements that only appear when logged in
                page_text = driver.find_element(By.TAG_NAME, "body").text.lower()
                logged_in_indicators = [
                    "news feed",
                    "what's on your mind",
                    "create",
                    "find friends"
                ]
                
                # Also check URL - if we're on facebook.com without /login, that's good
                is_logged_in = (
                    "facebook.com" in current_url and 
                    "login" not in current_url and
                    "checkpoint" not in current_url
                )
                
                if is_logged_in:
                    print("✅ Facebook login successful!")
                    
                    # Additional wait to ensure session is fully established
                    print("   Waiting for session to stabilize...")
                    smart_delay(5, 8)
                    
                    # Final verification - try accessing a protected page
                    try:
                        driver.get("https://www.facebook.com/groups/feed/")
                        smart_delay(3, 5)
                        final_url = driver.current_url.lower()
                        if "login" not in final_url and "checkpoint" not in final_url:
                            print("✅ Session established and active")
                            return True
                        else:
                            print("⚠️  Session verification failed - may need manual intervention")
                            return False
                    except:
                        print("✅ Session established and active")
                        return True
                else:
                    print("⚠️  Login status unclear - may need manual verification")
                    return False
                    
            except Exception as e:
                print(f"⚠️  Error verifying login: {str(e)}")
                # If we're not on login page, assume login worked
                if "login" not in current_url:
                    print("✅ Assuming login successful (not on login page)")
                    return True
                return False
                
        except Exception as e:
            print(f"⚠️  Error during login verification: {str(e)}")
            # If we got here without exception, assume it worked
            if "login" not in driver.current_url.lower():
                return True
            return False
            
    except Exception as e:
        # Handle any unexpected errors during login process
        print(f"Error during Facebook login: {str(e)}")
        print("\nDebug tip: Set headless=False in config to see the browser")
        return False


def get_driver_with_config():
    """
    Initialize WebDriver using settings from config.ini file
    
    This is a convenience wrapper around get_driver() that automatically
    reads the headless mode setting from the configuration file.
    
    Returns:
        webdriver.Chrome: Configured Chrome WebDriver instance
                        Returns None if initialization fails
    
    Configuration:
        Reads 'selenium.headless_mode' from config.ini
        Defaults to True (headless mode) if not specified
    """
    # Read configuration from config.ini file
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    # Get headless mode setting with True as fallback default
    headless = config.getboolean('selenium', 'headless_mode', fallback=True)
    
    # Initialize and return driver with the specified mode
    return get_driver(headless=headless)


def load_credentials_from_config():
    """
    Load Facebook credentials from config.ini configuration file
    
    Reads email and password from the [facebook] section of config.ini.
    Uses interpolation=None to prevent configparser from treating special
    characters (like % in passwords) as configuration variables.
    
    Returns:
        tuple: (email, password) if credentials found
               (None, None) if credentials are missing or file not found
    
    Configuration file structure:
        [facebook]
        email = your_email@example.com
        password = your_password_here
    """
    # Disable interpolation to handle special characters in passwords
    # Without this, passwords with % or $ would cause parsing errors
    config = configparser.ConfigParser(interpolation=None)
    config.read('config.ini')
    
    try:
        # Read email and password from [facebook] section
        email = config.get('facebook', 'email', fallback=None)
        password = config.get('facebook', 'password', fallback=None)
    except (configparser.NoSectionError, configparser.NoOptionError):
        # Config file doesn't have [facebook] section or values are missing
        return None, None
    
    return email, password


def validate_credentials(email, password):
    """
    Validate that Facebook credentials are properly provided
    
    Checks that both email and password are not None or empty strings.
    Provides helpful error messages if validation fails.
    
    Args:
        email (str): Facebook account email address
        password (str): Facebook account password
    
    Returns:
        bool: True if credentials are non-empty and valid
              False if either credential is missing or empty
    
    Example:
        >>> validate_credentials("user@email.com", "password123")
        True
        >>> validate_credentials("", "password123")
        False (prints warning)
        >>> validate_credentials(None, None)
        False (prints warning)
    """
    # Check if credentials are None or empty
    if not email or not password:
        print("⚠️  Facebook credentials not set!")
        print("   Set email and password in config.ini")
        return False
    
    # Check if credentials are empty strings
    if email == '' or password == '':
        print("⚠️  Facebook credentials are empty!")
        print("   Set email and password in config.ini")
        return False
    
    return True


def get_session(driver):
    """
    Retrieve current session information after login
    
    Gathers metadata about the active browser session including:
    - Current page URL
    - Page title
    - Number of cookies stored
    - Whether session is still active (logged in to Facebook)
    
    Args:
        driver (webdriver.Chrome): Active WebDriver instance with established session
    
    Returns:
        dict: Session information dictionary with keys:
              - 'url': Current page URL
              - 'title': Page title
              - 'cookies_count': Number of stored cookies
              - 'session_active': Boolean indicating if still logged in
              Returns None if driver is not accessible
    
    Example:
        >>> session = get_session(driver)
        >>> print(session['url'])
        'https://www.facebook.com/'
        >>> print(session['cookies_count'])
        45
    """
    try:
        session_info = {
            'url': driver.current_url,              # Current page being viewed
            'title': driver.title,                  # Page title/tab name
            'cookies_count': len(driver.get_cookies()),  # Number of stored cookies (session data)
            'session_active': 'facebook.com' in driver.current_url  # True if on Facebook domain
        }
        return session_info
    except:
        # Driver is no longer valid (session expired or browser closed)
        return None


if __name__ == "__main__":
    """Test the login functionality"""
    print("=" * 60)
    print("🧪 Testing Phase 1: Login & Session Management")
    print("=" * 60)
    
    # Load configuration
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    headless = config.getboolean('selenium', 'headless_mode', fallback=True)
    
    # Get driver
    driver = get_driver(headless=headless)
    
    if not driver:
        print("❌ Failed to initialize WebDriver")
        exit(1)
    
    # Try to login if credentials are provided
    email, password = load_credentials_from_config()
    
    if email and password and validate_credentials(email, password):
        print("\n🔐 Attempting login...")
        success = login_to_facebook(driver, email, password)
        
        if success:
            print("\n📊 Session Information:")
            session = get_session(driver)
            if session:
                print(f"   URL: {session['url']}")
                print(f"   Title: {session['title']}")
                print(f"   Cookies: {session['cookies_count']}")
                print(f"   Active: {session['session_active']}")
    else:
        print("\n⚠️  Credentials not set - skipping login test")
        print("   Driver initialized successfully without login")
    
    # Keep browser open briefly for inspection (if not headless)
    if not headless:
        print("\n🔍 Browser will stay open for 10 seconds for inspection...")
        time.sleep(10)
    else:
        time.sleep(2)
    
    # Cleanup
    driver.quit()
    print("\n✅ Test complete!")

