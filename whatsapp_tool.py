from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from helper_selenium_functions import * 
from webdriver_manager.chrome import ChromeDriverManager
from langchain.tools import tool
import time 

@tool
def send_whatsapp_message(contact_name, message) -> str:
    '''
    useful when to send whatsapp messages using selenium web driver.
    Args:
        contact_name (str): The name of the contact you want to send the message to.
        message (str): The message you want to send.

    '''
    try:
        # Set the path to your Chrome profile
        chrome_profile_path = "/home/shubharthak/.config/google-chrome"

        # Set up Chrome options
        options = Options()
        options.add_argument("--headless")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument(f"user-data-dir={chrome_profile_path}")
        options.add_argument(r'--profile-directory=Default')

        # Set up the Chrome service
        path = '/home/shubharthak/.wdm/drivers/chromedriver/linux64/122.0.6261.111/chromedriver-linux64/chromedriver'
        service = Service(path)
        driver = webdriver.Chrome(service=service, options=options)
        print(message, contact_name)
        print('Driver initialized...')
        # Now you can use Selenium as usual
        driver.get('https://web.whatsapp.com')
        print('Opened Whatsapp')
        operate(driver=driver, xpath='//*[@id="app"]/div/div[2]/div[3]/header/div[2]/div/span/div[4]/div/span', click=True)
        time.sleep(1)
        operate(driver=driver, xpath= '//*[@id="app"]/div/div[2]/div[2]/div[1]/span/div/span/div/div[1]/div[2]/div[2]/div/div[1]/p' , click=True)
        time.sleep(1)
        operate(driver=driver, xpath= '//*[@id="app"]/div/div[2]/div[2]/div[1]/span/div/span/div/div[1]/div[2]/div[2]/div/div[1]/p' , type=contact_name)
        time.sleep(1)
        operate(driver=driver, xpath= '//*[@id="app"]/div/div[2]/div[2]/div[1]/span/div/span/div/div[1]/div[2]/div[2]/div/div[1]/p' , type=Keys.ENTER)
        time.sleep(1)
        operate(driver=driver, xpath= '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div[1]/p' , type=message)
        time.sleep(1)
        operate(driver=driver, xpath= '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div[1]/p' , type=Keys.ENTER)
        print('Message sent')
        time.sleep(3)
        # Close the driver
        driver.close()
        print('Driver closed')
        return f'Message sent successfuly to {contact_name} with message {message}'
    except Exception as e:
        print(e)
        return f'Message not sent: {e}'

if __name__ == '__main__':
    pass 