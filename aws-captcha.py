# AWS Captcha Breaking using selenium, whisper & pydub
# 
# @Author: Janib Soomro
# @OS: Ubuntu 24.04

import whisper
from pydub import AudioSegment
import re, time, random, base64, json

import selenium.webdriver as webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from selenium.common.exceptions import TimeoutException

# optional
proxy = "xxx.xxx.xxx.xxx:xxxx"

Captcha_retrys = 15

# List of common stopwords that we want to avoid
stopwords = {"is", "the", "and", "of", "a", "an", "to", "in", "it", "for", "on", "with", "as", "at", "by", "me", "text", "or", "two", "all", "we", "have", "its","from", "has", "his", "her", "so", "far"}

LoginURL = "https://prodportal.kscourts.org/ProdPortal/Account/Login"
Log_ID = "dummy@email.com"
Log_PWD = "dummypswd"

TestCase_ID = "SG-2025-PR-000561"

USER_AGENT_LIST = [
   'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.36 Safari/535.7',
   'Mozilla/5.0 (Windows NT 6.2; Win64; x64; rv:16.0) Gecko/16.0 Firefox/16.0',
   'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/534.55.3 (KHTML, like Gecko) Version/5.1.3 Safari/534.53.10',
   'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
   'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
   'Mozilla/5.0 (Windows NT 5.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
   'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
   'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
   'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
   'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
   'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
   'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
   'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36',
   'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
   'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36',
   'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36',
   'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.89 Safari/537.36',
   'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.63 Safari/537.36',
   'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
   'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
   'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
   'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36'
]

blockedurllist = [
    "*://*.facebook.com/*",
    "*://admin.*/*",
    "*://*.analytics.google.com/*",
    "*://*.analytics*/*"
]

prefs = {
    'profile.default_content_setting_values': {
        'cookies': 1, 'javascript': 1, 'images': 1, 'popups': 2, 'plugins': 2,
        'mouselock': 2, 'app_banner': 2, 'fullscreen': 2, 'midi_sysex': 2,
        'geolocation': 1, 'ppapi_broker': 2, 'mixed_script': 2, 'media_stream': 2,
        'notifications': 2, 'push_messaging': 2, 'site_engagement': 2, 
        'durable_storage': 2, 'media_stream_mic': 2, 'protocol_handlers': 2,
        'ssl_cert_decisions': 1, 'automatic_downloads': 2, 'media_stream_camera': 2,
        'metro_switch_to_desktop': 2, 'auto_select_certificate': 1,
        'protected_media_identifier': 1
    }
}

options = webdriver.ChromeOptions()
# options.binary_location = "/usr/bin/chromedriver"
options.add_experimental_option('prefs', prefs)
# options.add_argument("--headless=new")
options.add_argument(f'--proxy-server=http://{proxy}')  # optional: if site doesn't loads
options.page_load_strategy = 'eager'
options.add_argument("--start-maximized")
options.add_argument("--disable-infobars")
options.add_argument("--disable-extensions")
options.add_argument('--disable-gpu')
options.add_argument('--log-level=3')
options.add_argument('user-data-dir=./chromeprofile')
options.add_argument(random.choice(USER_AGENT_LIST))

driver = webdriver.Chrome(options=options)
driver.execute_cdp_cmd('Network.enable', {})
driver.execute_cdp_cmd('Network.setBlockedURLs', { "urls": blockedurllist })
driver.implicitly_wait(2)

# algorithm for detecting required phrase from speach
def get_captcha_word(words):
    words = [w.lower() for w in words]
    for i in range(len(words) - 3):
        if words[i] == "by" and words[i+1] == "me":
            next_word = words[i+3]
            if next_word not in stopwords and len(next_word) >= 2:
                return next_word
    return None

# main
for attempt in range(Captcha_retrys):
    print(f"Attempt {attempt + 1} of {Captcha_retrys}...")

    time.sleep(1)

    driver.get(LoginURL)
    time.sleep(1)

    try:
        # check if loin form is visible
        login_username = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.ID, 'UserName')))
        element_found = True
    except TimeoutException:
        print("Element did not appear within 2 seconds.")
        element_found = False

    if element_found:
        break

    # double check if we are on captcha page
    src_btn_elements = driver.find_elements(By.XPATH, "//a[@href='/ProdPortal/Home/Dashboard/29' and contains(@class, 'portlet-buttons')]")
    if src_btn_elements:
        break

    # Login
    time.sleep(1)

    captcha_div = driver.find_element("id", "captcha-container")
    if captcha_div:
        print("CAPTCHA detected.")

        try:
            verify_button = driver.find_element("id", "amzn-captcha-verify-button")
            if verify_button.is_displayed():
                verify_button.click()
                print("Clicked CAPTCHA verify button.")
            else:
                print("Verify button is present but not visible.")

        except NoSuchElementException:
            print("Verify button not found.")

        except ElementClickInterceptedException:
            print("Could not click the button — it may be covered or disabled.")

        # Click the audio icon
        time.sleep(2)
        driver.find_element(By.ID, "amzn-btn-audio-internal").click()
        time.sleep(3)

        # --- click 'Play audio' button to reveal audio element ---
        driver.find_element(By.CLASS_NAME, "amzn-captcha-audio-play-btn").click()
        time.sleep(2)

        # --- find the <audio> element and get the src URL ---
        audio_element = driver.find_element(By.TAG_NAME, "audio")
        audio_src = audio_element.get_attribute("src")

        # --- extract base64 audio and save as .aac ---
        if audio_src.startswith("data:audio/aac;base64,"):
            audio_base64 = audio_src.split(",")[1]
            with open("captcha.aac", "wb") as f:
                f.write(base64.b64decode(audio_base64))
            print("[+] Audio saved as captcha.aac")
        else:
            print("[-] Unexpected audio source format!")
            driver.quit()
            exit()

        # --- Step 5: Convert AAC to WAV ---
        sound = AudioSegment.from_file("captcha.aac", format="aac")
        sound.export("captcha.wav", format="wav")
        print("[+] Converted to WAV")

        # --- Step 6: Transcribe using Whisper ---
        model = whisper.load_model("base")
        result = model.transcribe("captcha.wav")
        text = result["text"]
        print("[+] Transcribed:", text)
        time.sleep(2)

        words = re.findall(r"\b\w+\b", text.lower())
        print (f'Words: {words}')

        if words:
            answer = get_captcha_word(words)
            print("[+] Extracted answer:", answer)

            if answer is not None:
                input_field = driver.find_element(By.XPATH, "//input[@placeholder='Answer']")
                input_field.send_keys(answer)
                time.sleep(2)

                # Click the "Confirm" button
                driver.find_element(By.ID, "amzn-btn-verify-internal").click()
                time.sleep(2)

                try:
                    login_username = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'UserName')))
                    print("Element appeared and is clickable.")
                    element_found = True
                except TimeoutException:
                    print("Element did not appear within 20 seconds.")
                    element_found = False

                if element_found:
                    break

    else:
        print("No CAPTCHA detected.")

# fill out login credentials
login_username = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, 'UserName')))
login_username.send_keys(Log_ID)

login_username = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, 'Password')))
login_username.send_keys(Log_PWD)

login_checkbox = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, 'TOSCheckBox')))
login_checkbox.click()

# login_btn = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, 'btnSignIn')))
# login_btn.click()

time.sleep(3)

print ('Done!')
