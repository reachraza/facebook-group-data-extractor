# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from twocaptcha import TwoCaptcha
# import time
# import base64
# import requests
# from io import BytesIO

# class FacebookLoginWith2Captcha:
#     def __init__(self, api_key):
#         self.solver = TwoCaptcha(api_key)
#         self.driver = None
#         self.setup_driver()
        
#     def setup_driver(self):
#         """Initialize Chrome driver with appropriate options"""
#         options = webdriver.ChromeOptions()
#         options.add_argument('--no-sandbox')
#         options.add_argument('--disable-dev-shm-usage')
#         options.add_argument('--disable-blink-features=AutomationControlled')
#         options.add_experimental_option("excludeSwitches", ["enable-automation"])
#         options.add_experimental_option('useAutomationExtension', False)
        
#         self.driver = webdriver.Chrome(options=options)
#         self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
#     def detect_captcha_type(self):
#         """Detect what type of captcha Facebook is showing on current page"""
#         print("Detecting captcha type...")
#         print(f"Current URL: {self.driver.current_url}")
        
#         try:
#             # Check for reCAPTCHA on two-step verification page
#             if "two_step_verification" in self.driver.current_url:
#                 print("On two-step verification page, checking for captcha...")
                
#                 # Look for the specific iframe with id 'captcha-recaptcha'
#                 captcha_iframes = self.driver.find_elements(By.CSS_SELECTOR, "iframe[id='captcha-recaptcha']")
#                 if captcha_iframes:
#                     print("✓ Found captcha-recaptcha iframe")
#                     return "recaptcha_v2"
            
#             return None
            
#         except Exception as e:
#             print(f"Error detecting captcha type: {e}")
#             return None
    
#     def solve_recaptcha_v2(self):
#         """Solve reCAPTCHA v2 with the complete iframe flow"""
#         try:
#             print("Starting complete reCAPTCHA iframe flow...")
            
#             # Use the complete iframe flow since token method often fails
#             print("Using complete iframe flow...")
#             return self.solve_complete_iframe_flow()
                
#         except Exception as e:
#             print(f"reCAPTCHA v2 solving failed: {e}")
#             self.driver.switch_to.default_content()
#             return False
    
#     def solve_complete_iframe_flow(self):
#         """Complete iframe flow for captcha-recaptcha iframe"""
#         try:
#             print("Starting complete iframe flow...")
            
#             # Step 1: Find and switch to the captcha-recaptcha iframe
#             print("Step 1: Finding captcha-recaptcha iframe...")
#             captcha_iframe = self.find_captcha_iframe()
#             if not captcha_iframe:
#                 print("✗ Could not find captcha-recaptcha iframe")
#                 return False
            
#             # Step 2: Switch to captcha-recaptcha iframe
#             print("Step 2: Switching to captcha-recaptcha iframe...")
#             self.driver.switch_to.frame(captcha_iframe)
            
#             # Step 3: Find and switch to the checkbox iframe inside
#             print("Step 3: Finding checkbox iframe inside captcha-recaptcha...")
#             checkbox_iframe = self.find_checkbox_iframe_inside_captcha()
#             if not checkbox_iframe:
#                 print("✗ Could not find checkbox iframe inside captcha-recaptcha")
#                 self.driver.switch_to.default_content()
#                 return False
            
#             # Step 4: Switch to checkbox iframe and click checkbox
#             print("Step 4: Switching to checkbox iframe and clicking...")
#             self.driver.switch_to.frame(checkbox_iframe)
#             checkbox_clicked = self.click_recaptcha_checkbox()
            
#             if not checkbox_clicked:
#                 print("✗ Could not click checkbox")
#                 self.driver.switch_to.default_content()
#                 return False
            
#             # Step 5: Wait for challenge and handle it
#             print("Step 5: Handling challenge after checkbox click...")
#             challenge_solved = self.handle_challenge_after_checkbox()
            
#             # Always return to main content
#             self.driver.switch_to.default_content()
#             return challenge_solved
            
#         except Exception as e:
#             print(f"Complete iframe flow failed: {e}")
#             self.driver.switch_to.default_content()
#             return False
    
#     def find_captcha_iframe(self):
#         """Find the captcha-recaptcha iframe"""
#         try:
#             # Look for iframe with id 'captcha-recaptcha'
#             iframes = self.driver.find_elements(By.CSS_SELECTOR, "iframe[id='captcha-recaptcha']")
#             print(f"Found {len(iframes)} captcha-recaptcha iframes")
            
#             if iframes:
#                 print("✓ Using captcha-recaptcha iframe")
#                 return iframes[0]
            
#             return None
#         except Exception as e:
#             print(f"Error finding captcha iframe: {e}")
#             return None
    
#     def find_checkbox_iframe_inside_captcha(self):
#         """Find the checkbox iframe inside the captcha-recaptcha iframe"""
#         try:
#             iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
#             print(f"Found {len(iframes)} iframes inside captcha-recaptcha")
            
#             for i, iframe in enumerate(iframes):
#                 src = iframe.get_attribute("src") or ""
#                 print(f"  Checkbox iframe {i}: {src[:100]}...")
#                 if "google.com/recaptcha" in src and "anchor" in src:
#                     print(f"✓ Found checkbox iframe at index {i}")
#                     return iframe
            
#             return None
#         except Exception as e:
#             print(f"Error finding checkbox iframe: {e}")
#             return None
    
#     def click_recaptcha_checkbox(self):
#         """Click the reCAPTCHA checkbox"""
#         try:
#             print("Looking for checkbox element...")
            
#             # Wait for checkbox to load
#             time.sleep(2)
            
#             # Take screenshot for debugging
#             self.driver.save_screenshot("checkbox_iframe.png")
#             print("Saved screenshot: checkbox_iframe.png")
            
#             # Try multiple checkbox selectors
#             checkbox_selectors = [
#                 ".recaptcha-checkbox-border",
#                 "#recaptcha-anchor",
#                 ".recaptcha-checkbox",
#                 "div.recaptcha-checkbox-border",
#                 "span.recaptcha-checkbox",
#                 "#anchor",
#                 ".rc-anchor-checkbox"
#             ]
            
#             checkbox = None
#             for selector in checkbox_selectors:
#                 try:
#                     elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
#                     if elements:
#                         checkbox = elements[0]
#                         print(f"✓ Found checkbox with selector: {selector}")
#                         break
#                 except:
#                     continue
            
#             if checkbox and checkbox.is_displayed():
#                 print("Clicking checkbox...")
#                 # Use JavaScript click for reliability
#                 self.driver.execute_script("arguments[0].click();", checkbox)
#                 print("✓ Checkbox clicked successfully")
#                 return True
#             else:
#                 print("✗ Could not find clickable checkbox")
#                 return False
                
#         except Exception as e:
#             print(f"Error clicking checkbox: {e}")
#             return False
    
#     def handle_challenge_after_checkbox(self):
#         """Handle the challenge that appears after clicking checkbox"""
#         try:
#             print("Checking for challenge after checkbox click...")
            
#             # Wait for challenge to appear (it might take a moment)
#             print("Waiting for challenge to load...")
#             time.sleep(5)
            
#             # Step 1: Switch back to captcha-recaptcha iframe level
#             self.driver.switch_to.parent_frame()  # Back to captcha-recaptcha iframe
#             print("Switched back to captcha-recaptcha iframe level")
            
#             # Step 2: Look for challenge iframe that appears dynamically
#             print("Looking for dynamically loaded challenge iframe...")
#             challenge_iframe = self.find_dynamic_challenge_iframe()
#             if not challenge_iframe:
#                 print("No challenge iframe found - checkbox might have been sufficient")
#                 return True
            
#             # Step 3: Switch to challenge iframe
#             print("Switching to challenge iframe...")
#             self.driver.switch_to.frame(challenge_iframe)
            
#             # Step 4: Solve the challenge (could be grid, images, or other types)
#             print("Solving challenge...")
#             challenge_solved = self.solve_challenge()
            
#             return challenge_solved
            
#         except Exception as e:
#             print(f"Error handling challenge after checkbox: {e}")
#             return False
    
#     def find_dynamic_challenge_iframe(self):
#         """Find the challenge iframe that appears dynamically after checkbox click"""
#         try:
#             # Wait for the challenge iframe to appear
#             WebDriverWait(self.driver, 10).until(
#                 EC.presence_of_element_located((By.TAG_NAME, "iframe"))
#             )
            
#             iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
#             print(f"Found {len(iframes)} iframes after checkbox click")
            
#             for i, iframe in enumerate(iframes):
#                 src = iframe.get_attribute("src") or ""
#                 print(f"  Challenge iframe {i}: {src[:100]}...")
#                 if "google.com/recaptcha" in src and "bframe" in src:
#                     print(f"✓ Found challenge iframe at index {i}")
#                     return iframe
            
#             # If no bframe found, try to find any new iframe that appeared
#             if iframes:
#                 print(f"Using first available iframe for challenge")
#                 return iframes[0]
            
#             return None
#         except Exception as e:
#             print(f"Error finding dynamic challenge iframe: {e}")
#             return None
    
#     def solve_challenge(self):
#         """Solve whatever challenge appears (grid, images, etc.)"""
#         try:
#             print("Starting challenge solution...")
            
#             # Wait for challenge to load
#             time.sleep(3)
#             self.driver.save_screenshot("challenge_screen.png")

#             # Get full instruction
#             instruction = self.get_challenge_instruction().lower()
#             print(f"Full instruction: {instruction}")

#             # === DETECT SKIP CASE ===
#             skip_phrases = [
#                 "if there are none",
#                 "if none",
#                 "click skip",
#                 "skip if none"
#             ]
#             if any(phrase in instruction for phrase in skip_phrases):
#                 print("⚠️  'Skip if none' detected in instruction")

#                 # Check if any tile actually has the object
#                 # We'll use 2Captcha with hint to confirm "none"
#                 image_data = self.get_challenge_image()
#                 if image_data:
#                     try:
#                         print("Asking 2Captcha: is there any object? (hint: check if NONE)")
#                         result = self.solver.normal(
#                             image_data,
#                             hintText="If NO objects match, reply 'NONE'. Otherwise list positions.",
#                             lang='en'
#                         )
#                         answer = result['code'].strip().lower()
#                         print(f"2Captcha answer: {answer}")

#                         if 'none' in answer or answer in ['0', 'no', 'skip']:
#                             print("2Captcha confirmed: NO objects → Clicking Skip")
#                             if self.click_skip_button():
#                                 return True
#                     except Exception as e:
#                         print(f"2Captcha hint failed: {e}")

