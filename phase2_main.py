"""
Phase 2 Orchestrator - Search, Robustness, Rate Limiting
Facebook Group Data Extractor - Phase 2 Implementation

This is the main orchestrator for Phase 2 functionality. It implements:
1. Keyword Generation (input_processor.py) - Creates search terms from Excel/CSV files
2. Facebook Group Search (search.py) - Executes searches and finds group URLs
3. Rate Limiting - Adds delays to avoid detection and IP bans
4. Error Handling & Logging - Comprehensive logging to extraction.log
5. Data Enrichment (scraper.py) - Optionally scrapes full group details

Key Features:
- Searches Facebook for groups based on generated keywords
- Collects unique public group URLs
- Optional data enrichment for member counts and descriptions
- Session management with periodic re-login
- Saves results to output/search_results_TIMESTAMP.csv

Usage:
    python phase2_main.py
    
The script processes keywords from Resources/All Teams by Sport.xlsx
and saves results with timestamps.
"""

from __future__ import annotations

# Standard library imports
import os          # File and directory operations
import sys         # System-specific parameters
import csv         # CSV file operations
import time        # Adding delays and timestamps
import logging     # Comprehensive logging functionality
from datetime import datetime  # Timestamp generation
from configparser import ConfigParser  # Configuration file reading
from typing import List, Set  # Type hints for better code documentation

# Local module imports - Phase 2 functionality
from login import get_driver_with_config, login_to_facebook, load_credentials_from_config, validate_credentials
from scraper import scrape_group_data  # Data enrichment functionality
from search import find_group_urls  # Facebook group search
from input_processor import generate_keywords_from_resources  # Keyword generation


def _setup_logging(log_level: str, log_file: str) -> None:
    level = getattr(logging, (log_level or "INFO").upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_file, encoding="utf-8") if log_file else logging.NullHandler(),
        ],
    )


def _load_search_config(cfg: ConfigParser):
    delay_min = float(cfg.get("selenium", "delay_min", fallback="2"))
    delay_max = float(cfg.get("selenium", "delay_max", fallback="5"))
    timeout = int(cfg.get("selenium", "timeout", fallback="10"))

    max_scrolls = int(cfg.get("search", "max_scrolls_per_search", fallback="8"))
    max_results = int(cfg.get("search", "max_results_per_keyword", fallback="100"))
    enable_enrichment = cfg.getboolean("search", "enable_enrichment", fallback=True)
    keepalive_interval = int(cfg.get("search", "keepalive_interval", fallback="0"))

    log_level = cfg.get("logging", "log_level", fallback="INFO")
    log_file = cfg.get("logging", "log_file", fallback="extraction.log")

    return {
        "delay_min": delay_min,
        "delay_max": delay_max,
        "timeout": timeout,
        "max_scrolls": max_scrolls,
        "max_results": max_results,
        "enable_enrichment": enable_enrichment,
        "keepalive_interval": keepalive_interval,
        "log_level": log_level,
        "log_file": log_file,
    }


