from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep


browser = webdriver.Chrome()
browser.maximize_window()

browser.get("https://finance.vietstock.vn/ket-qua-giao-dich?")
sleep(3)

browser.find_element(By.XPATH, '/html/body/div[1]/button').click()
sleep(3)

browser.find_element(By.XPATH, value='//*[@id="trading-result"]/div/div[1]/div[1]/div/div[2]/a').click()
sleep(3)


with open(r'D:\chatbot-for-stocks\scraping\login.txt', 'r') as login_file:
    lines = login_file.readlines()
    mail = lines[0]
    password = lines[1]


try:
    mail_field = browser.find_element(By.ID, 'txtEmailLogin')
    mail_field.send_keys(mail)

    password_field = browser.find_element(By.ID, 'txtPassword')
    password_field.send_keys(password)

    browser.find_element(By.XPATH, '//*[@id="btnLoginAccount"]').click()

    print('Login successful')

except:
    print('Login failed')

sleep(3)

try:
    browser.find_element(By.XPATH, value='//*[@id="trading-result"]/div/div[1]/div[1]/div/div[2]/a').click()
    sleep(5)
    print("Download successful")
except:
    print("Download failed")
