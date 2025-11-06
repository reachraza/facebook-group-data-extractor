"""
Phase 1: Core Functionality & Initial Output
Facebook Group Data Extractor - Phase 1 Implementation

This is the main orchestrator for Phase 1 functionality. It coordinates:
1. Environment Setup (config.ini) - Loading settings and credentials
2. Login & Session Management (login.py) - Establishing Facebook session
3. Core Group Scraper (scraper.py) - Extracting data from group pages
4. Basic Data Storage (scraped_data_raw.csv) - Saving results to CSV

Usage:
    python phase1_main.py
    
The script reads group URLs from extracted_urls.txt and processes them sequentially.
Results are saved to output/scraped_data_raw.csv
"""

# Standard library imports
import os          # File and directory operations
import csv         # CSV file reading/writing
import configparser  # Reading configuration from .ini files
from datetime import datetime  # Generating timestamps

# Local module imports - Phase 1 core functionality
from login import get_driver_with_config, login_to_facebook, load_credentials_from_config, validate_credentials
from scraper import scrape_group_data, scrape_multiple_groups, validate_group_url


def save_to_raw_csv(data, filename='scraped_data_raw.csv'):
    """
    Save scraped data to a basic, unformatted CSV file
    As specified in Phase 1 Task 4
    
    Args:
        data (list): List of group data dictionaries
        filename (str): Output filename
    
    Returns:
        str: Path to saved file
    """
    output_dir = 'output'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"📁 Created output directory: {output_dir}")
    
    filepath = os.path.join(output_dir, filename)
    
    try:
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            if not data:
                print("⚠️  No data to save")
                return filepath
            
            # Get fieldnames from first item
            fieldnames = list(data[0].keys())
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for row in data:
                writer.writerow(row)
        
        print(f"✅ Data saved to: {filepath}")
        print(f"📊 Total records: {len(data)}")
        
        return filepath
        
    except PermissionError as e:
        # File is likely open in another program (like the IDE)
        print(f"⚠️  Permission denied (file may be open): {filepath}")
        print("💡 Attempting to save with timestamped filename...")
        
        # Try with timestamped filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name, ext = os.path.splitext(filename)
        alt_filename = f"{name}_{timestamp}{ext}"
        alt_filepath = os.path.join(output_dir, alt_filename)
        
        try:
            with open(alt_filepath, 'w', newline='', encoding='utf-8') as csvfile:
                if not data:
                    print("⚠️  No data to save")
                    return alt_filepath
                
                # Get fieldnames from first item
                fieldnames = list(data[0].keys())
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for row in data:
                    writer.writerow(row)
            
            print(f"✅ Data saved to: {alt_filepath}")
            print(f"📊 Total records: {len(data)}")
            print(f"💡 Original file is locked - saved with timestamp instead")
            
            return alt_filepath
        except Exception as e2:
            print(f"❌ Error saving to alternative file: {str(e2)}")
            return None
        
    except Exception as e:
        print(f"❌ Error saving to CSV: {str(e)}")
        return None


