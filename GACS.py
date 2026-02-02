#!/usr/bin/env python3
import time, keyboard, pyautogui, pytesseract, sys, threading, os, signal, random
from PIL import Image

# =============================================================================
# RESOLUTION DETECTION & DUAL SCALING
# =============================================================================
SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()
BASE_WIDTH = 1920
BASE_HEIGHT = 1080
BASE_ASPECT = 16/9

# Different scaling for mouse vs OCR
MOUSE_SCALE_X = SCREEN_WIDTH / BASE_WIDTH   
MOUSE_SCALE_Y = SCREEN_HEIGHT / BASE_HEIGHT 
OCR_SCALE = SCREEN_HEIGHT / BASE_HEIGHT     

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
BLACK_TWO_POS = scale_mouse(*REF_BLACK_TWO)   
RED_ONE_POS   = scale_mouse(*REF_RED_ONE)
FIRST_12_POS  = scale_mouse(*REF_FIRST_12)
OCR_BOX       = scale_ocr_box(*REF_OCR)       

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

TARGET_FIRST  = "red 1"
TARGET_SECOND = "move with"

# Base timings (seconds) with ±50ms (0.05s) jitter ranges
BASE_TAB_WAIT = 0.10      # Range: 0.05 - 0.15
BASE_HOLD_TIME = 0.05     # Range: 0.00 - 0.10  
BASE_OCR_POLL = 0.20      # Range: 0.15 - 0.25
BASE_MOVE_DUR = 0.15      # Range: 0.10 - 0.20

def rand_time(base):
    """Returns base ± 50ms (0.05s)"""
    return random.uniform(base - 0.05, base + 0.05)

def jitter_pos(x, y):
    """Returns x, y ± 5 pixels"""
    return (int(x + random.uniform(-5, 5)), int(y + random.uniform(-5, 5)))

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def ocr_text(box):
    img = pyautogui.screenshot(region=(box[0], box[1], box[2]-box[0], box[3]-box[1]))
    return pytesseract.image_to_string(img).strip().lower()

def wait_for_text(target):
    log(f"Waiting for '{target}' in OCR region…")
    while target not in ocr_text(OCR_BOX):
        time.sleep(rand_time(BASE_OCR_POLL))  # 0.20 ± 50ms
    log(f"'{target}' spotted – continuing.")

def click(x, y):
    jx, jy = jitter_pos(x, y)
    hold_t = rand_time(BASE_HOLD_TIME)  # 0.05 ± 50ms
    log(f"Click at {jx},{jy} (hold {int(hold_t*1000)} ms)")
    
    pyautogui.moveTo(jx, jy, duration=rand_time(BASE_MOVE_DUR))  # 0.15 ± 50ms
    time.sleep(rand_time(BASE_HOLD_TIME))  # Pre-click pause
    pyautogui.mouseDown(button='left')
    time.sleep(hold_t)  # Hold duration
    pyautogui.mouseUp(button='left')
    time.sleep(rand_time(BASE_HOLD_TIME))  # Post-release pause

def move(x, y):
    jx, jy = jitter_pos(x, y)
    log(f"Move to {jx},{jy}")
    pyautogui.moveTo(jx, jy, duration=rand_time(BASE_MOVE_DUR))  # 0.15 ± 50ms
    time.sleep(rand_time(BASE_HOLD_TIME))  # 0.05 ± 50ms

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
            time.sleep(rand_time(BASE_TAB_WAIT))  # 0.10 ± 50ms
            log("Tab Pressed")
            keyboard.send('tab')
            time.sleep(rand_time(BASE_TAB_WAIT))  # 0.10 ± 50ms
            click(*RED_ONE_POS)
            move(*FIRST_12_POS)
            log("Tab Pressed")
            keyboard.send('tab')
            time.sleep(rand_time(BASE_TAB_WAIT))  # 0.10 ± 50ms
            for _ in range(5):
                click(*FIRST_12_POS)
            wait_for_text(TARGET_FIRST)
            wait_for_text(TARGET_SECOND)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("\nUser interrupt – exiting.")