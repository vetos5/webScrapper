import csv
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

driver.get("https://www.csgoroll.com/roll")

WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, "//span[@data-test='color-roll-times']")))

previous_transform = None
is_spinning = False


def is_wheel_spinning():
    global previous_transform, is_spinning
    try:
        wheel_element = driver.find_element(By.XPATH, "/html/body/cw-root/mat-sidenav-container/mat-sidenav-content/div/cw-roulette/div/div[1]/cw-wheel/div/div[2]")

        current_transform = driver.execute_script("return window.getComputedStyle(arguments[0]).getPropertyValue('transform');", wheel_element)
        match = re.match(r"matrix\(([-\d.]+), ([-\d.]+), ([-\d.]+), ([-\d.]+), ([-\d.]+), ([-\d.]+)\)", current_transform)
        if match:
            current_x = match.group(5)
            current_y = match.group(6)
        else:
            current_x, current_y = None, None

        if previous_transform is None:
            previous_transform = (current_x, current_y)
            return False
        else:
            if previous_transform != (current_x, current_y):
                previous_transform = (current_x, current_y)
                if not is_spinning:
                    is_spinning = True
                    return True
                return False
            else:
                is_spinning = False
                return False

    except Exception as e:
        print(f"Error in is_wheel_spinning: {e}")
        return False


def fetch_and_save_data():
    try:
        elements = driver.find_elements(By.XPATH, "//span[@data-test='color-roll-times']")
        total_value_elements = driver.find_elements(By.XPATH, "//span[@data-test='value']")

        if len(elements) >= 5:
            red_quantity = elements[0].text
            zero_quantity = elements[1].text
            black_quantity = elements[2].text
            baitBet_red = elements[3].text
            baitBet_black = elements[4].text

            last_roll_element = driver.find_element(By.XPATH, "//a[contains(@class, 'bg-red') or contains(@class, 'bg-black') or contains(@class, 'bg-green')]")
            last_roll_color = 'Red' if 'bg-red' in last_roll_element.get_attribute("class") else (
                'Black' if 'bg-black' in last_roll_element.get_attribute("class") else 'Green')

            red_total_value = total_value_elements[2].text

            data = {
                "Red Quantity": red_quantity,
                "Black Quantity": black_quantity,
                "Zero Quantity": zero_quantity,
                "BaitBet Red": baitBet_red,
                "BaitBet Black": baitBet_black,
                "Last Roll Color": last_roll_color,
                "Red Bets Value": red_total_value,
                "Timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
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
        if is_wheel_spinning():
            print("Wheel is spinning. Starting to scrape data...")
            fetch_and_save_data()
            time.sleep(7)
        else:
            print("Wheel is not spinning yet. Waiting...")
            time.sleep(5)

finally:
    driver.quit()
