from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time
import os
import subprocess

def capture_animation():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--window-size=1024,600')  # Adjusted height to be divisible by 2
    chrome_options.add_argument('--hide-scrollbars')
    
    service = Service()
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        # Create frames directory if it doesn't exist
        if not os.path.exists('frames'):
            os.makedirs('frames')
        
        # Navigate to the animation page
        driver.get('http://localhost:8000')
        
        # Capture frames for 6 seconds (30fps = 180 frames)
        for i in range(180):
            driver.save_screenshot(f'frames/frame_{i:04d}.png')
            time.sleep(1/30)  # Wait for next frame
        
        # Convert frames to video using ffmpeg with crop filter
        subprocess.run([
            'ffmpeg', '-y',
            '-framerate', '30',
            '-i', 'frames/frame_%04d.png',
            '-vf', 'crop=1024:600:0:0',  # Crop to exact dimensions
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            'brain_animation.mp4'
        ])
        
        # Clean up frames
        for file in os.listdir('frames'):
            os.remove(os.path.join('frames', file))
        os.rmdir('frames')
        
        print("Animation captured and saved as brain_animation.mp4")
        
    finally:
        driver.quit()

if __name__ == '__main__':
    capture_animation()
