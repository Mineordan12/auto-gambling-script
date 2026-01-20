#!/usr/bin/env python3
import time, keyboard, pyautogui, pytesseract, sys, threading, os, signal
from PIL import Image

TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
OCR_BOX = (474, 23, 998, 148)
TARGET_FIRST  = "red 1"
TARGET_SECOND = "move with"
TAB_WAIT = 0.10
CLICK_DT = 0.10
HOLD_TIME = 0.05

def log(msg):
	print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def ocr_text(box):
	img = pyautogui.screenshot(region=(box[0], box[1], box[2]-box[0], box[3]-box[1]))
	return pytesseract.image_to_string(img).strip().lower()

def wait_for_text(target):
	log(f"Waiting for '{target}' in OCR region…")
	while target not in ocr_text(OCR_BOX):
		time.sleep(0.2)
	log(f"'{target}' spotted – continuing.")

def click(x, y):
	log(f"Click at {x},{y}	(hold {int(HOLD_TIME*1000)} ms)")
	pyautogui.moveTo(x, y, duration=0.15)
	time.sleep(HOLD_TIME)
	pyautogui.mouseDown(button='left')
	time.sleep(HOLD_TIME)
	pyautogui.mouseUp(button='left')
	time.sleep(HOLD_TIME)

def move(x, y):
	log(f"Move to {x},{y}")
	pyautogui.moveTo(x, y, duration=0.15)
	time.sleep(HOLD_TIME)

def emergency_exit():
	keyboard.wait('-')
	log("Emergency stop ('-') – terminating now!")
	os.kill(os.getpid(), signal.SIGTERM)

threading.Thread(target=emergency_exit, daemon=True).start()

def main():
	log("Tab Back into GTA and Press = to start	| Press - to stop")
	keyboard.wait('=')
	log("Starting…")
	outer = 0
	while True:
		outer += 1
		log(f"----- Cycle #{outer} -----")
		log("Losing Round, Clicking Black Two")
		click(500, 560)
		wait_for_text(TARGET_FIRST)
		wait_for_text(TARGET_SECOND)
		for inner in range(1, 5):
			log(f"	-- Winning Round {inner}/4 --")
			log("Clicking Red One")
			move(500, 880)
			time.sleep(TAB_WAIT)
			log("Tab Pressed")
			keyboard.send('tab')
			time.sleep(TAB_WAIT)
			click(500, 880)
			move(500, 1150)
			log("Tab Pressed")
			keyboard.send('tab')
			time.sleep(TAB_WAIT)
			for _ in range(5):
				click(500, 1150)
			wait_for_text(TARGET_FIRST)
			wait_for_text(TARGET_SECOND)

if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		log("\nUser interrupt – exiting.")