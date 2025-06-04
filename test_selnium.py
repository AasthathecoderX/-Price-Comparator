from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_experimental_option("detach", True)

service = Service('C:/Users/Aastha/Desktop/Price_Comp_final/chromedriver.exe')
try:
    driver = webdriver.Chrome(service=service, options=chrome_options)
    print("Chrome driver initialized successfully.")
    driver.quit()
except Exception as e:
    print(f"Error initializing Chrome driver: {e}")