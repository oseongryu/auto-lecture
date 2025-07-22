# 1. install
# pip install pyautogui pyscreeze pillow selenium webdriver-manager opencv-python

import os
import json
import requests
import threading
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pyautogui


def capture_network_calls(url, output_file, whitelist, interval=5):

    options = webdriver.ChromeOptions()
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_window_size(1300, 800)
    counter = 0
    timer = None

    def reset_timer():
        nonlocal timer
        if timer:
            timer.cancel()
        timer = threading.Timer(20, on_timeout)  # 2분(120초) 타이머 설정
        timer.start()

    def on_timeout():
        print("동작 않음: 2분 동안 counter가 증가하지 않았습니다.")
        try:
            # 첫 번째 이미지를 클릭
            first_image_path = "1.png"  # 첫 번째 클릭할 이미지 파일 경로
            first_button_location = pyautogui.locateOnScreen(first_image_path, confidence=0.8)
            if first_button_location:
                pyautogui.click(first_button_location)
                print(f"Clicked on the first button at {first_button_location}.")
                time.sleep(2)  # 2초 대기

                # 두 번째 이미지를 클릭
                second_image_path = "2.png"  # 두 번째 클릭할 이미지 파일 경로
                second_button_location = pyautogui.locateOnScreen(second_image_path, confidence=0.8)
                if second_button_location:
                    pyautogui.click(second_button_location)
                    print(f"Clicked on the second button at {second_button_location}.")
                    reset_timer()  # 두 번째 이미지를 클릭한 후 타이머를 다시 초기화
                else:
                    print("Second button image not found on the screen.")
            else:
                print("First button image not found on the screen.")
        except Exception as e:
            print(f"Error during pyautogui operation: {e}")

    try:
        driver.get(url)
        network_calls = []
        reset_timer()  # 타이머 초기화

        print("Capturing network calls and downloading .ts files. Press Ctrl+C to stop...")
        while True:
            logs = driver.get_log('performance')
            for log in logs:
                log_json = json.loads(log['message'])['message']
                if log_json['method'] == 'Network.requestWillBeSent':
                    request_url = log_json['params']['request']['url']

                    if any(allowed in request_url for allowed in whitelist):
                        if request_url not in network_calls:
                            network_calls.append(request_url)

                        if request_url.endswith('.ts'):
                            counter += 1
                            reset_timer()  # counter가 증가했으므로 타이머 재설정

            with open(output_file, 'w') as f:
                json.dump(network_calls, f, indent=4)

            time.sleep(interval)

    except KeyboardInterrupt:
        print("\nStopping network capture.")
    finally:
        if timer:
            timer.cancel()  # 타이머 종료
        driver.quit()


# Example usage
url = "https://academia.spartacodingclub.kr"  # Replace with the target URL
output_file = "network_calls.json"
whitelist = [
    "https://s3.ap-northeast-2.amazonaws.com/academia.spartacodingclub.kr/media/",
]

capture_network_calls(url, output_file, whitelist)