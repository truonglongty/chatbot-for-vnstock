import os
import shutil

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


with open('login.txt', 'r') as login_file:
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


download_folder = r'C:\Users\ADMIN\Downloads'
destination_folder = r'D:\chatbot-for-stocks\data'

# Biến để lưu trữ đường dẫn của file mới nhất
newest_file_path = None
newest_file_time = 0

# Duyệt qua tất cả các file trong thư mục tải xuống
for root, dirs, files in os.walk(download_folder):
    for file_name in files:
        file_path = os.path.join(root, file_name)
        
        # Kiểm tra nếu file là loại file bạn quan tâm (ví dụ: file Excel)
        if file_path.endswith('.xls'):
            try:
                # Lấy thông tin về thời gian tạo của file
                file_time = os.path.getctime(file_path)
                
                # Nếu thời gian tạo của file lớn hơn thời gian của file mới nhất hiện tại
                if file_time > newest_file_time:
                    newest_file_time = file_time
                    newest_file_path = file_path
            except Exception as e:
                print(f"Lỗi khi kiểm tra file {file_path}: {str(e)}")


# Kiểm tra nếu có file mới nhất được tìm thấy
if newest_file_path:
    try:
        # Thực hiện di chuyển file mới nhất đến thư mục đích
        shutil.move(newest_file_path, destination_folder)
        print(f"Đã chuyển file {newest_file_path} đến {destination_folder}")
    except Exception as e:
        print(f"Lỗi khi di chuyển file {newest_file_path}: {str(e)}")
else:
    print("Không tìm thấy file nào để di chuyển.")


browser.quit()