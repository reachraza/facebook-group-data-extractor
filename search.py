"""
Phase 2 - Search Integration and Rate Limiting
Facebook Group Search Module

Purpose:
- Execute Facebook group searches based on keywords
- Scrape search results and extract unique group URLs
- Implement rate limiting and human-like delays
- Filter and validate extracted URLs

Key Features:
- Scrolling through search results to load more groups
- URL normalization and validation
- Automatic dismissal of login/cookie overlays
- Retry logic for transient network failures
- Strict filtering to exclude non-group URLs

Workflow:
1. Navigate to Facebook search URL with encoded keyword
2. Scroll through results while collecting group URLs
3. Normalize and validate each URL
4. Return deduplicated list of valid group URLs
"""

from __future__ import annotations

# Standard library imports
import os              # OS-level operations
import time            # Adding delays between actions
import random          # Randomizing delays for human-like behavior
import logging         # Logging search progress and errors
import urllib.parse    # URL encoding and parsing
from typing import List, Set  # Type hints

# Selenium WebDriver imports
from selenium.webdriver.common.by import By  # Locator strategies
from selenium.webdriver.support.ui import WebDriverWait  # Wait for elements
from selenium.webdriver.support import expected_conditions as EC  # Expected conditions
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException


def _human_delay(delay_min: float, delay_max: float) -> None:
    """Sleep a random amount between min and max seconds."""
    try:
        low = max(0.0, float(delay_min))
        high = max(low, float(delay_max))
    except Exception:
        low, high = 2.0, 5.0
    sleep_s = random.uniform(low, high)
    logging.debug(f"Sleeping {sleep_s:.2f}s")
    time.sleep(sleep_s)


def _normalize_group_url(url: str) -> str:
    if not url:
        return ""
    # Strip URL params and fragments, remove trailing slash
    parsed = urllib.parse.urlsplit(url)
    clean = urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path, "", ""))
    if clean.endswith('/'):
        clean = clean.rstrip('/')
    # Ensure it's a group URL
    return clean

def _is_group_link(url: str) -> bool:
    """Heuristic to ensure the URL is a concrete group page, not the search page."""
    try:
        parsed = urllib.parse.urlsplit(url)
        path = (parsed.path or "").strip()
        if not path.startswith("/groups/"):
            return False
        # Exclude search endpoints and obvious non-group actions
        if "/search/groups" in url:
            return False
        if any(seg in path for seg in ["/create/", "/invite/", "/buy_sell_discussion", "/events/"]):
            return False
        # Require at least "/groups/<id or name>"
        parts = [p for p in path.split('/') if p]
        return len(parts) >= 2
    except Exception:
        return False


def _dismiss_overlays(driver, timeout: int = 6) -> None:
    """Best-effort dismissal of cookie/login overlays that hide content."""
    try:
        WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        candidates = [
            "//button[contains(., 'Allow all')]",
            "//button[contains(., 'Allow essential')]",
            "//button[contains(., 'Only allow essential')]",
            "//button[contains(., 'Accept')]",
            "//span[contains(., 'Accept')]",
            "//div[@role='button' and (contains(., 'Accept') or contains(., 'OK'))]",
            "//div[@aria-label='Close' or @role='button'][contains(., 'Close')]",
        ]
        for xp in candidates:
            try:
                el = driver.find_element(By.XPATH, xp)
                if el:
                    el.click()
                    time.sleep(0.5)
            except Exception:
                continue
    except Exception:
        pass


def find_group_urls(driver, keyword: str, *, max_scrolls: int = 8, delay_min: float = 2.0, delay_max: float = 5.0, timeout: int = 12) -> List[str]:
    """
    Execute a Facebook group search for the given keyword and collect public group links.

    Args:
        driver: Selenium WebDriver (already configured and optionally logged in)
        keyword: Search keyword, e.g., "Dallas Cowboys Tickets"
        max_scrolls: Max number of scroll steps to attempt
        delay_min, delay_max: Human-like delay bounds between actions
        timeout: Seconds to wait for key elements

    Returns:
        List of unique normalized group URLs.
    """
    logging.info(f"Searching groups for keyword: {keyword}")

    encoded = urllib.parse.quote(keyword)
    search_url = f"https://www.facebook.com/search/groups/?q={encoded}"

    # Open search URL with one retry on transient failures
    for attempt in range(2):
        try:
            driver.get(search_url)
            break
        except Exception as e:
            logging.error(f"Failed to open search URL (attempt {attempt+1}): {e}")
            if attempt == 0:
                time.sleep(3)
                continue
            return []

    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
    except TimeoutException:
        logging.warning("Search page body not loaded in time")

    # Try to clear overlays that can reduce visible results
    _dismiss_overlays(driver, timeout=4)

    collected: Set[str] = set()
    last_height = 0

    for i in range(max_scrolls):
        logging.debug(f"Scroll {i+1}/{max_scrolls}")

        # Collect anchors containing group links on the current viewport
        try:
            anchors = driver.find_elements(By.CSS_SELECTOR, "a[href*='/groups/']")
        except Exception:
            anchors = []

        for a in anchors:
            try:
                href = a.get_attribute("href")
                if not href:
                    continue
                normalized = _normalize_group_url(href)
                if _is_group_link(normalized):
                    collected.add(normalized)
            except StaleElementReferenceException:
                continue
            except Exception:
                continue

        # Human delay between scrolls
        _human_delay(delay_min, delay_max)

        # Perform scroll to load more results
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        except Exception:
            logging.debug("Scroll JS failed; continuing")

        # Wait a bit for new content
        _human_delay(delay_min, delay_max)

        # Detect if no more content loads
        try:
            new_height = driver.execute_script("return document.body.scrollHeight") or 0
        except Exception:
            new_height = 0
        if new_height == last_height:
            logging.debug("No further content loaded; stopping scroll")
            break
        last_height = new_height

    urls = sorted(collected)
    logging.info(f"Collected {len(urls)} group URLs for keyword '{keyword}'")
    return urls


__all__ = [
    "find_group_urls",
]


