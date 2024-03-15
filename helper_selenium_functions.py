#By Shubharthak 
'''
This script used selenium to automate tasks. 
it consist of some helper functions which helps in automating tasks.
'''
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import NoSuchElementException  # Import the exception
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support.ui import Select


def operate(driver=None, xpath=None, click=False, type=False, instructions=None, verbose=True):
    if driver is None:
        print('Driver not provided')
        return
    if xpath is None:
        print('Xpath not provided')
        return
    if instructions:
        if verbose:
            print('Inside Instructions')
        for inst in instructions:
            
            if 'click' in inst[0]:
                if verbose:
                    print('Clicking the element')
                WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH,inst[2]))).click()
                if verbose:
                    print('Clicked the element')
            if 'type' in inst[0]:
                if verbose:
                    print('Clicking the element to type')
                type_element = WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH,inst[2])))
                type_element.click()
                if verbose:
                    print('Clicked the element')
                type_element.send_keys(inst[1])
                if verbose:
                    print('typed the keys ')
    if click:
        if verbose:
            print('Clicking the element')
            print(xpath)
        WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH,xpath))).click()
        if verbose:
            print('Clicked the element')
    if type:
        if verbose:
            print('Clicking the element to type')
        type_element = WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH,xpath)))
        type_element.click()
        if verbose:
            print('Clicked the element')
            type_element.send_keys(type)
        if verbose:
            print('typed the keys ')


def sign_in_linkedin(username, password):
    sign_button_xpath = '//*[@id="main-content"]/div/form/p/button'
    email_button_xpath = '//*[@id="session_key"]'
    password_button_xpath = '//*[@id="session_password"]'
    submit_button_xpath = '//*[@id="main-content"]/div/div[2]/form/div[2]/button'
    operate(sign_button_xpath, click=True)
    # operate(email_button_xpath, type=username)
    # operate(password_button_xpath, type=password)
    operate(submit_button_xpath, click=True)

if __name__ == '__main__':
    pass 