def _save_search_results(records: List[dict], output_dir: str = "output") -> str:
    os.makedirs(output_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(output_dir, f"search_results_{ts}.csv")
    # Determine headers from union of keys to support enriched fields
    base_fields = ["keyword", "group_url", "captured_at"]
    extra_keys: Set[str] = set()
    for r in records:
        for k in r.keys():
            if k not in base_fields:
                extra_keys.add(k)
    fieldnames = base_fields + sorted(extra_keys)
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in records:
            writer.writerow(r)
    logging.info(f"Saved search results to: {path}")
    return path


def _append_urls(urls: List[str], dest: str = "extracted_urls.txt") -> None:
    existing: Set[str] = set()
    if os.path.exists(dest):
        try:
            with open(dest, "r", encoding="utf-8") as f:
                for line in f:
                    url = (line or "").strip().rstrip('/')
                    if url:
                        existing.add(url)
        except Exception:
            pass

    to_add = []
    for u in urls:
        u = (u or "").strip().rstrip('/')
        if u and u not in existing:
            to_add.append(u)
            existing.add(u)

    if not to_add:
        logging.info("No new URLs to append to extracted_urls.txt")
        return

    with open(dest, "a", encoding="utf-8") as f:
        for u in to_add:
            f.write(u + "\n")
    logging.info(f"Appended {len(to_add)} new URLs to {dest}")


def run_phase2_search() -> bool:
    print("\n" + "=" * 60)
    print("PHASE 2: Search, Robustness, and Rate Limiting")
    print("Facebook Group Data Extractor")
    print("=" * 60)

    # Load config
    cfg = ConfigParser()
    cfg.read("config.ini")

    search_cfg = _load_search_config(cfg)
    _setup_logging(search_cfg["log_level"], search_cfg["log_file"])

    # Setup driver (reuses Phase 1 utilities)
    driver = None
    try:
        driver = get_driver_with_config()

        # Optional login (recommended for better search results)
        email, password, twocaptcha_api_key = load_credentials_from_config()
        login_success = False
        if email and password and validate_credentials(email, password):
            logging.info("Attempting login for Phase 2 searches...")
            login_success = login_to_facebook(driver, email, password, twocaptcha_api_key)
            if login_success:
                logging.info("Login successful for Phase 2")
            else:
                logging.warning("Login failed - continuing with public-only search results")
        else:
            logging.info("No credentials - continuing with public-only search results")

        # Generate keywords
        keywords = generate_keywords_from_resources(resources_dir="Resources")
        # Limit to first 5 keywords to get 10-20 groups (approx 2-7 groups per keyword)
        keywords = keywords[:5]
        logging.info(f"Using {len(keywords)} keywords (limited for quick test)")

        all_urls: Set[str] = set()
        records: List[dict] = []
        ts_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Safer defaults if config is too aggressive
        if search_cfg["delay_min"] < 2:
            search_cfg["delay_min"] = 3
        if search_cfg["delay_max"] < search_cfg["delay_min"]:
            search_cfg["delay_max"] = search_cfg["delay_min"] + 3

        # Batch processing to reduce detection
        batch_size = 20
        cooldown_between_batches = 60  # seconds

        for idx, kw in enumerate(keywords, 1):
            print(f"[{idx}/{len(keywords)}] Searching: {kw}")

            # Check session every 5 keywords; try re-login if logged out
            try:
                if idx % 5 == 1:
                    driver.get("https://www.facebook.com")
                    time.sleep(2)
                    body_txt = (driver.find_element_by_tag_name("body").text or "").lower() if hasattr(driver, 'find_element_by_tag_name') else driver.find_element("tag name", "body").text.lower()
                    if any(x in body_txt for x in ["log in", "sign up", "create account"]):
                        logging.info("Session likely logged out; attempting re-login...")
                        if email and password and validate_credentials(email, password):
                            login_success = login_to_facebook(driver, email, password, twocaptcha_api_key)
                            logging.info("Re-login %s", "successful" if login_success else "failed")
            except Exception as e:
                # Session might be dead - try to recover
                logging.warning(f"Session check failed: {e}")
                try:
                    driver.quit()
                except:
                    pass
                # Recreate driver
                driver = get_driver_with_config()
                if email and password and validate_credentials(email, password):
                    logging.info("Attempting re-login with fresh driver...")
                    login_to_facebook(driver, email, password, twocaptcha_api_key)

            urls = []
            try:
                urls = find_group_urls(
                    driver,
                    kw,
                    max_scrolls=search_cfg["max_scrolls"],
                    delay_min=search_cfg["delay_min"],
                    delay_max=search_cfg["delay_max"],
                    timeout=search_cfg["timeout"],
                )
            except Exception as e:
                # Session died during search - recover
                logging.error(f"Search failed for '{kw}': {e}")
                try:
                    driver.quit()
                except:
                    pass
                # Recreate driver
                driver = get_driver_with_config()
                if email and password and validate_credentials(email, password):
                    logging.info("Attempting re-login with fresh driver...")
                    login_to_facebook(driver, email, password, twocaptcha_api_key)
                continue

            if search_cfg["max_results"] and len(urls) > search_cfg["max_results"]:
                urls = urls[: search_cfg["max_results"]]

            for u in urls:
                if u in all_urls:
                    continue
                all_urls.add(u)

                record = {
                    "keyword": kw,
                    "group_url": u,
                    "captured_at": ts_now,
                }

                # Enrich with group details using existing scraper (Phase 1 logic)
                if search_cfg.get("enable_enrichment", True):
                    try:
                        details = scrape_group_data(driver, u) or {}
                        # Map relevant fields into record
                        if details:
                            if details.get("group_name"):
                                record["group_name"] = details.get("group_name")
                            if details.get("member_count") is not None:
                                record["member_count"] = details.get("member_count")
                            if details.get("description"):
                                record["description"] = details.get("description")
                            if details.get("admin_names"):
                                record["admin_names"] = details.get("admin_names")
                            if details.get("admin_profile_urls"):
                                record["admin_profile_urls"] = details.get("admin_profile_urls")
                            if details.get("member_names"):
                                record["member_names"] = details.get("member_names")
                            if details.get("member_profile_urls"):
                                record["member_profile_urls"] = details.get("member_profile_urls")
                    except Exception as e:
                        logging.warning(f"Could not enrich details for {u}: {e}")

                records.append(record)

            # Cooldown between batches
            if idx % batch_size == 0:
                keepalive = search_cfg.get("keepalive_interval", 0)
                if keepalive > 0:
                    logging.info("Cooling down for %s seconds (with keepalive every %ss)...", cooldown_between_batches, keepalive)
                    elapsed = 0
                    while elapsed < cooldown_between_batches:
                        time.sleep(min(keepalive, cooldown_between_batches - elapsed))
                        elapsed += keepalive
                        if elapsed < cooldown_between_batches:
                            try:
                                driver.get("https://www.facebook.com")
                                time.sleep(1)
                            except:
                                pass
                else:
                    logging.info("Cooling down for %s seconds to avoid detection...", cooldown_between_batches)
                    time.sleep(cooldown_between_batches)

        # Save and append
        _save_search_results(records, output_dir="output")
        _append_urls(sorted(all_urls), dest="extracted_urls.txt")

        print("\n" + "=" * 60)
        print("✅ PHASE 2 SEARCH COMPLETE!")
        print("=" * 60)
        print(f"🔎 Keywords processed: {len(keywords)}")
        print(f"🔗 Unique group URLs found: {len(all_urls)}")
        return True

    except Exception as e:
        logging.exception(f"Phase 2 error: {e}")
        print(f"\n❌ Error during Phase 2: {e}")
        return False
    finally:
        if driver is not None:
            print("\n🧹 Cleaning up...")
            try:
                driver.quit()
            except Exception:
                pass
            print("✅ WebDriver closed")


if __name__ == "__main__":
    run_phase2_search()


