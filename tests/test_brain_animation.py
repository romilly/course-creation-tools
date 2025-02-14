import os
import pytest
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from screen_recorder import ScreenRecorder
import time
from datetime import datetime

@pytest.fixture
def firefox_driver():
    firefox_options = Options()
    firefox_options.add_argument('--width=1024')
    firefox_options.add_argument('--height=600')
    
    driver = webdriver.Firefox(options=firefox_options)
    driver.maximize_window()
    
    yield driver
    driver.quit()

@pytest.fixture
def screen_recorder(firefox_driver):
    # Load page and wait for ready indicator
    firefox_driver.get('http://localhost:8000')
    wait = WebDriverWait(firefox_driver, 10)
    # ready_element = wait.until(
    #     EC.presence_of_element_located((By.CSS_SELECTOR, "#ready-indicator[style*='visibility: visible']"))
    # )
    
    # Now start recording
    output_dir = 'recordings'
    recorder = ScreenRecorder(output_dir)
    recorder.start(firefox_driver)
    yield recorder
    recorder.stop()

def test_brain_animation(firefox_driver, screen_recorder):
    # Wait for the full animation duration (2s delay + 5s fade + 1s buffer)
    time.sleep(8)