#                 # Fallback: just click skip
#                 print("Fallback: clicking Skip button")
#                 if self.click_skip_button():
#                     return True

#             # === NORMAL FLOW: Solve with 2Captcha ===
#             challenge_type = self.detect_challenge_type()
#             print(f"Detected challenge type: {challenge_type}")

#             if challenge_type in ["grid_3x3", "grid_4x4"]:
#                 return self.solve_grid_challenge_with_skip_check(instruction)
#             elif challenge_type == "image_selection":
#                 return self.solve_image_selection_challenge()
#             else:
#                 return self.solve_generic_challenge()

#         except Exception as e:
#             print(f"Error solving challenge: {e}")
#             return False
    
# def solve_grid_challenge_with_skip_check(self, instruction):
#     try:
#         grid_elem = self.driver.find_element(By.CSS_SELECTOR, ".rc-imageselect-table")
#         tiles = grid_elem.find_elements(By.CSS_SELECTOR, "td")
#         tile_count = len(tiles)
#         rows = 3 if tile_count == 9 else 4
#         cols = 3 if tile_count == 9 else 4

#         image_data = self.get_challenge_image()
#         if not image_data:
#             return False

#         print(f"Sending {rows}x{cols} GRID to 2Captcha...")
#         result = self.solver.grid(image_data, rows=rows, columns=cols)
#         coordinates = result['code']
#         print(f"2Captcha grid result: {coordinates}")

#         # Skip if none
#         if not coordinates or coordinates.strip() in ['', '0']:
#             if any(p in instruction for p in ["if there are none", "click skip"]):
#                 print("No tiles + skip allowed → Skipping")
#                 return self.click_skip_button()

#         success = self.click_challenge_tiles(coordinates)
#         if not success:
#             return False

#         return self.submit_challenge_solution()

#     except Exception as e:
#         print(f"Grid solve failed: {e}")
#         return False


#     def detect_challenge_type(self):
#         """ACCURATELY detect reCAPTCHA challenge type — GRID vs MULTI-TILE"""
#         try:
#             # 1. PRIORITY: Look for GRID TABLE with <td> cells
#             table = self.driver.find_elements(By.CSS_SELECTOR, ".rc-imageselect-table")
#             if table:
#                 td_cells = table[0].find_elements(By.CSS_SELECTOR, "td")
#                 count = len(td_cells)
#                 print(f"Found .rc-imageselect-table with {count} <td> → GRID DETECTED")
#                 if count == 9:
#                     return "grid_3x3"
#                 elif count == 16:
#                     return "grid_4x4"

#             # 2. ONLY IF NO TABLE → multi-tile selection
#             tile_wrappers = self.driver.find_elements(By.CSS_SELECTOR, ".rc-imageselect-tile")
#             if tile_wrappers and len(tile_wrappers) > 1:
#                 # Double-check: no table → true multi-tile
#                 if not self.driver.find_elements(By.CSS_SELECTOR, ".rc-imageselect-table"):
#                     print(f"Found {len(tile_wrappers)} .rc-imageselect-tile (no table) → MULTI-TILE")
#                     return "image_selection"

#             # 3. Fallback
#             print("Unknown challenge type")
#             return "unknown"

#         except Exception as e:
#             print(f"Error in detection: {e}")
#             return "unknown"
    
#     def solve_3x3_grid_challenge(self):
#         """Solve the 3x3 grid image challenge"""
#         try:
#             print("Solving 3x3 grid challenge...")
            
#             # Get challenge instruction
#             instruction = self.get_challenge_instruction()
#             print(f"Challenge instruction: {instruction}")
            
#             # Get the challenge image
#             image_data = self.get_challenge_image()
#             if not image_data:
#                 print("✗ Could not get challenge image")
#                 return False
            
#             print("Sending 3x3 grid challenge to 2captcha...")
            
#             # Solve using grid method specifically for 3x3
#             try:
#                 result = self.solver.grid(
#                     image_data,
#                     rows=3,
#                     columns=3
#                 )
#                 coordinates = result['code']
#                 print(f"✓ 3x3 Grid challenge solved! Coordinates: {coordinates}")
                
#                 # Click the grid positions
#                 success = self.click_grid_positions(coordinates, 3, 3)
#                 if not success:
#                     print("✗ Failed to click grid positions")
#                     return False
                
#                 # Submit the solution
#                 return self.submit_challenge_solution()
                
#             except Exception as e:
#                 print(f"3x3 Grid solving failed: {e}")
#                 return False
            
#         except Exception as e:
#             print(f"Error solving 3x3 grid challenge: {e}")
#             return False
    
#     def solve_4x4_grid_challenge(self):
#         """Solve the 4x4 grid image challenge"""
#         try:
#             print("Solving 4x4 grid challenge...")
            
#             # Get challenge instruction
#             instruction = self.get_challenge_instruction()
#             print(f"Challenge instruction: {instruction}")
            
#             # Get the challenge image
#             image_data = self.get_challenge_image()
#             if not image_data:
#                 print("✗ Could not get challenge image")
#                 return False
            
#             print("Sending 4x4 grid challenge to 2captcha...")
            
#             # Solve using grid method specifically for 4x4
#             try:
#                 result = self.solver.grid(
#                     image_data,
#                     rows=4,
#                     columns=4
#                 )
#                 coordinates = result['code']
#                 print(f"✓ 4x4 Grid challenge solved! Coordinates: {coordinates}")
                
#                 # Click the grid positions
#                 success = self.click_grid_positions(coordinates, 4, 4)
#                 if not success:
#                     print("✗ Failed to click grid positions")
#                     return False
                
#                 # Submit the solution
#                 return self.submit_challenge_solution()
                
#             except Exception as e:
#                 print(f"4x4 Grid solving failed: {e}")
#                 return False
            
#         except Exception as e:
#             print(f"Error solving 4x4 grid challenge: {e}")
#             return False
    
#     def solve_image_selection_challenge(self):
#         """Solve image selection challenge"""
#         try:
#             print("Solving image selection challenge...")
            
#             # Get challenge instruction
#             instruction = self.get_challenge_instruction().lower()
#             print(f"Challenge instruction: {instruction}")

#             # === DETECT IF IT'S ACTUALLY A GRID ===
#             actual_type = self.detect_challenge_type()
#             if actual_type.startswith("grid_"):
#                 print(f"GRID DETECTED ({actual_type}) → USING GRID SOLVER")
#                 return self.solve_grid_challenge_with_skip_check(instruction)
            
#             # === TRUE MULTI-TILE SELECTION ===
#             image_data = self.get_challenge_image()
#             if not image_data:
#                 return False

#             # # === FORCE GRID SOLVER IF GRID LAYOUT ===
#             # if self.detect_challenge_type().startswith("grid_"):
#             #     print("GRID layout detected → using grid solver")
#             #     return self.solve_grid_challenge_with_skip_check(instruction)

#             # if any(p in instruction for p in ["if there are none", "click skip"]):
#             #     print("'Skip if none' in image selection → checking with 2Captcha")
#             #     image_data = self.get_challenge_image()
#             #     if image_data:
#             #         try:
#             #             result = self.solver.normal(
#             #                 image_data,
#             #                 hintText="Reply 'NONE' if no objects. Else describe.",
#             #                 lang='en'
#             #             )
#             #             if 'none' in result['code'].lower():
#             #                 return self.click_skip_button()
#             #         except:
#             #             pass
#                 # return self.click_skip_button()
            
#             # Get the challenge image
#             image_data = self.get_challenge_image()
#             if not image_data:
#                 print("✗ Could not get challenge image")
#                 return False
            
#             print("Sending image selection challenge to 2captcha...")
            
#             # Solve using normal image recognition
#             try:
#                 result = self.solver.normal(
#                     image_data,
#                     # numeric=0,
#                     # minLen=0,
#                     # maxLen=0,
#                     lang='en',
#                     hintText=instruction
#                 )
#                 answer = result['code']
#                 print(f"✓ Image selection challenge solved! Answer: {answer}")
                
#                 # For image selection, we might need to click specific areas
#                 # This is a simplified approach - might need adjustment based on actual challenge
#                 # success = self.click_image_positions(answer)
#                 success = self.click_challenge_tiles(answer)
#                 if not success:
#                     print("✗ Failed to click image positions")
#                     return False
                
#                 # Submit the solution
#                 return self.submit_challenge_solution()
                
#             except Exception as e:
#                 print(f"Image selection solving failed: {e}")
#                 return False
            
#         except Exception as e:
#             print(f"Error solving image selection challenge: {e}")
#             return False
    
#     def solve_generic_challenge(self):
#         """Generic challenge solving as fallback"""
#         try:
#             print("Trying generic challenge solving...")
            
#             # Get challenge instruction
#             instruction = self.get_challenge_instruction()
#             print(f"Challenge instruction: {instruction}")
            
#             # Get the challenge image
#             image_data = self.get_challenge_image()
#             if not image_data:
#                 print("✗ Could not get challenge image")
#                 return False
            
#             print("Sending generic challenge to 2captcha...")
            
#             # Try multiple methods
#             methods_to_try = [
#                 lambda: self.solver.grid(image_data, rows=3, columns=3),
#                 lambda: self.solver.grid(image_data, rows=4, columns=4),
#                 lambda: self.solver.normal(image_data, numeric=0, minLen=0, maxLen=0, lang='en')
#             ]
            
#             for i, method in enumerate(methods_to_try):
#                 try:
#                     print(f"Trying method {i+1}...")
#                     result = method()
#                     answer = result['code']
#                     print(f"✓ Challenge solved with method {i+1}! Answer: {answer}")
                    
#                     # Try to interpret and click the answer
#                     success = self.interpret_and_click_answer(answer)
#                     if success:
#                         return self.submit_challenge_solution()
#                     else:
#                         print(f"Method {i+1} failed to click positions")
                        
#                 except Exception as e:
#                     print(f"Method {i+1} failed: {e}")
#                     continue
            
#             print("All solving methods failed")
#             return False
            
#         except Exception as e:
#             print(f"Error in generic challenge solving: {e}")
#             return False
    
#     def get_challenge_instruction(self):
#         """Get the full challenge instruction text"""
#         try:
#             instruction_selectors = [
#                 ".rc-imageselect-desc",
#                 ".rc-imageselect-desc-no-wrap",
#                 ".rc-imageselect-instructions",
#                 "strong"
#             ]
            
