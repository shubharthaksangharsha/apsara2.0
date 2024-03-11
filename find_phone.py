from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from undetected_chromedriver import Chrome

from webdriver_manager.chrome import ChromeDriverManager
import time 

# Set the path to your Chrome profile
chrome_profile_path = "/home/shubharthak/.config/google-chrome"


# Set up Chrome options
options = Options()
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument(f"user-data-dir={chrome_profile_path}")
options.add_argument(r'--profile-directory=Default')


# Set up the Chrome service
path = '/home/shubharthak/.wdm/drivers/chromedriver/linux64/122.0.6261.111/chromedriver-linux64/chromedriver'
service = Service(path)

# Initialize the WebDriver
# driver = Chrome(user_data_dir=chrome_profile_path, headless=False, driverr_executable_path=path)
driver = webdriver.Chrome(service=service, options=options)
print('Driver initialized...')
# Now you can use Selenium as usual

driver.get("https://www.google.com/android/find/")
print('Currently at', driver.title)

time.sleep(5000)

# Wait for the page to load and the device to be present
try:
    # Assuming the device name is in a div with class "CMEZce"
    device_name = "OnePlus Nord CE 5G"
    device_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, f"//div[@class='CMEZce' and text()='{device_name}']"))
    )
    # Click on the device
    device_element.click()
    print(f'Clicked {device_name}')
except Exception as e:
    print(f"An error occurred: {e}")

# Wait for the page to load and the "PLAY SOUND" button to be clickable
try:
    # Assuming the "PLAY SOUND" button is a button with class "GLET6d HX6Ide"
    play_sound_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'GLET6d') and contains(@class, 'HX6Ide')]"))
    )
    # Click on the "PLAY SOUND" button
    play_sound_button.click()
    print('Clicked the Play SOUND button')
except Exception as e:
    print(f"An error occurred: {e}") 

print('Device must be ringing...')


