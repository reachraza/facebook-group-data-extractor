"""
Merge Multiple CSV Files into Single CSV
Combines all test_single_group_results CSV files into one consolidated file

Usage:
    python merge_csv.py
    python merge_csv.py --output merged_results.csv
    python merge_csv.py --pattern "test_single_group_results*.csv"
"""

import csv
import os
import glob
import argparse
from datetime import datetime
from collections import OrderedDict

def merge_csv_files(input_dir="output", output_file="output/merged_results.csv", pattern="test_single_group_results*.csv"):
    """
    Merge all CSV files matching the pattern into a single CSV file
    
    Args:
        input_dir (str): Directory containing CSV files to merge
        output_file (str): Path to output merged CSV file
        pattern (str): File pattern to match (e.g., "test_single_group_results*.csv")
    
    Returns:
        int: Number of unique rows merged
    """
    print("=" * 60)
    print("CSV MERGER")
    print("=" * 60)
    
    # Find all CSV files matching the pattern
    search_pattern = os.path.join(input_dir, pattern)
    csv_files = glob.glob(search_pattern)
    
    if not csv_files:
        print(f"❌ No CSV files found matching pattern: {pattern}")
        return 0
    
    print(f"\n📁 Found {len(csv_files)} CSV file(s) to merge:")
    for f in sorted(csv_files):
        print(f"   - {os.path.basename(f)}")
    
    # Dictionary to store unique records (keyed by group_url to avoid duplicates)
    unique_records = OrderedDict()
    header = None
    total_rows = 0
    
    # Read all CSV files
    for csv_file in sorted(csv_files):
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                # Store header from first file
                if header is None:
                    header = reader.fieldnames
                
                # Read rows from this file
                file_rows = 0
                for row in reader:
                    file_rows += 1
                    total_rows += 1
                    
                    # Use group_url as unique key
                    group_url = row.get('group_url', '').strip()
                    
                    if group_url:
                        # If URL already exists, keep the one with more data (fewer empty fields)
                        if group_url in unique_records:
                            existing = unique_records[group_url]
                            existing_empty = sum(1 for v in existing.values() if not v or v.strip() == '')
                            new_empty = sum(1 for v in row.values() if not v or v.strip() == '')
                            
                            # Keep the record with fewer empty fields
                            if new_empty < existing_empty:
                                unique_records[group_url] = row
                        else:
                            unique_records[group_url] = row
                
                print(f"   ✅ {os.path.basename(csv_file)}: {file_rows} rows")
                
        except Exception as e:
            print(f"   ⚠️  Error reading {os.path.basename(csv_file)}: {str(e)}")
            continue
    
    if not unique_records:
        print("\n❌ No data found in CSV files")
        return 0
    
    # Write merged data to output file
    try:
        # Ensure output directory exists
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            if header:
                writer = csv.DictWriter(f, fieldnames=header)
                writer.writeheader()
                
                for group_url, row in unique_records.items():
                    writer.writerow(row)
        
        print("\n" + "=" * 60)
        print("MERGE COMPLETE")
        print("=" * 60)
        print(f"📊 Total rows read: {total_rows}")
        print(f"📊 Unique groups: {len(unique_records)}")
        print(f"📁 Output file: {output_file}")
        print("=" * 60)
        
        return len(unique_records)
        
    except Exception as e:
        print(f"\n❌ Error writing merged CSV: {str(e)}")
        return 0


def main():
    """Main function to handle command-line arguments"""
    parser = argparse.ArgumentParser(
        description='Merge multiple CSV files into a single CSV file',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python merge_csv.py
  python merge_csv.py --output output/all_results.csv
  python merge_csv.py --pattern "*.csv" --output output/merged.csv
        """
    )
    
    parser.add_argument(
        '--input-dir',
        default='output',
        help='Directory containing CSV files to merge (default: output)'
    )
    
    parser.add_argument(
        '--output',
        default='output/merged_results.csv',
        help='Output CSV file path (default: output/merged_results.csv)'
    )
    
    parser.add_argument(
        '--pattern',
        default='test_single_group_results*.csv',
        help='File pattern to match (default: test_single_group_results*.csv)'
    )
    
    args = parser.parse_args()
    
    merge_csv_files(
        input_dir=args.input_dir,
        output_file=args.output,
        pattern=args.pattern
    )


if __name__ == "__main__":
    main()