#             for selector in instruction_selectors:
#                 try:
#                     elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
#                     for elem in elements:
#                         text = elem.text.strip()
#                         if text and len(text) > 5:
#                             print(f"Found instruction: {text}")
#                             return text
#                 except:
#                     continue
            
#             # Fallback
#             return ""
#         except:
#             return ""
    
#     def click_skip_button(self):
#         """Click the Skip button if available"""
#         try:
#             skip_selectors = [
#                 "#recaptcha-skipped-button",
#                 "button[title='Skip']",
#                 "button:contains('Skip')",
#                 ".rc-button-skip",
#                 "button span:contains('Skip')"
#             ]

#             for selector in skip_selectors:
#                 try:
#                     if ":contains" in selector:
#                         text = selector.split("'")[1]
#                         buttons = self.driver.find_elements(By.XPATH, f"//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{text.lower()}')]")
#                     else:
#                         buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
#                     for button in buttons:
#                         if button.is_displayed() and button.is_enabled():
#                             print("✓ Clicking Skip button")
#                             self.driver.execute_script("arguments[0].click();", button)
#                             time.sleep(2)
#                             return True
#                 except:
#                     continue
#             return False
#         except Exception as e:
#             print(f"Error clicking skip: {e}")
#             return False


#     def get_challenge_image(self):
#         """Get the challenge image"""
#         try:
#             # Wait for the challenge image to load
#             challenge_image = WebDriverWait(self.driver, 15).until(
#                 EC.presence_of_element_located((By.CSS_SELECTOR, ".rc-imageselect-challenge img"))
#             )
            
#             image_src = challenge_image.get_attribute("src")
#             print(f"Challenge image source: {image_src[:100]}...")
            
#             if image_src.startswith('data:image'):
#                 # Data URL image
#                 image_data = image_src.split(',')[1]
#                 print("Using data URL image")
#                 return image_data
#             else:
#                 # URL image - download with cookies
#                 print("Downloading challenge image from URL...")
#                 return self.download_image_with_cookies(image_src)
                
#         except Exception as e:
#             print(f"Error getting challenge image: {e}")
#             return None
    
#     def download_image_with_cookies(self, image_url):
#         """Download image with browser cookies"""
#         try:
#             # Get all cookies from the current domain
#             cookies = self.driver.get_cookies()
#             session = requests.Session()
            
#             # Add cookies to session
#             for cookie in cookies:
#                 session.cookies.set(cookie['name'], cookie['value'])
            
#             # Add headers to mimic browser request
#             headers = {
#                 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
#                 'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
#                 'Accept-Language': 'en-US,en;q=0.9',
#                 'Referer': 'https://www.google.com/',
#             }
            
#             print(f"Downloading image from: {image_url[:100]}...")
#             response = session.get(image_url, headers=headers, timeout=30)
#             response.raise_for_status()
            
#             image_base64 = base64.b64encode(response.content).decode('utf-8')
#             print("✓ Image downloaded successfully")
#             return image_base64
            
#         except Exception as e:
#             print(f"Error downloading image with cookies: {e}")
#             return None
    
#     # def click_grid_positions(self, coordinates, rows, columns):
#     #     """Click on grid positions"""
#     #     try:
#     #         positions = coordinates.split(',')
#     #         print(f"Clicking positions: {positions} in {rows}x{columns} grid")
            
#     #         # Find the grid table
#     #         grid = WebDriverWait(self.driver, 10).until(
#     #             EC.presence_of_element_located((By.CSS_SELECTOR, ".rc-imageselect-table"))
#     #         )
            
#     #         # Get all tiles in the grid
#     #         tiles = grid.find_elements(By.CSS_SELECTOR, "td")
#     #         print(f"Found grid with {len(tiles)} tiles")
            
#     #         expected_tiles = rows * columns
#     #         if len(tiles) != expected_tiles:
#     #             print(f"Warning: Expected {expected_tiles} tiles but found {len(tiles)}")
            
#     #         # Click each position
#     #         for pos in positions:
#     #             try:
#     #                 tile_index = int(pos.strip()) - 1  # Convert to 0-based index
#     #                 if 0 <= tile_index < len(tiles):
#     #                     print(f"Clicking tile {tile_index + 1}")
#     #                     tile = tiles[tile_index]
                        
#     #                     # Use JavaScript click to avoid any interception
#     #                     self.driver.execute_script("arguments[0].click();", tile)
#     #                     time.sleep(0.5)  # Wait between clicks
#     #                 else:
#     #                     print(f"Invalid tile index: {tile_index} (max: {len(tiles) - 1})")
#     #             except (ValueError, IndexError) as e:
#     #                 print(f"Error clicking position {pos}: {e}")
            
#     #         print("✓ All grid positions clicked")
#     #         return True
            
#     #     except Exception as e:
#     #         print(f"Error clicking grid positions: {e}")
#     #         return False
    
#     def click_challenge_tiles(self, answer):
#         """Click tiles for both grid and image selection challenges"""
#         try:
#             # Parse answer: "2358" → [2,3,5,8]
#             positions = []
#             for char in str(answer):
#                 if char.isdigit():
#                     positions.append(int(char))
            
#             if not positions:
#                 print("No positions to click")
#                 return True

#             print(f"Clicking positions: {positions}")

#             # Try GRID first (table-based)
#             grid_tiles = self.driver.find_elements(By.CSS_SELECTOR, ".rc-imageselect-table td")
#             if grid_tiles and len(grid_tiles) in [9, 16]:
#                 print(f"Using grid table ({len(grid_tiles)} tiles)")
#                 for pos in positions:
#                     idx = pos - 1
#                     if 0 <= idx < len(grid_tiles):
#                         tile = grid_tiles[idx]
#                         self.driver.execute_script("arguments[0].scrollIntoView(true);", tile)
#                         time.sleep(0.3)
#                         self.driver.execute_script("arguments[0].click();", tile)
#                         print(f"  Clicked grid tile {pos}")
#                         time.sleep(0.5)
#                 return True

#             # Fallback: multi-tile selection
#             tiles = self.driver.find_elements(By.CSS_SELECTOR, ".rc-imageselect-tile")
#             if tiles:
#                 print(f"Using multi-tile selection ({len(tiles)} tiles)")
#                 for pos in positions:
#                     idx = pos - 1
#                     if 0 <= idx < len(tiles):
#                         tile = tiles[idx]
#                         self.driver.execute_script("arguments[0].scrollIntoView(true);", tile)
#                         time.sleep(0.3)
#                         self.driver.execute_script("arguments[0].click();", tile)
#                         print(f"  Clicked tile {pos}")
#                         time.sleep(0.5)
#                 return True

#             print("No clickable tiles found")
#             return False

#         except Exception as e:
#             print(f"Error clicking tiles: {e}")
#             return False


#     # def click_image_positions(self, answer):
#     #     """Click tiles based on 2Captcha answer (e.g. '1389' = tiles 1,3,8,9)"""
#     #     try:
#     #         positions = [int(x) for x in str(answer).strip() if x.isdigit()]
#     #         if not positions:
#     #             print("No valid positions in answer, skipping clicks")
#     #             return True

#     #         # Find all clickable tiles
#     #         tiles = self.driver.find_elements(By.CSS_SELECTOR, ".rc-imageselect-tile")
#     #         if not tiles:
#     #             print("No tiles found to click")
#     #             return False

#     #         print(f"Clicking {len(positions)} tiles: {positions}")

#     #         for pos in positions:
#     #             tile_index = pos - 1  # 1-based → 0-based
#     #             if 0 <= tile_index < len(tiles):
#     #                 tile = tiles[tile_index]
#     #                 if tile.is_displayed():
#     #                     self.driver.execute_script("arguments[0].scrollIntoView(true);", tile)
#     #                     time.sleep(0.3)
#     #                     self.driver.execute_script("arguments[0].click();", tile)
#     #                     print(f"  Clicked tile {pos}")
#     #                     time.sleep(0.5)
#     #             else:
#     #                 print(f"  Invalid tile index: {pos}")

#     #         return True

#     #     except Exception as e:
#     #         print(f"Error clicking image positions: {e}")
#     #         return False
    
#     def interpret_and_click_answer(self, answer):
#         """Interpret the answer and try to click accordingly"""
#         try:
#             print(f"Interpreting answer: {answer}")
#             # If it looks like coordinates (comma-separated numbers)
#             if ',' in answer and answer.replace(',', '').isdigit():
#                 positions = answer.split(',')
#                 # Try different grid sizes
#                 for rows, cols in [(3, 3), (4, 4)]:
#                     if len(positions) <= rows * cols:
#                         return self.click_grid_positions(answer, rows, cols)
#             return True
#         except Exception as e:
#             print(f"Error interpreting answer: {e}")
#             return True
    
#     def submit_challenge_solution(self):
#         """Submit the challenge solution"""
#         try:
#             # Click verify button
#             verify_success = self.click_verify_button()
#             if not verify_success:
#                 print("✗ Failed to click verify button")
#                 return False
            
#             # Wait for result and check if additional challenges
#             time.sleep(5)
#             additional_solved = self.check_additional_challenges()
#             return additional_solved
            
#         except Exception as e:
#             print(f"Error submitting challenge solution: {e}")
#             return False
    
#     def click_verify_button(self):
#         """Click the verify button"""
#         try:
#             # Wait for verify button to be clickable
#             verify_button = WebDriverWait(self.driver, 10).until(
#                 EC.element_to_be_clickable((By.CSS_SELECTOR, "#recaptcha-verify-button"))
#             )
            
#             # Use JavaScript click for reliability
#             self.driver.execute_script("arguments[0].click();", verify_button)
#             print("✓ Verify button clicked")
#             return True
            
#         except Exception as e:
#             print(f"Error clicking verify button: {e}")
            
#             # Try alternative selectors
#             alternative_selectors = [
#                 "button[type='submit']",
#                 ".rc-button-default",
#                 "button:contains('Verify')",
#                 "button:contains('Skip')",
#                 "button:contains('Next')"
#             ]
            
#             for selector in alternative_selectors:
#                 try:
#                     if ":contains" in selector:
#                         text = selector.split("'")[1] if "'" in selector else selector.split('"')[1]
#                         buttons = self.driver.find_elements(By.XPATH, f"//button[contains(text(), '{text}')]")
#                     else:
#                         buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
#                     for button in buttons:
#                         if button.is_displayed():
#                             self.driver.execute_script("arguments[0].click();", button)
#                             print(f"✓ Clicked alternative button: {selector}")
#                             return True
#                 except:
#                     continue
            
