#TODO the file is still in progress...
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


