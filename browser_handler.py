import getpass
import json
import os
import subprocess
import webbrowser

from selenium import webdriver
from selenium.common import WebDriverException
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


def load_credentials():
    try:
        with open('credentials.json', 'r') as file:
            credentials = json.load(file)
        return credentials
    except FileNotFoundError:
        print("Credentials file not found. Please run the credentials setup script first.")
        return {}


def save_credentials(*services):
    credentials_file = 'credentials.json'
    credentials = {}

    if os.path.exists(credentials_file):
        update_existing = input(
            f"'credentials.json' already exists. Do you want to update it? (yes/no): ").strip().lower()
        if update_existing != 'yes':
            print("No updates made to the credentials file.")
            return

    for service in services:
        user_id = input(f"Enter your {service} ID: ")
        password = getpass.getpass(f"Enter your {service} password: ")
        credentials[service] = {"ID": user_id, "Password": password}

    # Save to a file
    with open(credentials_file, 'w') as file:
        json.dump(credentials, file, indent=4)

    print("Credentials saved successfully.")


def run_applescript(url):
    applescript = f"""
    tell application "Google Chrome"
        if it is running then
            quit
        end if
        delay 1
        do shell script "open -a 'Google Chrome' --args --profile-directory"
        delay 1
        tell the first window
            make new tab with properties {{URL: "{url}"}}
        end tell
        activate
    end tell
    """

    # subprocess.run(['osascript', '-e', applescript], check=True)
    # windows
    subprocess.run(['google-chrome', '--new-window', url], check=True)


def parse_zoom_url(zoom_url):
    from urllib.parse import urlparse, parse_qs

    parsed_url = urlparse(zoom_url)
    query_params = parse_qs(parsed_url.query)

    meet_code = parsed_url.path.split('/')[-1]
    password = query_params.get('pwd', [None])[0]

    return meet_code, password

def run_zoom_windows(zoom_url):
    webbrowser.open(zoom_url)

def browser_handler(url, meeting_type='meet'):
    webdriver_service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=webdriver_service, options=options)
    wait = WebDriverWait(driver, 20)

    credentials = load_credentials()

    if meeting_type == 'Google Meet':
        try:
            run_applescript(url)
        except subprocess.CalledProcessError as e:
            print(f"An error occurred: {e}")
    elif meeting_type == 'Zoom':

        if 'Zoom' in credentials:
            zoom_credentials = credentials['Zoom']
            zoom_id = zoom_credentials.get('ID')
            zoom_password = zoom_credentials.get('Password')
            if not (zoom_id or zoom_password):
                save_credentials("Zoom")
                zoom_credentials = credentials['Zoom']
                zoom_id = zoom_credentials.get('ID')
                zoom_password = zoom_credentials.get('Password')

        (meet_code, password) = parse_zoom_url(url)
        try:
            driver.get(f"https://app.zoom.us/wc/{meet_code}/start?from=pwa&fromPWA=1")
        except WebDriverException:
            pass

        accept_cookies_btn = driver.find_element(By.ID, "onetrust-accept-btn-handler")
        wait.until(EC.visibility_of(accept_cookies_btn)).click()

        email_input = driver.find_element(By.XPATH, "//input[@type='email']")
        password_input = driver.find_element(By.XPATH, "//input[@type='password']")
        sign_in_btn = driver.find_element(By.ID, "js_btn_login")
        wait.until(EC.visibility_of(email_input))

        email_input.send_keys(zoom_id)
        password_input.send_keys(zoom_password)
        sign_in_btn.click()
        wait.until(EC.invisibility_of_element(sign_in_btn))

        new_url = driver.find_element(By.ID, "webclient").get_attribute("src")
        driver.get(new_url)

        join_btn_path = "//button[text()='Join Audio by Computer']"
        wait.until(EC.presence_of_element_located((By.XPATH, join_btn_path)))

        (ActionChains(driver)
         .pause(1)
         .move_to_element(driver.find_element(By.XPATH, join_btn_path))
         .pause(1)
         .double_click().perform())
        # zoom url
        # (meet_code, password) = parse_zoom_url(url)
        # zoom_url = f"https://app.zoom.us/wc/{meet_code}/start?from=pwa&fromPWA=1"

        # run_zoom_windows(zoom_url)

    elif meeting_type == 'Other':
        driver.get(url)
    if meeting_type != 'Google Meet':
        user_input = input("Enter 'q' or 'quit' to quit the driver: ")
        if user_input == "q" or user_input == "quit":
            driver.quit()
            return


if __name__ == "__main__":
    save_credentials("Zoom")
    browser_handler("https://us05web.zoom.us/j/3582195858?pwd=9TTCTc6cTRV80flGFpc7JoaEngx8NC.1&omn=84811349927", 'Zoom')
    # browser_handler("https://meet.google.com/khv-udek-dbc?authuser=0&hs=122&ijlm=1702717531751&pli=1", 'Google Meet')
    # browser_handler("https://www.google.com", 'Other')