#             return False
    
#     def check_additional_challenges(self):
#         """Check if additional challenges need to be solved"""
#         try:
#             # Wait a bit to see if new challenge appears
#             time.sleep(5)
            
#             # Check if we're still in challenge mode
#             still_challenge = self.driver.find_elements(By.CSS_SELECTOR, ".rc-imageselect-challenge")
#             if still_challenge:
#                 print("Additional challenge detected, solving again...")
#                 return self.solve_challenge()
            
#             # Check if verify button is still visible (meaning challenge not completed)
#             verify_buttons = self.driver.find_elements(By.CSS_SELECTOR, "#recaptcha-verify-button")
#             if verify_buttons and verify_buttons[0].is_displayed():
#                 print("Challenge not completed, might need to wait longer...")
#                 return False
            
#             print("✓ Challenge completed successfully")
#             return True
            
#         except Exception as e:
#             print(f"Error checking additional challenges: {e}")
#             return True
    
#     def submit_verification_form(self):
#         """Submit the verification form"""
#         try:
#             # Switch back to main content first
#             self.driver.switch_to.default_content()
#             time.sleep(3)
            
#             submit_selectors = [
#                 "button[type='submit']",
#                 "input[type='submit']",
#                 "button[name='submit']",
#                 "#btnContinue",
#                 "button[data-testid*='continue']",
#                 "button:contains('Continue')",
#                 "button:contains('Submit')"
#             ]
            
#             for selector in submit_selectors:
#                 try:
#                     if ":contains" in selector:
#                         text = selector.split("'")[1] if "'" in selector else selector.split('"')[1]
#                         buttons = self.driver.find_elements(By.XPATH, f"//button[contains(text(), '{text}')]")
#                     else:
#                         buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
#                     for button in buttons:
#                         if button.is_displayed() and button.is_enabled():
#                             print(f"✓ Clicking submit button: {selector}")
#                             self.driver.execute_script("arguments[0].click();", button)
#                             time.sleep(5)
#                             return True
#                 except:
#                     continue
            
#             return True
            
#         except Exception as e:
#             print(f"Error submitting form: {e}")
#             return False

#     def handle_captcha(self):
#         """Main captcha handling function"""
#         captcha_type = self.detect_captcha_type()
        
#         if not captcha_type:
#             print("No captcha detected or unsupported type")
#             return False
        
#         print(f"Handling {captcha_type}...")
        
#         if captcha_type == "recaptcha_v2":
#             return self.solve_recaptcha_v2()
#         else:
#             print(f"Unsupported captcha type: {captcha_type}")
#             return False
    
#     def login_to_facebook(self, email, password):
#         """Login to Facebook with captcha detection and solving"""
#         try:
#             print("Navigating to Facebook login...")
#             self.driver.get("https://www.facebook.com/login")
            
#             WebDriverWait(self.driver, 10).until(
#                 EC.presence_of_element_located((By.ID, "email"))
#             )
            
#             print("Entering credentials...")
#             email_field = self.driver.find_element(By.ID, "email")
#             password_field = self.driver.find_element(By.ID, "pass")
            
#             email_field.clear()
#             password_field.clear()
            
#             email_field.send_keys(email)
#             password_field.send_keys(password)
            
#             login_button = self.driver.find_element(By.NAME, "login")
#             login_button.click()
            
#             print("Waiting for page redirect...")
#             time.sleep(5)
            
#             if "two_step_verification" in self.driver.current_url:
#                 print("Detected two-step verification page with captcha")
#                 captcha_solved = self.handle_captcha()
                
#                 if captcha_solved:
#                     print("✓ Captcha solved successfully!")
#                     # Submit the form after captcha is solved
#                     form_submitted = self.submit_verification_form()
#                     if form_submitted:
#                         time.sleep(5)
#                         return self.check_login_success()
#                     else:
#                         return False
#                 else:
#                     print("✗ Failed to solve captcha")
#                     return False
#             else:
#                 return self.check_login_success()
            
#         except Exception as e:
#             print(f"Login process failed: {e}")
#             return False
    
#     def check_login_success(self):
#         """Check if login was successful"""
#         try:
#             current_url = self.driver.current_url
#             print(f"Current URL: {current_url}")
            
#             if "two_step_verification" in current_url or "login" in current_url:
#                 print("Still on verification/login page - login failed")
#                 return False
            
#             if "facebook.com" in current_url:
#                 print("✓ Successfully redirected to Facebook main page")
#                 return True
                
#             return False
            
#         except Exception as e:
#             print(f"Error checking login status: {e}")
#             return False
    
#     def close(self):
#         """Close the browser"""
#         if self.driver:
#             self.driver.quit()

# # Usage
# def main():
#     API_KEY = "d6e5c610865fded5022c540af9b22fd0"  # Replace with your actual API key
#     EMAIL = "rcndevai1@gmail.com"    # Replace with your Facebook email
#     PASSWORD = "Ak@megakill001"          # Replace with your Facebook password
    
#     if API_KEY == "YOUR_2CAPTCHA_API_KEY":
#         print("Please set your 2Captcha API key first!")
#         return
    
#     fb_login = FacebookLoginWith2Captcha(API_KEY)
    
#     try:
#         print("Starting Facebook login process...")
#         success = fb_login.login_to_facebook(EMAIL, PASSWORD)
        
#         if success:
#             print("🎉 Successfully logged into Facebook!")
#         else:
#             print("❌ Failed to login to Facebook")
            
#         input("Press Enter to close the browser...")
            
#     except Exception as e:
#         print(f"Unexpected error: {e}")
#     finally:
#         fb_login.close()

# if __name__ == "__main__":
#     main()


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from twocaptcha import TwoCaptcha
import time
import base64
import requests
from io import BytesIO

