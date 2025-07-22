import pyautogui
import time

# 2초 대기 후 (100, 200) 좌표로 이동해서 클릭
time.sleep(2)
pyautogui.moveTo(100, 200)
pyautogui.click()