"""
Login and Session Management for Facebook Group Data Extractor
Phase 1: Core functionality for establishing a persistent, non-detected session
"""

import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import configparser
import os
import logging
from logging import log
from captcha_solver import FacebookCaptchaSolver

log = logging.getLogger(__name__)          # <-- proper logger

# ------------------------------------------------------------------
# Add a helper that runs after you click “Log In”
# ------------------------------------------------------------------
def _handle_captcha(driver, solver: FacebookCaptchaSolver) -> bool:
    attempts = 3
    for attempt in range(1, attempts + 1):
        if solver.solve(driver):
            return True
        log.warning(f"Captcha solve attempt {attempt}/{attempts} failed")
        time.sleep(3)
    return False

def get_driver(headless=True):
    """
    Get configured Chrome WebDriver with anti-detection measures
    
    Args:
        headless (bool): Run browser in headless mode (default: True)
        Can be disabled for debugging
    
    Returns:
        webdriver.Chrome: Configured Chrome WebDriver instance
    """
    print("Setting up Chrome WebDriver...")
    
    try:
        chrome_options = Options()
        
        # Stealth options to avoid detection
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        
        # User agent to appear more human
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        if headless:
            chrome_options.add_argument("--headless")
            print("   Running in HEADLESS mode (disable for debugging)")
        
        # Setup ChromeDriver
        try:
            # Method 1: Use ChromeDriverManager (most reliable)
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            print("   ✅ ChromeDriver initialized successfully")
            
        except Exception as e1:
            print(f"   ⚠️  ChromeDriverManager failed: {str(e1)}")
            try:
                # Method 2: Use system ChromeDriver
                driver = webdriver.Chrome(options=chrome_options)
                print("   ✅ ChromeDriver initialized (system Chrome)")
                
            except Exception as e2:
                print(f"   ⚠️  System ChromeDriver failed: {str(e2)}")
                raise Exception(f"ChromeDriver setup failed. Last error: {str(e2)}")
        
        # Execute script to remove webdriver property
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print("✅ Chrome WebDriver setup complete!")
        return driver
        
    except Exception as e:
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
    Add random delay to mimic human behavior
    
    Args:
        min_delay (int): Minimum delay in seconds
        max_delay (int): Maximum delay in seconds
    """
    delay = random.uniform(min_delay, max_delay)
    time.sleep(delay)


def login_to_facebook(driver, email, password, twocaptcha_api_key: str):
    """
    Login to Facebook with credentials and establish a persistent session
    
    Args:
        driver: Selenium WebDriver instance
        email (str): Facebook email
        password (str): Facebook password
    
    Returns:
        bool: True if login successful, False otherwise
    """
    print("🔐 Logging into Facebook...")
    
    try:
        solver = FacebookCaptchaSolver(twocaptcha_api_key)
        # Navigate to Facebook login
        driver.get("https://www.facebook.com/login")
        smart_delay(2, 4)
        
        # Wait for email field and enter credentials
        email_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "email"))
        )
        email_field.clear()
        email_field.send_keys(email)
        
        smart_delay(1, 2)
        
        # Enter password
        password_field = driver.find_element(By.ID, "pass")
        password_field.clear()
        password_field.send_keys(password)
        
        smart_delay(1, 2)
        
        # Click login button
        login_button = driver.find_element(By.NAME, "login")
        login_button.click()

        smart_delay(10, 20)
        # ----- CAPTCHA handling loop -----
        if not _handle_captcha(driver, solver):
            print("CAPTCHA could not be solved – aborting login")
            return False
        
        # Wait for login to complete
        smart_delay(4, 7)
        
        # Check if login was successful
        if "facebook.com" in driver.current_url and "login" not in driver.current_url:
            print("✅ Facebook login successful!")
            print("✅ Session established and active")
            return True
        else:
            print("Facebook login failed - check credentials")
            return False
            
    except Exception as e:
        print(f"Error during Facebook login: {str(e)}")
        print("\nDebug tip: Set headless=False in config to see the browser")
        return False


def get_driver_with_config():
    """
    Get driver with configuration from config.ini
    
    Returns:
        webdriver.Chrome: Configured Chrome WebDriver instance
    """
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    headless = config.getboolean('selenium', 'headless_mode', fallback=True)
    
    return get_driver(headless=headless)


def load_credentials_from_config():
    """
    Load Facebook credentials from config.ini
    
    Returns:
        tuple: (email, password) or (None, None) if not found
    """
    # Use interpolation=None to treat special chars like % literally in passwords
    config = configparser.ConfigParser(interpolation=None)
    config.read('config.ini')
    
    try:
        email = config.get('facebook', 'email', fallback=None)
        password = config.get('facebook', 'password', fallback=None)
    except (configparser.NoSectionError, configparser.NoOptionError):
        return None, None
    
    return email, password


def validate_credentials(email, password):
    """
    Validate that credentials are provided
    
    Args:
        email (str): Facebook email
        password (str): Facebook password
    
    Returns:
        bool: True if credentials are valid
    """
    if not email or not password:
        print("⚠️  Facebook credentials not set!")
        print("   Set email and password in config.ini")
        return False
    
    if email == '' or password == '':
        print("⚠️  Facebook credentials are empty!")
        print("   Set email and password in config.ini")
        return False
    
    return True


def get_session(driver):
    """
    Get session information after login
    
    Args:
        driver: Selenium WebDriver instance
    
    Returns:
        dict: Session information
    """
    try:
        session_info = {
            'url': driver.current_url,
            'title': driver.title,
            'cookies_count': len(driver.get_cookies()),
            'session_active': 'facebook.com' in driver.current_url
        }
        return session_info
    except:
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

