#!/usr/bin/env python3
import time, keyboard, pyautogui, pytesseract, sys, threading, os, signal
from PIL import Image

# =============================================================================
# RESOLUTION DETECTION & DUAL SCALING
# =============================================================================
SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()
BASE_WIDTH = 1920
BASE_HEIGHT = 1080
BASE_ASPECT = 16/9

# Different scaling for mouse vs OCR
MOUSE_SCALE_X = SCREEN_WIDTH / BASE_WIDTH   # Scale X by width (full screen span)
MOUSE_SCALE_Y = SCREEN_HEIGHT / BASE_HEIGHT # Scale Y by height
OCR_SCALE = SCREEN_HEIGHT / BASE_HEIGHT     # OCR uses height only (16:9 pillarbox logic)

# Calculate horizontal offset for OCR (16:9 centered zone)
UI_WIDTH_AT_16_9 = SCREEN_HEIGHT * BASE_ASPECT
OCR_H_OFFSET = 0
if SCREEN_WIDTH > UI_WIDTH_AT_16_9:
    OCR_H_OFFSET = (SCREEN_WIDTH - UI_WIDTH_AT_16_9) / 2

def scale_mouse(x, y):
    """Mouse uses full width scaling"""
    return (int(x * MOUSE_SCALE_X), int(y * MOUSE_SCALE_Y))

def scale_ocr_point(x, y):
    """OCR point uses height scaling with pillarbox offset"""
    return (int(x * OCR_SCALE + OCR_H_OFFSET), int(y * OCR_SCALE))

def scale_ocr_box(left, top, right, bottom):
    """OCR box uses height scaling with pillarbox offset"""
    return (
        int(left * OCR_SCALE + OCR_H_OFFSET),
        int(top * OCR_SCALE),
        int(right * OCR_SCALE + OCR_H_OFFSET),
        int(bottom * OCR_SCALE)
    )

# =============================================================================
# REFERENCE COORDINATES (from 1920x1080)
# =============================================================================
REF_BLACK_TWO = (280, 420)
REF_RED_ONE   = (280, 670)
REF_FIRST_12  = (475, 855)
REF_OCR       = (30, 20, 250, 50)

# =============================================================================
# SCALED COORDINATES
# =============================================================================
BLACK_TWO_POS = scale_mouse(*REF_BLACK_TWO)   # X scaled by width, Y by height
RED_ONE_POS   = scale_mouse(*REF_RED_ONE)
FIRST_12_POS  = scale_mouse(*REF_FIRST_12)
OCR_BOX       = scale_ocr_box(*REF_OCR)       # Keeps 16:9 pillarbox logic

print(f"[INIT] Monitor: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
print(f"[INIT] Mouse scale: X{MOUSE_SCALE_X:.3f} (width), Y{MOUSE_SCALE_Y:.3f} (height)")
print(f"[INIT] OCR scale: {OCR_SCALE:.3f} (height only), Offset: {OCR_H_OFFSET:.0f}px")
print(f"[INIT] Black Two: {BLACK_TWO_POS}, Red One: {RED_ONE_POS}")
print(f"[INIT] 1st 12: {FIRST_12_POS}, OCR: {OCR_BOX}")

# =============================================================================
# CONFIGURATION
# =============================================================================
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
TAB_WAIT = 0.10
HOLD_TIME = 0.05

TARGET_FIRST  = "red"
TARGET_SECOND = "move with"

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
    log(f"Click at {x},{y} (hold {int(HOLD_TIME*1000)} ms)")
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
    log(f"Mouse spans full width ({SCREEN_WIDTH}px), OCR uses 16:9 zone")
    log("Tab Back into GTA and Press = to start | Press - to stop")
    keyboard.wait('=')
    log("Starting…")
    outer = 0
    while True:
        outer += 1
        log(f"----- Cycle #{outer} -----")
        log("Losing Round, Clicking Black Two")
        click(*BLACK_TWO_POS)
        wait_for_text(TARGET_FIRST)
        wait_for_text(TARGET_SECOND)
        for inner in range(1, 5):
            log(f"	-- Winning Round {inner}/4 --")
            log("Clicking Red One")
            move(*RED_ONE_POS)
            time.sleep(TAB_WAIT)
            log("Tab Pressed")
            keyboard.send('tab')
            time.sleep(TAB_WAIT)
            click(*RED_ONE_POS)
            move(*FIRST_12_POS)
            log("Tab Pressed")
            keyboard.send('tab')
            time.sleep(TAB_WAIT)
            for _ in range(5):
                click(*FIRST_12_POS)
            wait_for_text(TARGET_FIRST)
            wait_for_text(TARGET_SECOND)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("\nUser interrupt – exiting.")