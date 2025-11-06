# test_captcha.py
from login import get_driver, login_to_facebook
import configparser, time

cfg = configparser.ConfigParser()
cfg.read('config.ini')

driver = get_driver(headless=False)
email = cfg['facebook']['email']
pwd   = str(cfg['facebook']['password'])
key   = cfg['captcha']['2captcha_api_key']
print(email, pwd, key)

login_to_facebook(driver, email, pwd, key)

time.sleep(20)      # keep browser open to see the result
driver.quit()