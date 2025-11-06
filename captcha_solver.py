# captcha_solver.py
import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from twocaptcha import TwoCaptcha, ApiException

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class FacebookCaptchaSolver:
    def __init__(self, api_key: str, timeout: int = 300):
        self.solver = TwoCaptcha(api_key)
        self.solver.default_timeout = timeout
        self.timeout = timeout

    # ------------------------------------------------------------------ #
    # Helper – wait for body
    # ------------------------------------------------------------------ #
    def _wait_body(self, driver):
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

    # ------------------------------------------------------------------ #
    # Detect any captcha
    # ------------------------------------------------------------------ #
    def _captcha_present(self, driver) -> bool:
        self._wait_body(driver)
        return bool(
            driver.find_elements(By.CSS_SELECTOR, "iframe[src*='referer_frame.php']")
            or driver.find_elements(By.CSS_SELECTOR, "iframe[title='reCAPTCHA']")
        )

    # ------------------------------------------------------------------ #
    # Click Continue button
    # ------------------------------------------------------------------ #
    def _click_continue(self, driver) -> bool:
        try:
            btn = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable(
                    (By.XPATH,
                     "//span[normalize-space()='Continue']/ancestor::div[@role='none' or @role='button'][1]")
                )
            )
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
            time.sleep(1)
            btn.click()
            log.info("Clicked Continue button")
            return True
        except Exception as e:
            log.warning(f"Continue button not clickable: {e}")
            return False

    # ------------------------------------------------------------------ #
    # Solve ANY reCAPTCHA with 2Captcha (sitekey from INNER iframe)
    # ------------------------------------------------------------------ #
    def _solve_with_2captcha(self, driver) -> bool:
        log.info("Solving reCAPTCHA with 2Captcha (sitekey from inner iframe)")
        try:
            # 1. Switch into outer iframe
            outer_iframe = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[src*='referer_frame.php']"))
            )
            WebDriverWait(driver, 15).until(EC.frame_to_be_available_and_switch_to_it(outer_iframe))
            log.info("Switched into outer iframe")

            # 2. Switch into inner reCAPTCHA iframe
            inner_iframe = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[title='reCAPTCHA']"))
            )
            WebDriverWait(driver, 15).until(EC.frame_to_be_available_and_switch_to_it(inner_iframe))
            log.info("Switched into inner reCAPTCHA iframe")

            # 3. Extract sitekey from inner iframe (robust JS)
            sitekey = driver.execute_script("""
                function find(node) {
                    if (node.getAttribute && node.getAttribute('data-sitekey')) {
                        return node.getAttribute('data-sitekey');
                    }
                    if (node.shadowRoot) {
                        const k = find(node.shadowRoot);
                        if (k) return k;
                    }
                    for (let c of node.children || []) {
                        const k = find(c);
                        if (k) return k;
                    }
                    return null;
                }
                return find(document.body) || find(document);
            """)
            if not sitekey:
                raise Exception("sitekey not found in inner iframe")
            log.info(f"Extracted sitekey from inner iframe: {sitekey}")

            # 4. Switch back to main page
            driver.switch_to.default_content()
            page_url = driver.current_url
            log.info(f"Using current URL for 2Captcha: {page_url}")

            # 5. Solve with 2Captcha
            result = self.solver.recaptcha(
                sitekey=sitekey,
                url=page_url,
                version='v2'
            )
            token = result['code']
            log.info("2Captcha solved! Token received.")

            # 6. Inject token into main DOM
            driver.execute_script(f'''
                var textarea = document.getElementById('g-recaptcha-response');
                if (!textarea) {{
                    textarea = document.createElement('textarea');
                    textarea.id = 'g-recaptcha-response';
                    textarea.style.display = 'none';
                    document.body.appendChild(textarea);
                }}
                textarea.innerHTML = "{token}";
                textarea.style.display = "";
            ''')

            # 7. Trigger callback
            driver.execute_script(f'''
                if (typeof ___grecaptcha_cfg !== 'undefined' && ___grecaptcha_cfg.clients) {{
                    for (var i in ___grecaptcha_cfg.clients) {{
                        var client = ___grecaptcha_cfg.clients[i];
                        if (client && typeof client.callback === 'function') {{
                            client.callback("{token}");
                        }}
                    }}
                }}
            ''')

            log.info("Token injected + callback triggered")

            # 8. Wait for UI
            time.sleep(3)

            # 9. Click Continue
            if not self._click_continue(driver):
                return False

            # 10. Wait for captcha to disappear
            WebDriverWait(driver, 20).until_not(
                lambda d: "referer_frame.php" in d.page_source
            )
            log.info("CAPTCHA SOLVED WITH 2CAPTCHA – continuing")
            return True

        except ApiException as e:
            log.error(f"2Captcha API error: {e}")
            driver.switch_to.default_content()
            return False
        except Exception as e:
            log.error(f"2Captcha solve failed: {e}")
            driver.switch_to.default_content()
            return False

    # ------------------------------------------------------------------ #
    # Public solve() – uses 2Captcha only
    # ------------------------------------------------------------------ #
    def solve(self, driver) -> bool:
        if not self._captcha_present(driver):
            log.debug("No captcha detected")
            return True

        return self._solve_with_2captcha(driver)