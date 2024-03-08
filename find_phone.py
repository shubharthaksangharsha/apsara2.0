from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options

#Initialize variables
op = Options()
fp = webdriver.FirefoxProfile('/home/shubharthak/.mozilla/firefox/33qh4ctq.default-release')
op.profile = fp
op.headless = True

def get_driver():
    driver = webdriver.Firefox(service=FirefoxService('/home/shubharthak/.wdm/drivers/geckodriver/linux64/v0.34.0/geckodriver'), options=op)
    return get_driver()

def findmyphone():
    try:
        driver = get_driver()
        driver.get('https://www.google.com/android/find/')
        print(driver.title)
        view = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, '//img[@aria-label="OnePlus Nord CE 5G"]'))).click()

        print('clicking the one plus tab button')

        # clicking the ring button 
        view = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/c-wiz/div/div[2]/div/div[2]/div[2]/div[5]/div/div[1]/button'))).click()
        print('clicked the ring button')
        return 'Ringing the phone'
    except:
        return 'Error occurred'

if __name__ == '__main__':
    pass