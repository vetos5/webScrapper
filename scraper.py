import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

driver.get("https://www.csgoroll.com/roll")

WebDriverWait(driver, 1).until(EC.presence_of_all_elements_located((By.XPATH, "//span[@data-test='color-roll-times']")))


def fetch_and_save_data():
    try:
        elements = driver.find_elements(By.XPATH, "//span[@data-test='color-roll-times']")

        if len(elements) >= 5:
            red_quantity = elements[0].text
            zero_quantity = elements[1].text
            black_quantity = elements[2].text
            baitBet_red = elements[3].text
            baitBet_black = elements[4].text

            last_roll_element = driver.find_element(By.XPATH, "//a[contains(@class, 'bg-red') or contains(@class, 'bg-black') or contains(@class, 'bg-green')]")
            last_roll_color = 'Red' if 'bg-red' in last_roll_element.get_attribute("class") else (
                'Black' if 'bg-black' in last_roll_element.get_attribute("class") else 'Green')

            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

            data = {
                "Timestamp": timestamp,
                "Red Quantity": red_quantity,
                "Black Quantity": black_quantity,
                "Zero Quantity": zero_quantity,
                "BaitBet Red": baitBet_red,
                "BaitBet Black": baitBet_black,
                "Last Roll Color": last_roll_color
            }

            with open('roll_quantities.csv', mode='a', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=data.keys())
                writer.writerow(data)

            print(f"Data saved: {data}")
        else:
            print("Not enough data found. Some elements may be missing.")
    except Exception as e:
        print(f"Error: {e}")

try:
    while True:
        fetch_and_save_data()

        time.sleep(23)
except KeyboardInterrupt:
    print("Program terminated by user.")

finally:
    driver.quit()