class FacebookLoginWith2Captcha:
    def __init__(self, api_key, driver=None):
        self.solver = TwoCaptcha(api_key)
        self.driver = driver  # Use provided driver if available
        self.challenge_attempts = 0  # Track challenge attempts
        self.max_challenge_attempts = 5  # Limit to prevent infinite loops
        
        # Only setup new driver if none was provided
        if self.driver is None:
            self.setup_driver()
        
    def setup_driver(self):
        """Initialize Chrome driver with appropriate options"""
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
    def detect_captcha_type(self):
        """Detect what type of captcha Facebook is showing on current page"""
        print("Detecting captcha type...")
        print(f"Current URL: {self.driver.current_url}")
        
        try:
            # Check for reCAPTCHA on two-step verification page
            if "two_step_verification" in self.driver.current_url:
                print("On two-step verification page, checking for captcha...")
                
                # Check for reCAPTCHA iframe FIRST (higher priority)
                captcha_iframes = self.driver.find_elements(By.CSS_SELECTOR, "iframe[id='captcha-recaptcha']")
                if captcha_iframes:
                    print("✓ Found captcha-recaptcha iframe")
                    return "recaptcha_v2"
                
                # Then check for text-based captcha (has image with text to enter)
                text_captcha_indicators = [
                    "captcha/tfbimage",
                    "Enter the characters you see"
                ]
                
                page_source = self.driver.page_source
                for indicator in text_captcha_indicators:
                    if indicator in page_source:
                        # Double-check: make sure the text captcha image actually exists
                        text_captcha_imgs = self.driver.find_elements(By.CSS_SELECTOR, "img[src*='captcha/tfbimage']")
                        if text_captcha_imgs:
                            print(f"✓ Found text captcha indicator: {indicator}")
                            return "text_captcha"
            
            return None
            
        except Exception as e:
            print(f"Error detecting captcha type: {e}")
            return None
    
    def solve_recaptcha_v2(self):
        """Solve reCAPTCHA v2 with the complete iframe flow and retry on timeout"""
        max_retries = 3  # Retry up to 3 times if captcha times out
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                if retry_count > 0:
                    print(f"\n🔄 Retry attempt {retry_count}/{max_retries - 1}...")
                    print("Captcha timed out - checking if checkbox reappeared...")
                    time.sleep(3)
                
                print("Starting complete reCAPTCHA iframe flow...")
                
                # Use the complete iframe flow since token method often fails
                print("Using complete iframe flow...")
                result = self.solve_complete_iframe_flow()
                
                if result:
                    print("✓ Captcha solved successfully!")
                    return True
                else:
                    print("✗ Captcha solving failed")
                    retry_count += 1
                    
                    # Check if we should retry
                    if retry_count < max_retries:
                        print("Checking if checkbox is available for retry...")
                        # Switch back to default to check for checkbox
                        self.driver.switch_to.default_content()
                        time.sleep(2)
                    else:
                        print(f"❌ Max retries ({max_retries}) reached")
                        return False
                    
            except Exception as e:
                print(f"reCAPTCHA v2 solving failed: {e}")
                self.driver.switch_to.default_content()
                retry_count += 1
                
                if retry_count < max_retries:
                    print(f"Will retry... ({retry_count}/{max_retries - 1})")
                    time.sleep(3)
                else:
                    print(f"❌ Max retries ({max_retries}) reached")
                    return False
        
        return False
    
    def solve_complete_iframe_flow(self):
        """Complete iframe flow for captcha-recaptcha iframe"""
        try:
            print("Starting complete iframe flow...")
            
            # Reset challenge attempt counter at the start
            self.challenge_attempts = 0
            
            # Step 1: Find and switch to the captcha-recaptcha iframe
            print("Step 1: Finding captcha-recaptcha iframe...")
            captcha_iframe = self.find_captcha_iframe()
            if not captcha_iframe:
                print("✗ Could not find captcha-recaptcha iframe")
                return False
            
            # Step 2: Switch to captcha-recaptcha iframe
            print("Step 2: Switching to captcha-recaptcha iframe...")
            self.driver.switch_to.frame(captcha_iframe)
            
            # Step 3: Find and switch to the checkbox iframe inside
            print("Step 3: Finding checkbox iframe inside captcha-recaptcha...")
            checkbox_iframe = self.find_checkbox_iframe_inside_captcha()
            if not checkbox_iframe:
                print("✗ Could not find checkbox iframe inside captcha-recaptcha")
                self.driver.switch_to.default_content()
                return False
            
            # Step 4: Switch to checkbox iframe and click checkbox
            print("Step 4: Switching to checkbox iframe and clicking...")
            self.driver.switch_to.frame(checkbox_iframe)
            checkbox_clicked = self.click_recaptcha_checkbox()
            
            if not checkbox_clicked:
                print("✗ Could not click checkbox")
                self.driver.switch_to.default_content()
                return False
            
            # Step 5: Wait for challenge and handle it
            print("Step 5: Handling challenge after checkbox click...")
            challenge_solved = self.handle_challenge_after_checkbox()
            
            # Always return to main content
            self.driver.switch_to.default_content()
            return challenge_solved
            
        except Exception as e:
            print(f"Complete iframe flow failed: {e}")
            self.driver.switch_to.default_content()
            return False
    
    def find_captcha_iframe(self):
        """Find the captcha-recaptcha iframe"""
        try:
            # Look for iframe with id 'captcha-recaptcha'
            iframes = self.driver.find_elements(By.CSS_SELECTOR, "iframe[id='captcha-recaptcha']")
            print(f"Found {len(iframes)} captcha-recaptcha iframes")
            
            if iframes:
                print("✓ Using captcha-recaptcha iframe")
                return iframes[0]
            
            return None
        except Exception as e:
            print(f"Error finding captcha iframe: {e}")
            return None
    
    def find_checkbox_iframe_inside_captcha(self):
        """Find the checkbox iframe inside the captcha-recaptcha iframe"""
        try:
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            print(f"Found {len(iframes)} iframes inside captcha-recaptcha")
            
            for i, iframe in enumerate(iframes):
                src = iframe.get_attribute("src") or ""
                print(f"  Checkbox iframe {i}: {src[:100]}...")
                if "google.com/recaptcha" in src and "anchor" in src:
                    print(f"✓ Found checkbox iframe at index {i}")
                    return iframe
            
            return None
        except Exception as e:
            print(f"Error finding checkbox iframe: {e}")
            return None
    
    def click_recaptcha_checkbox(self):
        """Click the reCAPTCHA checkbox"""
        try:
            print("Looking for checkbox element...")
            
            # Wait for checkbox to load
            time.sleep(2)
            
            # Take screenshot for debugging
            self.driver.save_screenshot("checkbox_iframe.png")
            print("Saved screenshot: checkbox_iframe.png")
            
            # Try multiple checkbox selectors
            checkbox_selectors = [
                ".recaptcha-checkbox-border",
                "#recaptcha-anchor",
                ".recaptcha-checkbox",
                "div.recaptcha-checkbox-border",
                "span.recaptcha-checkbox",
                "#anchor",
                ".rc-anchor-checkbox"
            ]
            
            checkbox = None
            for selector in checkbox_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        checkbox = elements[0]
                        print(f"✓ Found checkbox with selector: {selector}")
                        break
                except:
                    continue
            
            if checkbox and checkbox.is_displayed():
                print("Clicking checkbox...")
                # Use JavaScript click for reliability
                self.driver.execute_script("arguments[0].click();", checkbox)
                print("✓ Checkbox clicked successfully")
                return True
            else:
                print("✗ Could not find clickable checkbox")
                return False
                
        except Exception as e:
            print(f"Error clicking checkbox: {e}")
            return False
    
    def handle_challenge_after_checkbox(self):
        """Handle the challenge that appears after clicking checkbox"""
        try:
            print("Checking for challenge after checkbox click...")
            
            # Wait for challenge to appear (it might take a moment)
            print("Waiting for challenge to load...")
            time.sleep(5)
            
            # Step 1: Switch back to captcha-recaptcha iframe level
            self.driver.switch_to.parent_frame()  # Back to captcha-recaptcha iframe
            print("Switched back to captcha-recaptcha iframe level")
            
            # Step 2: Look for challenge iframe that appears dynamically
            print("Looking for dynamically loaded challenge iframe...")
            challenge_iframe = self.find_dynamic_challenge_iframe()
            if not challenge_iframe:
                print("No challenge iframe found - checkbox might have been sufficient")
                return True
            
            # Step 3: Switch to challenge iframe
            print("Switching to challenge iframe...")
            self.driver.switch_to.frame(challenge_iframe)
            
            # Step 4: Solve the challenge (could be grid, images, or other types)
            print("Solving challenge...")
            challenge_solved = self.solve_challenge()
            
            return challenge_solved
            
        except Exception as e:
            print(f"Error handling challenge after checkbox: {e}")
            return False
    
    def find_dynamic_challenge_iframe(self):
        """Find the challenge iframe that appears dynamically after checkbox click"""
        try:
            # Wait for the challenge iframe to appear
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "iframe"))
            )
            
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            print(f"Found {len(iframes)} iframes after checkbox click")
            
            for i, iframe in enumerate(iframes):
                src = iframe.get_attribute("src") or ""
                print(f"  Challenge iframe {i}: {src[:100]}...")
                if "google.com/recaptcha" in src and "bframe" in src:
                    print(f"✓ Found challenge iframe at index {i}")
                    return iframe
            
            # If no bframe found, try to find any new iframe that appeared
            if iframes:
                print(f"Using first available iframe for challenge")
                return iframes[0]
            
            return None
        except Exception as e:
            print(f"Error finding dynamic challenge iframe: {e}")
            return None
    
    def solve_challenge(self):
        """Solve whatever challenge appears (grid, images, etc.)"""
        try:
            print("Starting challenge solution...")
            
            # Wait for challenge to load
            time.sleep(3)
            self.driver.save_screenshot("challenge_screen.png")

            # Get full instruction
            instruction = self.get_challenge_instruction().lower()
            print(f"Full instruction: {instruction}")

            # === NORMAL FLOW: Solve with 2Captcha ===
            challenge_type = self.detect_challenge_type()
            print(f"Detected challenge type: {challenge_type}")

            # All grid types (3x3, 4x4) and image_selection use the same solver now
            # because solve_image_selection_challenge handles both table and non-table grids
            if challenge_type in ["grid_3x3", "grid_4x4", "image_selection"]:
                return self.solve_image_selection_challenge()
            else:
                return self.solve_generic_challenge()

        except Exception as e:
            print(f"Error solving challenge: {e}")
            return False
    
    def solve_grid_challenge_with_skip_check(self, instruction):
        """Solve 3x3 or 4x4 grid with skip detection"""
        try:
            # Determine grid size
            grid_elem = self.driver.find_element(By.CSS_SELECTOR, ".rc-imageselect-table")
            tiles = grid_elem.find_elements(By.CSS_SELECTOR, "td")
            tile_count = len(tiles)
            rows = 3 if tile_count == 9 else 4
            cols = 3 if tile_count == 9 else 4

            image_data = self.get_challenge_image()
            if not image_data:
                return False

            # Use 2Captcha grid solver
            result = self.solver.grid(image_data, rows=rows, columns=cols)
            coordinates = result['code']
            print(f"2Captcha grid result: {coordinates}")

            # If 2Captcha says nothing (or invalid), and skip is allowed → skip
            if not coordinates or coordinates.strip() in ['0', '']:
                if any(p in instruction for p in ["if there are none", "click skip"]):
                    print("No tiles to click + skip allowed → Skipping")
                    return self.click_skip_button()

            # Otherwise click positions
            success = self.click_grid_positions(coordinates, rows, cols)
            if not success:
                return False

            return self.submit_challenge_solution()

        except Exception as e:
            print(f"Grid solve failed: {e}")
            return False


    def detect_challenge_type(self):
        """Accurately detect reCAPTCHA challenge type"""
        try:
            # Save screenshot for debugging
            try:
                self.driver.save_screenshot("challenge_type_detection.png")
            except:
                pass
            
            # 1. PRIORITY: Check for GRID TABLE (3x3 or 4x4) - Most specific
            grid_table = self.driver.find_elements(By.CSS_SELECTOR, ".rc-imageselect-table")
            if grid_table:
                tiles = grid_table[0].find_elements(By.CSS_SELECTOR, "td")
                tile_count = len(tiles)
                print(f"Found .rc-imageselect-table with {tile_count} <td> cells → GRID DETECTED")
                if tile_count == 9:
                    return "grid_3x3"
                elif tile_count == 16:
                    return "grid_4x4"
            
            # 2. Check if there are 9 or 16 tile elements arranged in grid (even without table)
            tile_container = self.driver.find_elements(By.CSS_SELECTOR, ".rc-imageselect-tile")
            if tile_container:
                tile_count = len(tile_container)
                print(f"Found {tile_count} .rc-imageselect-tile elements")
                
                # Check if they're arranged in a grid pattern
                if tile_count == 9:
                    print("9 tiles detected → Treating as 3x3 GRID")
                    return "grid_3x3"
                elif tile_count == 16:
                    print("16 tiles detected → Treating as 4x4 GRID")
                    return "grid_4x4"
                elif tile_count > 1:
                    print(f"{tile_count} tiles → Using image_selection")
                    return "image_selection"

            # 3. Check for dynamic image grid (newer style)
            dynamic_grid = self.driver.find_elements(By.CSS_SELECTOR, ".rc-imageselect-dynamic-selected")
            if dynamic_grid:
                return "image_selection"

            # 4. Fallback
            return "unknown"

        except Exception as e:
            print(f"Error in challenge type detection: {e}")
            return "unknown"
    
    def solve_3x3_grid_challenge(self):
        """Solve the 3x3 grid image challenge"""
        try:
            print("Solving 3x3 grid challenge...")
            
            # Get challenge instruction
            instruction = self.get_challenge_instruction()
            print(f"Challenge instruction: {instruction}")
            
            # Get the challenge image
            image_data = self.get_challenge_image()
            if not image_data:
                print("✗ Could not get challenge image")
                return False
            
            print("Sending 3x3 grid challenge to 2captcha...")
            
            # Solve using grid method specifically for 3x3
            try:
                result = self.solver.grid(
                    image_data,
                    rows=3,
                    columns=3
                )
                coordinates = result['code']
                print(f"✓ 3x3 Grid challenge solved! Coordinates: {coordinates}")
                
                # Click the grid positions
                success = self.click_grid_positions(coordinates, 3, 3)
                if not success:
                    print("✗ Failed to click grid positions")
                    return False
                
                # Submit the solution
                return self.submit_challenge_solution()
                
            except Exception as e:
                print(f"3x3 Grid solving failed: {e}")
                return False
            
        except Exception as e:
            print(f"Error solving 3x3 grid challenge: {e}")
            return False
    
    def solve_4x4_grid_challenge(self):
        """Solve the 4x4 grid image challenge"""
        try:
            print("Solving 4x4 grid challenge...")
            
            # Get challenge instruction
            instruction = self.get_challenge_instruction()
            print(f"Challenge instruction: {instruction}")
            
            # Get the challenge image
            image_data = self.get_challenge_image()
            if not image_data:
                print("✗ Could not get challenge image")
                return False
            
            print("Sending 4x4 grid challenge to 2captcha...")
            
            # Solve using grid method specifically for 4x4
            try:
                result = self.solver.grid(
                    image_data,
                    rows=4,
                    columns=4
                )
                coordinates = result['code']
                print(f"✓ 4x4 Grid challenge solved! Coordinates: {coordinates}")
                
                # Click the grid positions
                success = self.click_grid_positions(coordinates, 4, 4)
                if not success:
                    print("✗ Failed to click grid positions")
                    return False
                
                # Submit the solution
                return self.submit_challenge_solution()
                
            except Exception as e:
                print(f"4x4 Grid solving failed: {e}")
                return False
            
        except Exception as e:
            print(f"Error solving 4x4 grid challenge: {e}")
            return False
    
    def solve_image_selection_challenge(self):
        """Solve image selection challenge using 2Captcha normal solver"""
        try:
            print("Solving image selection challenge...")
            
            # Get challenge instruction
            instruction = self.get_challenge_instruction().lower()
            print(f"Challenge instruction: {instruction}")

            # Check if this is a DYNAMIC challenge (tiles refresh after clicking)
            is_dynamic = "until there are none" in instruction or "once there are none" in instruction
            
            # Check tile count to determine if it's 4x4
            tile_elements = self.driver.find_elements(By.CSS_SELECTOR, ".rc-imageselect-tile")
            tile_count = len(tile_elements)
            print(f"Found {tile_count} tiles")
            
            # SKIP STRATEGY: Skip 4x4 and dynamic challenges, only solve 3x3 static
            if tile_count == 16:
                print("⚠️ 4x4 GRID detected - Reloading to get easier 3x3 challenge")
                self.click_reload_button()
                return self.solve_challenge()  # Recursively solve the new challenge
            
            if is_dynamic:
                print("⚠️ DYNAMIC CHALLENGE detected - Reloading to get easier static challenge")
                self.click_reload_button()
                return self.solve_challenge()  # Recursively solve the new challenge
            
            # Only solve 3x3 static challenges
            print("✓ 3x3 STATIC grid - Solving with 2Captcha...")
            
            # Static challenge - get image and solve
            image_data = self.get_challenge_image()
            if not image_data:
                print("✗ Could not get challenge image")
                return False
            
            # Extract just the object name from instruction
            object_name = instruction.replace('select all images with', '').replace('select all squares with', '').replace('if there are none, click skip', '').replace('click verify once there are none left', '').strip()
            
            # Use 2Captcha normal solver with clear, simple hint
            print(f"Sending to 2Captcha normal solver for {object_name}...")
            try:
                result = self.solver.normal(
                    image_data,
                    lang='en',
                    hintText=f"Which tile numbers (1-{tile_count}) contain: {object_name.replace('a', '').replace('an', '').strip()}? Reply with comma-separated numbers like '2,5,9' or 'NONE' if nothing matches"
                )
                answer = result['code'].strip()
                print(f"✓ 2Captcha answer: {answer}")
                
                # Handle NONE/empty/skip response
                if not answer or answer.upper() in ['NONE', 'NO', 'ZERO', '0', 'SKIP']:
                    print("2Captcha says no matches → Clicking Skip")
                    self.click_skip_button()
                    return self.submit_challenge_solution()
                
                # Validate answer contains only digits and commas
                cleaned_answer = answer.replace(',', '').replace(' ', '')
                if not cleaned_answer.isdigit():
                    print(f"⚠️ Invalid answer '{answer}' (not numeric), submitting empty to continue")
                    # Don't click Skip - just submit empty to trigger next challenge faster
                    return self.submit_challenge_solution()
                
                # Click the tiles
                success = self.click_image_positions(answer)
                if not success:
                    print("✗ Failed to click tiles")
                    return False
                
                return self.submit_challenge_solution()
                
            except Exception as e:
                error_msg = str(e)
                print(f"2Captcha solver failed: {error_msg}")
                
                # If UNSOLVABLE, reload this challenge to get a new one
                if 'UNSOLVABLE' in error_msg or 'ERROR' in error_msg:
                    print("⚠️ 2Captcha couldn't solve this - Reloading to get new challenge")
                    self.click_reload_button()
                    return self.solve_challenge()  # Recursively solve the new challenge
                
                return False
            
        except Exception as e:
            print(f"Error solving image selection challenge: {e}")
            return False
    
    def solve_dynamic_refreshing_challenge(self, instruction):
        """Solve dynamic challenge where tiles refresh with new images after clicking"""
        try:
            print("Starting DYNAMIC challenge solver...")
            print("Strategy: Get FULL grid screenshot, analyze, click tiles, repeat")
            
            target_object = instruction.replace('select all images with', '').replace('select all squares with', '').replace('click verify once there are none left', '').replace('until there are none', '').strip()
            print(f"Target object: {target_object}")
            
            max_iterations = 5  # Reduced from 15 to prevent timeout (5 iterations = ~75-125 seconds max)
            iteration = 0
            tiles_clicked_total = 0
            
            # Track total time to prevent timeout
            import time as time_module
            start_time = time_module.time()
            max_total_time = 60  # 60 seconds max for entire dynamic challenge
            
            while iteration < max_iterations:
                iteration += 1
                print(f"\n--- Iteration {iteration} ---")
                
                # Check if we've exceeded time limit
                elapsed_time = time_module.time() - start_time
                if elapsed_time > max_total_time:
                    print(f"⚠️ Time limit reached ({elapsed_time:.1f}s / {max_total_time}s)")
                    print("Submitting to avoid captcha timeout...")
                    break
                
                # Wait a moment for any animations to settle
                time.sleep(1)
                
                # Get the FULL GRID image (not individual tiles)
                image_data = self.get_challenge_image()
                if not image_data:
                    print("Could not get grid image, trying to submit...")
                    break
                
                # Get tile count
                tile_elements = self.driver.find_elements(By.CSS_SELECTOR, ".rc-imageselect-tile")
                tile_count = len(tile_elements)
                print(f"Analyzing full grid ({tile_count} tiles) for {target_object}...")
                
                # Ask 2Captcha which tiles contain the target object
                try:
                    result = self.solver.normal(
                        image_data,
                        lang='en',
                        hintText=f"Which tile numbers (1-{tile_count}) contain {target_object}? Reply with numbers like: 1,3,5 or reply NONE if no {target_object} visible"
                    )
                    answer = result['code'].strip().upper()
                    print(f"2Captcha answer: {answer}")
                    
                    # Check if no tiles contain the object
                    if answer in ['NONE', 'NO', '0', ''] or 'NONE' in answer:
                        print(f"✓ No {target_object} found in grid - Challenge complete!")
                        print(f"Total tiles clicked: {tiles_clicked_total}")
                        break
                    
                    # Parse tile positions - handle both "1,4,7,9" and "1479" formats
                    positions = []
                    if ',' in answer:
                        # Comma-separated: "1,4,7,9"
                        positions = [p.strip() for p in answer.split(',') if p.strip().isdigit()]
                    else:
                        # No commas - could be "1479" or "147 9" or just "1479"
                        # Split into individual digits
                        positions = [c for c in answer.replace(' ', '') if c.isdigit()]
                    
                    if not positions:
                        print("No valid tile numbers in answer, assuming complete")
                        break
                    
                    print(f"Found {target_object} in tiles: {positions}")
                    
                    # Click each tile
                    for pos in positions:
                        try:
                            tile_index = int(pos) - 1  # Convert to 0-based
                            if 0 <= tile_index < len(tile_elements):
                                tile = tile_elements[tile_index]
                                print(f"  Clicking tile {pos}...", end=" ")
                                self.driver.execute_script("arguments[0].click();", tile)
                                tiles_clicked_total += 1
                                print("✓")
                                time.sleep(0.8)  # Wait for tile to refresh
                            else:
                                print(f"  Invalid tile index: {pos}")
                        except Exception as e:
                            print(f"  Error clicking tile {pos}: {e}")
                    
                    # After clicking, wait for new images to load
                    print("Waiting for new tiles to load...")
                    time.sleep(1.5)
                    
                except Exception as e:
                    error_msg = str(e)
                    print(f"Error analyzing grid: {error_msg}")
                    
                    # If 2Captcha can't solve (UNSOLVABLE error), assume no more objects and submit
                    if 'UNSOLVABLE' in error_msg or 'ERROR' in error_msg:
                        print(f"2Captcha can't solve this iteration - assuming challenge complete")
                        break
                    
                    # For other errors, also break and submit what we have
                    print("Breaking due to error, will submit current progress")
                    break
            
            if iteration >= max_iterations:
                print(f"⚠️ Reached max iterations ({max_iterations}), submitting anyway")
            
            print(f"\n✓ Dynamic challenge complete! Clicked {tiles_clicked_total} tiles total")
            # Submit the solution
            return self.submit_challenge_solution()
            
        except Exception as e:
            print(f"Error in dynamic challenge solver: {e}")
            return False
    
    def solve_generic_challenge(self):
        """Generic challenge solving as fallback"""
        try:
            print("Trying generic challenge solving...")
            
            # Get challenge instruction
            instruction = self.get_challenge_instruction()
            print(f"Challenge instruction: {instruction}")
            
            # Get the challenge image
            image_data = self.get_challenge_image()
            if not image_data:
                print("✗ Could not get challenge image")
                return False
            
            print("Sending generic challenge to 2captcha...")
            
            # Try multiple methods
            methods_to_try = [
                lambda: self.solver.grid(image_data, rows=3, columns=3),
                lambda: self.solver.grid(image_data, rows=4, columns=4),
                lambda: self.solver.normal(image_data, numeric=0, minLen=0, maxLen=0, lang='en')
            ]
            
            for i, method in enumerate(methods_to_try):
                try:
                    print(f"Trying method {i+1}...")
                    result = method()
                    answer = result['code']
                    print(f"✓ Challenge solved with method {i+1}! Answer: {answer}")
                    
                    # Try to interpret and click the answer
                    success = self.interpret_and_click_answer(answer)
                    if success:
                        return self.submit_challenge_solution()
                    else:
                        print(f"Method {i+1} failed to click positions")
                        
                except Exception as e:
                    print(f"Method {i+1} failed: {e}")
                    continue
            
            print("All solving methods failed")
            return False
            
        except Exception as e:
            print(f"Error in generic challenge solving: {e}")
            return False
    
    def get_challenge_instruction(self):
        """Get the full challenge instruction text"""
        try:
            instruction_selectors = [
                ".rc-imageselect-desc",
                ".rc-imageselect-desc-no-wrap",
                ".rc-imageselect-instructions",
                "strong"
            ]
            
            for selector in instruction_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in elements:
                        text = elem.text.strip()
                        if text and len(text) > 5:
                            print(f"Found instruction: {text}")
                            return text
                except:
                    continue
            
            # Fallback
            return ""
        except:
            return ""
    
    def click_reload_button(self):
        """Click the reload/refresh button to get a new challenge"""
        try:
            reload_selectors = [
                "#recaptcha-reload-button",
                ".rc-button-reload",
                "button[title='Get a new challenge']",
                "button[aria-label='Get a new challenge']",
                ".rc-button-default[title='Get a new challenge']"
            ]

            for selector in reload_selectors:
                try:
                    buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for button in buttons:
                        if button.is_displayed() and button.is_enabled():
                            print("✓ Clicking Reload button to get new challenge")
                            self.driver.execute_script("arguments[0].click();", button)
                            time.sleep(3)  # Wait for new challenge to load
                            return True
                except:
                    continue
            
            print("⚠️ Reload button not found")
            return False
        except Exception as e:
            print(f"Error clicking reload: {e}")
            return False
    
    def click_skip_button(self):
        """Click the Skip button if available"""
        try:
            skip_selectors = [
                "#recaptcha-skipped-button",
                "button[title='Skip']",
                "button:contains('Skip')",
                ".rc-button-skip",
                "button span:contains('Skip')"
            ]

            for selector in skip_selectors:
                try:
                    if ":contains" in selector:
                        text = selector.split("'")[1]
                        buttons = self.driver.find_elements(By.XPATH, f"//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{text.lower()}')]")
                    else:
                        buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for button in buttons:
                        if button.is_displayed() and button.is_enabled():
                            print("✓ Clicking Skip button")
                            self.driver.execute_script("arguments[0].click();", button)
                            time.sleep(2)
                            return True
                except:
                    continue
            return False
        except Exception as e:
            print(f"Error clicking skip: {e}")
            return False


    def get_challenge_image(self):
        """Get the challenge image with retry logic"""
        max_retries = 2  # Reduced retries since we'll get fresh image each time
        for attempt in range(max_retries):
            try:
                # IMPORTANT: Always get fresh image element (don't reuse stale reference)
                # This prevents 410 Gone errors from expired URLs
                challenge_image = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".rc-imageselect-challenge img"))
                )
                
                # Small wait to ensure image is fully loaded
                time.sleep(0.5)
                
                image_src = challenge_image.get_attribute("src")
                
                if not image_src:
                    print(f"No image src found (attempt {attempt + 1}/{max_retries})")
                    if attempt < max_retries - 1:
                        time.sleep(1)
                        continue
                    return None
                
                print(f"Challenge image source: {image_src[:100]}...")
                
                if image_src.startswith('data:image'):
                    # Data URL image
                    image_data = image_src.split(',')[1]
                    print("Using data URL image")
                    return image_data
                else:
                    # URL image - download with cookies
                    print(f"Downloading challenge image (attempt {attempt + 1}/{max_retries})...")
                    image_data = self.download_image_with_cookies(image_src)
                    if image_data:
                        return image_data
                    elif attempt < max_retries - 1:
                        print(f"Download failed, getting fresh image URL...")
                        time.sleep(1)
                        # Continue to next iteration to get a fresh image element
                        continue
                    
            except Exception as e:
                print(f"Error getting challenge image (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                    
        print("✗ Failed to get challenge image after all retries")
        return None
    
    def download_image_with_cookies(self, image_url):
        """Download image with browser cookies - with better error handling"""
        try:
            # Get all cookies from the current domain
            cookies = self.driver.get_cookies()
            session = requests.Session()
            
            # Add cookies to session
            for cookie in cookies:
                session.cookies.set(cookie['name'], cookie['value'])
            
            # Add headers to mimic browser request
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://www.google.com/',
            }
            
            print(f"Downloading image from: {image_url[:100]}...")
            # Reduced timeout to 10 seconds to fail faster
            response = session.get(image_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            image_base64 = base64.b64encode(response.content).decode('utf-8')
            print("✓ Image downloaded successfully")
            return image_base64
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 410:
                print("Image URL expired (410 Gone) - need fresh image")
            else:
                print(f"HTTP Error downloading image: {e}")
            return None
        except requests.exceptions.Timeout:
            print("Image download timeout (>10s)")
            return None
        except Exception as e:
            print(f"Error downloading image: {e}")
            return None
    
    def click_grid_positions(self, coordinates, rows, columns):
        """Click on grid positions for TABLE-based grids"""
        try:
            positions = coordinates.split(',')
            print(f"Clicking positions: {positions} in {rows}x{columns} grid")
            
            # Find the grid table
            grid = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".rc-imageselect-table"))
            )
            
            # Get all tiles in the grid
            tiles = grid.find_elements(By.CSS_SELECTOR, "td")
            print(f"Found grid with {len(tiles)} tiles")
            
            expected_tiles = rows * columns
            if len(tiles) != expected_tiles:
                print(f"Warning: Expected {expected_tiles} tiles but found {len(tiles)}")
            
            # Click each position
            for pos in positions:
                try:
                    tile_index = int(pos.strip()) - 1  # Convert to 0-based index
                    if 0 <= tile_index < len(tiles):
                        print(f"Clicking tile {tile_index + 1}")
                        tile = tiles[tile_index]
                        
                        # Use JavaScript click to avoid any interception
                        self.driver.execute_script("arguments[0].click();", tile)
                        time.sleep(0.5)  # Wait between clicks
                    else:
                        print(f"Invalid tile index: {tile_index} (max: {len(tiles) - 1})")
                except (ValueError, IndexError) as e:
                    print(f"Error clicking position {pos}: {e}")
            
            print("✓ All grid positions clicked")
            return True
            
        except Exception as e:
            print(f"Error clicking grid positions: {e}")
            return False
    
    def click_tile_positions(self, coordinates, tile_elements):
        """Click on tile positions for DYNAMIC grids (without table)"""
        try:
            positions = coordinates.split(',')
            print(f"Clicking {len(positions)} tile positions: {positions}")
            print(f"Available tiles: {len(tile_elements)}")
            
            # Click each position
            for pos in positions:
                try:
                    tile_index = int(pos.strip()) - 1  # Convert to 0-based index
                    if 0 <= tile_index < len(tile_elements):
                        print(f"Clicking tile {tile_index + 1}")
                        tile = tile_elements[tile_index]
                        
                        # Scroll into view and click
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", tile)
                        time.sleep(0.3)
                        self.driver.execute_script("arguments[0].click();", tile)
                        print(f"  ✓ Clicked tile {pos}")
                        time.sleep(0.5)  # Wait between clicks to allow image refresh
                    else:
                        print(f"Invalid tile index: {tile_index} (max: {len(tile_elements) - 1})")
                except (ValueError, IndexError) as e:
                    print(f"Error clicking position {pos}: {e}")
            
            print("✓ All tile positions clicked")
            return True
            
        except Exception as e:
            print(f"Error clicking tile positions: {e}")
            return False
    
    def click_image_positions(self, answer):
        """Click tiles based on 2Captcha answer (e.g. '1389' = tiles 1,3,8,9)"""
        try:
            positions = [int(x) for x in str(answer).strip() if x.isdigit()]
            if not positions:
                print("No valid positions in answer, skipping clicks")
                return True

            # Find all clickable tiles
            tiles = self.driver.find_elements(By.CSS_SELECTOR, ".rc-imageselect-tile")
            if not tiles:
                print("No tiles found to click")
                return False

            print(f"Clicking {len(positions)} tiles: {positions}")

            for pos in positions:
                tile_index = pos - 1  # 1-based → 0-based
                if 0 <= tile_index < len(tiles):
                    tile = tiles[tile_index]
                    if tile.is_displayed():
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", tile)
                        time.sleep(0.3)
                        self.driver.execute_script("arguments[0].click();", tile)
                        print(f"  Clicked tile {pos}")
                        time.sleep(0.5)
                else:
                    print(f"  Invalid tile index: {pos}")

            return True

        except Exception as e:
            print(f"Error clicking image positions: {e}")
            return False
    
    def interpret_and_click_answer(self, answer):
        """Interpret the answer and try to click accordingly"""
        try:
            print(f"Interpreting answer: {answer}")
            # If it looks like coordinates (comma-separated numbers)
            if ',' in answer and answer.replace(',', '').isdigit():
                positions = answer.split(',')
                # Try different grid sizes
                for rows, cols in [(3, 3), (4, 4)]:
                    if len(positions) <= rows * cols:
                        return self.click_grid_positions(answer, rows, cols)
            return True
        except Exception as e:
            print(f"Error interpreting answer: {e}")
            return True
    
    def submit_challenge_solution(self):
        """Submit the challenge solution"""
        try:
            # Click verify button
            verify_success = self.click_verify_button()
            if not verify_success:
                print("✗ Failed to click verify button")
                return False
            
            # Wait for result and check if additional challenges
            time.sleep(5)
            additional_solved = self.check_additional_challenges()
            return additional_solved
            
        except Exception as e:
            print(f"Error submitting challenge solution: {e}")
            return False
    
    def click_verify_button(self):
        """Click the verify button"""
        try:
            # Wait for verify button to be clickable
            verify_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "#recaptcha-verify-button"))
            )
            
            # Use JavaScript click for reliability
            self.driver.execute_script("arguments[0].click();", verify_button)
            print("✓ Verify button clicked")
            return True
            
        except Exception as e:
            print(f"Error clicking verify button: {e}")
            
            # Try alternative selectors
            alternative_selectors = [
                "button[type='submit']",
                ".rc-button-default",
                "button:contains('Verify')",
                "button:contains('Skip')",
                "button:contains('Next')"
            ]
            
            for selector in alternative_selectors:
                try:
                    if ":contains" in selector:
                        text = selector.split("'")[1] if "'" in selector else selector.split('"')[1]
                        buttons = self.driver.find_elements(By.XPATH, f"//button[contains(text(), '{text}')]")
                    else:
                        buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for button in buttons:
                        if button.is_displayed():
                            self.driver.execute_script("arguments[0].click();", button)
                            print(f"✓ Clicked alternative button: {selector}")
                            return True
                except:
                    continue
            
            return False
    
    def check_additional_challenges(self):
        """Check if additional challenges need to be solved"""
        try:
            # Check challenge limit to prevent infinite loops
            if self.challenge_attempts >= self.max_challenge_attempts:
                print(f"⚠️ Reached maximum challenge attempts ({self.max_challenge_attempts})")
                print("Submitting anyway to avoid timeout...")
                return True
            
            # Wait a bit to see if new challenge appears
            time.sleep(5)
            
            # Check if we're still in challenge mode
            still_challenge = self.driver.find_elements(By.CSS_SELECTOR, ".rc-imageselect-challenge")
            if still_challenge:
                self.challenge_attempts += 1
                print(f"Additional challenge detected ({self.challenge_attempts}/{self.max_challenge_attempts}), solving again...")
                return self.solve_challenge()
            
            # Check if verify button is still visible (meaning challenge not completed)
            verify_buttons = self.driver.find_elements(By.CSS_SELECTOR, "#recaptcha-verify-button")
            if verify_buttons and verify_buttons[0].is_displayed():
                print("Challenge not completed, might need to wait longer...")
                return False
            
            print("✓ Challenge completed successfully")
            return True
            
        except Exception as e:
            print(f"Error checking additional challenges: {e}")
            return True
    
    def submit_verification_form(self):
        """Submit the verification form"""
        try:
            # Switch back to main content first
            self.driver.switch_to.default_content()
            time.sleep(3)
            
            submit_selectors = [
                "button[type='submit']",
                "input[type='submit']",
                "button[name='submit']",
                "#btnContinue",
                "button[data-testid*='continue']",
                "button:contains('Continue')",
                "button:contains('Submit')"
            ]
            
            for selector in submit_selectors:
                try:
                    if ":contains" in selector:
                        text = selector.split("'")[1] if "'" in selector else selector.split('"')[1]
                        buttons = self.driver.find_elements(By.XPATH, f"//button[contains(text(), '{text}')]")
                    else:
                        buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for button in buttons:
                        if button.is_displayed() and button.is_enabled():
                            print(f"✓ Clicking submit button: {selector}")
                            self.driver.execute_script("arguments[0].click();", button)
                            time.sleep(5)
                            return True
                except:
                    continue
            
            return True
            
        except Exception as e:
            print(f"Error submitting form: {e}")
            return False

    def handle_captcha(self):
        """Main captcha handling function"""
        captcha_type = self.detect_captcha_type()
        
        if not captcha_type:
            print("No captcha detected or unsupported type")
            return False
        
        print(f"Handling {captcha_type}...")
        
        if captcha_type == "recaptcha_v2":
            return self.solve_recaptcha_v2()
        elif captcha_type == "text_captcha":
            return self.solve_text_captcha()
        else:
            print(f"Unsupported captcha type: {captcha_type}")
            return False
    
    def solve_text_captcha(self):
        """Solve text-based captcha (enter characters from image) with retry logic"""
        max_retries = 3  # Retry up to 3 times if another captcha appears
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                if retry_count > 0:
                    print(f"\n🔄 Text Captcha Retry attempt {retry_count}/{max_retries - 1}...")
                    time.sleep(2)
                
                print("Solving text captcha...")
            
                # Find the captcha image
                captcha_img = None
                img_selectors = [
                    "img[src*='captcha/tfbimage']",
                    "img[alt='']",
                    ".x15mokao"
                ]
                
                for selector in img_selectors:
                    try:
                        imgs = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for img in imgs:
                            src = img.get_attribute("src") or ""
                            if "captcha" in src or "tfbimage" in src:
                                captcha_img = img
                                print(f"✓ Found captcha image: {src[:80]}...")
                                break
                        if captcha_img:
                            break
                    except:
                        continue
                
                if not captcha_img:
                    print("✗ Could not find captcha image")
                    retry_count += 1
                    continue
                
                # Get image as screenshot instead of downloading URL (to avoid 400 errors)
                print("Taking screenshot of captcha image...")
                try:
                    # Scroll image into view
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", captcha_img)
                    time.sleep(1)
                    
                    # Take screenshot of the image element
                    img_screenshot = captcha_img.screenshot_as_base64
                    image_data = img_screenshot
                    print("✓ Got captcha image screenshot")
                except Exception as e:
                    print(f"Error taking screenshot: {e}")
                    retry_count += 1
                    continue
                
                # Send to 2Captcha for solving
                print("Sending to 2Captcha text solver...")
                try:
                    result = self.solver.normal(
                        image_data,
                        numeric=0,  # Allow letters and numbers
                        minLen=4,   # Min 4 characters
                        maxLen=8,   # Max 8 characters
                        lang='en'
                    )
                    captcha_text = result['code']
                    print(f"✓ 2Captcha answer: {captcha_text}")
                    
                    # Find the input field and enter the text
                    input_selectors = [
                        "input[type='text']",
                        "input[id*='_r_']",
                        "input.x1i10hfl"
                    ]
                    
                    input_field = None
                    for selector in input_selectors:
                        try:
                            inputs = self.driver.find_elements(By.CSS_SELECTOR, selector)
                            for inp in inputs:
                                if inp.is_displayed():
                                    input_field = inp
                                    print(f"✓ Found input field: {selector}")
                                    break
                            if input_field:
                                break
                        except:
                            continue
                    
                    if not input_field:
                        print("✗ Could not find input field")
                        retry_count += 1
                        continue
                    
                    # Enter the captcha text
                    print(f"Entering captcha text: {captcha_text}")
                    input_field.clear()
                    input_field.send_keys(captcha_text)
                    time.sleep(1)
                    
                    # Click the Continue button
                    continue_selectors = [
                        "div[role='button']:has-text('Continue')",
                        "button:has-text('Continue')",
                        ".x1i10hfl[role='button']"
                    ]
                    
                    continue_button = None
                    for selector in continue_selectors:
                        try:
                            if ":has-text" in selector:
                                # Use XPath for text matching
                                buttons = self.driver.find_elements(By.XPATH, "//div[@role='button' and contains(., 'Continue')]")
                                if not buttons:
                                    buttons = self.driver.find_elements(By.XPATH, "//button[contains(., 'Continue')]")
                            else:
                                buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                            
                            for btn in buttons:
                                if btn.is_displayed() and "Continue" in btn.text:
                                    continue_button = btn
                                    print(f"✓ Found Continue button")
                                    break
                            if continue_button:
                                break
                        except:
                            continue
                    
                    if continue_button:
                        print("Clicking Continue button...")
                        self.driver.execute_script("arguments[0].click();", continue_button)
                    else:
                        print("⚠️ Could not find Continue button, trying Enter key")
                        input_field.send_keys(Keys.RETURN)
                    
                    time.sleep(18)
                    
                    # Check if another text captcha appeared or if we're logged in
                    if "two_step_verification" in self.driver.current_url:
                        # Check if another text captcha appeared
                        text_captcha_imgs = self.driver.find_elements(By.CSS_SELECTOR, "img[src*='captcha/tfbimage']")
                        if text_captcha_imgs:
                            print("⚠️ Another text captcha appeared, retrying...")
                            retry_count += 1
                            continue
                    
                    # Success - either logged in or moved past captcha
                    print("✓ Captcha solved successfully!")
                    return True
                    
                except Exception as e:
                    print(f"2Captcha solving failed: {e}")
                    retry_count += 1
                    continue
                
            except Exception as e:
                print(f"Error solving text captcha: {e}")
                retry_count += 1
                continue
        
        # Max retries reached
        print(f"❌ Max retries ({max_retries}) reached for text captcha")
        return False
    
    def login_to_facebook(self, email, password):
        """Login to Facebook with captcha detection and solving"""
        try:
            print("Navigating to Facebook login...")
            self.driver.get("https://www.facebook.com/login")
            
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "email"))
            )
            
            print("Entering credentials...")
            email_field = self.driver.find_element(By.ID, "email")
            password_field = self.driver.find_element(By.ID, "pass")
            
            email_field.clear()
            password_field.clear()
            
            email_field.send_keys(email)
            password_field.send_keys(password)
            
            login_button = self.driver.find_element(By.NAME, "login")
            login_button.click()
            
            print("Waiting for page redirect...")
            time.sleep(8)
            
            if "two_step_verification" in self.driver.current_url:
                print("Detected two-step verification page with captcha")
                captcha_solved = self.handle_captcha()
                
                if captcha_solved:
                    print("✓ Captcha solved successfully!")
                    # Submit the form after captcha is solved
                    form_submitted = self.submit_verification_form()
                    if form_submitted:
                        time.sleep(5)
                        return self.check_login_success()
                    else:
                        return False
                else:
                    print("✗ Failed to solve captcha")
                    return False
            else:
                return self.check_login_success()
            
        except Exception as e:
            print(f"Login process failed: {e}")
            return False
    
    def check_login_success(self):
        """Check if login was successful"""
        try:
            current_url = self.driver.current_url
            print(f"Current URL: {current_url}")
            
            if "two_step_verification" in current_url or "login" in current_url:
                print("Still on verification/login page - login failed")
                return False
            
            if "facebook.com" in current_url:
                print("✓ Successfully redirected to Facebook main page")
                return True
                
            return False
            
        except Exception as e:
            print(f"Error checking login status: {e}")
            return False
    
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()

# Usage
def main():
    API_KEY = "d6e5c610865fded5022c540af9b22fd0"  # Replace with your actual API key
    # EMAIL = "rcndevai1@gmail.com"    # Replace with your Facebook email
    # PASSWORD = "Ak@megakill001"          # Replace with your Facebook password
    EMAIL = "raees.azam9000@gmail.com"    # Replace with your Facebook email
    PASSWORD = "Edwardes2000#"          # Replace with your Facebook password
    
    if API_KEY == "YOUR_2CAPTCHA_API_KEY":
        print("Please set your 2Captcha API key first!")
        return
    
    fb_login = FacebookLoginWith2Captcha(API_KEY)
    
    try:
        print("Starting Facebook login process...")
        success = fb_login.login_to_facebook(EMAIL, PASSWORD)
        
        if success:
            print("🎉 Successfully logged into Facebook!")
        else:
            print("❌ Failed to login to Facebook")
            
        input("Press Enter to close the browser...")
            
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        fb_login.close()

if __name__ == "__main__":
    main()