import os
import subprocess
import time
from datetime import datetime

class ScreenRecorder:
    def __init__(self, output_dir="../recordings"):
        self.output_dir = os.path.abspath(output_dir)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        self.process = None
        print(f"\nScreen recorder initialized. Output directory: {self.output_dir}")
        
    def start(self, driver):
        """Start recording the screen using ffmpeg.
        Args:
            driver: Selenium WebDriver instance to get window position and size
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(self.output_dir, f"demo_{timestamp}.mp4")
            
            # FFmpeg command to record screen
            command = [
                'ffmpeg',
                '-f', 'x11grab',  # X11 display grabber
                '-video_size', '1920x1080',  # capture full HD screen
                '-framerate', '30',
                '-i', ':0.0',  # capture entire screen
                '-c:v', 'libx264',
                '-preset', 'ultrafast',
                '-y',  # overwrite output file if exists
                output_file
            ]
            
            print(f"\nStarting screen recording...")
            print(f"Command: {' '.join(command)}")
            print(f"Output file: {output_file}")
            
            self.process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.output_file = output_file
            
            # Check if process started successfully
            time.sleep(1)
            if self.process.poll() is not None:
                stdout, stderr = self.process.communicate()
                print(f"\nError starting screen recording: {stderr.decode()}")
                raise Exception("Failed to start screen recording")
                
            print("Screen recording started successfully")
            
        except Exception as e:
            print(f"\nError starting screen recording: {str(e)}")
            if hasattr(self, 'process') and self.process:
                self.process.terminate()
            raise
    
    def stop(self):
        """Stop the screen recording."""
        if self.process:
            print("\nStopping screen recording...")
            self.process.terminate()
            self.process.wait()
            print(f"Screen recording saved to: {self.output_file}")
            self.process = None