def run_phase1_extraction(group_urls=None):
    """
    Run Phase 1 extraction workflow
    
    Args:
        group_urls (list): List of Facebook group URLs to scrape
    
    Returns:
        bool: True if successful
    """
    print("=" * 60)
    print("🚀 PHASE 1: Core Functionality & Initial Output")
    print("=" * 60)
    
    # Load configuration
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    # Get headless mode setting
    headless = config.getboolean('selenium', 'headless_mode', fallback=True)
    
    if not headless:
        print("\n🔍 Running in VISIBLE mode for debugging")
        print("   Set headless_mode=true in config.ini for headless operation")
    
    # Step 1: Setup WebDriver
    print("\n" + "-" * 60)
    print("STEP 1: Setting up WebDriver")
    print("-" * 60)
    
    driver = get_driver_with_config()
    if not driver:
        print("❌ Phase 1 failed: Could not initialize WebDriver")
        return False
    
    try:
        # Step 2: Login to Facebook (if credentials provided)
        print("\n" + "-" * 60)
        print("STEP 2: Logging into Facebook")
        print("-" * 60)
        
        email, password, twocaptcha_api_key = load_credentials_from_config()
        login_success = False
        
        if email and password and validate_credentials(email, password):
            login_success = login_to_facebook(driver, email, password, twocaptcha_api_key)
            if login_success:
                print("✅ Login successful - will attempt full data extraction")
            else:
                print("⚠️  Login failed - will attempt public-only extraction")
        else:
            print("⚠️  Credentials not provided in config.ini")
            print("   Will attempt public-only extraction")
        
        # Step 3: Validate group URLs
        print("\n" + "-" * 60)
        print("STEP 3: Validating group URLs")
        print("-" * 60)
        
        if not group_urls:
            print("❌ No group URLs provided")
            print("   Usage: python phase1_main.py")
            print("   Edit this file to add group URLs")
            return False
        
        valid_urls = []
        for url in group_urls:
            if validate_group_url(url):
                valid_urls.append(url)
                print(f"   ✅ Valid URL: {url}")
            else:
                print(f"   ❌ Invalid URL: {url}")
        
        if not valid_urls:
            print("❌ No valid group URLs provided")
            return False
        
        # Step 4: Scrape group data
        print("\n" + "-" * 60)
        print("STEP 4: Scraping group data")
        print("-" * 60)
        
        # Pass login function and credentials for session management
        login_func = login_to_facebook if login_success else None
        credentials = (email, password) if email and password else None
        
        group_data = scrape_multiple_groups(driver, valid_urls, delay_between=3, 
                                          login_func=login_func, credentials=credentials)
        
        if not group_data:
            print("❌ No data extracted")
            return False
        
        # Step 5: Save to raw CSV
        print("\n" + "-" * 60)
        print("STEP 5: Saving to raw CSV file")
        print("-" * 60)
        
        filepath = save_to_raw_csv(group_data, filename='scraped_data_raw.csv')
        
        if not filepath:
            print("❌ Failed to save data to CSV")
            return False
        
        # Phase 1 Complete Summary
        print("\n" + "=" * 60)
        print("✅ PHASE 1 COMPLETE!")
        print("=" * 60)
        print(f"📊 Groups processed: {len(group_data)}")
        print(f"💾 Data saved to: {filepath}")
        print(f"🔐 Login status: {'✅ Logged in' if login_success else '❌ Not logged in'}")
        print("\n📋 Extracted Fields:")
        print("   - Group Name")
        print("   - Group URL")
        print("   - Visible Member Count")
        print("   - Short Description")
        print("   - Extraction Date")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during Phase 1 extraction: {str(e)}")
        return False
        
    finally:
        # Cleanup
        print("\n🧹 Cleaning up...")
        driver.quit()
        print("✅ WebDriver closed")


def main():
    """Main entry point for Phase 1"""
    print("\n" + "=" * 60)
    print("PHASE 1: Core Functionality & Initial Output")
    print("Facebook Group Data Extractor")
    print("=" * 60)
    
    # Load Facebook Group URLs from extracted_urls.txt
    example_urls = []
    urls_file = "extracted_urls.txt"
    
    if os.path.exists(urls_file):
        print(f"📖 Loading URLs from {urls_file}...")
        try:
            with open(urls_file, 'r', encoding='utf-8') as f:
                for line in f:
                    url = line.strip()
                    if url and url.startswith('http'):
                        # Remove trailing slash if present
                        url = url.rstrip('/')
                        example_urls.append(url)
            
            print(f"✅ Loaded {len(example_urls)} URLs from {urls_file}")
            
            # Limit to first 50 URLs for testing (remove this limit to process all)
            if len(example_urls) > 50:
                print(f"⚠️  Processing first 50 URLs for testing (total available: {len(example_urls)})")
                print("   Remove the 50 URL limit in phase1_main.py to process all URLs")
                example_urls = example_urls[:50]
            
        except Exception as e:
            print(f"❌ Error reading {urls_file}: {str(e)}")
            example_urls = []
    else:
        print(f"⚠️  File {urls_file} not found")
        print("   Using sample URLs as fallback")
        # Fallback to sample URLs
        example_urls = [
            "https://www.facebook.com/groups/1679801736170853",
            "https://www.facebook.com/groups/2264901493928412",
            "https://www.facebook.com/groups/784710944143009",
            "https://www.facebook.com/groups/977039707150947",
            "https://www.facebook.com/groups/1282962319612816",
        ]
    
    if not example_urls:
        print("\n⚠️  No group URLs provided!")
        print("\n📝 To use Phase 1 extraction:")
        print("1. Edit phase1_main.py")
        print("2. Add Facebook group URLs to the example_urls list")
        print("3. Configure your Facebook credentials in config.ini")
        print("4. Run: python phase1_main.py")
        print("\nExample URL format:")
        print('   example_urls = ["https://www.facebook.com/groups/123456789"]')
        return
    
    # Run Phase 1 extraction
    success = run_phase1_extraction(group_urls=example_urls)
    
    if success:
        print("\n🎉 Phase 1 implementation successful!")
    else:
        print("\n❌ Phase 1 implementation failed!")


if __name__ == "__main__":
    main()

