"""
Script to extract data from single or multiple Facebook group URLs
Usage:
    python test_single_group.py <url1> <url2> <url3> ...
    python test_single_group.py --file urls.txt
Results are saved to output/test_single_group_results.csv
"""

import sys
import os
import csv
import time
from datetime import datetime
from login import get_driver_with_config, login_to_facebook, load_credentials_from_config, validate_credentials
from scraper import scrape_group_data


def save_to_csv(data, filename='test_single_group_results.csv'):
    """
    Save scraped data to CSV file
    
    Args:
        data (dict): Group data dictionary
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
        # Check if file exists to determine if we need to write header
        file_exists = os.path.exists(filepath)
        
        with open(filepath, 'a', newline='', encoding='utf-8') as csvfile:
            # Get fieldnames from data dictionary
            fieldnames = list(data.keys())
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Write header only if file is new
            if not file_exists:
                writer.writeheader()
            
            # Write the data row
            writer.writerow(data)
        
        print(f"✅ Data saved to: {filepath}")
        return filepath
        
    except PermissionError as e:
        # File is likely open in another program
        print(f"⚠️  Permission denied (file may be open): {filepath}")
        print("💡 Attempting to save with timestamped filename...")
        
        # Try with timestamped filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name, ext = os.path.splitext(filename)
        alt_filename = f"{name}_{timestamp}{ext}"
        alt_filepath = os.path.join(output_dir, alt_filename)
        
        try:
            with open(alt_filepath, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = list(data.keys())
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerow(data)
            
            print(f"✅ Data saved to: {alt_filepath}")
            print(f"💡 Original file is locked - saved with timestamp instead")
            return alt_filepath
        except Exception as e2:
            print(f"❌ Error saving to alternative file: {str(e2)}")
            return None
        
    except Exception as e:
        print(f"❌ Error saving to CSV: {str(e)}")
        return None


def load_urls_from_file(filename):
    """
    Load URLs from a text file (one URL per line)
    
    Args:
        filename (str): Path to file containing URLs
    
    Returns:
        list: List of URLs
    """
    urls = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                url = line.strip()
                # Skip empty lines and comments
                if url and not url.startswith('#'):
                    urls.append(url)
        print(f"📄 Loaded {len(urls)} URLs from {filename}")
        return urls
    except FileNotFoundError:
        print(f"❌ File not found: {filename}")
        return []
    except Exception as e:
        print(f"❌ Error reading file {filename}: {str(e)}")
        return []


def process_single_group(driver, group_url, index=1, total=1):
    """
    Process a single group URL
    
    Args:
        driver: Selenium WebDriver instance
        group_url (str): Facebook group URL
        index (int): Current URL index (for progress tracking)
        total (int): Total number of URLs
    
    Returns:
        dict: Extracted group data or None if failed
    """
    print("\n" + "=" * 60)
    print(f"PROCESSING URL {index}/{total}")
    print("=" * 60)
    print(f"URL: {group_url}")
    
    # Extract data
    data = scrape_group_data(driver, group_url)
    
    # Print results
    if data:
        print("\n" + "-" * 60)
        print("EXTRACTION RESULTS")
        print("-" * 60)
        print(f"Group Name: {data.get('group_name', 'N/A')}")
        print(f"URL: {data.get('group_url', 'N/A')}")
        print(f"Member Count: {data.get('member_count', 0):,}")
        desc = data.get('description', 'No description available')
        print(f"Description: {desc[:100]}..." if len(desc) > 100 else f"Description: {desc}")
        print(f"Privacy: {data.get('privacy', 'N/A')}")
        print(f"Admin Names: {data.get('admin_names', 'N/A')}")
        print(f"Member Names: {data.get('member_names', 'N/A')}")
        print(f"Extraction Date: {data.get('extraction_date', 'N/A')}")
        
        # Save to CSV
        save_to_csv(data, filename='test_single_group_results.csv')
        return data
    else:
        print(f"\n❌ Extraction failed for: {group_url}")
        return None


def main():
    # Parse command-line arguments
    urls = []
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python test_single_group.py <url1> [url2] [url3] ...")
        print("  python test_single_group.py --file <filename.txt>")
        print("\nExample:")
        print("  python test_single_group.py https://www.facebook.com/groups/698593531630485")
        print("  python test_single_group.py url1 url2 url3")
        print("  python test_single_group.py --file test_urls.txt")
        return
    
    # Check if --file option is used
    if sys.argv[1] == '--file' or sys.argv[1] == '-f':
        if len(sys.argv) < 3:
            print("❌ Error: Please provide a filename after --file")
            return
        filename = sys.argv[2]
        urls = load_urls_from_file(filename)
        if not urls:
            return
    else:
        # URLs provided as command-line arguments
        urls = [url.strip() for url in sys.argv[1:] if url.strip()]
    
    if not urls:
        print("❌ No URLs provided")
        return
    
    print("=" * 60)
    print(f"MULTI-GROUP EXTRACTION ({len(urls)} URLs)")
    print("=" * 60)
    
    # Setup driver
    driver = get_driver_with_config()
    
    # Login once for all URLs
    email, password = load_credentials_from_config()
    login_success = False
    if email and password and validate_credentials(email, password):
        print("\n🔐 Logging in...")
        login_success = login_to_facebook(driver, email, password)
        if login_success:
            print("✅ Login complete\n")
        else:
            print("⚠️  Login failed - will try public-only extraction\n")
    else:
        print("⚠️  No credentials - will try public-only extraction\n")
    
    # Process each URL
    successful = 0
    failed = 0
    results = []
    
    for i, group_url in enumerate(urls, 1):
        try:
            data = process_single_group(driver, group_url, index=i, total=len(urls))
            if data:
                results.append(data)
                successful += 1
            else:
                failed += 1
            
            # Add delay between URLs (except for the last one)
            if i < len(urls):
                delay = 5  # 5 seconds between URLs
                print(f"\n⏳ Waiting {delay} seconds before next URL...")
                time.sleep(delay)
                
        except KeyboardInterrupt:
            print("\n\n⚠️  Process interrupted by user")
            break
        except Exception as e:
            print(f"\n❌ Unexpected error processing {group_url}: {str(e)}")
            failed += 1
            continue
    
    # Summary
    print("\n" + "=" * 60)
    print("EXTRACTION SUMMARY")
    print("=" * 60)
    print(f"Total URLs: {len(urls)}")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Results saved to: output/test_single_group_results.csv")
    
    # Keep browser open for 10 seconds
    print("\n⚠️  Browser will close in 10 seconds...")
    time.sleep(10)
    
    driver.quit()

if __name__ == "__main__":
    main()

